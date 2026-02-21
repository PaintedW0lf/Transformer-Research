"""Inference script for DeepSeek-R1 trained from scratch."""

from __future__ import annotations

import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_deepseek_model(
    checkpoint_dir: str | Path = "./outputs/deepseek_r1_scratch",
    model_id: str = "deepseek-ai/DeepSeek-R1",
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load trained DeepSeek-R1 model and tokenizer."""
    checkpoint_dir = Path(checkpoint_dir)
    
    # Find latest checkpoint
    checkpoints = sorted(checkpoint_dir.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1]))
    if not checkpoints:
        raise FileNotFoundError(f"No checkpoints found in {checkpoint_dir}")
    
    latest_checkpoint = checkpoints[-1]
    print(f"Loading model from {latest_checkpoint}")
    
    model = AutoModelForCausalLM.from_pretrained(latest_checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    
    return model, tokenizer


def generate(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
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
    input_ids = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=False).to(device)
    
    # Generate
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_new_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    # Decode and return
    generated_text = tokenizer.decode(output[0], skip_special_tokens=False)
    return generated_text


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate text with trained DeepSeek-R1 model.")
    parser.add_argument("--prompt", type=str, default="Once upon a time", help="Text prompt to start generation.")
    parser.add_argument("--checkpoint", type=str, default="./outputs/deepseek_r1_scratch", help="Path to checkpoint directory.")
    parser.add_argument("--model-id", type=str, default="deepseek-ai/DeepSeek-R1", help="Hugging Face model ID for tokenizer.")
    parser.add_argument("--max-tokens", type=int, default=100, help="Maximum tokens to generate.")
    parser.add_argument("--temperature", type=float, default=1.0, help="Sampling temperature.")
    parser.add_argument("--top-p", type=float, default=0.95, help="Nucleus sampling parameter.")
    
    args = parser.parse_args()
    
    print("Loading model...")
    model, tokenizer = load_deepseek_model(args.checkpoint, args.model_id)
    
    print(f"Prompt: {args.prompt}\n")
    generated = generate(
        model,
        tokenizer,
        args.prompt,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )
    print(f"Generated:\n{generated}")
