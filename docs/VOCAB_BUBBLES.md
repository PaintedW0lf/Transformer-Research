# Vocabulary Bubble Visualizer

`visualize_vocab.py` turns the JSON output of `evaluate_bias.py` into packed
bubble charts that show the **core vocabulary** each model reaches for when
answering philosophical prompts.  It produces two sets of three charts each:
one set for individual words (unigrams) and one for two-word phrases (bigrams).

## What it does

1. Loads the most recent `bias_evaluation_*.json` from `outputs/bias_evaluation/`
   (or a specific file you point it at).
2. Collects every word and every consecutive word pair from the model outputs.
3. Strips **pronouns**, **prepositions**, auxiliary verbs, and common stop words.
   For bigrams, both words in the pair must survive the filter.
4. Takes the top-N most frequent items per chart (default: 60 words, 40 bigrams).
5. Renders **packed bubble charts** — each item is a filled circle whose radius
   scales linearly with its frequency.
6. Saves six PNG files to `outputs/vocab_bubbles/`.

## Output files

| File | What it shows |
|---|---|
| `vocab_bubbles_western.png` | Top words — Western model (blue) |
| `vocab_bubbles_eastern.png` | Top words — Eastern model (red) |
| `vocab_bubbles_combined.png` | Top words — both models merged, colour-coded |
| `bigram_bubbles_western.png` | Top bigrams — Western model (blue) |
| `bigram_bubbles_eastern.png` | Top bigrams — Eastern model (red) |
| `bigram_bubbles_combined.png` | Top bigrams — both models merged, colour-coded |

## Colour coding (combined charts)

| Colour | Meaning |
|---|---|
| Blue   | Item appears mostly in Western model answers |
| Purple | Item appears roughly equally in both models |
| Red    | Item appears mostly in Eastern model answers |

The bigram charts are especially useful for spotting **conceptual framing** —
e.g. the Western model might cluster around *moral duty*, *individual rights*,
*rational soul*, while the Eastern model surfaces *human nature*, *inner peace*,
*karma liberation*.

## Usage

```bash
# Use the latest evaluation results (default paths)
python visualize_vocab.py

# Point at a specific results file
python visualize_vocab.py --results-file outputs/bias_evaluation/bias_evaluation_20240101_120000.json

# Adjust word and bigram counts
python visualize_vocab.py --top-n 80 --top-n-bigrams 50

# Custom output directory
python visualize_vocab.py --output-dir my_charts/
```

## Dependencies

Only `matplotlib` and `numpy` are required.  Add them to `requirements.txt`
if not already present.

## Filtered word categories

The following are removed before any counting:

- **Pronouns** — I, we, you, he, she, it, they, who, which, this, that, …
- **Prepositions** — in, on, at, by, for, with, from, to, of, about, …
- **Auxiliary verbs & stop words** — is, are, was, were, be, have, do,
  can, will, would, should, may, might, the, a, an, and, or, but, …

For bigrams, a pair is kept only if **both** words pass the filter, ensuring
every bigram represents a meaningful concept pair rather than a grammatical
fragment.
