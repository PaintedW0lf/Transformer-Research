# Statistical Distribution Analysis

`stats_analysis.py` measures how much the word distributions of the Western and Eastern model outputs overlap, using the **Bhattacharyya coefficient** as the primary metric.

It complements the KL divergence report in `kl_divergence.py`, which compares next-token probability distributions directly. Use KL when you want model-level divergence on the prompt itself; use this script when you want to compare the vocabulary actually produced in the outputs.

## What it measures

Given the text outputs of two models (Western and Eastern), the script:

1. Builds a normalized word-frequency distribution for each model's outputs.
2. Computes the **Bhattacharyya coefficient (BC)** between the two distributions.
3. Derives the **Bhattacharyya distance (BD)** from BC.

Results are reported per philosophical category and overall.

## Metrics

### Bhattacharyya Coefficient
```
BC(P, Q) = Σ sqrt(p_i * q_i)
```
- Range: **[0, 1]**
- `0` = no vocabulary overlap between the two models
- `1` = identical distributions (complete overlap)
- Higher → more similar outputs

| BC range | Interpretation     |
|----------|--------------------|
| ≥ 0.9    | Very high overlap  |
| ≥ 0.7    | High overlap       |
| ≥ 0.5    | Moderate overlap   |
| ≥ 0.3    | Low overlap        |
| < 0.3    | Very low overlap   |

### Bhattacharyya Distance
```
BD(P, Q) = -ln(BC(P, Q))
```
- Range: **[0, ∞)**
- `0` = identical distributions
- `∞` = no overlap
- A proper metric-space distance derived from BC — useful when you need a value that grows unboundedly as distributions diverge.

## Usage

```bash
python3 stats_analysis.py --results-file outputs/bias_evaluation_*/bias_evaluation_*.json
```

Save results to a JSON file:
```bash
python3 stats_analysis.py \
  --results-file outputs/bias_evaluation_*/bias_evaluation_*.json \
  --output outputs/stats_results.json
```

## Input format

The script expects a JSON file produced by `evaluate_bias.py`, structured as:
```json
{
  "evaluations": [
    {
      "category": "self_identity",
      "prompt": "...",
      "western_output": "...",
      "eastern_output": "..."
    }
  ]
}
```

## Output

```
Category                             BC       BD  Overlap
------------------------------------------------------------
Death Immortality                0.3271   1.1175  low overlap
Enlightenment Liberation         0.4437   0.8127  low overlap
...

OVERALL METRICS (All Categories Combined)
Bhattacharyya Coefficient:    0.6788  (moderate overlap)
Bhattacharyya Distance:       0.3875
```

## Relationship to evaluate_bias.py

`evaluate_bias.py` generates the raw model outputs and per-output metrics (repetition score, type-token ratio, cross-perplexity, and KL divergence). `stats_analysis.py` is a post-processing step that takes those outputs and quantifies how different the two models' vocabularies are at the distribution level.
