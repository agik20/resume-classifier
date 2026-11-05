# 07 — Audit Validation (Controlled Final Correction)

Date: 2026-11-04
Scope: authorized, narrowly-scoped final correction & validation only.
Files touched: `03_content_traceability.md` (D1), `PROJECT_REPORT.md` (D3), this file.
Prohibited actions (all avoided): no source-code / artifact / dataset / metric changes;
no `git add` / `commit` / reset / restore / clean / stash; no file moves/renames; no unrelated cleanup.

---

## A. Scope

Authorized by the "CONTROLLED FINAL CORRECTION & VALIDATION" task:
1. Verify actual git working-tree and index state (read-only).
2. Independently recompute the four documented SHA-256 digests.
3. Correct D1 — reconcile the stale body sections in `03_content_traceability.md` with
   the corrected summary table and post-repair state.
4. Correct D3 — fix the backwards CV/val causal wording in `PROJECT_REPORT.md` S8
   against `scripts/phase5_tuning.py`.
5. Consistency checks on the two affected documents.
6. Create this `07_audit_validation.md`.
7. Final summary.

Out of scope and NOT performed: any fix of secondary findings (practical 0.64–0.65 ceiling,
ACCEPTED-WITH-LIMITATIONS verdict, best_phase5_model.joblib unrecoverability, README empty-header
row) — these are dispositioned below, not auto-fixed.

## B. Initial Git State (recorded before any edit)

- Repo root: `C:/Users/ardut/projects/resume-classifier` (single git repo, master, tag v1.0.0).
- Unstaged modified: `CHANGELOG.md`, `CHANGELOG_FIXES.md`, `README.md`.
- Staged deletions (`git diff --cached --diff-filter=D`): 17 `.md` docs.
- Worktree deletions (`git diff --diff-filter=D`): 5 `.json` result files.
- Combined distinct deleted set: **22 files**, each verified present in `HEAD` via
  `git cat-file -e HEAD:<path>` (all `OK`). No restore performed.
- Untracked: `reports/PROJECT_REPORT.md`, `reports/artifacts/`, `reports/recovery_audit/`.
- Nothing staged or committed during this session.

## C. SHA-256 Hash Verification (independent recomputation)

Computed with Python `hashlib.sha256` on the live files; compared to the values in
`PROJECT_REPORT.md` (S6 / S15). All four match exactly; all are 64-hex, valid.

| Artifact | Path | Bytes | Recomputed SHA-256 | Documented | Match |
|---|---|---|---|---|---|
| test-split lock | `data/splits/test.csv` | 17,137,998 | `d852c272…e1ecad` | same (S6) | YES |
| word vectorizer | `experiments/best_phase5_word_vec.joblib` | 12,872,968 | `8cb2f503…b0a8c7` | same (S15) | YES |
| char vectorizer | `experiments/best_phase5_char_vec.joblib` | 1,944,189 | `28a4aff2…da096` | same (S15) | YES |
| classifier | `experiments/best_phase5_clf.joblib` | 102,854,211 | `0b58981f…f963133` | same (S15) | YES |

The char vectorizer digest specifically scrutinized for a "malformed / non-hex ending"
defect: full value `28a4aff295a9e7b5770d163e25d255249be592201c8ab988a6b5f960232da096`
is 64 valid hex chars; the trailing `…a096` is well-formed. **No defect reproduced;
no hash correction was required or made.**

## D. D1 Correction (03_content_traceability.md)

Eight stale body sections that contradicted the corrected SUMMARY table were reconciled:

| Source doc | Before | After |
|---|---|---|
| `03_split_strategy.md` | PARTIAL — "SHA-256 truncated" | COMPLETE — full hash now in S6, re-verified |
| `final_model_decision.md` | PARTIAL — 8-criteria "MISSING" | COMPLETE — table in S12; known-error figures dispositioned |
| `CLEANUP_REPORT.md` | MISSING | COMPLETE — S18a |
| `FINAL_ACCEPTANCE_REPORT.md` | PARTIAL — "SHA-256 MISSING" | COMPLETE — SHA-256 in S15, re-verified |
| `PROJECT_ANALYSIS.md` | PARTIAL — "P1-P10 MISSING" | COMPLETE — P1-P10 in S16 |
| `PROJECT_STATUS.md` | MISSING | COMPLETE — S18b |
| `PROJECT_COMPLETION_AUDIT.md` | MISSING | COMPLETE — gate matrix in S15a |
| `PROJECT_UNKNOWN_RESOLUTION.md` | PARTIAL — "U1-U5 MISSING" | COMPLETE — U1-U5 in S15 |

