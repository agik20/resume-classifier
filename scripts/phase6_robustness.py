import pandas as pd
import numpy as np
import json
import os
import re
import warnings
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score, classification_report
import joblib
from scipy.sparse import hstack

warnings.filterwarnings('ignore')

SEED = int(os.environ.get("SEED", 42))
np.random.seed(SEED)

DATA_DIR = os.environ.get('RESUME_DATA_DIR', 'data')
RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(DATA_DIR, 'Resume.csv'))
SPLIT_DIR = 'data/splits'
REPORT_DIR = 'reports'
EXPERIMENT_DIR = 'experiments'

os.makedirs(REPORT_DIR, exist_ok=True)


def strip_header(text, chars=200):
    if pd.isna(text):
        return ""
    text = str(text)
    return text[chars:] if len(text) > chars else text


def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    return re.sub(r'\s+', ' ', text).strip()


print("Loading dataset...")
df = pd.read_csv(RESUME_CSV)
df['clean_text'] = df['Resume_str'].apply(clean_text)
df['mitigated_text'] = df['clean_text'].apply(lambda x: strip_header(x, 200))

with open(os.path.join(SPLIT_DIR, 'splits.json')) as f:
    splits = json.load(f)
train_idx = splits['train_indices']
val_idx = splits['val_indices']

y_train = df.iloc[train_idx]['Category'].values
y_val = df.iloc[val_idx]['Category'].values
X_mit_train = df.iloc[train_idx]['mitigated_text'].values
X_mit_val = df.iloc[val_idx]['mitigated_text'].values

print(f"Train: {len(X_mit_train)}, Val: {len(X_mit_val)}")

# Load vectorizer and classifier from Phase 5
print("\nLoading best model components from Phase 5...")
word_vec = joblib.load(os.path.join(EXPERIMENT_DIR, 'best_phase5_word_vec.joblib'))
char_vec = joblib.load(os.path.join(EXPERIMENT_DIR, 'best_phase5_char_vec.joblib'))
clf = joblib.load(os.path.join(EXPERIMENT_DIR, 'best_phase5_clf.joblib'))

# Verify model
X_val_features = hstack([word_vec.transform(X_mit_val), char_vec.transform(X_mit_val)])
base_macro = f1_score(y_val, clf.predict(X_val_features), average='macro')
print(f"Base Macro F1 (Combined Word+Char SVM): {base_macro:.4f}")


def perturb_email_phone(text):
    """R1: Strip emails and phone numbers."""
    text = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '[EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{10,}\b', '[PHONE]', text)
    return text.strip()


def perturb_punctuation(text):
    """R2: Strip all punctuation."""
    return re.sub(r'[^\w\s]', '', text)


def perturb_typos(text):
    """R3: Inject 1-2 random typos per resume."""
    words = text.split()
    n_typos = min(len(words) // 10, 3)
    if n_typos == 0:
        return text
    np.random.seed(SEED)
    typo_indices = np.random.choice(len(words), size=n_typos, replace=False)
    for idx in typo_indices:
        word = words[idx]
        if len(word) > 3:
            pos = np.random.randint(1, len(word) - 1)
            chars = list(word)
            chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]
            words[idx] = ''.join(chars)
    return ' '.join(words)


def perturb_truncate(text):
    """R4: Truncate to first 200 words."""
    words = text.split()
    return ' '.join(words[:200])


def perturb_drop_header(text):
    """R5: Drop first 100 words."""
    words = text.split()
    return ' '.join(words[100:]) if len(words) > 100 else text


def perturb_stopwords(text):
    """R6: Remove all stopwords."""
    stopwords = set(['i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'she', 'it', 'its',
                     'they', 'them', 'their', 'what', 'which', 'who', 'this', 'that', 'these',
                     'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                     'can', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                     'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                     'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
                     'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                     'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                     'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just',
                     'don', 'now', 'also'])
    words = text.split()
    return ' '.join([w for w in words if w not in stopwords])


perturbation_map = {
    'R1_Strip_Email_Phone': perturb_email_phone,
    'R2_No_Punctuation': perturb_punctuation,
    'R3_Random_Typos': perturb_typos,
    'R4_Truncate_200w': perturb_truncate,
    'R5_Drop_First_100w': perturb_drop_header,
    'R6_Remove_Stopwords': perturb_stopwords,
}

print("\n" + "=" * 70)
print("PHASE 6: ROBUSTNESS CHECKS")
print("=" * 70)
print(f"Base Macro F1: {base_macro:.4f}")
print(f"Tolerance: <= 0.05 drop is acceptable")
print()

results = []

