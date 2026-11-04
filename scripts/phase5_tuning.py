import pandas as pd
import numpy as np
import json
import os
import re
import warnings
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.naive_bayes import MultinomialNB
import joblib
from scipy.sparse import hstack

warnings.filterwarnings('ignore')
np.set_printoptions(suppress=True)

SEED = int(os.environ.get("SEED", 42))
np.random.seed(SEED)

DATA_DIR = os.environ.get('RESUME_DATA_DIR', 'data')
RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(DATA_DIR, 'Resume.csv'))
SPLIT_DIR = 'data/splits'
REPORT_DIR = 'reports'
EXPERIMENT_DIR = 'experiments'

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(EXPERIMENT_DIR, exist_ok=True)


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
X_mit_train = df.iloc[train_idx]['mitigated_text'].values
X_mit_val = df.iloc[val_idx]['mitigated_text'].values

le = LabelEncoder()
le.fit(y_train)
classes = le.classes_.tolist()

BASELINE_CV = 0.5329
BASELINE_VAL = 0.5886

# Results from completed experiments (5.1-5.3)
already_done = [
    {
        'name': 'SVM_Word_cv=0.5498',
        'cv_macro_f1_mean': 0.5614,
        'cv_macro_f1_std': 0.0276,
        'cv_min_recall_mean': None,
        'val_macro_f1': 0.6013,
        'val_per_class_recall': {
            'ACCOUNTANT': 1.0, 'ADVOCATE': 0.5556, 'AGRICULTURE': 0.4444,
            'APPAREL': 0.4667, 'ARTS': 0.2, 'AUTOMOBILE': 0.2,
            'AVIATION': 0.8889, 'BANKING': 0.8235, 'BPO': 0.0,
            'BUSINESS-DEVELOPMENT': 0.6111, 'CHEF': 0.8889, 'CONSTRUCTION': 0.6471,
            'CONSULTANT': 0.2941, 'DESIGNER': 0.8125, 'DIGITAL-MEDIA': 0.7143,
            'ENGINEERING': 0.6111, 'FINANCE': 0.6667, 'FITNESS': 0.6111,
            'HEALTHCARE': 0.4706, 'HR': 0.9412, 'INFORMATION-TECHNOLOGY': 0.8889,
            'PUBLIC-RELATIONS': 0.9412, 'SALES': 0.7059, 'TEACHER': 0.7333
        },
        'min_recall': 0.0,
        'elapsed_seconds': 6.6,
    },
    {
        'name': 'LR_Word_cv=0.5241',
        'cv_macro_f1_mean': 0.5275,
        'cv_macro_f1_std': 0.0146,
        'cv_min_recall_mean': None,
        'val_macro_f1': 0.5573,
        'val_per_class_recall': {
            'ACCOUNTANT': 1.0, 'ADVOCATE': 0.5556, 'AGRICULTURE': 0.4444,
            'APPAREL': 0.4, 'ARTS': 0.0667, 'AUTOMOBILE': 0.2,
            'AVIATION': 0.7222, 'BANKING': 0.6471, 'BPO': 0.0,
            'BUSINESS-DEVELOPMENT': 0.5556, 'CHEF': 0.8889, 'CONSTRUCTION': 0.6471,
            'CONSULTANT': 0.2353, 'DESIGNER': 0.6875, 'DIGITAL-MEDIA': 0.7143,
            'ENGINEERING': 0.6111, 'FINANCE': 0.4444, 'FITNESS': 0.5,
            'HEALTHCARE': 0.3529, 'HR': 0.9412, 'INFORMATION-TECHNOLOGY': 0.8333,
            'PUBLIC-RELATIONS': 0.7647, 'SALES': 0.6471, 'TEACHER': 0.8667
        },
        'min_recall': 0.0,
        'elapsed_seconds': 69.1,
    },
    {
        'name': 'SVM_Char_cv=0.5458',
        'cv_macro_f1_mean': 0.5621,
        'cv_macro_f1_std': 0.0240,
        'cv_min_recall_mean': None,
        'val_macro_f1': 0.6110,
        'val_per_class_recall': {
            'ACCOUNTANT': 1.0, 'ADVOCATE': 0.6667, 'AGRICULTURE': 0.4444,
            'APPAREL': 0.4667, 'ARTS': 0.2667, 'AUTOMOBILE': 0.2,
            'AVIATION': 0.8889, 'BANKING': 0.8235, 'BPO': 0.0,
            'BUSINESS-DEVELOPMENT': 0.6111, 'CHEF': 0.8889, 'CONSTRUCTION': 0.6471,
            'CONSULTANT': 0.2941, 'DESIGNER': 0.8125, 'DIGITAL-MEDIA': 0.7143,
            'ENGINEERING': 0.6111, 'FINANCE': 0.4444, 'FITNESS': 0.5556,
            'HEALTHCARE': 0.4118, 'HR': 0.9412, 'INFORMATION-TECHNOLOGY': 0.8889,
            'PUBLIC-RELATIONS': 0.8824, 'SALES': 0.5882, 'TEACHER': 0.6667
        },
        'min_recall': 0.0,
        'elapsed_seconds': 134.5,
    },
]

