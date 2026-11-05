# 04 - Technical Fact Verification

Each claim checked against primary evidence (JSON artifacts, test.csv counts, on-disk file sizes, model metadata).
Verification status: VERIFIED / DISPUTED / UNVERIFIED / WRONG.

---

## 1. BPO test sample count: 3 vs 7

| Source | Value | Status |
|---|---|---|
| 10_test_results.json BPO recall = 0.142857... | 1/7 = 0.14286 | VERIFIED: 7 samples |
| test.csv direct pandas count | 7 BPO rows | VERIFIED: 7 samples |
| final_model_decision.md | BPO 0.14 recall, 7 test samples | VERIFIED: 7 samples |
| PROJECT_REPORT.md S11 | BPO recall 0.143 (1 of 7) | VERIFIED: 7 samples |
| PROJECT_REPORT.md S13 | Min test recall 0.143 (BPO, 7 samples) | VERIFIED: 7 samples |
| FINAL_REPORT.md | BPO (3 samples) | WRONG: says 3 |
| CHANGELOG.md | BPO: 3 test samples | WRONG: says 3 |
| FINAL_ACCEPTANCE_REPORT.md | BPO 0.14 recall (3 test samples) | WRONG: says 3 |

Conclusion: BPO has 7 test samples. The "3" in FINAL_REPORT.md, CHANGELOG.md, and
FINAL_ACCEPTANCE_REPORT.md is wrong (likely confused with the 3 BPO val samples).

---

## 2. BPO recall: 0.143 vs 0.14

10_test_results.json gives 0.142857... Both 0.143 and 0.14 are valid roundings. No conflict.

---

## 3. Test Macro F1: 0.5762

10_test_results.json: 0.57623639... VERIFIED. PROJECT_REPORT, FINAL_REPORT, and CHANGELOG
all use 0.5762 - VERIFIED.

08_embedding_report.md and final_model_decision.md label "0.6137" as "Test Macro F1" for
the Phase 5 model. This is WRONG: 0.6137 is the CV/val value; the true test value is 0.5762.

---

## 4. Validation Macro F1: 0.6137

phase5_results.json SVM_Combined: cv_macro_f1_mean = 0.61369853... AND val_macro_f1 =
0.61369853... (identical). 06_robustness_results.json base_macro_f1 = 0.61369853... VERIFIED.

Data quality concern: CV and Val are numerically identical in phase5_results.json.
Either val_macro_f1 was populated with the CV value (likely a code bug in the tuning script)
or both were computed on the same fold. This is documented but not resolved.

---

## 5. Baseline CV: 0.5329

04_baseline_results.json B4_SVM_Mitigated cv_macro_f1_mean = 0.53287283... VERIFIED.
All documents citing 0.5329 are correct (rounded from 0.532873).

---

## 6-8. Feature dimensions: 433,832 / 101,860 / 535,692

PROJECT_UNKNOWN_RESOLUTION.md Section 4 confirmed these values by joblib.load inspection.
FINAL_ACCEPTANCE_REPORT.md and PROJECT_REPORT.md cite the same values. All VERIFIED.

---

## 9. Active model artifact sizes

| Artifact | On-disk bytes | Decimal MB (/1e6) | Documents claim | Status |
|---|---|---|---|---|
| best_phase5_word_vec.joblib | 12,872,968 | 12.87 MB | 12.9 MB (FINAL_REPORT, PROJECT_REPORT) | VERIFIED |
| best_phase5_char_vec.joblib | 1,944,189 | 1.94 MB | 1.9 MB | VERIFIED |
| best_phase5_clf.joblib | 102,854,211 | 102.85 MB | 102.9 MB (FINAL_REPORT, PROJECT_REPORT) | VERIFIED |
| Total | 117,671,368 | 117.67 MB | ~117 MB | VERIFIED |

Note: All size claims in FINAL_REPORT.md and PROJECT_REPORT.md use decimal MB
(1 MB = 1,000,000 bytes). They are correct. The "~13 MB" figure in
PROJECT_ANALYSIS.md is wrong (gross underestimate). No discrepancy in the
FINAL_REPORT/PROJECT_REPORT artifact size claims.

---

## 10. Inference latency p50 and p95

10_test_results.json: p50 = 0.32544 ms, p95 = 0.44096 ms.
All documents citing 0.33 ms p50 and 0.44 ms p95 are VERIFIED (rounded).

---

## 11. Multi-domain keyword rate: 98.8%

| Source | Value | Status |
|---|---|---|
| 01_audit_report.md | 98.8% (2453/2484) | VERIFIED |
| 02_eda_findings.md | 98.8% (2453/2484) | VERIFIED |
| PROJECT_REPORT.md S4 | 98.8% | VERIFIED |
| CHANGELOG.md | 98.8% | VERIFIED |
| FINAL_ACCEPTANCE_REPORT.md | 98.8% | VERIFIED |
| final_model_decision.md | 94% | WRONG |
| FINAL_REPORT.md | 94% | WRONG |

Conclusion: 98.8% is correct. The "94%" in final_model_decision.md and FINAL_REPORT.md
is wrong and was NOT propagated to PROJECT_REPORT.md.

---

## 12. Error attribution: ~60% cross-domain ambiguity

Cited as an estimate in final_model_decision.md and PROJECT_REPORT.md S13.
No script computes this value; it is a qualitative inference from the 98.8% multi-domain
rate and the error breakdown. UNVERIFIED as a precise figure but consistent across documents.

---

## 13. Whether the 0.65 F1 target was achieved

Test Macro F1 = 0.5762 (10_test_results.json). 0.5762 < 0.65. NOT ACHIEVED.
All documents correctly state this. VERIFIED.

---

## 14. Dataset performance ceiling (0.65-0.67)

Theoretical ceiling in final_model_decision.md: 0.65-0.67. Practical: 0.64-0.65.
This is an ESTIMATE derived from the multi-domain rate and error analysis,
not a measured value. No experiment was run at that F1 level to confirm the ceiling.
UNVERIFIED as a hard bound; reasonable as a soft estimate. PROJECT_REPORT.md
correctly labels it as an "estimate" (Section 13: "The ~0.65-0.67 ceiling estimate").

---

## DISPUTED / WRONG FIGURES SUMMARY

| Figure | Correct Value | Wrong Source(s) |
|---|---|---|
| BPO test samples | 7 | FINAL_REPORT.md (3), CHANGELOG.md (3), FINAL_ACCEPTANCE_REPORT.md (3) |
| Multi-domain rate | 98.8% | final_model_decision.md (94%), FINAL_REPORT.md (94%) |
| 0.6137 labelled as "Test" | 0.6137 is CV/Val; test = 0.5762 | 08_embedding_report.md, final_model_decision.md |
| LR_TF-IDF(15K) Test 0.5607 | UNRECONCILABLE - no JSON entry | 08_embedding_report.md |
| Total artifact size ~117 MB | 117.67 MB decimal - VERIFIED | PROJECT_ANALYSIS.md (~13 MB is wrong) |

## UNVERIFIED FIGURES

| Figure | Reason |
|---|---|
| ~60% errors dataset-inherent | Qualitative estimate; no script computes it |
| Ceiling 0.65-0.67 | Estimate, not measured |
| CV=Val=0.6137 identical | Likely a code bug in phase5_tuning.py; unresolved |