# Vocabulary Bubble Visualizer

`visualize_vocab.py` turns the JSON output of `evaluate_bias.py` into packed
bubble charts that show the **core vocabulary** each model reaches for when
answering philosophical prompts.

## What it does

1. Loads the most recent `bias_evaluation_*.json` from `outputs/bias_evaluation/`
   (or a specific file you point it at).
2. Collects every word that appears in the `western_output` and `eastern_output`
   fields across all evaluated prompts.
3. Strips **pronouns**, **prepositions**, auxiliary verbs, and common stop words
   so that the chart surfaces semantically meaningful concepts rather than
   grammatical glue.
4. Takes the top-N most frequent surviving words (default 60) per chart.
5. Renders **packed bubble charts** — each word is a filled circle whose
   radius scales linearly with its frequency.  Larger circle = more often used.
6. Saves three PNG files to `outputs/vocab_bubbles/`:
   - `vocab_bubbles_western.png` — Western model only (blue)
   - `vocab_bubbles_eastern.png` — Eastern model only (red)
   - `vocab_bubbles_combined.png` — Both models merged into one chart; bubble
     colour encodes which model favours the word

## The three charts explained

### Western & Eastern (separate)

Each shows the top-N words used by that model alone.  Circle size = frequency
within that model's outputs.

| Colour | Model |
|---|---|
| Blue | Western model |
| Red  | Eastern model |

### Combined

The union of both models' vocabularies in a single chart.  Circle size is based
on the **total** frequency across both models.  Colour encodes dominance:

| Colour | Meaning |
|---|---|
| Blue   | Word appears mostly in Western model answers |
| Purple | Word appears roughly equally in both models |
| Red    | Word appears mostly in Eastern model answers |

Words that appear prominently in one model but not the other highlight the
philosophical framing each model has learned — e.g. the Western model might
surface *reason*, *virtue*, *individual* while the Eastern model surfaces
*dharma*, *karma*, *interconnected*.

## Usage

```bash
# Use the latest evaluation results (default paths)
python visualize_vocab.py

# Point at a specific results file
python visualize_vocab.py --results-file outputs/bias_evaluation/bias_evaluation_20240101_120000.json

# Show more words (up to 80 per model)
python visualize_vocab.py --top-n 80

# Custom output directory
python visualize_vocab.py --output-dir my_charts/
```

## Dependencies

Only `matplotlib` and `numpy` are required — both are standard in any ML
environment.  No extra packages needed beyond what is already in
`requirements.txt` (add `matplotlib` and `numpy` if not already present).

## Filtered word categories

The following word classes are removed before counting:

- **Pronouns** — I, we, you, he, she, it, they, who, which, this, that, …
- **Prepositions** — in, on, at, by, for, with, from, to, of, about, …
- **Auxiliary verbs & stop words** — is, are, was, were, be, have, do,
  can, will, would, should, may, might, the, a, an, and, or, but, …

Single-character tokens and two-letter tokens that passed through any other
filter are also discarded.
