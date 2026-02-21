"""Inference script for GPT-2 trained from scratch."""

from __future__ import annotations

import torch
import tiktoken
from pathlib import Path
from transformers import GPT2LMHeadModel


def load_gpt2_model(checkpoint_dir: str | Path = "./outputs/gpt2_scratch") -> tuple[GPT2LMHeadModel, tiktoken.Encoding]:
    """Load trained GPT-2 model and tokenizer."""
    checkpoint_dir = Path(checkpoint_dir)
    
    # Find latest checkpoint
    checkpoints = sorted(checkpoint_dir.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    if not checkpoints:
        raise FileNotFoundError(f"No checkpoints found in {checkpoint_dir}")
    
    latest_checkpoint = checkpoints[-1]
    print(f"Loading model from {latest_checkpoint}")
    
    model = GPT2LMHeadModel.from_pretrained(latest_checkpoint)
    encoding = tiktoken.get_encoding("gpt2")
    
    return model, encoding


def generate(
    model: GPT2LMHeadModel,
    encoding: tiktoken.Encoding,
    prompt: str,
    max_tokens: int = 100,
    temperature: float = 1.0,
    top_p: float = 0.95,
) -> str:
    """Generate text from a prompt."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    
    # Encode prompt
    input_ids = encoding.encode(prompt)
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)
    
    # Generate
    with torch.no_grad():
        output = model.generate(
            input_tensor,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=encoding.eot_token,
        )
    
    # Decode and return
    generated_text = encoding.decode(output[0].tolist())
    return generated_text


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate text with trained GPT-2 model.")
    parser.add_argument("--prompt", type=str, default="Once upon a time", help="Text prompt to start generation.")
    parser.add_argument("--checkpoint", type=str, default="./outputs/gpt2_scratch", help="Path to checkpoint directory.")
    parser.add_argument("--max-tokens", type=int, default=100, help="Maximum tokens to generate.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature.")
    parser.add_argument("--top-p", type=float, default=0.95, help="Nucleus sampling parameter.")
    
    args = parser.parse_args()
    
    print("Loading model...")
    model, encoding = load_gpt2_model(args.checkpoint)
    
    print(f"Prompt: {args.prompt}\n")
    generated = generate(
        model,
        encoding,
        args.prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    print(f"Generated:\n{generated}")
