# PC Gaming Frame-Pacing and RTX 4060 DLSS 3 Tuning

## Frame Pacing vs Raw FPS
Smooth visual gameplay requires consistent frame time delivery (e.g. 16.6ms for 60Hz, 6.94ms for 144Hz). A game running at 100 FPS with erratic 30ms frame-time spikes will feel stuttery compared to a flat, locked 80 FPS line.

## NVIDIA DLSS 3 & Frame Generation on RTX 4060
The Ada Lovelace RTX 4060 features Optical Flow Accelerators (OFA) that generate intermediate AI frames:
1. **Super Resolution (DLSS 2):** Renders base game at 1080p and reconstructs to 1440p using temporal AI autoencoders.
2. **Frame Generation (DLSS 3):** Inserts synthesized neural frames between rendered frames, doubling perceived refresh rate without taxing CPU bottlenecks.
3. **NVIDIA Reflex:** Bypasses render queue to slash input latency introduced by frame buffers.
