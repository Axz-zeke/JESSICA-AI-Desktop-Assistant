"""
Jessica Brain - Custom PyTorch LoRA / QLoRA Self-Trainer (8B Llama-3.1 NF4)
Fine-tunes a PEFT LoRA adapter (r=8, lora_alpha=16) on the 8B Cortex
using natural spoken emotional dialogue corpus + Obsidian Vault notes on RTX 4060 GPU.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from peft import LoraConfig, get_peft_model, TaskType, PeftModel, prepare_model_for_kbit_training

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.working_memory import WORKING_MEMORY
from brain.cortex_net import get_sovereign_cortex

LORA_ADAPTER_DIR = WORKSPACE_ROOT / "brain" / "lora_adapter"
SPOKEN_DATASET_FILE = WORKSPACE_ROOT / "datasets" / "natural_spoken_dialogues.jsonl"


class SpokenDialogueDataset(Dataset):
    def __init__(self, samples: List[str], tokenizer, max_len: int = 192):
        self.inputs = []
        for s in samples:
            tokens = tokenizer.encode(s, max_length=max_len, truncation=True)
            self.inputs.append(torch.tensor(tokens, dtype=torch.long))

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return self.inputs[idx]


def collate_tokens(batch, pad_id: int):
    max_len = max(len(t) for t in batch)
    padded = []
    targets = []
    for t in batch:
        pad_size = max_len - len(t)
        if pad_size > 0:
            padded_t = torch.cat([t, torch.full((pad_size,), pad_id, dtype=torch.long)])
            target_t = torch.cat([t, torch.full((pad_size,), -100, dtype=torch.long)])
        else:
            padded_t = t
            target_t = t.clone()
        padded.append(padded_t)
        targets.append(target_t)
    return torch.stack(padded), torch.stack(targets)


def extract_spoken_and_vault_corpus(tokenizer) -> List[str]:
    """
    Combines 100 natural spoken dialogues + Obsidian Vault notes into training sequences.
    """
    corpus = []
    sys_prompt = "You are Jessica, a real, warm, witty, emotionally intelligent woman and OS companion sitting right here in the room with your creator on RTX 4060. Speak naturally with contractions and zero textbook essays."

    # 1. Load 100 Natural Spoken Dialogues
    if SPOKEN_DATASET_FILE.exists():
        with open(SPOKEN_DATASET_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    messages = [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": item["user"]},
                        {"role": "assistant", "content": f"<emotion: {item.get('emotion', 'warm')}> {item['reply']}"}
                    ]
                    formatted = tokenizer.apply_chat_template(messages, tokenize=False)
                    corpus.append(formatted)

    # 2. Extract Obsidian Vault Knowledge
    vault_dir = WORKSPACE_ROOT / "obsidian_vault"
    if vault_dir.exists():
        for md_file in vault_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8").strip()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                paras = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 30]
                for p in paras[:3]:
                    messages = [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": f"Tell me about the knowledge in {md_file.stem}."},
                        {"role": "assistant", "content": f"<emotion: warm> Here's what we have stored on that: {p}"}
                    ]
                    formatted = tokenizer.apply_chat_template(messages, tokenize=False)
                    corpus.append(formatted)
            except Exception:
                pass

    # 3. Add conversation history from working memory
    history = WORKING_MEMORY.get_messages(max_turns=6)
    for i in range(0, len(history) - 1, 2):
        if history[i]["role"] == "user" and history[i+1]["role"] == "assistant":
            u = history[i]["content"]
            a = history[i+1]["content"]
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": u},
                {"role": "assistant", "content": a}
            ]
            formatted = tokenizer.apply_chat_template(messages, tokenize=False)
            corpus.append(formatted)

    return corpus


def evolve_brain(epochs: int = 1, lr: float = 2e-4) -> Dict[str, Any]:
    """
    Attaches LoRA adapter and fine-tunes on natural spoken dialogues + Obsidian notes.
    """
    cortex = get_sovereign_cortex()
    device = cortex.device
    tokenizer = cortex.tokenizer

    start_time = time.perf_counter()

    # 1. Attach or retrieve LoRA adapter
    if not isinstance(cortex.model, PeftModel):
        print("[*] Attaching trainable PyTorch QLoRA adapter (r=8, alpha=16) to 8B Cortex...")
        cortex.model = prepare_model_for_kbit_training(cortex.model)
        lora_config = LoraConfig(
            r=8,
            lora_alpha=16,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.CAUSAL_LM
        )
        cortex.model = get_peft_model(cortex.model, lora_config)
        cortex.active_lora = True

    cortex.model.train()

    # 2. Extract fine-tuning samples
    corpus = extract_spoken_and_vault_corpus(tokenizer)
    dataset = SpokenDialogueDataset(corpus, tokenizer, max_len=192)
    loader = DataLoader(
        dataset,
        batch_size=2,
        shuffle=True,
        collate_fn=lambda b: collate_tokens(b, pad_id=tokenizer.pad_token_id or tokenizer.eos_token_id)
    )

    optimizer = torch.optim.AdamW(cortex.model.parameters(), lr=lr, weight_decay=0.01)

    initial_loss = None
    final_loss = None
    total_steps = 0

    print(f"[*] Starting live GPU QLoRA spoken-acting evolution ({epochs} epoch(s), {len(dataset)} samples)...")
    for epoch in range(1, epochs + 1):
        epoch_loss = 0.0
        batches = 0
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)

            optimizer.zero_grad()
            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = cortex.model(input_ids=x, labels=y)
                loss = outputs.loss

            loss.backward()
            optimizer.step()

            b_loss = loss.item()
            epoch_loss += b_loss
            batches += 1
            total_steps += 1

            if initial_loss is None:
                initial_loss = round(b_loss, 4)

        final_loss = round(epoch_loss / max(batches, 1), 4)

    cortex.model.eval()
    duration = round(time.perf_counter() - start_time, 2)

    # Save adapter weights to disk
    LORA_ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
    cortex.model.save_pretrained(str(LORA_ADAPTER_DIR))

    trainable_params = sum(p.numel() for p in cortex.model.parameters() if p.requires_grad)

    print(f"[+] QLoRA spoken evolution complete in {duration}s! Loss: {initial_loss} -> {final_loss}. Saved to {LORA_ADAPTER_DIR}")

    return {
        "status": "EVOLVED",
        "epochs": epochs,
        "duration_seconds": duration,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "samples_trained": len(dataset),
        "steps_trained": total_steps,
        "trainable_lora_params": trainable_params,
        "architecture": "8.03B Foundation Model + Custom LoRA (r=8)"
    }


if __name__ == "__main__":
    res = evolve_brain(epochs=1)
    print("Evolution Result:", json.dumps(res, indent=2))
