# Resume Domain Classifier

**Version 1.0.0** — stable release (2026-11-04)

24-way classifier for resume domain prediction. Built with rigorous leakage
mitigation, a phase-gated experiment pipeline, and honest reporting — the
0.65 F1 target was not met and is documented as a dataset-inherent ceiling.

## Dataset

| | |
|---|---|
| Total resumes | 2,484 |
| Classes | 24 (5.45× imbalance) |
| Multi-domain rate | 98.8% contain keywords from ≥2 categories |
| Split | 55/15/30 · train 1,365 · val 373 · test 746 |

## Final Model

```
resume text → clean + strip first 200 chars (leakage mitigation)
           → word TF-IDF (1–2 grams, 433,832 feats)
           + char_wb TF-IDF (3–5 grams, 101,860 feats)
           → LinearSVC(C=10, max_iter=10000, 24 classes)
```

| Metric | Value |
|--------|-------|
| Test Macro F1 | **0.5762** |
| Val Macro F1 | 0.6137 |
| Improvement over mitigated baseline | +0.0808 CV (+15.1%) |
| Inference p50 / p95 | 0.33 ms / 0.44 ms |
| Model artifact total | ~117 MB |

The 0.65 target was **not** achieved. The gap is attributed to dataset
inherent ambiguity (~60% of errors are cross-domain keyword overlaps),
not model weakness.

## Key Limitations

- BPO test recall 0.143 (only 7 test samples); small classes are high-variance
- `confidence_score` is a raw LinearSVC decision value, **not** a probability
- Model artifacts (~117 MB) are excluded from git — obtain or reproduce (below)
- Results transfer only within this dataset's 24-class taxonomy

## Repository Layout

```
predict.py          Inference module + CLI
experiments/        Trained artifacts (.joblib) + experiment JSONs
scripts/           Phase-by-phase pipeline scripts
reports/PROJECT_REPORT.md   Full technical project report (20 sections)
reports/artifacts/ Raw evidence JSONs (baseline, robustness, errors, tests, decision)
data/               Dataset + split files
tests/              17 pytest tests
```

## Installation

Inference only (11 pinned packages):
```bash
pip install -r requirements.txt
```

Full validated environment (136 packages, includes sentence-transformers stack):
```bash
pip install -r requirements.lock
```

## Quick Start

```bash
# CLI
python predict.py --resume data/samples/engineer.txt --top_k 3

# Python
from predict import predict_resume
r = predict_resume("John Smith, Software Engineer ...")
print(r["predicted_category"])   # e.g. "ENGINEERING"
print(r["confidence_score"])     # raw decision value (not a probability)
```

> **Cloning is not sufficient to run inference.** The three `.joblib` files in
> `experiments/` are excluded from git. Obtain them as release assets or
> reproduce with `python scripts/phase5_tuning.py` (after installing
> `requirements.lock` and providing `data/Resume.csv`).

## Tests

```bash
python -m pytest tests/ -v   # 17 tests
```

## Full Technical Report

See [`reports/PROJECT_REPORT.md`](reports/PROJECT_REPORT.md) — 20 sections
covering data audit, leakage mitigation, all experimental phases, error
analysis, model architecture, reproducibility, and known limitations.

## License

MIT — see [`LICENSE`](LICENSE).
