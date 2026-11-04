# Phase 6: Robustness Checks

**Date**: 2026-08-16 | **Base Model**: Combined Word+Char SVM | **Seed**: 42

## Base Performance

Macro F1 (combined text, no perturbation): **0.6137**

## Results

| Perturbation | Macro F1 | Delta | Min Recall | Status |
|---|---|---|---|---|
| R1_Strip_Email_Phone | 0.6137 | +0.0000 | 0.0000 | OK |
| R2_No_Punctuation | 0.6085 | -0.0052 | 0.0000 | OK |
| R3_Random_Typos | 0.6155 | +0.0018 | 0.0000 | OK |
| R4_Truncate_200w | 0.5929 | -0.0208 | 0.0000 | OK |
| R5_Drop_First_100w | 0.5664 | -0.0473 | 0.0000 | OK |
| R6_Remove_Stopwords | 0.6028 | -0.0109 | 0.0000 | OK |

## Conclusion

All robustness checks passed (max drop <= 0.05).

## Per-Perturbation Details

### R1_Strip_Email_Phone
- Macro F1: 0.6137 (delta: +0.0000)
- Min Recall: 0.0000
- Low recall categories (<0.30): BPO, ARTS, AUTOMOBILE, CONSULTANT

### R2_No_Punctuation
- Macro F1: 0.6085 (delta: -0.0052)
- Min Recall: 0.0000
- Low recall categories (<0.30): BPO, AUTOMOBILE, CONSULTANT, ARTS

### R3_Random_Typos
- Macro F1: 0.6155 (delta: +0.0018)
- Min Recall: 0.0000
- Low recall categories (<0.30): BPO, ARTS, AUTOMOBILE, CONSULTANT

### R4_Truncate_200w
- Macro F1: 0.5929 (delta: -0.0208)
- Min Recall: 0.0000
- Low recall categories (<0.30): ARTS, BPO, AUTOMOBILE, CONSULTANT

### R5_Drop_First_100w
- Macro F1: 0.5664 (delta: -0.0473)
- Min Recall: 0.0000
- Low recall categories (<0.30): BPO, AUTOMOBILE, ARTS, CONSULTANT

### R6_Remove_Stopwords
- Macro F1: 0.6028 (delta: -0.0109)
- Min Recall: 0.0000
- Low recall categories (<0.30): BPO, ARTS, AUTOMOBILE

