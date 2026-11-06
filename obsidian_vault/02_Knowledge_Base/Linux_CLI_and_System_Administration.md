---
title: Linux CLI Mastery, Systemd & Kernel Tuning
category: Networking & Infrastructure
tags: [linux, sysadmin, systemd, bash, performance]
created: 2026-11-01
status: ACTIVE
related: "[[Windows_Server_Administration_Mastery]], [[TCP_IP_Protocol_Suite_Deep_Dive]], [[Docker_Containerization_Internals]]"
---

# Linux CLI Mastery, Systemd & Kernel Tuning

Linux powers cloud infrastructure, supercomputers, and modern AI training nodes. Mastery of Linux administration requires deep knowledge of the systemd init system, storage pipelines, process inspection, and kernel parameters.

## Systemd Architecture & Service Management
- **Units:** Service (`.service`), mount (`.mount`), timer (`.timer`), and socket (`.socket`) definitions.
- **Service Control:** `systemctl enable --now <service>`, `systemctl status <service>`, `journalctl -u <service> -f --no-tail`.
- **Cgroups v2:** Provides unified resource management limiting CPU, memory, and I/O per systemd slice.

## Kernel Performance & sysctl Tuning
- `vm.swappiness`: Controls tendency of the kernel to move processes out of physical RAM to swap disk (set to `10` or lower on AI/database servers).
- `net.core.somaxconn`: Maximum socket listen backlog for high-concurrency web endpoints.
- `fs.file-max`: Upper limit on concurrent open file descriptors.

See also: [[Docker_Containerization_Internals]], [[TCP_IP_Protocol_Suite_Deep_Dive]], [[Python_Asyncio_Internals]].
