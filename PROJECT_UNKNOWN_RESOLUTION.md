# Project Unknown Resolution

## 1. Executive Summary

**Status: FULLY RESOLVED**

All 5 UNKNOWN findings from PROJECT_COMPLETION_AUDIT.md have been resolved to verified facts via static inspection and read-only artifact loading. No project files were modified; the only file created is this report.

## 2. Unknown Resolution Matrix

| ID | Original Unknown | Status | Evidence | Conclusion |
|----|------------------|--------|----------|------------|
| U1 | best_phase5_vectorizer.joblib (613B) | RESOLVED | pickle payload contains CombinedVectorizer + wv/cv attrs; 613B; no script loads it | OBSOLETE |
| U2 | Directory contents | RESOLVED | ls -A + git ls-files per dir | 5 dirs empty; src/ holds seed util + empty sub-packages |
| U3 | test_seed.py passes? | RESOLVED | pytest tests/ -v -> 3/3 PASSED | YES, passes |
| U4 | exec() divergence | RESOLVED | full read of both files (section 10) | NO FUNCTIONAL DIVERGENCE |
| U5 | Feature dimensions | RESOLVED | joblib.load of active artifacts (section 4) | 535,692 combined features |

## 3. Artifact Verification

| Artifact | Path | Type | Size (B) | Used by predict.py? | Status |
|----------|------|------|----------|---------------------|--------|
| word vectorizer | experiments/best_phase5_word_vec.joblib | TfidfVectorizer (word, 1-2, min_df=1) | 12,872,968 | YES | ACTIVE |
| char vectorizer | experiments/best_phase5_char_vec.joblib | TfidfVectorizer (char_wb, 3-5, min_df=2) | 1,944,189 | YES | ACTIVE |
| classifier | experiments/best_phase5_clf.joblib | LinearSVC(C=10, max_iter=10000) | 102,854,211 | YES | ACTIVE |
| combined model | experiments/best_phase5_model.joblib | LinearSVC (same size as clf) | 102,854,211 | NO | REDUNDANT |
| combined vectorizer | experiments/best_phase5_vectorizer.joblib | CombinedVectorizer stub | 613 | NO | OBSOLETE |
| results | experiments/phase5_results.json | JSON | 124,358 | no | RECORD |
| results | experiments/phase8_results.json | JSON | 5,400 | no | RECORD |

Key facts:
- The 3 ACTIVE artifacts are exactly the set predict.py loads (_REQUIRED_ARTIFACTS), and exactly the three that phase10_inference.py and phase6_robustness.py load.
- best_phase5_clf.joblib and best_phase5_model.joblib are the same byte size (102,854,211 B); cmp/md5sum show they differ at byte 1041 - two independent dumps of the same LinearSVC, not a copy. clf is active; model is a redundant parallel save.
- best_phase5_vectorizer.joblib is only 613 bytes; it cannot contain vectorizer vocabularies. It is a serialized CombinedVectorizer object whose wv/cv attributes are references, not embedded data. Unpickling it in isolation fails with AttributeError: module __main__ has no attribute CombinedVectorizer. Meaningful only inside the Phase 5 training process.

## 4. Feature Dimension Verification

Measured by loading the active artifacts (joblib.load):

| Quantity | Value |
|----------|-------|
| word vectorizer features (len(vocabulary_)) | 433,832 |
| char vectorizer features (len(vocabulary_)) | 101,860 |
| word + char (combined) | 535,692 |
| classifier n_features_in_ | 535,692 |
| match (word+char == clf.n_features_in_) | True |
| classes | 24 |
| C | 10.0 |
| max_iter | 10000 |

The pipeline holds: word TF-IDF (433,832) + char TF-IDF (101,860) -> scipy.sparse.hstack -> LinearSVC (535,692 input features). Dimensions are exactly consistent. The audit estimate of ~535K is confirmed at 535,692.

## 5. Inference Consistency Verification

End-to-end trace of predict.py:
1. Preprocessing: mitigated = _strip_header(_clean_text(text), 200). _clean_text lowercases + collapses whitespace; _strip_header removes first 200 chars. Identical to training. CONSISTENT.
2. Word vectorizer: word_vec.transform([mitigated]) -> 433,832-dim sparse.
3. Char vectorizer: char_vec.transform([mitigated]) -> 101,860-dim sparse.
4. Combine: hstack -> 535,692-dim, matches classifier input. COMPATIBLE.
5. Classifier: clf.decision_function(X) -> 24 per-class raw scores.
6. Labels: clf.classes_ -> 24 category strings for argmax/top-k. CONSISTENT with training Category column.
7. Top-k: np.argsort(decisions)[::-1][:top_k] with clf.classes_[i] lookup.
8. Score: confidence_score = float(decisions[best_idx]) - a raw LinearSVC decision_function value, NOT a calibrated probability. Confirmed by code and docstring (lines 12-16). Negative values possible; only relative ordering meaningful.

