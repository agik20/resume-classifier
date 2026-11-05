# Resume Classifier — Technical Project Report

## 1. Executive Summary

- **Objective**: predict one of 24 professional domains from raw resume text, on a CPU-only, portable pipeline.
- **Problem**: 19/24 category names leak into resume text (10 categories at 100%), so naive keyword matching inflates performance. Leakage was quantified and mitigated; the mitigated pipeline is the reporting standard throughout this document.
- **Final solution**: LinearSVC(C=10) on combined word + character TF-IDF features (535,692 dimensions), trained on 1,365 mitigated resumes, evaluated on a locked 746-resume test set.
- **Main metrics**: test Macro F1 = 0.5762 (locked test set, n=746); validation Macro F1 = 0.6137 (single validation-set figure; no independent CV estimate exists for the winning model); baseline mitigated CV Macro F1 = 0.5329 (independent 5-fold CV); inference p50 latency 0.33 ms; model artifacts total ~117 MB.
- **Status**: complete. The original 0.65 Macro F1 target was **not** achieved. A plausible contributing factor is keyword overlap in the dataset (98.8% of resumes match 2+ categories) — treated in this document as an analytical hypothesis, not as a measured upper bound on performance. `confidence_score` is a raw LinearSVC decision value, never described as a probability.

## 2. Project Scope and Objectives

- **Task**: 24-way single-label classification of resume text (the dataset assigns one primary category per resume).
- **Deliverables**: frozen model artifacts + a single-file inference module (`predict.py`) with library and CLI entry points. Not a web service, SaaS, or database-backed app.
- **Methodology constraint**: phase-gated pipeline (Phases 0-10) with explicit Go/No-Go gates, so every experiment has a recorded decision and the final model selection is traceable.
- **Non-goals** (explicitly out of scope): fine-tuned transformers (CPU-only constraint), probability calibration, multi-label prediction, deployment infrastructure.

## 3. Dataset and Data Audit

Source: `data/Resume.csv` (2,484 rows x 4 columns: `ID`, `Resume_str`, `Resume_html`, `Category`). No missing values; all 2,484 IDs unique. Text length: mean ~5,926 chars, min 21, max 38,842 (one near-empty resume, 12 resumes over 20,000 chars).

**Class distribution** (24 classes, 5.45x imbalance):

| Most common | Count | Least common | Count |
|---|---|---|---|
| INFORMATION-TECHNOLOGY, BUSINESS-DEVELOPMENT | 120 | BPO | 22 |
| ADVOCATE, CHEF, ENGINEERING, ACCOUNTANT, FINANCE | 118 | AUTOMOBILE | 36 |

**Duplicates**: 2 exact-duplicate groups (4 rows, same label) and 6 near-duplicate groups (13 rows, 300-char shared prefix, no label conflicts) — handled by the group-aware split in Phase 3. `Resume_str` and `Resume_html` word-set Jaccard similarity averages 0.70; the plain-text column is used as the feature.

## 4. Exploratory Data Analysis

- **Multi-domain keyword rate: 98.8%** of resumes contain keywords from 2+ categories (only 31 resumes match exactly one category). This establishes widespread keyword overlap, but keyword overlap does not independently prove genuine label ambiguity or label noise — a resume that mentions skills from two domains may still have a clear primary category. The overlap is a plausible contributor to error but is not a measured upper bound on achievable F1.
- **Boilerplate dominates**: the most frequent words are generic (state, city, company, management, name), so discriminative signal lives in mid-frequency domain keywords.
- **Learnability check**: a quick logistic regression reached 66.2% accuracy, confirming the task is learnable but non-trivial.
- **Implication**: TF-IDF-style token matching is well-suited to this task. The analysis in section 17 (a ~0.65-0.67 practical ceiling estimate) is a hypothesis based on keyword-overlap rates; it has not been empirically confirmed as a hard upper bound.

## 5. Data Leakage Investigation

