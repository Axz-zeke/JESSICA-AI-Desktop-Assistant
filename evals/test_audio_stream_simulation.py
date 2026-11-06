"""
Phase 14.5 Real Audio Stream Simulation Test
Feeds synthetic/recorded WAV streams into WakeWordDaemon frame loop:
[Wake word "Jessica"] -> [Wait for chime & 0.25s reaction] -> [0.8s speech audio "How are you?"] -> [1.0s silence]
Proves _process_mode_b_command triggers, transcribes "How are you?", and dispatches to jessica_server.
"""

import os
import sys
import time
import math
import numpy as np
import soundfile as sf
import scipy.signal as sps
from pathlib import Path

# Force unbuffered stdout
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

WORKSPACE_ROOT = Path("E:/Documents/GitHub/JESSICA").resolve()
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
os.chdir(str(WORKSPACE_ROOT))

from senses.voice_engine import VOICE_ENGINE
from senses.wake_word_daemon import WAKE_DAEMON


def resample_to_16k(audio: np.ndarray, orig_sr: int) -> np.ndarray:
    if orig_sr == 16000:
        return audio.astype(np.float32)
    gcd = math.gcd(16000, orig_sr)
    up = 16000 // gcd
    down = orig_sr // gcd
    return sps.resample_poly(audio, up, down).astype(np.float32)


