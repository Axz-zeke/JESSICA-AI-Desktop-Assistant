---
title: Windows Server Administration, Hyper-V & PowerShell DSC
category: Networking & Infrastructure
tags: [windows, sysadmin, powershell, hyper-v, dsc]
created: 2026-11-01
status: ACTIVE
related: "[[Active_Directory_Domain_Services]], [[Windows_Administration]], [[Linux_CLI_and_System_Administration]]"
---

# Windows Server Administration, Hyper-V & PowerShell DSC

Enterprise Windows Server administration encompasses roles, services, enterprise storage, virtualization via Hyper-V, and declarative configuration management using PowerShell Desired State Configuration (DSC).

## Core Management Subsystems
- **Server Core:** Headless installation minimizing attack surface and memory overhead. Managed via PowerShell Remoting (`Enter-PSSession`, WinRM port 5985/5986).
- **Hyper-V Virtualization:** Type-1 bare-metal hypervisor. Supports dynamic memory allocation, vSwitch teaming, live migration, and nested virtualization.
- **Storage Spaces Direct (S2D):** Software-defined storage clustering pooling local NVMe/SATA drives into high-availability CSVs (Cluster Shared Volumes).

## PowerShell Automation & System Diagnostics
- `Get-WinEvent`: High-speed binary querying of Windows Event Logs (System, Security, Application).
- `Get-CimInstance`: Modern WMI interface replacing legacy `Get-WmiObject`.

See also: [[Windows_Administration]], [[Active_Directory_Domain_Services]], [[Linux_CLI_and_System_Administration]].
