---
title: SOP - Hardware Overheat & Thermal Protection Protocol
date: 2026-10-31
tags: [sop, hardware, thermals, gpu, rtx4060]
related: ["[[RTX_4060_Telemetry_Rules]]", "[[SOP_Daily_System_Audits]]"]
---

# SOP - Hardware Overheat & Thermal Protection Protocol

### Purpose
Protects the host Intel Core i5 CPU and NVIDIA GeForce RTX 4060 GPU against thermal degradation.

### Triggers
- **GPU Temp > 75°C**: Advisory Warning.
- **GPU Temp > 82°C**: Critical Threshold.
- **CPU Utilization > 95% sustained for > 60 seconds**.

### Standard Action Sequence
1. Check `get_system_telemetry()` to isolate offending component.
2. If GPU temperature exceeds 80°C:
   - Pause batch inference on `cortex_net.py` or `router_net.py`.
   - Clear PyTorch CUDA memory caches via `torch.cuda.empty_cache()`.
3. If CPU temperature is elevated:
   - Identify rogue background threads via `list_top_processes()`.
   - Alert user with recommendation to terminate top offender via [[SOP_Process_Termination]].
4. Append an incident note to `03_Daily_Logs/` documenting max temperatures observed.