- **Finding**: 19/24 categories have the category name appearing in over 80% of their own resumes; 10 categories are at 100% (ACCOUNTANT, CONSTRUCTION, CONSULTANT, DESIGNER, ENGINEERING, FINANCE, HEALTHCARE, HR, SALES, TEACHER).
- **Quantified impact** (Phase 1b, quick 5-fold CV, mitigated text = first 200 chars stripped): Raw text Macro F1 = 0.6506 vs Mitigated = 0.5982, delta = 0.0524. The 0.65 target would have been met on raw text; on the mitigated standard it would not.
- **Mitigation strategy**: strip the first 200 characters of every resume before any modeling (typical header: name, contact, title), and report all metrics on mitigated text. Phase 4 re-confirmed leakage impact on the final split: raw-to-mitigated delta was 0.0355 (LR) / 0.0482 (SVM).
- **Remaining limitation**: stripping 200 chars removes most but not all category-name occurrences; some leakage remains in the body text and cannot be removed without damaging content.

## 6. Data Splitting Strategy

- **Strategy**: stratified 55/15/30 train/val/test with group-aware handling — all rows sharing a 300-char prefix (near-duplicate groups) are kept in a single split. Random state 42.
- **Sizes**: train 1,365 / val 373 / test 746 (out of 2,484). Class proportions preserved to within 0.13% of the full-dataset distribution; 0 near-duplicate group crossings.
- **Reproducibility**: split indices are locked in `data/splits/splits.json`; `data/splits/test.csv` is the evaluation set and is locked (recorded SHA-256: d852c272da2333993e2b1255bb4b32d5c7dc6499e9b03a97e1bf8c0831e1ecad).
- **Limitation**: a 30% test set is a single fixed partition; per-class statistics for small classes (BPO: 7 samples in the locked test set) are therefore high-variance — one flipped prediction moves BPO recall by 0.143.

## 7. Baseline Model

Phase 4 compared 4 configurations (2 classifiers x 2 text types) with 5-fold stratified CV and a validation hold-out:

| Model | Input | CV Macro F1 | Val Macro F1 |
|---|---|---|---|
| LogisticRegression (C=1.0) | Raw | 0.5223 +/- 0.0138 | 0.5625 |
| LogisticRegression (C=1.0) | Mitigated | 0.4868 +/- 0.0162 | 0.5440 |
| LinearSVC (C=1.0) | Raw | 0.5811 +/- 0.0284 | 0.6167 |
| **LinearSVC (C=1.0)** | **Mitigated** | **0.5329 +/- 0.0148** | **0.5886** |

Baseline (SVM, mitigated) Macro F1 was 0.5329 — below the 0.65 target, so the pipeline continued to feature engineering. Raw-vs-mitigated deltas (0.0355-0.0482) independently confirmed the leakage impact measured in Phase 1b. Raw SVM (0.5811) beats mitigated SVM by 0.0482: a warning that training on raw text inflates the baseline and makes comparisons meaningless — which is why all downstream work uses mitigated text.

## 8. Model Development and Hyperparameter Tuning

Phase 5 ran 21 experiments across four families on mitigated text (full table: `experiments/phase5_results.json`):

| Family | Best result | Best val Macro F1 | Why it lost |
|---|---|---|---|
| **Combined word+char TF-IDF, LinearSVC, C=10** | SVM_Combined | **0.6137** | winner |
| Word TF-IDF only, SVM | SVM_Word | 0.5614 | char n-grams add morphological signal (+0.0523) |
| Char TF-IDF only, SVM | SVM_Char | 0.5621 | word n-grams add lexical signal |
| LSA (TF-IDF + TruncatedSVD) | LSA_n300_C10 | 0.5562 | dimensionality reduction discards discriminative tokens |
| Naive Bayes | NB_alpha0.1 | 0.4587 | independence assumption broken by overlapping multi-domain text |
| Logistic regression on TF-IDF | LR_Word | 0.5275 | SVM is better for keyword-discriminative problems |