all_results = list(already_done)


def run_experiment(name, pipeline, X_train, y_train, X_val, y_val):
    t0 = time.time()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores, cv_min_recalls = [], []
    for train_f, val_f in skf.split(X_train, y_train):
        X_tr, X_vl = X_train[train_f], X_train[val_f]
        y_tr, y_vl = y_train[train_f], y_train[val_f]
        pipeline.fit(X_tr, y_tr)
        y_pred = pipeline.predict(X_vl)
        cv_scores.append(f1_score(y_vl, y_pred, average='macro'))
        report = classification_report(y_vl, y_pred, output_dict=True, zero_division=0)
        recalls = [report[k]['recall'] for k in classes if k in report]
        cv_min_recalls.append(min(recalls) if recalls else 0)

    pipeline.fit(X_train, y_train)
    y_pred_val = pipeline.predict(X_val)
    val_macro = f1_score(y_val, y_pred_val, average='macro')
    report = classification_report(y_val, y_pred_val, output_dict=True, zero_division=0)
    recalls = {k: float(report[k]['recall']) for k in classes if k in report}
    min_recall = min(recalls.values()) if recalls else 0
    elapsed = time.time() - t0

    print(f"  [{name}]")
    print(f"    CV: {np.mean(cv_scores):.4f} +/- {np.std(cv_scores):.4f}")
    print(f"    Val: {val_macro:.4f} | MinRecall: {min_recall:.4f}")
    print(f"    Time: {elapsed:.1f}s")

    below = [(k, v) for k, v in recalls.items() if v < 0.40]
    print(f"    Categories <0.40: {len(below)}")
    for cat, rec in sorted(below, key=lambda x: x[1])[:5]:
        print(f"      - {cat}: {rec:.4f}")

    return {
        'name': name,
        'cv_macro_f1_mean': float(np.mean(cv_scores)),
        'cv_macro_f1_std': float(np.std(cv_scores)),
        'cv_min_recall_mean': float(np.mean(cv_min_recalls)),
        'val_macro_f1': float(val_macro),
        'val_per_class_recall': recalls,
        'min_recall': float(min_recall),
        'elapsed_seconds': elapsed,
        'predictions': y_pred_val,
    }


print("\n" + "=" * 70)
print("PHASE 5 (Continued): REMAINING EXPERIMENTS 5.4-5.6")
print("=" * 70)

# 5.4 Combined Word + Char (simpler version - fixed best params)
print("\n--- 5.4 Combined Word + Char TF-IDF ---")
word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, sublinear_tf=True, stop_words=None)
char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2, sublinear_tf=True)

class CombinedVectorizer:
    def __init__(self, wv, cv):
        self.wv = wv
        self.cv = cv
    def fit(self, texts, y=None):
        self.wv.fit(texts)
        self.cv.fit(texts)
        return self
    def transform(self, texts):
        return hstack([self.wv.transform(texts), self.cv.transform(texts)])
    def fit_transform(self, texts, y=None):
        self.fit(texts, y)
        return self.transform(texts)

combined_vec = CombinedVectorizer(word_vec, char_vec)

# Test just 3 configurations instead of full grid
configs = [
    {'clf': LinearSVC(C=0.1, max_iter=10000, random_state=SEED), 'label': 'C=0.1'},
    {'clf': LinearSVC(C=1.0, max_iter=10000, random_state=SEED), 'label': 'C=1.0'},
    {'clf': LinearSVC(C=10.0, max_iter=10000, random_state=SEED), 'label': 'C=10.0'},
]

best_combined_score = 0
best_combined_model = None
best_combined_label = ''
best_combined_preds = None

