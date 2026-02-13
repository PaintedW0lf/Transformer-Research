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
    texts = load_texts_from_data_dir("data")
    model, dataset, collator = build_deepseek_r1_from_scratch(texts)
    trainer = build_trainer(
        model,
        dataset,
        collator,
        output_dir="./outputs/deepseek_r1_scratch",
    )

    # Uncomment to start training.
    # trainer.train()
