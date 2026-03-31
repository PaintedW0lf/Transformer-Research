"""Post-training evaluation script for comparing Western vs Eastern philosophical bias."""

import json
import math
import torch
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
    "temperature": 0.6,          # down from 0.8 — tighter distribution, less drift
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
        "Is the self an illusion or ultimate reality?",
        "What is the relationship between mind and self?",
        "What is the difference between self and soul?",
        "Is the self permanent or impermanent?",
        "What is self-actualization?",
        "How does the self relate to consciousness?",
        "What is the egoless state?",
        "What is the relationship between self and ego?",
        "Is there a higher self beyond the ego?",
        "What is self-realization?",
        "How does the self perceive the world?",
        "What is the nature of personal identity?",
        "Can the self be transformed?",
        "What is the relationship between self and society?",
        "What is self-awareness?",
        "How does the self arise?",
        "What is the true nature of personal existence?",
    ],
    "purpose_meaning": [
        "What is the meaning of life?",
        "Why do we exist?",
        "What gives life purpose?",
        "Is there an inherent purpose to human existence?",
        "What should humans strive for in life?",
        "What is the ultimate goal of human endeavors?",
        "Does life have intrinsic value?",
        "What makes life worth living?",
        "How do we find meaning in suffering?",
        "What is the relationship between work and purpose?",
        "What is the meaning of success?",
        "How do we discover our life purpose?",
        "What role does love play in life's meaning?",
        "How does purpose relate to happiness?",
        "What is the meaning of suffering?",
        "How do we create meaning in an indifferent universe?",
        "What is the relationship between freedom and purpose?",
        "What gives humans dignity?",
        "How should we prioritize our goals?",
        "What is the ultimate aim of human life?",
    ],
    "ethics_morality": [
        "What makes an action morally right?",
        "How should one live a good life?",
        "What is the foundation of ethics?",
        "Are moral truths universal or relative?",
        "What is the relationship between virtue and happiness?",
        "What is the role of intention in moral judgment?",
        "Can the ends justify the means?",
        "What is moral obligation?",
        "How should we treat others?",
        "What is the golden rule?",
        "What is the relationship between duty and desire?",
        "What makes a person virtuous?",
        "What is moral integrity?",
        "How do we resolve moral dilemmas?",
        "What is the nature of moral responsibility?",
        "What is the relationship between morality and law?",
        "What is ethical relativism?",
        "How does culture affect morality?",
        "What is the basis of human rights?",
        "What is the relationship between compassion and ethics?",
    ],
    "reality_existence": [
        "What is the nature of reality?",
        "Is the physical world the ultimate reality?",
        "What is the relationship between mind and matter?",
        "Does reality exist independently of observation?",
        "What is the relationship between appearance and reality?",
        "Is the world real or a dream?",
        "What is the ultimate substance of reality?",
        "How many levels of reality exist?",
        "What is the relationship between being and becoming?",
        "Is there a fundamental layer of reality?",
        "What is the nature of objective reality?",
        "How does consciousness shape reality?",
        "What is the relationship between truth and reality?",
        "Is reality ultimately one or many?",
        "What is the nature of existence?",
        "How does nothingness relate to being?",
        "What is the relationship between time and reality?",
        "Is reality static or dynamic?",
        "What is the relationship between space and existence?",
        "How do we perceive the nature of reality?",
    ],
    "knowledge_truth": [
        "What is true knowledge?",
        "How can we know what is real?",
        "What is the nature of truth?",
        "What are the limits of human knowledge?",
        "Can we have certain knowledge about anything?",
        "What is the difference between belief and knowledge?",
        "How is knowledge acquired?",
        "What is justified true belief?",
        "Can we trust our senses?",
        "What is skepticism?",
        "What is the difference between opinion and knowledge?",
        "How does language shape knowledge?",
        "What is the relationship between knowledge and power?",
        "What is epistemic humility?",
        "How do we distinguish true from false beliefs?",
        "What is the nature of understanding?",
        "Can there be knowledge without experience?",
        "What is the role of reason in acquiring knowledge?",
        "How does memory contribute to knowledge?",
        "What is the relationship between wisdom and knowledge?",
    ],
    "death_immortality": [
        "What happens after death?",
        "Is death the end of existence?",
        "Does death feel painful?"
        "How should we face mortality?",
        "What is the proper attitude toward death?",
        "Does the soul survive physical death?",
        "What is the meaning of mortality?",
        "How does awareness of death affect life?",
        "What is a good death?",
        "Is immortality desirable?",
        "What is death?",
        "What is the relationship between life and death?",
        "How do different philosophies view death?",
        "What is the fear of death?",
        "Can death be overcome?",
        "What is the nature of dying?",
        "How should we prepare for death?",
        "What is the relationship between death and meaning?",
        "What is eternal life?",
        "How does culture shape attitudes toward death?",
        "What is the metaphysics of death?",
    ],
    "nature_universe": [
        "What is the relationship between humans and nature?",
        "What is the cosmic order of the universe?",
        "Are humans separate from or connected to the cosmos?",
        "Is the universe purposeful or indifferent?",
        "What is humanity's place in the universe?",
        "What is the origin of the universe?",
        "Is the universe finite or infinite?",
        "What is the relationship between nature and nurture?",
        "What is the natural order?",
        "Are natural laws absolute?",
        "What is the relationship between humanity and the environment?",
        "How should we understand natural disasters?",
        "What is the relationship between science and nature?",
        "Is nature inherently violent or peaceful?",
        "What is the role of humans in the ecosystem?",
        "What is the relationship between technology and nature?",
        "How does nature inspire human thought?",
        "What is the beauty of nature?",
        "How do we find meaning in nature?",
        "What is the relationship between natural and moral law?",
        "Is God the creator of universe?",
        "Is Universe always listening to us?",
        "Does manifestations come true if asked to the universe?"
    
    ],
    "enlightenment_liberation": [
        "How can one achieve enlightenment?",
        "What is liberation from suffering?",
        "What is the ultimate goal of spiritual practice?",
        "What is the path to spiritual awakening?",
        "How does one transcend worldly suffering?",
        "What is nirvana?",
        "What is moksha?",
        "What is satori?",
        "What is the nature of spiritual realization?",
        "How does one become fully awakened?",
        "What is the relationship between enlightenment and compassion?",
        "What blocks spiritual progress?",
        "What is the nature of spiritual liberation?",
        "How does meditation lead to enlightenment?",
        "What is the role of guru in enlightenment?",
        "What is self-enlightenment?",
        "What is the relationship between knowledge and enlightenment?",
        "Can enlightenment be gradual or sudden?",
        "What is the experience of enlightenment?",
        "How does enlightenment affect daily life?",
    ],
    "free_will_fate": [
        "Do humans have free will?",
        "Is everything predetermined by fate?",
        "What is the relationship between free will and determinism?",
        "Are humans responsible for their actions?",
        "Can we shape our own destiny?",
        "What is predestination?",
        "How does karma relate to free will?",
        "What is the nature of choice?",
        "Are our choices truly free?",
        "What is the relationship between freedom and responsibility?",
        "What is the difference between freedom and license?",
        "How does causality affect free will?",
        "What is the relationship between fate and destiny?",
        "Can we break free from our past?",
        "What is the nature of human agency?",
        "How does foreknowledge affect free will?",
        "What is the relationship between free will and morality?",
        "Can free will exist in a deterministic universe?",
        "What is the role of will in human life?",
        "How does determinism affect moral responsibility?",
    ],
    "good_evil": [
        "What is the nature of good and evil?",
        "Why does evil exist in the world?",
        "Is morality based on divine command or reason?",
        "Can good come from evil?",
        "What is the ultimate good for humans?",
        "What is the problem of evil?",
        "Is humanity inherently good or evil?",
        "What is the relationship between good and pleasure?",
        "Can evil be justified?",
        "What is moral relativism?",
        "What is the nature of moral evil?",
        "How do we combat evil in the world?",
        "What is the relationship between good and God?",
        "What is the root of human wickedness?",
        "Can evil be eliminated?",
        "What is the relationship between good and truth?",
        "What is moral courage?",
        "How does one overcome evil?",
        "What is the nature of sin?",
        "What is the relationship between good actions and good character?",
    ],
    "society_justice": [
        "What is the ideal form of government?",
        "What is social justice?",
        "What are the rights and duties of citizens?",
        "Should individuals prioritize society or self?",
        "What is the relationship between law and morality?",
        "What is the best political system?",
        "What is the relationship between freedom and equality?",
        "What is the social contract?",
        "How should power be distributed in society?",
        "What is the relationship between individual and collective?",
        "What is the nature of democracy?",
        "How should we balance individual rights with social goods?",
        "What is the role of education in society?",
        "How does economic inequality affect society?",
        "What is the relationship between religion and politics?",
        "What is the ideal community?",
        "How should we address systemic injustice?",
        "What is the relationship between freedom and authority?",
        "What makes a society just?",
        "How do we create a peaceful society?",
    ],
    "death_meaning": [
        "What is the proper way to face death?",
        "Does death give life meaning?",
        "How should the awareness of death affect how we live?",
        "What is a good death?",
        "Is immortality desirable?",
        "What is mortality?",
        "How do different cultures view death?",
        "What is the relationship between life and death?",
        "What is the fear of death?",
        "How can we accept death?",
        "What is the relationship between death and freedom?",
        "How does death relate to identity?",
        "What is the meaning of mortality for human action?",
        "How should we remember the dead?",
        "What is the relationship between death and love?",
        "How does death shape human values?",
        "What is the wisdom of mortality?",
        "How do we cope with the death of loved ones?",
        "What is the relationship between death and creativity?",
        "What is the spiritual significance of death?",
    ],
    "body_mind": [
        "What is the relationship between body and mind?",
        "Is the mind separate from the brain?",
        "What is consciousness?",
        "What is the nature of subjective experience?",
        "How do thoughts arise?",
        "What is the self?",
        "Is the mind eternal?",
        "What is the relationship between spirit and body?",
        "What is embodiment?",
        "How does the body influence the mind?",
        "What is the nature of mental states?",
        "Can the mind exist without the body?",
        "What is the relationship between emotions and thoughts?",
        "How does perception work?",
        "What is the nature of consciousness?",
        "What is the relationship between brain and mind?",
        "How do we control our minds?",
        "What is the nature of memory?",
        "How does attention shape experience?",
        "What is the relationship between intention and action?",
    ],
    "wisdom_truth": [
        "What is wisdom?",
        "How is wisdom different from knowledge?",
        "What is practical wisdom?",
        "How do we acquire wisdom?",
        "What is the wise person like?",
        "What is philosophical wisdom?",
        "Can wisdom be taught?",
        "What is the relationship between wisdom and virtue?",
        "What is the highest wisdom?",
        "How does wisdom manifest in action?",
        "What is the relationship between wisdom and compassion?",
        "How does wisdom relate to happiness?",
        "What is the difference between cleverness and wisdom?",
        "What is the role of experience in wisdom?",
        "How does wisdom develop over time?",
        "What is the relationship between wisdom and age?",
        "How do we apply wisdom in daily life?",
        "What is the relationship between wisdom and creativity?",
        "Can wisdom be measured?",
        "What is the pursuit of wisdom?",
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
                device=device,
            )
            eastern_output = generate(
                eastern_model,
                encoding,
                WESTERN_MARKERS = [
                    "soul", "virtue", "reason", "logos", "socrates", "plato", "aristotle",
                    "god", "justice", "polis", "republic", "form", "ideal", "rational",
                    "empirical", "substance", "cause", "effect", "categorical", "imperative",
                    "existence", "essence", "consciousness", "dialectic", "synthesis",
                    "kant", "hegel", "descartes", "nietzsche", "aristotelian",
                ]
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
    temperature: float = 0.6,

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
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": GENERATION_CONFIG["top_p"],
            "top_k": GENERATION_CONFIG["top_k"],
            "repetition_penalty": GENERATION_CONFIG["repetition_penalty"],

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
        default=0.8,
        help="Temperature for text generation",
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
            args.western_path, args.eastern_path, 
            args.output_dir, args.max_tokens, args.temperature
        )
        analyze_bias(results)