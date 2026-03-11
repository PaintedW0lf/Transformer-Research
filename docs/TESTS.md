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
