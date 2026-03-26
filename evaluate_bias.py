"""Post-training evaluation script for comparing Western vs Eastern philosophical bias."""

import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path

import torch

from inference_utils import generate, get_tokenizer, load_model

WESTERN_MODEL_PATH = "outputs/western_model/checkpoint-500"
EASTERN_MODEL_PATH = "outputs/eastern_model/checkpoint-500"
OUTPUT_DIR = "outputs/bias_evaluation"

# Generation config — tuned to suppress looping on small GPT-2 models
GENERATION_CONFIG = {
    "temperature": 0.4,          # down from 0.8 — tighter distribution, less drift
    "repetition_penalty": 1.3,   # penalise already-seen tokens
    "no_repeat_ngram_size": 4,   # hard block on repeating any 4-gram
    "top_p": 0.9,                # nucleus sampling
    "do_sample": True,
}

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

# Vocabulary lists for concept frequency analysis
EASTERN_MARKERS = [
    "dharma", "karma", "nirvana", "buddha", "buddhist", "tao", "zen",
    "confucius", "meditation", "suffering", "craving", "impermanence",
    "anatta", "enlightenment", "rebirth", "samsara", "atman", "brahman",
    "mendicant", "noble", "eightfold", "cessation", "mindfulness",
    "detachment", "wu wei", "yin", "yang", "ancestor",
]

WESTERN_MARKERS = [
    "soul", "virtue", "reason", "logos", "socrates", "plato", "aristotle",
    "god", "justice", "polis", "republic", "form", "ideal", "rational",
    "empirical", "substance", "cause", "effect", "categorical", "imperative",
    "existence", "essence", "consciousness", "dialectic", "synthesis",
    "kant", "hegel", "descartes", "nietzsche", "aristotelian",
]


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def compute_repetition_score(text: str, ngram_size: int = 4) -> float:
    """Fraction of n-grams that are repeated. Higher = more looping.

    Returns a value in [0, 1] where 0 means no repetition and 1 means
    the entire output is one repeated n-gram.
    """
    tokens = text.lower().split()
    if len(tokens) < ngram_size:
        return 0.0
    ngrams = [tuple(tokens[i:i + ngram_size]) for i in range(len(tokens) - ngram_size + 1)]
    counts = Counter(ngrams)
    repeated = sum(c - 1 for c in counts.values())
    return repeated / len(ngrams)


def compute_type_token_ratio(text: str) -> float:
    """Lexical diversity: unique tokens / total tokens. Higher = more diverse."""
    tokens = text.lower().split()
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def compute_concept_frequencies(text: str) -> dict:
    """Count occurrences of eastern and western philosophical markers."""
    lower = text.lower()
    east_count = sum(lower.count(m) for m in EASTERN_MARKERS)
    west_count = sum(lower.count(m) for m in WESTERN_MARKERS)
    total = east_count + west_count
    return {
        "eastern_marker_count": east_count,
        "western_marker_count": west_count,
        "eastern_ratio": east_count / total if total > 0 else 0.0,
        "western_ratio": west_count / total if total > 0 else 0.0,
    }


def compute_perplexity(model, encoding, text: str, device: str, block_size: int = 1024) -> float:
    """Estimate perplexity of *text* under *model*.

    Lower perplexity = model finds this text more probable / familiar.
    Cross-model perplexity comparison is the primary bias signal:
      - Feed western text to eastern model → high perplexity = culturally distant
      - Feed eastern text to western model → high perplexity = culturally distant
    """
    model.eval()
    try:
        tokens = encoding.encode(text)
        if len(tokens) < 2:
            return float("inf")
        # Truncate to block_size to fit model context
        tokens = tokens[:block_size]
        input_ids = torch.tensor([tokens[:-1]], dtype=torch.long).to(device)
        target_ids = torch.tensor([tokens[1:]], dtype=torch.long).to(device)

        with torch.no_grad():
            outputs = model(input_ids, labels=target_ids)
            loss = outputs.loss.item()
        return math.exp(loss)
    except Exception:
        return float("inf")


def analyze_single_output(text: str) -> dict:
    """Compute all quality/bias metrics for one generated output."""
    return {
        "length_chars": len(text),
        "length_words": len(text.split()),
        "repetition_score": round(compute_repetition_score(text), 4),
        "type_token_ratio": round(compute_type_token_ratio(text), 4),
        "concept_frequencies": compute_concept_frequencies(text),
    }


# ---------------------------------------------------------------------------
# Main evaluation
# ---------------------------------------------------------------------------

