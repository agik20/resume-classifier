# Phase 7: Error Analysis

**Date**: 2026-08-16 | **Model**: Combined Word+Char SVM (C=10)

## Summary
- Total errors: 126 / 373 samples
- Error rate: 33.8%

## Top Confusion Pairs
| True Class | Predicted | Count |
|---|---|---|
| HEALTHCARE -> ADVOCATE | 5 |
| FINANCE -> ACCOUNTANT | 5 |
| ARTS -> TEACHER | 5 |
| ENGINEERING -> AVIATION | 3 |
| CONSTRUCTION -> AVIATION | 3 |
| SALES -> BUSINESS-DEVELOPMENT | 2 |
| SALES -> APPAREL | 2 |
| PUBLIC-RELATIONS -> BUSINESS-DEVELOPMENT | 2 |
| HEALTHCARE -> HR | 2 |
| ENGINEERING -> CONSTRUCTION | 2 |
| DIGITAL-MEDIA -> PUBLIC-RELATIONS | 2 |
| DESIGNER -> ENGINEERING | 2 |
| CONSULTANT -> INFORMATION-TECHNOLOGY | 2 |
| CONSTRUCTION -> ACCOUNTANT | 2 |
| BUSINESS-DEVELOPMENT -> CHEF | 2 |
| APPAREL -> SALES | 2 |
| AGRICULTURE -> ADVOCATE | 2 |
| TEACHER -> ENGINEERING | 1 |
| TEACHER -> CONSULTANT | 1 |
| TEACHER -> ADVOCATE | 1 |

## Errors by True Class (Worst)
| Category | Errors | Error% |
|---|---|---|
| ARTS | 12 | 3.2% |
| CONSULTANT | 12 | 3.2% |
| SALES | 10 | 2.7% |
| HEALTHCARE | 9 | 2.4% |
| FINANCE | 8 | 2.1% |
| APPAREL | 7 | 1.9% |
| BUSINESS-DEVELOPMENT | 7 | 1.9% |
| CONSTRUCTION | 6 | 1.6% |
| DIGITAL-MEDIA | 6 | 1.6% |
| ENGINEERING | 6 | 1.6% |
| FITNESS | 6 | 1.6% |
| ADVOCATE | 5 | 1.3% |
| AGRICULTURE | 4 | 1.1% |
| AUTOMOBILE | 4 | 1.1% |
| PUBLIC-RELATIONS | 4 | 1.1% |
| BANKING | 3 | 0.8% |
| BPO | 3 | 0.8% |
| DESIGNER | 3 | 0.8% |
| INFORMATION-TECHNOLOGY | 3 | 0.8% |
| TEACHER | 3 | 0.8% |
| AVIATION | 2 | 0.5% |
| CHEF | 2 | 0.5% |
| HR | 1 | 0.3% |

## Key Findings
1. **Smallest classes fail most**: BPO (100%), ARTS (80%), AUTOMOBILE (80%), CONSULTANT (70.6%)
2. **Most confused pairs**: HEALTHCARE->ADVOCATE(5), FINANCE->ACCOUNTANT(5), ARTS->TEACHER(5)
3. **Cross-domain confusion**: HEALTHCARE vs ADVOCATE, ENGINEERING vs CONSTRUCTION suggest overlapping keyword signals
4. **Header stripping insufficient**: R5 dropped 0.047 F1, suggesting some leakage remains

## Recommendations
1. Phase 8: Embeddings may help separate confused classes using semantic features
2. Consider synthetic oversampling (SMOTE) for BPO, ARTS, AUTOMOBILE
3. Feature importance analysis to identify misleading keywords