**Selected configuration**: word n-grams (1,2) + char_wb n-grams (3,5), both sublinear_tf, concatenated (535,692 features), LinearSVC(C=10, max_iter=10000). The C sweep around the winner showed C=10 was best; char min_df=2 vs word min_df=1 kept vocabulary coverage while bounding feature count.

> **Data quality note**: In `experiments/phase5_results.json`, the `cv_macro_f1_mean` and `val_macro_f1` fields for the winning SVM_Combined experiment both record 0.61369853… — numerically identical, and `cv_macro_f1_std` is 0.0. The `cv_macro_f1_mean` field was populated using the validation-set score (a single `f1_score(y_val, y_pred)` at `scripts/phase5_tuning.py:233`), rather than an independently computed cross-validation result; `cv_macro_f1_std` was hardcoded to 0.0. Therefore, the reported CV and validation values are not independent measurements — the 0.6137 figure is a val-set F1 that was recorded into the CV field. A true separate cross-validation estimate was not computed for the combined experiment.

## 9. Robustness Evaluation

Six input perturbations were applied to the validation set; pass threshold = Macro F1 drop <= 0.05 (base: 0.6137):

| Perturbation | Macro F1 | Delta | Status |
|---|---|---|---|
| Strip emails/phones | 0.6137 | +0.0000 | pass |
| Remove punctuation | 0.6085 | -0.0052 | pass |
| Random typos | 0.6155 | +0.0018 | pass |
| Truncate to 200 words | 0.5929 | -0.0208 | pass |
| Drop first 100 words | 0.5664 | -0.0473 | pass |
| Remove stopwords | 0.6028 | -0.0109 | pass |

**Interpretation**: the model relies on content, not on formatting artifacts. The two meaningful drops — truncation (-0.0208) and leading-word removal (-0.0473) — show that early resume text carries real signal; the drop-first-100-words result is also evidence that residual header leakage still contributes a few points.

## 10. Embedding-Based Approach

Motivation: semantic embeddings might separate the most-confused categories better than keyword matching.

| Experiment | CV Macro F1 | Test Macro F1 | vs Phase 5 |
|---|---|---|---|
| LogisticRegression on 384-dim embeddings | 0.4671 | 0.4550 | -0.159 |
| Embeddings + TF-IDF combined | 0.4699 | 0.4549 | -0.159 |
| LinearSVC on 384-dim embeddings | 0.3875 | 0.3692 | -0.245 |

Model: all-MiniLM-L6-v2 (384 dims, sentence-transformers). **Rejected**: compressing resume text to 384 dimensions destroys the domain-specific keyword patterns (SQL, Python, React) that drive this task; explicit TF-IDF token matching outperformed every embedding variant. The recorded Phase 8 gate decision is NO GAIN / fallback to Phase 5, which is what this section reports (one unexplained intermediate value in the archived report is flagged in section 20).

## 11. Error Analysis

Validation-set error profile: 126 errors out of 373 samples (33.8% error rate). Raw evidence: `reports/artifacts/07_error_analysis.json`.

- **Worst classes** (validation errors): ARTS (12), CONSULTANT (12), SALES (10), HEALTHCARE (9), FINANCE (8).
- **Top confusion pairs**: HEALTHCARE->ADVOCATE (5), FINANCE->ACCOUNTANT (5), ARTS->TEACHER (5), ENGINEERING->AVIATION (3), CONSTRUCTION->AVIATION (3). These are cross-domain pairs with genuinely overlapping keyword vocabularies — the ambiguity predicted in Phase 2.
- **Small classes fail hardest**: BPO, ARTS, AUTOMOBILE, CONSULTANT sit below 0.40 recall in most configurations; on the locked test set BPO recall is 0.143 (1 of 7) — with 7 samples a single flip moves recall by 0.143.

## 12. Final Model and Architecture

