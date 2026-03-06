#!/bin/bash
# Setup script for LLMTraining on cluster
# Run this once on Cmps03.ok.ubc.ca

set -e

echo "=== LLMTraining Setup ==="

cd ~/LLMTraining

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install torch transformers tiktoken pytest tensorboard setuptools

# Verify
python -c "import torch; import transformers; import tiktoken; print('✓ All packages installed')"
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"

# Create directories
mkdir -p data/western data/eastern outputs

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next: Run ./cluster_download_data.sh to get training texts"
