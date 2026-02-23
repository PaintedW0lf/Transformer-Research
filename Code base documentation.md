## Quick documentation for phase 1 

Note: This file is added just so anyone looking at repo after long time or first time can a quick overview here. 

Codebase Overview
This is a minimal LLM pretraining scaffold with two training pipelines: GPT-2 and DeepSeek-R1.
File-by-File Explanation
| File | Purpose |
|------|---------|
| lm_utils.py | Shared utilities for both models. Contains: LMDataset (PyTorch Dataset wrapper), SimpleLMDataCollator (pads sequences), make_blocks (chunks token IDs into fixed-size blocks), build_trainer (creates HuggingFace Trainer), load_texts_from_data_dir (reads all .txt files from data/ folder) |
| gpt2_pretrain.py | GPT-2 pretraining. Uses tiktoken for BPE tokenization. Creates model from GPT2Config, tokenizes texts with gpt2 encoding, builds dataset, sets up trainer |
| deepseek_r1_pretrain.py | DeepSeek-R1 pretraining. Uses HuggingFace transformers tokenizer. Loads pretrained config from DeepSeek-R1, creates model from config, sets up trainer |
| data/sample.txt | Sample training corpus (13 lines of tech/ML text) |
| tests/ | Unit tests for builders and utilities |


Workflow
1. Place .txt files in data/
2. Run python gpt2_pretrain.py or python deepseek_r1_pretrain.py
3. Uncomment trainer.train() to start training
4. Outputs go to outputs/

EDITED ON - 22 Feb, 2026
