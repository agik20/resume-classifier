import pandas as pd
import sys
import os

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

def main():
    print("Loading data...")
    df = pd.read_csv(RESUME_CSV)

    print(f"\n=== 1.1 Structure Validation ===")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Column names: {list(df.columns)}")
    print(f"Unique IDs: {df['ID'].nunique()}")

    print(f"\n=== 1.2 Missing Values Check ===")
    for col in df.columns:
        null_count = df[col].isnull().sum()
        empty_count = (df[col] == '').sum() if df[col].dtype == 'object' else 0
        print(f"{col}: NaN={null_count}, empty_string={empty_count}")

    print(f"\n=== 1.3 Label Integrity ===")
    cat_counts = df['Category'].value_counts().sort_index()
    print(cat_counts.to_string())
    print(f"\nTotal categories: {len(cat_counts)}")
    print(f"Min count: {cat_counts.min()} ({cat_counts.idxmin()})")
    print(f"Max count: {cat_counts.max()} ({cat_counts.idxmax()})")

    print(f"\n=== 1.4 Text Length Analysis ===")
    df['text_len'] = df['Resume_str'].apply(len)
    print(f"Resume_str length stats:")
    print(df['text_len'].describe().to_string())
    print(f"\n<50 chars: {(df['text_len'] < 50).sum()}")
    print(f">20000 chars: {(df['text_len'] > 20000).sum()}")

    print(f"\n=== 1.5 Duplicate Detection ===")
    exact_dupes = df[df.duplicated(subset=['Resume_str'], keep=False)]
    print(f"Exact duplicate rows: {len(exact_dupes)}")

    if 'ID' in df.columns:
        id_dupes = df[df.duplicated(subset=['ID'], keep=False)]
        print(f"ID duplicates: {len(id_dupes)} rows")

    print("\nAudit complete!")
    return df

if __name__ == '__main__':
    main()
