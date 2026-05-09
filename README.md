# Transformer Research: LLM Training with Philosophical Data

## 📋 Project Overview

**Transformer Research** is an advanced language model pretraining framework designed to investigate how philosophical ideas evolve across historical time periods and geographic regions (Eastern vs. Western traditions). This project implements progressive pretraining on GPT-2 and DeepSeek-R1 models, tracking philosophical bias and knowledge development across 21 cumulative time periods from BCE to 2000 CE.

### Key Innovation

Rather than training a single model on all data, this framework trains **separate models for each cumulative historical period**, allowing researchers to observe how philosophical traditions diverge, converge, and influence each other over time. Each model incorporates all previous periods' data, creating a progressive snapshot of philosophical evolution.

---

## 🎯 Core Capabilities

| Feature | Description |
|---------|-------------|
| **Progressive Training** | Train cumulative models across 21 historical time periods (BC → 2000 CE) |
| **Dual Regional Models** | Separate Eastern and Western philosophical tradition models for comparative analysis |
| **Philosophical Bias Analysis** | Measure cross-perplexity and KL divergence between model outputs |
| **Automated Evaluation** | Batch chat testing and bias evaluation after each training cycle |
| **Production-Ready** | Error handling, checkpointing, resume support, comprehensive logging |
| **Flexible Configuration** | Customize periods, regions, learning rates, training steps, and more |

---

## 🚀 Quick Start

### Prerequisites
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run Training
```bash
# Preview what will train without GPU
python preview_training.py

# Start full pipeline (all 21 periods, both regions)
python main_progressive_training.py

# Train specific periods only (faster for testing)
python main_progressive_training.py --periods "older (BC)" 100 200 --regions east

# Custom configuration
python main_progressive_training.py \
  --max-steps 20000 \
  --learning-rate 5e-4 \
  --output-dir ./my_results
```

---

## 📊 Project Architecture

### Data Structure

The framework works with data organized into **time periods** and **regions**:

```
data/
├── east/
│   ├── older_bc/      # BCE philosophical texts (Chinese, Indian, etc.)
│   ├── 100/           # 0-100 CE texts
│   ├── 200/           # 100-200 CE texts
│   └── ...2000/       # 1900-2000 CE texts
└── west/
    ├── older_bc/      # Pre-Socratic, Classical Greek, Roman
    ├── 100/           # Early Christian, Roman Stoics
    └── ...2000/       # Modern Western philosophy
```

**Progressive Data Accumulation:**
- Period 100: BC data + 100 CE data
- Period 200: BC data + 100 CE data + 200 CE data
- Period 2000: All 21 periods combined

### Training Pipeline

```
Progressive Training Pipeline
│
├─ Input: Time period (e.g., "300")
│
├─ Data Loading:
│   └─ Load cumulative texts: BC + 100 + 200 + 300
│
├─ Model Training (for each region: east, west):
│   ├─ Build GPT2 model from scratch
│   ├─ Create dataset from cumulative texts
│   ├─ Train with HuggingFace Trainer
│   └─ Save checkpoint
│
├─ Evaluation (when both models trained):
│   ├─ Run evaluate_bias.py: Cross-perplexity & KL divergence analysis
│   ├─ Run batch_chat_test.py: Generate responses to 24 philosophical prompts
│   └─ Save results to JSON
│
└─ Output:
    ├─ training_manifest.json
    ├─ Model checkpoints
    └─ Evaluation results
```

---

## 📁 File Organization

### Main Scripts

| Script | Purpose |
|--------|---------|
| `main_progressive_training.py` | Orchestration script for the entire pipeline (500+ lines) |
| `batch_chat_test.py` | Non-interactive chat test runner for model evaluation |
| `preview_training.py` | Preview training plan without GPU processing |
| `gpt2_pretrain.py` | GPT-2 model and trainer building |
| `deepseek_r1_pretrain.py` | DeepSeek-R1 model and trainer building |
| `evaluate_bias.py` | Philosophical bias comparison with cross-perplexity and KL divergence |
| `lm_utils.py` | Training utilities and data loading functions |
| `inference_utils.py` | Model loading and text generation utilities |

### Documentation

