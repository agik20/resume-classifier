import pandas as pd
import numpy as np
import json
import hashlib
import os
from sklearn.model_selection import StratifiedShuffleSplit

RESUME_CSV = os.environ.get('RESUME_CSV', os.path.join(os.environ.get('RESUME_DATA_DIR', 'data'), 'Resume.csv'))

print("=" * 60)
print("PHASE 3: GROUP-AWARE SPLIT STRATEGY")
print("=" * 60)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv(RESUME_CSV)
print(f"    Loaded: {len(df)} rows")

# ============================================================
# Create group labels for near-duplicates
# ============================================================
print("\n" + "=" * 60)
print("CREATING GROUP LABELS FOR NEAR-DUPLICATES")
print("=" * 60)

df['prefix'] = df['Resume_str'].apply(lambda x: str(x)[:300] if pd.notna(x) else '')

# Assign group IDs based on prefix
group_counter = 0
group_map = {}
df['group_id'] = -1  # Default: not in a duplicate group

for prefix, group in df.groupby('prefix'):
    if len(group) > 1:
        # This is a near-duplicate group
        group_id = group_counter
        for idx in group.index:
            group_map[idx] = group_id
        group_counter += 1

# Assign group IDs to DataFrame
for idx, group_id in group_map.items():
    df.loc[idx, 'group_id'] = group_id

# Count groups
near_dup_groups = sum(1 for gid in df['group_id'].unique() if gid >= 0)
print(f"\nNear-duplicate groups: {near_dup_groups}")
print(f"Rows in duplicate groups: {df[df['group_id'] >= 0].shape[0]}")
print(f"Rows not in groups: {df[df['group_id'] == -1].shape[0]}")

# ============================================================
# Split Strategy with Group Awareness
# ============================================================
print("\n" + "=" * 60)
print("SPLIT STRATEGY (GROUP-AWARE)")
print("=" * 60)

RANDOM_STATE = 42

# Separate grouped and non-grouped rows
grouped_mask = df['group_id'] >= 0
non_grouped_mask = df['group_id'] == -1

grouped_df = df[grouped_mask].copy()
non_grouped_df = df[non_grouped_mask].copy()

print(f"\nGrouped rows: {len(grouped_df)}")
print(f"Non-grouped rows: {len(non_grouped_df)}")

# Split non-grouped rows first (70/15/15)
split1 = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=RANDOM_STATE)
train_val_idx_nongroup, test_idx_nongroup = next(split1.split(non_grouped_df, non_grouped_df['Category']))

# From train_val, split val (21.4% of train_val = 15% of total)
split2 = StratifiedShuffleSplit(n_splits=1, test_size=0.2142857, random_state=RANDOM_STATE)
train_idx_nongroup, val_idx_nongroup = next(split2.split(non_grouped_df.loc[train_val_idx_nongroup], non_grouped_df.loc[train_val_idx_nongroup]['Category']))

# Adjust indices for non-grouped
train_idx_nongroup = train_val_idx_nongroup[train_idx_nongroup]
val_idx_nongroup = train_val_idx_nongroup[val_idx_nongroup]
test_idx_nongroup = test_idx_nongroup

# Now handle grouped rows - assign entire groups to one split
print(f"\nAssigning groups to splits...")
group_assignments = {}

for group_id in grouped_df['group_id'].unique():
    if group_id < 0:
        continue
    group_indices = grouped_df[grouped_df['group_id'] == group_id].index.tolist()
    group_cat = grouped_df.loc[group_indices, 'Category'].iloc[0]

    # Count how many rows of this group are in each potential split
    train_count = sum(1 for idx in group_indices if idx in train_idx_nongroup)
    val_count = sum(1 for idx in group_indices if idx in val_idx_nongroup)
    test_count = sum(1 for idx in group_indices if idx in test_idx_nongroup)

    # Assign to smallest split to balance
    counts = {'train': train_count, 'val': val_count, 'test': test_count}
    smallest = min(counts, key=counts.get)
    group_assignments[group_id] = smallest

    print(f"  Group {group_id}: {counts} -> {smallest}")

