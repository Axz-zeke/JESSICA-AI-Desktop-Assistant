"""
Jessica Senses - Unified Fast Open-Mic Wake-Word Engine (Phase 13.5)
Features:
1. Native Sample Rate capture (44.1kHz / 48kHz) with Polyphase FIR Resampling to 16kHz float32.
2. Complete-Sentence VAD (1.1s natural pause detection) matching ear_engine.py manual mic accuracy.
3. Anti-Hallucination & Noise Gate: vad_filter=True, no_speech_prob < 0.55, and subtitle/hallucination blacklists.
4. Zero-Contention Pause/Resume: Pauses background Whisper worker completely during LLM inference and TTS playback.
5. Dual-Mode Alexa Flow:
   - Mode A (One-breath command: "Hey Jessica, play IV of Spades on YouTube"): immediate execution.
   - Mode B (Wake-only: "Hey Jessica"): instant (<80ms) attention chime ("Yeah, Boss?") + 6s command window.
"""

import os
import sys
import time
import math
import re
import random
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple, Callable

import numpy as np
import scipy.signal as sps
import sounddevice as sd
import soundfile as sf

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from senses.ear_engine import (
    find_active_microphone_device,
    list_audio_input_devices,
    get_whisper_model,
    WHISPER_VOCAB_PROMPT
)
from senses.voice_engine import VOICE_ENGINE

VOICES_DIR = WORKSPACE_ROOT / "senses" / "voices"
ATTENTION_DIR = VOICES_DIR / "cache" / "attention"
ATTENTION_DIR.mkdir(parents=True, exist_ok=True)

# Comprehensive Wake Word regex patterns (ordered by priority)
WAKE_PATTERNS = [
    # Arrival cues
    r'\b(?:jessica\s+)?daddy\'s\s+home\b',
    # Full multi-word phrases
    r'\b(?:hey|hi|yo|okay|ok|wake\s+up|listen|are\s+you\s+there)\s+(?:jessica|jess|jesika|jessa)\b',
    # Standalone name
    r'\b(?:jessica|jess|jesika|jessa)\b'
]
COMBINED_WAKE_REGEX = re.compile("|".join(WAKE_PATTERNS), re.IGNORECASE)

# Common Whisper hallucinations triggered by low-level room noise
HALLUCINATION_REGEXES = [
    re.compile(r'^\s*(?:thank\s+you|thanks\s+for\s+watching)[.!\s]*$', re.IGNORECASE),
    re.compile(r'^\s*(?:subtitles?\s+by|amara\.org|transcript\s+by)[^a-z0-9]*$', re.IGNORECASE),
    re.compile(r'^\s*(?:you|the|bye|hello|yeah|yes|no)[.!\s]*$', re.IGNORECASE)
]


