# Changelog

All notable changes to the project.

## [1.0.0] — 2026-11-04

### Added
- `predict.py` inference module (module + CLI) with lazy model loading, artifact
  existence checks, and documented `confidence_score` semantics (raw LinearSVC
  decision value, NOT a calibrated probability).
- `tests/test_predict.py` — 14 regression tests for inference, preprocessing,
  and artifact loading.
- `README.md` — project overview, results, quick start, artifact table,
  reproducibility strategy, and known limitations.
- Phase 4–10 pipeline scripts, reports, and results JSONs (previously
  untracked; the committed history only covered Phases 0–3).
- `LICENSE` (MIT), `CHANGELOG.md`, and `CHANGELOG_FIXES.md` (bug-fix log,
  now includes Fix #1 for this release).
- `data/samples/engineer.txt` — sample input for the documented CLI example.

### Changed
- **Path portability**: all 12 training/analysis scripts now resolve the
  dataset via `RESUME_CSV` / `RESUME_DATA_DIR` env vars (default:
  `data/Resume.csv`), replacing hard-coded absolute paths. No behavior change
  when run from the repo root.
- **`requirements.txt`**: restored to pinned versions from `requirements.lock`
  (the 136-package validated environment). The file lists the 11 packages
  directly imported by project code, pinned exactly; `pip install -r
  requirements.lock` reproduces the full environment.
- **`scripts/phase10_inference.py`**: removed `exec()`-based code generation;
  the self-test now uses `from predict import predict_resume`.
- **`.gitignore`**: excludes `data/Resume.csv`, `data/Resume.zip`, embedding
  caches, `__pycache__/`, `.pytest_cache/`, and virtual environments.
- **Documentation accuracy**: corrected model artifact sizes to ~117 MB total
  (word vec 12.9 MB + char vec 1.9 MB + classifier 102.9 MB) in README and
  `reports/FINAL_REPORT.md`; added the `confidence_score` caveat to
  `reports/FINAL_REPORT.md`.

### Removed
- `experiments/best_phase5_model.joblib` (102.9 MB) — redundant parallel dump
  of the same LinearSVC as `best_phase5_clf.joblib`; never loaded by any
  script. Recorded in `PROJECT_UNKNOWN_RESOLUTION.md` (U1).
- `experiments/best_phase5_vectorizer.joblib` (613 B) — unpicklable
  `CombinedVectorizer` stub; obsolete. Recorded in `PROJECT_UNKNOWN_RESOLUTION.md` (U1).
- 11 empty scaffolding directories (`app/`, `configs/`, `models/`,
  `notebooks/`, `utils/`, and 6 empty `src/` sub-packages).
  See `reports/CLEANUP_REPORT.md` §3 for the full list and evidence.

### Artifact distribution policy
The three active model artifacts (~117 MB combined) are **excluded from git**
and are not included in this repository. Obtain them by either:
- **Option C (reproduce)**: `pip install -r requirements.lock`, then
  `python scripts/phase5_tuning.py` (dataset: `data/Resume.csv` +
  `data/splits/splits.json`), or
- **Option B (distribute)**: the three `.joblib` files as release assets.
Git LFS (Option A) was not adopted.

### Known limitations (not a defect — documented results)
- Test Macro F1 = 0.5762; the 0.65 target was not met. The gap is attributed
  to inherent dataset ambiguity (98.8% of resumes contain keywords from
  2+ domains) and small-class scarcity (BPO: 7 test samples, 0.143 recall).
- `confidence_score` is a raw LinearSVC decision value, not a calibrated
  probability.
- The model artifacts themselves are not tracked in git; a fresh clone
  requires artifact distribution or reproduction to run inference.
