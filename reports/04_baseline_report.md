# Baseline Model Report

**Date**: 2026-08-15
**Phase**: 4
**Best Model**: Linear SVM on mitigated text

---

## Executive Summary

Baseline evaluated across 4 model configurations (2 classifiers x 2 text types) with stratified 5-fold cross-validation. Category-name leakage confirmed at ~0.03-0.05 Macro F1 delta. Best mitigated CV Macro F1 = 0.5329, below the 0.65 threshold -> **continue to Phase 5**.

---

## Results Summary

| Model | Input Text | CV Macro F1 | Val Macro F1 | Min Recall |
|-------|-----------|-------------|--------------|------------|
| LR (C=1.0) | Raw | 0.5223 +/- 0.0138 | 0.5625 | 0.0000 |
| LR (C=1.0) | Mitigated | 0.4868 +/- 0.0162 | 0.5440 | 0.0000 |
| SVM (C=1.0) | Raw | 0.5811 +/- 0.0284 | 0.6167 | 0.0000 |
| **SVM (C=1.0)** | **Mitigated** | **0.5329 +/- 0.0148** | **0.5886** | **0.0000** |

### Key Observations

1. **Leakage confirmed**: Raw -> Mitigated delta = 0.0355 (LR) / 0.0482 (SVM). Both > 0.02, indicating real leakage impact.
2. **SVM > LR**: Raw SVM (0.5811) outperforms raw LR (0.5223) by 0.0588.
3. **Small classes struggle**: BPO (0.0000), ARTS (0.0667), AUTOMOBILE (0.2000), CONSULTANT (0.2353) all below 0.40 recall on mitigated text.
4. **High-recall classes**: HR (0.941), INFORMATION-TECHNOLOGY (0.889), ENGINEERING (0.889), CHEF (0.889), AVIATION (0.889).

---

## Per-Class Recall - SVM Mitigated

| Category | Recall | Status |
|----------|--------|--------|
| ACCOUNTANT | 1.0000 | OK |
| ADVOCATE | 0.6667 | OK |
| AGRICULTURE | 0.4444 | OK |
| APPAREL | 0.4667 | OK |
| ARTS | 0.0667 | LOW |
| AUTOMOBILE | 0.2000 | LOW |
| AVIATION | 0.8889 | OK |
| BANKING | 0.8235 | OK |
| BPO | 0.0000 | LOW |
| BUSINESS-DEVELOPMENT | 0.6111 | OK |
| CHEF | 0.8889 | OK |
| CONSTRUCTION | 0.6471 | OK |
| CONSULTANT | 0.2353 | LOW |
| DESIGNER | 0.8125 | OK |
| DIGITAL-MEDIA | 0.7143 | OK |
| ENGINEERING | 0.6111 | OK |
| FINANCE | 0.4444 | OK |
| FITNESS | 0.5556 | OK |
| HEALTHCARE | 0.4118 | OK |
| HR | 0.9412 | OK |
| INFORMATION-TECHNOLOGY | 0.8889 | OK |
| PUBLIC-RELATIONS | 0.8824 | OK |
| SALES | 0.5882 | OK |
| TEACHER | 0.6667 | OK |

**4 categories below 0.40**: BPO, ARTS, AUTOMOBILE, CONSULTANT
**2 categories below 0.20**: BPO (0.00), ARTS (0.067)

---

## Go/No-Go Gate Decision

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Mitigated Macro F1 >= 0.65 | 0.65 | 0.5329 | FAIL |
| Min recall >= 0.40 | 0.40 | 0.0000 | FAIL |
| Mitigated Macro F1 >= 0.60 | 0.60 | 0.5329 | FAIL |
| Min recall >= 0.35 | 0.35 | 0.0000 | FAIL |
| Mitigated Macro F1 < 0.50 | 0.50 | 0.5329 | N/A |

**Decision: CONTINUE to Phase 5 (cautious)**

The mitigated baseline (0.5329) is below both the stop threshold (0.65) and the continue-with-confidence threshold (0.60). However, it's above the pause threshold (0.50). There is room for improvement through feature engineering (Phase 5) and possibly embeddings (Phase 8).

### Recommended Actions
1. **Phase 5**: Hyperparameter tuning on SVM/LR with mitigated text - try different C values, ngram ranges, character n-grams.
2. **Minority class handling**: Explicitly test `class_weight` strategies and focal loss alternatives for BPO, ARTS, AUTOMOBILE, CONSULTANT.
3. **Phase 8**: Embedding-based approach (Strategy A) may help small classes if semantic features provide better signal.

---

## Files Generated

| File | Description |
|------|-------------|
| `reports/04_baseline_results.json` | JSON results for all 4 model configurations |
| `scripts/phase4_baseline.py` | Main Phase 4 script |

---

## Next Steps

Proceed to **Phase 5: Feature Engineering & Hyperparameter Tuning** - explore TF-IDF grid search and classifier hyperparameter tuning on mitigated text.