| Document | Content |
|----------|---------|
| `docs/PROGRESSIVE_TRAINING_README.md` | Complete guide to the progressive training pipeline |
| `docs/IMPLEMENTATION_SUMMARY.md` | Technical implementation details and architecture |
| `docs/KL_DIVERGENCE.md` | KL divergence metrics documentation |
| `docs/CLUSTER_GUIDE.md` | Distributed training setup on computing clusters |
| `docs/TRAINING_RUNBOOK.md` | Step-by-step training execution guide |
| `docs/VOCAB_BUBBLES.md` | Vocabulary analysis and visualization |
| `docs/SOURCES_RATIONALE.md` | Philosophical source selection and validation (55KB reference) |
| `docs/LLM_Training_Effects___Vanshika.pdf` | Research on LLM training effects and biases |

### Example Layout

```
LLMTraining/
├── README.md
├── requirements.txt
├── main_progressive_training.py (500+ lines)
├── batch_chat_test.py (150+ lines)
├── preview_training.py (150+ lines)
├── gpt2_pretrain.py
├── deepseek_r1_pretrain.py
├── evaluate_bias.py
├── lm_utils.py
├── inference_utils.py
├── tests/
│   ├── test_lm_utils.py
│   ├── test_pretrain_builders.py
│   ├── test_streaming.py
│   ├── test_kl_divergence.py
│   ├── test_stats_analysis.py
│   ├── test_evaluate_bias.py
│   ├── test_visualize_vocab.py
│   ├── test_pipeline_cli.py
│   └── chat_test.py
├── scripts/
│   ├── cluster_setup.sh
│   ├── cluster_train.sh
│   ├── cluster_train_both.sh
│   └── cluster_download_data.sh
├── docs/
│   ├── PROGRESSIVE_TRAINING_README.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── KL_DIVERGENCE.md
│   ├── CLUSTER_GUIDE.md
│   ├── TRAINING_RUNBOOK.md
│   ├── VOCAB_BUBBLES.md
│   ├── SOURCES_RATIONALE.md
│   └── LLM_Training_Effects___Vanshika.pdf
├── data/
│   ├── east/
│   │   ├── older_bc/
│   │   ├── 100/
│   │   └── ...2000/
│   └── west/
│       ├── older_bc/
│       ├── 100/
│       └── ...2000/
└── outputs/
    ├── training_manifest.json
    ├── progressive_east/
    │   ├── period_BC/checkpoint-500/
    │   ├── period_100/checkpoint-500/
    │   └── ...
    ├── progressive_west/
    │   └── [same structure]
    └── progressive_evaluations/
        ├── period_BC_evaluation/
        ├── period_100_evaluation/
        └── ...
```

---

## 🕐 Available Time Periods

The framework supports **21 cumulative time periods**:

| # | Period | Years | Coverage |
|---|--------|-------|----------|
| 1 | `older (BC)` | BCE | Ancient philosophy (Vedic, Pre-Socratic, Classical) |
| 2-11 | `100` - `1000` | 0-1000 CE | Early medieval (Buddhist, Islamic, Christian, Tang) |
| 12-21 | `1100` - `2000` | 1000-2000 CE | Late medieval to contemporary philosophy |

Each period **cumulatively** includes all previous periods' data, allowing analysis of how knowledge builds over time.

---

## 🔧 Configuration & Usage

### Training Parameters

```bash
python main_progressive_training.py [OPTIONS]

Options:
  --periods [periods...]       # Periods to train: "older (BC)", 100, 200, ... 2000
  --regions [regions...]       # Regions: east, west, or both (default: both)
  --max-steps N                # Training steps per model (default: 10000)
  --learning-rate LR           # Learning rate (default: 5e-4)
  --output-dir DIR             # Output directory (default: ./outputs)
  --data-dir DIR               # Data directory (default: ./data)
  --skip-evaluation            # Skip evaluation steps for faster training
  --resume-from PERIOD         # Resume from specific period if interrupted
```

### Common Use Cases

**Fast Test Run (3 periods, east only, 5k steps):**
```bash
python main_progressive_training.py \
  --periods "older (BC)" 100 200 \
  --regions east \
  --max-steps 5000 \
  --output-dir ./test_run
```

**Full Pipeline (all periods, both regions, default config):**
```bash
python main_progressive_training.py
```

**Resume After Interruption:**
```bash
python main_progressive_training.py --resume-from 500
```

---

## 📈 Output Structure

After training, results are organized as:

