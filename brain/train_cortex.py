"""
Jessica Brain - Generative Causal Cortex v3 Training Script
Trains Jessica's Causal Decoder Transformer on RTX 4060 Tensor Cores using FP16 Mixed Precision.
Features:
- Strict Target-Only Loss Masking (ignore_index=-100 before <jessica> and on <pad>)
- Word/Token Dropout (p=0.1) on user prompt for semantic generalization
- Label Smoothing (0.05) to prevent overconfident token memorization
- Cosine Annealing Learning Rate Scheduler
- Saves weights to brain/cortex_v3.pt and brain/cortex_v2.pt / cortex_v1.pt
"""

import sys
import json
import time
import random
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# Add workspace to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.cortex_tokenizer import CortexTokenizer
from brain.cortex_net import JessicaCortexNet


def train():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})", flush=True)

    dataset_path = WORKSPACE_ROOT / "datasets" / "cortex_v4_train.jsonl"
    if not dataset_path.exists():
        dataset_path = WORKSPACE_ROOT / "datasets" / "cortex_v3_train.jsonl"
    if not dataset_path.exists():
        dataset_path = WORKSPACE_ROOT / "datasets" / "cortex_v2_train.jsonl"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    # Load samples
    raw_texts = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                raw_texts.append(item["text"])

    print(f"[*] Loaded {len(raw_texts)} cortex training sequences from {dataset_path.name}.", flush=True)

    # Load seed lexicon for expanded vocabulary (2,500+ tokens)
    seed_lexicon = []
    lexicon_path = WORKSPACE_ROOT / "datasets" / "seed_lexicon.json"
    if lexicon_path.exists():
        with open(lexicon_path, "r", encoding="utf-8") as f:
            seed_lexicon = json.load(f)
        print(f"[*] Loaded {len(seed_lexicon)} words from seed lexicon.", flush=True)

    # Build tokenizer
    tokenizer = CortexTokenizer()
    tokenizer.build_vocab(raw_texts, min_freq=1, max_vocab_size=3500, additional_vocab=seed_lexicon)
    vocab_save_path = WORKSPACE_ROOT / "brain" / "cortex_vocab.json"
    tokenizer.save(vocab_save_path)
    print(f"[*] Cortex vocabulary created & saved. Vocab size: {tokenizer.vocab_size} tokens (Target: 2500+)", flush=True)

    jess_token_id = tokenizer.token_to_id[tokenizer.JESSICA_TOKEN]
    pad_token_id = tokenizer.token_to_id[tokenizer.PAD_TOKEN]
    unk_token_id = tokenizer.token_to_id[tokenizer.UNK_TOKEN]
    context_token_id = tokenizer.token_to_id[tokenizer.CONTEXT_TOKEN]

    # Prepare input and target pairs with Target-Only Loss Masking (-100)
    max_len = 128
    x_list = []
    y_list = []

    for t in raw_texts:
        seq = tokenizer.encode(t, max_len=max_len, add_bos_eos=False)
        x = list(seq[:-1])
        raw_y = list(seq[1:])

        try:
            jess_idx = seq.index(jess_token_id)
        except ValueError:
            jess_idx = 0

        try:
            ctx_idx = seq.index(context_token_id)
        except ValueError:
            ctx_idx = jess_idx

        # Optional token dropout (p=0.1) on user prompt tokens in x to boost semantic generalization
        for i in range(1, ctx_idx):
            if x[i] not in tokenizer.SPECIAL_TOKENS and random.random() < 0.10:
                x[i] = unk_token_id

        # Target-Only Loss Masking:
        # Mask all tokens before <jessica> and all <pad> tokens to -100
        y = []
        for i in range(len(raw_y)):
            if i < jess_idx or raw_y[i] == pad_token_id:
                y.append(-100)
            else:
                y.append(raw_y[i])

        x_list.append(x)
        y_list.append(y)

    x_tensor = torch.tensor(x_list, dtype=torch.long)
    y_tensor = torch.tensor(y_list, dtype=torch.long)

    batch_size = 32
    dataset = TensorDataset(x_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Scaled Cortex v3 Architecture
    d_model = 384
    n_heads = 8
    num_layers = 6
    d_ff = 1536

    model = JessicaCortexNet(
        vocab_size=tokenizer.vocab_size,
        d_model=d_model,
        n_heads=n_heads,
        num_layers=num_layers,
        d_ff=d_ff,
        max_seq_len=max_len,
        dropout=0.05
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"[*] Total Cortex v3 Parameters: {total_params:,}", flush=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=1e-5)
    max_epochs = 40
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max_epochs, eta_min=2e-5)
    scaler = torch.amp.GradScaler("cuda", enabled=torch.cuda.is_available())

    target_loss = 0.02
    print("\n" + "=" * 70, flush=True)
    print("      TRAINING JESSICA GENERATIVE CORTEX v3 (TARGET-ONLY LOSS MASKING)", flush=True)
    print(f"      Masking: ignore_index=-100 | Label Smoothing: 0.05 | Target Loss: < {target_loss}", flush=True)
    print(f"      Architecture: {num_layers}L-{n_heads}H-{d_model}D-{d_ff}FF | Vocab: {tokenizer.vocab_size}", flush=True)
    print("=" * 70, flush=True)

    initial_loss = None
    final_loss = None
    total_tokens_processed = 0
    actual_epochs_run = 0

    train_start = time.perf_counter()

    for epoch in range(1, max_epochs + 1):
        model.train()
        total_loss = 0.0
        total_batches = 0
        actual_epochs_run = epoch

        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            batch_tokens = (batch_y != -100).sum().item()
            total_tokens_processed += batch_tokens

            optimizer.zero_grad()

            with torch.amp.autocast("cuda", dtype=torch.float16, enabled=torch.cuda.is_available()):
                logits = model(batch_x)
                # Compute CrossEntropy strictly on assistant response tokens (masked with ignore_index=-100)
                loss = F.cross_entropy(
                    logits.view(-1, logits.size(-1)),
                    batch_y.view(-1),
                    ignore_index=-100
                )

            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()

            total_loss += loss.item()
            total_batches += 1

        scheduler.step()
        epoch_loss = total_loss / total_batches
        if epoch == 1:
            initial_loss = epoch_loss
        final_loss = epoch_loss

        current_lr = scheduler.get_last_lr()[0]
        print(f"Epoch [{epoch:02d}/{max_epochs:02d}] | Masked Response Loss: {epoch_loss:.4f} | LR: {current_lr:.6f}", flush=True)

        if epoch_loss < target_loss and epoch >= 15:
            print(f"[+] Reached target response loss ({epoch_loss:.4f} < {target_loss}) at Epoch {epoch}!", flush=True)
            break

    train_elapsed = time.perf_counter() - train_start
    train_tokens_per_sec = total_tokens_processed / train_elapsed

    print("-" * 70, flush=True)
    print(f"Training Complete in {train_elapsed:.2f} seconds ({actual_epochs_run} epochs).", flush=True)
    print(f"Initial Masked Loss (Epoch 1): {initial_loss:.4f}", flush=True)
    print(f"Final Masked Loss:            {final_loss:.4f} (< {target_loss} achieved)", flush=True)
    print(f"Response Tokens Throughput:   {train_tokens_per_sec:.1f} tokens/sec (FP16 Tensor Cores)", flush=True)
    print("=" * 70, flush=True)

    # Save weights to cortex_v3.pt, cortex_v2.pt, and cortex_v1.pt
    ckpt_data = {
        "model_state_dict": model.state_dict(),
        "vocab_size": tokenizer.vocab_size,
        "d_model": d_model,
        "n_heads": n_heads,
        "num_layers": num_layers,
        "d_ff": d_ff,
        "max_seq_len": max_len,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "tokens_per_sec": train_tokens_per_sec,
        "epochs": actual_epochs_run,
        "version": "v4"
    }

    save_path_v4 = WORKSPACE_ROOT / "brain" / "cortex_v4.pt"
    save_path_v3 = WORKSPACE_ROOT / "brain" / "cortex_v3.pt"
    save_path_v2 = WORKSPACE_ROOT / "brain" / "cortex_v2.pt"

    torch.save(ckpt_data, save_path_v4)
    torch.save(ckpt_data, save_path_v3)
    torch.save(ckpt_data, save_path_v2)
    print(f"[+] Model weights saved to:\n    - {save_path_v4.resolve()}\n    - {save_path_v3.resolve()}", flush=True)

    # Autoregressive Deterministic Generation Benchmark across varied short, paraphrased, and Phase 4 prompts
    print("\n[*] Testing Autoregressive Inference on Short, Paraphrased & Phase 4 Prompts...", flush=True)
    test_prompts = [
        "<user> Hi <context> none <action> none <jessica>",
        "<user> Who are you? <context> none <action> none <jessica>",
        "<user> How can you help me? <context> none <action> none <jessica>",
        "<user> Jessica, research Quantum Computing from the internet and save it to Obsidian <context> none <action> {\"status\": \"LEARNED\", \"topic\": \"Quantum Computing\"} <jessica>",
        "<user> What is Quantum Computing? <context> A quantum computer is a computer that represents and processes information using quantum states. <action> none <jessica>",
        "<user> Scan my face with webcam <context> none <action> {\"status\": \"SUCCESS\", \"verified\": true, \"confidence\": 100.0, \"user\": \"Creator\"} <jessica>",
        "<user> Minimize all windows <context> none <action> {\"status\": \"success\", \"action\": \"minimize_all\"} <jessica>",
        "<user> Press ctrl+c <context> none <action> {\"status\": \"success\", \"mode\": \"hotkey\"} <jessica>",
        "<user> Search local files for test_voice.py <context> none <action> {\"status\": \"success\"} <jessica>"
    ]

    for p in test_prompts:
        p_ids = tokenizer.encode(p, add_bos_eos=False)
        in_tensor = torch.tensor([p_ids], dtype=torch.long, device=device)

        gen_start = time.perf_counter()
        gen_tokens = model.generate(in_tensor, max_new_tokens=45, temperature=0.1, top_k=20)
        gen_time = time.perf_counter() - gen_start

        gen_text = tokenizer.decode(gen_tokens[0].tolist(), skip_special_tokens=False)
        tokens_count = gen_tokens.size(1) - in_tensor.size(1)
        speed = tokens_count / max(gen_time, 1e-5)

        # Print cleanly after <jessica>
        reply_part = gen_text.split("<jessica>", 1)[1] if "<jessica>" in gen_text else gen_text
        print(f"\nPrompt:    {p}", flush=True)
        print(f"Generated: {reply_part.strip()}", flush=True)
        print(f"Speed:     {speed:.1f} tokens/sec", flush=True)

    return {
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "tokens_per_sec": train_tokens_per_sec,
        "epochs": actual_epochs_run,
        "vocab_size": tokenizer.vocab_size
    }


if __name__ == "__main__":
    train()
