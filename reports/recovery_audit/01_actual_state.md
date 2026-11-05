# 01 - Actual Project Documentation State

**Audit date**: 2026-11-04
**Method**: read-only filesystem inspection + git status / git log (no modifications)

## Root-level Markdown files

| File | Size | Git status | Notes |
|---|---|---|---|
| CHANGELOG.md | 3,476 B | tracked, committed | v1.0.0 entry, complete |
| CHANGELOG_FIXES.md | 1,792 B | tracked, committed | Fix #1 entry, complete |
| README.md | 3,128 B | tracked, MODIFIED (unstaged) | Rewritten during consolidation |
| LICENSE | 1,082 B | tracked, committed | MIT |
| PROJECT_ANALYSIS.md | - | DELETED (staged) | Recoverable from git show HEAD: |
| PROJECT_STATUS.md | - | DELETED (staged) | Recoverable from git show HEAD: |
| PROJECT_COMPLETION_AUDIT.md | - | DELETED (staged) | Recoverable from git show HEAD: |
| PROJECT_UNKNOWN_RESOLUTION.md | - | DELETED (staged) | Recoverable from git show HEAD: |
| FINAL_ACCEPTANCE_REPORT.md | - | DELETED (staged) | Recoverable from git show HEAD: |
| predict.py | 3,512 B | tracked, committed | Inference module |

## reports/ - current on-disk state

| File | Size | Git status |
|---|---|---|
| PROJECT_REPORT.md | 20,242 B | untracked (new, created by consolidation) |
| artifacts/04_baseline_results.json | 4,453 B | untracked (new path) |
| artifacts/06_robustness_results.json | 7,343 B | untracked (new path) |
| artifacts/07_error_analysis.json | 2,495 B | untracked (new path) |
| artifacts/10_test_results.json | 1,342 B | untracked (new path) |
| artifacts/final_model_decision.json | 357 B | untracked (new path) |

**Deleted from disk (recoverable via git HEAD)**:
01_audit_report.md, 01b_leakage_report.md, 02_eda_findings.md, 03_split_strategy.md,
04_baseline_report.md, 05_tuning_report.md, 06_robustness.md, 07_error_analysis.md,
08_embedding_report.md, CLEANUP_REPORT.md, FINAL_REPORT.md, final_model_decision.md

**Moved to reports/artifacts/ (unstaged-deleted at original path)**:
04_baseline_results.json, 06_robustness_results.json, 07_error_analysis.json,
10_test_results.json, final_model_decision.json

## experiments/

| File | Size | Status |
|---|---|---|
| best_phase5_word_vec.joblib | 12,872,968 B (12.3 MB) | on disk, gitignored |
| best_phase5_char_vec.joblib | 1,944,189 B (1.9 MB) | on disk, gitignored |
| best_phase5_clf.joblib | 102,854,211 B (98.1 MB) | on disk, gitignored |
| phase5_results.json | ~124 KB | on disk, gitignored |
| phase8_results.json | ~5.4 KB | on disk, gitignored |

Total artifact size: 117,671,368 bytes = 112.2 MB (documented as ~117 MB in multiple docs; see 04_fact_verification for discrepancy)

## scripts/ and tests/

All 12 pipeline scripts present. tests/test_predict.py (14 tests) and tests/test_seed.py (3 tests) present, 17/17 passing.

## Git repository state

- Git repository EXISTS: .git/ directory present at project root
- Branch: master only
- Tags: v1.0.0 (annotated, points at commit 27493e9)
- Commits: 12 total
- Working tree: 18 files staged for deletion; 5 JSON files unstaged-deleted at original paths; README.md modified (unstaged); reports/PROJECT_REPORT.md and reports/artifacts/ untracked
- No remote configured

## Original document recovery status

All 18 staged-deleted and 5 unstaged-deleted files are FULLY RECOVERABLE from git show HEAD:<path>.
No IDE local history, Windows File History, or Recycle Bin recovery is needed.
