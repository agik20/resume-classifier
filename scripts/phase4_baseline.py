import pandas as pd
import numpy as np
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, classification_report
import warnings
warnings.filterwarnings('ignore')

SEED = int(os.environ.get("SEED", 42))
np.random.seed(SEED)

DATA_DIR = os.environ.get('RESUME_DATA_DIR', 'data')
RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(DATA_DIR, 'Resume.csv'))
SPLIT_DIR = 'data/splits'
REPORT_DIR = 'reports'

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


# Load dataset and splits
print("Loading dataset...")
df = pd.read_csv(RESUME_CSV)
print(f"Total rows: {len(df)}")

df['clean_text'] = df['Resume_str'].apply(clean_text)
df['mitigated_text'] = df['clean_text'].apply(lambda x: strip_header(x, 200))

with open(os.path.join(SPLIT_DIR, 'splits.json')) as f:
    splits = json.load(f)
train_idx = splits['train_indices']
val_idx = splits['val_indices']
test_idx = splits['test_indices']

print(f"Train: {len(train_idx)}, Val: {len(val_idx)}, Test: {len(test_idx)}")

y_train = df.iloc[train_idx]['Category'].values
y_val = df.iloc[val_idx]['Category'].values

X_raw_train = df.iloc[train_idx]['clean_text'].values
X_mit_train = df.iloc[train_idx]['mitigated_text'].values
X_raw_val = df.iloc[val_idx]['clean_text'].values
X_mit_val = df.iloc[val_idx]['mitigated_text'].values


def run_baseline(X_train, y_train, X_val, y_val, model_type, vectorizer_kwargs, clf_kwargs):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores, cv_min_recalls = [], []

    for train_f, val_f in skf.split(X_train, y_train):
        X_tr, X_vl = X_train[train_f], X_train[val_f]
        y_tr, y_vl = y_train[train_f], y_train[val_f]

        vectorizer = TfidfVectorizer(**vectorizer_kwargs)
        X_tr_tfidf = vectorizer.fit_transform(X_tr)
        X_vl_tfidf = vectorizer.transform(X_vl)

        if model_type == 'svm':
            clf = LinearSVC(**clf_kwargs)
        else:
            clf = LogisticRegression(**clf_kwargs)
        clf.fit(X_tr_tfidf, y_tr)
        y_pred = clf.predict(X_vl_tfidf)

        cv_scores.append(f1_score(y_vl, y_pred, average='macro'))
        report = classification_report(y_vl, y_pred, output_dict=True, zero_division=0)
        recalls = [v['recall'] for k, v in report.items() if k not in ('accuracy', 'macro avg', 'weighted avg')]
        cv_min_recalls.append(min(recalls) if recalls else 0)

    # Final val eval
    vectorizer = TfidfVectorizer(**vectorizer_kwargs)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_val_tfidf = vectorizer.transform(X_val)
    if model_type == 'svm':
        clf = LinearSVC(**clf_kwargs)
    else:
        clf = LogisticRegression(**clf_kwargs)
    clf.fit(X_train_tfidf, y_train)
    y_pred_val = clf.predict(X_val_tfidf)

    val_macro = f1_score(y_val, y_pred_val, average='macro')
    val_report = classification_report(y_val, y_pred_val, output_dict=True, zero_division=0)
    val_per_class = {k: v['recall'] for k, v in val_report.items()
                     if k not in ('accuracy', 'macro avg', 'weighted avg')}

    return {
        'cv_macro_f1_mean': float(np.mean(cv_scores)),
        'cv_macro_f1_std': float(np.std(cv_scores)),
        'cv_min_recall_mean': float(np.mean(cv_min_recalls)),
        'val_macro_f1': float(val_macro),
        'val_per_class_recall': val_per_class,
    }


print("\n" + "=" * 70)
print("PHASE 4: BASELINE MODELS (Raw vs Mitigated)")
print("=" * 70)

results = {}

# B1: LR - Raw
print("\n[B1] Logistic Regression - Raw Text (5-fold CV)...")
results['B1_LR_Raw'] = run_baseline(
    X_raw_train, y_train, X_raw_val, y_val, 'lr',
    {'ngram_range': (1, 2), 'max_features': 50000, 'sublinear_tf': True},
    {'C': 1.0, 'class_weight': 'balanced', 'max_iter': 10000, 'random_state': SEED}
)
print(f"  CV: {results['B1_LR_Raw']['cv_macro_f1_mean']:.4f} +/- {results['B1_LR_Raw']['cv_macro_f1_std']:.4f}")
print(f"  Val: {results['B1_LR_Raw']['val_macro_f1']:.4f}")