```
resume text
  -> _clean_text: lowercase, collapse whitespace                       [predict.py]
  -> _strip_header: drop first 200 chars (leakage mitigation)          [predict.py]
  -> word TF-IDF (1-2 grams, min_df=1, sublinear_tf)  ->  433,832 features
  -> char_wb TF-IDF (3-5 grams, min_df=2, sublinear_tf) ->  101,860 features
  -> scipy.sparse.hstack  ->  535,692 features
  -> LinearSVC(C=10, max_iter=10000, 24 classes)
  -> decision_function (24 raw scores) -> argmax = predicted category
```

**Artifacts** (all under `experiments/`, ~117 MB total, see section 14 for obtaining them):

| Artifact | Size | Content |
|---|---|---|
| `best_phase5_word_vec.joblib` | 12.9 MB | Word TF-IDF vectorizer (433,832 features) |
| `best_phase5_char_vec.joblib` | 1.9 MB | Char TF-IDF vectorizer (101,860 features) |
| `best_phase5_clf.joblib` | 102.9 MB | LinearSVC(C=10) over 535,692 features, 24 classes |

Training time: ~7 s on CPU. Inference flow loads artifacts lazily (once per process) and caches them.

**Multi-criteria scoring** (from `reports/final_model_decision.md`; weighted score 7.3/10):

| Criterion | Weight | Score | Notes |
|---|---|---|---|
| Macro F1 (mitigated) | Primary | 8/10 | 0.6137, best across all experiments |
| Weighted F1 | High | 7/10 | ~0.85 on majority classes |
| Min Recall | Medium | 3/10 | 0.00 (BPO) — critical small-class limitation |
| Inference Latency | High | 9/10 | <1 ms on CPU |
| Interpretability | Medium | 9/10 | TF-IDF weights explainable |
| Reproducibility | Medium | 9/10 | Deterministic, seed=42 |
| Disk Size | Low | 8/10 | ~117 MB (vectorizers + classifier) |
| Ambiguity Resilience | High | 6/10 | ~60% inherent dataset ambiguity |

## 13. Final Evaluation

| Metric | Value | Notes |
|---|---|---|
| Test Macro F1 (locked test set, n=746) | **0.5762** | final evaluation number |
| Validation Macro F1 (n=373) | 0.6137 | selection-time val-set figure (see data note in S8; no independent CV estimate exists for the combined model) |
| Baseline (Phase 4, mitigated) CV Macro F1 | 0.5329 | independently measured 5-fold CV (std 0.0148) |
| Val-minus-baseline-CV | +0.0808 (+15.1%) | **NOT** a like-for-like improvement: 0.6137 is a val-set score, 0.5329 is a 5-fold CV; different measurement protocols |
| Min test recall | 0.143 (BPO, 7 samples) | small-class instability |
| Latency | p50 0.33 ms, p95 0.44 ms | single prediction, CPU |

**Target status**: the original >= 0.65 test Macro F1 target was **not** met (gap -0.0738). Validation (0.6137) and test (0.5762) are distinct numbers and are never substituted for each other in this document. **Note on CV vs. validation**: the 0.6137 figure is a single validation-set F1 recorded into the `cv_macro_f1_mean` field (`cv_macro_f1_std` hardcoded to 0.0; see `scripts/phase5_tuning.py:233`). No independent 5-fold cross-validation estimate was computed for the combined model, so the +0.0808 vs. the 0.5329 baseline CV is a cross-protocol comparison (val vs. CV), not a verified CV-to-CV improvement. The ~0.65-0.67 estimate (section 4, section 17) is an analytical hypothesis about keyword overlap, not an empirically measured ceiling. The validation-minus-test gap (0.6137 -> 0.5762) is expected: 373 validation samples vs 746 test samples, and the test set is the stricter, final arbiter.
## 14. Inference and Deployment

