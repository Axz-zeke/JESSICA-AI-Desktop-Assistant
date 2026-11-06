"""
Jessica Brain - Deep Full-Linear QLoRA Training Marathon (8B Llama-3.1 NF4)
Target Modules: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
r=16, lora_alpha=32, lora_dropout=0.05
Features:
- 4-Bit NF4 Quantization with FP16 Compute & Double Quantization
- Strict Target-Only Loss Masking (labels=-100 on prompt tokens)
- Gradient Accumulation (steps=4) and Cosine Annealing Learning Rate
- Evaluates Validation Perplexity and Saves Checkpoint after EVERY single stage
"""

import os
import sys
import json
import time
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    get_cosine_schedule_with_warmup
)
from peft import (
    prepare_model_for_kbit_training,
    LoraConfig,
    get_peft_model,
    TaskType,
    PeftModel
)

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
STORAGE_MODELS = Path("E:/GitHub/JESSICA_STORAGE/models")
SOVEREIGN_V8_DIR = STORAGE_MODELS / "jessica_sovereign_v8"
BASE_MODEL_ID = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
LORA_ADAPTER_DIR = WORKSPACE_ROOT / "brain" / "lora_adapter"
CORPUS_FILE = WORKSPACE_ROOT / "datasets" / "marathon_spoken_corpus.jsonl"
STAGES_LOG_FILE = WORKSPACE_ROOT / "datasets" / "marathon_training_stages.json"

SYSTEM_PROMPT = """You are Jessica, a real, warm, witty, emotionally intelligent woman and OS companion sitting right here in the room with your creator on RTX 4060.
Speak in natural, casual human conversation as if speaking aloud to a close friend.
Always use natural contractions ("I'm", "don't", "you're", "let's", "that's", "we've", "it's").
Keep casual replies concise, punchy, and human (1 to 3 spoken sentences). Never ramble, lecture, or sound like a Wikipedia article.
NEVER output bullet points, numbered lists (1. 2. 3.), asterisks (*smiles*), emoticons, emojis, or markdown formatting in casual conversation.
NEVER say robotic corporate disclaimers like "As an AI", "As a digital entity", or "I possess advanced capabilities".
Always prefix your response with your emotional state: <emotion: warm>, <emotion: playful>, <emotion: curious>, <emotion: calm>, <emotion: serious>, or <emotion: excited>."""


class SpokenMarathonDataset(Dataset):
    def __init__(self, samples: List[Dict[str, Any]], tokenizer, max_len: int = 160):
        self.features = []
        pad_id = tokenizer.pad_token_id or tokenizer.eos_token_id

        for s in samples:
            u = s["user"].strip()
            emo = s.get("emotion", "warm").strip()
            r = s["reply"].strip()

            prompt_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": u}
            ]
            prompt_text = tokenizer.apply_chat_template(prompt_messages, tokenize=False, add_generation_prompt=True)
            prompt_ids = tokenizer.encode(prompt_text, add_special_tokens=False)

            full_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": u},
                {"role": "assistant", "content": f"<emotion: {emo}> {r}"}
            ]
            full_text = tokenizer.apply_chat_template(full_messages, tokenize=False)
            full_ids = tokenizer.encode(full_text, add_special_tokens=False)

            if len(full_ids) > max_len:
                full_ids = full_ids[:max_len]

            # Construct input_ids and target-only masked labels
            input_ids = torch.tensor(full_ids, dtype=torch.long)
            labels = input_ids.clone()

            # Mask out the prompt tokens with -100 so loss is computed ONLY on Jessica's spoken reply
            prompt_len = min(len(prompt_ids), len(full_ids) - 1)
            labels[:prompt_len] = -100

            self.features.append({"input_ids": input_ids, "labels": labels})

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx]


def collate_masked(batch, pad_id: int):
    max_len = max(len(item["input_ids"]) for item in batch)
    padded_inputs = []
    padded_labels = []

    for item in batch:
        inp = item["input_ids"]
        lbl = item["labels"]
        pad_size = max_len - len(inp)

        if pad_size > 0:
            p_inp = torch.cat([inp, torch.full((pad_size,), pad_id, dtype=torch.long)])
            p_lbl = torch.cat([lbl, torch.full((pad_size,), -100, dtype=torch.long)])
        else:
            p_inp = inp
            p_lbl = lbl

        padded_inputs.append(p_inp)
        padded_labels.append(p_lbl)

    return {
        "input_ids": torch.stack(padded_inputs),
        "labels": torch.stack(padded_labels),
        "attention_mask": (torch.stack(padded_inputs) != pad_id).long()
    }