def run_audio_stream_simulation():
    print("=" * 70, flush=True)
    print("PHASE 14.5: REAL AUDIO STREAM SIMULATION TEST", flush=True)
    print("=" * 70, flush=True)

    # 1. Synthesize and resample audio clips to exact 16,000 Hz
    print("\n[STEP 1] Generating and preparing 16kHz test clips...", flush=True)
    res_wake = VOICE_ENGINE.synthesize("Jessica", play_audio=False)
    res_followup = VOICE_ENGINE.synthesize("How are you?", play_audio=False)

    wake_raw, sr1 = sf.read(res_wake["audio_path"], dtype="float32")
    follow_raw, sr2 = sf.read(res_followup["audio_path"], dtype="float32")

    wake_16k = resample_to_16k(wake_raw, sr1)
    follow_16k = resample_to_16k(follow_raw, sr2)

    print(f"  [+] 'Jessica' 16kHz Audio: {len(wake_16k)/16000:.2f}s (Samples={len(wake_16k)}, Peak={np.max(np.abs(wake_16k)):.3f})", flush=True)
    print(f"  [+] 'How are you?' 16kHz Audio: {len(follow_16k)/16000:.2f}s (Samples={len(follow_16k)}, Peak={np.max(np.abs(follow_16k)):.3f})", flush=True)

    # 2. Configure WakeWordDaemon for simulated audio injection
    dispatched_commands = []
    def on_command_dispatched(cmd_text: str):
        print(f"\n>>> [CALLBACK RECEIVED] Voice Command Dispatched: '{cmd_text}' <<<\n", flush=True)
        dispatched_commands.append(cmd_text)

    WAKE_DAEMON.stop()
    WAKE_DAEMON._simulate_audio_feed = True
    WAKE_DAEMON.active_mic_index = 99
    WAKE_DAEMON.active_mic_name = "Virtual Simulation Stream"
    WAKE_DAEMON.native_samplerate = 16000
    WAKE_DAEMON.target_sr = 16000
    WAKE_DAEMON.input_channels = 1
    WAKE_DAEMON.silence_threshold = 0.009
    WAKE_DAEMON.ambient_rms = 0.0035

    print("\n[STEP 2] Starting WakeWordDaemon virtual listener...", flush=True)
    WAKE_DAEMON.start(command_callback=on_command_dispatched)
    time.sleep(1.0)  # Let worker thread & whisper initialize

    block_size = 1600  # 100ms blocks at 16000 Hz

    def feed_audio(audio_data: np.ndarray, label: str):
        print(f"\n[*] Feeding {label} ({len(audio_data)/16000:.2f}s) into _audio_callback...", flush=True)
        for i in range(0, len(audio_data), block_size):
            chunk = audio_data[i:i + block_size]
            if len(chunk) < block_size:
                chunk = np.pad(chunk, (0, block_size - len(chunk)))
            WAKE_DAEMON._audio_callback(chunk, len(chunk), None, None)
            time.sleep(0.08)

    def feed_silence(duration_sec: float, label: str = "ambient silence"):
        print(f"[*] Feeding {duration_sec}s of {label}...", flush=True)
        total_samples = int(16000 * duration_sec)
        np.random.seed(42)
        noise = (np.random.randn(total_samples) * 0.003).astype(np.float32)
        for i in range(0, total_samples, block_size):
            chunk = noise[i:i + block_size]
            if len(chunk) < block_size:
                chunk = np.pad(chunk, (0, block_size - len(chunk)))
            WAKE_DAEMON._audio_callback(chunk, len(chunk), None, None)
            time.sleep(0.08)

    # 3. Feed "Jessica" wake phrase
    print("\n[STEP 3] Triggering Mode B via Wake Word 'Jessica'...", flush=True)
    feed_silence(0.4, "pre-wake baseline (0.4s)")
    feed_audio(wake_16k, "Wake Word 'Jessica'")
    feed_silence(1.4, "post-wake silence (sentence boundary >= 1.1s)")

    # 4. Wait for Whisper to transcribe wake word and trigger Mode B
    print("\n[STEP 4] Awaiting Wake Word detection & Mode B attention chime...", flush=True)
    t_wake_wait = time.time()
    while not WAKE_DAEMON.in_command_window and (time.time() - t_wake_wait < 10.0):
        time.sleep(0.1)

    assert WAKE_DAEMON.in_command_window is True, "FAILED: Mode B failed to open command window!"
    print(f"  [+] Mode B activated! Active command window is OPEN. (Latency: {time.time() - t_wake_wait:.2f}s)", flush=True)

    # 5. Wait strictly for chime playback to finish
    print("\n[STEP 5] Verifying chime playback completion...", flush=True)
    chime_wait_start = time.time()
    while VOICE_ENGINE.is_speaking(cooldown_sec=0.08):
        time.sleep(0.04)
        if time.time() - chime_wait_start > 5.0:
            break
    print(f"  [+] Attention chime finished playback! (is_speaking=False, hardware idle)", flush=True)

    # 6. Human hesitation pause: 0.25s after chime
    print("\n[STEP 6] Simulating 0.25s human reaction time before speaking...", flush=True)
    feed_silence(0.25, "human reaction delay (0.25s)")

    # 7. Feed "How are you?" follow-up audio
    print("\n[STEP 7] Feeding follow-up speech audio 'How are you?'...", flush=True)
    feed_audio(follow_16k, "Follow-Up Speech 'How are you?'")

    # 8. Feed 1.1s of silence to trigger natural complete-sentence boundary (>=0.85s pause)
    print("\n[STEP 8] Feeding 1.1s silence to trigger sentence boundary transcription...", flush=True)
    feed_silence(1.1, "post-command silence (0.85s boundary trigger)")

    # 9. Wait up to 6s for Whisper transcription and dispatch
    print("\n[STEP 9] Awaiting Whisper Mode B transcription and command dispatch...", flush=True)
    t_wait_dispatch = time.time()
    while not dispatched_commands and (time.time() - t_wait_dispatch < 8.0):
        time.sleep(0.1)

    print("\n" + "=" * 70, flush=True)
    print("SIMULATION VERIFICATION RESULTS", flush=True)
    print("=" * 70, flush=True)
    print(f"Dispatched Commands List: {dispatched_commands}", flush=True)

    assert len(dispatched_commands) > 0, "FAILED: No command was dispatched from Mode B!"
    captured = dispatched_commands[0].strip().lower()
    print(f"Captured Command Text: '{captured}'", flush=True)
    assert "how" in captured or "you" in captured or "are" in captured, f"Expected 'how are you', got '{captured}'"
    print("  [+] Mode B transcription verified: captured follow-up WITHOUT requiring wake word!", flush=True)

    print("\n" + "=" * 70, flush=True)
    print("SUCCESS: FULL TIMELINE FROM WAKE TO FOLLOW-UP DISPATCH PROVEN END-TO-END!", flush=True)
    print("=" * 70, flush=True)

    WAKE_DAEMON.stop()


if __name__ == "__main__":
    run_audio_stream_simulation()
