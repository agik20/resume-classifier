# Dataset Audit Report — Resume Classification

**Date**: 2026-08-14
**Source**: `dataset/Resume.csv`
**Rows**: 2,484 | **Columns**: 4 | **Categories**: 24

---

## 1. Structure Validation

| Metric | Value |
|--------|-------|
| Total rows | 2,484 |
| Total columns | 4 |
| Column names | `ID`, `Resume_str`, `Resume_html`, `Category` |
| Unique IDs | 2,484 (no collisions) |

**Conclusion**: Clean structure, no structural anomalies.

---

## 2. Missing Values

| Column | NaN count | Empty string count |
|--------|-----------|-------------------|
| ID | 0 | 0 |
| Resume_str | 0 | 0 |
| Resume_html | 0 | 0 |
| Category | 0 | 0 |

**Conclusion**: No missing or empty values anywhere in the dataset.

---

## 3. Label Integrity

| Category | Count | Notes |
|----------|-------|-------|
| ACCOUNTANT | 118 | |
| ADVOCATE | 118 | |
| AGRICULTURE | 63 | |
| APPAREL | 97 | |
| ARTS | 103 | |
| AUTOMOBILE | 36 | Small class |
| AVIATION | 117 | |
| BANKING | 115 | |
| BPO | 22 | Smallest class |
| BUSINESS-DEVELOPMENT | 120 | Largest class |
| CHEF | 118 | |
| CONSTRUCTION | 112 | |
| CONSULTANT | 115 | |
| DESIGNER | 107 | |
| DIGITAL-MEDIA | 96 | |
| ENGINEERING | 118 | |
| FINANCE | 118 | |
| FITNESS | 117 | |
| HEALTHCARE | 115 | |
| HR | 110 | |
| INFORMATION-TECHNOLOGY | 120 | |
| PUBLIC-RELATIONS | 111 | |
| SALES | 116 | |
| TEACHER | 102 | |

- Min count: 22 (BPO)
- Max count: 120 (BUSINESS-DEVELOPMENT)
- **No typos detected** — `FITNESS` and `APPAREL` are confirmed correct (per plan finding E4)
- Range: 22–120 per class, mostly balanced

---

## 4. Text Length Analysis

| Stat | Value |
|------|-------|
| Mean | 6,295 chars |
| Median | 5,887 chars |
| Min | 21 chars |
| Max | 38,842 chars |
| <50 chars | 1 row |
| >20,000 chars | 12 rows |

**Outliers**:
- 1 very short resume (ID: 12632728, Category: BUSINESS-DEVELOPMENT) — likely a data quality issue or placeholder
- 12 very long resumes (>20K chars) — need inspection for boilerplate/repetition

---

## 5. Category Leakage (CRITICAL)

| Category | Leakage % | Status |
|----------|-----------|--------|
| ACCOUNTANT | 100.0% | CRITICAL |
| ADVOCATE | 81.4% | HIGH |
| AGRICULTURE | 46.0% | Low |
| APPAREL | 53.6% | Moderate |
| ARTS | 88.3% | HIGH |
| AUTOMOBILE | 41.7% | Low |
| AVIATION | 82.9% | HIGH |
| BANKING | 80.0% | HIGH |
| BPO | 45.5% | Low |
| BUSINESS-DEVELOPMENT | 98.3% | CRITICAL |
| CHEF | 91.5% | HIGH |
| CONSTRUCTION | 100.0% | CRITICAL |
| CONSULTANT | 100.0% | CRITICAL |
| DESIGNER | 100.0% | CRITICAL |
| DIGITAL-MEDIA | 40.6% | Low |
| ENGINEERING | 100.0% | CRITICAL |
| FINANCE | 100.0% | CRITICAL |
| FITNESS | 85.5% | HIGH |
| HEALTHCARE | 100.0% | CRITICAL |
| HR | 100.0% | CRITICAL |
| INFORMATION-TECHNOLOGY | 94.2% | HIGH |
| PUBLIC-RELATIONS | 95.5% | HIGH |
| SALES | 100.0% | CRITICAL |
| TEACHER | 100.0% | CRITICAL |

**Summary**: 19/24 categories (79%) have >80% category-name leakage. **10 categories at 100%**.

This is the #1 threat to model validity — a model can learn to predict by simple keyword matching rather than understanding resume content.

---

## 6. Multi-domain Resume Analysis

- **Multi-domain rate: 98.8%** (2,453/2,484)
- Only 31 resumes (1.2%) contain keywords from exactly one category

This means most resumes legitimately span multiple domains — some prediction errors are inherent, not fixable.

---

## 7. Duplicate Detection

| Type | Groups | Rows | Action |
|------|--------|------|--------|
| Exact duplicates (Resume_str) | 2 | 4 | Safe to remove (low risk per plan finding E5) |
| Near duplicates (300-char prefix) | 6 | 13 | Very low risk, no label conflicts |
| ID duplicates | 0 | 0 | None |

**Conclusion**: Low leakage risk from duplication. Standard stratified split is safe.

---

## 8. Text vs HTML Similarity

- Sample of 100 resumes
- **Jaccard similarity (word sets): avg=0.70, min=0.49, max=0.85**

Recommendation: Use `Resume_str` as primary feature (it's the cleaned text field). `Resume_html` is largely redundant but could be used for additional context if needed.

---

## 9. Key Findings Summary

| Finding | Severity | Impact |
|---------|----------|--------|
| 19/24 categories have >80% category-name leakage | **CRITICAL** | Model can cheat via keyword matching |
| 98.8% multi-domain rate | HIGH | Inherent ambiguity limits achievable F1 |
| 2 exact duplicate groups | LOW | Safe to remove or keep |
| 1 very short resume (<50 chars) | LOW | Inspect and decide whether to keep |
| BPO (22) and AUTOMOBILE (36) small classes | MEDIUM | Need special handling for recall |
| No missing values | None | Clean dataset |

---

## 10. Next Steps

Proceed to **Phase 1b: Category Leakage Mitigation** — implement header stripping (S1) + dual-model comparison (S4) to quantify leakage impact before any training begins.
