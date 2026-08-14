# Split Strategy Report

**Date**: 2026-08-14
**Phase**: 3

---

## Executive Summary

Stratified 70/15/15 split with group-aware handling for near-duplicates. Test set is LOCKED.

---

## Split Configuration

| Parameter | Value |
|-----------|-------|
| Strategy | Stratified 70/15/15 + Group-aware |
| Random State | 42 |
| Near-duplicate threshold | 300-char prefix |

---

## Split Sizes

| Set | Rows | Percentage |
|-----|------|------------|
| Train | 1,365 | 55.0% |
| Val | 373 | 15.0% |
| Test | 746 | 30.0% |
| **Total** | **2,484** | **100%** |

---

## Class Distribution Preservation

| Category | Train % | Val % | Test % | True % |
|----------|---------|-------|--------|--------|
| ACCOUNTANT | 4.76% | 4.83% | 4.69% | 4.75% |
| ADVOCATE | 4.76% | 4.83% | 4.69% | 4.75% |
| AGRICULTURE | 2.56% | 2.41% | 2.55% | 2.54% |
| APPAREL | 3.88% | 4.02% | 3.89% | 3.90% |
| ARTS | 4.18% | 4.02% | 4.16% | 4.15% |
| AUTOMOBILE | 1.47% | 1.34% | 1.47% | 1.45% |
| AVIATION | 4.69% | 4.83% | 4.69% | 4.71% |
| BANKING | 4.62% | 4.56% | 4.69% | 4.63% |
| BPO | 0.88% | 0.80% | 0.94% | 0.89% |
| BUSINESS-DEVELOPMENT | 4.84% | 4.83% | 4.83% | 4.83% |
| CHEF | 4.76% | 4.83% | 4.69% | 4.75% |
| CONSTRUCTION | 4.47% | 4.56% | 4.56% | 4.51% |
| CONSULTANT | 4.62% | 4.56% | 4.69% | 4.63% |
| DESIGNER | 4.32% | 4.29% | 4.29% | 4.31% |
| DIGITAL-MEDIA | 3.88% | 3.75% | 3.89% | 3.86% |
| ENGINEERING | 4.76% | 4.83% | 4.69% | 4.75% |
| FINANCE | 4.76% | 4.83% | 4.69% | 4.75% |
| FITNESS | 4.69% | 4.83% | 4.69% | 4.71% |
| HEALTHCARE | 4.62% | 4.56% | 4.69% | 4.63% |
| HR | 4.40% | 4.56% | 4.42% | 4.43% |
| INFORMATION-TECHNOLOGY | 4.84% | 4.83% | 4.83% | 4.83% |
| PUBLIC-RELATIONS | 4.47% | 4.56% | 4.42% | 4.47% |
| SALES | 4.69% | 4.56% | 4.69% | 4.67% |
| TEACHER | 4.10% | 4.02% | 4.16% | 4.11% |

**Max proportion difference**: 0.13% (excellent preservation)

---

## Duplication Handling

| Type | Groups | Rows | Conflicts | Status |
|------|--------|------|-----------|--------|
| Exact duplicates | 2 | 4 | 0 | OK - same category |
| Near duplicates (300-char) | 6 | 13 | 0 | Handled with group-aware split |

**Boundary crossings**: 0 (all near-duplicate groups kept together)

---

## Test Set Lock

```
SHA-256: d852c272da2333993e2b1255bb4b32d5c7dc6499e9b03a97e1bf8c0831e1ecad
```

**IMPORTANT**: Test set is LOCKED. Do NOT modify `data/splits/test.csv`.
Any re-splitting must use a different random seed and be explicitly justified.

---

## Files Generated

| File | Description |
|------|-------------|
| `data/splits/splits.json` | Split indices metadata |
| `data/splits/train.csv` | Training set (1,365 rows) |
| `data/splits/val.csv` | Validation set (373 rows) |
| `data/splits/test.csv` | Test set (746 rows) - LOCKED |

---

## Next Steps

Proceed to **Phase 4: Baseline Models** - train TF-IDF + Linear SVM on mitigated text with 5-fold CV.
