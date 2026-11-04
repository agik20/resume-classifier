# Final Acceptance Report — Resume Classifier v1.0.0

**Date**: 2026-11-04
**Branch**: `master`
**Reviewer**: Release audit (Phases A–F)

---

## A. Release Verdict

**ACCEPTED WITH LIMITATIONS**

The project is a complete, reproducible, honestly documented v1.0.0 release.
The limitations are scientific (documented ML performance ceiling, uncalibrated
scores) and logistical (artifacts distributed outside git), not defects in the
shipped inference path. None are release-blocking.

## B. ML Model

| Property | Value |
|----------|-------|
| Architecture | LinearSVC(C=10, max_iter=10000) on combined word+char TF-IDF |
| Word TF-IDF | analyzer='word', ngram_range=(1,2), min_df=1, sublinear_tf=True, stop_words=None — 433,832 features |
| Char TF-IDF | analyzer='char_wb', ngram_range=(3,5), min_df=2, sublinear_tf=True — 101,860 features |
| Feature dimensions | 535,692 (verified: 433,832 + 101,860 == clf.n_features_in_) |
| Classes | 24 |
| Test Macro F1 | 0.5762 |
| Validation Macro F1 | 0.6137 |
| Baseline (unmitigated) | 0.5329 (+15.1% improvement) |
| Target Macro F1 | 0.65 — **not achieved** (estimated dataset-inherent ceiling 0.65–0.67) |
| Inference latency | 0.33 ms p50 |

## C. Engineering

- **Portability**: all 12 pipeline scripts resolve the dataset via
  `RESUME_CSV` / `RESUME_DATA_DIR` env vars (default `data/Resume.csv`).
  No hard-coded machine paths remain (verified by scan). No `exec()` remains.
- **Dependency reproducibility**: `requirements.txt` (11 directly-imported
  packages, pinned exactly) + `requirements.lock` (136 packages, fully pinned
  validated environment). Both are internally consistent.
- **Inference reliability**: `predict.py` loads exactly the three active
  artifacts, checks for their existence, and its preprocessing
  (lowercase → collapse whitespace → strip 200-char header) matches the
  training pipeline. Deterministic (idempotency test passes).
- **Test results**: `python -m pytest tests/ -v` → **17 passed, 0 failed**
  (`tests/test_predict.py` 14, `tests/test_seed.py` 3).
- **CLI**: `python predict.py --resume data/samples/engineer.txt --top_k 3`
  → `ENGINEERING` (score -0.4034), top-k ordering descending and correct.