- **Python API**: `from predict import predict_resume`; `predict_resume(text, top_k=3) -> dict` with keys `predicted_category`, `confidence_score`, `top_k_predictions` (a list of `{"category", "score"}` pairs, best-first).
- **CLI**: `python predict.py --resume path/to/resume.txt --top_k 3`.
- **confidence_score semantics**: raw LinearSVC decision-function margin for the winning class. It is **not a probability**: it can be negative, is unbounded, and only its relative ordering across classes is meaningful. Calibrating it (Platt scaling / isotonic regression) is documented future work, not a current feature.
- **Artifacts are not shipped in this directory**: `experiments/*.joblib` (~117 MB) and `data/Resume.csv` are excluded from version control. To run inference you must either (a) place the three `.joblib` files in `experiments/` yourself, or (b) reproduce them: `pip install -r requirements.lock` then `python scripts/phase5_tuning.py` (with `RESUME_CSV` / `RESUME_DATA_DIR` pointing at the data root; default `data/Resume.csv`).
- **Install**: `pip install -r requirements.txt` covers the direct dependencies of the shipped inference code (joblib, numpy, scipy, scikit-learn, pandas, nltk, matplotlib, seaborn, pytest). `requirements.lock` is the full pinned environment (136 packages) validated during training, including the sentence-transformers stack used in the rejected Phase 8 experiments.
- **Runtime**: CPU-only; p50 0.33 ms per prediction after artifacts are loaded.

## 15. Testing and Verification

- `tests/test_predict.py` — 14 tests: artifact existence, return structure, top-k ordering and limits, empty/short-input handling, preprocessing unit behavior, float typing, determinism (idempotency), confidence-type check. `tests/test_seed.py` — 3 tests for `src/utils/seed.py` (determinism, seed sensitivity, default value 42). All 17 pass (`python -m pytest tests/ -v`).
- Documented CLI command verified against the shipped sample input: `python predict.py --resume data/samples/engineer.txt --top_k 3` -> `ENGINEERING` (score -0.4034; note the negative raw score, which is normal — see section 14).
- **Artifact integrity**: the three active artifacts are verified by size and by re-loading through `predict.py` in tests. SHA-256 hashes were recorded in the v1.0.0 release audit; no script or test in this project modifies artifacts in `experiments/`.
- Not covered by automated tests: the raw JSON evidence files in `reports/artifacts/` (they are records, not executable contracts) and behavior across different scikit-learn releases.

**SHA-256 artifact hashes** (recorded in v1.0.0 release audit; unchanged after all validation runs):

| Artifact | Size (bytes) | SHA-256 |
|---|---|---|
| `experiments/best_phase5_word_vec.joblib` | 12,872,968 | `8cb2f503220722e50b1cc83f9769631a1238485c5195243eaaa4378b12b0a8c7` |
| `experiments/best_phase5_char_vec.joblib` | 1,944,189 | `28a4aff295a9e7b5770d163e25d255249be592201c8ab988a6b5f960232da096` |
| `experiments/best_phase5_clf.joblib` | 102,854,211 | `0b58981fb33297a790fac172b82c753be7a0b996a8c1d82887f604568f963133` |

**Unknowns resolution matrix** (from `PROJECT_UNKNOWN_RESOLUTION.md`; all 5 resolved):

| ID | Unknown | Status | Conclusion |
|---|---|---|---|
| U1 | `best_phase5_vectorizer.joblib` (613 B) | RESOLVED | OBSOLETE — unpicklable `CombinedVectorizer` stub; no script loads it |
| U2 | Contents of empty dirs (`app/`, `configs/`, `models/`, `notebooks/`, `utils/`) | RESOLVED | All empty scaffolding; safe to remove |
| U3 | Does `test_seed.py` pass? | RESOLVED | Yes — 3/3 PASSED |
| U4 | `exec()` in `phase10_inference.py` — does it cause inference divergence? | RESOLVED | NO — embedded code and on-disk `predict.py` are functionally equivalent |
| U5 | Actual feature dimension count | RESOLVED | 535,692 (433,832 word + 101,860 char = `clf.n_features_in_`) |

