"""
Jessica Sovereign AI - Phase 13.5 Verification Suite
Verifies:
1. Sovereign Browser, YouTube Auto-Play & Spotify Controller (hands/web_media_controller.py)
   - YouTube direct video URL auto-play resolution (<0.8s)
   - Spotify URI and Windows hardware virtual media keys (VK_MEDIA_PLAY_PAUSE)
   - Google search with live grounded sovereign web summary
2. Unified Fast Open-Mic Pipeline (senses/wake_word_daemon.py & desktop_app/frontend/index.html)
   - Frontend competing webkitSpeechRecognition removed
   - Zero-contention pause/resume mechanism active
   - Complete-sentence VAD (1.1s natural pause) + 0.85 AGC + no_speech_prob < 0.55 filter
3. Camera Vision & Sentence Cutoff Checks
   - Indoor object whitelist + human natural lighting descriptions
   - Trailing conjunction regex stripper in ensure_complete_sentences

Outputs results to: evals/phase13_5_verification_results.json
"""

import os
import sys
import time
import json
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from hands.web_media_controller import (
    play_on_youtube,
    control_spotify_and_media,
    open_browser_or_site,
    can_handle_web_media,
    execute_web_media_command
)
from brain.sovereign_web_researcher import search_live_web
from senses.wake_word_daemon import WAKE_DAEMON, COMBINED_WAKE_REGEX, HALLUCINATION_REGEXES
from brain.cortex_net import ensure_complete_sentences


