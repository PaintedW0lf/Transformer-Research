# Progressive Philosophical Training Pipeline

## What Changed

Added a progressive training pipeline that trains language models sequentially through historical time periods (BC → 2000 CE), where each model is trained on cumulative data from all previous periods. This enables analysis of how philosophical ideas evolve over time.

### Files Added
- `main_progressive_training.py` - Main training orchestrator
- `batch_chat_test.py` - Non-interactive model evaluation
- `preview_training.py` - Preview tool (no training)
- `PROGRESSIVE_TRAINING_README.md` - Usage guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details

### Files Updated
- `download_pretraining_data.py` - Updated for progressive training data workflow

### Key Features
- **Progressive training**: BC only → BC+100 → BC+100+200 → ... → full history
- **Dual regions**: Separate East and West philosophical models
- **Dynamic scaling**: Training steps scale with corpus size
- **Automated evaluation**: Bias comparison and chat testing after each period
- **Resumable**: Can continue from any interrupted period

## How to Use

**See [`PROGRESSIVE_TRAINING_README.md`](./PROGRESSIVE_TRAINING_README.md) for complete usage with examples.**

Quick start:
```bash
python main_progressive_training.py              # Run full pipeline
python preview_training.py                       # Preview without training
python main_progressive_training.py --periods "older (BC)" 100 200 --regions east  # Specific periods
```

## How Data Works

**See [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md) for data organization and architecture.**

Key points:
- **21 cumulative periods**: BC, 100, 200, ..., 2000
- **Cumulative loading**: Period 200 = BC + 100 + 200 texts combined
- **Two regions**: East (119 texts total) and West (75 texts total)
- **Smart scaling**: Training steps automatically adjust based on corpus size

## No Breaking Changes

- Adds new functionality only
- Does not modify existing workflows or APIs
- All integration with existing code (`gpt2_pretrain.py`, `evaluate_bias.py`, etc.)

---

**For detailed usage:** [`PROGRESSIVE_TRAINING_README.md`](./PROGRESSIVE_TRAINING_README.md)
**For architecture/data details:** [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md)
