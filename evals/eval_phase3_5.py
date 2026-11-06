"""
Evaluation suite for Phase 3.5: Voice Lock & Cortex v3 Generalization.
Tests the 8 core prompts against Jessica's live API.
"""

import json
import urllib.request
import time

TEST_PROMPTS = [
    "Hi",
    "Who are you?",
    "Tell me who you are",
    "How can you help me?",
    "What can you do for me Jessica?",
    "Who are you and who created you?",
    "How are you feeling today?",
    "Check my RTX 4060 telemetry"
]

def run_eval():
    url = "http://127.0.0.1:8000/api/command"
    results = []

    print("=" * 80)
    print("      RUNNING PHASE 3.5 LIVE EVALUATION SUITE")
    print("=" * 80)

    for i, p in enumerate(TEST_PROMPTS, 1):
        req_data = json.dumps({"command": p}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )

        start = time.perf_counter()
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        elapsed = (time.perf_counter() - start) * 1000

        res = {
            "index": i,
            "prompt": p,
            "intent": data.get("predicted_intent"),
            "confidence": data.get("confidence"),
            "emotion": data.get("emotion"),
            "reply": data.get("reply"),
            "raw_reply": data.get("raw_reply"),
            "audio_url": data.get("audio_url"),
            "latency_ms": data.get("latency_ms", elapsed),
            "tokens_per_sec": data.get("tokens_per_sec", 0.0)
        }
        results.append(res)

        print(f"\n[Test {i}/8] Prompt: '{p}'")
        print(f"  Intent:         [{res['intent']}] ({res['confidence']}%)")
        print(f"  Emotion:        [{res['emotion']}]")
        print(f"  Latency / Tok:  {res['latency_ms']:.1f}ms | {res['tokens_per_sec']:.1f} tok/s")
        print(f"  Audio File:     {res['audio_url']}")
        print(f"  Spoken Reply:   \"{res['reply']}\"")

    with open("evals/phase3_5_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 80)
    print("      PHASE 3.5 EVALUATION COMPLETE - RESULTS SAVED")
    print("=" * 80)
    return results

if __name__ == "__main__":
    run_eval()

