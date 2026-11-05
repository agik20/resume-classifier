# 05 - README Structural Audit

Target: README.md (3,128 bytes, modified/unstaged on disk)

## 1. Duplicate headings
None found.

## 2. Duplicate paragraphs
None found.

## 3. Broken Markdown tables
Issue A: Dataset table first row is empty cells instead of named column headers.

## 4. Incomplete code blocks
None found.

## 5. Truncated text
None found.

## 6. Stale / Broken links
The Key Reports section lists 5 files that no longer exist on disk:
- reports/02_eda_findings.md (DELETED)
- reports/05_tuning_report.md (DELETED)
- reports/07_error_analysis.md (DELETED)
- reports/final_model_decision.md (DELETED)
- reports/FINAL_REPORT.md (DELETED)
These 5 references are stale. Should be replaced with link to reports/PROJECT_REPORT.md.

## 7. Contradictory model metrics
BPO sample count: README says BPO 0.14 recall (only 3 test samples).
Actual: 7 BPO test samples per test.csv. 0.143 = 1/7. The 3 is WRONG.
All other metrics consistent with primary evidence.

## 8. Artifact sizes
README: 12.9 MB + 1.9 MB + 102.9 MB = ~117 MB total.
Actual (decimal MB): 12.87 + 1.94 + 102.85 = 117.67 MB. VERIFIED.

## 9. Installation instructions
No conflict. requirements.txt (11 pkgs) vs requirements.lock (136 pkgs) correctly distinguished.

## 10. Repository structure
Matches on-disk state. No incorrect entries.

## 11. Git claims
No unsupported claims found. .gitignore and git repo both exist and are correctly described.

## DEFECTS SUMMARY
| # | Defect | Severity |
|---|---|---|
| 1 | 5 stale references in Key Reports section | HIGH |
| 2 | BPO 3 test samples should be 7 | MEDIUM |
| 3 | Dataset table empty header row | LOW |