# B2: LR - Mitigated
print("\n[B2] Logistic Regression - Mitigated Text (5-fold CV)...")
results['B2_LR_Mitigated'] = run_baseline(
    X_mit_train, y_train, X_mit_val, y_val, 'lr',
    {'ngram_range': (1, 2), 'max_features': 50000, 'sublinear_tf': True},
    {'C': 1.0, 'class_weight': 'balanced', 'max_iter': 10000, 'random_state': SEED}
)
print(f"  CV: {results['B2_LR_Mitigated']['cv_macro_f1_mean']:.4f} +/- {results['B2_LR_Mitigated']['cv_macro_f1_std']:.4f}")
print(f"  Val: {results['B2_LR_Mitigated']['val_macro_f1']:.4f}")

# B3: SVM - Raw
print("\n[B3] Linear SVM - Raw Text (5-fold CV)...")
results['B3_SVM_Raw'] = run_baseline(
    X_raw_train, y_train, X_raw_val, y_val, 'svm',
    {'ngram_range': (1, 2), 'max_features': 50000, 'sublinear_tf': True},
    {'C': 1.0, 'class_weight': 'balanced', 'max_iter': 10000}
)
print(f"  CV: {results['B3_SVM_Raw']['cv_macro_f1_mean']:.4f} +/- {results['B3_SVM_Raw']['cv_macro_f1_std']:.4f}")
print(f"  Val: {results['B3_SVM_Raw']['val_macro_f1']:.4f}")

# B4: SVM - Mitigated
print("\n[B4] Linear SVM - Mitigated Text (5-fold CV)...")
results['B4_SVM_Mitigated'] = run_baseline(
    X_mit_train, y_train, X_mit_val, y_val, 'svm',
    {'ngram_range': (1, 2), 'max_features': 50000, 'sublinear_tf': True},
    {'C': 1.0, 'class_weight': 'balanced', 'max_iter': 10000}
)
print(f"  CV: {results['B4_SVM_Mitigated']['cv_macro_f1_mean']:.4f} +/- {results['B4_SVM_Mitigated']['cv_macro_f1_std']:.4f}")
print(f"  Val: {results['B4_SVM_Mitigated']['val_macro_f1']:.4f}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"{'Model':<35} {'CV Macro F1':>15} {'Val Macro F1':>15} {'Min Recall':>12}")
print("-" * 77)
for key, r in results.items():
    min_rec = min(r['val_per_class_recall'].values()) if r['val_per_class_recall'] else 0
    label = key.replace('_', ' ')
    print(f"{label:<35} {r['cv_macro_f1_mean']:>15.4f} {r['val_macro_f1']:>15.4f} {min_rec:>12.4f}")

# Leakage impact
print("\n" + "=" * 70)
print("LEAKAGE IMPACT (Raw vs Mitigated)")
print("=" * 70)
lr_delta = results['B1_LR_Raw']['cv_macro_f1_mean'] - results['B2_LR_Mitigated']['cv_macro_f1_mean']
svm_delta = results['B3_SVM_Raw']['cv_macro_f1_mean'] - results['B4_SVM_Mitigated']['cv_macro_f1_mean']
print(f"LR delta: {lr_delta:.4f}")
print(f"SVM delta: {svm_delta:.4f}")

# Per-class recall for best mitigated
print("\n" + "=" * 70)
print("PER-CLASS RECALL (SVM Mitigated)")
print("=" * 70)
best = results['B4_SVM_Mitigated']
below_040, below_020 = [], []
for cat in sorted(best['val_per_class_recall'].keys()):
    rec = best['val_per_class_recall'][cat]
    status = "LOW" if rec < 0.40 else ("CRIT" if rec < 0.20 else "OK")
    if rec < 0.40:
        below_040.append((cat, rec))
    if rec < 0.20:
        below_020.append((cat, rec))
    print(f"  {cat:<30} {rec:.4f}  [{status}]")

print(f"\n< 0.40: {len(below_040)} categories | < 0.20: {len(below_020)} categories")
for cat, rec in sorted(below_040, key=lambda x: x[1]):
    print(f"  - {cat}: {rec:.4f}")

# Go/No-Go gate
print("\n" + "=" * 70)
print("GO / NO-GO GATE")
print("=" * 70)
best_f1 = results['B4_SVM_Mitigated']['cv_macro_f1_mean']
best_min_rec = min(results['B4_SVM_Mitigated']['val_per_class_recall'].values())
print(f"Best mitigated Macro F1: {best_f1:.4f}")
print(f"Best mitigated min recall: {best_min_rec:.4f}")

if best_f1 >= 0.65 and best_min_rec >= 0.40:
    gate = "STOP - Baseline meets threshold. Skip Phase 5-8."
elif best_f1 >= 0.60 and best_min_rec >= 0.35:
    gate = "CONTINUE to Phase 5 - room for improvement"
elif best_f1 < 0.50:
    gate = "PAUSE - revisit Phase 1-1b"
else:
    gate = "CONTINUE (cautious) - marginal baseline"
print(f"\nGATE: {gate}")

# Save
with open(os.path.join(REPORT_DIR, '04_baseline_results.json'), 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {REPORT_DIR}/04_baseline_results.json")
