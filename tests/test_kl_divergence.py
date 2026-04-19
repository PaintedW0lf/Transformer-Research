from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

from kl_divergence import (
    _to_pct,
    compute_kl_pct,
    compute_kl_report,
    compute_symmetric_kl_pct,
)


class DummyEncoding:
    def __init__(self, token_count: int = 4) -> None:
        self.token_count = token_count

    def encode(self, text: str) -> list[int]:
        _ = text
        return list(range(self.token_count))


class DummyModel:
    def __init__(self, logits: torch.Tensor) -> None:
        self.logits = logits
        self.eval_calls = 0

    def eval(self) -> "DummyModel":
        self.eval_calls += 1
        return self

    def __call__(self, input_ids: torch.Tensor) -> SimpleNamespace:
        seq_len = input_ids.shape[1]
        logits = self.logits.unsqueeze(0).expand(1, seq_len, -1).clone()
        return SimpleNamespace(logits=logits)


class BrokenModel(DummyModel):
    def __call__(self, input_ids: torch.Tensor) -> SimpleNamespace:
        _ = input_ids
        raise RuntimeError("model failure")


def test_to_pct_handles_special_values() -> None:
    assert _to_pct(float("nan")) != _to_pct(float("nan"))
    assert _to_pct(float("inf")) != _to_pct(float("inf"))


def test_compute_kl_pct_returns_nan_for_short_text() -> None:
    model = DummyModel(torch.tensor([1.0, 0.0]))
    encoding = DummyEncoding(token_count=1)

    assert compute_kl_pct(model, model, encoding, text="x", device="cpu") != compute_kl_pct(
        model, model, encoding, text="x", device="cpu"
    )


def test_compute_kl_pct_is_zero_for_identical_models() -> None:
    logits = torch.tensor([2.0, 0.5, -1.0])
    model = DummyModel(logits)
    encoding = DummyEncoding(token_count=5)

    result = compute_kl_pct(model, model, encoding, text="shared prompt", device="cpu")

    assert result == pytest.approx(0.0, abs=1e-6)
    assert model.eval_calls >= 2


def test_compute_kl_pct_returns_nan_on_failure() -> None:
    encoding = DummyEncoding(token_count=5)
    broken = BrokenModel(torch.tensor([1.0, 0.0]))

    result = compute_kl_pct(broken, broken, encoding, text="shared prompt", device="cpu")

    assert result != result


def test_compute_symmetric_kl_pct_is_symmetric() -> None:
    model_a = DummyModel(torch.tensor([2.0, 0.0]))
    model_b = DummyModel(torch.tensor([0.0, 2.0]))
    encoding = DummyEncoding(token_count=5)

    left = compute_symmetric_kl_pct(model_a, model_b, encoding, text="shared prompt", device="cpu")
    right = compute_symmetric_kl_pct(model_b, model_a, encoding, text="shared prompt", device="cpu")

    assert left == pytest.approx(right, rel=1e-9)
    assert left > 0.0


def test_compute_kl_report_returns_expected_schema() -> None:
    model_west = DummyModel(torch.tensor([1.5, 0.3, -0.2]))
    model_east = DummyModel(torch.tensor([-0.2, 0.3, 1.5]))
    encoding = DummyEncoding(token_count=6)

    report = compute_kl_report(
        model_west,
        model_east,
        encoding,
        prompt="What is the self?",
        west_output="western answer",
        east_output="eastern answer",
        device="cpu",
    )

    assert set(report) == {
        "west_to_east_on_prompt",
        "east_to_west_on_prompt",
        "symmetric_on_prompt",
        "west_to_east_on_east_output",
        "east_to_west_on_west_output",
        "_note",
    }
    assert report["_note"] == "all values are percentages (0=identical, 100=max divergence)"
    for key, value in report.items():
        if key != "_note":
            assert isinstance(value, float)
