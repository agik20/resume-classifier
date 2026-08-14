# EDA Findings Report

**Date**: 2026-08-14
**Phase**: 2

---

## Executive Summary

Dataset is moderately imbalanced (5.45x ratio) with extremely high multi-domain rate (98.8%). Average resume length is ~5,900 characters. High category leakage confirmed in Phase 1b.

---

## 2.1 Label Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| INFORMATION-TECHNOLOGY | 120 | 4.83% |
| BUSINESS-DEVELOPMENT | 120 | 4.83% |
| ADVOCATE | 118 | 4.75% |
| CHEF | 118 | 4.75% |
| ENGINEERING | 118 | 4.75% |
| ACCOUNTANT | 118 | 4.75% |
| FINANCE | 118 | 4.75% |
| FITNESS | 117 | 4.71% |
| AVIATION | 117 | 4.71% |
| SALES | 116 | 4.67% |
| BANKING | 115 | 4.63% |
| HEALTHCARE | 115 | 4.63% |
| CONSULTANT | 115 | 4.63% |
| CONSTRUCTION | 112 | 4.51% |
| PUBLIC-RELATIONS | 111 | 4.47% |
| HR | 110 | 4.43% |
| DESIGNER | 107 | 4.31% |
| ARTS | 103 | 4.15% |
| TEACHER | 102 | 4.11% |
| APPAREL | 97 | 3.90% |
| DIGITAL-MEDIA | 96 | 3.86% |
| AGRICULTURE | 63 | 2.54% |
| AUTOMOBILE | 36 | 1.45% |
| BPO | 22 | 0.89% |

- **Imbalance Ratio**: 5.45x
- **Most common**: INFORMATION-TECHNOLOGY (120 samples)
- **Least common**: BPO (22 samples)

---

## 2.2 Length Statistics per Category

| Category | Count | Mean | Median | Min | Max |
|----------|-------|------|--------|-----|-----|
| ACCOUNTANT | 118 | 5,920 | 5,566 | 1,022 | 24,071 |
| ADVOCATE | 118 | 6,177 | 5,385 | 1,839 | 20,626 |
| AGRICULTURE | 63 | 6,231 | 5,631 | 1,369 | 14,252 |
| APPAREL | 97 | 5,619 | 5,580 | 1,689 | 12,573 |
| ARTS | 103 | 5,608 | 5,177 | 1,113 | 11,792 |
| AUTOMOBILE | 36 | 5,941 | 5,250 | 1,574 | 21,063 |
| AVIATION | 117 | 5,849 | 5,535 | 1,317 | 13,646 |
| BANKING | 115 | 5,851 | 5,417 | 1,530 | 15,428 |
| BPO | 22 | 6,933 | 6,470 | 3,054 | 15,663 |
| BUSINESS-DEVELOPMENT | 120 | 5,693 | 5,482 | 0 | 12,186 |
| CHEF | 118 | 5,597 | 5,352 | 980 | 35,217 |
| CONSTRUCTION | 112 | 6,229 | 5,696 | 688 | 29,013 |
| CONSULTANT | 115 | 6,485 | 6,090 | 1,443 | 14,759 |
| DESIGNER | 107 | 5,266 | 5,333 | 794 | 16,517 |
| DIGITAL-MEDIA | 96 | 5,753 | 5,513 | 1,592 | 23,723 |
| ENGINEERING | 118 | 6,136 | 5,676 | 1,190 | 18,672 |
| FINANCE | 118 | 5,948 | 5,504 | 1,856 | 19,957 |
| FITNESS | 117 | 5,227 | 5,213 | 1,325 | 13,754 |
| HEALTHCARE | 115 | 6,594 | 5,834 | 1,750 | 20,400 |
| HR | 110 | 6,405 | 5,638 | 1,831 | 24,559 |
| INFORMATION-TECHNOLOGY | 120 | 6,871 | 6,244 | 1,843 | 19,991 |
| PUBLIC-RELATIONS | 111 | 6,543 | 5,677 | 1,888 | 35,111 |
| SALES | 116 | 4,915 | 5,058 | 838 | 17,961 |
| TEACHER | 102 | 5,197 | 5,148 | 1,349 | 17,726 |

**Overall**: Mean = 5,926 chars, Median = 5,542 chars

---

## 2.3 Vocabulary Analysis

### Top 20 Most Frequent Words (after stopword removal)

1. state (16,062)
2. city (15,045)
3. company (14,663)
4. management (11,994)
5. name (11,737)
6. sales (8,124)
7. skills (7,695)
8. business (7,686)
9. customer (7,603)
10. new (6,334)

### Top 20 TF-IDF Weighted Terms

1. and (1,047.54)
2. to (475.12)
3. of (371.69)
4. the (316.00)
5. in (250.11)
6. for (243.79)
7. with (189.70)
8. state (160.17)
9. city (149.54)
10. company (141.53)

**Observation**: Many top terms are generic resume boilerplate ("state", "city", "company", "name"). Discriminative terms like "sales", "skills", "business", "customer" appear higher.

---

## 2.4 Class Separability (Quick Logistic Regression)

- **Accuracy**: 66.20%
- **Note**: This is a quick sanity check, not a final baseline
- Models can achieve ~66% accuracy on this dataset

---

## 2.5 Multi-domain Resume Profiling

| Category | Total | Multi% |
|----------|-------|--------|
| ACCOUNTANT | 118 | 100.0% |
| ADVOCATE | 118 | 100.0% |
| AGRICULTURE | 63 | 96.8% |
| APPAREL | 97 | 99.0% |
| ARTS | 103 | 98.1% |
| AUTOMOBILE | 36 | 100.0% |
| AVIATION | 117 | 96.6% |
| BANKING | 115 | 99.1% |
| BPO | 22 | 100.0% |
| BUSINESS-DEVELOPMENT | 120 | 99.2% |
| CHEF | 118 | 96.6% |
| CONSTRUCTION | 112 | 95.5% |
| CONSULTANT | 115 | 100.0% |
| DESIGNER | 107 | 99.1% |
| DIGITAL-MEDIA | 96 | 100.0% |
| ENGINEERING | 118 | 98.3% |
| FINANCE | 118 | 100.0% |
| FITNESS | 117 | 99.1% |
| HEALTHCARE | 115 | 100.0% |
| HR | 110 | 99.1% |
| INFORMATION-TECHNOLOGY | 120 | 100.0% |
| PUBLIC-RELATIONS | 111 | 100.0% |
| SALES | 116 | 95.7% |
| TEACHER | 102 | 99.0% |

**Overall multi-domain rate: 98.8%** (2,453/2,484)

Only 31 resumes (1.2%) contain keywords from exactly one category.

---

## Key Findings

| Finding | Severity | Action Required |
|---------|----------|-----------------|
| 5.45x imbalance ratio | MEDIUM | Use class_weight='balanced' |
| 98.8% multi-domain rate | HIGH | Inherent ambiguity - limit achievable F1 |
| Small classes: BPO(22), AUTOMOBILE(36) | MEDIUM | Special handling for recall |
| Generic boilerplate dominates text | LOW | Focus on TF-IDF discriminative terms |
| Quick LR accuracy: 66.2% | INFO | Confirms dataset is challenging but learnable |

---

## Next Steps

Proceed to **Phase 3: Data Leakage Investigation & Split Strategy** to establish train/val/test splits before any modeling begins.
