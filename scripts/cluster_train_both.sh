#!/bin/bash
# Train both Western and Eastern models for bias comparison
# Run from ~/LLMTraining directory

set -e

source .venv/bin/activate

echo "=== LLMTraining - Western vs Eastern Bias Comparison ==="

# Check data exists
check_data() {
    local dir=$1
    local name=$2
    if [ ! -d "$dir" ] || [ -z "$(ls -A $dir/*.txt 2>/dev/null)" ]; then
        echo "ERROR: No .txt files in $dir/"
        exit 1
    fi
    echo "✓ $name: $(ls $dir/*.txt | wc -l) files"
}

check_data "data/western" "Western"
check_data "data/eastern" "Eastern"

# Training parameters
BLOCK_SIZE=1024
MAX_STEPS=500
LEARNING_RATE=5e-4

echo ""
echo "Training parameters:"
echo "  Block size: $BLOCK_SIZE"
echo "  Max steps: $MAX_STEPS"
echo "  Learning rate: $LEARNING_RATE"
echo ""

# Train Western model
echo "=== Training Western Model ==="
# Note: You need to modify gpt2_pretrain.py to accept data_dir as argument
# For now, copy data to data/ directory temporarily

cp -r data/western/* data/
python gpt2_pretrain.py
mv outputs/gpt2_scratch outputs/western_model

echo ""
echo "=== Training Eastern Model ==="
rm -f data/*.txt
cp -r data/eastern/* data/
python gpt2_pretrain.py
mv outputs/gpt2_scratch outputs/eastern_model

echo ""
echo "=== Both Models Trained! ==="
echo "Western: outputs/western_model/"
echo "Eastern: outputs/eastern_model/"
echo ""
echo "Next: Compare model outputs to analyze bias differences"
