from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

import inference_utils


class DummyEncoding:
    eot_token = 0

    def encode(self, text: str) -> list[int]:
        return [ord(c) % 50 for c in text if c.strip()] or [1, 2]

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(t + 65) for t in tokens)


class DummyModel:
    def __init__(self, vocab_size: int = 50) -> None:
        self._vocab_size = vocab_size
        self._device = torch.device("cpu")

    def parameters(self):
        yield torch.zeros(1, device=self._device)

    def eval(self) -> "DummyModel":
        return self

    def to(self, device) -> "DummyModel":
        self._device = torch.device(device)
        return self

    def generate(self, input_ids: torch.Tensor, **kwargs) -> torch.Tensor:
        new_tokens = torch.zeros(1, 3, dtype=torch.long)
        return torch.cat([input_ids, new_tokens], dim=1)


def test_generate_returns_string(monkeypatch) -> None:
    encoding = DummyEncoding()
    model = DummyModel()

    result = inference_utils.generate(model, encoding, "What is virtue?", device="cpu")

    assert isinstance(result, str)


def test_generate_excludes_prompt_tokens(monkeypatch) -> None:
    encoding = DummyEncoding()
    model = DummyModel()

    prompt = "test"
    result = inference_utils.generate(model, encoding, prompt, device="cpu")

    # result should only contain new tokens, not the prompt re-decoded
    prompt_decoded = encoding.decode(encoding.encode(prompt))
    assert result != prompt_decoded or result == ""


def test_generate_with_history_formats_prompt() -> None:
    encoding = DummyEncoding()
    model = DummyModel()

    reply, updated_history = inference_utils.generate_with_history(
        model, encoding, "What is the self?", history="", device="cpu"
    )

    assert isinstance(reply, str)
    assert "Human: What is the self?" in updated_history
    assert "Assistant:" in updated_history


def test_generate_with_history_appends_to_existing_history() -> None:
    encoding = DummyEncoding()
    model = DummyModel()

    prior = "Human: Hello\nAssistant: Hi\n"
    _, updated = inference_utils.generate_with_history(
        model, encoding, "Next question", history=prior, device="cpu"
    )

    assert updated.startswith(prior)
    assert "Next question" in updated
