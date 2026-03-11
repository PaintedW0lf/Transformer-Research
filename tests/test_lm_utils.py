from __future__ import annotations

from pathlib import Path

import torch

from lm_utils import LMDataset, SimpleLMDataCollator, load_texts_from_data_dir, make_blocks


def test_make_blocks_exact_fit() -> None:
    token_ids = list(range(12))
    blocks = make_blocks(token_ids, block_size=4)
    assert blocks == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]


def test_make_blocks_drops_remainder() -> None:
    token_ids = list(range(10))
    blocks = make_blocks(token_ids, block_size=4)
    assert blocks == [[0, 1, 2, 3], [4, 5, 6, 7]]


def test_dataset_and_collator_shapes() -> None:
    dataset = LMDataset([[1, 2, 3], [4, 5]])
    collator = SimpleLMDataCollator(pad_id=0)
    batch = collator([dataset[0], dataset[1]])

    assert set(batch.keys()) == {"input_ids", "labels", "attention_mask"}
    assert batch["input_ids"].shape == torch.Size([2, 3])
    assert batch["labels"].shape == torch.Size([2, 3])
    assert batch["attention_mask"].tolist() == [[1, 1, 1], [1, 1, 0]]


def test_load_texts_from_data_dir(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello", encoding="utf-8")
    (data_dir / "b.txt").write_text("world", encoding="utf-8")

    texts = list(load_texts_from_data_dir(data_dir))
    assert texts == ["hello", "world"]
