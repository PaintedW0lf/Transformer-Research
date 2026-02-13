"""Shared utilities for causal LM pretraining."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import torch
from torch.utils.data import Dataset
from transformers import Trainer, TrainingArguments


@dataclass
class LMExample:
    input_ids: List[int]


class LMDataset(Dataset):
    def __init__(self, input_id_blocks: List[List[int]]):
        self._data = input_id_blocks

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, idx: int) -> LMExample:
        return LMExample(input_ids=self._data[idx])


class SimpleLMDataCollator:
    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, features: List[LMExample]) -> dict:
        max_len = max(len(f.input_ids) for f in features)
        input_ids = [f.input_ids + [self.pad_id] * (max_len - len(f.input_ids)) for f in features]
        input_tensor = torch.tensor(input_ids, dtype=torch.long)
        return {
            "input_ids": input_tensor,
            "labels": input_tensor.clone(),
            "attention_mask": (input_tensor != self.pad_id).long(),
        }


def make_blocks(token_ids: List[int], block_size: int) -> List[List[int]]:
    blocks = []
    for i in range(0, len(token_ids) - block_size + 1, block_size):
        blocks.append(token_ids[i : i + block_size])
    return blocks


def build_trainer(
    model: torch.nn.Module,
    dataset: Dataset,
    collator: SimpleLMDataCollator,
    output_dir: str,
    per_device_train_batch_size: int = 1,
    learning_rate: float = 5e-4,
    max_steps: int = 100,
) -> Trainer:
    args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        learning_rate=learning_rate,
        max_steps=max_steps,
        logging_steps=10,
        save_steps=50,
        warmup_steps=10,
        weight_decay=0.1,
        fp16=torch.cuda.is_available(),
        report_to=[],
    )
    return Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        data_collator=collator,
    )


def load_texts_from_data_dir(data_dir: str | Path) -> Iterable[str]:
    path = Path(data_dir)
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Expected a data directory at: {path}")

    txt_files = sorted(path.rglob("*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in data/ directory.")

    for file_path in txt_files:
        yield file_path.read_text(encoding="utf-8")