```
outputs/
├── training_manifest.json           # Track of all trained models with timestamps
│
├── progressive_east/                # Eastern philosophical models
│   ├── period_BC/checkpoint-500/    # Best checkpoint for BC period
│   ├── period_100/checkpoint-500/
│   └── ...period_2000/checkpoint-500/
│
├── progressive_west/                # Western philosophical models
│   ├── period_BC/checkpoint-500/
│   ├── period_100/checkpoint-500/
│   └── ...period_2000/checkpoint-500/
│
└── progressive_evaluations/         # Evaluation results
    ├── period_BC_evaluation/
    │   ├── bias_evaluation_*.json    # Bias comparison with cross-perplexity & KL divergence
    │   ├── chat_responses_east.json  # Chat test results (24 philosophical prompts)
    │   └── chat_responses_west.json
    ├── period_100_evaluation/
    └── ...period_2000_evaluation/
```

### Evaluation Metrics

**Bias Evaluation** includes:
- **Cross-Perplexity**: How well each model understands the other's output
- **KL Divergence**: Probability distribution differences between models
- **8 Philosophical Categories**: Self-identity, purpose, ethics, reality, knowledge, death, nature, enlightenment

**Chat Test Results** capture model responses to:
- 24 philosophical prompts across all 8 categories
- Multi-turn conversation history tracking
- Response length and quality metrics

---

## 📊 Research Insights

### LLM Training Effects (from Vanshika's Research)

The `LLM_Training_Effects___Vanshika.pdf` document provides empirical analysis of:
- How philosophical biases emerge during training
- East vs. West philosophical tradition differences
- Convergence patterns across time periods
- Implications for interpretable AI and cultural representation

### Source Selection Methodology

The `SOURCES_RATIONALE.md` document (55KB) provides:
- **Complete audit** against Wikipedia timelines (Eastern & Western philosophers)
- **Reasoning** for every included philosopher
- **Gap analysis** showing 500+ philosophers across traditions
- **Status tracking** for 378 philosophical texts
- **Coverage**: ~232 fetchable works, ~146 unavailable (with explicit reasons)

---

## ⚙️ Performance Expectations

### Training Time (per model)
| Period | Dataset Size | Typical Duration |
|--------|--------------|-----------------|
| BC | Smallest | 5-10 minutes |
| 100-300 | Medium | 10-25 minutes |
| 500-1000 | Large | 30-50 minutes |
| 1500-2000 | Largest | 60-90 minutes |

### Full Pipeline (all 21 periods × 2 regions)
- **Minimum**: 2-3 hours (with skip-evaluation)
- **Typical**: 8-12 hours (with evaluation)
- **Maximum**: 18-24 hours (full evaluation + verbose logging)

### Hardware Requirements
- **GPU**: RTX 6000 Ada or equivalent (~45GB VRAM)
- **Storage**: 50-100GB for all checkpoints and results
- **CPU**: 8+ cores recommended for data loading

### Memory Optimization

```bash
# Reduce batch size if OOM errors occur
# Edit DEFAULT_CONFIG in main_progressive_training.py:
# DEFAULT_CONFIG['per_device_train_batch_size'] = 4  # reduce from 8
# DEFAULT_CONFIG['gradient_accumulation_steps'] = 2  # reduce from 4
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Test Categories
- **Unit Tests**: `test_lm_utils.py`, `test_pretrain_builders.py`
- **Integration Tests**: `test_pipeline_cli.py`, `test_streaming.py`
- **Metrics Tests**: `test_kl_divergence.py`, `test_stats_analysis.py`
- **Analysis Tests**: `test_evaluate_bias.py`, `test_visualize_vocab.py`
- **Interactive Tests**: `chat_test.py` for checkpoint inference

### Interactive Checkpoint Chat
```bash
python tests/chat_test.py --checkpoint outputs/progressive_east/period_500/checkpoint-500
```

---

## 📚 Data Format

### Text Data Requirements
- **Format**: Plain text (UTF-8), `.txt` extension
- **Location**: `data/east/<period>/` and `data/west/<period>/`
- **Naming**: Files are read in sorted order; name accordingly
- **Concatenation**: Multiple `.txt` files are automatically concatenated

### Example
```
data/west/100/
├── 01_early_christian_0100ce.txt
├── 02_roman_stoic_0100ce.txt
└── 03_patristic_writings_0100ce.txt
```

---

## 🛠️ Utility Scripts

### Cluster Setup & Training
```bash
# Setup distributed training environment
bash scripts/cluster_setup.sh

