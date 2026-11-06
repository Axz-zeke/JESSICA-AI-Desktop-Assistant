"""
Jessica Senses - Master Voice Analyzer
Processes senses/voices/jessica-voice.mp3, converts to clean 24kHz mono reference WAV,
and extracts fundamental frequency (F0 pitch), spectral centroid (warmth/brightness),
and cadence metrics into senses/voices/jessica_voice_profile.json.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
VOICES_DIR = WORKSPACE_ROOT / "senses" / "voices"
MP3_SOURCE = VOICES_DIR / "jessica-voice.mp3"
WAV_REF = VOICES_DIR / "jessica_reference.wav"
PROFILE_OUT = VOICES_DIR / "jessica_voice_profile.json"


def analyze_voice():
    print("=" * 65)
    print("        JESSICA ACOUSTIC & VOCAL PROFILER")
    print("=" * 65)

    if not MP3_SOURCE.exists():
        raise FileNotFoundError(f"Source voice file not found at {MP3_SOURCE}")

    print(f"[*] Loading master reference voice: {MP3_SOURCE}")
    
    import librosa
    import soundfile as sf

    # Load and resample to 24,000 Hz mono (ideal for neural TTS / vocoder)
    sr_target = 24000
    y, sr = librosa.load(str(MP3_SOURCE), sr=sr_target, mono=True)
    duration_sec = float(len(y) / sr)

    print(f"[+] Loaded {duration_sec:.2f}s audio at {sr} Hz mono.")

    # Save clean reference WAV
    sf.write(str(WAV_REF), y, sr_target)
    print(f"[+] Saved clean reference WAV: {WAV_REF.name}")

    # Generate multi-emotion slices for conditioning
    # Split into 3 segments: early (warm), mid (playful), late (calm)
    seg_len = len(y) // 3
    if seg_len > sr_target * 2:
        sf.write(str(VOICES_DIR / "jessica_slice_warm.wav"), y[:seg_len], sr_target)
        sf.write(str(VOICES_DIR / "jessica_slice_playful.wav"), y[seg_len:2*seg_len], sr_target)
        sf.write(str(VOICES_DIR / "jessica_slice_calm.wav"), y[2*seg_len:], sr_target)
        print("[+] Generated multi-emotion reference conditioning slices.")

    # Extract Fundamental Frequency (F0 Pitch)
    print("[*] Tracking fundamental frequency (F0) contour via PyIN...")
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('C3'),
        fmax=librosa.note_to_hz('C6'),
        sr=sr_target
    )

    # Filter voiced frames
    f0_voiced = f0[voiced_flag & ~np.isnan(f0)] if voiced_flag is not None else np.array([])
    if len(f0_voiced) == 0:
        f0_voiced = np.array([215.0])  # fallback female nominal pitch

    f0_mean = float(np.mean(f0_voiced))
    f0_std = float(np.std(f0_voiced))
    f0_min = float(np.min(f0_voiced))
    f0_max = float(np.max(f0_voiced))

    # Extract Spectral Centroid (Warmth vs Brightness)
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr_target)[0]
    spec_cent_mean = float(np.mean(spec_cent))
    spec_cent_std = float(np.std(spec_cent))

    # Spectral Rolloff & Bandwidth
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr_target)[0]
    spec_bw_mean = float(np.mean(spec_bw))

    # Energy / RMS
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))

    # Tempo / Cadence (Beats/Onsets per minute)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr_target)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr_target)
    tempo_bpm = float(tempo[0] if isinstance(tempo, (list, np.ndarray)) else tempo)

    # Determine warmth profile rating
    if spec_cent_mean < 2500:
        warmth_desc = "Rich, Warm, Intimate Contours"
    elif spec_cent_mean < 3500:
        warmth_desc = "Warm, Playful, Bright Human Voice"
    else:
        warmth_desc = "Crisp, High-Presence, Articulate"

    profile_data = {
        "source_file": "jessica-voice.mp3",
        "reference_wav": "jessica_reference.wav",
        "duration_seconds": round(duration_sec, 2),
        "sample_rate_hz": sr_target,
        "pitch_f0": {
            "mean_hz": round(f0_mean, 2),
            "std_hz": round(f0_std, 2),
            "min_hz": round(f0_min, 2),
            "max_hz": round(f0_max, 2),
            "voice_range": "Soprano / Bright Alto" if f0_mean > 200 else "Mezzo-Soprano"
        },
        "timbre_acoustics": {
            "spectral_centroid_mean_hz": round(spec_cent_mean, 2),
            "spectral_centroid_std_hz": round(spec_cent_std, 2),
            "spectral_bandwidth_mean_hz": round(spec_bw_mean, 2),
            "warmth_profile": warmth_desc,
            "rms_energy_mean": round(rms_mean, 4)
        },
        "prosody_cadence": {
            "estimated_tempo_bpm": round(tempo_bpm, 1),
            "speaking_rate_wpm": 165
        },
        "emotion_acoustic_mappings": {
            "warm": {"pitch_shift_semitones": 0.0, "rate_mult": 1.0, "warmth_gain_db": 1.5, "pause_ms": 120},
            "playful": {"pitch_shift_semitones": 1.2, "rate_mult": 1.08, "warmth_gain_db": 0.8, "pause_ms": 90},
            "excited": {"pitch_shift_semitones": 2.0, "rate_mult": 1.15, "warmth_gain_db": 0.5, "pause_ms": 60},
            "calm": {"pitch_shift_semitones": -0.8, "rate_mult": 0.92, "warmth_gain_db": 2.2, "pause_ms": 180},
            "serious": {"pitch_shift_semitones": -1.2, "rate_mult": 0.96, "warmth_gain_db": 1.0, "pause_ms": 140},
            "curious": {"pitch_shift_semitones": 1.5, "rate_mult": 1.04, "warmth_gain_db": 1.2, "pause_ms": 100}
        }
    }

    with open(PROFILE_OUT, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    print(f"[+] Saved vocal profile to: {PROFILE_OUT.name}")
    print("-" * 65)
    print(f"  Duration:            {duration_sec:.2f} seconds")
    print(f"  Sample Rate:         {sr_target} Hz (Mono)")
    print(f"  Mean F0 Pitch:       {f0_mean:.1f} Hz (Std: {f0_std:.1f} Hz)")
    print(f"  Pitch Range:         {f0_min:.1f} Hz - {f0_max:.1f} Hz ({profile_data['pitch_f0']['voice_range']})")
    print(f"  Spectral Centroid:   {spec_cent_mean:.1f} Hz ({warmth_desc})")
    print(f"  Cadence / Tempo:     {tempo_bpm:.1f} BPM (~165 WPM)")
    print("=" * 65)

    return profile_data


if __name__ == "__main__":
    analyze_voice()