## 15a. Release Gate Matrix

From `PROJECT_COMPLETION_AUDIT.md` (pre-cleanup audit, 2026-11-03):

| Gate | PASS | FAIL | UNKNOWN |
|---|---|---|---|
| 1 — Functionality | 11 | 0 | 0 |
| 2 — Model Quality | 15 | 2 | 0 |
| 3 — Inference | 10 | 0 | 0 |
| 4 — Testing | 8 | 2 | 0 |
| 5 — Engineering | 4 | 7 | 0 |
| 6 — Documentation | 16 | 2 | 0 |
| 7 — Reproducibility | 4 | 2 | 1 |
| 8 — Repository | 1 | 6 | 0 |
| **TOTAL** | **69** | **21** | **1** |

The 21 FAIL items are addressed by the cleanup (Phases A–G in the plan): broken `requirements.txt` reverted, hard-coded paths parameterized, `exec()` removed, orphaned artifacts and empty directories deleted, and documentation gaps filled. The 1 UNKNOWN was resolved by `PROJECT_UNKNOWN_RESOLUTION.md` (U5: 535,692 features confirmed). Verdict: **NEARLY COMPLETE** → **READY FOR FINAL ACCEPTANCE** after cleanup.

## 16. Known Limitations and Risks

1. **Performance**: test Macro F1 0.5762 is below the original 0.65 target. A plausible contributor is dataset keyword overlap (98.8% of resumes match 2+ categories), which may inflate the error rate; however, keyword overlap does not by itself prove genuine label ambiguity or label noise, so the ~60% "dataset-inherent" estimate is a hypothesis, not a measured figure.
2. **Class imbalance**: 5.45x ratio; BPO (22 total) test recall 0.143; ARTS, AUTOMOBILE, CONSULTANT unstable. Small-class numbers move with single samples.
3. **Uncalibrated scores**: decision-function margins only; consumers that need probabilities must add calibration themselves, and must re-fit it on data — no calibrated interface exists.
4. **Artifact distribution**: inference is not runnable from a bare copy of this directory; the three `.joblib` files must be supplied or reproduced.
5. **No probability calibration, no CI, no packaging** (`pyproject.toml`), no lint config: deliberate for a single-contributor portfolio project, but a real deployment would need them.
6. **Preprocessing duplication**: `clean_text`/`strip_header` are re-implemented inline in multiple scripts (and in `predict.py`); behavior is consistent but the duplication is a maintenance risk if the rule ever changes.
7. **Dataset-specific**: results transfer only within this taxonomy; the 24 labels and the keyword-dense resume format are specific to this dataset.

**Engineering issues catalogued in `PROJECT_ANALYSIS.md`** (P1–P10; resolved in cleanup except where noted):

| ID | Severity | Issue |
|---|---|---|
| P1 | High | Hard-coded absolute data path in every script (resolved: `RESUME_CSV`/`RESUME_DATA_DIR` env vars) |
| P2 | Low | No input validation in `predict_resume()` beyond the `isinstance` check |
| P3 | Medium | Uncalibrated confidence scores (documented, not a defect) |
| P4 | Medium | Duplicated preprocessing logic in 6+ scripts (acceptable maintenance risk) |
| P5 | Low | `exec()` in `phase10_inference.py` (resolved: replaced with `from predict import predict_resume`) |
| P6 | Low | No CI/CD or linting config (out of scope for portfolio project) |
| P7 | Low | `requirements.lock` redundant with `requirements.txt` (both retained intentionally) |
| P8 | Low | Orphaned model artifacts `best_phase5_model.joblib` + `best_phase5_vectorizer.joblib` (resolved: removed) |
| P9 | Low | 7 empty `src/` sub-packages (resolved: removed) |
| P10 | Medium | BPO recall = 0.143 with only 7 test samples (data-scarcity limitation, documented) |

## 17. Final Decisions and Recommendations

