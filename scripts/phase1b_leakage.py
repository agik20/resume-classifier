import os
import pandas as pd

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

print("Loading data...")
df = pd.read_csv(RESUME_CSV)

print("\n=== Category Leakage Analysis ===")
cats = sorted(df['Category'].unique())
leakage_data = []

for cat in cats:
    pattern = cat.lower().replace('-', ' ')
    mask = df['Category'] == cat
    count = df[mask]['Resume_str'].str.contains(pattern, case=False, na=False).sum()
    total = mask.sum()
    pct = count / total * 100
    leakage_data.append({
        'category': cat,
        'count': count,
        'total': total,
        'percentage': pct
    })
    print(f'{cat}: {pct:.1f}% ({count}/{total})')

high_leakage = [d for d in leakage_data if d['percentage'] >= 80]
low_leakage = [d for d in leakage_data if d['percentage'] < 50]

print(f"\n=== Summary ===")
print(f"High leakage (>80%): {len(high_leakage)}/{len(cats)} categories")
print(f"Low leakage (<50%): {len(low_leakage)}/{len(cats)} categories")
print(f"\nHigh leakage categories: {[d['category'] for d in high_leakage]}")
print(f"Low leakage categories: {[d['category'] for d in low_leakage]}")

print("\nLeakage analysis complete!")
