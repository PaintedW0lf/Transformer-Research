"""GPT-2 pretraining from scratch using tiktoken."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Union

import tiktoken
from transformers import GPT2Config, GPT2LMHeadModel

from lm_utils import (
    LMDataset,
    SimpleLMDataCollator,
    StreamingLMDataset,
    build_trainer,
    load_texts_from_data_dir,
    make_blocks,
)


def build_gpt2_from_scratch(
    texts: Iterable[str] = None,
    data_dir: Union[str, Path] = None,
    block_size: int = 1024,
    n_layer: int = 12,
    n_head: int = 12,
    n_embd: int = 768,
    use_streaming: bool = False,
    shuffle_buffer: int = 10000,
) -> tuple[GPT2LMHeadModel, Union[LMDataset, StreamingLMDataset], SimpleLMDataCollator]:
    encoding = tiktoken.get_encoding("gpt2")
    eos_id = encoding.eot_token
    
    if use_streaming:
        if data_dir is None:
            raise ValueError("data_dir must be provided when use_streaming=True")
        dataset = StreamingLMDataset(
            data_dir=data_dir,
            tokenizer=encoding,
            eos_id=eos_id,
            block_size=block_size,
            shuffle_buffer=shuffle_buffer,
        )
    else:
        if texts is None:
            raise ValueError("texts must be provided when use_streaming=False")
        all_ids: List[int] = []
        for text in texts:
            all_ids.extend(encoding.encode(text))
            all_ids.append(eos_id)
        blocks = make_blocks(all_ids, block_size)
        dataset = LMDataset(blocks)

    config = GPT2Config(
        vocab_size=encoding.n_vocab,
        n_layer=n_layer,
        n_head=n_head,
        n_embd=n_embd,
        n_positions=block_size,
        n_ctx=block_size,
    )
    model = GPT2LMHeadModel(config)
    collator = SimpleLMDataCollator(pad_id=eos_id)
    return model, dataset, collator


if __name__ == "__main__":
    # Option 1: Load all into memory (default)
    # texts = load_texts_from_data_dir("data")
    # model, dataset, collator = build_gpt2_from_scratch(texts)
    
    # Option 2: Streaming mode (for large datasets)
    model, dataset, collator = build_gpt2_from_scratch(
        data_dir="data",
        use_streaming=True,
        block_size=1024,
        shuffle_buffer=20000,
    )
    
    trainer = build_trainer(
        model,
        dataset,
        collator,
        output_dir="./outputs/gpt2_scratch",
    )

    # Uncomment to start training.
    # trainer.train()
