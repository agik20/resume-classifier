# Phase 5: Feature Engineering & Hyperparameter Tuning

**Date**: 2026-08-16
**Baseline Phase 4 CV**: 0.5329, Val: 0.5886

## Summary

| Experiment | CV Macro F1 | Val Macro F1 | Min Recall |
|---|---|---|---|
| SVM_Combined_best=C=10.0_cv=0.6137 | 0.6137 | 0.6137 | 0.0000 |
| SVM_Char_cv=0.5458 | 0.5621 | 0.6110 | 0.0000 |
| SVM_Word_cv=0.5498 | 0.5614 | 0.6013 | 0.0000 |
| LSA_n300_C10.0 | 0.5562 | 0.5562 | 0.0000 |
| LSA_n300_C1.0 | 0.5436 | 0.5436 | 0.0000 |
| LSA_n200_C1.0 | 0.5385 | 0.5385 | 0.0000 |
| LSA_n100_C10.0 | 0.5363 | 0.5363 | 0.0000 |
| LSA_n200_C10.0 | 0.5319 | 0.5319 | 0.0000 |
| LR_Word_cv=0.5241 | 0.5275 | 0.5573 | 0.0000 |
| LSA_n100_C1.0 | 0.4841 | 0.4841 | 0.0000 |
| LSA_n300_C0.1 | 0.4650 | 0.4650 | 0.0000 |
| LSA_n200_C0.1 | 0.4603 | 0.4603 | 0.0000 |
| NB_alpha0.1_ng1-1 | 0.4587 | 0.4587 | 0.0000 |
| NB_alpha0.1_ng1-2 | 0.4579 | 0.4579 | 0.0000 |
| NB_alpha0.5_ng1-1 | 0.4322 | 0.4322 | 0.0000 |
| LSA_n100_C0.1 | 0.4284 | 0.4284 | 0.0000 |
| NB_alpha1.0_ng1-1 | 0.4152 | 0.4152 | 0.0000 |
| NB_alpha0.5_ng1-2 | 0.4130 | 0.4130 | 0.0000 |
| NB_alpha2.0_ng1-1 | 0.4103 | 0.4103 | 0.0000 |
| NB_alpha1.0_ng1-2 | 0.4018 | 0.4018 | 0.0000 |
| NB_alpha2.0_ng1-2 | 0.3976 | 0.3976 | 0.0000 |

**Best Model**: SVM_Combined_best=C=10.0_cv=0.6137
**Improvement over baseline**: CV ++0.0808, Val ++0.0251
**Gate Decision**: CONTINUE to Phase 8 (embeddings)
