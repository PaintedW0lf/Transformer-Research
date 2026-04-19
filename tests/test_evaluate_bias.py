from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

import evaluate_bias


class DummyTokenizer:
    def encode(self, text: str) -> list[int]:
        return [ord(ch) % 10 for ch in text if ch.strip()] or [1, 2]


class DummyModel:
    def __init__(self, name: str) -> None:
        self.name = name
        self.generation_config = SimpleNamespace(eos_token_id=2, pad_token_id=None)


def test_single_output_metrics_and_concept_counts() -> None:
    metrics = evaluate_bias.analyze_single_output("Dharma and virtue, dharma again")

    assert metrics["length_chars"] == len("Dharma and virtue, dharma again")
    assert metrics["length_words"] == 5
    assert metrics["repetition_score"] == 0.0
    assert metrics["type_token_ratio"] == 0.8
    assert metrics["concept_frequencies"]["eastern_marker_count"] == 2
    assert metrics["concept_frequencies"]["western_marker_count"] == 1


def test_repetition_score_and_type_token_ratio_edge_cases() -> None:
    assert evaluate_bias.compute_repetition_score("a b c") == 0.0
    assert evaluate_bias.compute_repetition_score("a a a a a") > 0.0
    assert evaluate_bias.compute_type_token_ratio("") == 0.0
    assert evaluate_bias.compute_type_token_ratio("same same same") == pytest.approx(1 / 3)


def test_concept_frequencies_are_case_insensitive() -> None:
    freqs = evaluate_bias.compute_concept_frequencies("Dharma and Virtue, DHARMA")

    assert freqs["eastern_marker_count"] == 2
    assert freqs["western_marker_count"] == 1
    assert freqs["eastern_ratio"] == pytest.approx(2 / 3)
    assert freqs["western_ratio"] == pytest.approx(1 / 3)


def test_compute_perplexity_returns_loss_based_value(monkeypatch) -> None:
    class FakeModel:
        def eval(self) -> "FakeModel":
            return self

        def __call__(self, input_ids, labels):
            _ = input_ids
            _ = labels
            return SimpleNamespace(loss=torch.tensor(0.25))

    perplexity = evaluate_bias.compute_perplexity(FakeModel(), DummyTokenizer(), "shared text", "cpu")

    assert perplexity == pytest.approx(torch.exp(torch.tensor(0.25)).item())


def test_compute_perplexity_gracefully_handles_short_text() -> None:
    class ShortTokenizer:
        def encode(self, text: str) -> list[int]:
            _ = text
            return [1]

    class EvalModel(DummyModel):
        def eval(self) -> "EvalModel":
            return self

    result = evaluate_bias.compute_perplexity(EvalModel("west"), ShortTokenizer(), "x", "cpu")

    assert result == float("inf")


def test_analyze_bias_prints_kl_columns(capsys) -> None:
    results = {
        "evaluations": [
            {
                "category": "self_identity",
                "western_metrics": {"repetition_score": 0.0, "type_token_ratio": 1.0, "concept_frequencies": {"eastern_ratio": 0.0}},
                "eastern_metrics": {"repetition_score": 0.1, "type_token_ratio": 0.5, "concept_frequencies": {"eastern_ratio": 1.0}},
                "cross_perplexity": {"western_model_on_eastern_text": 1.2, "eastern_model_on_western_text": 2.3},
                "kl_divergence": {
                    "west_to_east_on_prompt": 10.0,
                    "east_to_west_on_prompt": 11.0,
                    "symmetric_on_prompt": 10.5,
                },
            }
        ]
    }

    evaluate_bias.analyze_bias(results)
    output = capsys.readouterr().out

    assert "KL W→E%" in output
    assert "KL Sym%" in output


def test_evaluate_models_writes_kl_output_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(evaluate_bias, "PHILOSOPHICAL_PROMPTS", {"self_identity": ["What is the self?"]})
    monkeypatch.setattr(evaluate_bias, "load_model", lambda path, device: DummyModel(path))
    monkeypatch.setattr(evaluate_bias, "get_tokenizer", lambda: DummyTokenizer())

    def fake_generate(model, encoding, prompt, device, max_new_tokens, **kwargs):
        _ = encoding
        _ = device
        _ = max_new_tokens
        _ = kwargs
        return f"{model.name}:{prompt}"

    monkeypatch.setattr(evaluate_bias, "generate", fake_generate)
    monkeypatch.setattr(evaluate_bias, "compute_perplexity", lambda *args, **kwargs: 1.23)
    monkeypatch.setattr(
        evaluate_bias,
        "compute_kl_report",
        lambda *args, **kwargs: {
            "west_to_east_on_prompt": 10.0,
            "east_to_west_on_prompt": 11.0,
            "symmetric_on_prompt": 10.5,
            "west_to_east_on_east_output": 12.0,
            "east_to_west_on_west_output": 13.0,
            "_note": "all values are percentages (0=identical, 100=max divergence)",
        },
    )

    results = evaluate_bias.evaluate_models(
        western_path="west-model",
        eastern_path="east-model",
        output_dir=str(tmp_path),
        max_tokens=12,
    )

    files = list(tmp_path.glob("bias_evaluation_*.json"))
    assert len(files) == 1

    saved = json.loads(files[0].read_text(encoding="utf-8"))
    assert saved["evaluations"][0]["kl_divergence"]["symmetric_on_prompt"] == 10.5
    assert results["evaluations"][0]["cross_perplexity"]["western_model_on_eastern_text"] == 1.23