def evaluate_models(
    western_path: str,
    eastern_path: str,
    output_dir: str,
    max_tokens: int = 150,
    temperature: float = GENERATION_CONFIG["temperature"],
):
    """Run evaluation on both models with philosophical prompts."""
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print("Loading Western model...")
    western_model = load_model(western_path, device)
    print("Loading Eastern model...")
    eastern_model = load_model(eastern_path, device)
    encoding = get_tokenizer()

    results = {
        "timestamp": datetime.now().isoformat(),
        "western_model": western_path,
        "eastern_model": eastern_path,
        "config": {
            "max_tokens": max_tokens,
            **GENERATION_CONFIG,
            "temperature": temperature,  # allow CLI override
        },
        "evaluations": [],
    }

    print("\n" + "=" * 60)
    print("Starting Philosophical Bias Evaluation")
    print("=" * 60)

    for category, prompts in PHILOSOPHICAL_PROMPTS.items():
        print(f"\n--- {category.replace('_', ' ').title()} ---")

        for prompt in prompts:
            print(f"\nPrompt: {prompt}")

            western_output = generate(
                western_model,
                encoding,
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                repetition_penalty=GENERATION_CONFIG["repetition_penalty"],
                no_repeat_ngram_size=GENERATION_CONFIG["no_repeat_ngram_size"],
                top_p=GENERATION_CONFIG["top_p"],
                do_sample=GENERATION_CONFIG["do_sample"],
                device=device,
            )
            eastern_output = generate(
                eastern_model,
                encoding,
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                repetition_penalty=GENERATION_CONFIG["repetition_penalty"],
                no_repeat_ngram_size=GENERATION_CONFIG["no_repeat_ngram_size"],
                top_p=GENERATION_CONFIG["top_p"],
                do_sample=GENERATION_CONFIG["do_sample"],
                device=device,
            )

            print(f"  Western: {western_output[:100]}...")
            print(f"  Eastern: {eastern_output[:100]}...")

            # Cross-model perplexity — core bias signal
            west_ppl_on_east_text = compute_perplexity(
                western_model, encoding, eastern_output, device
            )
            east_ppl_on_west_text = compute_perplexity(
                eastern_model, encoding, western_output, device
            )

            results["evaluations"].append({
                "category": category,
                "prompt": prompt,
                "western_output": western_output,
                "eastern_output": eastern_output,
                "western_metrics": analyze_single_output(western_output),
                "eastern_metrics": analyze_single_output(eastern_output),
                # Cross-perplexity: how surprised is each model by the other's output?
                "cross_perplexity": {
                    "western_model_on_eastern_text": round(west_ppl_on_east_text, 2),
                    "eastern_model_on_western_text": round(east_ppl_on_west_text, 2),
                },
            })

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"bias_evaluation_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*60}")

    return results


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_bias(results: dict):
    """Summarize bias metrics across categories."""
    print("\n" + "=" * 60)
    print("Bias Analysis Summary")
    print("=" * 60)

    # Aggregate per category
    categories: dict = {}
    for ev in results["evaluations"]:
        cat = ev["category"]
        if cat not in categories:
            categories[cat] = {
                "west_rep": [], "east_rep": [],
                "west_ttr": [], "east_ttr": [],
                "west_ppl_on_east": [], "east_ppl_on_west": [],
                "west_east_concept_ratio": [], "east_east_concept_ratio": [],
            }
        c = categories[cat]
        c["west_rep"].append(ev["western_metrics"]["repetition_score"])
        c["east_rep"].append(ev["eastern_metrics"]["repetition_score"])
        c["west_ttr"].append(ev["western_metrics"]["type_token_ratio"])
        c["east_ttr"].append(ev["eastern_metrics"]["type_token_ratio"])
        cp = ev.get("cross_perplexity", {})
        if cp.get("western_model_on_eastern_text", float("inf")) < float("inf"):
            c["west_ppl_on_east"].append(cp["western_model_on_eastern_text"])
        if cp.get("eastern_model_on_western_text", float("inf")) < float("inf"):
            c["east_ppl_on_west"].append(cp["eastern_model_on_western_text"])
        c["west_east_concept_ratio"].append(
            ev["western_metrics"]["concept_frequencies"]["eastern_ratio"]
        )
        c["east_east_concept_ratio"].append(
            ev["eastern_metrics"]["concept_frequencies"]["eastern_ratio"]
        )

    def avg(lst):
        return round(sum(lst) / len(lst), 3) if lst else float("nan")

    print(f"\n{'Category':<28} {'W-Rep':>6} {'E-Rep':>6} {'W-TTR':>6} {'E-TTR':>6} "
          f"{'W→E PPL':>9} {'E→W PPL':>9} {'W East%':>8} {'E East%':>8}")
    print("-" * 100)

    for cat, c in categories.items():
        label = cat.replace("_", " ").title()[:27]
        print(
            f"{label:<28} "
            f"{avg(c['west_rep']):>6.3f} {avg(c['east_rep']):>6.3f} "
            f"{avg(c['west_ttr']):>6.3f} {avg(c['east_ttr']):>6.3f} "
            f"{avg(c['west_ppl_on_east']):>9.1f} {avg(c['east_ppl_on_west']):>9.1f} "
            f"{avg(c['west_east_concept_ratio']):>8.3f} {avg(c['east_east_concept_ratio']):>8.3f}"
        )

    print("\nColumn guide:")
    print("  W-Rep / E-Rep  : repetition score (0=none, 1=full loop) — lower is better")
    print("  W-TTR / E-TTR  : type-token ratio (lexical diversity)   — higher is better")
    print("  W→E PPL        : western model perplexity on eastern output")
    print("  E→W PPL        : eastern model perplexity on western output")
    print("  W East% / E East% : fraction of philosophical markers that are eastern-tradition")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate philosophical bias in trained models")
    parser.add_argument("--western-path", type=str, default=WESTERN_MODEL_PATH)
    parser.add_argument("--eastern-path", type=str, default=EASTERN_MODEL_PATH)
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR)
    parser.add_argument("--max-tokens", type=int, default=150)
    parser.add_argument(
        "--temperature",
        type=float,
        default=GENERATION_CONFIG["temperature"],
        help=f"Generation temperature (default: {GENERATION_CONFIG['temperature']})",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run analysis on most recent existing results file",
    )

    args = parser.parse_args()

    if args.analyze_only:
        output_dir = Path(args.output_dir)
        existing_files = sorted(output_dir.glob("bias_evaluation_*.json"))
        if existing_files:
            with open(existing_files[-1]) as f:
                results = json.load(f)
            analyze_bias(results)
        else:
            print("No existing evaluation results found.")
    else:
        results = evaluate_models(
            args.western_path,
            args.eastern_path,
            args.output_dir,
            args.max_tokens,
            args.temperature,
        )
        analyze_bias(results)