# 02 - Recovery Results

**Method**: git show HEAD:<path> (read-only, no modifications to git state)

All 22 files below were verified recoverable. No external recovery sources (IDE history,
File History, Recycle Bin, OneDrive sync) were needed or consulted.

## Recovered Files (git HEAD)

| File | Size in HEAD | Status |
|---|---|---|
| FINAL_ACCEPTANCE_REPORT.md | 7,751 B (157 lines) | RECOVERED - full content readable |
| PROJECT_ANALYSIS.md | full file | RECOVERED |
| PROJECT_STATUS.md | full file | RECOVERED |
| PROJECT_COMPLETION_AUDIT.md | full file | RECOVERED |
| PROJECT_UNKNOWN_RESOLUTION.md | full file | RECOVERED |
| reports/01_audit_report.md | full file | RECOVERED |
| reports/01b_leakage_report.md | full file | RECOVERED |
| reports/02_eda_findings.md | full file | RECOVERED |
| reports/03_split_strategy.md | full file | RECOVERED |
| reports/04_baseline_report.md | full file | RECOVERED |
| reports/05_tuning_report.md | full file | RECOVERED |
| reports/06_robustness.md | full file | RECOVERED |
| reports/07_error_analysis.md | full file | RECOVERED |
| reports/08_embedding_report.md | full file | RECOVERED |
| reports/CLEANUP_REPORT.md | full file | RECOVERED |
| reports/FINAL_REPORT.md | 4,322 B | RECOVERED |
| reports/final_model_decision.md | full file | RECOVERED |
| reports/04_baseline_results.json | 4,453 B | RECOVERED |
| reports/06_robustness_results.json | 7,343 B | RECOVERED |
| reports/07_error_analysis.json | 2,495 B | RECOVERED |
| reports/10_test_results.json | 1,342 B | RECOVERED |
| reports/final_model_decision.json | 357 B | RECOVERED |

## Not Recoverable

No files were found to be unrecoverable. All deleted documents exist in git HEAD.

## Untracked Files (created after HEAD, no git history)

| File | Notes |
|---|---|
| reports/PROJECT_REPORT.md | Created by consolidation; only exists on disk; no git commit |
| reports/artifacts/*.json (5 files) | Moved from reports/ root; no git commit at new path |

These untracked files cannot be recovered from git if deleted - their only copy is on disk.
