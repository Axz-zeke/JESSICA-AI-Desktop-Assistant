# Windows 11 Event Viewer Diagnostics & Triage Guide

## Core Operational Logs
1. **System Log**: Hardware errors, driver crashes, power events, and kernel panic warnings (Event ID 41 Kernel-Power indicates unexpected shutdown).
2. **Application Log**: Crash reports for desktop binaries (Event ID 1000 Application Error, Event ID 1001 Windows Error Reporting).
3. **Security Log**: Audit success and failure logs (Event ID 4624 successful logon, Event ID 4625 failed logon attempt).

## Essential Event IDs for IT Triage
- **Event ID 41**: Critical Kernel-Power loss without clean shutdown (check PSU, overclock stability, or sudden AC power loss).
- **Event ID 7036**: Service entered running or stopped state (useful for tracing background daemon crashes).
- **Event ID 10016**: DistributedCOM permission warning (common and generally harmless unless application hangs).
- **Event ID 1000**: Faulting application path and exception code (e.g., `0xc0000005` Access Violation).

## Filtering & CLI Extraction
Query specific errors via PowerShell:
```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddHours(-24)} | Select-Object TimeCreated, Id, Message
```