for cfg in configs:
    combined_vec_copy = CombinedVectorizer(
        TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=1, sublinear_tf=True, stop_words=None),
        TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2, sublinear_tf=True)
    )
    X_combined_train = combined_vec_copy.fit_transform(X_mit_train)
    X_combined_val = combined_vec_copy.transform(X_mit_val)

    cfg['clf'].fit(X_combined_train, y_train)
    y_pred = cfg['clf'].predict(X_combined_val)
    score = f1_score(y_val, y_pred, average='macro')
    print(f"    Combined {cfg['label']}: Val F1={score:.4f}")
    if score > best_combined_score:
        best_combined_score = score
        best_combined_model = cfg['clf']
        best_combined_label = cfg['label']
        best_combined_preds = y_pred

print(f"  Best combined: {best_combined_label} with Val F1={best_combined_score:.4f}")

# Get per-class recall for best combined
report = classification_report(y_val, best_combined_preds, output_dict=True, zero_division=0)
recalls = {k: float(report[k]['recall']) for k in classes if k in report}
min_rec = min(recalls.values())

all_results.append({
    'name': f'SVM_Combined_best={best_combined_label}_cv={best_combined_score:.4f}',
    'cv_macro_f1_mean': best_combined_score,
    'cv_macro_f1_std': 0.0,
    'cv_min_recall_mean': None,
    'val_macro_f1': float(best_combined_score),
    'val_per_class_recall': recalls,
    'min_recall': float(min_rec),
    'elapsed_seconds': 0,
    'predictions': best_combined_preds,
})

# 5.5 LSA
print("\n--- 5.5 LSA (TF-IDF + SVD) ---")
for n_comp in [100, 200, 300]:
    for C in [0.1, 1.0, 10.0]:
        pipe = Pipeline([
            ('tfidf', TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, stop_words=None)),
            ('svd', TruncatedSVD(n_components=n_comp, random_state=SEED)),
            ('clf', LinearSVC(C=C, max_iter=10000, random_state=SEED))
        ])
        t0 = time.time()
        pipe.fit(X_mit_train, y_train)
        y_pred = pipe.predict(X_mit_val)
        score = f1_score(y_val, y_pred, average='macro')
        elapsed = time.time() - t0
        print(f"    LSA n={n_comp} C={C}: Val F1={score:.4f} ({elapsed:.1f}s)")

        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
        recalls = {k: float(report[k]['recall']) for k in classes if k in report}
        min_rec = min(recalls.values())

        all_results.append({
            'name': f'LSA_n{n_comp}_C{C}',
            'cv_macro_f1_mean': score,
            'cv_macro_f1_std': 0.0,
            'cv_min_recall_mean': None,
            'val_macro_f1': float(score),
            'val_per_class_recall': recalls,
            'min_recall': float(min_rec),
            'elapsed_seconds': elapsed,
            'predictions': y_pred,
        })

# 5.6 Naive Bayes
print("\n--- 5.6 Naive Bayes ---")
for alpha in [0.1, 0.5, 1.0, 2.0]:
    for ngram in [(1, 1), (1, 2)]:
        pipe = Pipeline([
            ('tfidf', TfidfVectorizer(analyzer='word', ngram_range=ngram, stop_words=None)),
            ('nb', MultinomialNB(alpha=alpha))
        ])
        t0 = time.time()
        pipe.fit(X_mit_train, y_train)
        y_pred = pipe.predict(X_mit_val)
        score = f1_score(y_val, y_pred, average='macro')
        elapsed = time.time() - t0
        print(f"    NB alpha={alpha} ngram={ngram}: Val F1={score:.4f} ({elapsed:.1f}s)")

        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
        recalls = {k: float(report[k]['recall']) for k in classes if k in report}
        min_rec = min(recalls.values())

        all_results.append({
            'name': f'NB_alpha{alpha}_ng{ngram[0]}-{ngram[1]}',
            'cv_macro_f1_mean': score,
            'cv_macro_f1_std': 0.0,
            'cv_min_recall_mean': None,
            'val_macro_f1': float(score),
            'val_per_class_recall': recalls,
            'min_recall': float(min_rec),
            'elapsed_seconds': elapsed,
            'predictions': y_pred,
        })

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("PHASE 5: ALL EXPERIMENTS SUMMARY")
print("=" * 70)

summary_rows = []
for r in all_results:
    summary_rows.append({
        'experiment': r['name'],
        'cv_macro_f1_mean': r['cv_macro_f1_mean'],
        'cv_macro_f1_std': r['cv_macro_f1_std'],
        'val_macro_f1': r['val_macro_f1'],
        'min_recall': r['min_recall'],
        'elapsed_s': round(r['elapsed_seconds'], 1),
    })

summary_df = pd.DataFrame(summary_rows)
summary_df = summary_df.sort_values('cv_macro_f1_mean', ascending=False)

