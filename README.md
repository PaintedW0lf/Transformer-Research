# LLMTraining

Minimal pretraining scaffolds for GPT-2 (tiktoken) and DeepSeek-R1 (transformers).

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
- GPT-2: `gpt2_pretrain.py`
- DeepSeek-R1: `deepseek_r1_pretrain.py`

Each script loads data from **data/** and builds a scratch model + trainer. Uncomment the `trainer.train()` line to start training.

## Notes
- Outputs are written to `outputs/`.
- For large corpora, replace the simple loader with a streaming dataset.
