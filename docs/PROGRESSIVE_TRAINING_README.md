# Progressive Philosophical Training Pipeline

## Overview

This pipeline progressively trains language models across historical time periods to analyze how philosophical ideas evolve from ancient (BC) times through the year 2000. Models are trained on cumulative datasets, where each period includes all previous periods' data.

## Architecture

### Files Created
- **`main_progressive_training.py`**: Main orchestration script that manages the entire pipeline
- **`batch_chat_test.py`**: Non-interactive chat test runner for model evaluation

### How It Works

1. **Progressive Data Accumulation**:
   - Period BC: Only BC era texts
   - Period 100: BC + 0-100 CE texts
   - Period 200: BC + 0-100 CE + 100-200 CE texts
   - And so on through period 2000

2. **Dual Regional Training**:
   - Trains separate models for Eastern and Western philosophical traditions
   - Both models trained for each time period to enable comparative analysis

3. **Automated Evaluation**:
   - After training each period pair, runs:
      - `evaluate_bias.py`: Compares philosophical biases between east/west, including cross-perplexity and KL divergence
     - `batch_chat_test.py`: Generates responses to philosophical prompts
     - Results saved in organized JSON format

## Usage

### Basic Usage - Train All Periods

```bash
python main_progressive_training.py
```

This will:
- Train fresh models for each time period (BC through 2000)
- Train for both east and west regions
- Run full evaluation after each period
- Save to `./outputs/` directory

### Train Specific Periods

```bash
# Train only BC and 100 period
python main_progressive_training.py --periods "older (BC)" 100 200

# Train only east region
python main_progressive_training.py --regions east

# Train both, but only west region for specific periods
python main_progressive_training.py --periods 300 400 500 --regions west
```

### Training Configuration

```bash
# Adjust training parameters
python main_progressive_training.py \
  --max-steps 20000 \
  --learning-rate 1e-4 \
  --periods "older (BC)" 100 200

# Custom output directory
python main_progressive_training.py --output-dir ./my_results

# Custom data directory
python main_progressive_training.py --data-dir /path/to/data
```

### Advanced Options

```bash
# Skip evaluation to speed up training
python main_progressive_training.py --skip-evaluation

# Resume from specific period if interrupted
python main_progressive_training.py --resume-from 500

# All options together
python main_progressive_training.py \
  --periods 200 300 400 \
  --regions east west \
  --max-steps 15000 \
  --learning-rate 5e-4 \
  --output-dir ./my_outputs \
  --skip-evaluation
```

## Output Structure

After running the pipeline, the output directory contains:

```
outputs/
├── training_manifest.json              # Track of all trained models
├── progressive_east/                   # Eastern philosophical models
│   ├── period_BC/
│   │   └── checkpoint-500/             # Final checkpoint
│   ├── period_100/
│   │   └── checkpoint-500/
│   └── ...
├── progressive_west/                   # Western philosophical models
│   ├── period_BC/
│   │   └── checkpoint-500/
│   ├── period_100/
│   │   └── checkpoint-500/
│   └── ...
└── progressive_evaluations/            # Evaluation results
    ├── period_BC_evaluation/
    │   ├── bias_evaluation_*.json       # Bias comparison with cross-perplexity and KL divergence
    │   ├── chat_responses_east.json     # Chat test results
    │   └── chat_responses_west.json
    ├── period_100_evaluation/
    │   └── ...
    └── ...
```

## Training Manifest

The `training_manifest.json` file tracks all completed training runs:

```json
{
  "older (BC)": {
    "timestamp": "2026-03-23T10:30:45.123456",
    "east_checkpoint": "outputs/progressive_east/period_BC/checkpoint-500",
    "west_checkpoint": "outputs/progressive_west/period_BC/checkpoint-500",
    "training_config": {
      "block_size": 1024,
      "max_steps": 10000,
      "learning_rate": 0.0005,
      ...
    }
  },
  "100": {
    ...
  }
}
```

## Evaluation Results

### Bias Evaluation (`bias_evaluation_*.json`)

Compares model responses to philosophical prompts across 8 categories and records:
- response text for each model
- repetition score and type-token ratio for each output
- cross-perplexity between the two models' outputs
- KL divergence metrics from `kl_divergence.py`

