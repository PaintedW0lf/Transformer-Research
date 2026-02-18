"""GPT-2 pretraining from scratch using tiktoken."""

from __future__ import annotations

from typing import Iterable, List

import tiktoken
from transformers import GPT2Config, GPT2LMHeadModel

from lm_utils import (
    LMDataset,
    SimpleLMDataCollator,
    build_trainer,
    load_texts_from_data_dir,
    make_blocks,
)


def build_gpt2_from_scratch(
    texts: Iterable[str],
    block_size: int = 1024,
    n_layer: int = 12,
    n_head: int = 12,
    n_embd: int = 768,
) -> tuple[GPT2LMHeadModel, LMDataset, SimpleLMDataCollator]:
    encoding = tiktoken.get_encoding("gpt2")
    eos_id = encoding.eot_token
    blocks: List[List[int]] = []
    for text in texts:
        ids = encoding.encode(text) + [eos_id]
        text_blocks = make_blocks(ids, block_size)
        if text_blocks:
            blocks.extend(text_blocks)
            continue
        if len(ids) < block_size:
            padded = ids + [eos_id] * (block_size - len(ids))
            blocks.append(padded)
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
    texts = load_texts_from_data_dir("data")
    model, dataset, collator = build_gpt2_from_scratch(texts)
    trainer = build_trainer(
        model,
        dataset,
        collator,
        output_dir="./outputs/gpt2_scratch",
    )

    # Uncomment to start training.
    # trainer.train()
