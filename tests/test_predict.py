"""Integration tests for predict.py inference path."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from predict import predict_resume, _strip_header, _clean_text

PROJECT_ROOT = Path(__file__).parent.parent


def test_model_artifacts_exist():
    for name in ["best_phase5_word_vec.joblib", "best_phase5_char_vec.joblib", "best_phase5_clf.joblib"]:
        assert (PROJECT_ROOT / "experiments" / name).exists(), f"Missing: {name}"


def test_predict_returns_expected_keys():
    result = predict_resume("Software Engineer, Python, Django, Machine Learning, Data Science")
    assert "predicted_category" in result
    assert "confidence_score" in result
    assert "top_k_predictions" in result


def test_predicted_category_is_string():
    result = predict_resume("Financial analyst, accounting, audit, banking, finance")
    assert isinstance(result["predicted_category"], str)
    assert len(result["predicted_category"]) > 0


def test_top_k_respects_limit():
    result = predict_resume("Sales, business development, customer service, finance", top_k=5)
    assert len(result["top_k_predictions"]) == 5


def test_top_k_sorted_descending():
    result = predict_resume("Engineer, Python, software, data", top_k=3)
    scores = [p["score"] for p in result["top_k_predictions"]]
    assert scores == sorted(scores, reverse=True)


def test_top_k_each_item_has_category_and_score():
    result = predict_resume("Chef, cooking, restaurant, food, kitchen", top_k=2)
    for item in result["top_k_predictions"]:
        assert "category" in item
        assert "score" in item
        assert isinstance(item["category"], str)
        assert isinstance(item["score"], float)


def test_empty_string_returns_valid_structure():
    result = predict_resume("")
    assert isinstance(result["predicted_category"], str)
    assert isinstance(result["confidence_score"], float)


def test_short_text_still_produces_prediction():
    result = predict_resume("doctor")
    assert isinstance(result["predicted_category"], str)


def test_strip_header_removes_first_chars():
    text = "A" * 500
    stripped = _strip_header(text, 200)
    assert len(stripped) == 300
    assert stripped == "A" * 300


def test_strip_header_short_text_unchanged():
    text = "short"
    assert _strip_header(text, 200) == "short"


def test_clean_text_lowercases_and_collapses_whitespace():
    text = "Hello   World\n\tFOO"
    assert _clean_text(text) == "hello world foo"


def test_clean_text_empty():
    assert _clean_text("") == ""
    assert _clean_text(None) == ""


def test_confidence_score_is_float():
    result = predict_resume("Engineer, Python, software, data, ML")
    assert isinstance(result["confidence_score"], float)


def test_predict_resume_idempotent():
    text = "Accountant, finance, audit, banking, sales, business"
    r1 = predict_resume(text)
    r2 = predict_resume(text)
    assert r1["predicted_category"] == r2["predicted_category"]
    assert r1["confidence_score"] == r2["confidence_score"]