Artifact consistency: the three loaded artifacts are the exact Phase 5 SVM_Combined_best=C=10.0_cv=0.6137 set. No divergence between training-time and inference-time artifacts.

## 6. Test Results

Command: python -m pytest tests/ -v (Python 3.14.0, pytest 8.1.1, win32)

    collected 17 items
    tests/test_predict.py :: 14 passed
    tests/test_seed.py   ::  3 passed
    ============================= 17 passed in 8.50s =============================

- 17 passed, 0 failed, 0 errors.
- tests/test_seed.py: 3/3 PASSED (resolves U3).
- tests/test_predict.py: 14/14 PASSED.
- No dependency-missing blocker; environment is complete enough to run the suite.

## 7. Repository / Git State

- Branch: master (single local branch; no remotes).
- Total commits: 7.
- Phases committed: 0, 1, 1b, 2, 3. Tracked training scripts: phase1_audit.py, phase1b_compare.py, phase1b_leakage.py, phase2_eda.py, phase3_split.py.
- Phases 4-10: UNTRACKED / NOT COMMITTED. No git commit mentions Phase 4 through 10.
- experiments/: NOT tracked by git (git ls-files experiments/ is empty). No model artifact is version-controlled.
- Untracked files (git status --short): requirements.txt (M, modified); all of experiments/, predict.py, data/Resume.csv, data/Resume.zip, reports/04,05,06,07,08,10,FINAL_REPORT; scripts/phase3_group_split.py, phase4_baseline.py, phase5_tuning.py, phase6_robustness.py, phase8_embeddings.py, phase10_inference.py; tests/test_predict.py; README.md, PROJECT_ANALYSIS.md, PROJECT_STATUS.md, PROJECT_COMPLETION_AUDIT.md.
- Modified: requirements.txt.
- PROJECT_COMPLETION_AUDIT.md: UNTRACKED.
- No local resets, no staged changes observed.

## 8. Dependency Verification

| File | Lines | Style |
|------|-------|-------|
| requirements.txt | 20 | Unpinned lower-bounds: joblib>=1.4, numpy>=1.26, scikit-learn>=1.5, scipy>=1.12, ... |
| requirements.lock | 136 | Pinned exact: aiohttp==3.14.3, alembic==1.19.1, ... |

Findings:
- requirements.txt is NOT a pinned reproducible subset of requirements.lock. It is a hand-trimmed 20-line minimum core list using >= floors.
- requirements.lock (136 pinned packages) is the original validated environment snapshot and appears authoritative.
- Installing from requirements.txt alone will not reproduce the training environment (versions may drift above the floors). requirements.txt should be restored/derived from requirements.lock.
- Confirms the audit P1 requirements.txt broken finding.

## 9. Directory Audit

| Directory | Contents | Referenced? | Purpose | Status | Removal Candidate? |
|-----------|----------|-------------|---------|--------|--------------------|
| app/ | empty | No | Unknown scaffolding | EMPTY | Yes (safe) |
| configs/ | empty | No | Unknown scaffolding | EMPTY | Yes (safe) |
| models/ | empty | No | Unknown scaffolding (artifacts live in experiments/) | EMPTY | Yes (safe) |
| notebooks/ | empty | No | Unknown scaffolding | EMPTY | Yes (safe) |
| utils/ | empty | No | Unknown scaffolding (real seed util in src/utils/) | EMPTY | Yes (safe) |
| src/ | __init__.py x7 (empty sub-packages) + utils/seed.py | Yes | Seed-utility package; sub-packages empty | SUPPORTING / EMPTY | seed.py keep; empty sub-packages candidates |
| experiments/ | 7 files | Yes | Live model artifacts + results | ACTIVE | Orphans only |
| reports/ | 15 files | Yes | Phase outputs | ACTIVE | No |
| scripts/ | 12 files | Yes | Training/inference pipeline | ACTIVE | No |
| tests/ | test_seed.py, test_predict.py | Yes | Test suite | ACTIVE | No |
| data/ | Resume.csv, Resume.zip | Yes | Dataset | ACTIVE | No |

