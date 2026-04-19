from __future__ import annotations

import json
from pathlib import Path

import pytest

import visualize_vocab


def test_raw_counts_and_bigrams_filter_stop_words() -> None:
    counts = visualize_vocab.raw_counts(["The mind soul reason", "mind soul reason"])
    bigrams = visualize_vocab.raw_bigrams(["The mind soul reason", "mind soul reason"])

    assert counts["mind"] == 2
    assert "the" not in counts
    assert ("mind", "soul") in bigrams
    assert all(token not in visualize_vocab.FILTER for token in ["mind", "soul"])


def test_blend_maps_dominance_extremes() -> None:
    red = visualize_vocab._blend(0.0)
    purple = visualize_vocab._blend(0.5)
    blue = visualize_vocab._blend(1.0)

    assert red == pytest.approx(tuple(visualize_vocab._RED))
    assert blue == pytest.approx(tuple(visualize_vocab._BLUE))
    assert purple == pytest.approx(tuple(visualize_vocab._PURPLE))


def test_pack_circles_handles_empty_and_singleton_inputs() -> None:
    assert visualize_vocab.pack_circles([]) == []
    assert visualize_vocab.pack_circles([1.0]) == [(0.0, 0.0)]


def test_load_latest_results_selects_latest_file(tmp_path: Path) -> None:
    older = tmp_path / "bias_evaluation_20240101_120000.json"
    newer = tmp_path / "bias_evaluation_20240102_120000.json"
    older.write_text(json.dumps({"evaluations": []}), encoding="utf-8")
    newer.write_text(json.dumps({"evaluations": [{"western_output": "x", "eastern_output": "y"}]}), encoding="utf-8")

    results = visualize_vocab.load_latest_results(str(tmp_path))

    assert results["evaluations"][0]["western_output"] == "x"


def test_build_charts_writes_all_expected_images(tmp_path: Path) -> None:
    results = {
        "evaluations": [
            {"western_output": "mind soul reason", "eastern_output": "dharma karma mind"},
            {"western_output": "reason and virtue", "eastern_output": "karma and dharma"},
        ]
    }

    visualize_vocab.build_charts(results, str(tmp_path), top_n=5, top_n_bigrams=3)

    expected = {
        "vocab_bubbles_western.png",
        "vocab_bubbles_eastern.png",
        "vocab_bubbles_combined.png",
        "bigram_bubbles_western.png",
        "bigram_bubbles_eastern.png",
        "bigram_bubbles_combined.png",
    }
    assert expected == {path.name for path in tmp_path.iterdir()}
