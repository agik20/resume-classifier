# Resume Domain Classifier

**Version 1.0.0** — stable release (2026-11-04)

Multi-class classifier for resume domain prediction across 24 categories.
Built as a portfolio-grade ML engineering demonstration with rigorous
leakage mitigation, documented experimentation, and honest performance
analysis.

## Results

| Metric | Value |
|--------|-------|
| Test Macro F1 | 0.5762 |
| Validation Macro F1 | 0.6137 |
| Baseline (unmitigated) | 0.5329 |
| Improvement | +15.1% |
| Inference latency (p50) | 0.33 ms |
| Model size (active artifacts) | ~117 MB (word vec 12.9 MB + char vec 1.9 MB + classifier 102.9 MB) |

The 0.65 target was not met. This is attributed to inherent dataset
ambiguity (98.8% of resumes contain keywords from 2+ domains), not model
failure. See `reports/final_model_decision.md` for the full analysis.

## Quick Start

For inference only:

```bash
pip install -r requirements.txt
```

For the full validated environment (all 136 packages, including Phase 8
embedding dependencies):

```bash
pip install -r requirements.lock
```

Run inference:

```bash
python predict.py --resume path/to/resume.txt --top_k 3
```

Or import in Python:

```python
from predict import predict_resume

result = predict_resume("John Smith, Software Engineer ...")
print(result["predicted_category"])   # "ENGINEERING"
print(result["confidence_score"])     # raw decision value (not a probability)
print(result["top_k_predictions"])    # top 3 with scores
```

## Repository Layout

```
predict.py              Inference entry point (module + CLI)
experiments/            Trained model artifacts (.joblib)
scripts/                Phase-by-phase training and analysis scripts
reports/                Generated reports (EDA, tuning, error analysis, final)
data/                   Dataset + split files
tests/                  pytest test suite
```

## Model Artifacts

The three active artifacts in `experiments/` are the frozen final model:

| Artifact | Size | Role |
|----------|------|------|
| `best_phase5_word_vec.joblib` | 12.9 MB | Word TF-IDF vectorizer (433,832 features) |
| `best_phase5_char_vec.joblib` | 1.9 MB | Char TF-IDF vectorizer (101,860 features) |
| `best_phase5_clf.joblib` | 102.9 MB | LinearSVC classifier (535,692 input features, 24 classes) |

**Reproducibility strategy**: The artifacts are **not** committed to git (total ~117 MB).
Instead, they can be deterministically reproduced from `scripts/phase5_tuning.py`
using `data/Resume.csv` + `data/splits/splits.json` + `requirements.lock`.
The dataset file is large (~56 MB unzipped) and is excluded from git via `.gitignore`.
To reproduce: run `pip install -r requirements.lock` then
`python scripts/phase5_tuning.py` with `RESUME_DATA_DIR` pointing to the data root.

For deployment, distribute the three `.joblib` files alongside `predict.py`
(e.g., via a release tarball or a private artifact registry).
Git LFS is recommended if the artifacts need to live in this repository.

> **Important: cloning the repository is not sufficient to run inference.**
> The model artifacts (`experiments/*.joblib`) and the dataset
> (`data/Resume.csv`) are excluded from git. You must either obtain the
> three `.joblib` files separately, or reproduce them via the
> `scripts/phase5_tuning.py` pipeline as described above.

## Key Reports

| File | Contents |
|------|----------|
| `reports/02_eda_findings.md` | Label distribution, multi-domain rate, separability |
| `reports/05_tuning_report.md` | 20-experiment grid search results |
| `reports/07_error_analysis.md` | Confusion pairs, worst classes |
| `reports/final_model_decision.md` | Multi-criteria model selection |
| `reports/FINAL_REPORT.md` | Executive summary |

## Model

**LinearSVC(C=10)** on combined word+char TF-IDF features:
- Word n-grams (1,2), `sublinear_tf=True`
- Char n-grams (3,5), `min_df=2`, `sublinear_tf=True`
- ~535K total feature dimensions
- Training time: ~7 seconds (CPU only)

## Limitations

- **BPO**: 0.14 recall (only 3 test samples)
- Small classes (ARTS, AUTOMOBILE, CONSULTANT) are unstable
- `confidence_score` is a raw decision value, not a calibrated probability
- ~60% of errors are dataset-inherent ambiguity

## Future Work

- **Synthetic data / manual relabeling**: The 0.65-0.67 F1 ceiling is dataset-inherent.
  Synthetic oversampling or manual relabeling of ambiguous multi-domain resumes could close the gap.
- **Probability calibration**: `confidence_score` is a raw LinearSVC decision value.
  Applying Platt scaling or isotonic regression would produce calibrated probabilities.
- **Feature engineering**: Semantic embeddings (e.g., sentence-transformers) were tested
  and rejected in Phase 8. A hybrid TF-IDF + embedding pipeline is unexplored.
- **Deployment**: A lightweight API wrapper (e.g., FastAPI) around `predict_resume()`
  is a natural next step.

## License

MIT — see [`LICENSE`](LICENSE).

## Release Notes

See [`CHANGELOG.md`](CHANGELOG.md) for the full v1.0.0 change history,
artifact distribution policy, and known limitations.
