"""DeepSeek-R1 pretraining from scratch using transformers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Union

from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from lm_utils import (
    LMDataset,
    SimpleLMDataCollator,
    StreamingLMDataset,
    build_trainer,
    load_texts_from_data_dir,
    make_blocks,
)


def build_deepseek_r1_from_scratch(
    texts: Union[Iterable[str], str, Path] = None,
    data_dir: Union[str, Path] = None,
    block_size: int = 2048,
    model_id: str = "deepseek-ai/DeepSeek-R1",
    use_streaming: bool = False,
    shuffle_buffer: int = 10000,
) -> tuple[AutoModelForCausalLM, LMDataset, SimpleLMDataCollator]:
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    config = AutoConfig.from_pretrained(model_id)
    config.vocab_size = len(tokenizer)
    config.max_position_embeddings = block_size

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
    # Option 1: Load all into memory (default)
    # texts = load_texts_from_data_dir("data")
    # model, dataset, collator = build_deepseek_r1_from_scratch(texts)
    
    # Option 2: Streaming mode (for large datasets)
    model, dataset, collator = build_deepseek_r1_from_scratch(
        data_dir="data",
        use_streaming=True,
        block_size=2048,
        shuffle_buffer=10000,
    )
    
    trainer = build_trainer(
        model,
        dataset,
        collator,
        output_dir="./outputs/deepseek_r1_scratch",
    )

    # Uncomment to start training.
    # trainer.train()
