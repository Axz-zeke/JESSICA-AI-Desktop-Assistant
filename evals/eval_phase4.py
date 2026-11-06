"""
Evaluation suite for Jessica Phase 4: Full Sovereign Agent Upgrade.
Tests Biometrics, Wake-Word, Autonomous Web-to-Obsidian Learner, and the 5 new OS powers.
"""

import json
import urllib.request
import time

TEST_COMMANDS = [
    ("learn_from_internet", "Jessica, research Quantum Computing from the internet and save it to Obsidian"),
    ("learned_knowledge_qa", "What is Quantum Computing?"),
    ("control_window", "Minimize all windows"),
    ("type_and_automate", "Press ctrl+c"),
    ("search_local_files", "Search local files for test_voice.py"),
    ("verify_biometrics", "Scan my face with webcam")
]

def run_phase4_eval():
    url = "http://127.0.0.1:8000/api/command"
    results = []

    print("=" * 80)
    print("      RUNNING PHASE 4 LIVE EVALUATION SUITE")
    print("=" * 80)

    for i, (test_name, cmd) in enumerate(TEST_COMMANDS, 1):
        req_data = json.dumps({"command": cmd}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        elapsed = (time.perf_counter() - start) * 1000

        res = {
            "index": i,
            "test_name": test_name,
            "command": cmd,
            "intent": data.get("predicted_intent"),
            "confidence": data.get("confidence"),
            "emotion": data.get("emotion"),
            "spoken_reply": data.get("reply"),
            "raw_reply": data.get("raw_reply"),
            "action_result": data.get("action_result"),
            "audio_url": data.get("audio_url"),
            "latency_ms": data.get("latency_ms", elapsed),
            "tokens_per_sec": data.get("tokens_per_sec", 0.0)
        }
        results.append(res)

        print(f"\n[Test {i}/6] Command: '{cmd}'")
        print(f"  Category:       [{test_name}]")
        print(f"  Routed Intent:  [{res['intent']}] ({res['confidence']}%)")
        print(f"  Emotion:        [{res['emotion']}]")
        print(f"  Latency:        {res['latency_ms']:.1f}ms | Cortex: {res['tokens_per_sec']:.1f} tok/s")
        print(f"  Spoken Reply:   \"{res['spoken_reply']}\"")
        if res['action_result']:
            act_keys = list(res['action_result'].keys()) if isinstance(res['action_result'], dict) else []
            print(f"  Action Result:  Keys={act_keys} (Stored in collapsible JSON drawer)")

    with open("evals/phase4_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("      PHASE 4 EVALUATION COMPLETE - RESULTS SAVED")
    print("=" * 80)
    return results

if __name__ == "__main__":
    run_phase4_eval()

