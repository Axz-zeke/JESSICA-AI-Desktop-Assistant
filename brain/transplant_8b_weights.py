"""
Jessica Brain - 8-Billion Parameter Llama-3.1 NF4 Tensor Transplant
Downloads and transplants unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit into E:\\GitHub\\JESSICA_STORAGE\\models\\jessica_sovereign_v8
Purges all legacy Qwen files from disk.
"""

import os
import sys
import shutil
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
STORAGE_MODELS = Path("E:/GitHub/JESSICA_STORAGE/models")
TARGET_DIR = STORAGE_MODELS / "jessica_sovereign_v8"
PRIMARY_MODEL_ID = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
FALLBACK_MODEL_ID = "unsloth/Llama-3.2-3B-Instruct"

def purge_qwen_files():
    print("[*] PURGING all legacy Qwen files from disk...")
    deleted_count = 0
    for item in STORAGE_MODELS.glob("*Qwen*"):
        try:
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
                print(f"[-] Deleted directory: {item}")
                deleted_count += 1
            elif item.is_file():
                item.unlink(missing_ok=True)
                print(f"[-] Deleted file: {item}")
                deleted_count += 1
        except Exception as e:
            print(f"[!] Warning deleting {item}: {e}")
    print(f"[+] Qwen purge complete. {deleted_count} items purged.")

def transplant():
    print("=" * 70)
    print("JESSICA 8-BILLION PARAMETER LLAMA-3.1 NF4 TENSOR TRANSPLANT")
    print("=" * 70)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    model_to_use = PRIMARY_MODEL_ID
    print(f"[*] Attempting to download and load {model_to_use} on cuda:0...")

    try:
        t0 = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(model_to_use, cache_dir=str(STORAGE_MODELS))
        model = AutoModelForCausalLM.from_pretrained(
            model_to_use,
            quantization_config=bnb_config,
            device_map="cuda:0",
            cache_dir=str(STORAGE_MODELS)
        )
        load_dur = round(time.perf_counter() - t0, 2)
        print(f"[+] Primary model {model_to_use} loaded successfully in {load_dur}s!")
    except Exception as e:
        print(f"[!] Failed loading primary 8B model: {e}")
        print(f"[*] Falling back to {FALLBACK_MODEL_ID}...")
        model_to_use = FALLBACK_MODEL_ID
        t0 = time.perf_counter()
        tokenizer = AutoTokenizer.from_pretrained(model_to_use, cache_dir=str(STORAGE_MODELS))
        model = AutoModelForCausalLM.from_pretrained(
            model_to_use,
            device_map="cuda:0",
            dtype=torch.float16,
            cache_dir=str(STORAGE_MODELS)
        )
        load_dur = round(time.perf_counter() - t0, 2)
        print(f"[+] Fallback model {model_to_use} loaded in {load_dur}s!")

    # Calculate parameter count and VRAM allocation
    total_params = sum(p.numel() for p in model.parameters())
    vram_alloc_mb = round(torch.cuda.memory_allocated() / (1024**2), 1)

    print(f"[+] Total Parameters: {total_params:,} ({total_params/1e9:.2f}B)")
    print(f"[+] VRAM Allocated on RTX 4060: {vram_alloc_mb} MiB")

    # Save tokenizer to TARGET_DIR
    print(f"[*] Saving sovereign tokenizer & configs to {TARGET_DIR}...")
    tokenizer.save_pretrained(str(TARGET_DIR))

    # Save metadata info
    meta_info = {
        "model_id": model_to_use,
        "transplant_timestamp": time.time(),
        "total_parameters": total_params,
        "vram_allocated_mb": vram_alloc_mb,
        "quantization": "NF4 4-bit" if "4bit" in model_to_use else "FP16",
        "device": "cuda:0"
    }
    with open(TARGET_DIR / "jessica_sovereign_meta.json", "w") as f:
        import json
        json.dump(meta_info, f, indent=2)

    # Purge Qwen models
    purge_qwen_files()

    # Quick test inference
    print("\n[*] Running test inference on cuda:0...")
    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are Jessica, a warm, witty, 100% local AI partner on RTX 4060.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nHey Jessica, how's it going?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")

    t_gen = time.perf_counter()
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=40,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    gen_time = time.perf_counter() - t_gen
    new_tokens = out[0][inputs["input_ids"].shape[1]:]
    resp_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    print(f"[+] Test Generation: \"{resp_text}\"")
    print(f"[+] Generation Speed: {len(new_tokens) / max(gen_time, 1e-4):.1f} tok/s")
    print("\n[+] TRANSPLANT OPERATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    transplant()

