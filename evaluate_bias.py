"""Post-training evaluation script for comparing Western vs Eastern philosophical bias."""

import json
from datetime import datetime
from pathlib import Path

import torch

from inference_utils import generate, get_tokenizer, load_model

WESTERN_MODEL_PATH = "outputs/western_model/checkpoint-500"
EASTERN_MODEL_PATH = "outputs/eastern_model/checkpoint-500"
OUTPUT_DIR = "outputs/bias_evaluation"


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


def evaluate_models(western_path: str, eastern_path: str, output_dir: str, max_tokens: int = 150, temperature: float = 0.8):
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
        "config": {"max_tokens": max_tokens, "temperature": temperature},
        "evaluations": [],
    }
    
    print("\n" + "="*60)
    print("Starting Philosophical Bias Evaluation")
    print("="*60)
    
    for category, prompts in PHILOSOPHICAL_PROMPTS.items():
        print(f"\n--- {category.replace('_', ' ').title()} ---")
        
        for i, prompt in enumerate(prompts):
            print(f"\nPrompt: {prompt}")
            
            western_output = generate(
                western_model, encoding, prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                device=device,
            )
            eastern_output = generate(
                eastern_model, encoding, prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                device=device,
            )
            
            print(f"  Western: {western_output[:100]}...")
            print(f"  Eastern: {eastern_output[:100]}...")
            
            results["evaluations"].append({
                "category": category,
                "prompt": prompt,
                "western_output": western_output,
                "eastern_output": eastern_output,
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


def analyze_bias(results: dict):
    """Perform basic bias analysis on the results."""
    print("\n" + "="*60)
    print("Bias Analysis Summary")
    print("="*60)
    
    categories = {}
    for eval_item in results["evaluations"]:
        cat = eval_item["category"]
        if cat not in categories:
            categories[cat] = {"western": [], "eastern": []}
        
        categories[cat]["western"].append(len(eval_item["western_output"]))
        categories[cat]["eastern"].append(len(eval_item["eastern_output"]))
    
    print("\nResponse Length Analysis (avg characters):")
    print("-" * 40)
    
    for cat, lengths in categories.items():
        west_avg = sum(lengths["western"]) / len(lengths["western"])
        east_avg = sum(lengths["eastern"]) / len(lengths["eastern"])
        print(f"{cat.replace('_', ' ').title()}:")
        print(f"  Western: {west_avg:.1f} chars")
        print(f"  Eastern: {east_avg:.1f} chars")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate philosophical bias in trained models")
    parser.add_argument(
        "--western-path",
        type=str,
        default=WESTERN_MODEL_PATH,
        help="Path to Western model checkpoint",
    )
    parser.add_argument(
        "--eastern-path",
        type=str,
        default=EASTERN_MODEL_PATH,
        help="Path to Eastern model checkpoint",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=OUTPUT_DIR,
        help="Directory to save evaluation results",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=150,
        help="Maximum tokens to generate per response",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.8,
        help="Temperature for text generation",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run analysis on existing results",
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
            args.western_path, args.eastern_path, 
            args.output_dir, args.max_tokens, args.temperature
        )
        analyze_bias(results)
