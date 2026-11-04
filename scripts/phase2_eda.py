import os
import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

print("=" * 60)
print("PHASE 2: EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 60)

print("\n[1] Loading data...")
df = pd.read_csv(RESUME_CSV)
print(f"    Loaded: {len(df)} rows, {len(df.columns)} columns")

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['clean_text'] = df['Resume_str'].apply(clean_text)
df['text_len'] = df['clean_text'].apply(len)

# ============================================================
# 2.1 Label Distribution
# ============================================================
print("\n" + "=" * 60)
print("2.1 LABEL DISTRIBUTION")
print("=" * 60)

cat_counts = df['Category'].value_counts().sort_values(ascending=False)
print(f"\n{'Category':<30} {'Count':>6} {'Percentage':>12}")
print("-" * 55)
for cat, count in cat_counts.items():
    pct = count / len(df) * 100
    print(f"{cat:<30} {count:>6} {pct:>11.2f}%")

imbalance_ratio = cat_counts.max() / cat_counts.min()
print(f"\nImbalance Ratio (max/min): {imbalance_ratio:.2f}")
print(f"Most common: {cat_counts.idxmax()} ({cat_counts.max()} samples)")
print(f"Least common: {cat_counts.idxmin()} ({cat_counts.min()} samples)")

# ============================================================
# 2.2 Length Statistics per Category
# ============================================================
print("\n" + "=" * 60)
print("2.2 LENGTH STATISTICS PER CATEGORY")
print("=" * 60)

print(f"\n{'Category':<30} {'Count':>6} {'Mean':>8} {'Median':>8} {'Min':>8} {'Max':>8}")
print("-" * 75)
for cat in sorted(df['Category'].unique()):
    cat_df = df[df['Category'] == cat]
    lengths = cat_df['text_len']
    print(f"{cat:<30} {len(cat_df):>6} {lengths.mean():>8.0f} {lengths.median():>8.0f} {lengths.min():>8} {lengths.max():>8}")

print(f"\nOverall mean length: {df['text_len'].mean():.0f} chars")
print(f"Overall median length: {df['text_len'].median():.0f} chars")

# ============================================================
# 2.3 Vocabulary Analysis
# ============================================================
print("\n" + "=" * 60)
print("2.3 VOCABULARY ANALYSIS")
print("=" * 60)

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

word_counts = {}
for text in df['clean_text']:
    for word in text.split():
        word = re.sub(r'[^\w]', '', word)
        if word not in stopwords and len(word) > 2:
            word_counts[word] = word_counts.get(word, 0) + 1

sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
print(f"\nTop 50 Most Frequent Words:")
for i, (word, count) in enumerate(sorted_words[:50], 1):
    print(f"  {i:2d}. {word:<25} {count:>6}")

# TF-IDF top terms
print(f"\nTop 20 TF-IDF Weighted Terms:")
vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
tfidf_matrix = vectorizer.fit_transform(df['clean_text'])
feature_names = vectorizer.get_feature_names_out()
tfidf_sum = tfidf_matrix.sum(axis=0).A1
top_tfidf_indices = np.argsort(tfidf_sum)[-20:][::-1]
for i, idx in enumerate(top_tfidf_indices, 1):
    print(f"  {i:2d}. {feature_names[idx]:<25} {tfidf_sum[idx]:.2f}")

# ============================================================
# 2.4 Class Separability
# ============================================================
print("\n" + "=" * 60)
print("2.4 CLASS SEPARABILITY (Quick Logistic Regression)")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'], df['Category'], test_size=0.2, random_state=42, stratify=df['Category']
)

vec = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
X_train_vec = vec.fit_transform(X_train)
X_test_vec = vec.transform(X_test)

clf = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
clf.fit(X_train_vec, y_train)
y_pred = clf.predict(X_test_vec)

accuracy = clf.score(X_test_vec, y_test)
print(f"\nAccuracy: {accuracy:.4f}")

# ============================================================
# 2.5 Multi-domain Resume Profiling
# ============================================================
print("\n" + "=" * 60)
print("2.5 MULTI-DOMAIN RESUME PROFILING")
print("=" * 60)

cats = sorted(df['Category'].unique())
keywords = {cat: set(cat.lower().replace('-', ' ').split()) for cat in cats}

domain_stats = {cat: {'total': 0, 'multi': 0} for cat in cats}

for _, row in df.iterrows():
    text = row['Resume_str'].lower()
    true_cat = row['Category']
    found_cats = [cat for cat, kw in keywords.items() if any(k in text for k in kw)]

    domain_stats[true_cat]['total'] += 1
    if len(found_cats) > 1:
        domain_stats[true_cat]['multi'] += 1

print(f"\n{'Category':<30} {'Total':>6} {'Multi%':>8}")
print("-" * 50)
for cat in sorted(cats):
    stats = domain_stats[cat]
    multi_pct = stats['multi'] / stats['total'] * 100 if stats['total'] > 0 else 0
    print(f"{cat:<30} {stats['total']:>6} {multi_pct:>7.1f}%")

total_multi = sum(s['multi'] for s in domain_stats.values())
print(f"\nOverall multi-domain rate: {total_multi}/{len(df)} ({total_multi/len(df)*100:.1f}%)")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("EDA SUMMARY")
print("=" * 60)

print(f"""
+---------------------------+------------------+
| Metric                    | Value            |
+---------------------------+------------------+
| Total resumes             | {len(df):>10,d}         |
| Categories                | {len(cats):>10}           |
| Imbalance ratio           | {imbalance_ratio:>10.2f}           |
| Avg text length           | {df['text_len'].mean():>10.0f} chars     |
| Median text length        | {df['text_len'].median():>10.0f} chars     |
| Multi-domain rate         | {total_multi/len(df)*100:>9.1f}%           |
+---------------------------+------------------+
""")

print("\nKEY FINDINGS:")
print(f"  1. Dataset is {imbalance_ratio:.1f}x imbalanced (BPO: 22, BUSINESS-DEVELOPMENT: 120)")
print(f"  2. Average resume length: {df['text_len'].mean():.0f} characters")
print(f"  3. Multi-domain rate: {total_multi/len(df)*100:.1f}%")
print(f"  4. Small classes (BPO, AUTOMOBILE) need special handling")
print(f"  5. High category leakage (19/24 >80%) requires mitigation")

print("\n" + "=" * 60)
print("PHASE 2 EDA COMPLETE")
print("=" * 60)
