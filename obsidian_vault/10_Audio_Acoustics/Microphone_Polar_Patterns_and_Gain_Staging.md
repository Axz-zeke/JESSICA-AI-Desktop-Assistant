# Microphone Polar Patterns and Audio Gain Staging

## 1. Polar Patterns in Acoustic Capture
- **Cardioid / Supercardioid:** Highest sensitivity directly on-axis (0 degrees), with maximum rejection at 180 degrees (rear) or 126 degrees. Ideal for directional vocal capture and suppressing room acoustic reverberations.
- **Omnidirectional:** Captures sound equally from all angles (360 degrees). Less susceptible to proximity effect but prone to room reflections, fan noise, and acoustic feedback loops.
- **Figure-8 (Bidirectional):** Equal sensitivity at front and rear, with near-total null points at 90 and 270 degrees. Common in ribbon microphones and Blumlein stereo pairs.

## 2. Gain Staging & Dynamic Headroom
- Maintain an input RMS level between -18 dBFS and -12 dBFS on 24-bit converters to prevent digital clipping (0 dBFS inter-sample peaks).
- Avoid blind software multiplier boosts (e.g. 12x linear digital gain), which amplify the analog pre-amp noise floor and cause square-wave harmonic clipping.
- Use polyphase FIR decimation when downsampling from 44.1 kHz / 48 kHz to 16 kHz to eliminate Nyquist aliasing.

## 3. Acoustic Echo Suppression
- Digital signal processing (DSP) echo suppression calculates reference playback correlation:
  $$E_{corr} = \frac{\sum (x[n] \cdot y[n])}{\sqrt{\sum x^2[n] \cdot \sum y^2[n]}}$$
- A physical hardware mute or audio callback gate during active TTS playback guarantees zero acoustic re-triggering.

Related: [[Audio_DSP_Spectral_Analysis]] | [[Digital_Signal_Processing_Principles]]

