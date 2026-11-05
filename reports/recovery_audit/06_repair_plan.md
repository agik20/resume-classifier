# 06 - Documentation Repair Plan

For reference only. No changes made until explicit approval.

## Must Be Restored (from git HEAD)

R1. 8-criteria scoring table (weighted 7.3/10) from final_model_decision.md -> PROJECT_REPORT S12
R2. P1-P10 issue list from PROJECT_ANALYSIS.md -> PROJECT_REPORT S16
R3. U1-U5 resolution matrix from PROJECT_UNKNOWN_RESOLUTION.md -> PROJECT_REPORT S15
R4. 69/21/1 gate matrix from PROJECT_COMPLETION_AUDIT.md -> PROJECT_REPORT new S15a
R5. Full SHA-256 test lock hash from 03_split_strategy.md -> PROJECT_REPORT S6
R6. SHA-256 artifact hashes from FINAL_ACCEPTANCE_REPORT.md -> PROJECT_REPORT S15
R7. Clean-up history from CLEANUP_REPORT.md -> PROJECT_REPORT new S18a
R8. Unauthorized-changes catalog from PROJECT_STATUS.md -> PROJECT_REPORT S18

## Cannot Be Recovered

U1. LR_TF-IDF(15K) experiment (CV 0.5411 / Test 0.5607) - no JSON backing; UNRECONCILABLE
U2. best_phase5_model.joblib - never in git; not needed (active artifact is best_phase5_clf.joblib)
U3. data/processed/embeddings/mitigated_embeddings.npy - gitignored, gone; not needed

## README Fixes

F1. Remove 5 stale references in Key Reports section -> replace with link to PROJECT_REPORT.md
F2. Fix BPO 3 test samples to 7 test samples in Limitations
F3. Fix empty Dataset table header row

## CHANGELOG.md Fix

F4. Fix BPO 3 test samples to 7 test samples in known-limitations bullet

## Unresolved Data Quality Issues (document, do not fix)

V1. CV=Val=0.6137 identical in phase5_results.json - likely bug in phase5_tuning.py
V2. 94% multi-domain rate in final_model_decision.md and FINAL_REPORT.md (correct: 98.8%)
V3. 0.6137 mislabelled as Test Macro F1 in 08_embedding_report.md and final_model_decision.md

## Recommended Sequence

1. Fix README (F1-F3) - HIGH priority, quick
2. Fix CHANGELOG.md (F4) - MEDIUM priority
3. Restore missing content to PROJECT_REPORT.md (R1-R8) - MEDIUM priority
4. Document unresolved issues (V1-V3) in PROJECT_REPORT.md Section 20
5. git add reports/PROJECT_REPORT.md and reports/artifacts/ if committing

## What Not To Do

- Do not delete PROJECT_REPORT.md
- Do not delete reports/artifacts/*.json
- Do not delete CHANGELOG.md or CHANGELOG_FIXES.md
- Do not modify model artifacts
- Do not initialize a new git repo
