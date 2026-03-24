#!/bin/bash
# Setup script for LLMTraining on cluster
# Run this on Cmps03.ok.ubc.ca

set -e

echo "=== LLMTraining Setup Script ==="

# 1. Create project directory
mkdir -p ~/LLMTraining
cd ~/LLMTraining

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install torch transformers tiktoken pytest tensorboard

# Verify installation
python -c "import torch; import transformers; import tiktoken; print('✓ All packages installed')"

# 4. Create data directories
mkdir -p data/western data/eastern outputs

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Copy your text files to:"
echo "   - data/western/ (Bible, Greek philosophy, etc.)"
echo "   - data/eastern/ (Gita, Tao Te Ching, etc.)"
echo ""
echo "2. Run training:"
echo "   source .venv/bin/activate"
echo "   python gpt2_pretrain.py"
echo ""
echo "3. To use streaming mode (for large datasets), edit gpt2_pretrain.py"
echo "   and uncomment the streaming section in __main__"
