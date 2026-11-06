---
title: Process Management & Security Sandboxing
date: 2026-10-31
tags: [security, sandbox, permissions, processes]
related: ["[[SOP_Process_Termination]]", "[[Windows_Administration]]"]
---

# Process Management & Security Sandboxing

To guarantee host safety, Jessica implements a strict 2-tier **Permission Sandbox**:

### Tier 1: `SAFE` Execution (Implicit Authorization)
Read-only queries, diagnostic tools, and non-destructive launches:
- `get_system_telemetry()`
- `list_top_processes()`
- `check_network_status()`
- `open_application()` (for whitelisted apps)
- `write_obsidian_note()` (sandboxed inside `obsidian_vault/`)
- `read_obsidian_vault()`
- `set_system_volume()`
- `take_screenshot()`

### Tier 2: `CONFIRM_REQUIRED` (Human-in-the-Loop Gate)
Destructive, process-terminating, or system-altering commands:
- `kill_process(process_name)`: Requires explicit user approval via UI modal or chat confirmation `[APPROVE]` before execution.

See [[SOP_Process_Termination]] for step-by-step confirmation lifecycle.

