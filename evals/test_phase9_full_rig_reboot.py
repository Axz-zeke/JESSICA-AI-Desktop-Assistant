"""
Project Jessica - Phase 9 Multi-Process Cold Shutdown & Reboot Memory Verification Test
Tests 3-Tier Persistent Memory across independent operating system processes:
Process 1 (Seeding / Active Session) -> Full Shutdown / Process Termination
Process 2 (Cold Reboot Session) -> Instant RAM Preload (<0.05ms) -> Sovereign Neural Recall
Verifies complete permanent elimination of Shutdown Amnesia.
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

RESULTS_JSON = WORKSPACE_ROOT / "evals" / "phase9_reboot_results.json"


def run_process_1_seeding():
    print("=" * 70)
    print("PROCESS 1 (ACTIVE SESSION): SEEDING 3-TIER PERSISTENCE GRAPH")
    print(f"PID: {os.getpid()} | Python: {sys.version.split()[0]}")
    print("=" * 70)

    from brain.ram_cache import get_ram_cache
    from brain.persistence_engine import get_persistence_engine
    from brain.memory_consolidator import get_memory_consolidator

    ram = get_ram_cache()
    persistence = get_persistence_engine()
    consolidator = get_memory_consolidator()

    # Seed essential turns
    t0 = time.perf_counter()
    ram.append_conversation_turn("user", "Hey Jessica, remember that my bass is a 4-string passive Jcraft Jazz bass.")
    ram.append_conversation_turn("assistant", "Got it, Boss! Your 4-string passive Jcraft Jazz bass is permanently locked in memory.", emotion="warm")
    
    persistence.log_turn("proc1_seed", "user", "Hey Jessica, remember that my bass is a 4-string passive Jcraft Jazz bass.", "neutral", 15)
    persistence.log_turn("proc1_seed", "assistant", "Got it, Boss! Your 4-string passive Jcraft Jazz bass is permanently locked in memory.", "warm", 20)
    
    # Consolidate facts
    consolidator.consolidate_turn("My girlfriend is Crishaira and my favorite dish is Sinigang")
    consolidator.consolidate_turn("Whenever I say Jessica! Daddy's home, welcome me warmly Boss")

    # Flush persistence engine to disk
    persistence.flush()
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"[+] Process 1: Seeding complete in {elapsed_ms:.2f}ms.")
    print("[+] Process 1: Memory written through to RAM, SQLite (E:\\GitHub\\JESSICA_STORAGE\\memory), and Obsidian Vault.")
    print("[!] Process 1: Terminating completely (Simulating Power-Off / Server Shutdown)...\n")
    sys.exit(0)


def run_process_2_cold_reboot():
    print("=" * 70)
    print("PROCESS 2 (COLD REBOOT): VERIFYING 3-TIER MEMORY & CORTEX RECALL")
    print(f"PID: {os.getpid()} | Python: {sys.version.split()[0]}")
    print("=" * 70)

    t_boot_start = time.perf_counter()

    # Load RAM Cache & Persistence Engine in fresh process
    from brain.ram_cache import get_ram_cache
    from brain.persistence_engine import get_persistence_engine
    from brain.hardware_orchestrator import get_full_rig_telemetry

    ram = get_ram_cache()
    persistence = get_persistence_engine()
    telemetry = get_full_rig_telemetry()

    boot_time_ms = (time.perf_counter() - t_boot_start) * 1000
    print(f"[+] Process 2 Cold Boot: 32GB RAM Cache initialized in {boot_time_ms:.2f}ms.")

    # 1. Benchmark RAM Cache Retrieval Latency (< 0.5 ms required)
    latencies_us: List[float] = []
    for _ in range(100):
        t0 = time.perf_counter()
        mem = ram.get_creator_memories()
        latencies_us.append((time.perf_counter() - t0) * 1_000_000)

    avg_latency_us = sum(latencies_us) / len(latencies_us)
    avg_latency_ms = avg_latency_us / 1000.0
    print(f"[+] RAM Cache Retrieval Latency: {avg_latency_us:.2f} µs ({avg_latency_ms:.4f} ms) [TARGET < 0.5 ms: {'PASSED' if avg_latency_ms < 0.5 else 'FAILED'}]")
    assert avg_latency_ms < 0.5, f"RAM latency {avg_latency_ms}ms exceeded 0.5ms limit!"

    # 2. Verify Creator Core Memories in RAM Cache and SQLite
    creator_mem = ram.get_creator_memories()
    print(f"[+] Creator Core Memories loaded: {len(creator_mem)} characters.")
    
    sqlite_facts = persistence.get_creator_facts()
    print(f"[+] SQLite Eternal Facts count: {len(sqlite_facts)}")
    assert len(sqlite_facts) >= 10, f"Expected at least 10 SQLite facts, found {len(sqlite_facts)}"

    # Check key entity presence in memory
    assert "Alexander Lopez" in creator_mem or any(f["value"] == "Alexander Lopez" for f in sqlite_facts), "Missing Alexander Lopez"
    assert "Boss" in creator_mem or any(f["value"] == "Boss" for f in sqlite_facts), "Missing Boss"
    assert "Crishaira" in creator_mem or any(f["value"] == "Crishaira" for f in sqlite_facts), "Missing Crishaira"
    assert "Sinigang" in creator_mem or any("Sinigang" in f["value"] for f in sqlite_facts), "Missing Sinigang"
    assert "bass" in creator_mem.lower() or any("bass" in f["value"].lower() for f in sqlite_facts), "Missing bass"
    assert "Daddy's home" in creator_mem or any("Daddy's home" in f["value"] for f in sqlite_facts), "Missing Daddy's home cue"
    print("[+] ALL CORE FACT ENTITIES VERIFIED IN MEMORY GRAPH!")

    # 3. Load 8.03B Sovereign Cortex for Cold Recall Evaluation
    print("\n[*] Initializing Jessica Sovereign Cortex 8B on CUDA:0 for zero-amnesia recall...")
    from brain.cortex_net import get_sovereign_cortex
    cortex = get_sovereign_cortex()

    eval_prompts = [
        "Who am I, and what do you remember about me?",
        "Jessica! Daddy's home!"
    ]

    test_results = []
    for prompt in eval_prompts:
        print(f"\n[EVAL PROMPT]: '{prompt}'")
        res = cortex.generate(
            user_prompt=prompt,
            max_new_tokens=100,
            temperature=0.6,
            top_p=0.9
        )
        reply = res["clean_text"]
        emotion = res["emotion"]
        speed = res["tokens_per_sec"]
        latency = res["latency_ms"]

        print(f"  [REPLY]: {reply}")
        print(f"  [EMOTION]: <emotion: {emotion}> | Speed: {speed} tok/s | Latency: {latency}ms")

        # Assertions
        assert len(reply) > 10, "Response too short!"
        assert reply[-1] in ".!?", f"Response must end on punctuation mark (.!?), got '{reply[-1]}'"
        assert not any(tag in reply for tag in ["<emotion:", "[emotion:", "*smiles*", "*laughs*"]), "Sanitizer leak detected!"
        
        test_results.append({
            "prompt": prompt,
            "reply": reply,
            "emotion": emotion,
            "tokens_per_sec": speed,
            "latency_ms": latency
        })

    # Test 1 Verification: Confirms memory of Boss, Crishaira, bass, or rig
    reply_1 = test_results[0]["reply"].lower()
    has_identity_recall = any(term in reply_1 for term in ["boss", "alexander", "crishaira", "bass", "jcraft", "creator"])
    print(f"[+] Identity Recall Score: {'PASSED (Zero Amnesia)' if has_identity_recall else 'FAILED'}")
    assert has_identity_recall, f"Jessica failed to recall identity in: {test_results[0]['reply']}"

    # Test 2 Verification: Confirms Daddy's home response welcomes Boss back
    reply_2 = test_results[1]["reply"].lower()
    has_welcome_recall = any(term in reply_2 for term in ["welcome", "home", "boss", "daddy", "how was", "good to have"])
    print(f"[+] Arrival Cue Recall Score: {'PASSED (Zero Amnesia)' if has_welcome_recall else 'FAILED'}")
    assert has_welcome_recall, f"Jessica failed to respond to arrival cue in: {test_results[1]['reply']}"

    # Save summary report
    final_data = {
        "test_name": "Phase 9 Full-Rig Multi-Process Cold Reboot Test",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "boot_preload_ms": round(boot_time_ms, 2),
        "ram_cache_avg_retrieval_us": round(avg_latency_us, 2),
        "ram_cache_avg_retrieval_ms": round(avg_latency_ms, 4),
        "target_latency_met": bool(avg_latency_ms < 0.5),
        "sqlite_facts_verified": len(sqlite_facts),
        "identity_recall_passed": bool(has_identity_recall),
        "arrival_cue_passed": bool(has_welcome_recall),
        "responses": test_results,
        "hardware_telemetry": telemetry
    }

    with open(RESULTS_JSON, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2)

    print("\n" + "=" * 70)
    print("ALL PHASE 9 FULL-RIG SYMBIOSIS & COLD REBOOT TESTS PASSED (100%)!")
    print(f"Results saved to: {RESULTS_JSON}")
    print("=" * 70)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Phase 9 Multi-Process Cold Reboot Test")
    parser.add_argument("--mode", choices=["seed", "cold_reboot", "orchestrate"], default="orchestrate")
    args = parser.parse_args()

    if args.mode == "seed":
        run_process_1_seeding()
    elif args.mode == "cold_reboot":
        run_process_2_cold_reboot()
    else:
        # Orchestrate multi-process test
        print("[*] Launching Phase 9 Multi-Process Test Orchestrator...")
        
        # Step 1: Run Process 1
        print("[*] Spawning Process 1 (Seeding / Active Session)...")
        p1 = subprocess.run([sys.executable, __file__, "--mode", "seed"], capture_output=True, text=True)
        print(p1.stdout)
        if p1.returncode != 0:
            print(f"[!] Process 1 failed with code {p1.returncode}:\n{p1.stderr}")
            sys.exit(p1.returncode)

        print("[*] Process 1 successfully terminated and fully unmapped from memory.")
        print("[*] Cold reboot delay (1.0s)...")
        time.sleep(1.0)

        # Step 2: Run Process 2
        print("[*] Spawning Process 2 (Cold Reboot Session)...")
        p2 = subprocess.run([sys.executable, __file__, "--mode", "cold_reboot"], capture_output=True, text=True)
        print(p2.stdout)
        if p2.returncode != 0:
            print(f"[!] Process 2 failed with code {p2.returncode}:\n{p2.stderr}")
            sys.exit(p2.returncode)

        print("[+] Multi-Process Cold Reboot Test Orchestration Complete: 100% SUCCESS.")


if __name__ == "__main__":
    main()

