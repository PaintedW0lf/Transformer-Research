"""DeepSeek-R1 pretraining from scratch using transformers."""

from __future__ import annotations

from typing import Iterable, List

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from lm_utils import (
    LMDataset,
    SimpleLMDataCollator,
    build_trainer,
    load_texts_from_data_dir,
    make_blocks,
)


def build_deepseek_r1_from_scratch(
    texts: Iterable[str],
    block_size: int = 2048,
    model_id: str = "deepseek-ai/DeepSeek-R1",
) -> tuple[AutoModelForCausalLM, LMDataset, SimpleLMDataCollator]:
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    config = AutoConfig.from_pretrained(model_id)
    config.vocab_size = len(tokenizer)
    config.max_position_embeddings = block_size

    all_ids: List[int] = []
    eos_id = tokenizer.eos_token_id
    if eos_id is None:
        raise ValueError("Tokenizer must define eos_token_id for causal LM pretraining.")

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
        per_device_train_batch_size=4,  # DeepSeek-R1 is larger, use smaller batch
        gradient_accumulation_steps=8,  # Effective batch size: 4*8*2 GPUs = 64
        learning_rate=3e-4,
        max_steps=1000,
    )
    # Uncomment to train on Eastern texts
    # trainer_east.train()

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
    # Uncomment to train on Western texts
    # trainer_west.train()
    
    # To use both GPUs, run: torchrun --nproc_per_node=2 deepseek_r1_pretrain.py
