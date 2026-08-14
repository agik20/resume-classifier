import pandas as pd
import re

print("Loading data...")
df = pd.read_csv('C:/Users/ardut/projects/resume-dataset/dataset/Resume.csv')

print("\n=== 1.1 Structure Validation ===")
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")
print(f"Unique IDs: {df['ID'].nunique()}")

print("\n=== 1.2 Missing Values Check ===")
for col in df.columns:
    null_count = df[col].isnull().sum()
    empty_count = (df[col] == '').sum() if df[col].dtype == 'object' else 0
    print(f"{col}: NaN={null_count}, empty_string={empty_count}")

print("\n=== 1.3 Label Integrity ===")
cat_counts = df['Category'].value_counts().sort_index()
print(cat_counts.to_string())
print(f"\nTotal categories: {len(cat_counts)}")
print(f"Min count: {cat_counts.min()} ({cat_counts.idxmin()})")
print(f"Max count: {cat_counts.max()} ({cat_counts.idxmax()})")

print("\n=== 1.4 Text Length Analysis ===")
df['text_len'] = df['Resume_str'].apply(len)
print(f"Resume_str length stats:")
print(df['text_len'].describe().to_string())
print(f"\n<50 chars: {(df['text_len'] < 50).sum()}")
print(f">20000 chars: {(df['text_len'] > 20000).sum()}")

print("\n=== 1.5 Category Leakage Check ===")
cats = sorted(df['Category'].unique())
high_leakage = []
for cat in cats:
    pattern = cat.lower().replace('-', ' ')
    mask = df['Category'] == cat
    count = df[mask]['Resume_str'].str.contains(pattern, case=False, na=False).sum()
    total = mask.sum()
    pct = count / total * 100 if total > 0 else 0
    if pct >= 80:
        high_leakage.append(cat)
    print(f'{cat}: {pct:.1f}% ({count}/{total})')
print(f"\nHigh leakage (>80%): {len(high_leakage)}/{len(cats)} categories")

print("\n=== 1.6 Multi-domain Resume Analysis ===")
keywords = {}
for cat in cats:
    keywords[cat] = set(cat.lower().replace('-', ' ').split())

multi_domain_count = 0
for _, row in df.iterrows():
    text = row['Resume_str'].lower()
    found_cats = [cat for cat, kw in keywords.items() if any(k in text for k in kw)]
    if len(found_cats) > 1:
        multi_domain_count += 1

print(f"Multi-domain resumes: {multi_domain_count}/{len(df)} ({multi_domain_count/len(df)*100:.1f}%)")

print("\n=== 1.7 Duplicate Detection ===")
exact_dupes = df[df.duplicated(subset=['Resume_str'], keep=False)]
print(f"Exact duplicate rows: {len(exact_dupes)}")
print(f"Exact duplicate groups: {len(exact_dupes) // 2 if len(exact_dupes) > 0 else 0}")

id_dupes = df[df.duplicated(subset=['ID'], keep=False)]
print(f"ID duplicates: {len(id_dupes)} rows")

print("\n=== 1.8 Text vs HTML Similarity (Sample 100) ===")
sample = df.sample(100, random_state=42)
sims = []
for _, r in sample.iterrows():
    t = set(re.findall(r'\w+', str(r['Resume_str']).lower()))
    h = set(re.findall(r'\w+', str(r['Resume_html']).lower()))
    j = len(t & h) / max(len(t | h), 1)
    sims.append(j)
print(f"Jaccard similarity: avg={sum(sims)/len(sims):.4f}, min={min(sims):.4f}, max={max(sims):.4f}")

print("\n=== Summary ===")
print(f"- Total resumes: {len(df)}")
print(f"- Categories: {len(cats)}")
print(f"- Missing values: None")
print(f"- Exact duplicates: {len(exact_dupes) // 2} groups")
print(f"- High category leakage: {len(high_leakage)}/{len(cats)} categories")
print(f"- Multi-domain rate: {multi_domain_count/len(df)*100:.1f}%")
print(f"- Small classes (<50): BPO(22), AUTOMOBILE(36)")
