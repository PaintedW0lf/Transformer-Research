#!/bin/bash
# Train both Western and Eastern models for bias comparison
# Run from ~/LLMTraining directory in a tmux session

set -e
source .venv/bin/activate

MAX_STEPS=${1:-500}

echo "=== Training Both Models (${MAX_STEPS} steps each) ==="

# Verify data
for type in western eastern; do
    if [ ! -d "data/${type}" ] || [ -z "$(ls -A data/${type}/*.txt 2>/dev/null)" ]; then
        echo "ERROR: No .txt files in data/${type}/"
        echo "Run ./cluster_download_data.sh first"
        exit 1
    fi
    echo "✓ ${type}: $(ls data/${type}/*.txt | wc -l) files"
done

echo ""
echo "=== Training Western Model ==="
python gpt2_pretrain.py \
    --data-dir data/western \
    --streaming \
    --max-steps ${MAX_STEPS} \
    --output-dir outputs/western_model

echo ""
echo "=== Training Eastern Model ==="
python gpt2_pretrain.py \
    --data-dir data/eastern \
    --streaming \
    --max-steps ${MAX_STEPS} \
    --output-dir outputs/eastern_model

echo ""
echo "=== Both Models Trained! ==="
echo "Western: outputs/western_model/"
echo "Eastern: outputs/eastern_model/"
echo ""
echo "Next: Download models and run generate.py to compare outputs"