- **Why this model**: it was the best of 21 Phase-5 experiments on the validation set (val Macro F1 0.6137; +0.0808 above the 0.5329 baseline CV — note these are different measurement protocols, not a verified like-for-like CV improvement) and outperformed every embedding variant by 0.05-0.25 on test Macro F1. Combined word+char TF-IDF retains explicit token evidence while the character n-grams add robustness to typos and morphology.
- **Rejected approaches**: embeddings (smoothing destroys keyword signal), LSA (loses rare-but-discriminative tokens), Naive Bayes (independence assumption violated), fine-tuned transformers (compute constraint, CPU-only).
- **Why no further experiments now**: the remaining gap to 0.65 may be attributable in part to dataset keyword overlap, but this is a hypothesis — not a verified ceiling — and could be closed by an improved model on enriched or relabelled data. No additional experiments were run in this project; the decision to stop is a resource constraint, not a demonstrated impossibility.
- **Conditions that would justify retraining**: (a) relabeled or enriched data, (b) a calibrated-probability requirement, (c) a new distribution of resume domains not covered by the 24 classes.

## 18. Reproducibility and Project Maintenance

- **Environment**: `pip install -r requirements.lock` (136 pinned packages, validated environment; Python 3.14 recorded at release audit; the model files also load under scikit-learn 1.7.2 and produced identical predictions). Direct-dependency quick install: `pip install -r requirements.txt`.
- **Seed**: 42 (default; `SEED` env var overrides). All splits, CV folds, and model `random_state` values use it.
- **Split reproducibility**: `data/splits/splits.json` + `data/splits/{train,val,test}.csv` are the locked evaluation definition; regenerating requires a new seed and a documented justification.
- **Key commands**:
  - `python predict.py --resume data/samples/engineer.txt --top_k 3` — inference demo
  - `python -m pytest tests/ -v` — full test suite
  - `python scripts/phase5_tuning.py` — retrain the frozen configuration (reproduces the artifacts)
- **Artifact management**: the three `.joblib` files are the only required runtime artifacts; `phase5_results.json` / `phase8_results.json` in `experiments/` and `reports/artifacts/*.json` are evidence records only.

## 18a. Finalization and Cleanup History

From `reports/CLEANUP_REPORT.md` (2026-11-03):

- **14 files modified** during finalization: `requirements.txt` restored to pinned set; all 12 training scripts parameterized with `RESUME_CSV`/`RESUME_DATA_DIR` env vars; `exec()` removed from `phase10_inference.py`; `.gitignore` updated; README and `FINAL_REPORT.md` corrected for artifact sizes.
- **2 orphaned artifacts removed**: `best_phase5_model.joblib` (102.8 MB, redundant parallel LinearSVC dump) and `best_phase5_vectorizer.joblib` (613 B, unpicklable stub).
- **11 empty directories removed**: `app/`, `configs/`, `models/`, `notebooks/`, `utils/`, and 6 empty `src/` sub-packages.
- **`exec()` removed** from `phase10_inference.py`: the self-test now uses `from predict import predict_resume`; `predict.py` is maintained independently at the repo root.
- **All 17 pytest tests pass** at cleanup time; CLI inference verified; artifact SHA-256 hashes unchanged.

## 18b. Unauthorized-Changes Catalog

From `PROJECT_STATUS.md` §11 (prior audit session):

| File | Action | Disposition |
|---|---|---|
| `predict.py` | Modified: added docstring, `_REQUIRED_ARTIFACTS` guard, `argmax` confidence | KEEP — correct and behavior-equivalent |
| `requirements.txt` | Modified: trimmed to 10 unpinned packages | REVERTED — restored to original 137-package pinned set during cleanup |
| `README.md` | Created by audit session | KEEP — accurate and useful |
| `tests/test_predict.py` | Created by audit session (14 tests) | KEEP — provides regression coverage |

## 19. Conclusion

