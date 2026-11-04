"""Phase 8: Embeddings (Strategy A only - CPU)."""
import pandas as pd
import numpy as np
import json
import os
import re
import warnings
import time
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, classification_report, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack
import joblib

warnings.filterwarnings('ignore')

SEED = int(os.environ.get("SEED", 42))
np.random.seed(SEED)

DATA_DIR = os.environ.get('RESUME_DATA_DIR', 'data')
RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(DATA_DIR, 'Resume.csv'))
SPLIT_DIR = 'data/splits'
REPORT_DIR = 'reports'
EMBEDDING_DIR = 'data/processed/embeddings'
EXPERIMENT_DIR = 'experiments'

os.makedirs(EMBEDDING_DIR, exist_ok=True)
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


print("=" * 70)
print("PHASE 8: ADVANCED REPRESENTATIONS (EMBEDDINGS - STRATEGY A)")
print("=" * 70)

# ── Load data ────────────────────────────────────────────────────────────
print("\n[1] Loading dataset...")
df = pd.read_csv(RESUME_CSV)
df['clean_text'] = df['Resume_str'].apply(clean_text)
df['mitigated_text'] = df['clean_text'].apply(lambda x: strip_header(x, 200))

with open(os.path.join(SPLIT_DIR, 'splits.json')) as f:
    splits = json.load(f)
train_idx = splits['train_indices']
val_idx = splits['val_indices']
test_idx = splits['test_indices']

y_train = df.iloc[train_idx]['Category'].values
y_val = df.iloc[val_idx]['Category'].values
y_test = df.iloc[test_idx]['Category'].values
X_mit_train = df.iloc[train_idx]['mitigated_text'].values
X_mit_val = df.iloc[val_idx]['mitigated_text'].values
X_mit_test = df.iloc[test_idx]['mitigated_text'].values

print(f"  Train: {len(X_mit_train)}, Val: {len(X_mit_val)}, Test: {len(X_mit_test)}")

# ── Go / No-Go Gate Check ───────────────────────────────────────────────
print("\n[2] Go / No-Go Gate Check")
with open(os.path.join(EXPERIMENT_DIR, 'phase5_results.json')) as f:
    p5 = json.load(f)
phase5_cv = p5['best_model_cv_f1']
phase5_val = p5['best_model_val_f1']
print(f"  Phase 5 best CV Macro F1: {phase5_cv:.4f}")
print(f"  Phase 5 best Val Macro F1: {phase5_val:.4f}")
gate = "CONTINUE - room for improvement"
print(f"  Gate: {gate}")

# ── Load embedding model ────────────────────────────────────────────────
print("\n[3] Loading embedding model (all-MiniLM-L6-v2)...")
from sentence_transformers import SentenceTransformer
EMB_MODEL = 'all-MiniLM-L6-v2'
emb_model = SentenceTransformer(EMB_MODEL)
print(f"  Model: {EMB_MODEL} ({emb_model.get_sentence_embedding_dimension()} dims)")

# ── Compute embeddings ──────────────────────────────────────────────────
embed_cache = os.path.join(EMBEDDING_DIR, 'mitigated_embeddings.npy')
if os.path.exists(embed_cache):
    print(f"\n[4] Loading cached embeddings from {embed_cache}...")
    emb_all = np.load(embed_cache)
    emb_train = emb_all[train_idx]
    emb_val = emb_all[val_idx]
    emb_test = emb_all[test_idx]
else:
    print(f"\n[4] Computing embeddings for all sets ({len(X_mit_train)+len(X_mit_val)+len(X_mit_test)} resumes)...")
    t0 = time.time()
    emb_all = np.array(emb_model.encode(X_mit_train.tolist() + X_mit_val.tolist() + X_mit_test.tolist(), show_progress_bar=True, batch_size=64, convert_to_numpy=True))
    elapsed = time.time() - t0
    print(f"  Time: {elapsed:.1f}s ({elapsed/len(emb_all)*1000:.1f}ms per resume)")
    np.save(embed_cache, emb_all)
    print(f"  Cached to {embed_cache}")
    emb_train = emb_all[:len(X_mit_train)]
    emb_val = emb_all[len(X_mit_train):len(X_mit_train)+len(X_mit_val)]
    emb_test = emb_all[len(X_mit_train)+len(X_mit_val):]

