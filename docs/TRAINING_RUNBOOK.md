# Training Runbook

All exact commands run during pretraining, in order.

---

## Server Workflow (General)

```bash
# SSH into server, then:
tmux new -s training

# Run training:
python gpt2_pretrain.py --subdir east --output-dir ./outputs/eastern_model

# Ctrl+B then D to detach
# tmux attach -t training   ← to reattach later
```

---

## Round 1 — First Two Models (checkpoint-5000)

Trained east and west models to 5000 steps using the general flow above.

```bash
python gpt2_pretrain.py --subdir east --output-dir ./outputs/eastern_model
python gpt2_pretrain.py --subdir west --output-dir ./outputs/western_model
```

---

## Round 2 — v2 Models (checkpoint-1500 → 15000 target)

```bash
git pull

# tmux 1 — East
tmux new -s east2
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=0 python3 gpt2_pretrain.py --subdir east --output-dir ./outputs/eastern_model_v2 --max-steps 15000
# Ctrl+B D

# tmux 2 — West
tmux new -s west2
source .venv/bin/activate
CUDA_VISIBLE_DEVICES=1 python3 gpt2_pretrain.py --subdir west --output-dir ./outputs/western_model_v2 --max-steps 15000
# Ctrl+B D
```

---

## Evaluation

### Quick test at checkpoint-100 - added padding in gpt training to test repitation

```bash
python3 evaluate_bias.py \
  --western-path outputs/western_test/checkpoint-100 \
  --eastern-path outputs/eastern_test/checkpoint-100 \
  --output-dir outputs/test_evaluation
```

---

## Post-Training Strategy invented after pre training (LoRA + SFT)

Reference: https://www.kaggle.com/code/ahmetyasin1/post-training-deep-dive-sft-dpo-with-trl

Full pipeline: Could be added as future improvements- can be seen in branch post-training-plans

```bash
# Step 1: Train 15000-step base models (if not done yet)
CUDA_VISIBLE_DEVICES=0 python3 gpt2_pretrain.py --subdir east --output-dir ./outputs/eastern_model_v2 --max-steps 15000

# Step 2: Generate SFT data from improved base
python3 generate_sft_data.py \
  --model-path outputs/eastern_model_v2/checkpoint-15000 \
  --output data/sft_east_v2.json \
  --region east

# Step 3: LoRA + SFT training
python3 lora_train.py \
  --model-path outputs/eastern_model_v2/checkpoint-15000 \
  --sft-data data/sft_east_v2.json \
  --output-dir outputs/eastern_lora_sft

# Step 4: Merge LoRA back into base model
python3 merge_lora.py \
  --base-model outputs/eastern_model_v2/checkpoint-15000 \
  --lora-adapter outputs/eastern_lora_sft/lora_adapter \
  --output-dir outputs/eastern_lora_sft/merged

# Step 5: Evaluate
python3 evaluate_sft.py \
  --base-model outputs/eastern_model_v2/checkpoint-15000 \
  --sft-model outputs/eastern_lora_sft/merged \
  --output-dir outputs/lora_sft_evaluation
```

Why LoRA + SFT over plain SFT:
- Only trains ~1% of parameters (faster, less memory)
- Small adapter file (~10MB vs ~500MB for full model)
- Can stack multiple adapters on one base
- Less risk of destroying base model knowledge

### Post training results 
- https://github.com/bohuie/LLMTraining/pull/12 - Check PR for results 
- To keep repetition in check we modified repitition penality and modified temperature to have better results without post training. 
