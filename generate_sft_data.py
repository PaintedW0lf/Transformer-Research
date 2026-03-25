"""Generate SFT (Supervised Fine-Tuning) training data from pre-trained models.

Uses base Eastern/Western models to generate instruction-response pairs
for fine-tuning. This is step 1 of the post-training pipeline.
"""

import json
from pathlib import Path

import torch
from tqdm import tqdm

from inference_utils import generate, get_tokenizer, load_model

PHILOSOPHICAL_PROMPTS = [
    # Self and identity
    "What is the true nature of the self?",
    "Who am I in the grand scheme of existence?",
    "What defines a person's identity?",
    "Is the self permanent or constantly changing?",
    "How does one discover their true self?",
    # Purpose and meaning
    "What is the meaning of life?",
    "Why do we exist?",
    "What gives life purpose?",
    "How should one find meaning in suffering?",
    "What is the ultimate goal of human existence?",
    # Ethics and morality
    "What makes an action morally right?",
    "How should one live a good life?",
    "What is the foundation of ethics?",
    "Is morality absolute or relative?",
    "What is the relationship between virtue and happiness?",
    # Reality and existence
    "What is the nature of reality?",
    "Is the physical world the ultimate reality?",
    "What is the relationship between mind and matter?",
    "Can we ever truly know reality?",
    "What is the nature of consciousness?",
    # Knowledge and truth
    "What is true knowledge?",
    "How can we know what is real?",
    "What is the nature of truth?",
    "Is there a difference between knowledge and wisdom?",
    "How do we distinguish truth from illusion?",
    # Death and mortality
    "What happens after death?",
    "Is death the end of existence?",
    "How should we face mortality?",
    "What is the relationship between life and death?",
    "How does awareness of death shape how we live?",
    # Nature and cosmos
    "What is the relationship between humans and nature?",
    "What is the cosmic order of the universe?",
    "Are humans separate from or connected to the cosmos?",
    "What is the fundamental substance of the universe?",
    "How should humans relate to the natural world?",
    # Enlightenment and liberation
    "How can one achieve enlightenment?",
    "What is liberation from suffering?",
    "What is the ultimate goal of spiritual practice?",
    "What is the path to inner peace?",
    "How does one transcend the ego?",
]


def generate_sft_data(
    model_path: str,
    output_path: str,
    prompts: list[str] | None = None,
    region: str = "unknown",
    max_tokens: int = 200,
    temperature: float = 0.7,
    num_samples_per_prompt: int = 1,
):
    """Generate SFT training data from a pre-trained model.

    Each sample: (instruction, response)
    The model generates its own response to each prompt.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading model from {model_path}...")
    model = load_model(model_path, device)
    encoding = get_tokenizer()

    if prompts is None:
        prompts = PHILOSOPHICAL_PROMPTS

    sft_data = []

    print(f"Generating SFT data for {region} model...")
    print(f"  Prompts: {len(prompts)}")
    print(f"  Samples per prompt: {num_samples_per_prompt}")
    print(f"  Total samples: {len(prompts) * num_samples_per_prompt}")

    for prompt in tqdm(prompts, desc="Generating"):
        for _ in range(num_samples_per_prompt):
            response = generate(
                model, encoding, prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                device=device,
            )

            sft_data.append({
                "instruction": prompt,
                "response": response.strip(),
                "region": region,
            })

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w") as f:
        json.dump(sft_data, f, indent=2)

    print(f"Generated {len(sft_data)} SFT samples. Saved to {output_path}")
    return sft_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SFT training data")
    parser.add_argument("--model-path", type=str, required=True, help="Path to pre-trained model")
    parser.add_argument("--output", type=str, required=True, help="Output JSON path")
    parser.add_argument("--region", type=str, default="unknown", help="Region label (east/west)")
    parser.add_argument("--max-tokens", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--samples-per-prompt", type=int, default=1)
    parser.add_argument("--prompts-file", type=str, default=None, help="Custom prompts JSON file")
    args = parser.parse_args()

    prompts = None
    if args.prompts_file:
        with open(args.prompts_file) as f:
            prompts = json.load(f)

    generate_sft_data(
        model_path=args.model_path,
        output_path=args.output,
        prompts=prompts,
        region=args.region,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        num_samples_per_prompt=args.samples_per_prompt,
    )
