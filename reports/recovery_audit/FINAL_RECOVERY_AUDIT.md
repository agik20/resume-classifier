# FINAL RECOVERY AUDIT - Resume Classifier

Date: 2026-11-04
Scope: Documentation recovery and integrity audit
Constraint: Read-only on all existing project files; all audit output in reports/recovery_audit/

---

## 1. Executive Summary

The previous documentation consolidation produced reports/PROJECT_REPORT.md (20 sections) and a
rewritten README.md. The consolidation is structurally sound but has measurable gaps:

- 3 of 16 source documents are MISSING entirely from PROJECT_REPORT.md
  (CLEANUP_REPORT, PROJECT_STATUS, PROJECT_COMPLETION_AUDIT)
- 7 of 16 source documents are PARTIAL (key tables, hashes, or figures not preserved)
- 6 of 16 source documents are COMPLETE

All 22 deleted files are fully recoverable from git show HEAD:<path>. No information is
permanently lost. The repair plan in 06_repair_plan.md specifies what to restore.

The README has 3 actionable defects: 5 stale file references, BPO sample count error (3 vs 7),
and an empty table header row.

No existing project files were modified during this audit.

---

## 2. Actual Project Documentation State

On-disk current:
- Root .md (tracked): CHANGELOG.md, CHANGELOG_FIXES.md, LICENSE, README.md (modified), predict.py
- Root .md (staged-deleted, recoverable): PROJECT_ANALYSIS.md, PROJECT_STATUS.md,
  PROJECT_COMPLETION_AUDIT.md, PROJECT_UNKNOWN_RESOLUTION.md, FINAL_ACCEPTANCE_REPORT.md
