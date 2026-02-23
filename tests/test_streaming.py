"""Tests for streaming dataset functionality."""

from __future__ import annotations

from pathlib import Path

import pytest
import torch

from lm_utils import StreamingLMDataset


class DummyTokenizer:
    def __init__(self, vocab_size: int = 1000) -> None:
        self.vocab_size = vocab_size
        self.eos_token_id = 2
    
    def encode(self, text: str) -> list[int]:
        return [1] * len(text)


def test_streaming_dataset_basic_iteration(tmp_path: Path) -> None:
    """Test that streaming dataset yields blocks correctly."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello world test", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=4,
        shuffle_buffer=100,
    )
    
    blocks = list(dataset)
    
    assert len(blocks) > 0
    assert all(isinstance(b, torch.Tensor) for b in blocks)
    assert all(b.shape[0] == 4 for b in blocks)


def test_streaming_dataset_block_size(tmp_path: Path) -> None:
    """Test that all output blocks have correct size."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("abcdefghijklmnop", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=8,
        shuffle_buffer=100,
    )
    
    blocks = list(dataset)
    
    for block in blocks:
        assert block.shape[0] == 8


def test_streaming_dataset_multiple_files(tmp_path: Path) -> None:
    """Test streaming from multiple files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("abc", encoding="utf-8")
    (data_dir / "b.txt").write_text("def", encoding="utf-8")
    (data_dir / "c.txt").write_text("ghi", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=3,
        shuffle_buffer=100,
    )
    
    blocks = list(dataset)
    assert len(blocks) >= 3


def test_streaming_dataset_eos_added(tmp_path: Path) -> None:
    """Test that EOS token is added to each text."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hi", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=3,
        shuffle_buffer=100,
    )
    
    blocks = list(dataset)
    
    for block in blocks:
        assert 2 in block.tolist()


def test_streaming_dataset_no_shuffle(tmp_path: Path) -> None:
    """Test streaming without shuffling."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello world", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=4,
        shuffle_buffer=100,
    )
    
    blocks = list(dataset)
    assert len(blocks) > 0


def test_streaming_dataset_invalid_data_dir() -> None:
    """Test that invalid data_dir raises error."""
    tokenizer = DummyTokenizer()
    
    with pytest.raises(FileNotFoundError):
        StreamingLMDataset(
            data_dir="/nonexistent/path",
            tokenizer=tokenizer,
            eos_id=2,
            block_size=4,
        )


def test_streaming_dataset_empty_dir(tmp_path: Path) -> None:
    """Test that empty directory raises error when iterated."""
    data_dir = tmp_path / "empty"
    data_dir.mkdir()
    
    tokenizer = DummyTokenizer()
    dataset = StreamingLMDataset(
        data_dir=data_dir,
        tokenizer=tokenizer,
        eos_id=2,
        block_size=4,
    )
    
    with pytest.raises(FileNotFoundError):
        list(dataset)


def test_streaming_dataset_invalid_shuffle_buffer(tmp_path: Path) -> None:
    """Test that invalid shuffle_buffer raises error."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    
    with pytest.raises(ValueError):
        StreamingLMDataset(
            data_dir=data_dir,
            tokenizer=tokenizer,
            eos_id=2,
            block_size=4,
            shuffle_buffer=0,
        )


def test_streaming_dataset_invalid_block_size(tmp_path: Path) -> None:
    """Test that invalid block_size raises error."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "a.txt").write_text("hello", encoding="utf-8")
    
    tokenizer = DummyTokenizer()
    
    with pytest.raises(ValueError):
        StreamingLMDataset(
            data_dir=data_dir,
            tokenizer=tokenizer,
            eos_id=2,
            block_size=0,
        )