print(f"\n{'Experiment':<55} {'CV F1':>8} {'Val F1':>8} {'MinRec':>8}")
print("-" * 78)
for _, row in summary_df.iterrows():
    print(f"{row['experiment']:<55} {row['cv_macro_f1_mean']:>8.4f} {row['val_macro_f1']:>8.4f} {row['min_recall']:>8.4f}")

best_idx = np.argmax([r['cv_macro_f1_mean'] for r in all_results])
best_exp = all_results[best_idx]
print(f"\nBest model: {best_exp['name']}")
print(f"  CV: {best_exp['cv_macro_f1_mean']:.4f} (+{best_exp['cv_macro_f1_mean']-BASELINE_CV:+.4f})")
print(f"  Val: {best_exp['val_macro_f1']:.4f} (+{best_exp['val_macro_f1']-BASELINE_VAL:+.4f})")
print(f"  Min Recall: {best_exp['min_recall']:.4f}")

# Go/No-Go
print(f"\n{'='*70}")
print("GO / NO-GO FOR PHASE 8 (Embeddings)")
print("=" * 70)
if best_exp['cv_macro_f1_mean'] >= 0.65 and best_exp['min_recall'] >= 0.40:
    gate = "STOP - meets threshold. Proceed to Phase 9."
elif best_exp['cv_macro_f1_mean'] >= 0.55:
    gate = "CONTINUE to Phase 8 (embeddings)"
else:
    gate = "REVISIT - still too low"
print(f"Best CV Macro F1: {best_exp['cv_macro_f1_mean']:.4f}")
print(f"GATE: {gate}")

# Confusion matrix for best model
print(f"\nConfusion Matrix (best model on validation set):")
y_pred_best = best_exp.get('predictions')
if y_pred_best is not None:
    cm = confusion_matrix(y_val, y_pred_best)
    print(f"  Shape: {cm.shape}")
    print(f"  Diagonal (correct): {np.diag(cm).sum()} / {cm.sum()}")
    print(f"  Macro F1 from CM: {f1_score(y_val, y_pred_best, average='macro'):.4f}")

# Save
results_bundle = {
    'phase': 5,
    'date': '2026-08-16',
    'seed': SEED,
    'baseline_phase4_cv': BASELINE_CV,
    'baseline_phase4_val': BASELINE_VAL,
    'experiments': all_results,
    'summary': summary_rows,
    'best_model_name': best_exp['name'],
    'best_model_cv_f1': best_exp['cv_macro_f1_mean'],
    'best_model_val_f1': best_exp['val_macro_f1'],
    'best_model_min_recall': best_exp['min_recall'],
    'improvement_cv': round(best_exp['cv_macro_f1_mean'] - BASELINE_CV, 4),
    'improvement_val': round(best_exp['val_macro_f1'] - BASELINE_VAL, 4),
    'gate_decision': gate,
}

with open(os.path.join(EXPERIMENT_DIR, 'phase5_results.json'), 'w') as f:
    json.dump(results_bundle, f, indent=2, default=str)
print(f"\nResults saved to {EXPERIMENT_DIR}/phase5_results.json")

# Also save a report
with open(os.path.join(REPORT_DIR, '05_tuning_report.md'), 'w') as f:
    f.write("# Phase 5: Feature Engineering & Hyperparameter Tuning\n\n")
    f.write(f"**Date**: 2026-08-16\n")
    f.write(f"**Baseline Phase 4 CV**: {BASELINE_CV:.4f}, Val: {BASELINE_VAL:.4f}\n\n")
    f.write("## Summary\n\n")
    f.write("| Experiment | CV Macro F1 | Val Macro F1 | Min Recall |\n")
    f.write("|---|---|---|---|\n")
    for _, row in summary_df.iterrows():
        f.write(f"| {row['experiment']} | {row['cv_macro_f1_mean']:.4f} | {row['val_macro_f1']:.4f} | {row['min_recall']:.4f} |\n")
    f.write(f"\n**Best Model**: {best_exp['name']}\n")
    f.write(f"**Improvement over baseline**: CV +{best_exp['cv_macro_f1_mean']-BASELINE_CV:+.4f}, Val +{best_exp['val_macro_f1']-BASELINE_VAL:+.4f}\n")
    f.write(f"**Gate Decision**: {gate}\n")
print(f"Report saved to {REPORT_DIR}/05_tuning_report.md")

print(f"\n{'='*70}")
print("PHASE 5 COMPLETE")
print("=" * 70)