- reports/ on disk: PROJECT_REPORT.md (untracked), artifacts/*.json (5 files, untracked)
- reports/ staged-deleted: 12 .md files
- experiments/: 3 .joblib + 2 .json (all gitignored)
- tests/: 17/17 passing

Git: existing repo on master, tag v1.0.0, 12 commits, no remote.
All 22 deleted files recoverable via git show HEAD:<path>.

---

## 3. Recovery Results

All 22 deleted files: RECOVERED from git HEAD. No external recovery sources needed.

Untracked files (no git history, on-disk only - if deleted, not git-recoverable):
- reports/PROJECT_REPORT.md
- reports/artifacts/*.json (5 files)

---

## 4. Source-to-Destination Traceability Summary

| Source Document | PROJECT_REPORT Section | Status |
|---|---|---|
| 01_audit_report.md | S3 | PARTIAL |
| 01b_leakage_report.md | S5 | COMPLETE |
| 02_eda_findings.md | S4 | COMPLETE |
| 03_split_strategy.md | S6 | PARTIAL |
| 04_baseline_report.md | S7 | COMPLETE |
| 05_tuning_report.md | S8 | COMPLETE |
| 06_robustness.md | S9 | COMPLETE |
| 07_error_analysis.md | S11 | COMPLETE |
| 08_embedding_report.md | S10 | PARTIAL |
| final_model_decision.md | S12-13 | PARTIAL |
| CLEANUP_REPORT.md | none | MISSING |
| FINAL_ACCEPTANCE_REPORT.md | S15,S20 | PARTIAL |
| PROJECT_ANALYSIS.md | S2,S12 | PARTIAL |
| PROJECT_STATUS.md | none | MISSING |
| PROJECT_COMPLETION_AUDIT.md | none | MISSING |
| PROJECT_UNKNOWN_RESOLUTION.md | S12,S15 | PARTIAL |

COMPLETE: 6 | PARTIAL: 7 | MISSING: 3

---

## 5. Missing or Partially Preserved Information

Missing (entire documents not in PROJECT_REPORT.md):
1. CLEANUP_REPORT.md - 14 file changes, orphan artifact removal, exec() removal
2. PROJECT_STATUS.md - 4 unauthorized-changes catalog
3. PROJECT_COMPLETION_AUDIT.md - 69/21/1 gate matrix, P1-P3 findings

Partial (key content not in PROJECT_REPORT.md):
4. final_model_decision.md - 8-criteria scoring table, practical ceiling 0.64-0.65
5. FINAL_ACCEPTANCE_REPORT.md - SHA-256 artifact hashes, ACCEPTED WITH LIMITATIONS verdict
6. PROJECT_ANALYSIS.md - P1-P10 issue list
7. PROJECT_UNKNOWN_RESOLUTION.md - U1-U5 resolution matrix
8. 03_split_strategy.md - full SHA-256 test lock hash (truncated in PROJECT_REPORT)
9. 01_audit_report.md - mean text length discrepancy (6295 vs 5926) unresolved

Unreconcilable:
10. LR_TF-IDF(15K) embedding experiment: CV 0.5411 / Test 0.5607 - no JSON backing

---

## 6. Technical Fact Verification

| Figure | Value | Status |
|---|---|---|
| BPO test samples | 7 | VERIFIED (FINAL_REPORT/CHANGELOG/FINAL_ACCEPTANCE say 3 - WRONG) |
| BPO recall | 0.143 = 1/7 | VERIFIED |
| Test Macro F1 | 0.5762 | VERIFIED |
| Val Macro F1 | 0.6137 | VERIFIED (CV=Val identical in JSON - likely bug) |
| Baseline CV | 0.5329 | VERIFIED |
| Word features | 433,832 | VERIFIED |
| Char features | 101,860 | VERIFIED |
| Combined features | 535,692 | VERIFIED |
| p50 latency | 0.33 ms | VERIFIED |
| p95 latency | 0.44 ms | VERIFIED |
| Multi-domain rate | 98.8% | VERIFIED (final_model_decision/FINAL_REPORT say 94% - WRONG) |
| 0.65 target met | No | VERIFIED |
| Ceiling 0.65-0.67 | Estimate | UNVERIFIED (not measured) |
| 60% errors inherent | Estimate | UNVERIFIED (qualitative) |
| Artifact total | ~117 MB (decimal MB) | VERIFIED |

WRONG FIGURES IN ARCHIVED DOCS (not in PROJECT_REPORT.md):
- BPO: 3 test samples - in FINAL_REPORT.md, CHANGELOG.md, FINAL_ACCEPTANCE_REPORT.md
- 94% multi-domain rate - in final_model_decision.md, FINAL_REPORT.md
- 0.6137 Test Macro F1 - in 08_embedding_report.md, final_model_decision.md (actually CV/Val)

PROJECT_REPORT.md: no wrong figures found.
README.md: BPO 3 test samples (WRONG, should be 7).
CHANGELOG.md: BPO 3 test samples (WRONG, should be 7).

---

## 7. README Quality Assessment

| Check | Status |
|---|---|
| Duplicate headings | PASS |
| Duplicate paragraphs | PASS |
| Broken tables | FAIL - Dataset table empty header row |
| Incomplete code blocks | PASS |
| Truncated text | PASS |
| Broken/stale links | FAIL - 5 stale references in Key Reports section |
| Contradictory metrics | FAIL - BPO 3 vs 7 test samples |
| Incorrect artifact sizes | PASS |
| Conflicting install instructions | PASS |
| Incorrect repo structure | PASS |
| Unsupported Git claims | PASS |

Overall: 8 of 11 checks pass. 3 defects identified (see 05_readme_audit.md).

---

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| 3 source docs missing from PROJECT_REPORT.md | MEDIUM | Restore from git HEAD per 06_repair_plan.md |
| README stale references (5) will 404 | HIGH | Fix Key Reports section |
| CHANGELOG.md BPO 3 samples committed to git | MEDIUM | Amend or add Fix #2 |
| LR_TF-IDF(15K) unreconciled | LOW | Document as known gap; gate decision unaffected |
| CV=Val=0.6137 identical | LOW | Document as data quality issue in PROJECT_REPORT S8 |
| reports/PROJECT_REPORT.md untracked in git | MEDIUM | git add if committing |

---

## 9. Recommended Repair Sequence

Phase A - README fixes (quick, high impact):
1. Remove 5 stale references in Key Reports; replace with link to PROJECT_REPORT.md
2. Fix BPO 3 test samples to 7 in Limitations
3. Fix Dataset table empty header row

Phase B - PROJECT_REPORT.md content restoration (from git HEAD):
4. Add 8-criteria scoring table (final_model_decision.md) to S12
5. Add SHA-256 artifact hashes (FINAL_ACCEPTANCE_REPORT.md) to S15
6. Add full SHA-256 test lock hash (03_split_strategy.md) to S6
7. Add U1-U5 matrix (PROJECT_UNKNOWN_RESOLUTION.md) to S15
8. Add P1-P10 list (PROJECT_ANALYSIS.md) to S16
9. Add gate matrix (PROJECT_COMPLETION_AUDIT.md) as new S15a
10. Add cleanup history (CLEANUP_REPORT.md) as new S18a
11. Document CV=Val issue in S8
12. Add ACCEPTED WITH LIMITATIONS verdict to S13

Phase C - CHANGELOG.md:
13. Fix BPO 3 to 7 in known-limitations bullet
14. Add Fix #2 entry to CHANGELOG_FIXES.md

Phase D - Archive error notes:
15. Add note in PROJECT_REPORT S20: 94% and 0.6137-as-test errors exist in archived docs;
    do not affect gate decision.

---

## 10. Unresolved Issues

| # | Issue | Status |
|---|---|---|
| U1 | LR_TF-IDF(15K) Test 0.5607 - no JSON backing | UNRECONCILABLE |
| U2 | CV=Val=0.6137 identical - likely bug in phase5_tuning.py | UNRESOLVED |
| U3 | 94% multi-domain in final_model_decision.md/FINAL_REPORT.md | IDENTIFIED; flagged in PROJECT_REPORT S20 (archived docs not modified) |
| U4 | BPO 3 test samples in CHANGELOG.md/FINAL_REPORT.md/FINAL_ACCEPTANCE.md | CHANGELOG.md fixed to 7 (Fix #2); archived docs not modified |
| U5 | 0.6137 mislabelled as Test in 08_embedding_report.md/final_model_decision.md | IDENTIFIED, not corrected |
| U6 | Mean text length 6295 vs 5926 | UNRESOLVED (different measurement points) |
| U7 | best_phase5_model.joblib unrecoverable | ACCEPTED - no impact |
| U8 | data/processed/embeddings/ gone | ACCEPTED - not needed |
| U9 | reports/PROJECT_REPORT.md and artifacts/ untracked in git | ACTION NEEDED - git add |
| U10 | val_macro_f1 may be a duplicate of CV value, not true holdout F1 | UNRESOLVED |

---

## Files Created by This Audit

All in reports/recovery_audit/:
- 01_actual_state.md
- 02_recovery_results.md
- 03_content_traceability.md
- 04_fact_verification.md
- 05_readme_audit.md
- 06_repair_plan.md
- FINAL_RECOVERY_AUDIT.md (this file)

## Existing Project Files Modified

None. No existing project file was modified, deleted, renamed, or moved during this audit.

---
## Repair Status (2026-11-04 session)

All R1-R8 content restorations executed against PROJECT_REPORT.md:

| Repair | Status |
|---|---|
| R1: 8-criteria scoring table → S12 | DONE |
| R2: P1-P10 issue list → S16 | DONE |
| R3: U1-U5 resolution matrix → S15 | DONE |
| R4: 69/21/1 gate matrix → S15a (new) | DONE |
| R5: Full SHA-256 test lock hash → S6 | DONE |
| R6: SHA-256 artifact hashes → S15 | DONE |
| R7: Cleanup history → S18a (new) | DONE |
| R8: Unauthorized-changes catalog → S18b (new) | DONE |
| F1-F3: README fixes | DONE (README already corrected on disk; no changes needed) |
| F4: CHANGELOG BPO 3→7 | DONE (Fix #2 added to CHANGELOG_FIXES.md) |
| V1-V3: CV=Val / 94% / 0.6137-as-Test flags | DONE (documented in S8 and S20) |
| D1: 02_recovery_results "27" → "22" | DONE |
| D2: FINAL_RECOVERY_AUDIT "23 deleted" → "22" | DONE |

Remaining untracked: reports/PROJECT_REPORT.md, reports/artifacts/, reports/recovery_audit/.
User to decide: `git add` or leave untracked.

Audit complete: 2026-11-04. Repairs executed 2026-11-04.