# Train on single cluster node
bash scripts/cluster_train.sh

# Train on east/west clusters simultaneously
bash scripts/cluster_train_both.sh

# Download public pretraining data
bash scripts/cluster_download_data.sh
```

See `docs/CLUSTER_GUIDE.md` for detailed cluster setup instructions.

---

## 📖 Documentation

Comprehensive documentation is provided:

1. **PROGRESSIVE_TRAINING_README.md** — Complete usage guide
2. **IMPLEMENTATION_SUMMARY.md** — Technical architecture and features
3. **KL_DIVERGENCE.md** — Metrics and mathematics behind KL divergence analysis
4. **SOURCES_RATIONALE.md** — Philosophical source selection and audit trail
5. **CLUSTER_GUIDE.md** — Distributed training setup
6. **TRAINING_RUNBOOK.md** — Step-by-step execution
7. **VOCAB_BUBBLES.md** — Vocabulary analysis tools
8. **LLM_Training_Effects___Vanshika.pdf** — Research on training effects

---

## 🔍 Troubleshooting

### Out of Memory (OOM) Errors
Reduce batch size or gradient accumulation in `DEFAULT_CONFIG` within `main_progressive_training.py`.

### Training Interrupted
Resume from the last completed period using `--resume-from <period>`.

### Missing Data Files
The pipeline automatically skips missing periods with a warning. Verify data exists in:
```bash
ls data/east/older_bc/
ls data/west/older_bc/
```

### Model Loading Errors
Check checkpoint path and directory structure:
```bash
ls outputs/progressive_east/period_BC/
```

---

## 🔗 Integration Points

The framework integrates seamlessly with existing utilities:

| Component | Usage | Source |
|-----------|-------|--------|
| Model Building | GPT2 from scratch | `gpt2_pretrain.py:build_gpt2_from_scratch()` |
| Data Loading | Texts from directories | `lm_utils.py:load_texts_from_data_dir()` |
| Training | HuggingFace Trainer | `lm_utils.py:build_trainer()` |
| Tokenization | GPT2 encoding | tiktoken via `lm_utils.py` |
| Bias Evaluation | Cross-perplexity & KL divergence | `evaluate_bias.py:evaluate_models()` |
| Inference | Text generation | `inference_utils.py:generate_with_history()` |

---

## ✨ Features Highlight

✅ **Cumulative Training** — Each model includes all previous periods
✅ **Dual Regions** — East/West comparative analysis  
✅ **Automated Evaluation** — Bias & chat tests after each period  
✅ **Progress Tracking** — Training manifest with full audit trail  
✅ **Resume Support** — Pause and resume at any period  
✅ **Flexible Configuration** — CLI customization for all parameters  
✅ **Comprehensive Logging** — Detailed logs at every stage  
✅ **Preview Mode** — Dry-run without GPU  
✅ **Error Handling** — Graceful handling of edge cases  
✅ **Production-Ready** — Well-tested, documented, extensible  

---

## 🚀 Getting Started

**Step 1:** Clone and setup
```bash
git clone <repository>
cd Transformer-Research
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Step 2:** Prepare data
```bash
# Place philosophical texts in data/east/<period>/ and data/west/<period>/
# See Data Format section above
```

**Step 3:** Preview training plan
```bash
python preview_training.py
```

**Step 4:** Run training
```bash
python main_progressive_training.py --periods "older (BC)" 100 200 --max-steps 5000
```

**Step 5:** Analyze results
```bash
cat outputs/training_manifest.json | jq .
cat outputs/progressive_evaluations/period_200_evaluation/bias_evaluation_*.json | jq .
```

---

## 📝 Notes

- All outputs are written to `outputs/` directory
- For very large corpora, consider using streaming dataset with `load_dataset()` 
- GPU memory usage can be adjusted via batch size and gradient accumulation
- Complete philosophical source bibliography available in `docs/SOURCES_RATIONALE.md`

---

## 🙏 Acknowledgments

Research on LLM training effects and philosophical bias analysis by **Vanshika**.

---

**Version**: 1.0  
**Last Updated**: 2026-05-09  
**Status**: Production-Ready
