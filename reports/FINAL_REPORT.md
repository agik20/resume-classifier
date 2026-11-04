# Resume Classification Project - Final Report

**Date**: 2026-11-04 (v1.0.0 release)
**Status**: RELEASED v1.0.0

---

## Executive Summary

Built a multi-class classifier (24 categories) for resume domain prediction using CPU-only infrastructure. Implemented rigorous leakage mitigation, extensive experimentation, and documented limitations.

## Model Performance

| Metric | Value |
|--------|-------|
| **Validation Macro F1** | **0.6137** |
| **Test Macro F1** | **0.5762** |
| **Improvement vs Baseline** | **+0.0808 (+15.1%)** |
| **Baseline (unmitigated)** | 0.5329 |
| **Latency (p50)** | 0.33ms |
| **Model Size (active artifacts)** | ~117 MB (word vec 12.9 MB + char vec 1.9 MB + classifier 102.9 MB) |

## Final Model

**LinearSVC(C=10) on Combined Word+Char TF-IDF**

- Word n-grams: (1,2), min_df=1, sublinear_tf=True
- Char n-grams: (3,5), min_df=2, sublinear_tf=True
- Combined features: ~535K dimensions
- Training time: ~7 seconds on CPU

## Threshold Analysis

**Target**: >= 0.65 Macro F1
**Achieved**: 0.5762 (test) / 0.6137 (validation)
**Gap**: -0.0738 (test) / -0.0363 (validation)

### Why Threshold Not Met:
1. **Inherent ambiguity**: 94% of resumes contain keywords from >=2 categories
2. **Small class imbalance**: BPO (3 samples), ARTS (15), AUTOMOBILE (5)
3. **Feature limitation**: TF-IDF captures keywords but not semantic similarity
4. **Embeddings failed**: all-MiniLM-L6-v2 reduced performance by -0.155

### Theoretical Ceiling:
- Estimated at **0.65-0.67** based on ambiguity analysis
- Requires manual relabeling or synthetic oversampling to reach

## Known Limitations

### Critical (Must Disclose)
- **BPO**: 0.14 recall (3 validation samples)
- **Small classes**: ARTS (0.29), AUTOMOBILE (0.18), CONSULTANT (0.17)
- **High ambiguity**: ~60% of errors are dataset-inherent, not model failure

### Moderate
- Cross-domain confusion pairs (HEALTHCARE<->ADVOCATE, FINANCE<->ACCOUNTANT)
- No probability calibration (decision scores only)

### Minor
- Single threshold C=10 may not optimize all use cases

## Deliverables

| File | Description |
|------|-------------|
| `reports/final_model_decision.md` | Multi-criteria selection justification |
| `reports/10_test_results.json` | Test set evaluation metrics |
| `predict.py` | Inference function + CLI |
| `experiments/best_phase5_clf.joblib` | Best classifier |
| `experiments/best_phase5_word_vec.joblib` | Word vectorizer |
| `experiments/best_phase5_char_vec.joblib` | Char vectorizer |

## Usage

```python
from predict import predict_resume

result = predict_resume('John Smith, Software Engineer, Python, Django...')
print(result['predicted_category'])  # 'INFORMATION-TECHNOLOGY'
print(result['confidence_score'])    # raw LinearSVC decision value (NOT a calibrated probability;
                                     # can be negative; only relative ordering is meaningful)
print(result['top_k_predictions'])   # top 3 predictions with raw decision scores
```

> **Note on `confidence_score`**: The `confidence_score` returned by `predict_resume()`
> is a **raw LinearSVC `decision_function` value**, not a calibrated probability.
> It can be negative. Only the relative ordering across classes is meaningful.
> Applying Platt scaling or isotonic regression would produce calibrated probabilities.

```bash
python predict.py --resume path/to/resume.txt --top_k 3
```

> **Note:** The model artifacts in `experiments/` are excluded from git.
> A fresh clone of the repository alone is not sufficient to run inference;
> the three `.joblib` files must be obtained separately or reproduced via
> `scripts/phase5_tuning.py` (see README "Reproducibility strategy").

## Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Environment Setup | COMPLETE |
| 1 | Data Audit | COMPLETE |
| 1b | Leakage Mitigation | COMPLETE |
| 2 | EDA | COMPLETE |
| 3 | Split Strategy | COMPLETE |
| 4 | Baseline | COMPLETE (0.5329) |
| 5 | Feature Engineering | COMPLETE (0.6137) |
| 6 | Robustness Checks | COMPLETE (all passed) |
| 7 | Error Analysis | COMPLETE (33.8% error rate) |
| 8 | Embeddings | COMPLETE (failed, fallback) |
| 9 | Model Selection | COMPLETE |
| 10 | Inference & Deployment | COMPLETE |

---

*Project completed: 2026-08-16*
*Released: 2026-11-04 (v1.0.0)*
*License: MIT — see LICENSE*
