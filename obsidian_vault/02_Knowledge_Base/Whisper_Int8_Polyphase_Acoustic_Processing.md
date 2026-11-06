# Whisper Int8 Polyphase Acoustic Processing

## Faster-Whisper CTranslate2 Engine
Faster-Whisper re-implements OpenAI Whisper in C++ using CTranslate2, executing quantized 8-bit integer matrix multiplication on CPU vector registers.
- **Polyphase Resampling:** Converts 44,100 Hz or 48,000 Hz hardware microphone audio directly to 16,000 Hz with anti-aliasing sinc filters.
- **Log-Mel Spectrogram:** Transforms 16 kHz raw audio into 80-channel log-magnitude Mel-frequency representations across 25ms windows with 10ms hop length.
- **Transcription Latency:** Cuts transcription latency from ~2.4s to <400ms on Intel Core i5 CPUs.
