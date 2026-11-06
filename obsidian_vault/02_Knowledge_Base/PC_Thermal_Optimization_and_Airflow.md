---
title: PC Thermal Optimization, Fan Curves & Airflow Dynamics
category: Hardware, Audio & Everyday Companion
tags: [hardware, cooling, thermals, pc-building, fans]
created: 2026-11-01
status: ACTIVE
related: "[[RTX_4060_Ada_Lovelace_Architecture]], [[RTX_4060_Telemetry_Rules]], [[SOP_Hardware_Overheat_Protocol]]"
---

# PC Thermal Optimization, Fan Curves & Airflow Dynamics

Maintaining cool operating temperatures ensures silicon longevity, prevents thermal throttling, and minimizes acoustic fan noise during heavy LLM inference and gaming sessions.

## Pressure Dynamics: Positive vs Negative
- **Positive Pressure (Intake > Exhaust):** More air is drawn into the case through dust filters than exhausted, forcing air out through small chassis cracks and keeping dust out.
- **Negative Pressure (Exhaust > Intake):** Draws ambient dust through unfilted cracks; slightly lower GPU temperatures in some cases at the expense of dust buildup.
- **Ideal Configuration:** 3x 120mm filtered front intake fans, 1x 120mm rear exhaust fan, and 1x top-rear exhaust fan.

## Fan Curve Tuning
- **0 - 45°C (Idle):** 30% fan speed (whisper quiet).
- **45 - 65°C (Inference Load):** 50% fan speed (smooth linear ramp).
- **65 - 75°C (Heavy Workload):** 70% fan speed.
- **75°C+ (Thermal Warning):** 100% fan speed to avert GPU core throttling at 83°C.

See also: [[RTX_4060_Telemetry_Rules]], [[SOP_Hardware_Overheat_Protocol]], [[RTX_4060_Ada_Lovelace_Architecture]].
