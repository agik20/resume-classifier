"""Phase 10: Final Inference & Deployment Readiness."""
import os
import joblib
import numpy as np
import pandas as pd
import re
import time
import json
from scipy.sparse import hstack
from sklearn.metrics import classification_report, f1_score
from pathlib import Path

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

print("=" * 70)
print("PHASE 10: FINAL INFERENCE & DEPLOYMENT READINESS")
print("=" * 70)

# Load model
print("\n[1] Loading model components...")
word_vec = joblib.load('experiments/best_phase5_word_vec.joblib')
char_vec = joblib.load('experiments/best_phase5_char_vec.joblib')
clf = joblib.load('experiments/best_phase5_clf.joblib')
print(f"   Word vectorizer: {len(word_vec.vocabulary_)} features")
print(f"   Char vectorizer: {len(char_vec.vocabulary_)} features")
print(f"   Classifier: LinearSVC(C=10)")

# Load test data
print("\n[2] Loading test data...")
df = pd.read_csv(RESUME_CSV)
with open('data/splits/splits.json') as f:
    splits = json.load(f)
test_idx = splits['test_indices']
y_test = df.iloc[test_idx]['Category'].values

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

X_test_raw = df.iloc[test_idx]['Resume_str'].values
X_test_mitigated = np.array([strip_header(clean_text(t), 200) for t in X_test_raw])
print(f"   Test set: {len(X_test_raw)} resumes")

# Evaluate on test set
print("\n[3] Evaluating on held-out test set (FINAL)...")
t0 = time.time()
X_test_features = hstack([
    word_vec.transform(X_test_mitigated),
    char_vec.transform(X_test_mitigated)
])
y_pred = clf.predict(X_test_features)
test_time = time.time() - t0

test_macro = f1_score(y_test, y_pred, average='macro')
print(f"   Test Macro F1: {test_macro:.4f}")
print(f"   Evaluation time: {test_time:.2f}s")

report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
recalls = {k: report[k]['recall'] for k in report if k not in ('accuracy', 'macro avg', 'weighted avg')}
min_rec = min(recalls.values())
low_recall_cats = [(k, v) for k, v in recalls.items() if v < 0.40]

print(f"   Min Recall: {min_rec:.4f}")
print(f"   Categories with recall < 0.40: {len(low_recall_cats)}")
for cat, rec in sorted(low_recall_cats, key=lambda x: x[1]):
    print(f"     - {cat}: {rec:.4f}")

# Latency benchmark
print("\n[4] Latency benchmark (100 predictions)...")
latencies = []
for _ in range(100):
    t_start = time.time()
    clf.predict(X_test_features[:1])
    latencies.append((time.time() - t_start) * 1000)
latencies.sort()
p50 = np.percentile(latencies, 50)
p95 = np.percentile(latencies, 95)
print(f"   p50: {p50:.2f}ms")
print(f"   p95: {p95:.2f}ms")

# Save results
test_results = {
    'phase': 10,
    'date': '2026-08-16',
    'model': 'LinearSVC(C=10) + Combined Word+Char TF-IDF',
    'test_macro_f1': float(test_macro),
    'test_min_recall': float(min_rec),
    'latency_p50_ms': float(p50),
    'latency_p95_ms': float(p95),
    'per_class_recall': {k: float(v) for k, v in sorted(recalls.items())},
    'low_recall_categories': [cat for cat, _ in low_recall_cats],
}
with open('reports/10_test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)
print(f"\n[5] Test results saved to reports/10_test_results.json")

# Test inference
print("\n[6] Testing inference function...")
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from predict import predict_resume
r1 = predict_resume('John Smith Software Engineer Python Django PostgreSQL React Node.js Docker AWS')
print(f"   Test 1 (Software Engineer): {r1['predicted_category']}")
r2 = predict_resume('Jane Doe Nurse BSN ICU Experience Registered')
print(f"   Test 2 (Nurse): {r2['predicted_category']}")

# Summary
print("\n" + "=" * 70)
print("PHASE 10 SUMMARY")
print("=" * 70)
print(f"""
Final Test Results:
  Macro F1:     {test_macro:.4f}
  Min Recall:   {min_rec:.4f}
  Latency p50:  {p50:.2f}ms
  Latency p95:  {p95:.2f}ms

Low Recall Categories:
  {', '.join(cat for cat, _ in low_recall_cats) if low_recall_cats else 'None'}

Deliverables Created:
  - reports/10_test_results.json
  - predict.py (inference function + CLI)
""")
print("=" * 70)
print("PHASE 10 COMPLETE")
print("=" * 70)