- **Documentation**: README (v1.0.0, results, quick start, artifact table,
  limitations, future work), `reports/FINAL_REPORT.md`, `CHANGELOG.md`,
  `CHANGELOG_FIXES.md` (Fix #1), 5 project-analysis reports, `LICENSE` (MIT).

## D. Artifact Integrity

### Active artifacts (hashes measured pre- and post-validation — identical)

| Artifact | Size | SHA-256 |
|----------|------|---------|
| `experiments/best_phase5_word_vec.joblib` | 12,872,968 B | `8cb2f503220722e50b1cc83f9769631a1238485c5195243eaaa4378b12b0a8c7` |
| `experiments/best_phase5_char_vec.joblib` | 1,944,189 B | `28a4aff295a9e7b5770d163e25d255249be592201c8ab988a6b5f960232da096` |
| `experiments/best_phase5_clf.joblib` | 102,854,211 B | `0b58981fb33297a790fac172b82c753be7a0b996a8c1d82887f604568f963133` |

No artifact hash changed during the release validation run.

### Semantic equivalence investigation (deleted `best_phase5_model.joblib`)

The deleted artifact **cannot be recovered**: it was never committed to git
(`git log --all --full-history` returns no commits containing it) and no other
copy exists on disk. **Semantic equivalence therefore cannot be conclusively
verified**, and no such claim is made.

What *can* be stated as evidence:
- `PROJECT_UNKNOWN_RESOLUTION.md` (U1) and the original audit established it
  was a 102,854,211-byte parallel joblib dump of the same LinearSVC saved by
  a second code path in Phase 5; byte-level `cmp` showed it diverged from
  `best_phase5_clf.joblib` at byte 1041 (pickle streaming differences, not a
  different estimator).
- No script or test references it; `predict.py` loads only the three active
  artifacts above.
- Removing it changed no behavior (tests passed before and after; hashes of
  the active set are unchanged).

Residual risk: if the parallel dump had in fact been trained on slightly
different data, it is unrecoverable. This does not affect the shipped model,
which is fully specified by the three active artifacts + `requirements.lock` +
`data/Resume.csv` + `data/splits/splits.json`.

### Distribution policy

**Option C (reproduce) + Option B (distribute as release assets) recommended;
Option A (Git LFS) not adopted.** The ~117 MB artifacts remain excluded from
git. A clone alone is not sufficient to run inference — stated explicitly in
README and `reports/FINAL_REPORT.md`.

## E. Git Release

- **Branch**: `master`
- **Prior history**: 7 commits (Phases 0–3). No force-push, reset, or
  rewrite performed.
- **Release commit**: staged files reviewed via `git diff --cached`; commit
  message `release: finalize resume classifier v1.0.0`.
- **Tag**: `v1.0.0` (annotated, on the release commit; working tree clean at
  tag time).
- **No remote configured** — nothing pushed; no remote push was requested.
- **Excluded from the commit** (by `.gitignore` or absence):
  `data/Resume.csv`, `data/Resume.zip`, `data/processed/embeddings/`,
  `data/raw/`, `experiments/*.joblib`, `.pytest_cache/`, `__pycache__/`,
  `.venv/`, IDE files.
- **Committed**: all source, scripts, tests, reports, docs, split files
  (`data/splits/` — index metadata + CSV subsets, the split definition is
  itself a required artifact), LICENSE, CHANGELOG, `data/samples/`.

## F. Known Limitations

1. **Target not met**: test Macro F1 = 0.5762 vs 0.65 target. Root cause:
   dataset-inherent ambiguity (98.8% of resumes span 2+ domains; ~60% of
   errors are ambiguous, not model failure).
2. **Class imbalance / small-class instability**: BPO 0.14 recall (3 test
   samples); ARTS, AUTOMOBILE, CONSULTANT unstable.
3. **Uncalibrated scores**: `confidence_score` is a raw LinearSVC
   decision-function margin (can be negative; only relative ordering is
   meaningful). No Platt/isotonic calibration applied.
4. **Artifacts not in git**: inference requires the three `.joblib` files to
   be separately distributed or reproduced.
5. **Environment drift note**: the validated environment pins
   scikit-learn 1.9.0 / scipy 1.18.0 / numpy 2.5.2; the audit host ran
   scikit-learn 1.7.2 / scipy 1.16.3 / numpy 2.3.5 and produced identical
   predictions (ENGINEERING, score -0.4034), but `requirements.lock` should
   be used for exact reproducibility.
6. **Unverifiable deleted artifact**: semantic equivalence of the removed
   `best_phase5_model.joblib` could not be confirmed (see §D).
7. **No CI, no lint config, no packaging** (`pyproject.toml`) — out of scope
   for this release; flat-script layout is by design.

## G. Final Verdict

The project is **ready to be presented as a completed portfolio project**.

What it demonstrates end-to-end: a rigorous, phase-gated ML engineering
process (data audit → leakage mitigation → split → baseline → tuning →
robustness → error analysis → embedding exploration → model selection →
inference), honest reporting of a missed performance target with a
data-driven justification, frozen-model release discipline (no artifact
modification during release), and a reproducible, portable engineering
baseline.

This is a **successful release of a model that did not hit its original
target** — which is exactly what the documentation says. A successful release
and a perfect model are different things; both facts are preserved here.

---

*Prepared for v1.0.0 acceptance. All commands listed in §C–§E were executed
and verified on 2026-11-04; results above are recorded observations, not
projections.*
