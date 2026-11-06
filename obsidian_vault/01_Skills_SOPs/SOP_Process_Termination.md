---
title: SOP - Process Termination Protocol (CONFIRM_REQUIRED)
date: 2026-10-31
tags: [sop, security, processes, confirmation, kill_process]
related: ["[[Process_Management_Security]]", "[[Windows_Administration]]"]
---

# SOP - Process Termination Protocol

### Purpose
Regulates the execution of `kill_process` to prevent unintended service termination or system instability.

### Prerequisites
1. Intent router flags command as `kill_process`.
2. Target process name or PID is extracted via [[Process_Management_Security]].

### Execution Procedure
1. **Safety Check**: Check whether the target process is a critical system service (`csrss.exe`, `lsass.exe`, `services.exe`, `explorer.exe`). If yes, reject immediately.
2. **User Confirmation Prompt**:
   - Issue prompt: `"Terminating process <TARGET> requires confirmation. Proceed? [APPROVE] / [DENY]"`.
3. **Execution on Approval**:
   - Call `action_api.kill_process(target)`.
   - Log execution result in `03_Daily_Logs/` with timestamp.
4. **Cancellation on Denial**:
   - Discard action payload and report abort status to user.
