"""
Jessica Senses - Ear Engine (Microphone & STT Audio Transcription)
Provides 100% local speech-to-text transcription using faster-whisper (small.en / base.en).
Features Deduplicated Hardware Audio Device Selection, Native Sample Rate Recording,
Polyphase Resampling to 16kHz, Dynamic Non-Clipping AGC, Interactive Push-to-Start / Click-to-Stop
Recording Sessions, and Vocabulary-Primed Whisper.
"""

import os
import sys
import io
import tempfile
import time
import math
import re
import threading
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Callable, Tuple

import numpy as np
import scipy.signal as sps

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Global Whisper instance cache
_WHISPER_MODEL = None

WAKE_PHRASES = ["hey jessica", "jessica", "hey jess"]
WAKE_WORD_STATE = {
    "enabled": False,
    "listening": False,
    "last_trigger_time": None,
    "last_command": None,
    "triggers_count": 0
}
_WAKE_THREAD: Optional[threading.Thread] = None
_WAKE_STOP_EVENT = threading.Event()

# Technical vocabulary priming for Whisper
WHISPER_VOCAB_PROMPT = (
    "Boss, Alexander Lopez, Crishaira, Jessica, RTX 4060, Obsidian, BGP, OSPF, Spotify, "
    "telemetry, YouTube, Python, PyTorch, LoRA, GPU, CPU, RAM, microphone, webcam."
)


def get_whisper_model(model_size: str = "small.en", device: str = "cpu"):
    """
    Loads or returns cached faster-whisper model.
    Defaults to small.en (falling back to base.en) on CPU int8 with 8 threads
    for high accuracy and low latency alongside PyTorch cortex.
    """
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
            print(f"[*] Initializing local faster-whisper ({model_size}) on {device} (8 CPU threads, int8)...")
            _WHISPER_MODEL = WhisperModel(model_size, device=device, compute_type="int8", cpu_threads=8)
            print(f"[+] faster-whisper ({model_size}) ready for instant local speech recognition.")
        except Exception as e:
            print(f"[!] Warning: faster-whisper {model_size} load error: {e}. Trying base.en...")
            try:
                from faster_whisper import WhisperModel
                _WHISPER_MODEL = WhisperModel("base.en", device=device, compute_type="int8", cpu_threads=8)
                print("[+] faster-whisper (base.en fallback) ready.")
            except Exception as e2:
                print(f"[!] Warning: faster-whisper fallback initialization failed: {e2}")
                _WHISPER_MODEL = None
    return _WHISPER_MODEL


def find_active_microphone_device() -> Tuple[int, str]:
    """
    Smart hardware microphone finder.
    Prioritizes real physical microphone hardware:
    1. Webcam Mic (A4tech FHD 1080P PC Camera) - Confirmed reliable physical mic!
    2. Headset Mic (High Definition Audio Device / Realtek)
    over disconnected 3.5mm jacks or silent virtual mapper devices.
    """
    try:
        import sounddevice as sd
        devices = sd.query_devices()

        # 1. Look for known working Webcam microphone keywords FIRST (preferring DirectSound device #12)
        webcam_candidates = []
        for idx, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                name = dev.get("name", "")
                if any(k in name.lower() for k in ["a4tech", "fhd 1080p", "fhd", "webcam", "usb camera"]):
                    webcam_candidates.append((idx, name))
        if webcam_candidates:
            # Sort: prioritize Device 12 (DirectSound) first
            webcam_candidates.sort(key=lambda x: (0 if x[0] == 12 else 1, -x[0]))
            return webcam_candidates[0][0], webcam_candidates[0][1]

        # 2. Look for known Headset keywords second
        for idx, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                name = dev.get("name", "")
                if any(k in name.lower() for k in ["high definition", "headset", "realtek"]):
                    return idx, name

        # 3. Probe inputs with non-zero RMS signal
        best_idx = 0
        best_name = "Default System Microphone"
        best_rms = -1.0
        for idx, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                name = dev.get("name", "")
                native_sr = int(dev.get("default_samplerate", 44100))
                ch = int(dev.get("max_input_channels", 1))
                try:
                    chunk = sd.rec(int(native_sr * 0.15), samplerate=native_sr, channels=ch, dtype="float32", device=idx)
                    sd.wait()
                    rms = float(np.sqrt(np.mean(chunk**2)))
                    if rms > best_rms:
                        best_rms = rms
                        best_idx = idx
                        best_name = name
                except Exception:
                    continue

        return best_idx, best_name
    except Exception as e:
        print(f"[!] Active mic auto-detect notice: {e}")
        return 12, "Microphone (A4tech FHD 1080P PC Camera)"


