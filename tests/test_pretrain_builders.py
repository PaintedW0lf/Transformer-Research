from __future__ import annotations

from typing import Iterable, List

import torch

import deepseek_r1_pretrain as deepseek
import gpt2_pretrain as gpt2


class DummyTokenizer:
    def __init__(self) -> None:
        self.eos_token_id = 2

    def __len__(self) -> int:
        return 10

    def encode(self, text: str, add_special_tokens: bool = False) -> List[int]:
        _ = add_special_tokens
        return [1] * len(text)


class DummyConfig:
    def __init__(self) -> None:
        self.vocab_size = 0
        self.max_position_embeddings = 0


class DummyModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()


class DummyAutoTokenizer:
    @staticmethod
    def from_pretrained(model_id: str, use_fast: bool = True) -> DummyTokenizer:
        _ = model_id
        _ = use_fast
        return DummyTokenizer()


class DummyAutoConfig:
    @staticmethod
    def from_pretrained(model_id: str) -> DummyConfig:
        _ = model_id
        return DummyConfig()


class DummyAutoModel:
    @staticmethod
    def from_config(config: DummyConfig) -> DummyModel:
        _ = config
        return DummyModel()


def test_build_gpt2_from_scratch() -> None:
    texts = ["hello", "world"]
    model, dataset, collator = gpt2.build_gpt2_from_scratch(texts, block_size=4)

    assert model.config.n_positions == 4
    assert len(dataset) == 2
    assert collator.pad_id == gpt2.tiktoken.get_encoding("gpt2").eot_token


def test_build_deepseek_from_scratch(monkeypatch) -> None:
    monkeypatch.setattr(deepseek, "AutoTokenizer", DummyAutoTokenizer)
    monkeypatch.setattr(deepseek, "AutoConfig", DummyAutoConfig)
    monkeypatch.setattr(deepseek, "AutoModelForCausalLM", DummyAutoModel)

    texts: Iterable[str] = ["hi", "there"]
    model, dataset, collator = deepseek.build_deepseek_r1_from_scratch(texts, block_size=5)

    assert isinstance(model, DummyModel)
    assert len(dataset) == 1
    assert collator.pad_id == 2
