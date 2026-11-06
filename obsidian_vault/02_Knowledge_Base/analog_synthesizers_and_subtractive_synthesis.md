# Analog Synthesizers & Subtractive Sound Synthesis

## Subtractive Synthesis Signal Path
1. **Oscillator (VCO)**: Generates harmonically rich raw audio waveforms:
   - **Sawtooth**: Rich in all integer harmonics (ideal for strings, brass, aggressive leads).
   - **Square / Pulse**: Odd harmonics only (ideal for hollow reed tones, woodwinds, classic 80s basslines).
   - **Triangle**: Low harmonic amplitude, close to pure fundamental tone.
2. **Filter (VCF)**: Subtractive sculpting core. Low-Pass Filter (LPF) cuts high frequencies above the cutoff point. **Resonance** boosts frequencies right at the cutoff threshold into self-oscillation.
3. **Amplifier (VCA)**: Shapes output volume over time governed by envelope generators.

## ADSR Envelope Architecture
- **Attack**: Time taken to rise from silence to peak amplitude.
- **Decay**: Time taken to drop from peak to the sustain level.
- **Sustain**: Steady amplitude level held while the key is pressed.
- **Release**: Time taken to fade back to silence after key is released.
