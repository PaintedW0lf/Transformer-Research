# LLMTraining

Minimal pretraining scaffolds for GPT-2 (tiktoken) and DeepSeek-R1 (transformers).

## Setup
Create a virtual environment and install dependencies:
```
python -m venv .venv
source .venv/bin/activate
pip install torch transformers tiktoken pytest
```

## Data format
- Place your training corpus in the **data/** folder.
- Files must be **UTF-8** plain text (`.txt`).
- You can include many `.txt` files; they will be read and concatenated in sorted order.

Example layout:
```
LLMTraining/
  data/
    shard-0001.txt
    shard-0002.txt
```

## Scripts
**Training:**
- GPT-2: `gpt2_pretrain.py`
- DeepSeek-R1: `deepseek_r1_pretrain.py`

Each script loads data from **data/** and builds a scratch model + trainer. Uncomment the `trainer.train()` line to start training.

**Inference:**
- GPT-2: `infer_gpt2.py`
- DeepSeek-R1: `infer_deepseek_r1.py`

Each loads the latest checkpoint from **outputs/** and generates text from a prompt.

## Run
**Training:**

GPT-2 scratch pretraining (builds model + trainer):
```
python gpt2_pretrain.py
```

DeepSeek-R1 scratch pretraining (builds model + trainer):
```
python deepseek_r1_pretrain.py
```

**Inference:**

Generate with trained GPT-2 model:
```
python infer_gpt2.py --prompt "Your prompt here" --max-tokens 100
```

Generate with trained DeepSeek-R1 model:
```
python infer_deepseek_r1.py --prompt "Your prompt here" --max-tokens 100
```

Both inference scripts look for checkpoints in **outputs/** and accept `--checkpoint`, `--temperature`, and `--top-p` flags.

## Tests
Run all tests:
```
pytest
```

## Notes
- Outputs are written to `outputs/`.
- For large corpora, replace the simple loader with a streaming dataset.
