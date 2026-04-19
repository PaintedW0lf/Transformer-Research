from __future__ import annotations

import pytest

from stats_analysis import (
    analyze_category,
    bhattacharyya_coefficient,
    bhattacharyya_distance,
    compute_overlap_metrics,
    get_word_distribution,
    tokenize,
)


def test_tokenize_filters_short_and_nonalpha_tokens() -> None:
    assert tokenize("A 1 ! x") == []
    assert tokenize("Mind, body, and soul!") == ["mind", "body", "and", "soul"]


def test_get_word_distribution_normalizes_counts() -> None:
    distribution = get_word_distribution(["aa bb", "aa cc"])

    assert distribution == pytest.approx({"aa": 0.5, "bb": 0.25, "cc": 0.25})


def test_bhattacharyya_metrics_cover_boundaries() -> None:
    identical = {"a": 0.5, "b": 0.5}
    disjoint_left = {"a": 1.0}
    disjoint_right = {"b": 1.0}

    assert bhattacharyya_coefficient(identical, identical) == pytest.approx(1.0)
    assert bhattacharyya_coefficient(disjoint_left, disjoint_right) == pytest.approx(0.0)
    assert bhattacharyya_distance(identical, identical) == pytest.approx(0.0)
    assert bhattacharyya_distance(disjoint_left, disjoint_right) == float("inf")


def test_compute_overlap_metrics_returns_expected_schema() -> None:
    metrics = compute_overlap_metrics(["alpha beta", "alpha"], ["alpha gamma"])

    assert set(metrics) == {
        "bhattacharyya_coefficient",
        "bhattacharyya_distance",
        "bhattacharyya_interpretation",
        "unique_western_words",
        "unique_eastern_words",
        "common_words",
    }
    assert metrics["unique_western_words"] == 2
    assert metrics["unique_eastern_words"] == 2
    assert metrics["common_words"] == 1


def test_analyze_category_counts_prompts() -> None:
    result = analyze_category(
        "self_identity",
        [
            {"western_output": "alpha beta", "eastern_output": "alpha gamma"},
            {"western_output": "alpha", "eastern_output": "alpha"},
        ],
    )

    assert result["category"] == "self_identity"
    assert result["num_prompts"] == 2