Genuinely PARTIAL documents left PARTIAL (not forcibly escalated):
- `01_audit_report.md` S3 — mean-text-length 6295 vs 5926 (different measurement points).
- `08_embedding_report.md` S10 — LR_TF-IDF(15K) Test 0.5607 has no JSON backing (UNRECONCILABLE).

Summary table now internally consistent: 16 source docs, each exactly once;
**COMPLETE 14 / PARTIAL 2 / MISSING 0.** (Recalculated, not copied.)

## E. D3 Correction (PROJECT_REPORT.md S8)

Ground truth (`scripts/phase5_tuning.py:233` → `:250`,`:251`): `best_combined_score` is a
single val-set `f1_score(y_val, y_pred, average='macro')` written to `cv_macro_f1_mean`,
with `cv_macro_f1_std` hardcoded to `0.0`. The original S8 note said the *val* field was
populated with the *CV* value — the **reverse** of the actual data flow. Corrected S8 to
state that `cv_macro_f1_mean` was populated from the validation-set score, std was
hardcoded 0.0, and the two reported values are therefore not independent measurements.

## F. Secondary Findings (dispositioned, not auto-fixed — outside authorized scope)

| # | Finding | Disposition |
|---|---|---|
| S-a | Practical ceiling 0.64–0.65 (theoretical 0.65–0.67) not restored to S13 | Documented in 03 traceability (final_model_decision section) as UNRESOLVED |
| S-b | "ACCEPTED WITH LIMITATIONS" verdict not carried into S13/S15 | Dispositioned in FINAL_RECOVERY_AUDIT register |
| S-c | `experiments/best_phase5_model.joblib` unrecoverable (removed as redundant in v1.0.0) | Known; no impact on gate decision (U7) |
| S-d | README dataset table empty-header row (`\| \| \|`) | Low; renders as 2-col key/value table; not in authorized scope |

## G. Documentation Consistency

- `03_content_traceability.md`: all 8 corrected body sections now agree with the SUMMARY
  table and the "RESTORED CONTENT" checklist; PARTIAL entries (01, 08) align with their
  status lines. No section contradicts the table.
- `PROJECT_REPORT.md` S8: D3 wording now matches `phase5_tuning.py`; the 0.6137 figure is
  consistently described as a val-set F1 recorded into the CV field.
- No source files, artifacts, datasets, or metrics modified.

## H. Git State After Correction

Post-edit `git status --short` (re-checked): same 3 unstaged-modified + 17 staged-deleted +
5 worktree-deleted as initial state, plus `PROJECT_REPORT.md` and the two recovery_audit docs
now modified/untracked. **Nothing newly staged; nothing committed; no destructive command run.**
No Python source, artifact, or data file touched.

## I. Final Defect Register (carried forward)

| ID | Severity | Item | Status |
|---|---|---|---|
| D1 | HIGH | Stale traceability body sections | CORRECTED (this session) |
| D3 | LOW/MED | Backwards CV/val causality in S8 | CORRECTED (this session) |
| D2 | LOW | (prior) exec-summary counts | already reconciled to 16-document wording |
| S-a..S-d | LOW | secondary findings | dispositioned, not auto-fixed |
| Hash | — | char_vec "malformed digest" suspicion | NOT reproduced; digest valid & matches |

## J. Final Verdict

**ACCEPTED — controlled correction complete.** All four SHA-256 digests independently
re-verified (char vectorizer confirmed well-formed, no correction needed); D1 and D3
corrections applied within authorized scope; no prohibited file or git action performed.
Remaining items are dispositioned secondary findings, intentionally left unfixed.

---

# Final Documentation Consistency Audit

Date: 2026-11-04 (second pass)

## 1. Initial Git State

`git status --short` at session start (pre-edit):
- 3 unstaged-modified: `CHANGELOG.md`, `CHANGELOG_FIXES.md`, `README.md`
- 17 staged-deleted `.md` docs (index `D`)
- 5 worktree-deleted `.json` files (worktree `D`)
- Untracked: `reports/PROJECT_REPORT.md`, `reports/artifacts/`, `reports/recovery_audit/`
- No new staging or commits in this session.

