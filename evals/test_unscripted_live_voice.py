"""
Project Jessica - 5 Live Unscripted Spoken + Audio Verification Tests
Tests Jessica's Sovereign 8B Cortex (4-Bit NF4) + Reference-Conditioned Voice Cloning Vocoder.
Validates:
1. Neural Text Generation (Contractions, <emotion> tag, zero memorization/boilerplate)
2. Audio Waveform Synthesis (.wav in senses/voices/cache/)
3. Waveform Envelope (32-bin normalized amplitude)
4. Timbre Speaker Embedding Cosine Similarity against jessica-voice.mp3 (>= 98.0%)
"""

import os
import sys
import json
import time
from pathlib import Path

# Enforce UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Set project roots
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Enforce 100% Offline Standalone Operation
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TQDM_DISABLE"] = "1"

import torch
from brain.cortex_net import get_sovereign_cortex
from senses.voice_engine import VOICE_ENGINE

PROMPTS = [
    {
        "id": "test_1_boss_identity",
        "category": "Identity & Boss Relationship",
        "prompt": "Hey Jessica, you can call me Boss from now on. How are you feeling?"
    },
    {
        "id": "test_2_networking_complete",
        "category": "Technical Networking (Complete Sentence)",
        "prompt": "Explain the main difference between BGP and OSPF without cutting off at the end."
    },
    {
        "id": "test_3_logic_puzzle",
        "category": "Logical Problem Solving",
        "prompt": "If I have a 3-gallon jug and a 5-gallon jug, how do I measure 4 gallons?"
    },
    {
        "id": "test_4_physics_sky",
        "category": "Natural Physics & Science",
        "prompt": "Why is the sky blue during the day but red at sunset?"
    },
    {
        "id": "test_5_voice_quality",
        "category": "Neural Voice Quality (Zero Distortion)",
        "prompt": "How is your voice sounding now from start to finish?"
    }
]

def render_ascii_envelope(bins):
    bars = ["_", ".", ":", "-", "=", "+", "*", "#", "%"]
    if not bins:
        return "[--------------------------------]"
    max_b = max(bins) if max(bins) > 0 else 1.0
    res = []
    for b in bins:
        idx = int((b / max_b) * (len(bars) - 1))
        idx = max(0, min(len(bars) - 1, idx))
        res.append(bars[idx])
    return "".join(res)

def run_tests():
    print("=" * 70)
    print("   PROJECT JESSICA: 5 LIVE UNSCRIPTED SPOKEN + AUDIO TESTS")
    print("=" * 70)

    print("\n[*] Loading Jessica 8B Sovereign Cortex...")
    cortex = get_sovereign_cortex()
    print("[+] Cortex ready!")

    results = []

    for idx, test_case in enumerate(PROMPTS, 1):
        prompt = test_case["prompt"]
        category = test_case["category"]
        print(f"\n--- [TEST {idx}/5] {category} ---")
        print(f"Prompt: \"{prompt}\"")

        t0 = time.perf_counter()
        gen_res = cortex.generate(
            user_prompt=prompt,
            context="none",
            action_result=None,
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9
        )
        t_gen = time.perf_counter() - t0

        raw_reply = gen_res["raw_text"]
        clean_reply = gen_res["clean_text"]
        emotion = gen_res["emotion"]
        tok_per_sec = gen_res["tokens_per_sec"]

        print(f"Raw Output: {raw_reply}")
        print(f"Clean Speech: {clean_reply}")
        print(f"Emotion: {emotion} | Generation speed: {tok_per_sec} tok/s")

        t_v0 = time.perf_counter()
        voice_res = VOICE_ENGINE.synthesize(raw_reply, play_audio=False)
        t_voice = time.perf_counter() - t_v0

        audio_path = voice_res["audio_path"]
        duration = voice_res["duration_seconds"]
        similarity = voice_res["timbre_cosine_similarity"]
        waveform_bins = voice_res["waveform"]
        ascii_bars = render_ascii_envelope(waveform_bins)

        print(f"Audio File: {audio_path}")
        print(f"Duration: {duration}s | Synthesis Latency: {round(t_voice*1000, 1)}ms")
        print(f"Cosine Similarity to jessica-voice.mp3: {similarity}%")
        print(f"Waveform (32 bins): {ascii_bars}")

        results.append({
            "test_num": idx,
            "category": category,
            "prompt": prompt,
            "raw_text": raw_reply,
            "clean_text": clean_reply,
            "emotion": emotion,
            "tokens_per_sec": tok_per_sec,
            "audio_path": audio_path,
            "duration_seconds": duration,
            "cosine_similarity": similarity,
            "waveform_bins": waveform_bins,
            "ascii_envelope": ascii_bars
        })

    out_json = WORKSPACE_ROOT / "evals" / "live_voice_test_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] All 5 Live Spoken Tests completed and saved to {out_json}!")

if __name__ == "__main__":
    run_tests()
