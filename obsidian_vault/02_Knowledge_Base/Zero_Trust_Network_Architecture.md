---
title: Zero Trust Network Architecture (ZTNA) & Identity Security
category: Networking & Infrastructure
tags: [security, zerotrust, ztna, microsegmentation, iam]
created: 2026-11-01
status: ACTIVE
related: "[[FortiGate_NextGen_Firewalls]], [[Tailscale_and_WireGuard_Mesh_VPN]], [[Active_Directory_Domain_Services]]"
---

# Zero Trust Network Architecture (ZTNA) & Identity Security

**Zero Trust** is a strategic security framework founded on the core axiom: *"Never trust, always verify."* It abolishes the antiquated perimeter defense ("castle-and-moat") model, assuming breaches are already present within internal networks.

## Fundamental Pillars
1. **Continuous Identity Verification:** Every access request is authenticated, authorized, and encrypted before granting session connectivity.
2. **Least Privilege Enforcement:** Users and service principals receive only the granular permissions strictly required for their immediate function (JIT / Just-In-Time access).
3. **Assume Breach:** Design networks assuming attackers already have code execution inside internal subnets. Minimize blast radius through micro-segmentation.

## Technical Implementation
- **Micro-Segmentation:** Dividing data centers into discrete security segments down to individual workload containers.
- **Context-Aware Access Policies:** Evaluating device posture (OS version, disk encryption, EDR presence), physical location, and user risk scores.
- **ZTNA Application Proxies:** Users access specific internal applications without being placed onto the wider network subnet.

See also: [[FortiGate_NextGen_Firewalls]], [[Tailscale_and_WireGuard_Mesh_VPN]], [[Active_Directory_Domain_Services]].