## 2. Files Modified in This Pass

| File | Changes |
|---|---|
| `reports/PROJECT_REPORT.md` | S8 table header (CV→val), S13 (improvement row re-labelled, CV/val distinction note), S1 executive summary (metric terminology, ceiling wording), S4 (keyword-overlap vs. label-ambiguity distinction), S16 limitation #1, S17 "why this model" + "why no further experiments", S19 conclusion, S20 CV=Val row (verified data-flow explanation) |
| `reports/recovery_audit/03_content_traceability.md` | Added status definitions (COMPLETE, COMPLETE WITH UNRESOLVED ITEMS, PARTIAL, MISSING, UNVERIFIABLE); re-graded 5 entries to COMPLETE WITH UNRESOLVED ITEMS; recalculated summary counts to 8/5/2/0/0 |
| `reports/recovery_audit/07_audit_validation.md` | This section added |

No source code, model artifacts, dataset files, README, CHANGELOG, or requirements files were modified.

## 3. CV/Validation Correction Details

**Ground truth** (`scripts/phase5_tuning.py:231-253`):
```
y_pred = cfg['clf'].predict(X_combined_val)   # val-set predictions
score  = f1_score(y_val, y_pred, average='macro')  # single val F1
...
'cv_macro_f1_mean': best_combined_score,   # val F1 written into CV field
'cv_macro_f1_std':  0.0,                   # hardcoded
'val_macro_f1':     float(best_combined_score),  # same value
```
There is no independent 5-fold CV loop for the combined experiment. The 0.6137 figure is a
validation-set Macro F1 recorded into the `cv_macro_f1_mean` field; `cv_macro_f1_std`
was hardcoded to 0.0. No true CV estimate exists for the combined model.

**Corrections made:**
- S8 table header: "CV Macro F1" → "Best val Macro F1".
- S13 improvement row: "+0.0808 CV / +15.1%" relabelled as "Val-minus-baseline-CV" with
  an explicit cross-protocol caveat; 0.6137 identified as a val-set figure throughout.
- S1: removed "+0.0808 CV F1 (+15.1%)" from the executive summary; 0.65–0.67 reframed
  as an analytical hypothesis, not a measured ceiling.
- S20: "Likely a code-path bug" replaced with the verified data-flow explanation.

## 4. Dataset Ceiling Wording Correction

**Problem:** the report described the ~0.65–0.67 estimate as a "dataset-inherent ceiling,"
implying it was empirically proven. The 98.8% multi-domain keyword rate establishes keyword
overlap, not necessarily genuine multi-label ambiguity or label noise.

**Corrections made (S1, S4, S13, S16, S17, S19):**
- The 98.8% figure is now explicitly identified as a keyword-overlap rate, not a proof
  of label ambiguity.
- The ~0.65–0.67 estimate is retained as an analytical hypothesis only.
- Three distinct concepts are now distinguished: keyword overlap, genuine label ambiguity,
  and label noise. No new measurements were introduced.

## 5. Traceability Status Definitions and Final Counts

A new "Status Definitions" section was added to `03_content_traceability.md`. The key
distinction is: **COMPLETE** requires that no important finding is left unresolved;
**COMPLETE WITH UNRESOLVED ITEMS** means the core content is restored but one or more
secondary findings remain open or intentionally not carried into PROJECT_REPORT.md.

Final summary counts (16 source documents):
- COMPLETE: 8
- COMPLETE WITH UNRESOLVED ITEMS: 5 (final_model_decision, FINAL_ACCEPTANCE_REPORT,
  PROJECT_STATUS, PROJECT_COMPLETION_AUDIT, PROJECT_UNKNOWN_RESOLUTION)
- PARTIAL: 2 (01_audit_report.md, 08_embedding_report.md)
- MISSING: 0
- UNVERIFIABLE: 0

## 6. JSON Migration Verification

The 5 original result JSON files (`reports/04_baseline_results.json`,
`reports/06_robustness_results.json`, `reports/07_error_analysis.json`,
`reports/10_test_results.json`, `reports/final_model_decision.json`) are deleted from the
working tree and recoverable from git HEAD. The consolidated report claims they were
migrated to `reports/artifacts/`. Verification results:

| Source (HEAD) | Destination (`reports/artifacts/`) | Readable | Byte-level | After CRLF-strip | JSON-structurally equal |
|---|---|---|---|---|---|
| `reports/04_baseline_results.json` | `04_baseline_results.json` | YES | DIFFERENT | IDENTICAL | YES |
| `reports/06_robustness_results.json` | `06_robustness_results.json` | YES | DIFFERENT | IDENTICAL | YES |
| `reports/07_error_analysis.json` | `07_error_analysis.json` | YES | DIFFERENT | IDENTICAL | YES |
| `reports/10_test_results.json` | `10_test_results.json` | YES | DIFFERENT | IDENTICAL | YES |
| `reports/final_model_decision.json` | `final_model_decision.json` | YES | DIFFERENT | IDENTICAL | YES |

**Conclusion:** all 5 destination files are JSON-identical to their HEAD sources after
stripping `\r\n` → `\n`. The byte-level difference is CRLF line-ending normalization
(Windows on-disk files vs. LF-only git storage). No structural or value differences.
The migration is confirmed; PROJECT_REPORT's claim that evidence was migrated to
`reports/artifacts/` is accurate. No JSON file was restored, deleted, renamed, moved,
or overwritten in this session.

## 7. Remaining Unresolved Findings

| # | Finding | Status |
|---|---|---|
| R1 | `01_audit_report.md` mean text length 6295 vs. PROJECT_REPORT 5926 (different measurement points) | PARTIAL — documented, not resolved |
| R2 | `08_embedding_report.md` LR_TF-IDF(15K) Test 0.5607 — no JSON backing | PARTIAL — UNRECONCILABLE, documented in S20 |
| R3 | Practical 0.64–0.65 ceiling (vs. theoretical 0.65–0.67) not restored to S13 | COMPLETE WITH UNRESOLVED ITEMS — dispositioned in 03 traceability |
| R4 | "ACCEPTED WITH LIMITATIONS" verdict (FINAL_ACCEPTANCE_REPORT) not carried into S15/S20 | COMPLETE WITH UNRESOLVED ITEMS — dispositioned |
| R5 | NEARLY COMPLETE verdict (PROJECT_STATUS) not restored | COMPLETE WITH UNRESOLVED ITEMS — dispositioned |
| R6 | 8 audit dimensions + critical findings P1–P3 (PROJECT_COMPLETION_AUDIT) not individually restored | COMPLETE WITH UNRESOLVED ITEMS — dispositioned |
| R7 | `experiments/best_phase5_model.joblib` unrecoverable (U7) | COMPLETE WITH UNRESOLVED ITEMS — no gate impact |

## 8. Final Git State

Post-edit `git status --short` (verified): same 3 unstaged-modified + 17 staged-deleted +
5 worktree-deleted as initial state. No new files staged or committed. No destructive git
command run. No source, artifact, or data file modified.

## 9. Explicit Statement

No model artifacts (`.joblib`), dataset files (`.csv`), Python source code, experiment
result files, README, CHANGELOG, requirements files, or Git history were modified in this
session. The only files modified are `reports/PROJECT_REPORT.md`,
`reports/recovery_audit/03_content_traceability.md`, and this file
(`reports/recovery_audit/07_audit_validation.md`).

## Final Verdict

**ACCEPTED WITH LIMITATIONS.**

Rationale:
- All D3 (CV/val) corrections are applied and verified against `phase5_tuning.py`.
- All dataset-ceiling wording corrections are applied; the 0.65–0.67 estimate is
  consistently framed as a hypothesis, not a proven upper bound.
- D1 traceability status definitions are now precise; the 5 entries with unresolved items
  are correctly marked COMPLETE WITH UNRESOLVED ITEMS; counts are 8/5/2/0/0.
- JSON migration is confirmed (5/5 JSON-identical after CRLF normalization).
- The remaining 7 findings (R1–R7) are dispositioned and documented; none undermines the
  integrity of PROJECT_REPORT.md as an authoritative reference.
- No prohibited file or git action was performed.

The limitations are: R1 (mean-text-length discrepancy unresolved) and R2 (LR_TF-IDF(15K)
value unreconcilable) are PARTIAL, and R3–R7 are secondary items intentionally not
restored. None affects the primary metrics, gate decision, or model artifacts.
