"""
Jessica Brain - Neural Router Training Script
Trains Jessica's custom Transformer router on the RTX 4060 for 20 epochs.
Saves model weights to brain/router_v1.pt and vocabulary to brain/tokenizer_vocab.json.
"""

import json
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path

import sys
from pathlib import Path

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.tokenizer import JessicaTokenizer
from brain.router_net import JessicaRouterNet, INTENT_TO_ID, INTENT_CLASSES


def train():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[*] Training Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    dataset_path = Path("datasets/router_train.jsonl")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    # Load dataset
    samples = []
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                samples.append(json.loads(line))

    print(f"[*] Loaded {len(samples)} training samples.")

    # Build tokenizer vocabulary
    corpus = [s["command"] for s in samples]
    tokenizer = JessicaTokenizer()
    tokenizer.build_vocab(corpus, min_freq=1, max_vocab_size=2048)
    tokenizer.save("brain/tokenizer_vocab.json")
    print(f"[*] Vocabulary built and saved. Vocab size: {tokenizer.vocab_size}")

    # Prepare tensors
    max_len = 48
    input_ids = [tokenizer.encode(s["command"], max_len=max_len) for s in samples]
    target_ids = [INTENT_TO_ID[s["intent"]] for s in samples]

    x_tensor = torch.tensor(input_ids, dtype=torch.long)
    y_tensor = torch.tensor(target_ids, dtype=torch.long)

    dataset = TensorDataset(x_tensor, y_tensor)
    batch_size = 16
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    model = JessicaRouterNet(
        vocab_size=tokenizer.vocab_size,
        d_model=128,
        n_heads=4,
        num_layers=3,
        d_ff=256,
        num_classes=len(INTENT_CLASSES),
        max_seq_len=max_len,
        dropout=0.1
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20, eta_min=1e-5)

    epochs = 20
    print("\n" + "=" * 65)
    print("           TRAINING JESSICA INTENT ROUTER v0.2")
    print("=" * 65)

    initial_loss = None
    final_loss = None

    start_time = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_x, batch_y in dataloader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(logits, dim=-1)
            correct += (preds == batch_y).sum().item()
            total += batch_x.size(0)

        scheduler.step()
        epoch_loss = total_loss / total
        epoch_acc = (correct / total) * 100.0

        if epoch == 1:
            initial_loss = epoch_loss
        if epoch == epochs:
            final_loss = epoch_loss

        print(f"Epoch [{epoch:02d}/{epochs:02d}] | Loss: {epoch_loss:.4f} | Accuracy: {epoch_acc:6.2f}% | LR: {scheduler.get_last_lr()[0]:.6f}")

    total_training_time = time.perf_counter() - start_time
    print("-" * 65)
    print(f"Training Complete in {total_training_time:.2f} seconds.")
    print(f"Initial Loss (Epoch 1):  {initial_loss:.4f}")
    print(f"Final Loss (Epoch {epochs}):   {final_loss:.4f}")
    print("=" * 65)

    # Save weights to router_v4.pt, router_v3.pt, router_v2.pt and router_v1.pt
    save_path_v4 = WORKSPACE_ROOT / "brain" / "router_v4.pt"
    save_path_v3 = WORKSPACE_ROOT / "brain" / "router_v3.pt"
    save_path_v2 = WORKSPACE_ROOT / "brain" / "router_v2.pt"
    save_path_v1 = WORKSPACE_ROOT / "brain" / "router_v1.pt"
    checkpoint_data = {
        "model_state_dict": model.state_dict(),
        "vocab_size": tokenizer.vocab_size,
        "max_seq_len": max_len,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "classes": INTENT_CLASSES
    }
    torch.save(checkpoint_data, save_path_v4)
    torch.save(checkpoint_data, save_path_v3)
    torch.save(checkpoint_data, save_path_v2)
    torch.save(checkpoint_data, save_path_v1)
    print(f"[+] Model weights saved to: {save_path_v4.resolve()}, {save_path_v3.resolve()} and {save_path_v2.resolve()}")


if __name__ == "__main__":
    train()
