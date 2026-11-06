---
title: SOP - Daily System Health Audit Procedures
date: 2026-10-31
tags: [sop, telemetry, audit, maintenance]
related: ["[[RTX_4060_Telemetry_Rules]]", "[[Network_Diagnostics]]", "[[Windows_Administration]]"]
---

# SOP - Daily System Health Audit Procedures

### Purpose
Scheduled automated checklist executed at system startup and daily milestones to verify host sovereignty.

### Execution Checklist
1. **Telemetry Snapshot**:
   - Query `get_system_telemetry()`. Verify RAM is under 80% usage and GPU VRAM has at least 3GB free for neural inference.
   - Cross-reference with [[RTX_4060_Telemetry_Rules]].
2. **Network Health Probe**:
   - Query `check_network_status()`. Ensure latency to `1.1.1.1` is under 30ms.
   - Cross-reference with [[Network_Diagnostics]].
3. **Heavy Process Audit**:
   - Execute `list_top_processes(limit=5)`. Ensure no unauthorized miners or runaway CPU threads exist.
4. **Log Retention**:
   - Generate summary markdown and save to `obsidian_vault/03_Daily_Logs/Daily_Audit_<YYYY-MM-DD>.md`.
