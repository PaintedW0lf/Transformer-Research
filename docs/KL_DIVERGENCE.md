# KL Divergence — Evaluation Module

## What Was Added

Two files were changed or created:

| File | Change |
|---|---|
| `kl_divergence.py` | New module — all KL logic lives here |
| `evaluate_bias.py` | Imports from `kl_divergence.py`; adds KL columns to results JSON and summary table |

---

## Why It Is Necessary

The existing evaluation used **cross-perplexity** to measure how different the Western and Eastern models are.  Cross-perplexity tells you how surprised model B is when it reads text that model A *generated* — but that is indirect.  The generated text is already filtered through sampling, so high perplexity could just mean model B dislikes the word choices, not that the underlying beliefs are different.

**KL divergence** cuts out the sampling step.  Given the same input prompt, both models produce a probability distribution over the entire vocabulary for every next token.  KL divergence directly compares those distributions.  If the Western model thinks the next word is probably "virtue" or "reason" while the Eastern model thinks it is probably "dharma" or "karma", that disagreement is captured at the logit level — before any token is ever sampled.

This makes KL divergence a cleaner signal for the core research question: *do these models encode genuinely different philosophical worldviews, or do they just generate different-sounding text by chance?*

---

## How It Works

### The Math

For two probability distributions P and Q over a vocabulary V:

```
KL(P || Q) = Σ  P(token) * log( P(token) / Q(token) )
              v∈V
```

- **0** when P and Q are identical at every token position.
- **Increases** the more P and Q disagree.
- **Asymmetric** — KL(P‖Q) ≠ KL(Q‖P) in general.

In this codebase each model produces one distribution per token *position* in the sequence.  We average KL across all positions to get a single number per text.

### Normalization to a Percentage

Raw KL is measured in nats and is unbounded, which makes it hard to interpret ("is 2.3 nats a lot?").  We normalize by the theoretical maximum:

```
max KL = log(vocab_size) = log(50 257) ≈ 10.83 nats
```

This maximum is reached when P puts all its probability mass on a single token and Q spreads it uniformly — the worst-case scenario.

```
KL % = (raw KL in nats / 10.83) * 100
```

Now the value is interpretable:
- **~0 %** — the models predict nearly the same next-token distribution. Very similar.
- **~10–20 %** — noticeable divergence; models lean toward different vocabulary.
- **~50 %+** — strongly different distributions; models inhabit different conceptual spaces.
- **100 %** — theoretical ceiling, never reached in practice.

### Symmetric KL

Because KL(W‖E) ≠ KL(E‖W), we also compute the symmetric version:

```
KL_sym = 0.5 * (KL(W || E) + KL(E || W))
```

This is a single number that summarizes total divergence without picking either model as the reference.  It is the most useful column for comparing categories against each other.

---

## Public API (`kl_divergence.py`)

### `compute_kl_pct(model_p, model_q, encoding, text, device, block_size=1024)`

Computes **KL(P‖Q)** on `text` and returns it as a percentage.

- `model_p` is the reference model (P).
- `model_q` is the comparison model (Q).
- Higher % means model_q's predictions are more surprising given model_p's.
- Returns `nan` if the text is too short or an error occurs.

### `compute_symmetric_kl_pct(model_a, model_b, encoding, text, device, block_size=1024)`

Computes **0.5 * (KL(A‖B) + KL(B‖A))** and returns it as a percentage.

Use this when neither model is the clear "ground truth" — which is always the case here since both are trained on real philosophical corpora.

### `compute_kl_report(model_west, model_east, encoding, prompt, west_output, east_output, device)`

Convenience function used by `evaluate_bias.py`.  Returns a dict with all five KL metrics for one prompt/response pair:

| Key | What it measures |
|---|---|
| `west_to_east_on_prompt` | KL(W‖E) on the shared prompt |
| `east_to_west_on_prompt` | KL(E‖W) on the shared prompt |
| `symmetric_on_prompt` | Symmetric KL on the shared prompt |
| `west_to_east_on_east_output` | KL(W‖E) when reading the Eastern model's generated text |
| `east_to_west_on_west_output` | KL(E‖W) when reading the Western model's generated text |

All values are percentages (0–100 %).

---

## Output

### JSON (`bias_evaluation_*.json`)

Each entry in `results["evaluations"]` gains a `"kl_divergence"` field:

```json
"kl_divergence": {
    "west_to_east_on_prompt": 14.32,
    "east_to_west_on_prompt": 11.87,
    "symmetric_on_prompt": 13.10,
    "west_to_east_on_east_output": 18.45,
    "east_to_west_on_west_output": 16.02,
    "_note": "all values are percentages (0=identical, 100=max divergence)"
}
```

### Summary Table

The `analyze_bias()` console table gains three columns on the right:

```
KL W→E%   KL E→W%   KL Sym%
  14.3%     11.9%     13.1%
```

- **KL W→E%** — western model's predictions diverge this much from eastern on the prompt.
- **KL E→W%** — eastern model's predictions diverge this much from western on the prompt.
- **KL Sym%** — overall divergence, direction-agnostic. The easiest column to compare across categories.

---

## Interpreting Results

A high `KL Sym%` for a category like `enlightenment_liberation` (e.g. 25 %) and a low one for `society_justice` (e.g. 5 %) tells you:

- The models encode substantially different beliefs about enlightenment — their token distributions diverge strongly when asked about it.
- Their beliefs about societal justice are relatively similar — the training corpora may have converged on shared vocabulary or concepts for that topic.

This is the kind of finding that cross-perplexity alone cannot cleanly surface, because cross-perplexity is confounded by fluency differences and generation randomness.
