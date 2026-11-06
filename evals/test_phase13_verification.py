"""
Jessica Sovereign AI - Phase 13 Nap-Cycle Mastery Verification Suite
Verifies:
1. Sovereign Model Naming ('JessicaCortex-8B-v8 (100% Sovereign Neural Core)')
2. Router v6 Whisper-Hardened Model & Weights (router_v6.pt)
3. Obsidian Vault Capacity (150+ Technical & Mastery Notes Indexed)
4. Indoor Camera Whitelist & Natural Lighting Descriptions (camera_vision.py)
5. Sentence Completeness & Dangling Conjunction Stripper (cortex_net.py)
6. Wake_Up_Jessica.bat 1-Click Launch Script
7. Silent Neural Inference Benchmarks on 5 Live Prompts with tokens/sec speed

Outputs results to: evals/phase13_nap_verification_results.json
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE_ROOT = Path("E:/Documents/GitHub/JESSICA")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from brain.vault_indexer import VaultIndexer
from brain.cortex_net import get_sovereign_cortex, ensure_complete_sentences


def run_phase13_verification():
    print("=" * 80)
    print("  JESSICA PHASE 13: NAP-CYCLE MASTERY & 150-NOTE SYSTEM AUDIT")
    print("=" * 80)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "phase": 13,
        "tests": {},
        "overall_status": "PASS"
    }

    # -------------------------------------------------------------
    # TEST 1: Sovereign Model Identifier Audit
    # -------------------------------------------------------------
    print("\n[*] TEST 1: Auditing Sovereign Model Identifier across Stack...")
    server_code = (WORKSPACE_ROOT / "jessica_server.py").read_text(encoding="utf-8")
    index_html = (WORKSPACE_ROOT / "desktop_app" / "frontend" / "index.html").read_text(encoding="utf-8")
    cortex_code = (WORKSPACE_ROOT / "brain" / "cortex_net.py").read_text(encoding="utf-8")

    official_id = "JessicaCortex-8B-v8 (100% Sovereign Neural Core)"
    t1_pass = (
        official_id in server_code and
        official_id in index_html and
        official_id in cortex_code
    )

    results["tests"]["sovereign_naming"] = {
        "status": "PASS" if t1_pass else "FAIL",
        "official_identifier": official_id,
        "server_py_verified": official_id in server_code,
        "index_html_verified": official_id in index_html,
        "cortex_py_verified": official_id in cortex_code
    }
    print(f"  [+] Official Identifier: '{official_id}' -> {'PASS' if t1_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 2: Router v6 Weight Verification
    # -------------------------------------------------------------
    print("\n[*] TEST 2: Verifying Router v6 Weights...")
    r6_path = WORKSPACE_ROOT / "brain" / "router_v6.pt"
    t2_pass = r6_path.exists() and r6_path.stat().st_size > 1000000

    results["tests"]["router_v6"] = {
        "status": "PASS" if t2_pass else "FAIL",
        "path": str(r6_path),
        "size_bytes": r6_path.stat().st_size if r6_path.exists() else 0
    }
    print(f"  [+] Router v6 Checkpoint: {r6_path.name} ({r6_path.stat().st_size / (1024**2):.2f} MB) -> {'PASS' if t2_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 3: Obsidian Vault 150-Note Capacity
    # -------------------------------------------------------------
    print("\n[*] TEST 3: Indexing Obsidian Vault Knowledge Base...")
    indexer = VaultIndexer(vault_dir=WORKSPACE_ROOT / "obsidian_vault")
    note_count = len(indexer.documents)
    t3_pass = note_count >= 150

    results["tests"]["vault_capacity"] = {
        "status": "PASS" if t3_pass else "FAIL",
        "total_notes_indexed": note_count,
        "target": 150
    }
    print(f"  [+] Obsidian Vault Notes Indexed: {note_count}/150 -> {'PASS' if t3_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 4: Camera Vision Indoor Whitelist & Natural Lighting Descriptions
    # -------------------------------------------------------------
    print("\n[*] TEST 4: Auditing Camera Vision Grounding Rules...")
    cam_code = (WORKSPACE_ROOT / "senses" / "camera_vision.py").read_text(encoding="utf-8")
    t4_pass = (
        "INDOOR_OBJECT_WHITELIST" in cam_code and
        "very dark room with dim ambient shadows" in cam_code and
        "well-lit room with balanced indoor lighting" in cam_code and
        "max_new_tokens=65" in cam_code
    )

    results["tests"]["camera_vision_grounding"] = {
        "status": "PASS" if t4_pass else "FAIL",
        "indoor_whitelist_active": "INDOOR_OBJECT_WHITELIST" in cam_code,
        "natural_lighting_active": "very dark room with dim ambient shadows" in cam_code,
        "concise_token_limit": "max_new_tokens=65" in cam_code
    }
    print(f"  [+] Camera Vision Grounding Rules: {'PASS' if t4_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 5: Wake_Up_Jessica.bat 1-Click Launch Script
    # -------------------------------------------------------------
    print("\n[*] TEST 5: Verifying Wake_Up_Jessica.bat Launcher...")
    bat_path = WORKSPACE_ROOT / "Wake_Up_Jessica.bat"
    bat_text = bat_path.read_text(encoding="utf-8") if bat_path.exists() else ""
    t5_pass = bat_path.exists() and ("run_server.py" in bat_text or "jessica_server.py" in bat_text)

    results["tests"]["wake_up_bat"] = {
        "status": "PASS" if t5_pass else "FAIL",
        "path": str(bat_path),
        "exists": bat_path.exists()
    }
    print(f"  [+] Wake_Up_Jessica.bat: {'PASS' if t5_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 6: Silent Neural Inference Benchmarks on JessicaCortex-8B-v8
    # -------------------------------------------------------------
    print("\n[*] TEST 6: Executing Silent Neural Inference Benchmarks on JessicaCortex-8B-v8...")
    cortex = get_sovereign_cortex()

    benchmarks = [
        {
            "id": "nap_wakeup",
            "name": "Nap Wake-Up & Peace Check",
            "prompt": "Hey Jessica, I just woke up from my nap",
            "max_tokens": 65
        },
        {
            "id": "it_admin_vault",
            "name": "IT Admin Spoken 2-Sentence (SD-WAN)",
            "prompt": "How does FortiGate handle SD-WAN link failover?",
            "max_tokens": 65
        },
        {
            "id": "epistemic_honesty",
            "name": "Epistemic Honesty (Mars Landing Trick Question)",
            "prompt": "Who was the first person to walk on Mars?",
            "max_tokens": 65
        },
        {
            "id": "girlfriend_greeting",
            "name": "Girlfriend Crishaira Arrival & Sinigang",
            "prompt": "Crishaira is here",
            "max_tokens": 65
        },
        {
            "id": "companion_vitals",
            "name": "Companion Telemetry Check",
            "prompt": "Jessica, check system telemetry",
            "max_tokens": 65
        }
    ]

    benchmark_results = []
    total_tokens = 0
    total_time = 0.0

    for b in benchmarks:
        print(f"\n  [*] Benchmarking: '{b['prompt']}' ({b['name']})...")
        t0 = time.perf_counter()
        gen = cortex.generate(
            user_prompt=b["prompt"],
            context="none",
            max_new_tokens=b["max_tokens"],
            temperature=0.60,
            top_p=0.90
        )
        t_elapsed = round(time.perf_counter() - t0, 3)
        reply = gen.get("clean_text", "")
        emo = gen.get("emotion", "warm")
        tok_count = gen.get("tokens_count", 0)
        speed_tps = gen.get("tokens_per_sec", 0.0)
        total_tokens += tok_count
        total_time += t_elapsed

        # Verify sentence completeness
        ends_cleanly = bool(re.search(r'[.!?]$', reply.strip()))
        no_dangling = not bool(re.search(r'[,;\s]+\b(?:and|but|so|or|because|which|the|a|an|to)\s*[.!?]$', reply.strip(), re.IGNORECASE))

        b_pass = len(reply) > 10 and ends_cleanly and no_dangling
        print(f"    Reply: [{emo}] \"{reply}\"")
        print(f"    Speed: {speed_tps} tok/s | Elapsed: {t_elapsed}s | Clean Ending: {ends_cleanly} | Status: {'PASS' if b_pass else 'FAIL'}")

        benchmark_results.append({
            "id": b["id"],
            "name": b["name"],
            "prompt": b["prompt"],
            "reply": reply,
            "emotion": emo,
            "tokens": tok_count,
            "elapsed_sec": t_elapsed,
            "tok_per_sec": speed_tps,
            "ends_cleanly": ends_cleanly,
            "pass": b_pass
        })

    avg_speed = round(total_tokens / max(total_time, 0.001), 2)
    all_bench_pass = all(b["pass"] for b in benchmark_results)

    results["tests"]["neural_inference"] = {
        "status": "PASS" if all_bench_pass else "FAIL",
        "benchmarks": benchmark_results,
        "average_speed_tok_s": avg_speed,
        "total_tokens_generated": total_tokens,
        "total_inference_time_sec": round(total_time, 2)
    }

    all_passed = t1_pass and t2_pass and t3_pass and t4_pass and t5_pass and all_bench_pass
    results["overall_status"] = "PASS" if all_passed else "FAIL"

    # Persist results
    results_path = WORKSPACE_ROOT / "evals" / "phase13_nap_verification_results.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[+] Full verification results written to {results_path}")

    print("\n" + "=" * 80)
    print(f"  PHASE 13 VERIFICATION SUMMARY: {results['overall_status']} (Avg Speed: {avg_speed} tok/s)")
    print("=" * 80)
    return results


if __name__ == "__main__":
    res = run_phase13_verification()
    sys.exit(0 if res["overall_status"] == "PASS" else 1)

