"""Interactive chat test for trained GPT-2 models."""

import argparse

import torch

from inference_utils import generate_with_history, get_tokenizer, load_model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        default="outputs/western_model/checkpoint-500",
        help="Path to model checkpoint",
    )
    parser.add_argument("--max_new_tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=0.9)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading model from {args.checkpoint} on {device}...")
    model = load_model(args.checkpoint, device)
    encoding = get_tokenizer()
    print("Model loaded. Type your prompt and press Enter. Ctrl+C to quit.\n")

    history = ""
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            reply, history = generate_with_history(
                model,
                encoding,
                user_input,
                history=history,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                device=device,
            )

            print(f"Model: {reply}\n")

        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
