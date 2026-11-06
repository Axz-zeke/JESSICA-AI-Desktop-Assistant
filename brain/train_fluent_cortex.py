"""
Jessica Brain - Scaled Fluent Cortex FP16 Tensor Core Trainer
Trains JessicaCortexLM (51.1M Parameters) on RTX 4060 using:
- FlashAttention (PyTorch 2.5 SDPA)
- Automatic Mixed Precision (AMP FP16)
- Target-Only Loss Masking (ignore_index=-100)
- AdamW (weight_decay=0.05, betas=(0.9, 0.95)) + Grad Clip (1.0)
- Cosine Annealing Learning Rate Schedule with Warmup
- Multi-Stage Validation Perplexity Tracking (Stage 1, 2, 3)
"""

import os
import sys
import json
import math
import time
import random
from pathlib import Path
from typing import List, Dict, Tuple, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.cortex_net import JessicaCortexLM
from brain.bpe_tokenizer import JessicaBPETokenizer, VOCAB_SIZE_ALIGNED


class EnglishCurriculumDataset(Dataset):
    """
    Dataset wrapping english_mastery_corpus.jsonl with BPE tokenization and target masking.
    """
    def __init__(self, data_items: List[Dict[str, Any]], tokenizer: JessicaBPETokenizer, max_seq_len: int = 192):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.samples = []

        for item in data_items:
            user_msg = item.get("user", "")
            completion = item.get("completion", "")
            stage = item.get("stage", 1)
            category = item.get("category", "")

            seq_dict = self.tokenizer.format_training_sequence(
                user_msg=user_msg,
                completion=completion,
                context="none",
                action="none"
            )

            full_ids = seq_dict["full_ids"]
            targets = seq_dict["targets"]

            # Truncate if exceeding max_seq_len
            if len(full_ids) > max_seq_len:
                full_ids = full_ids[:max_seq_len]
                targets = targets[:max_seq_len]

            self.samples.append({
                "stage": stage,
                "category": category,
                "full_ids": full_ids,
                "targets": targets,
                "seq_len": len(full_ids)
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def collate_fn(batch, pad_token_id: int = 50259):
    """
    Dynamic batch padding to the longest sequence in the batch.
    """
    max_len = max(len(item["full_ids"]) for item in batch)
    # Ensure multiple of 8 for optimal tensor core execution
    max_len = min(256, ((max_len + 7) // 8) * 8)

    batch_input_ids = []
    batch_targets = []
    stages = []

    for item in batch:
        ids = list(item["full_ids"])
        tgts = list(item["targets"])

        pad_len = max_len - len(ids)
        if pad_len > 0:
            ids = ids + [pad_token_id] * pad_len
            tgts = tgts + [-100] * pad_len
        else:
            ids = ids[:max_len]
            tgts = tgts[:max_len]

        batch_input_ids.append(ids)
        batch_targets.append(tgts)
        stages.append(item["stage"])

    return {
        "input_ids": torch.tensor(batch_input_ids, dtype=torch.long),
        "targets": torch.tensor(batch_targets, dtype=torch.long),
        "stages": stages
    }


def get_cosine_lr(step: int, warmup_steps: int, total_steps: int, lr_max: float = 3e-4, lr_min: float = 1e-5) -> float:
    """
    Cosine learning rate with linear warmup.
    """
    if step < warmup_steps:
        return lr_max * (step + 1) / (warmup_steps + 1)
    if step > total_steps:
        return lr_min
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * progress))


@torch.no_grad()
def evaluate_validation(
    model: nn.Module,
    val_loader: DataLoader,
    device: torch.device
) -> Dict[str, float]:
    """
    Compute validation loss and perplexity across overall dataset and individual stages.
    """
    model.eval()
    total_loss = 0.0
    total_tokens = 0

    stage_losses = {1: 0.0, 2: 0.0, 3: 0.0}
    stage_counts = {1: 0, 2: 0, 3: 0}

    for batch in val_loader:
        input_ids = batch["input_ids"].to(device)
        targets = batch["targets"].to(device)
        stages = batch["stages"]

        with torch.amp.autocast("cuda", dtype=torch.float16):
            logits = model(input_ids)
            shift_logits = logits[..., :-1, :].contiguous()
            shift_targets = targets[..., 1:].contiguous()

            # Per-token cross entropy
            loss_flat = F.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_targets.view(-1),
                ignore_index=-100,
                reduction="none"
            )

            mask = shift_targets.view(-1) != -100
            n_tokens = mask.sum().item()
            if n_tokens > 0:
                b_loss = loss_flat[mask].sum().item()
                total_loss += b_loss
                total_tokens += n_tokens

                # Track by stage
                stg = stages[0] if stages else 1
                stage_losses[stg] = stage_losses.get(stg, 0.0) + b_loss
                stage_counts[stg] = stage_counts.get(stg, 0) + n_tokens

    mean_loss = total_loss / max(total_tokens, 1)
    ppl = math.exp(min(mean_loss, 20.0))

    res = {
        "val_loss": round(mean_loss, 4),
        "val_ppl": round(ppl, 2),
    }

    for s in (1, 2, 3):
        if stage_counts[s] > 0:
            s_loss = stage_losses[s] / stage_counts[s]
            res[f"stage{s}_loss"] = round(s_loss, 4)
            res[f"stage{s}_ppl"] = round(math.exp(min(s_loss, 20.0)), 2)

    return res


def train_fluent_cortex(
    corpus_path: Path = WORKSPACE_ROOT / "datasets" / "english_mastery_corpus.jsonl",
    output_checkpoint: Path = WORKSPACE_ROOT / "brain" / "cortex_v5_fluent.pt",
    epochs: int = 3,
    batch_size: int = 32,
    lr_max: float = 3.5e-4,
    warmup_steps: int = 80
):
    print("=" * 70)
    print("JESSICA PHASE 6: SCALED CORTEX TRAINING (cortex_v5_fluent.pt)")
    print("=" * 70)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    tokenizer = JessicaBPETokenizer()
    print(f"BPE Tokenizer loaded: {tokenizer.actual_vocab_size} tokens (aligned to {VOCAB_SIZE_ALIGNED})")

    # 1. Load Corpus
    print(f"Loading curriculum corpus: {corpus_path}")
    raw_data = []
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                raw_data.append(json.loads(line))

    print(f"Loaded {len(raw_data):,} total samples.")
    random.seed(42)
    random.shuffle(raw_data)

    # 95% Train, 5% Val
    split_idx = int(len(raw_data) * 0.95)
    train_raw = raw_data[:split_idx]
    val_raw = raw_data[split_idx:]
    print(f"Train split: {len(train_raw):,} samples | Val split: {len(val_raw):,} samples")

    train_dataset = EnglishCurriculumDataset(train_raw, tokenizer, max_seq_len=192)
    val_dataset = EnglishCurriculumDataset(val_raw, tokenizer, max_seq_len=192)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda b: collate_fn(b, pad_token_id=tokenizer.pad_token_id),
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=lambda b: collate_fn(b, pad_token_id=tokenizer.pad_token_id),
        pin_memory=True
    )

    # 2. Instantiate JessicaCortexLM (51.1M Parameters)
    model = JessicaCortexLM(
        vocab_size=VOCAB_SIZE_ALIGNED,
        d_model=512,
        n_heads=8,
        num_layers=8,
        d_ff=2048,
        max_seq_len=256,
        dropout=0.05
    ).to(device)

    total_params = model.count_parameters()
    print(f"JessicaCortexLM Model instantiated: {total_params:,} parameters ({total_params / 1e6:.2f}M)")

    # 3. Setup Optimizer & Scheduler
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr_max,
        weight_decay=0.05,
        betas=(0.9, 0.95)
    )
    scaler = torch.amp.GradScaler("cuda")

    total_steps = len(train_loader) * epochs
    print(f"Total training steps: {total_steps:,} ({epochs} epochs x {len(train_loader)} batches/epoch)")

    # Baseline evaluation before training
    print("Evaluating initial baseline perplexity...")
    initial_val = evaluate_validation(model, val_loader, device)
    print(f"Initial Baseline -> Val Loss: {initial_val['val_loss']} | Val PPL: {initial_val['val_ppl']}")

    step = 0
    start_time = time.perf_counter()
    history = []

    print("\n--- Starting High-Throughput Tensor Core Training ---")
    for epoch in range(1, epochs + 1):
        model.train()
        epoch_loss = 0.0
        epoch_tokens = 0
        epoch_start = time.perf_counter()

        for batch_idx, batch in enumerate(train_loader):
            step += 1
            lr = get_cosine_lr(step, warmup_steps, total_steps, lr_max=lr_max)
            for param_group in optimizer.param_groups:
                param_group["lr"] = lr

            input_ids = batch["input_ids"].to(device, non_blocking=True)
            targets = batch["targets"].to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            # Mixed precision forward & backward
            with torch.amp.autocast("cuda", dtype=torch.float16):
                logits, loss = model(input_ids, targets=targets)

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()

            # Metrics
            n_tokens = (targets != -100).sum().item()
            epoch_loss += loss.item() * n_tokens
            epoch_tokens += n_tokens

            if step % 150 == 0 or step == total_steps:
                elapsed = time.perf_counter() - epoch_start
                tok_per_sec = epoch_tokens / max(elapsed, 1e-4)
                cur_loss = loss.item()
                cur_ppl = math.exp(min(cur_loss, 20.0))
                print(f"Epoch {epoch}/{epochs} | Step {step}/{total_steps} | LR {lr:.2e} | Loss {cur_loss:.4f} | PPL {cur_ppl:.2f} | Speed: {tok_per_sec:,.0f} tok/s")

        # End of Epoch Validation
        epoch_duration = time.perf_counter() - epoch_start
        val_metrics = evaluate_validation(model, val_loader, device)
        print(f"\n[EPOCH {epoch} COMPLETE] Duration: {epoch_duration:.2f}s | Val Loss: {val_metrics['val_loss']} | Val PPL: {val_metrics['val_ppl']}")
        print(f"  Stage 1 (Everyday English): Loss {val_metrics.get('stage1_loss', 'N/A')} | PPL {val_metrics.get('stage1_ppl', 'N/A')}")
        print(f"  Stage 2 (World Knowledge):  Loss {val_metrics.get('stage2_loss', 'N/A')} | PPL {val_metrics.get('stage2_ppl', 'N/A')}")
        print(f"  Stage 3 (Companion Persona): Loss {val_metrics.get('stage3_loss', 'N/A')} | PPL {val_metrics.get('stage3_ppl', 'N/A')}\n")

        history.append({
            "epoch": epoch,
            "step": step,
            "val_loss": val_metrics["val_loss"],
            "val_ppl": val_metrics["val_ppl"],
            "stage1_ppl": val_metrics.get("stage1_ppl"),
            "stage2_ppl": val_metrics.get("stage2_ppl"),
            "stage3_ppl": val_metrics.get("stage3_ppl")
        })

    total_training_time = time.perf_counter() - start_time
    print(f"Training successfully completed in {total_training_time:.2f}s ({total_training_time/60:.2f} min)!")

    # 4. Save Checkpoint
    output_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_data = {
        "model_state_dict": model.state_dict(),
        "arch_config": {
            "vocab_size": VOCAB_SIZE_ALIGNED,
            "d_model": 512,
            "n_heads": 8,
            "num_layers": 8,
            "d_ff": 2048,
            "max_seq_len": 256,
            "dropout": 0.05,
            "total_parameters": total_params
        },
        "training_history": history,
        "final_metrics": history[-1] if history else {},
        "timestamp": time.time()
    }
    torch.save(checkpoint_data, output_checkpoint)
    print(f"Saved cortex_v5_fluent.pt to: {output_checkpoint}")
    print(f"File size: {output_checkpoint.stat().st_size / (1024 * 1024):.2f} MB")
    print("=" * 70)

    return checkpoint_data


if __name__ == "__main__":
    train_fluent_cortex()