def run_marathon_training(total_stages: int = 5):
    print("=" * 75)
    print("JESSICA WAVE 3: DEEP FULL-LINEAR QLoRA TRAINING MARATHON (8B NF4)")
    print("=" * 75)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"[*] Compute Target: {device} ({torch.cuda.get_device_name(0)})")

    # 1. Load Tokenizer
    tok_source = str(SOVEREIGN_V8_DIR) if (SOVEREIGN_V8_DIR / "tokenizer_config.json").exists() else BASE_MODEL_ID
    tokenizer = AutoTokenizer.from_pretrained(tok_source, cache_dir=str(STORAGE_MODELS))
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # 2. Load 4-Bit NF4 Base Model
    print(f"[*] Loading 4-Bit NF4 Base Model ({BASE_MODEL_ID})...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        quantization_config=bnb_config,
        device_map=device,
        cache_dir=str(STORAGE_MODELS)
    )

    base_model = prepare_model_for_kbit_training(base_model)

    # 3. Configure Full-Linear QLoRA Adapter (r=16, alpha=32, target all 7 linear layers)
    print("[*] Upgrading QLoRA to Full-Linear Projections (r=16, alpha=32)...")
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )

    model = get_peft_model(base_model, lora_config)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[+] Trainable LoRA Parameters: {trainable_params:,} / {total_params:,} ({trainable_params/total_params*100:.3f}%)")

    # 4. Load Corpus and Create Train/Val Splits
    print(f"[*] Loading marathon spoken corpus from {CORPUS_FILE}...")
    all_samples = []
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_samples.append(json.loads(line))

    # Split: 2,300 train, 200 validation
    val_samples = all_samples[:200]
    train_samples = all_samples[200:]

    train_dataset = SpokenMarathonDataset(train_samples, tokenizer, max_len=160)
    val_dataset = SpokenMarathonDataset(val_samples, tokenizer, max_len=160)

    train_loader = DataLoader(
        train_dataset,
        batch_size=2,
        shuffle=True,
        collate_fn=lambda b: collate_masked(b, pad_id=tokenizer.pad_token_id)
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=2,
        shuffle=False,
        collate_fn=lambda b: collate_masked(b, pad_id=tokenizer.pad_token_id)
    )

    # 5. Optimizer & Cosine Scheduler
    accumulation_steps = 4
    total_train_steps = (len(train_loader) // accumulation_steps) * total_stages
    optimizer = torch.optim.AdamW(model.parameters(), lr=1.8e-4, weight_decay=0.01)
    scheduler = get_cosine_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_train_steps * 0.05),
        num_training_steps=total_train_steps
    )

    stage_records = []
    print(f"\n[*] Starting {total_stages}-Stage QLoRA Training Marathon on RTX 4060...")
    print(f"[*] Total Steps: {total_train_steps} (Gradient Accumulation = {accumulation_steps}, Batch Size = 2)")

    overall_start = time.perf_counter()

    for stage in range(1, total_stages + 1):
        stage_start = time.perf_counter()
        model.train()
        train_loss = 0.0
        optimizer.zero_grad()
        step_count = 0

        for idx, batch in enumerate(train_loader):
            input_ids = batch["input_ids"].to(device)
            labels = batch["labels"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            with torch.amp.autocast("cuda", dtype=torch.float16):
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss / accumulation_steps

            loss.backward()
            train_loss += loss.item() * accumulation_steps

            if (idx + 1) % accumulation_steps == 0 or (idx + 1) == len(train_loader):
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                step_count += 1

        avg_train_loss = round(train_loss / max(len(train_loader), 1), 4)

        # Validation Pass
        model.eval()
        val_loss = 0.0
        val_batches = 0
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                labels = batch["labels"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                with torch.amp.autocast("cuda", dtype=torch.float16):
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += outputs.loss.item()
                val_batches += 1

        avg_val_loss = round(val_loss / max(val_batches, 1), 4)
        val_ppl = round(math.exp(min(avg_val_loss, 20.0)), 2)
        stage_duration = round(time.perf_counter() - stage_start, 2)

        # Save Checkpoint after EVERY single stage for safety & persistence!
        LORA_ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(str(LORA_ADAPTER_DIR))
        tokenizer.save_pretrained(str(LORA_ADAPTER_DIR))

        # Test Generation Sample
        test_prompt_text = tokenizer.apply_chat_template([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Explain BGP routing like we're chatting over coffee."}
        ], tokenize=False, add_generation_prompt=True)
        test_inputs = tokenizer(test_prompt_text, return_tensors="pt").to(device)

        with torch.no_grad():
            gen_out = model.generate(
                **test_inputs,
                max_new_tokens=45,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        new_tokens = gen_out[0][test_inputs["input_ids"].shape[1]:]
        sample_gen = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        stage_data = {
            "stage": stage,
            "train_loss": avg_train_loss,
            "val_loss": avg_val_loss,
            "val_perplexity": val_ppl,
            "duration_seconds": stage_duration,
            "sample_generation": sample_gen,
            "checkpoint_saved": str(LORA_ADAPTER_DIR)
        }
        stage_records.append(stage_data)

        # Persist stage metrics to disk immediately
        with open(STAGES_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(stage_records, f, indent=2)

        print(f"\n[+] STAGE {stage}/{total_stages} COMPLETE in {stage_duration}s")
        print(f"    Train Loss: {avg_train_loss} | Val Loss: {avg_val_loss} | Val PPL: {val_ppl}")
        print(f"    Sample Output: \"{sample_gen}\"")
        print(f"    Checkpoint Saved -> {LORA_ADAPTER_DIR}")

    total_duration = round(time.perf_counter() - overall_start, 2)
    print(f"\n[+] ALL {total_stages} STAGES COMPLETED in {total_duration}s!")
    print(f"[+] Final Stage Val Loss: {stage_records[-1]['val_loss']} | PPL: {stage_records[-1]['val_perplexity']}")

    return stage_records


if __name__ == "__main__":
    records = run_marathon_training(total_stages=5)

