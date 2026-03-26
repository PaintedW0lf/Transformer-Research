# LLMTraining - Cluster Guide

## What This Does
Trains GPT-2 models from scratch on philosophical texts to compare Western vs Eastern bias. The model learns language patterns from the training data and can generate text reflecting those patterns.

---

## Quick Start

### 1. Copy Project to Cluster
```bash
# From local machine
scp -r LLMTraining vanshi05@Cmps03.ok.ubc.ca:~/
```

### 2. Setup (Run Once)
```bash
ssh vanshi05@Cmps03.ok.ubc.ca
cd ~/LLMTraining
chmod +x *.sh
./cluster_setup.sh
```

### 3. Download Training Data
```bash
./cluster_download_data.sh
```
Downloads from Project Gutenberg:
- **Western**: Bible, Plato's Republic, Aristotle's Politics
- **Eastern**: Bhagavad Gita, Tao Te Ching, Upanishads

### 4. Train Models (Use tmux!)
```bash
# Start tmux session (persists if disconnected)
tmux new -s train

# Activate environment
source .venv/bin/activate

# Train Western model
python gpt2_pretrain.py --data-dir data/western --streaming --max-steps 500 --output-dir outputs/western_model

# Open new tmux window: Ctrl+B, C
# Train Eastern model
python gpt2_pretrain.py --data-dir data/eastern --streaming --max-steps 500 --output-dir outputs/eastern_model

# Detach: Ctrl+B, D (training continues)
# Reattach: tmux attach -t train
```

### 5. Download Trained Models
```bash
# From local machine
scp -r vanshi05@Cmps03.ok.ubc.ca:~/LLMTraining/outputs ./LLMTraining/
```

---

## Training Flow

```
Text Files (.txt)
      ↓
   Tokenize (tiktoken GPT-2 encoding)
      ↓
   Create blocks of 1024 tokens
      ↓
   Feed to GPT-2 model (124M params)
      ↓
   Predict next token, compute loss
      ↓
   Backpropagate, update weights
      ↓
   Save checkpoints & final model
```

---

## Output Files Explained

| File | Description |
|------|-------------|
| `model.safetensors` | **Trained weights** (~500MB) - the "learned knowledge" |
| `config.json` | Model architecture (layers, heads, dimensions) |
| `trainer_state.json` | Training history (loss per step) |
| `runs/` | TensorBoard logs for visualization |

---

## Command Reference

### Training Options
```bash
python gpt2_pretrain.py \
    --data-dir data/western \    # Source text directory
    --streaming \                 # Memory-efficient mode (required for large data)
    --max-steps 500 \            # Training iterations
    --output-dir outputs/model   # Where to save
```

| Option | Default | Description |
|--------|---------|-------------|
| `--data-dir` | data | Directory with .txt files |
| `--output-dir` | outputs/gpt2_scratch | Output directory |
| `--streaming` | off | Use for large datasets |
| `--max-steps` | 100000 | Training steps |
| `--block-size` | 1024 | Sequence length |

### Helper Scripts
```bash
./cluster_setup.sh           # Initial setup
./cluster_download_data.sh   # Download texts
./cluster_train.sh western   # Train one model
./cluster_train_both.sh      # Train both models
```

### tmux Shortcuts
| Keys | Action |
|------|--------|
| `Ctrl+B, C` | New window |
| `Ctrl+B, N/P` | Next/Previous window |
| `Ctrl+B, D` | Detach (keeps running) |
| `tmux attach -t train` | Reattach |

---

## Understanding Training Output

```
{'loss': 5.5, 'grad_norm': 1.0, 'learning_rate': 5e-4, 'epoch': 0.5}
```
- **loss**: Prediction error (lower = better, ~4-5 is reasonable for small data)
- **grad_norm**: Gradient magnitude (1-2 is healthy)
- **learning_rate**: Decays over training
- **epoch**: How many times through the data

---

## Next Steps After Training

1. **Generate text** to compare models
2. **Analyze bias** in generated outputs
3. **Fine-tune** with more data or steps
4. **Visualize** with TensorBoard: `tensorboard --logdir outputs/`

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `No .txt files found` | Run `./cluster_download_data.sh` |
| `no_cuda` error | Update lm_utils.py from repo |
| `pkg_resources` missing | `pip install setuptools` |
| Training slow | Check GPU: `nvidia-smi` |