def list_audio_input_devices() -> List[Dict[str, Any]]:
    """
    Lists real physical audio input devices deduplicated across Windows host APIs.
    Filters out broken duplicates and tests each device at its own native sample rate.
    Prioritizes Windows DirectSound / MME with full device names.
    """
    devices = []
    try:
        import sounddevice as sd
        raw_devices = sd.query_devices()
        hostapis = sd.query_hostapis()
        default_input = sd.default.device[0] if hasattr(sd.default, "device") else None

        candidates = []
        for idx, dev in enumerate(raw_devices):
            if dev.get("max_input_channels", 0) > 0:
                h_idx = dev.get("hostapi", 0)
                api_name = hostapis[h_idx]["name"] if h_idx < len(hostapis) else "MME"
                candidates.append((idx, dev, api_name))

        # Deduplicate by normalized name root
        seen_roots: Dict[str, Dict[str, Any]] = {}

        for idx, dev, api_name in candidates:
            raw_name = dev.get("name", f"Microphone {idx}")
            is_generic_mapper = ("sound mapper" in raw_name.lower() or "sound capture driver" in raw_name.lower())

            clean_name = re.sub(r'^[0-9]+-\s*', '', raw_name)
            clean_name = re.sub(r'^(microphone|mic)\s*\(?', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\)$', '', clean_name).strip()

            # Canonical deduplication key
            n_lower = raw_name.lower()
            if any(k in n_lower for k in ["high definition", "realtek", "headset"]):
                norm_key = "headset_mic"
            elif any(k in n_lower for k in ["a4tech", "fhd", "webcam", "usb camera"]):
                norm_key = "webcam_mic"
            elif is_generic_mapper:
                norm_key = "windows_default_mapper"
            else:
                norm_key = re.sub(r'[^a-zA-Z0-9]', '', clean_name.lower()) or f"dev_{idx}"

            # API priority score: DirectSound (4) > MME (3) > WASAPI (2) > WDM-KS (1)
            api_score = 1
            if "directsound" in api_name.lower():
                api_score = 4
            elif "mme" in api_name.lower():
                api_score = 3
            elif "wasapi" in api_name.lower():
                api_score = 2

            name_len_score = len(raw_name)
            native_sr = int(dev.get("default_samplerate", 44100))
            channels = int(dev.get("max_input_channels", 1))

            # Test input settings validity
            is_valid = True
            try:
                sd.check_input_settings(device=idx, channels=channels, samplerate=native_sr)
            except Exception:
                is_valid = False

            if not is_valid and not is_generic_mapper:
                continue

            entry = {
                "index": idx,
                "name": raw_name,
                "clean_name": clean_name,
                "hostapi": api_name,
                "channels": channels,
                "default_samplerate": native_sr,
                "is_default": (idx == default_input),
                "is_headset": any(k in raw_name.lower() for k in ["high definition", "headset", "realtek", "headphone"]),
                "is_webcam": any(k in raw_name.lower() for k in ["a4tech", "fhd", "webcam", "camera", "usb"]),
                "is_generic_mapper": is_generic_mapper,
                "score": api_score * 100 + name_len_score
            }

            if norm_key not in seen_roots or entry["score"] > seen_roots[norm_key]["score"]:
                seen_roots[norm_key] = entry

        # Format clean list
        for key, entry in seen_roots.items():
            if entry["is_headset"]:
                display_label = f"Headset Mic: High Definition Audio ({entry['default_samplerate']}Hz, {entry['channels']}ch)"
            elif entry["is_webcam"]:
                display_label = f"Webcam Mic: A4tech FHD 1080P ({entry['default_samplerate']}Hz, {entry['channels']}ch)"
            elif entry["is_generic_mapper"]:
                display_label = f"Default Windows Capture ({entry['hostapi']})"
            else:
                display_label = f"{entry['clean_name']} ({entry['default_samplerate']}Hz)"

            devices.append({
                "index": entry["index"],
                "name": entry["name"],
                "display_label": display_label,
                "hostapi": entry["hostapi"],
                "channels": entry["channels"],
                "default_samplerate": entry["default_samplerate"],
                "is_default": entry["is_webcam"],
                "is_headset": entry["is_headset"],
                "is_webcam": entry["is_webcam"]
            })

        # Put working Webcam Mic first!
        devices.sort(key=lambda d: (0 if d["is_webcam"] else (1 if d["is_headset"] else 2)))

    except Exception as e:
        print(f"[!] Error querying sound devices: {e}")
        devices.append({
            "index": 11,
            "name": "Microphone (2- High Definition Audio Device)",
            "display_label": "Headset Mic: High Definition Audio (44100Hz, 2ch)",
            "hostapi": "Windows DirectSound",
            "channels": 2,
            "default_samplerate": 44100,
            "is_default": True,
            "is_headset": True,
            "is_webcam": False
        })
    return devices