for name, perturb_fn in perturbation_map.items():
    print(f"\n--- {name} ---")
    t0 = time.time()
    X_perturbed = np.array([perturb_fn(t) for t in X_mit_val])
    X_features = hstack([word_vec.transform(X_perturbed), char_vec.transform(X_perturbed)])
    y_pred = clf.predict(X_features)
    macro = f1_score(y_val, y_pred, average='macro')
    elapsed = time.time() - t0
    delta = macro - base_macro
    status = "OK" if abs(delta) <= 0.05 else "WARNING"

    print(f"  Macro F1: {macro:.4f} (delta: {delta:+.4f}) [{status}]")
    print(f"  Time: {elapsed:.2f}s")

    report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
    recalls = {k: float(report[k]['recall']) for k in report if k not in ('accuracy', 'macro avg', 'weighted avg')}
    min_rec = min(recalls.values()) if recalls else 0
    print(f"  Min Recall: {min_rec:.4f}")

    results.append({
        'perturbation': name,
        'macro_f1': float(macro),
        'delta': float(delta),
        'min_recall': float(min_rec),
        'elapsed_seconds': elapsed,
        'status': status,
        'per_class_recall': recalls,
    })

# Summary
print("\n" + "=" * 70)
print("ROBUSTNESS SUMMARY")
print("=" * 70)
print(f"\n{'Perturbation':<30} {'Macro F1':>10} {'Delta':>10} {'MinRec':>8} {'Status':>8}")
print("-" * 70)
for r in results:
    print(f"{r['perturbation']:<30} {r['macro_f1']:>10.4f} {r['delta']:>+10.4f} {r['min_recall']:>8.4f} {r['status']:>8}")

failed = [r for r in results if r['delta'] < -0.05]
if failed:
    print(f"\nFAILED ({len(failed)} perturbations with >0.05 drop):")
    for r in failed:
        print(f"  - {r['perturbation']}: delta={r['delta']:.4f}")
else:
    print(f"\nAll perturbations within tolerance (<=0.05 drop)")

r5 = next(r for r in results if r['perturbation'] == 'R5_Drop_First_100w')
if abs(r5['delta']) > 0.03:
    print(f"\nWARNING: R5 (header drop) has significant delta ({r5['delta']:.4f}).")
    print("  This suggests leakage mitigation may be insufficient.")
else:
    print(f"\nR5 (header drop) delta is acceptable ({r5['delta']:.4f}).")
    print("  Leakage mitigation appears effective.")

# Save
with open(os.path.join(REPORT_DIR, '06_robustness_results.json'), 'w') as f:
    json.dump({
        'phase': 6,
        'date': '2026-08-16',
        'seed': SEED,
        'base_macro_f1': float(base_macro),
        'tolerance': 0.05,
        'results': results,
        'all_passed': len(failed) == 0,
    }, f, indent=2, default=str)
print(f"\nResults saved to {REPORT_DIR}/06_robustness_results.json")

with open(os.path.join(REPORT_DIR, '06_robustness.md'), 'w') as f:
    f.write("# Phase 6: Robustness Checks\n\n")
    f.write(f"**Date**: 2026-08-16 | **Base Model**: Combined Word+Char SVM | **Seed**: {SEED}\n\n")
    f.write(f"## Base Performance\n\n")
    f.write(f"Macro F1 (combined text, no perturbation): **{base_macro:.4f}**\n\n")
    f.write("## Results\n\n")
    f.write("| Perturbation | Macro F1 | Delta | Min Recall | Status |\n")
    f.write("|---|---|---|---|---|\n")
    for r in results:
        f.write(f"| {r['perturbation']} | {r['macro_f1']:.4f} | {r['delta']:+.4f} | {r['min_recall']:.4f} | {r['status']} |\n")
    f.write(f"\n## Conclusion\n\n")
    if len(failed) == 0:
        f.write("All robustness checks passed (max drop <= 0.05).\n")
    else:
        f.write(f"{len(failed)} perturbation(s) caused >0.05 performance drop. Investigate before proceeding.\n")
    f.write(f"\n## Per-Perturbation Details\n\n")
    for r in results:
        f.write(f"### {r['perturbation']}\n")
        f.write(f"- Macro F1: {r['macro_f1']:.4f} (delta: {r['delta']:+.4f})\n")
        f.write(f"- Min Recall: {r['min_recall']:.4f}\n")
        low_cats = [(k, v) for k, v in r['per_class_recall'].items() if v < 0.30]
        if low_cats:
            f.write(f"- Low recall categories (<0.30): {', '.join(k for k, v in sorted(low_cats, key=lambda x: x[1]))}\n")
        f.write("\n")
print(f"Report saved to {REPORT_DIR}/06_robustness.md")

print(f"\n{'='*70}")
print("PHASE 6 COMPLETE")
print("=" * 70)
