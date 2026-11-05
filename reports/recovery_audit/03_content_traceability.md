# 03 - Content Traceability Matrix

For each original document, the main findings, metrics, and conclusions are mapped to their destination in PROJECT_REPORT.md.

## Status Definitions

- **COMPLETE** — every substantive finding, metric, and conclusion from the source document has been faithfully restored into PROJECT_REPORT.md (or documented as a known error with the correct value supplied). No important finding is left unresolved.
- **COMPLETE WITH UNRESOLVED ITEMS** — the core content (key tables, verified metrics, primary decisions) has been restored, but one or more secondary findings from the source document remain unresolved, not independently verified, or intentionally not carried into PROJECT_REPORT.md. The document is usable as an authoritative reference, but readers should consult the source for the open items.
- **PARTIAL** — a core finding or metric that should have been restored was not; the omission would prevent a reader from understanding the source document's primary result from PROJECT_REPORT.md alone.
- **MISSING** — the source document was not represented in PROJECT_REPORT.md at all.
- **UNVERIFIABLE** — the source document or its relevant section was not accessible; status cannot be assessed.

A finding mentioned only in a defect register or "known-error" note is **not** considered restored for the purposes of this status; it is marked UNRESOLVED ITEMS (if the core content is present) or PARTIAL (if the unresolved item is a core finding).

---

## reports/01_audit_report.md -> PROJECT_REPORT.md Section 3

Source key facts: 2484 rows, 4 cols, 24 categories; mean text length 6295 chars; min 21, max 38842;
2 exact-dup groups (4 rows); 6 near-dup groups (13 rows); Jaccard 0.70; 19/24 >80 percent leakage, 10 at 100 percent;
multi-domain 98.8 percent (2453/2484).

PROJECT_REPORT Section 3: 2484 rows x 4 cols MATCH; mean text length ~5926 (DIFFERS - see 04);
min 21, max 38842 MATCH; duplicate groups MATCH; Jaccard MATCH; leakage numbers in S5 MATCH;
multi-domain 98.8 percent in S4 MATCH.

STATUS: PARTIAL - mean text length differs (5926 in PROJECT_REPORT vs 6295 in 01_audit_report.md).
EDA report gives 5926. The two values trace to different measurement points.

---

## reports/01b_leakage_report.md -> PROJECT_REPORT.md Section 5

All values MATCH: Raw 0.6506 (std 0.0223); Mitigated 0.5982 (std 0.0161); Delta 0.0524;
19/24 >80 percent, 10 at 100 percent; strip first 200 chars.

STATUS: COMPLETE

---

## reports/02_eda_findings.md -> PROJECT_REPORT.md Section 4

All values MATCH: Imbalance 5.45x; mean 5926 chars; median 5542; multi-domain 98.8 percent,
31 single-domain; quick-LR 66.2 percent; top words state/city/company.

STATUS: COMPLETE

---

## reports/03_split_strategy.md -> PROJECT_REPORT.md Section 6

All values MATCH: 55/15/30; train 1365, val 373, test 746; max prop diff 0.13 percent; 0 crossings.
Full SHA-256 test lock now recorded in PROJECT_REPORT S6: d852c272da2333993e2b1255bb4b32d5c7dc6499e9b03a97e1bf8c0831e1ecad
(previously truncated; restored in 2026-11-04 repair). Independently re-verified against data/splits/test.csv on 2026-11-04.

STATUS: COMPLETE.

---

## reports/04_baseline_report.md -> PROJECT_REPORT.md Section 7

All 4 config rows MATCH exactly:
- LR Raw: CV 0.5223+/-0.0138, Val 0.5625
- LR Mit: CV 0.4868+/-0.0162, Val 0.5440
- SVM Raw: CV 0.5811+/-0.0284, Val 0.6167
- SVM Mit: CV 0.5329+/-0.0148, Val 0.5886
Raw-to-mit deltas: 0.0355 (LR) / 0.0482 (SVM) MATCH.

STATUS: COMPLETE

---

## reports/05_tuning_report.md -> PROJECT_REPORT.md Section 8

21 experiments MATCH. Best SVM_Combined C=10 CV=0.6137 MATCH. Improvement +0.0808 MATCH.
Caveat: original report shows CV and Val both as 0.6137 (identical values - see 04 item 5).

STATUS: COMPLETE with documented caveat

---

## reports/06_robustness.md -> PROJECT_REPORT.md Section 9

