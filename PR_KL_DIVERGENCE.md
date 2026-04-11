# PR: Add KL Divergence Evaluation

## Summary
This branch adds a KL divergence-based evaluation path to compare the Western and Eastern models more directly at the next-token distribution level.

## What Changed
- Added a new `kl_divergence.py` module that implements KL divergence helpers and a combined KL report.
- Updated `evaluate_bias.py` to import the new helpers and include KL metrics in evaluation output.
- Extended the bias summary table with KL columns so divergence is visible alongside the existing metrics.
- Updated the documentation to describe KL divergence alongside the existing cross-perplexity and vocabulary-overlap analysis.
- Documented the feature and interpretation details in [docs/KL_DIVERGENCE.md](docs/KL_DIVERGENCE.md).

## Why
Cross-perplexity compares generated text indirectly. KL divergence compares the models' probability distributions on the same prompt, which is a cleaner signal for how much the two models differ in their token-level predictions.

## Validation
- Python syntax and imports were checked during development.
- The new KL outputs are documented in the evaluation docs and reflected in the summary table behavior.

## Notes
- KL is reported as a normalized percentage for easier interpretation.
- Both directional KL values and a symmetric KL value are included so reviewers can compare asymmetry and overall divergence.

## Related Docs
- [docs/KL_DIVERGENCE.md](docs/KL_DIVERGENCE.md)
- [docs/STATS_ANALYSIS.md](docs/STATS_ANALYSIS.md)
- [docs/PROGRESSIVE_TRAINING_README.md](docs/PROGRESSIVE_TRAINING_README.md)
- [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)
- [docs/VOCAB_BUBBLES.md](docs/VOCAB_BUBBLES.md)