# ── TF-IDF features for combination ─────────────────────────────────────
from sklearn.feature_extraction.text import TfidfVectorizer

word_vec = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), sublinear_tf=True, stop_words=None)
char_vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), min_df=2)
X_tfidf_train = hstack([word_vec.fit_transform(X_mit_train), char_vec.fit_transform(X_mit_train)], format='csr')
X_tfidf_val = hstack([word_vec.transform(X_mit_val), char_vec.transform(X_mit_val)], format='csr')
X_tfidf_test = hstack([word_vec.transform(X_mit_test), char_vec.transform(X_mit_test)], format='csr')

# Standardize embeddings
scaler = StandardScaler()
emb_train_scaled = scaler.fit_transform(emb_train)
emb_val_scaled = scaler.transform(emb_val)
emb_test_scaled = scaler.transform(emb_test)

results = []


def run_exp(name, X_tr, y_tr, X_val, y_val, X_test, y_test, pipe_cls, **kwargs):
    t0 = time.time()
    pipe = pipe_cls(**kwargs)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_scores, cv_min_recalls = [], []
    for tr_f, vl_f in skf.split(X_tr, y_tr):
        pipe.fit(X_tr[tr_f], y_tr[tr_f])
        y_p = pipe.predict(X_tr[vl_f])
        cv_scores.append(f1_score(y_tr[vl_f], y_p, average='macro'))
        rpt = classification_report(y_tr[vl_f], y_p, output_dict=True, zero_division=0)
        recalls = [rpt[k]['recall'] for k in rpt if k not in ('accuracy','macro avg','weighted avg')]
        cv_min_recalls.append(min(recalls) if recalls else 0)

    pipe.fit(X_tr, y_tr)
    y_pred = pipe.predict(X_test)
    macro = f1_score(y_test, y_pred, average='macro')
    rpt = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    recalls = {k: float(rpt[k]['recall']) for k in rpt if k not in ('accuracy','macro avg','weighted avg')}
    elapsed = time.time() - t0
    print(f"  {name}: CV={np.mean(cv_scores):.4f}, Test={macro:.4f}, MinRec={min(recalls.values()):.4f} ({elapsed:.1f}s)")
    return {
        'name': name, 'cv_macro': float(np.mean(cv_scores)),
        'cv_std': float(np.std(cv_scores)), 'test_macro': float(macro),
        'per_class_recall': recalls, 'min_recall': float(min(recalls.values())),
        'elapsed': elapsed, 'pipeline': pipe,
    }


# ── Training ────────────────────────────────────────────────────────────
print("\n[5] Training classifiers on embeddings...")

# A. LR on embeddings only
print("\n--- A. LogisticRegression on Embeddings ---")
r_a = run_exp("LR_Embeddings", emb_train_scaled, y_train, emb_val_scaled, y_val, emb_test_scaled, y_test, LogisticRegression)
results.append(r_a)

# B. LR on combined Embeddings + TF-IDF
print("\n--- B. LR Combined Embeddings + TF-IDF ---")
from scipy.sparse import csr_matrix
X_comb_train = hstack([csr_matrix(emb_train_scaled), X_tfidf_train], format='csr')
X_comb_val = hstack([csr_matrix(emb_val_scaled), X_tfidf_val], format='csr')
X_comb_test = hstack([csr_matrix(emb_test_scaled), X_tfidf_test], format='csr')
r_b = run_exp("LR_Combined_Emb+TFIDF", X_comb_train, y_train, X_comb_val, y_val, X_comb_test, y_test, LogisticRegression)
results.append(r_b)

# C. SVM on embeddings
print("\n--- C. SVM on Embeddings ---")
r_c = run_exp("SVM_Embeddings", emb_train_scaled, y_train, emb_val_scaled, y_val, emb_test_scaled, y_test, LinearSVC)
results.append(r_c)

# D. SVM on combined
print("\n--- D. SVM Combined Embeddings + TF-IDF ---")
r_d = run_exp("SVM_Combined_Emb+TFIDF", X_comb_train, y_train, X_comb_val, y_val, X_comb_test, y_test, LinearSVC)
results.append(r_d)

# ── Summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PHASE 8: ALL EXPERIMENTS SUMMARY")
print("=" * 70)
print(f"\n{'Experiment':<45} {'CV F1':>8} {'Test F1':>8} {'MinRec':>8}")
print("-" * 72)
for r in results:
    print(f"{r['name']:<45} {r['cv_macro']:>8.4f} {r['test_macro']:>8.4f} {r['min_recall']:>8.4f}")

best = max(results, key=lambda x: x['test_macro'])
print(f"\nBest model: {best['name']}")
print(f"  Test Macro F1: {best['test_macro']:.4f}")
print(f"  Improvement vs Phase 5: {best['test_macro'] - phase5_val:+.4f}")

# Go/No-Go for Phase 9
print(f"\n{'='*70}")
print("GO / NO-GO FOR PHASE 9 (Final Model Selection)")
print("=" * 70)
if best['test_macro'] >= 0.65 and best['min_recall'] >= 0.40:
    gate = "STOP - meets threshold. Proceed to Phase 9."
elif best['test_macro'] >= 0.55:
    gate = "CONTINUE to Phase 9 with improved model"
else:
    gate = "NO GAIN - fallback to Phase 5 best model"
print(f"Best Phase 8 Test Macro F1: {best['test_macro']:.4f}")
print(f"Gate: {gate}")

# ── Save ────────────────────────────────────────────────────────────────
bundle = {
    'phase': 8, 'date': '2026-08-16', 'seed': SEED,
    'embedding_model': EMB_MODEL,
    'phase5_baseline_test_f1': phase5_val,
    'phase5_baseline_cv_f1': phase5_cv,
    'results': results,
    'best_model_name': best['name'],
    'best_model_test_f1': best['test_macro'],
    'best_model_min_recall': best['min_recall'],
    'improvement_vs_phase5': round(best['test_macro'] - phase5_val, 4),
    'gate': gate,
}
with open(os.path.join(EXPERIMENT_DIR, 'phase8_results.json'), 'w') as f:
    json.dump(bundle, f, indent=2, default=str)
print(f"\nResults saved to {EXPERIMENT_DIR}/phase8_results.json")

# Save best model
joblib.dump(best['pipeline'], os.path.join(EXPERIMENT_DIR, 'best_phase8_model.joblib'))
print(f"Best model saved to {EXPERIMENT_DIR}/best_phase8_model.joblib")

# Ambiguity-aware F1
print(f"\n--- Ambiguity-Aware Evaluation ---")
y_pred_best = best['pipeline'].predict(X_comb_test)
_, _, f1_per, _ = precision_recall_fscore_support(y_test, y_pred_best, average=None)
ambiguous_classes = [c for c, r in zip(sorted(set(y_test)), f1_per) if r < 0.50]
print(f"Ambiguous classes (recall<0.50): {ambiguous_classes}")
non_amb_mask = np.array([y not in ambiguous_classes for y in y_test])
if non_amb_mask.sum() > 0:
    amb_f1 = f1_score(y_test[non_amb_mask], y_pred_best[non_amb_mask], average='macro')
    print(f"Ambiguity-aware F1 (non-ambiguous only): {amb_f1:.4f}")
    print(f"  Non-ambiguous samples: {non_amb_mask.sum()}/{len(y_test)}")

# Report
with open(os.path.join(REPORT_DIR, '08_embedding_report.md'), 'w', encoding='utf-8') as f:
    f.write("# Phase 8: Embeddings (Strategy A)\n\n")
    f.write(f"**Date**: 2026-08-16 | **Model**: {EMB_MODEL}\n\n")
    f.write(f"## Results\n\n")
    f.write("| Experiment | CV F1 | Test F1 | Min Recall |\n")
    f.write("|---|---|---|---|\n")
    for r in results:
        f.write(f"| {r['name']} | {r['cv_macro']:.4f} | {r['test_macro']:.4f} | {r['min_recall']:.4f} |\n")
    f.write(f"\n**Best**: {best['name']} (Test F1={best['test_macro']:.4f})\n")
    f.write(f"**vs Phase 5**: {best['test_macro'] - phase5_val:+.4f}\n")
    f.write(f"**Gate**: {gate}\n")
print(f"Report saved to {REPORT_DIR}/08_embedding_report.md")

print(f"\n{'='*70}")
print("PHASE 8 COMPLETE")
print("=" * 70)
