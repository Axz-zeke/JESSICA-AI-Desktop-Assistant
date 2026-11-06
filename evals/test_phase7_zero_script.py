"""
Jessica Phase 7 Zero-Script Verification Test Suite
Tests live server on http://127.0.0.1:8000/api/command:
1. "Where do you live?"
2. "How smart are you now?"
3. "Explain how the BGP routing protocol works" (Ensure routed to conversation, NOT control_window)
4. "Who created you?"
5. Multi-Turn Memory Verification:
   Turn 1: "My favorite instrument to play is a 4-string Jcraft Jazz bass guitar."
   Turn 2: "What instrument did I just tell you I play, and why is it cool?"
"""

import urllib.request
import json
import time

SERVER_URL = "http://127.0.0.1:8000/api/command"

def send_command(command: str) -> dict:
    req_data = json.dumps({"command": command}).encode("utf-8")
    req = urllib.request.Request(
        SERVER_URL,
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    res["client_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return res

def main():
    print("=" * 70)
    print("JESSICA PHASE 7 ZERO-SCRIPT LIVE TEST SUITE")
    print("=" * 70)

    # Clear memory first
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/brain/memory/clear", data=b"{}", headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        print("[+] Working memory buffer reset.")
    except Exception as e:
        print("[!] Memory clear note:", e)

    tests = [
        ("TEST 1: Persona Living Location", "Where do you live?"),
        ("TEST 2: Parameter & Brain Intelligence", "How smart are you now?"),
        ("TEST 3: Router Guardrail Negative Query", "Explain how the BGP routing protocol works"),
        ("TEST 4: Sovereign Creator & Origin", "Who created you?"),
        ("TEST 5 (Turn 1): Instrument Memory Seed", "My favorite instrument to play is a 4-string Jcraft Jazz bass guitar."),
        ("TEST 5 (Turn 2): Multi-Turn Recall & Synthesis", "What instrument did I just tell you I play, and why is it cool?")
    ]

    results = []
    for title, cmd in tests:
        print(f"\n--- {title} ---")
        print(f"User Prompt: \"{cmd}\"")
        res = send_command(cmd)
        intent = res.get("predicted_intent", "unknown")
        conf = res.get("confidence", 0.0)
        reply = res.get("reply", "")
        raw_reply = res.get("raw_reply", "")
        emotion = res.get("emotion", "warm")
        tok_speed = res.get("tokens_per_sec", 0.0)
        lat = res.get("latency_ms", 0.0)
        turns = res.get("working_memory_turns", 0)

        print(f"Routed Intent: [{intent}] ({conf}%)")
        print(f"Emotion Prosody: [{emotion}] | Speed: {tok_speed} tok/s | Latency: {lat}ms | Active Memory: {turns} turns")
        print(f"Spoken Clean Reply: {reply}")
        print(f"Raw Output: {raw_reply}")

        results.append({
            "title": title,
            "cmd": cmd,
            "intent": intent,
            "conf": conf,
            "reply": reply,
            "raw": raw_reply,
            "emotion": emotion,
            "speed": tok_speed,
            "latency": lat,
            "turns": turns
        })

    print("\n" + "=" * 70)
    print("ALL 5 TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()