class WakeWordDaemon:
    """
    Hands-Free Autonomous Wake-Word Background Listener.
    Continuously monitors the active microphone for Jessica's name,
    executing commands or opening interactive listening windows with zero keyboard interaction.
    """
    def __init__(self):
        self.enabled = False
        self.is_listening = False
        self.is_paused = False
        self.pause_reason: Optional[str] = None

        self.active_mic_index: Optional[int] = None
        self.active_mic_name: str = "Unassigned"
        self.native_samplerate: int = 44100
        self.input_channels: int = 1

        self.stream: Optional[sd.InputStream] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.buffer_lock = threading.Lock()

        # Audio Buffering & VAD
        self.target_sr = 16000
        self.pre_buffer_duration = 0.45  # 450ms pre-speech buffer to retain initial syllables ("Hey", "Jess")
        self.pre_buffer_size = int(self.target_sr * self.pre_buffer_duration)
        self.pre_buffer = np.zeros(self.pre_buffer_size, dtype=np.float32)

        self.active_speech_frames: List[np.ndarray] = []
        self.ambient_rms = 0.002
        self.rms_alpha = 0.05
        self.silence_threshold = 0.0050
        self.speech_active = False
        self.speech_start_time = 0.0
        self.last_speech_time = 0.0

        # Mode B Active Command Capture State (10.0s Multi-Turn Window)
        self.in_command_window = False
        self.command_window_start = 0.0
        self.command_window_expires_at = 0.0
        self.command_window_timeout = 10.0
        self.command_audio_frames: List[np.ndarray] = []
        self._has_speech_in_window = False
        self.mute_until = 0.0
        self._last_wake_time = 0.0
        self._last_telemetry_time = 0.0
        self._simulate_audio_feed = False

        # Telemetry & Stats
        self.triggers_count = 0
        self.last_trigger_time: Optional[str] = None
        self.last_mode: Optional[str] = None
        self.last_detected_phrase: Optional[str] = None
        self.last_dispatched_command: Optional[str] = None

        # Pre-cached attention sounds
        self._attention_sounds: Dict[str, Any] = {}
        self._init_attention_chimes()

        # Command Dispatcher Hook
        self.command_callback: Optional[Callable[[str], None]] = None

    def _init_attention_chimes(self):
        """
        Pre-synthesizes and loads instant zero-latency attention chimes
        into sound memory (<10ms playback start).
        """
        chimes = {
            "yeah_boss": "Yeah, Boss?",
            "im_here": "I'm here, Boss, what's up?",
            "listening": "Listening, Boss!"
        }
        for key, phrase in chimes.items():
            wav_path = ATTENTION_DIR / f"{key}.wav"
            if not wav_path.exists():
                try:
                    VOICE_ENGINE.synthesize(phrase, emotion="warm", play_audio=False)
                    cache_files = sorted(list((VOICES_DIR / "cache").glob("jessica_speech_*.wav")), key=lambda p: p.stat().st_mtime)
                    if cache_files:
                        import shutil
                        shutil.copyfile(str(cache_files[-1]), str(wav_path))
                except Exception as e:
                    print(f"[!] Warning caching attention chime {key}: {e}")

            if wav_path.exists():
                self._attention_sounds[key] = str(wav_path)

    def _play_instant_attention_chime(self) -> float:
        """
        Instantly plays a pre-cached warm attention phrase (<80ms latency).
        Returns the duration of the audio in seconds.
        """
        if not self._attention_sounds:
            return 0.8
        chosen_key = random.choice(list(self._attention_sounds.keys()))
        wav_file = self._attention_sounds[chosen_key]
        try:
            info = sf.info(wav_file)
            dur = float(info.duration)
        except Exception:
            dur = 0.8
        t_now = time.time()
        print(f"[{time.strftime('%H:%M:%S')}][T+0.00s] Attention Chime '{chosen_key}' starting playback ({dur:.2f}s duration)...")
        VOICE_ENGINE._play_file_async(wav_file)
        return dur

    def open_followup_window(self, duration_sec: float = 10.0, wait_for_speech: bool = True):
        """
        Opens a multi-turn active listening window where subsequent user speech
        is accepted and dispatched WITHOUT requiring the user to say 'Jessica' again!
        Waits strictly until speech playback finishes + tiny 0.08s tail, then opens immediately.
        """
        def _activator():
            if wait_for_speech:
                # Wait for playback thread to start
                time.sleep(0.04)
                # Wait strictly while audio hardware is busy
                while VOICE_ENGINE.is_speaking(cooldown_sec=0.08):
                    time.sleep(0.02)

            now = time.time()
            elapsed_since_wake = round(now - self._last_wake_time, 3) if self._last_wake_time > 0 else 0.0
            with self.buffer_lock:
                self.is_paused = False
                self.pause_reason = None
                self.in_command_window = True
                self.command_window_start = now
                self.command_window_expires_at = now + duration_sec
                self.command_audio_frames.clear()
                self.last_speech_time = now
                self._has_speech_in_window = False
                self._last_telemetry_time = 0.0
            print(f"[{time.strftime('%H:%M:%S')}][T+{elapsed_since_wake:.2f}s] [WAKE DAEMON] Multi-Turn Active Command Window OPEN ({duration_sec}s). Speech accepted without wake-word (Zero-Blindspot).")

        threading.Thread(target=_activator, daemon=True, name="JessicaFollowupWindow").start()

    def select_microphone(self, device_index: Optional[int] = None) -> Tuple[int, str]:
        """
        Selects and validates the active microphone device.
        """
        if device_index is None:
            dev_idx, dev_name = find_active_microphone_device()
        else:
            dev_idx = device_index
            try:
                info = sd.query_devices(dev_idx)
                dev_name = info.get("name", f"Microphone {dev_idx}")
            except Exception:
                dev_idx, dev_name = find_active_microphone_device()

        info = sd.query_devices(dev_idx)
        native_sr = int(info.get("default_samplerate", 44100))
        ch = int(min(2, info.get("max_input_channels", 1)))

        with self._lock:
            self.active_mic_index = dev_idx
            self.active_mic_name = dev_name
            self.native_samplerate = native_sr
            self.input_channels = ch

        print(f"[+] WakeWordDaemon: Selected mic #{dev_idx} '{dev_name}' ({native_sr}Hz, {ch}ch).")
        return dev_idx, dev_name

    def pause(self, reason: str = "inference_or_speech"):
        """
        Pauses Open-Mic processing completely to eliminate CPU/driver contention
        while Jessica is thinking or speaking.
        """
        with self.buffer_lock:
            self.is_paused = True
            self.pause_reason = reason
            self._clear_buffers(clear_command_window=False)

    def resume(self, cooldown_sec: float = 0.6):
        """
        Resumes Open-Mic listening after a brief cooldown window.
        """
        def _delayed_resume():
            time.sleep(max(0.1, cooldown_sec))
            with self.buffer_lock:
                self.is_paused = False
                self.pause_reason = None
                self._clear_buffers(clear_command_window=False)

        threading.Thread(target=_delayed_resume, daemon=True, name="JessicaWakeResume").start()

    def _clear_buffers(self, clear_command_window: bool = False):
        self.active_speech_frames.clear()
        self.speech_active = False
        self.pre_buffer.fill(0)
        if clear_command_window:
            self.in_command_window = False
            self.command_audio_frames.clear()
            self._has_speech_in_window = False

    def start(self, command_callback: Optional[Callable[[str], None]] = None):
        """
        Starts the always-on background listener stream.
        """
        with self._lock:
            if self.enabled and self._thread is not None and self._thread.is_alive():
                return
            if command_callback:
                self.command_callback = command_callback

            if self.active_mic_index is None:
                self.select_microphone()

            self.enabled = True
            self.is_listening = True
            self.is_paused = False
            self._stop_event.clear()

            self._thread = threading.Thread(target=self._run_listener, daemon=True, name="JessicaWakeDaemon")
            self._thread.start()
            print(f"[+] WakeWordDaemon: Open-Mic Wake Word listening active on '{self.active_mic_name}'.")

    def stop(self):
        """
        Stops the wake word background stream.
        """
        with self._lock:
            self.enabled = False
            self.is_listening = False
            self._stop_event.set()

        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        print("[*] WakeWordDaemon: Open-Mic listener stopped.")

    def match_wake_phrase(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Tests if text contains any recognized wake phrase.
        Returns: (matched, matched_wake_phrase, remainder_command)
        """
        text_clean = text.strip()
        m = COMBINED_WAKE_REGEX.search(text_clean)
        if not m:
            return False, None, None

        wake_phrase = m.group(0)
        remainder = text_clean[m.end():].strip().lstrip(" ,.?!:;-")
        return True, wake_phrase, remainder

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Real-time audio callback delivering native chunks.
        """
        if not self.enabled or self.is_paused:
            return

        now = time.time()

        # 1. Echo suppression check: pause strictly while hardware audio is playing (+ tiny 0.08s tail)
        if VOICE_ENGINE.is_speaking(cooldown_sec=0.08):
            return

        # Check explicit mute_until if set
        if now < self.mute_until:
            return

        # 2. Convert to mono float32
        if indata.ndim > 1 and indata.shape[1] > 1:
            ch0 = indata[:, 0]
            ch1 = indata[:, 1]
            mono = ch1.astype(np.float32) if np.mean(ch1**2) > np.mean(ch0**2) * 1.3 else indata.mean(axis=1).astype(np.float32)
        else:
            mono = indata.flatten().astype(np.float32)

        # 3. Polyphase FIR Resample to 16,000 Hz float32
        if self.native_samplerate != self.target_sr:
            gcd = math.gcd(self.target_sr, self.native_samplerate)
            up = self.target_sr // gcd
            down = self.native_samplerate // gcd
            resampled = sps.resample_poly(mono, up, down).astype(np.float32)
        else:
            resampled = mono

        # 4. Energy calculation & VAD
        chunk_rms = float(np.sqrt(np.mean(resampled**2)))

        # Bug B Fix: ONLY update ambient RMS during true background silence (neither speaker nor user speaking)
        time_since_speech_end = now - VOICE_ENGINE.last_playback_end
        if time_since_speech_end > 0.25 and not VOICE_ENGINE.is_speaking(cooldown_sec=0.25):
            if not self.in_command_window and not self.speech_active:
                self.ambient_rms = (1.0 - self.rms_alpha) * self.ambient_rms + self.rms_alpha * chunk_rms
            elif self.in_command_window and not self._has_speech_in_window and chunk_rms <= self.silence_threshold:
                self.ambient_rms = (1.0 - self.rms_alpha) * self.ambient_rms + self.rms_alpha * chunk_rms

        with self.buffer_lock:
            if self.in_command_window:
                # Mode B active follow-up: conversational threshold (65% of standard silence, 1.2x ambient)
                conv_threshold = max(self.silence_threshold * 0.65, self.ambient_rms * 1.2)
                is_conv_speech = chunk_rms > conv_threshold

                # Live RMS vs VAD telemetry every 200ms
                if (now - self._last_telemetry_time) >= 0.20:
                    self._last_telemetry_time = now
                    t_rel = round(now - self.command_window_start, 2)
                    print(f"  [T+{t_rel:.2f}s] [Mode B Telemetry] RMS: {chunk_rms:.4f} | Thresh: {conv_threshold:.4f} | Amb: {self.ambient_rms:.4f} | SpeechActive: {is_conv_speech} (has_speech: {self._has_speech_in_window}) | Frames: {len(self.command_audio_frames)}")

                if is_conv_speech:
                    if not self._has_speech_in_window:
                        self._has_speech_in_window = True
                        # Include pre-buffer so the opening syllable is never clipped
                        self.command_audio_frames.append(self.pre_buffer.copy())
                    self.last_speech_time = now
                    self.command_audio_frames.append(resampled)
                elif self._has_speech_in_window:
                    # User briefly paused between words; keep frame
                    self.command_audio_frames.append(resampled)
                else:
                    # User hasn't spoken yet in this window: roll the pre-buffer
                    shift_len = len(resampled)
                    if shift_len < self.pre_buffer_size:
                        self.pre_buffer[:-shift_len] = self.pre_buffer[shift_len:]
                        self.pre_buffer[-shift_len:] = resampled
                    else:
                        self.pre_buffer[:] = resampled[-self.pre_buffer_size:]
                return

            # Normal Mode:
            current_threshold = max(self.silence_threshold, self.ambient_rms * 1.6)
            is_speech = chunk_rms > current_threshold
            if is_speech:
                if not self.speech_active:
                    self.speech_active = True
                    self.speech_start_time = now
                self.last_speech_time = now
                self.active_speech_frames.append(resampled)
            else:
                if self.speech_active:
                    # User briefly paused between words; keep frame to prevent word drop
                    self.active_speech_frames.append(resampled)
                else:
                    # Rolling pre-speech buffer
                    shift_len = len(resampled)
                    if shift_len < self.pre_buffer_size:
                        self.pre_buffer[:-shift_len] = self.pre_buffer[shift_len:]
                        self.pre_buffer[-shift_len:] = resampled
                    else:
                        self.pre_buffer[:] = resampled[-self.pre_buffer_size:]

    def _run_listener(self):
        """
        Main worker thread managing audio stream and complete-sentence VAD Whisper processing.
        """
        block_frames = int(self.native_samplerate * 0.1)  # 100ms blocks

        if not getattr(self, "_simulate_audio_feed", False):
            try:
                self.stream = sd.InputStream(
                    samplerate=self.native_samplerate,
                    channels=self.input_channels,
                    device=self.active_mic_index,
                    blocksize=block_frames,
                    dtype="float32",
                    callback=self._audio_callback
                )
                self.stream.start()
            except Exception as e:
                print(f"[!] WakeWordDaemon stream error on device #{self.active_mic_index}: {e}")
                self.enabled = False
                self.is_listening = False
                return
        else:
            print("[+] WakeWordDaemon running in simulated audio feed mode (virtual stream).")

        whisper = get_whisper_model(model_size="small.en", device="cpu")

        while not self._stop_event.is_set():
            time.sleep(0.12)
            if self.is_paused:
                continue

            now = time.time()

            # ---------------------------------------------------------
            # CASE 1: Mode B Active Command Window (10.0s Window)
            # ---------------------------------------------------------
            if self.in_command_window:
                if now > self.command_window_expires_at:
                    # Timeout reached
                    with self.buffer_lock:
                        frames_to_process = list(self.command_audio_frames)
                        had_speech = self._has_speech_in_window
                        self.in_command_window = False
                        self.command_audio_frames.clear()
                        self._has_speech_in_window = False

                    if had_speech and frames_to_process:
                        cmd_audio = np.concatenate(frames_to_process)
                        if len(cmd_audio) > int(self.target_sr * 0.25):
                            self._process_mode_b_command(cmd_audio, whisper)
                    else:
                        print("[*] [WAKE DAEMON] Mode B: 10s Window timed out with no speech.")
                    continue

                if self._has_speech_in_window:
                    silence_gap = now - self.last_speech_time
                    # If user spoke and paused for >=0.85s (natural sentence boundary), process follow-up command
                    if silence_gap >= 0.85:
                        with self.buffer_lock:
                            frames_to_process = list(self.command_audio_frames)
                            self.in_command_window = False
                            self.command_audio_frames.clear()
                            self._has_speech_in_window = False

                        if frames_to_process:
                            cmd_audio = np.concatenate(frames_to_process)
                            if len(cmd_audio) > int(self.target_sr * 0.25):
                                self._process_mode_b_command(cmd_audio, whisper)
                            else:
                                print(f"[*] [WAKE DAEMON] Mode B: Speech too brief ({len(cmd_audio)} samples < {int(self.target_sr * 0.25)}), window closed.")
                        else:
                            print("[*] [WAKE DAEMON] Mode B: Speech buffer was empty, window closed.")
                continue

            # ---------------------------------------------------------
            # CASE 2: Complete-Sentence Natural Pause Detection (1.1s)
            # ---------------------------------------------------------
            if not self.speech_active:
                continue

            time_since_speech = now - self.last_speech_time
            speech_duration = now - self.speech_start_time

            # Trigger only when user paused for >= 1.1s (complete sentence boundary) or hit 7.0s max
            if (time_since_speech >= 1.1 and speech_duration >= 0.5) or (speech_duration >= 7.0):
                with self.buffer_lock:
                    pre_snap = self.pre_buffer.copy()
                    speech_snap = list(self.active_speech_frames)
                    self._clear_buffers(clear_command_window=False)

                if not speech_snap:
                    continue

                full_audio = np.concatenate([pre_snap] + speech_snap)

                # Peak AGC normalization to 0.85 (-1.4 dBFS)
                peak = np.max(np.abs(full_audio))
                if peak > 0.007:
                    gain = min(0.85 / peak, 8.0)
                    full_audio_norm = np.clip(full_audio * gain, -0.92, 0.92)

                    # Robust Whisper transcription
                    try:
                        segments, info = whisper.transcribe(
                            full_audio_norm,
                            initial_prompt=WHISPER_VOCAB_PROMPT,
                            language="en",
                            vad_filter=True,
                            beam_size=5,
                            condition_on_previous_text=False
                        )

                        # Filter out noise chunks with high no_speech_prob
                        valid_segments = [s for s in segments if getattr(s, "no_speech_prob", 0.0) < 0.55]
                        transcribed_text = " ".join([s.text.strip() for s in valid_segments]).strip()

                        # Check hallucination blacklist
                        is_hallucination = any(rgx.search(transcribed_text) for rgx in HALLUCINATION_REGEXES)

                        if transcribed_text and not is_hallucination and len(transcribed_text) > 2:
                            matched, wake_phrase, remainder = self.match_wake_phrase(transcribed_text)
                            if matched:
                                self._handle_wake_detection(wake_phrase, remainder)
                    except Exception as e:
                        print(f"[!] Open-Mic transcription error: {e}")

    def _handle_wake_detection(self, wake_phrase: str, remainder: Optional[str]):
        """
        Dispatches Mode A (One-breath command) vs Mode B (Wake-only attention chime).
        """
        self.triggers_count += 1
        self.last_trigger_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.last_detected_phrase = wake_phrase

        remainder_clean = remainder.strip().lstrip(" ,.?!:;-") if remainder else ""
        is_mode_a = len(remainder_clean) > 3 and not re.match(r'^(?:uh|um|huh|hey|hi)$', remainder_clean, re.IGNORECASE)

        if is_mode_a:
            # MODE A: One-breath command ("Hey Jessica, play IV of Spades on YouTube")
            self.last_mode = "MODE_A"
            self.last_dispatched_command = remainder_clean
            print(f"[+] [WAKE DAEMON] >>> Mode A Triggered! Wake: '{wake_phrase}' | Command: '{remainder_clean}'")
            self.pause("mode_a_dispatch")
            self._dispatch_command(remainder_clean)
        else:
            # MODE B: Name-only wake call ("Hey Jessica!")
            self.last_mode = "MODE_B"
            t_wake = time.time()
            self._last_wake_time = t_wake
            print(f"[{time.strftime('%H:%M:%S')}][T+0.00s] Wake word detected: '{wake_phrase}' -> Playing Attention Chime...")
            dur = self._play_instant_attention_chime()
            self.open_followup_window(duration_sec=10.0, wait_for_speech=True)

    def _process_mode_b_command(self, cmd_audio: np.ndarray, whisper):
        """
        Transcribes and dispatches the follow-up command captured in Mode B window.
        """
        t0 = time.time()
        peak = float(np.max(np.abs(cmd_audio))) if len(cmd_audio) > 0 else 0.0
        audio_dur_sec = round(len(cmd_audio) / self.target_sr, 2)
        print(f"[+] [WAKE DAEMON] Mode B: Processing {audio_dur_sec}s speech audio (Peak={peak:.4f})...")

        if peak < 0.005 or len(cmd_audio) < int(self.target_sr * 0.25):
            print(f"[*] [WAKE DAEMON] Mode B: Audio too quiet or brief (peak={peak:.4f}, dur={audio_dur_sec}s). Discarding.")
            return

        gain = min(0.85 / max(peak, 1e-4), 10.0)
        cmd_audio_norm = np.clip(cmd_audio * gain, -0.92, 0.92)

        try:
            # Transcribe WITHOUT Silero VAD dropping short speech like 'How are you?' or 'Mundo'
            segments, info = whisper.transcribe(
                cmd_audio_norm,
                initial_prompt=WHISPER_VOCAB_PROMPT,
                language="en",
                vad_filter=False,
                beam_size=5,
                condition_on_previous_text=False
            )
            raw_segments = list(segments)
            raw_text = " ".join([s.text.strip() for s in raw_segments]).strip()
            probs = [round(getattr(s, "no_speech_prob", 0.0), 3) for s in raw_segments]
            print(f"[+] [WAKE DAEMON] Mode B Raw Whisper Transcript: '{raw_text}' | no_speech_probs={probs} | Duration: {audio_dur_sec}s")

            # Filter only if no_speech_prob is extraordinarily high (>0.85)
            valid_segments = [s for s in raw_segments if getattr(s, "no_speech_prob", 0.0) < 0.85]
            command_text = " ".join([s.text.strip() for s in valid_segments]).strip()
            if not command_text and raw_text:
                command_text = raw_text

            is_hallucination = any(rgx.search(command_text) for rgx in HALLUCINATION_REGEXES)

            if command_text and not is_hallucination and len(command_text) > 2:
                # Strip repeated wake phrase if user said it again, but if not, keep full command
                matched, _, clean_cmd = self.match_wake_phrase(command_text)
                final_command = clean_cmd if (matched and clean_cmd and len(clean_cmd) > 2) else command_text
                final_command = final_command.strip().lstrip(" ,.?!:;-")

                self.last_dispatched_command = final_command
                latency_ms = round((time.time() - t0) * 1000, 1)
                print(f"[+] [WAKE DAEMON] Mode B Follow-Up Command Dispatched: '{final_command}' (Transcription Latency: {latency_ms}ms)")
                self.pause("mode_b_dispatch")
                self._dispatch_command(final_command)
        except Exception as e:
            print(f"[!] Error transcribing Mode B follow-up: {e}")

    def _dispatch_command(self, command_text: str):
        """
        Dispatches recognized voice command to server API or callback.
        """
        if self.command_callback:
            try:
                self.command_callback(command_text)
            except Exception as e:
                print(f"[!] Command callback execution error: {e}")
        else:
            import urllib.request
            import json
            try:
                req = urllib.request.Request(
                    "http://127.0.0.1:8000/api/command",
                    data=json.dumps({"command": command_text}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(req, timeout=12.0)
            except Exception as e:
                print(f"[!] Failed HTTP dispatch to /api/command: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Returns real-time operational status for Mission Control HUD.
        """
        return {
            "enabled": self.enabled,
            "is_listening": self.is_listening and not self.is_paused,
            "is_paused": self.is_paused,
            "pause_reason": self.pause_reason,
            "active_microphone": self.active_mic_name,
            "active_mic_index": self.active_mic_index,
            "native_samplerate": self.native_samplerate,
            "sample_rate_resampled": self.target_sr,
            "triggers_count": self.triggers_count,
            "last_trigger_time": self.last_trigger_time,
            "last_mode": self.last_mode,
            "last_detected_phrase": self.last_detected_phrase,
            "last_dispatched_command": self.last_dispatched_command,
            "echo_suppression_active": VOICE_ENGINE.is_speaking(cooldown_sec=0.6)
        }


# Singleton Daemon instance
WAKE_DAEMON = WakeWordDaemon()