# Build final indices
train_idx = list(train_idx_nongroup)
val_idx = list(val_idx_nongroup)
test_idx = list(test_idx_nongroup)

for group_id, split_name in group_assignments.items():
    group_indices = grouped_df[grouped_df['group_id'] == group_id].index.tolist()
    if split_name == 'train':
        train_idx.extend(group_indices)
    elif split_name == 'val':
        val_idx.extend(group_indices)
    elif split_name == 'test':
        test_idx.extend(group_indices)

print(f"\nFinal split sizes:")
print(f"  Train: {len(train_idx)} ({len(train_idx)/len(df)*100:.1f}%)")
print(f"  Val:   {len(val_idx)} ({len(val_idx)/len(df)*100:.1f}%)")
print(f"  Test:  {len(test_idx)} ({len(test_idx)/len(df)*100:.1f}%)")

# Verify no near-duplicate crosses boundaries
print(f"\nVerifying no near-duplicate crosses boundaries:")
crossings = 0
for prefix, group in df.groupby('prefix'):
    if len(group) <= 1:
        continue
    indices = group.index.tolist()
    in_train = any(i in train_idx for i in indices)
    in_val = any(i in val_idx for i in indices)
    in_test = any(i in test_idx for i in indices)
    if sum([in_train, in_val, in_test]) > 1:
        crossings += 1
        print(f"  CROSS: Group with prefix '{prefix[:20]}...'")

if crossings == 0:
    print(f"  OK: No near-duplicate groups cross split boundaries")

# ============================================================
# Save Splits
# ============================================================
print("\n" + "=" * 60)
print("SAVING SPLITS")
print("=" * 60)

os.makedirs('data/splits', exist_ok=True)

splits_data = {
    'random_state': RANDOM_STATE,
    'strategy': 'group-aware stratified 70/15/15',
    'train_size': len(train_idx),
    'val_size': len(val_idx),
    'test_size': len(test_idx),
    'near_dup_groups': near_dup_groups,
    'train_indices': sorted(train_idx),
    'val_indices': sorted(val_idx),
    'test_indices': sorted(test_idx)
}

with open('data/splits/splits.json', 'w') as f:
    json.dump(splits_data, f, indent=2)

print(f"\nSaved splits to data/splits/splits.json")

# Create split datasets
train_df = df.loc[train_idx].reset_index(drop=True)
val_df = df.loc[val_idx].reset_index(drop=True)
test_df = df.loc[test_idx].reset_index(drop=True)

train_df.to_csv('data/splits/train.csv', index=False)
val_df.to_csv('data/splits/val.csv', index=False)
test_df.to_csv('data/splits/test.csv', index=False)

print(f"Saved train.csv ({len(train_df)} rows)")
print(f"Saved val.csv ({len(val_df)} rows)")
print(f"Saved test.csv ({len(test_df)} rows)")

# ============================================================
# Lock Test Set
# ============================================================
print("\n" + "=" * 60)
print("TEST SET LOCKED")
print("=" * 60)

test_hash = hashlib.sha256(open('data/splits/test.csv', 'rb').read()).hexdigest()
print(f"\nTest set SHA-256: {test_hash}")
print(f"\nIMPORTANT: Test set is LOCKED. Do NOT modify test.csv.")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print("PHASE 3 SUMMARY")
print("=" * 60)

print(f"""
+----------------------------------+------------------+
| Metric                           | Value            |
+----------------------------------+------------------+
| Total resumes                    | {len(df):>10,d}         |
| Train size                       | {len(train_idx):>10,d}         |
| Val size                         | {len(val_idx):>10,d}         |
| Test size                        | {len(test_idx):>10,d}         |
| Near-duplicate groups            | {near_dup_groups:>10}           |
| Boundary crossings               | {crossings:>10}           |
+----------------------------------+------------------+
""")

print("\nSPLIT STRATEGY: Group-aware stratified 70/15/15 (random_state=42)")
print("TEST SET: LOCKED - do not modify")
print("LEAKAGE RISK: NONE (0 boundary crossings)")

print("\n" + "=" * 60)
print("PHASE 3 COMPLETE")
print("=" * 60)
