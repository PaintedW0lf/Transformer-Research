"""SFT (Supervised Fine-Tuning) for philosophical models.

SFT fine-tunes a pre-trained model on instruction-response pairs.
This is the first post-training step after pre-training.

Pipeline:
1. generate_sft_data.py → creates (instruction, response) pairs
2. sft_train.py → fine-tunes model on those pairs
3. evaluate_sft.py → compares base vs SFT model
"""

import json
from pathlib import Path

import torch
from torch.utils.data import Dataset
from tqdm import tqdm
from transformers import AutoModelForCausalLM, TrainingArguments, Trainer

from inference_utils import get_tokenizer


class SFTDataset(Dataset):
    """Dataset for supervised fine-tuning.

    Each item: (instruction, response) formatted as:
        Human: {instruction}\nAssistant: {response}
    """

    def __init__(self, data_path: str, max_length: int = 512):
        with open(data_path) as f:
            self.data = json.load(f)
        self.max_length = max_length
        self.tokenizer = get_tokenizer()

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> dict:
        item = self.data[idx]
        text = f"Human: {item['instruction']}\nAssistant: {item['response']}"

        tokens = self.tokenizer.encode(text)
        if len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]

        return {"input_ids": tokens}


class SFTDataCollator:
    """Data collator for SFT with padding."""

    def __init__(self, pad_id: int):
        self.pad_id = pad_id

    def __call__(self, features: list[dict]) -> dict:
        max_len = max(len(f["input_ids"]) for f in features)
        input_ids = []
        labels = []
        attention_mask = []

        for f in features:
            ids = f["input_ids"]
            pad_len = max_len - len(ids)

            padded = ids + [self.pad_id] * pad_len
            label = ids + [-100] * pad_len
            mask = [1] * len(ids) + [0] * pad_len

            input_ids.append(padded)
            labels.append(label)
            attention_mask.append(mask)

        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "attention_mask": torch.tensor(attention_mask, dtype=torch.long),
        }


def train_sft(
    model_path: str,
    sft_data_path: str,
    output_dir: str,
    learning_rate: float = 2e-5,
    num_epochs: int = 3,
    batch_size: int = 4,
    max_length: int = 512,
    warmup_ratio: float = 0.1,
    logging_steps: int = 10,
    save_strategy: str = "epoch",
):
    """Train a model using SFT on instruction-response data."""
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading model from {model_path}...")
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16 if device == "cuda" and torch.cuda.is_bf16_supported() else torch.float32,
    )

    print(f"Loading SFT data from {sft_data_path}...")
    dataset = SFTDataset(sft_data_path, max_length=max_length)
    print(f"Dataset size: {len(dataset)} samples")

    tokenizer = get_tokenizer()
    pad_id = tokenizer.eot_token

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        num_train_epochs=num_epochs,
        warmup_ratio=warmup_ratio,
        logging_steps=logging_steps,
        save_strategy=save_strategy,
        save_total_limit=2,
        bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
        max_grad_norm=1.0,
        report_to=[],
        logging_first_step=True,
        optim="adamw_torch_fused",
        dataloader_num_workers=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=SFTDataCollator(pad_id=pad_id),
    )

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Starting SFT training...")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Epochs: {num_epochs}")
    print(f"  Batch size: {batch_size} (effective: {batch_size * 4})")
    print(f"  Max length: {max_length}")
    print()

    trainer.train()

    final_path = Path(output_dir) / "final"
    model.save_pretrained(final_path)
    print(f"SFT training complete! Final model saved to {final_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SFT training for philosophical alignment")
    parser.add_argument("--model-path", type=str, required=True, help="Path to pre-trained model checkpoint")
    parser.add_argument("--sft-data", type=str, required=True, help="Path to SFT JSON data")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    args = parser.parse_args()

    train_sft(
        model_path=args.model_path,
        sft_data_path=args.sft_data,
        output_dir=args.output_dir,
        learning_rate=args.learning_rate,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        max_length=args.max_length,
        warmup_ratio=args.warmup_ratio,
    )
