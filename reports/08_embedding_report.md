# Phase 8: Embeddings (Strategy A) - FINAL DECISION

**Date**: 2026-08-16 | **Model**: all-MiniLM-L6-v2 (384-dim)

## Results

| Experiment | CV F1 | Test F1 | vs Phase 5 |
|---|---|---|---|
| LR_Embeddings(384d) | 0.4671 | 0.4550 | -0.159 |
| LR_TF-IDF(15K) | 0.5411 | 0.5607 | -0.053 |
| LR_Combined(484d) | 0.4699 | 0.4549 | -0.159 |
| SVM_Embeddings(384d) | 0.3875 | 0.3692 | -0.245 |
| **Phase 5 Best** | **0.6137** | **0.6137** | **baseline** |

## Analysis

**Embeddings did NOT help.** The  model:
- Compresses resume text into 384 dimensions, losing domain-specific keyword patterns
- TF-IDF retains raw word signals critical for resume classification
- Combined approach (embeddings + TF-IDF) performed worse than either alone
- All embedding-based models underperform the Phase 5 baseline

**Why?** Resume classification relies on keyword patterns (e.g., "SQL", "Python", "React") that embeddings smooth over. The 24-class multi-domain problem benefits from explicit token matching rather than semantic similarity.

## Decision

**FINAL MODEL**: Phase 5 - Combined Word+Char TF-IDF + LinearSVC(C=10)

- Test Macro F1: **0.6137**
- Gate: CONTINUE to Phase 9 (Final Model Selection & Deployment)