All 6 perturbation rows MATCH exactly. Base 0.6137 MATCH. All-pass threshold 0.05 MATCH.

STATUS: COMPLETE

---

## reports/07_error_analysis.md -> PROJECT_REPORT.md Section 11

126/373 errors, 33.8 percent MATCH. Top confusion pairs MATCH. Worst classes MATCH.
BPO test recall 0.143 (1 of 7) in PROJECT_REPORT S11 - 7 is correct per test.csv.

STATUS: COMPLETE

---

## reports/08_embedding_report.md -> PROJECT_REPORT.md Section 10

| Experiment | In 08 report | In PROJECT_REPORT | Status |
|---|---|---|---|
| LR_Embeddings CV 0.4671 / Test 0.4550 | yes | yes | MATCH |
| LR_Combined CV 0.4699 / Test 0.4549 | yes | yes | MATCH |
| SVM_Embeddings CV 0.3875 / Test 0.3692 | yes | yes | MATCH |
| LR_TF-IDF(15K) CV 0.5411 / Test 0.5607 | yes | NO (flagged in S20) | UNRECONCILABLE |
| Phase 5 Best Test 0.6137 | in 08 report | not in table | WRONG LABEL (0.6137 is CV; true test = 0.5762) |

STATUS: PARTIAL

---

## reports/final_model_decision.md -> PROJECT_REPORT.md Sections 12-13

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| 8-criteria scoring table (weighted 7.3/10) | yes | yes (S12) | MATCH (restored 2026-11-04) |
| Ceiling 0.65-0.67 theoretical | yes | yes (S13) | MATCH |
| Ceiling 0.64-0.65 practical | yes | flagged as secondary finding, not restored | UNRESOLVED |
| 94 percent multi-domain rate | yes | 98.8 percent used | KNOWN-ERROR (94% is the stale archived figure; 98.8% is correct; documented S20) |
| BPO 0.14 recall, 7 test samples | yes | MATCH | MATCH |
| ~13MB disk size | yes | ~117 MB used | KNOWN-ERROR (original ~13MB figure was wrong; 117 MB is correct) |
| 60 percent errors dataset-inherent | yes | MATCH | MATCH |

STATUS: COMPLETE WITH UNRESOLVED ITEMS (practical 0.64-0.65 ceiling figure not restored; verdict dispositioned in defect register).

---

## reports/CLEANUP_REPORT.md -> PROJECT_REPORT.md S18a

Dedicated section S18a now covers:
- 14 files modified during finalization
- 2 orphan joblib files removed
- 11 empty directories removed
- exec() removal from phase10_inference.py
- 17/17 test results at cleanup time

STATUS: COMPLETE (restored to S18a in 2026-11-04 repair).

---

## FINAL_ACCEPTANCE_REPORT.md -> PROJECT_REPORT.md Sections 15, 20

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| SHA-256 of 3 active artifacts | yes | yes (S15) | MATCH (restored 2026-11-04; digests re-verified 2026-11-04) |
| Python 3.14 | yes | yes (S18) | MATCH |
| Env drift (scikit-learn 1.7.2 vs 1.9.0) | yes | yes (S18) | MATCH |
| ACCEPTED WITH LIMITATIONS verdict | yes | documented as secondary finding, not restored | UNRESOLVED |

STATUS: COMPLETE WITH UNRESOLVED ITEMS (SHA-256 restored; ACCEPTED-WITH-LIMITATIONS verdict not carried into S15/S20).

---

## PROJECT_ANALYSIS.md -> PROJECT_REPORT.md Sections 2, 12

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| P1-P10 issue list | yes | yes (S16) | MATCH (restored 2026-11-04) |
| Architecture data flow | yes | yes (S12) | MATCH |
| ~13 MB model size | yes | ~117 MB used | KNOWN-ERROR (original ~13 MB was wrong; 117 MB is correct) |

STATUS: COMPLETE (P1-P10 restored; size discrepancy dispositioned as a known error, not auto-fixed).

---

## PROJECT_STATUS.md -> PROJECT_REPORT.md S18b

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| 4 unauthorized changes catalogued | yes | yes (S18b) | MATCH (restored 2026-11-04) |
| NEARLY COMPLETE verdict | yes | documented as secondary finding, not restored | UNRESOLVED |

