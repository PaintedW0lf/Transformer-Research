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
  docs/
    CLUSTER_GUIDE.md
    TESTS.md
  scripts/
    cluster_setup.sh
    cluster_train.sh
    cluster_train_both.sh
    cluster_download_data.sh
  tests/
    test_lm_utils.py
    test_pretrain_builders.py
    test_streaming.py
    chat_test.py
  data/
    shard-0001.txt
    shard-0002.txt
```

## Training Scripts
- GPT-2: `gpt2_pretrain.py`
- DeepSeek-R1: `deepseek_r1_pretrain.py`

Each script loads data from **data/** and builds a scratch model + trainer.

## Run
GPT-2 scratch pretraining (builds model + trainer):
```
python gpt2_pretrain.py
```

DeepSeek-R1 scratch pretraining (builds model + trainer):
```
python deepseek_r1_pretrain.py
```

## Utility Scripts
- Cluster setup: `scripts/cluster_setup.sh`
- Cluster training (single run): `scripts/cluster_train.sh`
- Cluster training (east/west): `scripts/cluster_train_both.sh`
- Download public data: `scripts/cluster_download_data.sh`

Cluster instructions: `docs/CLUSTER_GUIDE.md`

## Tests
Run all tests:
```
pytest
```

Interactive checkpoint chat:
```
python tests/chat_test.py --checkpoint outputs/gpt2_east/checkpoint-1000
```

## Notes
- Outputs are written to `outputs/`.
- For large corpora, replace the simple loader with a streaming dataset.
