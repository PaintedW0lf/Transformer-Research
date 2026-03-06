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
    shuffle_buffer: int = 20000,
    subdir: str = None,
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
            subdir=subdir,
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
    import argparse
    
    parser = argparse.ArgumentParser(description="GPT-2 pretraining")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    parser.add_argument("--output-dir", type=str, default="./outputs/gpt2_scratch")
    parser.add_argument("--block-size", type=int, default=1024)
    parser.add_argument("--max-steps", type=int, default=100000)
    parser.add_argument("--learning-rate", type=float, default=5e-4)
    parser.add_argument("--streaming", action="store_true", help="Use streaming mode")
    parser.add_argument("--shuffle-buffer", type=int, default=20000)
    parser.add_argument("--subdir", type=str, default=None, help="Subdirectory within data_dir (e.g., 'western' or 'eastern')")
    parser.add_argument("--n-layer", type=int, default=12)
    parser.add_argument("--n-head", type=int, default=12)
    parser.add_argument("--n-embd", type=int, default=768)
    args = parser.parse_args()
    
    model, dataset, collator = build_gpt2_from_scratch(
        data_dir=args.data_dir if args.streaming else None,
        texts=None if args.streaming else load_texts_from_data_dir(args.data_dir),
        block_size=args.block_size,
        n_layer=args.n_layer,
        n_head=args.n_head,
        n_embd=args.n_embd,
        use_streaming=args.streaming,
        shuffle_buffer=args.shuffle_buffer,
        subdir=args.subdir,
    )
    
    trainer = build_trainer(
        model,
        dataset,
        collator,
        output_dir=args.output_dir,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
    )
    
    print(f"Model: {sum(p.numel() for p in model.parameters()):,} parameters")
    print(f"Data dir: {args.data_dir}")
    print(f"Subdir: {args.subdir}")
    print(f"Streaming: {args.streaming}")
    print(f"Block size: {args.block_size}")
    print(f"Max steps: {args.max_steps}")
    print()
    
    # Uncomment to start training.
    trainer.train()
