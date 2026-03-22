#!/bin/bash
# Train a single model on cluster
# Usage: ./cluster_train.sh [western|eastern] [max_steps]

set -e
source .venv/bin/activate

DATA_TYPE=${1:-western}  # western or eastern
MAX_STEPS=${2:-500}

echo "=== Training ${DATA_TYPE} model ==="

# Verify data exists
if [ ! -d "data/${DATA_TYPE}" ] || [ -z "$(ls -A data/${DATA_TYPE}/*.txt 2>/dev/null)" ]; then
    echo "ERROR: No .txt files in data/${DATA_TYPE}/"
    echo "Run ./cluster_download_data.sh first"
    exit 1
fi

echo "Data files: $(ls data/${DATA_TYPE}/*.txt | wc -l)"
echo "Max steps: ${MAX_STEPS}"
echo ""

python gpt2_pretrain.py \
    --data-dir data/${DATA_TYPE} \
    --streaming \
    --max-steps ${MAX_STEPS} \
    --output-dir outputs/${DATA_TYPE}_model

echo ""
echo "=== Done! Model saved to outputs/${DATA_TYPE}_model/ ==="
