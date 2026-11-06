"""
Jessica Phase 3 - Evaluation Script
Executes the 6 critical test queries against the live Mission Control server and records word-for-word responses.
"""

import json
import urllib.request
import time

TEST_QUERIES = [
    "Hi",
    "How are you feeling today Jessica?",
    "Who are you and who created you?",
    "Check my RTX 4060 GPU temperature and system telemetry",
    "What are the thermal limits in my Obsidian vault?",
    "Is my internet connection working?"
]

URL = "http://127.0.0.1:8000/api/command"

results = []

for q in TEST_QUERIES:
    req_data = json.dumps({"command": q}).encode("utf-8")
    req = urllib.request.Request(URL, data=req_data, headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    data["total_eval_elapsed_ms"] = elapsed
    results.append(data)
    time.sleep(0.5)

print(json.dumps(results, indent=2))

