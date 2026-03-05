# LLMTraining - Cluster Quick Reference

## Connect to Cluster
```bash
ssh your_username@Cmps03.ok.ubc.ca
```

## Setup (Run Once)
```bash
# Copy files to cluster
scp -r LLMTraining your_username@Cmps03.ok.ubc.ca:~/

# SSH into cluster
ssh your_username@Cmps03.ok.ubc.ca

# Run setup
cd ~/LLMTraining
chmod +x cluster_setup.sh
./cluster_setup.sh
```

## Prepare Data
```bash
# Upload your text files
scp your_text_files/* your_username@Cmps03.ok.ubc.ca:~/LLMTraining/data/western/
scp your_text_files/* your_username@Cmps03.ok.ubc.ca:~/LLMTraining/data/eastern/
```

## Train Single Model
```bash
cd ~/LLMTraining
source .venv/bin/activate

# Basic training (loads all into memory)
python gpt2_pretrain.py --data-dir data/western --max-steps 500

# Streaming mode (for large datasets)
python gpt2_pretrain.py --data-dir data/western --streaming --max-steps 500

# With custom output directory
python gpt2_pretrain.py --data-dir data/western --output-dir outputs/western --max-steps 1000
```

## Train Both Models (Western vs Eastern)
```bash
cd ~/LLMTraining
source .venv/bin/activate

# Train Western
python gpt2_pretrain.py --data-dir data/western --output-dir outputs/western --max-steps 500

# Train Eastern
python gpt2_pretrain.py --data-dir data/eastern --output-dir outputs/eastern --max-steps 500
```

## Command Line Options
| Option | Default | Description |
|--------|---------|-------------|
| `--data-dir` | data | Directory with .txt files |
| `--output-dir` | outputs/gpt2_scratch | Output directory |
| `--block-size` | 1024 | Sequence length |
| `--max-steps` | 100 | Training steps |
| `--learning-rate` | 5e-4 | Learning rate |
| `--streaming` | False | Use streaming mode |
| `--shuffle-buffer` | 10000 | Buffer size for streaming |
| `--n-layer` | 12 | Number of layers |
| `--n-head` | 12 | Number of heads |
| `--n-embd` | 768 | Embedding dimension |

## GPU Training (Recommended)
```bash
# Check GPU
nvidia-smi

# Run with GPU (automatically detected)
python gpt2_pretrain.py --data-dir data/western --max-steps 500
```

## Training Tips
- For GPT-2 base: ~125M params, needs ~2GB VRAM
- For GPT-2 large: ~760M params, needs ~10-15GB VRAM
- Use `--streaming` for datasets > 1GB
- Start with `--max-steps 100` to test

## Monitor Training
```bash
# Check GPU usage
watch -n 1 nvidia-smi

# Check output
tail -f outputs/gpt2_scratch/trainer_state.json
```

## Download Results
```bash
# Download trained models
scp -r your_username@Cmps03.ok.ubc.ca:~/LLMTraining/outputs ./
```
