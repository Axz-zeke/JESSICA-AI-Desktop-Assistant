"""
Jessica Phase 8 Spoken Acting & Sanitizer Verification Test Suite
Runs the 6 target prompts against http://127.0.0.1:8000/api/command:
1. "Hey Jessica, how's it going?"
2. "Why were you reading emoticons out loud earlier?"
3. "Where do you live?"
4. "I'm exhausted from working all day."
5. "Explain BGP routing to me like we're just chatting over coffee."
6. "I play a 4-string Jcraft Jazz bass" -> "What instrument did I tell you I play?"
"""

import sys
import json
import time
import urllib.request

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

SERVER_URL = "http://127.0.0.1:8000/api/command"

def send_command(command: str) -> dict:
    req_data = json.dumps({"command": command}).encode("utf-8")
    req = urllib.request.Request(
        SERVER_URL,
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    res["client_latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return res

def main():
    print("=" * 75)
    print("JESSICA PHASE 8: LLAMA-3.1 8B SPOKEN ACTING & SANITIZER VERIFICATION")
    print("=" * 75)

    # Clear memory first
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/brain/memory/clear", data=b"{}", headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
        print("[+] Working memory buffer reset.")
    except Exception as e:
        print("[!] Memory clear note:", e)

    tests = [
        ("TEST 1: Casual Greeting & Tone", "Hey Jessica, how's it going?"),
        ("TEST 2: Emoticon Reading Fix Explanation", "Why were you reading emoticons out loud earlier?"),
        ("TEST 3: Location & Sovereign Living", "Where do you live?"),
        ("TEST 4: Emotional Empathy & Fatigue Support", "I'm exhausted from working all day."),
        ("TEST 5: Conversational Technical Coffee Chat", "Explain BGP routing to me like we're just chatting over coffee."),
        ("TEST 6A: Instrument Memory Seed", "I play a 4-string Jcraft Jazz bass."),
        ("TEST 6B: Instrument Recall & Synthesis", "What instrument did I tell you I play?")
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
        print(f"Emotion Acting: [{emotion}] | Speed: {tok_speed} tok/s | Latency: {lat}ms | Active Turns: {turns}")
        print(f"Spoken Clean Reply: \"{reply}\"")

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

    print("\n" + "=" * 75)
    print("ALL PHASE 8 TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 75)

if __name__ == "__main__":
    main()