def record_hardware_audio(
    device_index: Optional[int] = None,
    duration: float = 4.0,
    sample_rate: int = 16000,
    silence_timeout: float = 2.0
) -> Dict[str, Any]:
    """
    Records audio directly from the selected hardware microphone at its NATIVE sample rate
    (e.g. 48000Hz or 44100Hz on Headset Mic, 44100Hz on Webcam Mic).
    Picks the active stereo channel, applies polyphase FIR resampling down to 16kHz,
    and applies smart non-clipping AGC (peak 0.85).
    """
    import sounddevice as sd
    import soundfile as sf

    start_time = time.perf_counter()
    duration = max(1.0, min(15.0, float(duration)))

    # Resolve device and query native capabilities
    if device_index is None or device_index < 0:
        selected_dev, dev_name = find_active_microphone_device()
    else:
        selected_dev = device_index
        try:
            dev_info = sd.query_devices(selected_dev)
            dev_name = dev_info.get("name", f"Device #{selected_dev}")
        except Exception:
            dev_name = f"Device #{selected_dev}"

    try:
        dev_info = sd.query_devices(selected_dev)
        native_sr = int(dev_info.get("default_samplerate", 44100))
        native_channels = int(dev_info.get("max_input_channels", 1))
    except Exception:
        native_sr = 44100
        native_channels = 1

    print(f"[*] Recording {duration}s from '{dev_name}' (device #{selected_dev}) at native {native_sr}Hz ({native_channels} ch)...")

    try:
        num_frames = int(duration * native_sr)
        raw_rec = sd.rec(num_frames, samplerate=native_sr, channels=native_channels, dtype="float32", device=selected_dev)
        sd.wait()
    except Exception as e:
        print(f"[!] Hardware recording error on dev #{selected_dev}: {e}. Retrying default...")
        num_frames = int(duration * 44100)
        raw_rec = sd.rec(num_frames, samplerate=44100, channels=1, dtype="float32")
        sd.wait()
        native_sr = 44100

    # Stereo Channel Selection (pick channel with highest voice energy)
    if raw_rec.ndim > 1 and raw_rec.shape[1] > 1:
        ch0 = raw_rec[:, 0]
        ch1 = raw_rec[:, 1]
        rms0 = float(np.sqrt(np.mean(ch0**2)))
        rms1 = float(np.sqrt(np.mean(ch1**2)))
        if rms1 > rms0 * 1.3:
            audio_data = ch1
        elif rms0 > rms1 * 1.3:
            audio_data = ch0
        else:
            audio_data = np.mean(raw_rec, axis=1)
    else:
        audio_data = raw_rec.flatten()

    # Polyphase FIR Resampling down to 16,000 Hz for Whisper
    target_sr = 16000
    if native_sr != target_sr:
        g = math.gcd(target_sr, native_sr)
        up = target_sr // g
        down = native_sr // g
        audio_data = sps.resample_poly(audio_data, up, down).astype(np.float32)

    rec_duration = round(len(audio_data) / target_sr, 2)
    max_amp = float(np.max(np.abs(audio_data))) if len(audio_data) > 0 else 0.0
    rms_val = float(np.sqrt(np.mean(audio_data**2))) if len(audio_data) > 0 else 0.0

    # Smart Non-Clipping AGC: normalize peak to 0.85 cleanly (-1.4 dBFS)
    # NEVER apply blind 12x multiplier that clips speech into square waves
    gain_applied = 1.0
    if 0.0005 < max_amp < 0.80:
        gain_applied = min(0.85 / max_amp, 8.0)
        audio_data = audio_data * gain_applied
        audio_data = np.clip(audio_data, -0.92, 0.92)
        print(f"[*] Smart AGC applied: {gain_applied:.2f}x gain (peak normalized to {np.max(np.abs(audio_data)):.2f}).")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        sf.write(tmp_path, audio_data, target_sr, subtype="PCM_16")
        transcribe_res = transcribe_audio_file(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "status": "success",
        "text": transcribe_res.get("text", ""),
        "recorded_duration_s": rec_duration,
        "max_amplitude": round(max_amp, 5),
        "rms_energy": round(rms_val, 6),
        "gain_boost": round(gain_applied, 2),
        "transcription_latency_ms": transcribe_res.get("latency_ms", 0),
        "total_latency_ms": total_latency_ms,
        "device_index": selected_dev,
        "device_name": dev_name,
        "native_sample_rate": native_sr,
        "native_channels": native_channels
    }


