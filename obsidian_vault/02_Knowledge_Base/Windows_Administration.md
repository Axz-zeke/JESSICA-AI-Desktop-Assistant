---
title: Windows Administration & Native Process Architecture
date: 2026-10-31
tags: [windows, administration, processes, win32, sop]
related: ["[[Process_Management_Security]]", "[[SOP_Process_Termination]]", "[[Network_Diagnostics]]"]
---

# Windows Administration & Native Process Architecture

Windows NT architecture isolates user-mode processes from kernel-mode executive services. For **Jessica**, maintaining sovereign control of the OS requires interfacing directly with native Win32 APIs, the Windows Management Instrumentation (WMI) infrastructure, and low-overhead subprocess execution.

### Key Administrative Directives
1. **Process Privilege Levels**:
   - Elevated administrator vs. standard medium integrity user processes.
   - See [[Process_Management_Security]] for authorization boundaries before invoking termination hooks.
2. **Process Execution Pipelines**:
   - Spawning utilities like `notepad.exe`, `calc.exe`, and `taskmgr.exe` via `subprocess.Popen` without invoking shell interpreters prevents command injection attacks.
3. **Core Administration Tools**:
   - `tasklist` / `psutil`: Querying running threads, working sets, and CPU times.
   - `route print`: Mapping default IPv4 gateway routes. See [[Network_Diagnostics]].
   - `netstat -ano`: Auditing open listening ports and TCP socket states.

Refer to [[SOP_Daily_System_Audits]] for the mandatory morning verification checklist.

