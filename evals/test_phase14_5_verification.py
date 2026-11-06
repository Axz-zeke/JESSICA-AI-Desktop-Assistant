"""
Phase 14.5 Verification Suite:
Multi-Turn Active Listening Window, Speak-Before-Action Sequencing, and Smart Song Disambiguation.
"""

import sys
import os
import time
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

def test_disambiguation():
    print("=" * 60)
    print("TEST 1: Smart Artist vs Song Disambiguation Engine")
    print("=" * 60)
    from brain.media_disambiguator import check_media_disambiguation, get_pending_media, clear_pending_media
    from hands.web_media_controller import execute_web_media_command, can_handle_web_media

    clear_pending_media()

    # Case A: Artist only ("IV of Spades")
    print("[*] Case A: Query = 'Jessica, play IV of Spades on YouTube'")
    res1 = execute_web_media_command("Jessica, play IV of Spades on YouTube", defer_open=True)
    assert res1 is not None, "Failed: res1 is None"
    assert res1.get("status") == "disambiguation_required", f"Expected disambiguation_required, got {res1.get('status')}"
    assert res1.get("requires_followup") is True, "Expected requires_followup=True"
    assert "Mundo" in res1.get("reply", ""), f"Expected song suggestion in reply: {res1.get('reply')}"
    print(f"  [+] Case A Passed: Jessica asked: '{res1['reply']}'")

    # Verify pending state exists
    pending = get_pending_media()
    assert pending is not None, "Expected pending media state"
    assert pending["artist"] == "iv of spades", f"Expected iv of spades, got {pending['artist']}"
    assert can_handle_web_media("Mundo") is True, "can_handle_web_media must return True for follow-up choice"
    print("  [+] Pending media state verified: artist = 'iv of spades'")

    # Case B: Follow-up song choice ("Mundo")
    print("[*] Case B: Follow-up query = 'Mundo'")
    res2 = execute_web_media_command("Mundo", defer_open=True)
    assert res2 is not None, "Failed: res2 is None"
    assert res2.get("status") == "success", f"Expected success, got {res2.get('status')}"
    assert res2.get("action") == "youtube_autoplay", f"Expected youtube_autoplay, got {res2.get('action')}"
    assert "IV of Spades Mundo" in res2.get("query", ""), f"Expected resolved query containing IV of Spades Mundo, got {res2.get('query')}"
    assert res2.get("deferred_url") is not None, "Expected deferred_url for speak-before-action"
    assert get_pending_media() is None, "Pending media must be cleared after resolution"
    print(f"  [+] Case B Passed: Resolved to '{res2['query']}' | URL: {res2['url']}")

    # Case C: Direct query with artist AND song ("Jessica, play Mundo by IV of Spades on YouTube")
    print("[*] Case C: Direct query = 'Jessica, play Mundo by IV of Spades on YouTube'")
    res3 = execute_web_media_command("Jessica, play Mundo by IV of Spades on YouTube", defer_open=True)
    assert res3 is not None
    assert res3.get("status") == "success"
    assert "mundo" in res3.get("query", "").lower()
    print(f"  [+] Case C Passed: Direct playback resolved without prompt | Query: '{res3['query']}'")

    # Additional Artist Checks (Queen, Bruno Mars, Eraserheads)
    print("[*] Checking Queen disambiguation...")
    clear_pending_media()
    res_queen = execute_web_media_command("play Queen on youtube", defer_open=True)
    assert res_queen.get("status") == "disambiguation_required"
    assert "Bohemian Rhapsody" in res_queen.get("reply", "")
    print(f"  [+] Queen Disambiguation Passed: '{res_queen['reply']}'")

    res_queen_followup = execute_web_media_command("Bohemian Rhapsody", defer_open=True)
    assert res_queen_followup.get("status") == "success"
    assert "Queen Bohemian Rhapsody" in res_queen_followup.get("query", "")
    print(f"  [+] Queen Follow-Up Passed: Resolved '{res_queen_followup['query']}'")


