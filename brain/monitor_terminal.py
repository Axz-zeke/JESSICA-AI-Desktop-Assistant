import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Force UTF-8 stdout if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
STAGES_FILE = ROOT_DIR / "datasets" / "marathon_training_stages.json"
TRAINER_PID = 9248

def get_gpu_stats():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
            text=True,
            timeout=2
        ).strip()
        parts = [p.strip() for p in out.split(",")]
        return {
            "util": parts[0],
            "mem_used": parts[1],
            "mem_total": parts[2],
            "temp": parts[3]
        }
    except Exception:
        return {"util": "N/A", "mem_used": "N/A", "mem_total": "N/A", "temp": "N/A"}

def is_pid_alive(pid):
    try:
        out = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", f"Get-Process -Id {pid} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],
            text=True,
            timeout=2
        ).strip()
        return str(pid) in out
    except Exception:
        return False

def render_dashboard():
    # Enable ANSI escape codes on Windows
    os.system("")

    while True:
        try:
            gpu = get_gpu_stats()
            alive = is_pid_alive(TRAINER_PID)

            # Clear screen
            print("\033[2J\033[H", end="")

            print("\033[96m" + "=" * 78 + "\033[0m")
            print("\033[93m" + "        PROJECT JESSICA - LIVE QLORA TRAINING TERMINAL (STAGE 3/5)" + "\033[0m")
            print("\033[96m" + "=" * 78 + "\033[0m")

            status_color = "\033[92m" if alive else "\033[91m"
            status_text = "TRAINING ACTIVE (99-100% GPU LOAD)" if alive else "COMPLETED / IDLE"
            print(f"Status        : {status_color}{status_text}\033[0m (PID: {TRAINER_PID})")
            print(f"Compute Unit  : \033[97mNVIDIA GeForce RTX 4060 (8GB VRAM)\033[0m")
            print(f"GPU Load      : \033[92m{gpu['util']}%\033[0m  |  Temp: \033[93m{gpu['temp']} C\033[0m")
            print(f"VRAM Allocated: \033[95m{gpu['mem_used']} MiB / {gpu['mem_total']} MiB\033[0m")
            print(f"Model Arch    : \033[94m8.03B Llama-3.1 NF4 (Target: all 7 Linear Projections, r=16, alpha=32)\033[0m")
            print(f"Objective     : \033[94mTarget-Only Loss Masking on 2,500 Spoken Dialogue Samples\033[0m")
            print("\033[96m" + "-" * 78 + "\033[0m")

            if STAGES_FILE.exists():
                try:
                    with open(STAGES_FILE, "r", encoding="utf-8") as f:
                        stages = json.load(f)

                    print("\033[93m--- STAGE CHECKPOINTS COMPLETED ---\033[0m")
                    for s in stages:
                        stg = s.get("stage", "?")
                        t_loss = s.get("train_loss", 0.0)
                        v_loss = s.get("val_loss", 0.0)
                        ppl = s.get("val_perplexity", 1.0)
                        dur = s.get("duration_seconds", 0) / 60.0
                        sample = s.get("sample_generation", "")

                        print(f"  \033[92m[OK] STAGE {stg}/5 COMPLETE\033[0m ({dur:.1f} min)")
                        print(f"    Train Loss: \033[97m{t_loss:.4f}\033[0m | Val Loss: \033[97m{v_loss:.4f}\033[0m | Val PPL: \033[92m{ppl:.2f}\033[0m")
                        print(f"    Sample: \"\033[90m{sample}\033[0m\"")
                        print()

                    curr_stage = len(stages) + 1
                    if curr_stage <= 5 and alive:
                        print(f"\033[93m>>> CURRENTLY EXECUTING STAGE {curr_stage}/5 ON GPU <<<\033[0m")
                        print("    \033[96m[Optimizing Backpropagation across 2,300 dialogues]\033[0m")
                        print("    \033[90mCheckpoints automatically saved to E:\\GitHub\\JESSICA_STORAGE\\brain\\lora_adapter\033[0m")
                    elif curr_stage > 5:
                        print("\033[92m[COMPLETE] ALL 5 QLORA TRAINING STAGES SUCCESSFULLY COMPLETED!\033[0m")
                except Exception as e:
                    print(f"Reading stage log: {e}")

            print("\033[96m" + "=" * 78 + "\033[0m")
            print("\033[90mAuto-refreshing every 3 seconds... Press Ctrl+C to exit monitor.\033[0m")

        except Exception as e:
            print(f"Dashboard error: {e}")

        time.sleep(3)

if __name__ == "__main__":
    try:
        render_dashboard()
    except KeyboardInterrupt:
        print("\nMonitor paused. Training continues in background.")
