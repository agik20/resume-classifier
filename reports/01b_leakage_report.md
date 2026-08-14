# Category Leakage Mitigation Report

**Date**: 2026-08-14
**Phase**: 1b

---

## Executive Summary

Category-name leakage is **REAL and SIGNIFICANT**. Removing category names from text reduces baseline Macro F1 by **0.0524** (from 0.6506 to 0.5982).

---

## Leakage Quantification

| Metric | Value |
|--------|-------|
| High leakage categories (>80%) | **19/24** (79%) |
| 100% leakage categories | **10** |
| Low leakage categories (<50%) | **4/24** (17%) |

### High Leakage Categories (100%)
ACCOUNTANT, CONSTRUCTION, CONSULTANT, DESIGNER, ENGINEERING, FINANCE, HEALTHCARE, HR, SALES, TEACHER

### Moderate Leakage (80-90%)
ADVOCATE (81.4%), AVIATION (82.9%), BANKING (80.0%), ARTS (88.3%), CHEF (91.5%), FITNESS (85.5%), INFORMATION-TECHNOLOGY (94.2%), PUBLIC-RELATIONS (95.5%), BUSINESS-DEVELOPMENT (98.3%)

### Low Leakage (<50%)
AGRICULTURE (46.0%), AUTOMOBILE (41.7%), BPO (45.5%), DIGITAL-MEDIA (40.6%)

---

## Baseline Comparison

| Variant | Macro F1 | Std Dev |
|---------|----------|---------|
| **Raw Text** | **0.6506** | ±0.0223 |
| **Mitigated Text** | **0.5982** | ±0.0161 |
| **Delta** | **0.0524** | - |

**Interpretation**: The 0.0524 delta confirms that category-name leakage inflates baseline performance by over 5 percentage points.

---

## Mitigation Strategy

**Chosen approach**: Header stripping (S1) + dual-model comparison (S4)

- Strip first 200 characters (typical header area: name, contact, title)
- Compare performance raw vs. mitigated
- Document leakage impact for honest reporting

**Recommendation**: Use **mitigated text** for all future training and evaluation to ensure metrics reflect genuine semantic understanding, not label matching shortcuts.

---

## Decision

✅ **Continue with mitigated pipeline** — leakage mitigation significantly changes results (>0.05 Macro F1 delta).

---

## Next Steps

Proceed to **Phase 2: EDA** using mitigated text as input.
