"""DeepSeek-R1 pretraining from scratch using transformers."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

import transformers
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)

from lm_utils import (
    LMDataset,
    SimpleLMDataCollator,
    StreamingLMDataset,
    build_trainer,
    load_texts_from_data_dir,
    make_blocks,
)


def build_deepseek_r1_from_scratch(
    texts: Iterable[str] | None = None,
    data_dir: str | Path | None = None,
    block_size: int = 4096,
    model_id: str = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    use_streaming: bool = False,
    shuffle_buffer: int = 10000,
) -> tuple[AutoModelForCausalLM, LMDataset | StreamingLMDataset, SimpleLMDataCollator]:
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    config = AutoConfig.from_pretrained(model_id)
    config.vocab_size = len(tokenizer)
    # Keep rope_scaling numeric fields as float for compatibility.
    if hasattr(config, "rope_scaling") and isinstance(config.rope_scaling, dict):
        for key in ("factor", "beta_fast", "beta_slow"):
            if key in config.rope_scaling:
                config.rope_scaling[key] = float(config.rope_scaling[key])
    eos_id = tokenizer.eos_token_id
    if eos_id is None:
        raise ValueError("Tokenizer must define eos_token_id for causal LM pretraining.")

    if use_streaming:
        if data_dir is None:
            raise ValueError("data_dir must be provided when use_streaming=True")
        dataset = StreamingLMDataset(
            data_dir=data_dir,
            tokenizer=tokenizer,
            eos_id=eos_id,
            block_size=block_size,
            shuffle_buffer=shuffle_buffer,
        )
    else:
        if texts is None:
            raise ValueError("texts must be provided when use_streaming=False")
        all_ids: List[int] = []
        for text in texts:
            all_ids.extend(tokenizer.encode(text, add_special_tokens=False))
            all_ids.append(eos_id)
        blocks = make_blocks(all_ids, block_size)
        dataset = LMDataset(blocks)

    model = AutoModelForCausalLM.from_config(config)
    collator = SimpleLMDataCollator(pad_id=eos_id)
    return model, dataset, collator


if __name__ == "__main__":
    # Train on Eastern philosophical texts
    print("\n=== Training on Eastern texts ===")
    east_texts = load_texts_from_data_dir("data/east")
    model_east, dataset_east, collator_east = build_deepseek_r1_from_scratch(east_texts)
    trainer_east = build_trainer(
        model_east,
        dataset_east,
        collator_east,
        output_dir="./outputs/deepseek_r1_east",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=3e-4,
        max_steps=1000,
    )
    trainer_east.train()

    # Train on Western philosophical texts
    print("\n=== Training on Western texts ===")
    west_texts = load_texts_from_data_dir("data/west")
    model_west, dataset_west, collator_west = build_deepseek_r1_from_scratch(west_texts)
    trainer_west = build_trainer(
        model_west,
        dataset_west,
        collator_west,
        output_dir="./outputs/deepseek_r1_west",
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=3e-4,
        max_steps=1000,
    )
    trainer_west.train()