The project demonstrates a complete, honest ML engineering lifecycle on a real-world messy text dataset: leakage was detected, quantified (0.0524), and mitigated before any modeling; every experimental choice is recorded with its gate decision; the final evaluation is on a locked test set; and the missed 0.65 target is explicitly attributed to a combination of dataset keyword overlap, small-class scarcity, and model-family constraints — not papered over as a proven upper bound.

What it does **not** demonstrate: a model that beats the estimated ~0.65-0.67 performance ceiling (which remains an analytical hypothesis, not a measured limit), a calibrated probability interface, or a deployable service. Read together with section 16, that is the accurate statement of the project readiness.

## 20. Source Documents and Evidence

**Consolidated into this report** (previously standalone; removed after migration):

- Phase reports: `01_audit_report.md`, `01b_leakage_report.md`, `02_eda_findings.md`, `03_split_strategy.md`, `04_baseline_report.md`, `05_tuning_report.md`, `06_robustness.md`, `07_error_analysis.md`, `08_embedding_report.md`, `FINAL_REPORT.md`
- Project audit documents: `PROJECT_ANALYSIS.md`, `PROJECT_STATUS.md`, `PROJECT_COMPLETION_AUDIT.md`, `PROJECT_UNKNOWN_RESOLUTION.md`, `FINAL_ACCEPTANCE_REPORT.md`, `CLEANUP_REPORT.md`

**Retained raw evidence**:

| File | What it records |
|---|---|
| `experiments/phase5_results.json` | 21-experiment tuning grid, winner, gate decision |
| `experiments/phase8_results.json` | 4 embedding experiments, per-class recall, NO-GAIN gate |
| `reports/artifacts/04_baseline_results.json` | 4-config baseline CV + per-class recall |
| `reports/artifacts/06_robustness_results.json` | 6-perturbation robustness table with deltas |
| `reports/artifacts/07_error_analysis.json` | confusion matrix, errors by true/predicted class |
| `reports/artifacts/10_test_results.json` | final test metrics: 0.5762 Macro F1, per-class recall, latency |
| `reports/artifacts/final_model_decision.json` | Phase 9 selection record (Phase 5 model retained) |

**Known evidence gap**: one Phase 8 table in the archived embedding report listed an "LR_TF-IDF (15K)" variant at test Macro F1 0.5607 with no supporting entry in `experiments/phase8_results.json` (whose best variant is `LR_Combined`, 0.4586). The authoritative decision (NO GAIN -> use Phase 5) is unaffected, but that single intermediate value could not be reconciled and is flagged here rather than silently dropped. No metric in this report was invented; every number traces to a file above or to the raw records of Phases 4, 5, 6, 7, and 10.

**Known errors in archived source documents** (not propagated into this report):

| Error | Wrong source(s) | Correct value |
|---|---|---|
| "94%" multi-domain keyword rate | `final_model_decision.md`, `FINAL_REPORT.md` | 98.8% (2,453 / 2,484 per `02_eda_findings.md`) |
| BPO "3 test samples" | `FINAL_REPORT.md`, `CHANGELOG.md`, `FINAL_ACCEPTANCE_REPORT.md` | 7 test samples (per `10_test_results.json` and `data/splits/test.csv`) |
| 0.6137 labelled as "Test Macro F1" | `08_embedding_report.md`, `final_model_decision.md` | 0.6137 is CV/val; test Macro F1 = 0.5762 |
| CV = val (identical 0.61369853) in `phase5_results.json` | `05_tuning_report.md`, archived docs | Verified data flow: `scripts/phase5_tuning.py:233` computes a single val-set `f1_score(y_val, y_pred)` and writes it into both `cv_macro_f1_mean` and `val_macro_f1`; `cv_macro_f1_std` is hardcoded to `0.0`. The validation score was recorded in the CV field, not that an independent CV was never computed — no 5-fold CV loop exists for the combined experiment. 0.6137 is therefore a validation Macro F1, not a CV estimate. |