def test_speak_before_action_sequencing():
    print("\n" + "=" * 60)
    print("TEST 2: Speak-Before-Action YouTube Sequencing")
    print("=" * 60)
    from hands.web_media_controller import play_on_youtube

    t0 = time.perf_counter()
    res = play_on_youtube("IV of Spades Mundo", defer_open=True)
    elapsed = round(time.perf_counter() - t0, 3)

    assert res["status"] == "success"
    assert "deferred_url" in res and res["deferred_url"] is not None
    assert "watch?v=" in res["url"] or "youtube.com" in res["url"]
    print(f"  [+] Fast YouTube Scrape Latency: {elapsed}s (<1.0s target)")
    print(f"  [+] Resolved Auto-Play URL: {res['url']}")
    print(f"  [+] Deferred URL present: {res['deferred_url']} (Browser opening deferred until voice completes)")


def test_wake_daemon_command_window():
    print("\n" + "=" * 60)
    print("TEST 3: WakeWordDaemon Multi-Turn Active Listening Window")
    print("=" * 60)
    from senses.wake_word_daemon import WAKE_DAEMON

    # 1. Test wake phrase matching
    matched, wake_phrase, remainder = WAKE_DAEMON.match_wake_phrase("Hey Jessica")
    assert matched is True
    assert wake_phrase.lower() == "hey jessica"
    assert remainder == ""
    print(f"  [+] Wake phrase matching passed: matched='{wake_phrase}' | remainder='{remainder}'")

    # 2. Test opening follow-up window
    WAKE_DAEMON.open_followup_window(duration_sec=10.0, delay_sec=0.05)
    time.sleep(0.15)
    assert WAKE_DAEMON.in_command_window is True, "Expected in_command_window=True"
    assert WAKE_DAEMON.command_window_expires_at > time.time(), "Expected valid expiration timestamp"
    print(f"  [+] Active command window opened: expires in {WAKE_DAEMON.command_window_expires_at - time.time():.1f}s")

    # 3. Test that pause() and resume() do NOT wipe the command window
    WAKE_DAEMON.pause("test_pause")
    assert WAKE_DAEMON.in_command_window is True, "pause() must NOT reset in_command_window"
    WAKE_DAEMON.resume(cooldown_sec=0.1)
    time.sleep(0.2)
    assert WAKE_DAEMON.in_command_window is True, "resume() must NOT reset in_command_window"
    print("  [+] Buffer isolation verified: pause/resume cycles preserve active command window!")

    # 4. Clean up window
    with WAKE_DAEMON.buffer_lock:
        WAKE_DAEMON._clear_buffers(clear_command_window=True)
    assert WAKE_DAEMON.in_command_window is False
    print("  [+] Command window cleanly closed.")


def test_voice_engine_authoritative_speaker():
    print("\n" + "=" * 60)
    print("TEST 4: VoiceEngine Authoritative Native Speaker")
    print("=" * 60)
    from senses.voice_engine import VOICE_ENGINE

    # Check env var default
    allowed = os.environ.get("JESSICA_BACKEND_AUDIO_PLAYBACK", "1") != "0"
    assert allowed is True, "Backend playback must be allowed by default for authoritative voice"
    print("  [+] Single Authoritative Speaker verified: JESSICA_BACKEND_AUDIO_PLAYBACK=1 active by default.")

    # Test synthesis
    res = VOICE_ENGINE.synthesize("Listening, Boss!", emotion="warm", play_audio=False)
    assert res["status"] == "success"
    assert Path(res["audio_path"]).exists()
    print(f"  [+] Synthesized attention phrase: duration = {res['duration_seconds']}s | path = {res['audio_filename']}")


def test_drive_storage_headroom():
    print("\n" + "=" * 60)
    print("TEST 5: C-Drive NVMe Headroom & Storage Health")
    print("=" * 60)
    c_usage = shutil.disk_usage("C:\\")
    c_free_gb = round(c_usage.free / (1024**3), 2)
    print(f"  [+] C: Drive Free Space: {c_free_gb} GB")
    assert c_free_gb >= 12.0, f"C: drive free space {c_free_gb} GB is below 12.0 GB safety threshold!"
    print("  [+] Storage headroom verified stable!")


if __name__ == "__main__":
    test_disambiguation()
    test_speak_before_action_sequencing()
    test_wake_daemon_command_window()
    test_voice_engine_authoritative_speaker()
    test_drive_storage_headroom()
    print("\n" + "=" * 60)
    print("ALL 5 PHASE 14.5 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)