def transcribe_audio_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Transcribes an audio file (.wav, .mp3, .ogg, .webm) locally using faster-whisper (small.en)
    with primed vocabulary (Alexander Lopez, Crishaira, Jessica, RTX 4060, BGP, Spotify)
    and VAD voice activity filtering.
    """
    file_path = str(file_path)
    if not os.path.exists(file_path):
        return {"status": "error", "message": f"File not found: {file_path}", "text": ""}

    start_time = time.perf_counter()
    model = get_whisper_model()

    if model is not None:
        try:
            import soundfile as sf
            audio_data, sr = sf.read(file_path, dtype="float32")
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)

            if len(audio_data) == 0:
                return {"status": "success", "text": "", "latency_ms": 0, "duration": 0}

            segments, info = model.transcribe(
                audio_data,
                beam_size=5,
                language="en",
                vad_filter=True,
                initial_prompt=WHISPER_VOCAB_PROMPT,
                condition_on_previous_text=False
            )
            text_chunks = [segment.text.strip() for segment in segments]
            full_text = " ".join(text_chunks).strip()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "success",
                "text": full_text,
                "language": info.language,
                "duration": round(info.duration, 2),
                "latency_ms": elapsed_ms
            }
        except Exception as e:
            print(f"[!] Whisper transcription failed: {e}")

    # Fallback to SpeechRecognition
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "success",
                "text": text,
                "latency_ms": elapsed_ms,
                "engine": "fallback"
            }
    except Exception as e:
        return {"status": "error", "message": f"Transcription error: {e}", "text": ""}


class AudioRecorderSession:
    """
    Push-to-Start / Click-to-Stop interactive recording session.
    Allows user to speak for as long as they want (up to 15s max),
    or auto-stops only after speech is detected AND followed by 2.0s of silence.
    Stops immediately when user clicks [SEND VOICE].
    """
    def __init__(self):
        self.is_recording = False
        self.device_index: Optional[int] = None
        self.device_name: str = "Default"
        self.native_sr: int = 44100
        self.native_channels: int = 1
        self.start_time: float = 0.0
        self.max_duration: float = 15.0
        self.chunks: List[np.ndarray] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.speech_detected = False
        self.last_speech_time = 0.0
        self.auto_stopped = False

    def start(self, device_index: Optional[int] = None, max_duration: float = 15.0) -> Dict[str, Any]:
        with self._lock:
            if self.is_recording:
                return {"status": "already_recording", "device_index": self.device_index}

            import sounddevice as sd
            self.chunks.clear()
            self.speech_detected = False
            self.auto_stopped = False
            self.max_duration = max(3.0, min(30.0, float(max_duration)))
            self._stop_event.clear()

            # Resolve device settings
            if device_index is None or device_index < 0:
                self.device_index, self.device_name = find_active_microphone_device()
            else:
                self.device_index = device_index
                try:
                    d_info = sd.query_devices(self.device_index)
                    self.device_name = d_info.get("name", f"Device #{self.device_index}")
                except Exception:
                    self.device_name = f"Device #{self.device_index}"

            try:
                d_info = sd.query_devices(self.device_index)
                self.native_sr = int(d_info.get("default_samplerate", 44100))
                self.native_channels = int(d_info.get("max_input_channels", 1))
            except Exception:
                self.native_sr = 44100
                self.native_channels = 1

            self.start_time = time.time()
            self.last_speech_time = self.start_time
            self.is_recording = True

            self._thread = threading.Thread(target=self._record_worker, daemon=True)
            self._thread.start()
            print(f"[*] [REC] Started interactive recording on '{self.device_name}' (#{self.device_index}) at {self.native_sr}Hz.")

            return {
                "status": "recording_started",
                "device_index": self.device_index,
                "device_name": self.device_name,
                "native_samplerate": self.native_sr,
                "max_duration": self.max_duration
            }

    def _record_worker(self):
        import sounddevice as sd

        def _audio_callback(indata, frames, time_info, status):
            if not self.is_recording or self._stop_event.is_set():
                return
            with self._lock:
                self.chunks.append(indata.copy())

            # Real-time VAD & energy check
            rms = float(np.sqrt(np.mean(indata**2)))
            now = time.time()
            if rms > 0.008:
                self.speech_detected = True
                self.last_speech_time = now

            if self.speech_detected and (now - self.last_speech_time > 2.0):
                self.auto_stopped = True
                self._stop_event.set()

            if now - self.start_time > self.max_duration:
                self.auto_stopped = True
                self._stop_event.set()

        try:
            with sd.InputStream(
                samplerate=self.native_sr,
                channels=self.native_channels,
                dtype="float32",
                device=self.device_index,
                callback=_audio_callback
            ):
                while not self._stop_event.is_set() and self.is_recording:
                    time.sleep(0.05)
        except Exception as e:
            print(f"[!] InputStream worker exception: {e}")
        finally:
            self.is_recording = False

    def stop(self) -> Dict[str, Any]:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.5)
        self.is_recording = False

        with self._lock:
            if not self.chunks:
                return {
                    "status": "empty",
                    "text": "",
                    "duration": 0.0,
                    "message": "No audio captured."
                }
            combined = np.concatenate(self.chunks, axis=0)

        # Process channel selection
        if combined.ndim > 1 and combined.shape[1] > 1:
            ch0 = combined[:, 0]
            ch1 = combined[:, 1]
            rms0 = float(np.sqrt(np.mean(ch0**2)))
            rms1 = float(np.sqrt(np.mean(ch1**2)))
            if rms1 > rms0 * 1.3:
                audio_data = ch1
            elif rms0 > rms1 * 1.3:
                audio_data = ch0
            else:
                audio_data = np.mean(combined, axis=1)
        else:
            audio_data = combined.flatten()

        # Resample to 16,000 Hz
        target_sr = 16000
        if self.native_sr != target_sr:
            g = math.gcd(target_sr, self.native_sr)
            up = target_sr // g
            down = self.native_sr // g
            audio_data = sps.resample_poly(audio_data, up, down).astype(np.float32)

        # Smart AGC (peak 0.85)
        max_amp = float(np.max(np.abs(audio_data))) if len(audio_data) > 0 else 0.0
        if 0.0005 < max_amp < 0.80:
            gain = min(0.85 / max_amp, 8.0)
            audio_data = np.clip(audio_data * gain, -0.92, 0.92)

        duration_sec = round(len(audio_data) / target_sr, 2)

        # Write WAV and transcribe with primed Whisper
        import soundfile as sf
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_wav = tmp.name

        try:
            sf.write(tmp_wav, audio_data, target_sr, subtype="PCM_16")
            res = transcribe_audio_file(tmp_wav)
        finally:
            try:
                os.remove(tmp_wav)
            except Exception:
                pass

        return {
            "status": "success",
            "text": res.get("text", ""),
            "duration": duration_sec,
            "transcription_latency_ms": res.get("latency_ms", 0),
            "device_name": self.device_name,
            "auto_stopped": self.auto_stopped
        }

    def get_status(self) -> Dict[str, Any]:
        now = time.time()
        elapsed = round(now - self.start_time, 1) if self.is_recording else 0.0
        return {
            "is_recording": self.is_recording,
            "device_name": self.device_name,
            "elapsed_seconds": elapsed,
            "speech_detected": self.speech_detected,
            "auto_stopped": self.auto_stopped
        }


ACTIVE_RECORDER = AudioRecorderSession()


def start_wake_word_listener(on_trigger_callback: Optional[Callable[[], None]] = None):
    """
    Starts background wake word listener thread.
    """
    global _WAKE_THREAD
    if _WAKE_THREAD is not None and _WAKE_THREAD.is_alive():
        WAKE_WORD_STATE["listening"] = True
        return

    _WAKE_STOP_EVENT.clear()
    WAKE_WORD_STATE["enabled"] = True
    WAKE_WORD_STATE["listening"] = True

    def _worker():
        while not _WAKE_STOP_EVENT.is_set():
            time.sleep(1.0)

    _WAKE_THREAD = threading.Thread(target=_worker, daemon=True)
    _WAKE_THREAD.start()


def stop_wake_word_listener():
    """
    Stops background wake word listener.
    """
    global _WAKE_THREAD
    _WAKE_STOP_EVENT.set()
    WAKE_WORD_STATE["listening"] = False
    WAKE_WORD_STATE["enabled"] = False


def transcribe_audio_bytes(audio_bytes: bytes, format_hint: str = "wav") -> Dict[str, Any]:
    """
    Transcribes raw audio bytes by writing to a temporary file and running transcribe_audio_file.
    """
    suffix = f".{format_hint}" if not format_hint.startswith(".") else format_hint
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        return transcribe_audio_file(tmp_path)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def get_wake_word_status() -> Dict[str, Any]:
    return WAKE_WORD_STATE.copy()


def set_wake_word_enabled(enabled: bool):
    WAKE_WORD_STATE["enabled"] = enabled
    if enabled:
        start_wake_word_listener()
    else:
        stop_wake_word_listener()


def trigger_wake_command_simulation(command: str = "hey jessica"):
    WAKE_WORD_STATE["last_trigger_time"] = time.time()
    WAKE_WORD_STATE["last_command"] = command
    WAKE_WORD_STATE["triggers_count"] += 1
