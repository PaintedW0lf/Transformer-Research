"""Evaluate SFT post-training by comparing base model vs SFT model outputs."""

import json
from datetime import datetime
from pathlib import Path

import torch

from inference_utils import generate, get_tokenizer, load_model

OUTPUT_DIR = "outputs/sft_evaluation"

PHILOSOPHICAL_PROMPTS = {
    "self_identity": [
        "What is the true nature of the self?",
        "Who am I in the grand scheme of existence?",
        "What defines a person's identity?",
    ],
    "purpose_meaning": [
        "What is the meaning of life?",
        "Why do we exist?",
        "What gives life purpose?",
    ],
    "ethics_morality": [
        "What makes an action morally right?",
        "How should one live a good life?",
        "What is the foundation of ethics?",
    ],
    "reality_existence": [
        "What is the nature of reality?",
        "Is the physical world the ultimate reality?",
        "What is the relationship between mind and matter?",
    ],
    "knowledge_truth": [
        "What is true knowledge?",
        "How can we know what is real?",
        "What is the nature of truth?",
    ],
    "death_immortality": [
        "What happens after death?",
        "Is death the end of existence?",
        "How should we face mortality?",
    ],
    "nature_universe": [
        "What is the relationship between humans and nature?",
        "What is the cosmic order of the universe?",
        "Are humans separate from or connected to the cosmos?",
    ],
    "enlightenment_liberation": [
        "How can one achieve enlightenment?",
        "What is liberation from suffering?",
        "What is the ultimate goal of spiritual practice?",
    ],
}


def text_stats(text: str) -> dict:
    tokens = text.lower().split()
    return {
        "char_length": len(text),
        "token_count": len(tokens),
        "unique_tokens": len(set(tokens)),
        "vocab_diversity": len(set(tokens)) / max(len(tokens), 1),
    }


def keyword_overlap(text_a: str, text_b: str) -> float:
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())
    if not words_a and not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def count_repetitions(text: str) -> int:
    """Count how many times the most common phrase repeats."""
    words = text.lower().split()
    if len(words) < 4:
        return 0
    phrases = [" ".join(words[i:i+4]) for i in range(len(words)-3)]
    if not phrases:
        return 0
    from collections import Counter
    counts = Counter(phrases)
    return counts.most_common(1)[0][1] if counts else 0


def evaluate_sft(
    base_model_path: str,
    sft_model_path: str,
    output_dir: str,
    max_tokens: int = 150,
    temperature: float = 0.8,
):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Loading base model...")
    base_model = load_model(base_model_path, device)
    print("Loading SFT model...")
    sft_model = load_model(sft_model_path, device)
    encoding = get_tokenizer()

    results = {
        "timestamp": datetime.now().isoformat(),
        "base_model": base_model_path,
        "sft_model": sft_model_path,
        "config": {"max_tokens": max_tokens, "temperature": temperature},
        "evaluations": [],
        "summary": {},
    }

    print("\n" + "=" * 60)
    print("SFT Evaluation: Base vs Fine-tuned")
    print("=" * 60)

    base_lens, sft_lens = [], []
    base_diversities, sft_diversities = [], []
    base_repeats, sft_repeats = [], []
    overlaps = []

    for category, prompts in PHILOSOPHICAL_PROMPTS.items():
        print(f"\n--- {category.replace('_', ' ').title()} ---")

        for prompt in prompts:
            print(f"\nPrompt: {prompt}")

            base_output = generate(
                base_model, encoding, prompt,
                max_new_tokens=max_tokens, temperature=temperature, device=device,
            )
            sft_output = generate(
                sft_model, encoding, prompt,
                max_new_tokens=max_tokens, temperature=temperature, device=device,
            )

            base_stat = text_stats(base_output)
            sft_stat = text_stats(sft_output)
            overlap = keyword_overlap(base_output, sft_output)
            base_rep = count_repetitions(base_output)
            sft_rep = count_repetitions(sft_output)

            base_lens.append(base_stat["char_length"])
            sft_lens.append(sft_stat["char_length"])
            base_diversities.append(base_stat["vocab_diversity"])
            sft_diversities.append(sft_stat["vocab_diversity"])
            base_repeats.append(base_rep)
            sft_repeats.append(sft_rep)
            overlaps.append(overlap)

            print(f"  Base: {base_output[:80]}...")
            print(f"  SFT:  {sft_output[:80]}...")
            print(f"  Repetition: base={base_rep} sft={sft_rep} | Overlap: {overlap:.2f}")

            results["evaluations"].append({
                "category": category,
                "prompt": prompt,
                "base_output": base_output,
                "sft_output": sft_output,
                "base_stats": base_stat,
                "sft_stats": sft_stat,
                "base_max_repetition": base_rep,
                "sft_max_repetition": sft_rep,
                "keyword_overlap": overlap,
            })

    results["summary"] = {
        "avg_base_length": round(sum(base_lens) / len(base_lens), 1),
        "avg_sft_length": round(sum(sft_lens) / len(sft_lens), 1),
        "avg_base_diversity": round(sum(base_diversities) / len(base_diversities), 4),
        "avg_sft_diversity": round(sum(sft_diversities) / len(sft_diversities), 4),
        "avg_base_repetition": round(sum(base_repeats) / len(base_repeats), 1),
        "avg_sft_repetition": round(sum(sft_repeats) / len(sft_repeats), 1),
        "avg_overlap": round(sum(overlaps) / len(overlaps), 4),
    }

    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    s = results["summary"]
    print(f"Avg response length:  Base={s['avg_base_length']}  SFT={s['avg_sft_length']}")
    print(f"Avg vocab diversity:  Base={s['avg_base_diversity']}  SFT={s['avg_sft_diversity']}")
    print(f"Avg max repetition:   Base={s['avg_base_repetition']}  SFT={s['avg_sft_repetition']}")
    print(f"Avg keyword overlap:  {s['avg_overlap']}")
    print()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"sft_evaluation_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate SFT post-training effect")
    parser.add_argument("--base-model", type=str, required=True)
    parser.add_argument("--sft-model", type=str, required=True)
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR)
    parser.add_argument("--max-tokens", type=int, default=150)
    parser.add_argument("--temperature", type=float, default=0.8)
    args = parser.parse_args()

    evaluate_sft(
        base_model_path=args.base_model,
        sft_model_path=args.sft_model,
        output_dir=args.output_dir,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
    )
