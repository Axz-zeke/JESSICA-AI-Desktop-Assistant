import urllib.request
import json
import time

def test_api():
    commands = [
        "Jessica, play IV of Spades on YouTube",
        "Pause the music",
        "Open Google and search for RTX 4060 specs"
    ]
    for cmd in commands:
        print(f"\n==========================================")
        print(f"Command: {cmd}")
        payload = json.dumps({"command": cmd}).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:8000/api/command", data=payload, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                elapsed = time.time() - t0
                data = json.loads(resp.read().decode("utf-8"))
                print(f"Status: {resp.status} (Total Roundtrip: {elapsed:.3f}s)")
                print(f"Predicted Intent: {data.get('predicted_intent')} (Conf: {data.get('confidence')}%)")
                print(f"Reply: \"{data.get('reply')}\"")
                print(f"Action Result: {json.dumps(data.get('action_result'), indent=2)}")
                print(f"Latency: {data.get('latency_ms'):.1f}ms | TTS Waveform Len: {len(data.get('waveform', []))}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
