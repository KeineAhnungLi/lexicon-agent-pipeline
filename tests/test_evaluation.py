from __future__ import annotations

import pytest

from lexicon_pipeline.evaluation.metrics import exact_match
from lexicon_pipeline.evaluation.rubric import DEFAULT_RUBRIC
from lexicon_pipeline.evaluation.sampling import deterministic_sample


def test_exact_match_reports_fields() -> None:
    result = exact_match([{"a": 1, "b": 2}], [{"a": 1, "b": 3}], ["a", "b"])
    assert result == {"matched": 1, "compared": 2, "rate": 0.5}


def test_exact_match_length_mismatch() -> None:
    assert exact_match([], [{"a": 1}], ["a"])["rate"] == 0.0


def test_sampling_is_reproducible() -> None:
    assert deterministic_sample(list(range(10)), 3, seed=7) == deterministic_sample(
        list(range(10)), 3, seed=7
    )


def test_sampling_rejects_negative_size() -> None:
    with pytest.raises(ValueError):
        deterministic_sample([1], -1)


def test_default_rubric_has_no_results() -> None:
    assert {item.name for item in DEFAULT_RUBRIC} == {
        "meaning", "word_form", "grammar", "collocation", "translation"
    }
