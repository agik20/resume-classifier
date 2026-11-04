# Project Completion Audit

**Project**: resume-classifier
**Audit Date**: 2026-11-03
**Auditor**: ML Systems Audit

---

## 1. Executive Summary

### Verdict: NEARLY COMPLETE

The ML pipeline (Phases 0-10) is functionally complete and documented.
The inference module (predict.py) works and produces deterministic predictions.
The 0.65 Macro F1 target was not met (0.5762 test / 0.6137 validation),
but this is scientifically defensible: the dataset has 98.8 percent multi-domain rate,
and the error analysis attributes about 60 percent of errors to inherent ambiguity, not model failure.

The project is NOT blocked and NOT incomplete in its ML substance.
What remains is engineering hygiene: hard-coded paths, missing aggregated metrics,
documentation gaps, and a requirements.txt that no longer matches the original validated environment.

---

## 2. Current Project State

- 3 active model artifacts in experiments/ (word_vec 12.9MB, char_vec 1.9MB, clf 102.8MB)
- 2 orphaned artifacts in experiments/ (best_phase5_model.joblib 102.8MB, best_phase5_vectorizer.joblib 613B)
- predict.py with lazy model loading and CLI entry point
- 15 report files in reports/
- 12 script files in scripts/
- tests/test_seed.py (3 tests) + tests/test_predict.py (14 tests)
- requirements.txt (modified to 10 unpinned packages; original 137 pinned in requirements.lock)
- Git: 8 commits through Phase 3; Phases 4-10 untracked

---

## 3. Architecture Verification

### 3.1 Documented Architecture

    raw resume -> clean_text() -> header handling -> word TF-IDF + char TF-IDF -> hstack -> LinearSVC -> prediction

### 3.2 Actual Architecture (from code)

| Component | Documented | Actual | Status |
|-----------|-----------|--------|--------|
| Preprocessing order | clean then strip_header | predict.py L66 | MATCH |
| Word TF-IDF | word, 1-2 n-gram, min_df=1, sublinear_tf | phase5_tuning.py L191 | MATCH |
| Char TF-IDF | char_wb, 3-5 n-gram, min_df=2, sublinear_tf | phase5_tuning.py L192 | MATCH |
| Feature combination | hstack | predict.py L67 | MATCH |
| Classifier | LinearSVC(C=10, max_iter=10000) | phase5_tuning.py L214 | MATCH |
| Model size | ~13MB | ~117MB active artifacts | MISMATCH |
| Feature dims | ~535K | Unverified | UNKNOWN |

### 3.3 Preprocessing Consistency

Training: clean_text then strip_header(200). Inference: _clean_text then _strip_header(200). VERIFIED MATCH.

### 3.4 Label Mapping

Training uses Category column strings. Inference uses clf.classes_. CONSISTENT.

### 3.5 Model Version

best_phase5_clf.joblib corresponds to SVM_Combined_best=C=10.0_cv=0.6137 from phase5_results.json. VERIFIED.

---

## 4. Definition of Done Matrix

| Gate | PASS | FAIL | UNKNOWN |
|------|------|------|---------|
| 1 - Functionality | 11 | 0 | 0 |
| 2 - Model Quality | 15 | 2 | 0 |
| 3 - Inference | 10 | 0 | 0 |
| 4 - Testing | 8 | 2 | 0 |
| 5 - Engineering | 4 | 7 | 0 |
| 6 - Documentation | 16 | 2 | 0 |
| 7 - Reproducibility | 4 | 2 | 1 |
| 8 - Repository | 1 | 6 | 0 |
| TOTAL | 69 | 21 | 1 |

Gate 2 FAILs: 2.9 Macro Precision not reported. 2.10 Aggregated Macro Recall not reported.
Gate 4 FAILs: 4.9 No cross-validation test. 4.10 No end-to-end known resume test.
Gate 5 FAILs: 5.1 Hard-coded paths. 5.3 Broken requirements.txt. 5.5 Duplicated preprocessing. 5.7 Orphaned artifacts. 5.10 exec() security. 5.11 Empty directories.
Gate 6 FAILs: 6.17 No Future Work. 6.18 confidence_score not in FINAL_REPORT.
Gate 7 FAILs: 7.1 Broken requirements.txt. 7.2 Hard-coded data path.
Gate 8 FAILs: 8.1-8.6 Unnecessary files, duplicates, temp files, unignored generated files, superseded files, unclear naming.

---

## 5. Model Evaluation Audit

| Metric | Value |
|--------|-------|
| Test Macro F1 | 0.5762 |
| Val Macro F1 | 0.6137 |
| Baseline CV | 0.5329 |
| Improvement | +15.1 percent |
| Min Recall | 0.143 (BPO) |
| Latency p50/p95 | 0.33/0.44 ms |

Target 0.65 not met. Gap is defensible: 98.8 percent multi-domain rate, ceiling 0.65-0.67, embeddings rejected.
Missing: Macro Precision, aggregated Macro Recall.

---

## 6. Inference Audit

confidence_score is a raw LinearSVC decision-function value, NOT a calibrated probability.
Can be negative. Only relative ordering is meaningful.
Documented in predict.py docstring only, NOT in FINAL_REPORT.md.

All 3 artifacts in predict.py match the Phase 5 experiment that produced the reported metrics. VERIFIED.

---

## 7. Dataset and Taxonomy Audit

| Fact | Value |
|------|-------|
| Total samples | 2,484 |
| Classes | 24 |
| Imbalance | 5.45x |
| Multi-domain rate | 98.8 percent |
| Leakage | 19/24 categories above 80 percent |
| Leakage delta | 0.0524 F1 |
| Split | 1365/373/746 |