src/ detail: 7 empty sub-package dirs (data, evaluation, features, inference, models, preprocessing, plus __pycache__) contain only __init__.py with no implementation. The only real code is src/utils/seed.py, which tests/test_seed.py imports and which passes. Empty sub-packages are dead scaffolding.

## 10. exec() Investigation

Location: scripts/phase10_inference.py line 171, exec(inference_code).

What it does:
- inference_code (lines 104-164) is the source string of a provisional predict.py.
- Phase 10 writes that string to disk at lines 165-166.
- Line 171 then runs exec(inference_code) so the in-process predict_resume symbol is defined, enabling the two self-test calls at lines 172-175 without re-reading the file.

Why it exists: a convenient in-process self-test hook at the end of the training run. It does not generate model artifacts and does not modify saved artifacts.

Divergence analysis - the on-disk predict.py has since been hand-edited and is not identical to the inference_code string embedded in phase10_inference.py:

| Aspect | Embedded inference_code (phase10) | On-disk predict.py |
|--------|-----------------------------------|--------------------|
| _load_model missing-artifact check | none | raises FileNotFoundError listing missing files |
| confidence_score | decisions[list(classes).index(prediction)] | decisions[best_idx] where best_idx = argmax |
| docstring | minimal | full, incl. NOT a probability caveat |
| module guards / typing | minimal | fuller |

Classification of the differences:
1. Missing-artifact check - pure defensive code, no effect on prediction values. Not a functional divergence.
2. confidence_score index source - embedded uses list(classes).index(prediction); on-disk uses best_idx = argmax(decisions). For top-1, argmax selects the max-score class, so decisions[best_idx] is the max score. list(classes).index(prediction) finds the position of the predicted label in classes_ and decisions[that_position] is the same label score. Because prediction (from clf.predict) is the label whose score is the maximum, both index to the same class and value in the normal single-max case; they differ only in degenerate ties (equal top scores), measure-zero for real resumes. Conclusion: no functional divergence in practice.

Overall classification: NO FUNCTIONAL DIVERGENCE.

Rationale:
- predict.py (the on-disk deliverable used by tests and CLI) loads the 3 ACTIVE artifacts directly; its preprocessing is identical to training. Its behavior is fully determined by predict.py + the 3 joblib files, not by exec().
- exec(inference_code) affects only the self-test lines inside phase10_inference.py; it does not write, overwrite, or corrupt predict.py at inference time, and it does not generate or modify any model artifact.
- The differences are (a) defensive boilerplate and (b) an equivalent expression for the top-1 score. Neither changes a prediction result.

So exec() is a code-quality/security smell only (audit P2). It does not create a functional inference divergence. It can be removed or replaced (e.g., from predict import predict_resume) with no change to inference behavior.

## 11. Remaining Risks

Evidence-supported risks:
1. No model artifact is under git. experiments/ is untracked. The 3 active artifacts (about 117 MB combined) exist only on this machine; no reproducibility of the exact binary without artifacts + data + requirements.lock.
2. Phases 4-10 not committed. All pipeline scripts from phase4_baseline.py through phase10_inference.py, the reports, predict.py, and tests/test_predict.py are untracked; a fresh clone lacks the entire model-building pipeline.
3. requirements.txt is a 20-line unpinned list, not the 136-line pinned requirements.lock; fresh-environment reproducibility would drift.
4. best_phase5_vectorizer.joblib is an un-picklable 613 B stub (fails to load in isolation) - a confusing dead artifact, not a risk to inference. best_phase5_model.joblib is a 102.8 MB redundant save of the same LinearSVC. Both are safe to remove after documentation.
5. 5 empty scaffolding dirs + 7 empty src/ sub-packages are dead weight.
6. exec() in phase10_inference.py - confirmed no functional divergence; code-quality/security concern, not a correctness risk.

No correctness risk to the shipped predict.py inference path was found.

## 12. Recommended Next Action

Do NOT implement now. Highest-value next action:

Restore requirements.txt from requirements.lock (the 136 pinned packages), so the validated environment is reproducible. Then, as the follow-up commit step: commit the untracked Phases 4-10 pipeline scripts, reports, predict.py, tests/test_predict.py, and (deciding on a git-lfs or exclusion policy for the 117 MB of joblib) the model artifacts; remove the 2 orphaned artifacts + 5 empty dirs + 7 empty src/ sub-packages only after documenting their removal in CHANGELOG_FIXES.md.

This closes the two P1 blockers (broken requirements.txt; untracked reproducibility) and the P2 cleanliness items, in dependency order: reproduce env -> commit pipeline -> clean orphans -> tag v1.0.
