import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
import re

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

print("Loading data...")
df = pd.read_csv(RESUME_CSV)

def strip_header(text, chars=200):
    if pd.isna(text):
        return text
    text = str(text)
    if len(text) > chars:
        return text[chars:]
    return text

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

print("\n=== Preparing Data ===")
df['clean_text'] = df['Resume_str'].apply(clean_text)
df['mitigated_text'] = df['clean_text'].apply(lambda x: strip_header(x, 200))

print("\n=== Baseline: Raw Text ===")
vectorizer_raw = TfidfVectorizer(ngram_range=(1, 2), max_features=50000)
X_raw = vectorizer_raw.fit_transform(df['clean_text'])
y = df['Category'].values

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
raw_scores = []
for train_idx, val_idx in skf.split(X_raw, y):
    X_train, X_val = X_raw[train_idx], X_raw[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    clf = LinearSVC(class_weight='balanced', max_iter=10000)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_val)
    raw_scores.append(f1_score(y_val, y_pred, average='macro'))

print(f"Macro F1: {np.mean(raw_scores):.4f} +/- {np.std(raw_scores):.4f}")

print("\n=== Baseline: Mitigated Text (Header Stripped) ===")
vectorizer_mit = TfidfVectorizer(ngram_range=(1, 2), max_features=50000)
X_mit = vectorizer_mit.fit_transform(df['mitigated_text'])

mit_scores = []
for train_idx, val_idx in skf.split(X_mit, y):
    X_train, X_val = X_mit[train_idx], X_mit[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
    clf = LinearSVC(class_weight='balanced', max_iter=10000)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_val)
    mit_scores.append(f1_score(y_val, y_pred, average='macro'))

print(f"Macro F1: {np.mean(mit_scores):.4f} +/- {np.std(mit_scores):.4f}")

print("\n=== Comparison ===")
delta = np.mean(raw_scores) - np.mean(mit_scores)
print(f"Raw Macro F1: {np.mean(raw_scores):.4f}")
print(f"Mitigated Macro F1: {np.mean(mit_scores):.4f}")
print(f"Delta: {delta:.4f}")

if delta > 0.05:
    print("\nConclusion: Leakage is REAL and significant (>0.05 delta)")
elif delta > 0.02:
    print("\nConclusion: Leakage has moderate impact (0.02-0.05 delta)")
else:
    print("\nConclusion: Leakage impact is minimal (<0.02 delta)")

print("\nPhase 1b analysis complete!")