The 8 prompt categories are:
- self_identity
- purpose_meaning
- ethics_morality
- reality_existence
- knowledge_truth
- death_immortality
- nature_universe
- enlightenment_liberation

### Chat Test Results (`chat_responses_*.json`)

Contains model responses to 24 philosophical prompts with:
- Prompt text
- Model response
- Response length metrics

## Available Time Periods

Training supports the following cumulative time periods:

1. `older (BC)` - Pre-Common Era philosophical texts
2. `100` - 0-100 CE
3. `200` - 100-200 CE
4. `300` - 200-300 CE
5. `400` - 300-400 CE
6. `500` - 400-500 CE
7. `600` - 500-600 CE
8. `700` - 600-700 CE
9. `800` - 700-800 CE
10. `900` - 800-900 CE
11. `1000` - 900-1000 CE
12. `1100` - 1000-1100 CE (west only)
13. `1200` - 1100-1200 CE
14. `1300` - 1200-1300 CE
15. `1400` - 1300-1400 CE
16. `1500` - 1400-1500 CE
17. `1600` - 1500-1600 CE
18. `1700` - 1600-1700 CE
19. `1800` - 1700-1800 CE
20. `1900` - 1800-1900 CE
21. `2000` - 1900-2000 CE

## Performance Considerations

### GPU Memory
- Training uses RTX 6000 Ada GPU optimizations
- Default batch size: 8 (per-device)
- Gradient accumulation: 4 (effective batch size: 32)
- Approximate VRAM usage: 45GB per GPU

### Training Time
- BC period: ~5-10 minutes (smallest dataset)
- Later periods: 20-60 minutes each (larger cumulative datasets)
- Full pipeline (21 periods, both regions): 8-20 hours

### Storage
- Each checkpoint: ~500MB-1GB
- Full pipeline outputs: ~50-100GB (with checkpoints)

## Troubleshooting

### Out of Memory Errors
Reduce batch size or gradient accumulation:
```bash
# Pass via command line (note: requires modifying script) or edit DEFAULT_CONFIG
```

### Training Interrupted
Resume from the last completed period:
```bash
python main_progressive_training.py --resume-from <last_period>
```

### Missing Data Files
The pipeline automatically skips missing time periods with a warning. Check that data files exist in:
- `data/east/<period>/`
- `data/west/<period>/`

### Model Loading Errors
Ensure the checkpoint path is correct:
```bash
ls outputs/progressive_east/period_BC/  # Verify directory structure
```

## Batch Chat Test

To run batch chat tests standalone:

```bash
python batch_chat_test.py \
  --checkpoint outputs/progressive_east/period_500/checkpoint-500 \
  --output results.json \
  --max-new-tokens 200 \
  --temperature 0.8
```

The script will:
1. Load the trained model
2. Run 24 philosophical prompts with conversation history
3. Save responses to JSON file
4. Print summary statistics

Output format:
```json
{
  "timestamp": "2026-03-23T10:45:00.123456",
  "checkpoint": "...",
  "device": "cuda",
  "config": {...},
  "responses": [
    {
      "prompt": "What is the meaning of life?",
      "response": "The meaning of life...",
      "response_length": 145
    },
    ...
  ]
}
```

## Example: Complete Workflow

```bash
# Train on just BC and first 3 time periods (fastest for testing)
python main_progressive_training.py \
  --periods "older (BC)" 100 200 300 \
  --max-steps 5000 \
  --output-dir ./test_run

# Check results
ls -la test_run/progressive_evaluations/
cat test_run/training_manifest.json | jq .

# View bias evaluation
cat test_run/progressive_evaluations/period_300_evaluation/bias_evaluation_*.json | jq .

# View chat responses
cat test_run/progressive_evaluations/period_300_evaluation/chat_responses_east.json | jq '.responses[0]'
```

## Integration with Other Scripts

The pipeline uses and integrates with existing scripts:
- `gpt2_pretrain.py`: Model and dataset building
- `lm_utils.py`: Training utilities and data loading
- `evaluate_bias.py`: Philosophical bias comparison with cross-perplexity and KL divergence
- `inference_utils.py`: Model loading and text generation
- `batch_chat_test.py`: Non-interactive chat testing

All integration is handled automatically by `main_progressive_training.py`.