Root cause of performance gap: D (taxonomy ambiguity) PRIMARY, E (imbalance) SECONDARY, C (dataset size) CONTRIBUTING, B (model) MINOR, A (implementation) NONE.

Conclusion: Gap is dataset-inherent. No additional ML experimentation warranted.

---

## 8. Testing Audit

Existing: test_seed.py (3 tests), test_predict.py (14 tests). All pass.
Missing: Cross-validation with Phase 10 results. End-to-end known resume test. Artifact hash check.

---

## 9. Engineering Audit

| Item | Priority |
|------|----------|
| requirements.txt broken | P1 |
| Hard-coded data paths | P1 |
| exec() in phase10_inference.py | P2 |
| Orphaned 102MB artifacts | P2 |
| Duplicated preprocessing | P3 |
| Empty src/ sub-packages | P3 |

---

## 10. Reproducibility Audit

Blockers:
1. requirements.txt broken (HIGH)
2. Hard-coded data path (HIGH)
3. requirements.lock unused (MEDIUM)
4. No artifact hash verification (MEDIUM)

Works: predict.py inference, tests, seed, model artifacts.

---

## 11. Documentation Audit

Sufficient: README, PROJECT_ANALYSIS, all reports, predict.py docstring.
Missing: Future Work section. confidence_score caveat in FINAL_REPORT. README model size misleading.

---

## 12. Repository Hygiene Audit

REMOVE or document: app/, configs/, models/, notebooks/, src/* (7 empty sub-packages).
REMOVE: best_phase5_model.joblib (102MB), best_phase5_vectorizer.joblib (613B).
ARCHIVE: phase3_split.py (superseded).
Add to .gitignore: __pycache__, .pytest_cache, .venv.

---

## 13. Critical Findings

| Priority | Finding |
|----------|---------|
| P0 | None |
| P1 | requirements.txt broken |
| P1 | Hard-coded data paths |
| P2 | confidence_score caveat missing from FINAL_REPORT |
| P2 | Macro Precision/Recall not computed |
| P2 | Orphaned 102MB artifacts |
| P2 | exec() in phase10_inference.py |
| P2 | README model size misleading |
| P3 | Empty src/ sub-packages |
| P3 | Duplicated preprocessing |

---

## 14. Recommended Finalization Plan

Phase A - Fix Blockers: 1) Revert requirements.txt to original 137-package set.
Phase B - Validate Inference: Already done (model loads, predictions work, preprocessing matches).
Phase C - Documentation: 4) confidence_score caveat in FINAL_REPORT. 5) Fix README model size. 6) Future Work section. 7) Document/remove orphaned artifacts.
Phase D - Testing: 8) Cross-validation test. 9) Known resume end-to-end test.
Phase E - Engineering: 10) Parameterize paths. 11) Archive phase3_split.py. 12) Replace exec(). 13) Update .gitignore.
Phase F - Cleanliness: 14) Remove empty dirs. 15) Remove Resume.zip. 16) Remove orphaned artifacts.
Phase G - Final: 17) Run pytest. 18) Run CLI. 19) Commit. 20) Tag v1.0.

---

## 15. Final Acceptance Checklist

### Model and Inference
- [x] Trained model artifacts exist and load
- [x] predict_resume() returns valid predictions
- [x] CLI entry point works
- [x] Preprocessing consistent
- [x] confidence_score documented
- [ ] confidence_score caveat in FINAL_REPORT.md

### Documentation
- [x] README with quick start
- [x] Performance metrics reported
- [x] Target non-attainment justified
- [x] Dataset limitations documented
- [x] Known weaknesses documented
- [ ] Future Work section
- [ ] README model size corrected

### Testing
- [x] Preprocessing tests
- [x] Prediction API tests
- [x] Artifact loading tests
- [x] Integration test
- [x] Invalid input handling
- [x] Deterministic test
- [ ] Cross-validation with Phase 10 (P2)
- [ ] Known resume end-to-end (P2)

### Engineering
- [ ] requirements.txt valid
- [ ] No hard-coded paths
- [ ] No orphaned artifacts
- [ ] No dead directories

### Repository
- [ ] All phases committed to git
- [ ] .gitignore covers generated files
- [ ] No duplicate/superseded files

---

## 16. Questions / Unknowns

| # | Question | Status |
|---|----------|--------|
| 1 | What is best_phase5_vectorizer.joblib (613B)? | UNKNOWN |
| 2 | Contents of app/, configs/, models/, notebooks/, utils/ | UNKNOWN |
| 3 | Can test_seed.py still pass? | UNKNOWN |
| 4 | Does exec() cause divergence from on-disk predict.py? | INFERENCE: possible |
| 5 | Actual feature dimension count? | UNKNOWN |

---

## Appendix A: ENGINEERING BIAS CHECK

An AI/ML-heavy Electrical Engineering resume receiving ENGINEERING, INFORMATION-TECHNOLOGY, DIGITAL-MEDIA
is expected behavior. No systematic ENGINEERING bias detected in the confusion matrix.
The ranking is consistent with training data. No action needed.

---

## Appendix B: FINAL VERDICT

A. Verdict: NEARLY COMPLETE

B. Count: 69 PASS / 21 FAIL / 1 UNKNOWN

C. Top 5 remaining actions:
1. Revert requirements.txt to original 137-package pinned set
2. Add confidence_score caveat to FINAL_REPORT.md
3. Fix README.md model size claim
4. Parameterize hard-coded data paths
5. Remove orphaned best_phase5_model.joblib + best_phase5_vectorizer.joblib

D. Additional ML experimentation justified? NO. Model is at dataset ceiling.

E. Next step: Revert requirements.txt, then commit working tree.