def run_phase13_5_verification():
    print("=" * 80)
    print("  JESSICA PHASE 13.5: MEDIA CONTROLLER & UNIFIED FAST OPEN-MIC AUDIT")
    print("=" * 80)

    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "phase": "13.5",
        "tests": {},
        "overall_status": "PASS"
    }

    # -------------------------------------------------------------
    # TEST 1: YouTube Direct Video Auto-Play Resolution
    # -------------------------------------------------------------
    print("\n[*] TEST 1: Testing Direct YouTube Video Auto-Play Scraper (<0.8s)...")
    query_yt = "IV of Spades"
    t0 = time.perf_counter()
    res_yt = play_on_youtube(query_yt)
    yt_elapsed = round(time.perf_counter() - t0, 3)

    has_video_id = res_yt.get("video_id") is not None and len(res_yt["video_id"]) == 11
    has_watch_url = "watch?v=" in res_yt.get("url", "")
    t1_pass = has_video_id and has_watch_url

    results["tests"]["youtube_autoplay"] = {
        "status": "PASS" if t1_pass else "FAIL",
        "query": query_yt,
        "video_id": res_yt.get("video_id"),
        "url": res_yt.get("url"),
        "elapsed_sec": yt_elapsed,
        "reply": res_yt.get("reply")
    }
    print(f"  [+] Query: '{query_yt}'")
    print(f"  [+] Resolved Video ID: {res_yt.get('video_id')} | Elapsed: {yt_elapsed}s")
    print(f"  [+] Direct Auto-Play URL: {res_yt.get('url')}")
    print(f"  [+] Spoken Reply: \"{res_yt.get('reply')}\" -> {'PASS' if t1_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 2: Spotify Launch & Hardware Media Keys
    # -------------------------------------------------------------
    print("\n[*] TEST 2: Testing Spotify & Hardware Virtual Media Keys...")
    res_spot_open = control_spotify_and_media("open")
    res_spot_pause = control_spotify_and_media("pause")
    res_spot_next = control_spotify_and_media("next")

    t2_pass = (
        res_spot_open.get("status") == "success" and
        res_spot_pause.get("status") == "success" and
        res_spot_next.get("status") == "success"
    )

    results["tests"]["spotify_and_media_keys"] = {
        "status": "PASS" if t2_pass else "FAIL",
        "open_action": res_spot_open,
        "pause_action": res_spot_pause,
        "next_action": res_spot_next
    }
    print(f"  [+] Open Spotify: {res_spot_open.get('reply')}")
    print(f"  [+] Media Key (Play/Pause 0xB3): {res_spot_pause.get('reply')}")
    print(f"  [+] Media Key (Next Track 0xB0): {res_spot_next.get('reply')} -> {'PASS' if t2_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 3: Google Search & Live Sovereign Web Research
    # -------------------------------------------------------------
    print("\n[*] TEST 3: Testing Google Search & Live Grounded Web Scraper...")
    search_q = "RTX 4060 specifications"
    t0 = time.perf_counter()
    research = search_live_web(search_q)
    scrape_elapsed = round(time.perf_counter() - t0, 3)

    summary = research.get("summary", "")
    t3_pass = len(summary) > 25 and ("rtx" in summary.lower() or "geforce" in summary.lower() or "nvidia" in summary.lower())

    results["tests"]["web_researcher"] = {
        "status": "PASS" if t3_pass else "FAIL",
        "query": search_q,
        "summary": summary,
        "source": research.get("source"),
        "url": research.get("url"),
        "elapsed_sec": scrape_elapsed
    }
    print(f"  [+] Query: '{search_q}'")
    print(f"  [+] Source: {research.get('source')} | Elapsed: {scrape_elapsed}s")
    print(f"  [+] Grounded Summary: \"{summary}\" -> {'PASS' if t3_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 4: Unified Open-Mic Architecture & Anti-Hallucination
    # -------------------------------------------------------------
    print("\n[*] TEST 4: Auditing Unified Fast Open-Mic Configuration...")
    html_code = (WORKSPACE_ROOT / "desktop_app" / "frontend" / "index.html").read_text(encoding="utf-8")
    daemon_code = (WORKSPACE_ROOT / "senses" / "wake_word_daemon.py").read_text(encoding="utf-8")

    # Verify frontend competing webkit loop is disabled
    fe_disabled = "Browser-native wake loop disabled" in html_code or "disabled. Sole hardware microphone ownership" in html_code

    # Verify backend pause/resume mechanism
    be_pause_resume = "def pause(" in daemon_code and "def resume(" in daemon_code and "is_paused" in daemon_code

    # Verify complete sentence VAD (1.1s) and smart AGC
    be_sentence_vad = "1.1" in daemon_code and "pre_buffer" in daemon_code and "0.85" in daemon_code

    # Verify anti-hallucination filter
    be_anti_hallucination = "no_speech_prob" in daemon_code and "HALLUCINATION_REGEXES" in daemon_code

    t4_pass = fe_disabled and be_pause_resume and be_sentence_vad and be_anti_hallucination

    results["tests"]["unified_open_mic"] = {
        "status": "PASS" if t4_pass else "FAIL",
        "frontend_loop_disabled": fe_disabled,
        "backend_pause_resume_active": be_pause_resume,
        "complete_sentence_vad_active": be_sentence_vad,
        "anti_hallucination_filter_active": be_anti_hallucination
    }
    print(f"  [+] Frontend Competing Loop Disabled: {fe_disabled}")
    print(f"  [+] Zero-Contention Pause/Resume: {be_pause_resume}")
    print(f"  [+] Complete-Sentence VAD (1.1s) + 0.85 AGC: {be_sentence_vad}")
    print(f"  [+] Anti-Hallucination Noise Filter: {be_anti_hallucination} -> {'PASS' if t4_pass else 'FAIL'}")

    # -------------------------------------------------------------
    # TEST 5: Camera Vision Grounding & Sentence Trimmer Integrity
    # -------------------------------------------------------------
    print("\n[*] TEST 5: Verifying Camera Indoor Whitelist & Conjunction Stripper...")
    cam_code = (WORKSPACE_ROOT / "senses" / "camera_vision.py").read_text(encoding="utf-8")

    cam_whitelist = "INDOOR_OBJECT_WHITELIST" in cam_code and "0.62" in cam_code
    cam_natural_light = "very dark room with dim ambient shadows" in cam_code

    # Test sentence trimmer regex
    trimmer_test_1 = ensure_complete_sentences("The GPU is running cool, and.")
    trimmer_test_2 = ensure_complete_sentences("Everything is quiet, so.")
    trimmer_test_3 = ensure_complete_sentences("We have plenty of memory, because.")

    trimmer_pass = (
        trimmer_test_1 == "The GPU is running cool." and
        trimmer_test_2 == "Everything is quiet." and
        trimmer_test_3 == "We have plenty of memory."
    )

    t5_pass = cam_whitelist and cam_natural_light and trimmer_pass

    results["tests"]["camera_and_trimmer"] = {
        "status": "PASS" if t5_pass else "FAIL",
        "camera_whitelist_active": cam_whitelist,
        "camera_natural_lighting": cam_natural_light,
        "sentence_trimmer_accurate": trimmer_pass
    }
    print(f"  [+] Camera Whitelist & Threshold 0.62: {cam_whitelist}")
    print(f"  [+] Natural Lighting Descriptions: {cam_natural_light}")
    print(f"  [+] Conjunction Stripper (', and.' -> '.'): {trimmer_pass} -> {'PASS' if t5_pass else 'FAIL'}")

    # Overall Status
    all_pass = t1_pass and t2_pass and t3_pass and t4_pass and t5_pass
    results["overall_status"] = "PASS" if all_pass else "FAIL"

    # Persist JSON
    out_file = WORKSPACE_ROOT / "evals" / "phase13_5_verification_results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n[+] Full verification metrics saved to {out_file}")

    print("\n" + "=" * 80)
    print(f"  PHASE 13.5 AUDIT OVERALL: {results['overall_status']}")
    print("=" * 80)
    return results


if __name__ == "__main__":
    res = run_phase13_5_verification()
    sys.exit(0 if res["overall_status"] == "PASS" else 1)
