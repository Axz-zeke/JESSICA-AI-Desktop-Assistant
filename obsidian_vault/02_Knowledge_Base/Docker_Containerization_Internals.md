---
title: Docker Containerization, Namespaces & Cgroups
category: Full-Stack & Systems Engineering
tags: [docker, containers, devops, namespaces, cgroups]
created: 2026-11-01
status: ACTIVE
related: "[[Linux_CLI_and_System_Administration]], [[Microservices_vs_Modular_Monolith]], [[FastAPI_High_Performance_Design]]"
---

# Docker Containerization, Namespaces & Cgroups

Containers are not lightweight virtual machines; they are standard Linux processes running directly on the host kernel, isolated by Linux kernel features.

## The Dual Pillars of Container Isolation
1. **Linux Namespaces (What a process can SEE):**
   - **pid:** Process ID isolation (container process is PID 1 inside, but PID 28412 on host).
   - **net:** Isolated network stacks, IP addresses, and routing tables.
   - **mnt:** Independent filesystem mount points.
   - **ipc:** Inter-process communication isolation.
   - **uts:** Isolated hostname and domain name.
2. **Control Groups / Cgroups (What a process can USE):**
   - Restricts CPU quotas, physical memory limits, I/O bandwidth, and maximum process counts.

## Layered Filesystem & Overlay2
Docker images are stacks of read-only tar archives managed by the `overlay2` storage driver, creating a copy-on-write (CoW) container layer at runtime.

See also: [[Linux_CLI_and_System_Administration]], [[Microservices_vs_Modular_Monolith]], [[FastAPI_High_Performance_Design]].
