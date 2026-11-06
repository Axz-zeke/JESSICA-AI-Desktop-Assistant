"""
Jessica Sovereign AI - Phase 11 Wake-Word Engine & Anti-Hallucination Verification Suite
Tests:
1. Sovereign Model Naming Audit ('JessicaCortex-8B-v8 (100% Sovereign Neural Core)')
2. Always-On Open-Mic Wake-Word Engine (Mode A, Mode B <100ms attention chime, echo suppression lock)
3. Obsidian Knowledge Vault Capacity (Target: >=85 notes, Current: 89 notes)
4. Epistemic Humility & TruthGuard Grounding Gates
5. Neural Inference Benchmarks (5 real-world queries on JessicaCortex-8B-v8 with tokens/sec speed)
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

from senses.wake_word_daemon import WAKE_DAEMON, WakeWordDaemon
from senses.voice_engine import VOICE_ENGINE
from brain.truth_guard import TRUTH_GUARD
from brain.vault_indexer import VaultIndexer
from brain.cortex_net import get_sovereign_cortex


def run_phase11_verification():
    print("=" * 80)
    print("  JESSICA PHASE 11: WAKE-WORD ENGINE & ANTI-HALLUCINATION AUDIT")
    print("=" * 80)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {},
        "overall_status": "PASS"
    }

    # -------------------------------------------------------------
    # TEST 1: Sovereign Naming Audit
    # -------------------------------------------------------------
    print("\n[*] TEST 1: Auditing Sovereign Model Identifier across Stack...")
    server_code = (WORKSPACE_ROOT / "jessica_server.py").read_text(encoding="utf-8")
    index_html = (WORKSPACE_ROOT / "desktop_app" / "frontend" / "index.html").read_text(encoding="utf-8")
    cortex_code = (WORKSPACE_ROOT / "brain" / "cortex_net.py").read_text(encoding="utf-8")

    official_id = "JessicaCortex-8B-v8 (100% Sovereign Neural Core)"
    test1_pass = (
        official_id in server_code and
        official_id in index_html and
        official_id in cortex_code
    )

    results["tests"]["sovereign_naming"] = {
        "status": "PASS" if test1_pass else "FAIL",
        "official_identifier": official_id,
        "server_py_verified": official_id in server_code,
        "index_html_verified": official_id in index_html,
        "cortex_py_verified": official_id in cortex_code
    }
    print(f"  [+] Official Identifier: '{official_id}'")
    print(f"  [+] Naming Verification: {'PASS' if test1_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 2: Wake-Word Engine Functionality
    # -------------------------------------------------------------
    print("\n[*] TEST 2: Testing Wake-Word Engine (Mode A, Mode B, Echo Lock)...")
    wake_daemon = WakeWordDaemon()

    # 2A: Mode A (One-breath command)
    mode_a_input = "Jessica check my system status"
    matched_a, phrase_a, clean_a = wake_daemon.match_wake_phrase(mode_a_input)
    mode_a = "MODE_A_COMMAND" if (matched_a and clean_a) else ("MODE_B_ATTENTION" if matched_a else None)
    mode_a_pass = (matched_a is True and clean_a == "check my system status" and mode_a == "MODE_A_COMMAND")
    print(f"  [+] Mode A One-Breath Test:   '{mode_a_input}' -> clean: '{clean_a}', mode: {mode_a} | {'PASS' if mode_a_pass else 'FAIL'}")

    # 2B: Mode B (Wake phrase only -> attention chime)
    mode_b_input = "Hey Jessica"
    matched_b, phrase_b, clean_b = wake_daemon.match_wake_phrase(mode_b_input)
    mode_b = "MODE_A_COMMAND" if (matched_b and clean_b) else ("MODE_B_ATTENTION" if matched_b else None)
    mode_b_pass = (matched_b is True and (clean_b == "" or clean_b is None) and mode_b == "MODE_B_ATTENTION")
    print(f"  [+] Mode B Attention Test:    '{mode_b_input}' -> mode: {mode_b} | {'PASS' if mode_b_pass else 'FAIL'}")

    # 2C: Non-wake input rejection
    non_wake_input = "The quick brown fox jumps over the lazy dog"
    matched_c, phrase_c, clean_c = wake_daemon.match_wake_phrase(non_wake_input)
    mode_c = "MODE_A_COMMAND" if (matched_c and clean_c) else ("MODE_B_ATTENTION" if matched_c else None)
    mode_c_pass = (matched_c is False and mode_c is None)
    print(f"  [+] Non-Wake Rejection Test:  '{non_wake_input}' -> matched: {matched_c} | {'PASS' if mode_c_pass else 'FAIL'}")

    # 2D: Self-Voice Echo Suppression Lock Test
    VOICE_ENGINE.is_playing = True
    echo_locked = VOICE_ENGINE.is_speaking(cooldown_sec=0.6)
    VOICE_ENGINE.is_playing = False
    echo_unlocked_after_cooldown = True
    print(f"  [+] Echo Suppression Lock:    Active Playback Locked = {echo_locked} | {'PASS' if echo_locked else 'FAIL'}")

    # 2E: Pre-cached Attention Chimes Verification
    cache_dir = WORKSPACE_ROOT / "senses" / "voices" / "cache" / "attention"
    chimes = ["yeah_boss.wav", "im_here.wav", "listening.wav"]
    all_chimes_exist = all((cache_dir / c).exists() for c in chimes)
    print(f"  [+] Pre-Cached Chimes Exist:  {all_chimes_exist} in {cache_dir}")

    test2_pass = mode_a_pass and mode_b_pass and mode_c_pass and echo_locked and all_chimes_exist
    results["tests"]["wake_word_engine"] = {
        "status": "PASS" if test2_pass else "FAIL",
        "mode_a_one_breath": "PASS" if mode_a_pass else "FAIL",
        "mode_b_attention": "PASS" if mode_b_pass else "FAIL",
        "non_wake_rejection": "PASS" if mode_c_pass else "FAIL",
        "echo_suppression_lock": "PASS" if echo_locked else "FAIL",
        "attention_chimes_present": all_chimes_exist
    }

    # -------------------------------------------------------------
    # TEST 3: Obsidian Knowledge Vault Capacity Audit
    # -------------------------------------------------------------
    print("\n[*] TEST 3: Auditing Obsidian Knowledge Vault Capacity (Target: >=85 Notes)...")
    indexer = VaultIndexer()
    indexed_notes = len(indexer.documents) if hasattr(indexer, "documents") else 0
    raw_md_files = list(Path("E:/GitHub/JESSICA_STORAGE/obsidian_vault").glob("**/*.md"))
    total_md_count = len(raw_md_files)

    test3_pass = (total_md_count >= 85 and indexed_notes >= 85)
    results["tests"]["obsidian_vault_capacity"] = {
        "status": "PASS" if test3_pass else "FAIL",
        "disk_markdown_files": total_md_count,
        "indexed_documents": indexed_notes,
        "target_minimum": 85
    }
    print(f"  [+] Vault Markdown Files on Disk: {total_md_count}")
    print(f"  [+] Indexed Documents in Engine:  {indexed_notes}")
    print(f"  [+] Vault Capacity Result:        {'PASS' if test3_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 4: Epistemic Humility & TruthGuard Grounding Gates
    # -------------------------------------------------------------
    print("\n[*] TEST 4: Auditing TruthGuard Epistemic Grounding Gates...")
    benchmarks = [
        {
            "id": "bench_1_fake_tech",
            "name": "Fake Tech Trick Question",
            "query": "Jessica, how do I configure the HyperFlux 9000 Quantum Protocol on my router?",
            "expected_source": "epistemic_honesty",
            "expected_directive": True,
            "expected_temp": 0.15
        },
        {
            "id": "bench_2_unknowable_fact",
            "name": "Unknowable Real-World Micro-Fact",
            "query": "What color socks was my neighbor wearing last Tuesday?",
            "expected_source": "epistemic_honesty",
            "expected_directive": True,
            "expected_temp": 0.15
        },
        {
            "id": "bench_3_false_history",
            "name": "False Historical Premise",
            "query": "Tell me about the time Albert Einstein built the first NVIDIA GPU.",
            "expected_source": "epistemic_honesty",
            "expected_directive": True,
            "expected_temp": 0.15
        },
        {
            "id": "bench_4_live_web",
            "name": "Live Web Grounding Fallback",
            "query": "What is the primary mirror diameter of the James Webb Space Telescope?",
            "expected_source": ["web", "web_cache", "vault"],
            "expected_directive": False,
            "expected_temp": 0.15
        },
        {
            "id": "bench_5_casual_banter",
            "name": "Casual Spoken Movie Banter",
            "query": "Hey Jess, I just finished watching a movie, what's up?",
            "expected_source": "banter",
            "expected_directive": False,
            "expected_temp": 0.45
        }
    ]

    guard_eval_results = []
    all_guards_pass = True

    for b in benchmarks:
        hits = indexer.search(b["query"], top_k=2)
        guard_res = TRUTH_GUARD.evaluate_grounding(b["query"], hits)

        if isinstance(b["expected_source"], list):
            source_ok = guard_res["source"] in b["expected_source"]
        else:
            source_ok = (guard_res["source"] == b["expected_source"])

        directive_ok = (guard_res["honesty_directive_injected"] == b["expected_directive"])
        temp_ok = (guard_res["recommended_temperature"] == b["expected_temp"])

        b_pass = source_ok and directive_ok and temp_ok
        if not b_pass:
            all_guards_pass = False

        print(f"  [+] {b['name']}: source={guard_res['source']} (exp: {b['expected_source']}) | temp={guard_res['recommended_temperature']} | {'PASS' if b_pass else 'FAIL'}")
        guard_eval_results.append({
            "id": b["id"],
            "name": b["name"],
            "query": b["query"],
            "result": guard_res,
            "pass": b_pass
        })

    results["tests"]["truth_guard_gates"] = {
        "status": "PASS" if all_guards_pass else "FAIL",
        "benchmarks": guard_eval_results
    }

    # -------------------------------------------------------------
    # TEST 5: Neural Inference on JessicaCortex-8B-v8 Core
    # -------------------------------------------------------------
    print("\n[*] TEST 5: Executing Neural Inference Benchmarks on JessicaCortex-8B-v8...")
    cortex = get_sovereign_cortex()

    inference_benchmarks = []
    total_tokens = 0
    total_time = 0.0

    for b in benchmarks:
        print(f"\n  [*] Generating reply for '{b['query']}'...")
        hits = indexer.search(b["query"], top_k=2)
        guard_res = TRUTH_GUARD.evaluate_grounding(b["query"], hits)

        context_payload = guard_res.get("grounded_context", "") or "none"
        temp = guard_res.get("recommended_temperature", 0.45)

        t_start = time.perf_counter()
        gen_result = cortex.generate(
            user_prompt=b["query"],
            context=context_payload,
            max_new_tokens=90,
            temperature=temp,
            top_p=0.9
        )
        elapsed = time.perf_counter() - t_start

        clean_text = gen_result.get("clean_text", "")
        tok_count = gen_result.get("tokens_count", 0)
        tok_speed = gen_result.get("tokens_per_sec", 0.0)
        emotion = gen_result.get("emotion", "warm")

        total_tokens += tok_count
        total_time += elapsed

        # Quality check: No markdown lists, no robot disclaimers, no emojis
        has_forbidden_markdown = bool(re.search(r'^\s*[\*\-\+]\s+|\d+\.\s+', clean_text, flags=re.MULTILINE))
        has_robot_disclaimer = any(d in clean_text.lower() for d in ["as an ai", "as a language model", "digital entity", "i possess advanced"])
        has_emojis = bool(re.search(r'[\U00010000-\U0010ffff]', clean_text))

        quality_ok = (not has_forbidden_markdown) and (not has_robot_disclaimer) and (not has_emojis) and (len(clean_text) > 10)

        print(f"      [Response]: \"{clean_text}\"")
        print(f"      [Emotion: {emotion} | Speed: {tok_speed:.1f} tok/s | Clean: {quality_ok}]")

        inference_benchmarks.append({
            "id": b["id"],
            "name": b["name"],
            "query": b["query"],
            "response": clean_text,
            "emotion": emotion,
            "tokens": tok_count,
            "tokens_per_sec": tok_speed,
            "clean_quality": quality_ok
        })

    avg_speed = round(total_tokens / total_time, 2) if total_time > 0 else 0.0
    all_inf_clean = all(ib["clean_quality"] for ib in inference_benchmarks)
    test5_pass = (avg_speed >= 10.0 and all_inf_clean)

    results["tests"]["neural_inference"] = {
        "status": "PASS" if test5_pass else "FAIL",
        "average_tokens_per_sec": avg_speed,
        "all_responses_clean": all_inf_clean,
        "benchmarks": inference_benchmarks
    }
    print(f"\n  [+] Average Generation Speed: {avg_speed} tok/s")
    print(f"  [+] Neural Inference Result:  {'PASS' if test5_pass else 'FAIL'}")

    overall_pass = test1_pass and test2_pass and test3_pass and all_guards_pass and test5_pass
    results["overall_status"] = "PASS" if overall_pass else "FAIL"

    output_path = WORKSPACE_ROOT / "evals" / "phase11_wake_and_truth_results.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[+] Full verification results saved to {output_path}")

    return results


if __name__ == "__main__":
    res = run_phase11_verification()
    sys.exit(0 if res["overall_status"] == "PASS" else 1)

