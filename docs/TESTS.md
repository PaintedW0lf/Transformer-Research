# Tests

This document is a quick reference for what the automated suite protects and why each test file exists.

Current coverage: 46 passing tests.

## What you are looking at
1. `tests/test_lm_utils.py`
   - Guards the core data pipeline helpers used by both training scripts.
   - Verifies block slicing behavior, batching output shapes, padding masks, and sorted shard loading.

2. `tests/test_pretrain_builders.py`
   - Guards the "build from scratch" wiring for both GPT-2 and DeepSeek-R1.
   - Ensures block size is plumbed into model config for GPT-2.
   - Ensures padding token IDs are set consistently for both builders.
   - Uses dummy Hugging Face classes so the tests validate wiring without network downloads.

3. `tests/test_streaming.py`
   - Exercises the streaming dataset path used for large corpora.
   - Verifies block sizes, EOS handling, invalid inputs, and multi-file iteration.

4. `tests/test_kl_divergence.py`
   - Covers KL normalization helpers and report structure.
   - Verifies identical-model behavior, symmetric KL, and failure handling.

5. `tests/test_stats_analysis.py`
   - Covers tokenization, word distributions, Bhattacharyya metrics, and per-category overlap analysis.

6. `tests/test_evaluate_bias.py`
   - Covers repetition score, type-token ratio, concept frequencies, perplexity, summary formatting, and JSON output shape.
   - Verifies the KL divergence metrics are written into the evaluation results.

7. `tests/test_visualize_vocab.py`
   - Covers vocabulary filtering, circle packing, color blending, result loading, and chart generation.

8. `tests/test_pipeline_cli.py`
   - Smoke-tests the CLI-style entry points for preview training, progressive training, and batch chat output.
   - Verifies manifest writing and the expected artifact layout without running real training.

9. `tests/conftest.py`
   - Keeps imports stable by adding the repo root to `sys.path` during tests.

10. `tests/test_download_data.py`
   - Guards the data download and preprocessing helpers in `download_pretraining_data.py`.
   - Verifies time/folder path helpers (`get_time_folder`, `get_folder_path`) for BCE and CE years.
   - Verifies `clean_whitespace` normalises CRLF, collapses blank lines and spaces, and strips edges.
   - Verifies `strip_gutenberg_boilerplate` removes header/footer markers and passes through plain text.
   - Verifies `html_to_text` strips tags and drops `<script>`/`<style>` content.
   - Verifies `_english_stats` and `_is_probably_english` heuristics for language detection.
   - Verifies `fetch_unavailable` always returns `False` and prints the label.
   - Verifies `_parse_entry` unpacks a work-queue tuple into its components.

11. `tests/test_inference_utils.py`
   - Guards the inference helpers in `inference_utils.py`.
   - Verifies `generate` returns a string and excludes the prompt tokens from the output.
   - Verifies `generate_with_history` formats the prompt correctly and appends to existing history.
   - Uses lightweight dummy model and encoding classes so no GPU or network is required.
   - Interactive utility to chat with a trained GPT-2 checkpoint.
   - Not part of the automated pytest suite by default.

## What the suite now covers
- Core dataset building and batching.
- GPT-2 and DeepSeek-R1 builder wiring.
- Streaming dataset behavior.
- KL divergence utilities and evaluation output.
- Bhattacharyya overlap statistics.
- Bias evaluation JSON generation and summary formatting.
- Vocabulary visualizer helpers and image artifact creation.
- CLI smoke tests for the progressive pipeline and preview tool.

## Notes
- The visualization tests require `matplotlib` and `numpy`.
- The suite is designed to stay fast by mocking heavy model loading and training.
- End-to-end training on real checkpoints is still manual, but the orchestration and output paths are covered.
