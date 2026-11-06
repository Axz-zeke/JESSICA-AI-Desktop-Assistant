---
title: RTX 4060 Telemetry Rules & Tensor Core Limits
date: 2026-10-31
tags: [hardware, gpu, rtx4060, vram, thermals, tensorcores]
related: ["[[SOP_Hardware_Overheat_Protocol]]", "[[SOP_Daily_System_Audits]]"]
---

# RTX 4060 Telemetry Rules & Tensor Core Limits

Jessica's neural backbone relies exclusively on the **NVIDIA GeForce RTX 4060 (8GB GDDR6 VRAM)**, utilizing Ada Lovelace (Compute Capability 8.9) 4th Generation Tensor Cores.

### Critical Operating Thresholds
- **Maximum VRAM**: 8,188 MiB (8.00 GB).
- **VRAM High-Water Mark**: 7,200 MiB (88% allocation). If VRAM exceeds this mark, non-essential caches must be evicted.
- **Nominal Temperature**: 40°C – 65°C under sustained FP16 matrix operations.
- **Thermal Warning**: 75°C. Trigger fan acceleration and log warning.
- **Thermal Critical (TJunction)**: 85°C. Immediate model throttling via [[SOP_Hardware_Overheat_Protocol]].

### Tensor Core Compute Benchmarks
- Benchmark throughput for FP16 4096x4096 GEMM operations should achieve **~30.00 TFLOPS**.
- Latency per 4096 matmul: ~4.5ms on Ada Lovelace Tensor Cores.

Refer to [[SOP_Hardware_Overheat_Protocol]] for automatic emergency response procedures.

