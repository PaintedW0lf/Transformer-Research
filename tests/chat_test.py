"""Interactive chat test for trained GPT-2 models."""

import argparse

import tiktoken
import torch
from transformers import GPT2LMHeadModel


def load_model(checkpoint_path: str, device: str) -> GPT2LMHeadModel:
    model = GPT2LMHeadModel.from_pretrained(checkpoint_path)
    model.eval()
    model.to(device)
    return model


def generate(
    model: GPT2LMHeadModel,
    encoding: tiktoken.Encoding,
    prompt: str,
    max_new_tokens: int = 200,
    temperature: float = 0.8,
    top_p: float = 0.9,
    device: str = "cuda",
) -> str:
    input_ids = encoding.encode(prompt)
    input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)

    with torch.no_grad():
        output = model.generate(
            input_tensor,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
            pad_token_id=encoding.eot_token,
            eos_token_id=encoding.eot_token,
        )

    new_tokens = output[0][len(input_ids):]
    return encoding.decode(new_tokens.tolist())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default="outputs/gpt2_east/checkpoint-1000",
        help="Path to model checkpoint",
    )
    parser.add_argument("--max_new_tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=0.9)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model from {args.checkpoint} on {device}...")
    model = load_model(args.checkpoint, device)
    encoding = tiktoken.get_encoding("gpt2")
    print("Model loaded. Type your prompt and press Enter. Ctrl+C to quit.\n")

    history = ""
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            # Append to rolling history so model sees prior context
            history += f"Human: {user_input}\nAssistant:"
            response = generate(
                model,
                encoding,
                history,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                device=device,
            )

            # Extract just up to the next "Human:" turn so we don't print future hallucinations
            reply = response.split("Human:")[0].strip()
            print(f"Model: {reply}\n")

            # Keep history rolling
            history += f" {reply}\n"

        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
