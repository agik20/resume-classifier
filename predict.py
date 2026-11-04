"""Resume Classifier Inference Function

Usage (as module):
    from predict import predict_resume
    result = predict_resume("John Smith, Software Engineer ...")
    print(result["predicted_category"])  # e.g. "ENGINEERING"
    print(result["confidence_score"])    # uncalibrated decision value

Usage (CLI):
    python predict.py --resume path/to/resume.txt --top_k 3

Note:
    confidence_score is a raw LinearSVC decision value, NOT a calibrated
    probability. Negative values are normal and mean the sample is closer
    to the decision boundary than the training-set mean. Only the relative
    ordering across classes is meaningful.
"""
import joblib
import numpy as np
import re
from pathlib import Path
from scipy.sparse import hstack

MODEL_DIR = Path(__file__).parent / "experiments"
_REQUIRED_ARTIFACTS = [
    MODEL_DIR / "best_phase5_word_vec.joblib",
    MODEL_DIR / "best_phase5_char_vec.joblib",
    MODEL_DIR / "best_phase5_clf.joblib",
]

def _strip_header(text, chars=200):
    if not text or not isinstance(text, str):
        return ""
    return text[chars:] if len(text) > chars else text

def _clean_text(text):
    if not text or not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.lower()).strip()

_word_vec = _char_vec = _clf = None

def _load_model():
    global _word_vec, _char_vec, _clf
    if _word_vec is None:
        missing = [p.name for p in _REQUIRED_ARTIFACTS if not p.exists()]
        if missing:
            raise FileNotFoundError(
                f"Model artifacts missing from {MODEL_DIR}: {', '.join(missing)}. "
                "Run the training pipeline (scripts/phase5_tuning.py) first."
            )
        _word_vec = joblib.load(_REQUIRED_ARTIFACTS[0])
        _char_vec = joblib.load(_REQUIRED_ARTIFACTS[1])
        _clf = joblib.load(_REQUIRED_ARTIFACTS[2])
    return _word_vec, _char_vec, _clf

def predict_resume(text: str, top_k: int = 3) -> dict:
    """Predict the resume domain category.

    Returns a dict with:
        predicted_category (str) — the most likely domain
        confidence_score (float) — raw decision value (NOT a probability)
        top_k_predictions (list) — top-k categories with decision scores
    """
    word_vec, char_vec, clf = _load_model()
    mitigated = _strip_header(_clean_text(text), 200)
    X = hstack([word_vec.transform([mitigated]), char_vec.transform([mitigated])])
    decisions = clf.decision_function(X)[0]
    best_idx = int(np.argmax(decisions))
    top_indices = np.argsort(decisions)[::-1][:top_k]
    top_predictions = [
        {"category": str(clf.classes_[i]), "score": float(decisions[i])}
        for i in top_indices
    ]
    return {
        "predicted_category": str(clf.classes_[best_idx]),
        "confidence_score": float(decisions[best_idx]),
        "top_k_predictions": top_predictions,
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", required=True)
    parser.add_argument("--top_k", type=int, default=3)
    args = parser.parse_args()
    with open(args.resume) as f:
        text = f.read()
    result = predict_resume(text, args.top_k)
    print(f"Predicted: {result['predicted_category']}")
    print(f"Score: {result['confidence_score']:.4f}")
    for i, p in enumerate(result['top_k_predictions'], 1):
        print(f"  {i}. {p['category']} ({p['score']:.4f})")
