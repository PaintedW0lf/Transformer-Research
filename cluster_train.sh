#!/bin/bash
# Training script for LLMTraining on cluster
# Run from ~/LLMTraining directory

set -e

source .venv/bin/activate

echo "=== LLMTraining - Training Script ==="

# Check data exists
if [ ! -d "data/western" ] || [ -z "$(ls -A data/western)" ]; then
    echo "ERROR: No files in data/western/"
    exit 1
fi

if [ ! -d "data/eastern" ] || [ -z "$(ls -A data/eastern)" ]; then
    echo "ERROR: No files in data/eastern/"
    exit 1
fi

echo "Found training data:"
echo "  Western: $(ls data/western/*.txt 2>/dev/null | wc -l) files"
echo "  Eastern: $(ls data/eastern/*.txt 2>/dev/null | wc -l) files"

# Check GPU availability
if command -v nvidia-smi &> /dev/null; then
    echo ""
    echo "GPU Info:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
fi

echo ""
echo "Starting training..."
echo ""

# Set training parameters
export DATA_DIR="data/western"
export MODEL_TYPE="gpt2"
export BLOCK_SIZE=1024
export MAX_STEPS=1000
export LEARNING_RATE=5e-4

# Run training (uncomment trainer.train() in the script first!)
python gpt2_pretrain.py

echo ""
echo "=== Training Complete! ==="
echo "Check outputs/ for checkpoints"
