# Tests

This document is a quick reference for what this test suite exists to protect and why each file is here.

## What you are looking at
1. `tests/test_lm_utils.py`
   - Guards the core data pipeline helpers used by both training scripts.
   - Verifies block slicing behavior (exact fit vs. remainder drop).
   - Verifies batching output shapes and masks for padding correctness.
   - Verifies reading `.txt` shards in sorted order from `data/`.

2. `tests/test_pretrain_builders.py`
   - Guards the "build from scratch" wiring for both GPT-2 and DeepSeek-R1.
   - Ensures block size is plumbed into model config for GPT-2.
   - Ensures padding token IDs are set consistently for both builders.
   - Uses dummy Hugging Face classes so the tests validate wiring without network downloads.

3. `tests/conftest.py`
   - Keeps imports stable by adding the repo root to `sys.path` during tests.

4. `tests/test_download_data.py`
   - Guards the data download and preprocessing helpers in `download_pretraining_data.py`.
   - Verifies time/folder path helpers (`get_time_folder`, `get_folder_path`) for BCE and CE years.
   - Verifies `clean_whitespace` normalises CRLF, collapses blank lines and spaces, and strips edges.
   - Verifies `strip_gutenberg_boilerplate` removes header/footer markers and passes through plain text.
   - Verifies `html_to_text` strips tags and drops `<script>`/`<style>` content.
   - Verifies `_english_stats` and `_is_probably_english` heuristics for language detection.
   - Verifies `fetch_unavailable` always returns `False` and prints the label.
   - Verifies `_parse_entry` unpacks a work-queue tuple into its components.

5. `tests/test_inference_utils.py`
   - Guards the inference helpers in `inference_utils.py`.
   - Verifies `generate` returns a string and excludes the prompt tokens from the output.
   - Verifies `generate_with_history` formats the prompt correctly and appends to existing history.
   - Uses lightweight dummy model and encoding classes so no GPU or network is required.

6. `tests/chat_test.py`
   - Interactive utility to chat with a trained GPT-2 checkpoint.
   - Not part of the automated pytest suite by default.
