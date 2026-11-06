# Fiber Optic Transceivers (SFP/QSFP) and OTDR Testing

## Transceiver Form Factors & Wavelengths
- **SFP+ (10 Gbps):** 850nm (10GBASE-SR Multimode, up to 300m OM3/OM4) vs 1310nm (10GBASE-LR Singlemode, up to 10km).
- **SFP28 (25 Gbps):** High-density top-of-rack interconnects.
- **QSFP28 (100 Gbps):** 4x25Gbps optical lanes (e.g. 100GBASE-SR4 MPO or 100GBASE-LR4 LC duplex).

## Optical Time-Domain Reflectometer (OTDR) Diagnostics
An OTDR injects high-speed laser light pulses down an optical fiber and analyzes backscattered Rayleigh reflections and Fresnel reflection peaks:
- Reflection Spikes: Identify physical connector junctions, dirty patch panels, or mechanical splices.
- Attenuation Slope: Measures loss in dB/km (standard singlemode 1310nm loss: ~0.35 dB/km).
- Abrupt Drops: Pinpoint micro-bends, macro-bends, or physical cable breaks.