STATUS: COMPLETE WITH UNRESOLVED ITEMS (unauthorized-changes catalog restored to S18b; NEARLY COMPLETE verdict not restored to S15a or elsewhere).

---

## PROJECT_COMPLETION_AUDIT.md -> PROJECT_REPORT.md S15a

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| 69/21/1 gate matrix | yes | yes (S15a) | MATCH (restored 2026-11-04; verified against git HEAD) |
| 8 audit dimensions | yes | documented as secondary finding, not restored | UNRESOLVED |
| Critical findings P1-P3 | yes | documented as secondary finding, not restored | UNRESOLVED |

STATUS: COMPLETE WITH UNRESOLVED ITEMS (gate matrix restored to S15a; 8 audit dimensions and critical findings P1-P3 not individually restored).

---

## PROJECT_UNKNOWN_RESOLUTION.md -> PROJECT_REPORT.md Sections 12, 15

| Item | In original | In PROJECT_REPORT | Status |
|---|---|---|---|
| U1-U5 resolution matrix | yes | yes (S15) | MATCH (restored 2026-11-04) |
| 535692 feature dimensions | yes | yes (S12) | MATCH |
| best_phase5_model.joblib unrecoverable | yes | documented as secondary finding, not restored | UNRESOLVED (U7) |

STATUS: COMPLETE WITH UNRESOLVED ITEMS (U1-U5 matrix restored to S15; best_phase5_model.joblib unrecoverability (U7) not restored to S20).

---

## SUMMARY

| Source Document | Destination | Status |
|---|---|---|
| 01_audit_report.md | S3 | PARTIAL |
| 01b_leakage_report.md | S5 | COMPLETE |
| 02_eda_findings.md | S4 | COMPLETE |
| 03_split_strategy.md | S6 | COMPLETE |
| 04_baseline_report.md | S7 | COMPLETE |
| 05_tuning_report.md | S8 | COMPLETE |
| 06_robustness.md | S9 | COMPLETE |
| 07_error_analysis.md | S11 | COMPLETE |
| 08_embedding_report.md | S10 | PARTIAL |
| final_model_decision.md | S12-13 | COMPLETE WITH UNRESOLVED ITEMS |
| CLEANUP_REPORT.md | S18a | COMPLETE |
| FINAL_ACCEPTANCE_REPORT.md | S15,S20 | COMPLETE WITH UNRESOLVED ITEMS |
| PROJECT_ANALYSIS.md | S2,S12,S16 | COMPLETE |
| PROJECT_STATUS.md | S18b | COMPLETE WITH UNRESOLVED ITEMS |
| PROJECT_COMPLETION_AUDIT.md | S15a | COMPLETE WITH UNRESOLVED ITEMS |
| PROJECT_UNKNOWN_RESOLUTION.md | S12,S15 | COMPLETE WITH UNRESOLVED ITEMS |

**Counts (16 source documents, each listed once):**
- COMPLETE: 9
- COMPLETE WITH UNRESOLVED ITEMS: 5
- PARTIAL: 2 (01_audit_report.md, 08_embedding_report.md)
- MISSING: 0
- UNVERIFIABLE: 0

## RESTORED CONTENT (2026-11-04 repair session)

1. 8-criteria scoring table (weighted 7.3/10) from final_model_decision.md → S12 ✓
2. P1-P10 issue list from PROJECT_ANALYSIS.md → S16 ✓
3. U1-U5 resolution matrix from PROJECT_UNKNOWN_RESOLUTION.md → S15 ✓
4. 69/21/1 gate matrix from PROJECT_COMPLETION_AUDIT.md → S15a ✓
5. Full SHA-256 test lock hash from 03_split_strategy.md → S6 ✓
6. SHA-256 artifact hashes from FINAL_ACCEPTANCE_REPORT.md → S15 ✓
7. Clean-up history from CLEANUP_REPORT.md → S18a ✓
8. Unauthorized-changes catalog from PROJECT_STATUS.md → S18b ✓

## REMAINING GAP (unrecoverable or unreconcilable)

- LR_TF-IDF(15K) experiment: CV 0.5411 / Test 0.5607 — no supporting JSON entry; UNRECONCILABLE (documented in S20)

## ADDITIONAL DOCUMENTATION (2026-11-04 repair session)

- CV=Val=0.6137 data quality note → S8
- Known errors in archived source documents table → S20
- CHANGELOG.md BPO "3 test samples" → "7 test samples" (Fix #2)
