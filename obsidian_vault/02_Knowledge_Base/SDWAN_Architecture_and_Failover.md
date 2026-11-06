---
title: Software-Defined WAN (SD-WAN) & Dynamic Path Steering
category: Networking & Infrastructure
tags: [networking, sdwan, wan, failover, sla]
created: 2026-11-01
status: ACTIVE
related: "[[FortiGate_NextGen_Firewalls]], [[BGP_Routing_Protocol]], [[MPLS_Architecture_and_Label_Switching]]"
---

# Software-Defined WAN (SD-WAN) & Dynamic Path Steering

**Software-Defined Wide Area Networking (SD-WAN)** decouples network hardware from control mechanisms, dynamically routing application traffic across multiple heterogeneous WAN connections (MPLS, broadband fiber, 5G/LTE, Starlink).

## Performance SLA Metrics
SD-WAN probes evaluate each WAN underlay using continuous health checks (ping, HTTP probes, TWAMP):
- **Jitter:** Packet arrival variance in milliseconds. Essential for VoIP and video conferencing ($< 15	ext{ms}$).
- **Latency (RTT):** Round-trip transit delay ($< 100	ext{ms}$).
- **Packet Loss:** Percentage of dropped packets ($< 0.5\%$).

## Dynamic Traffic Steering Strategies
1. **Best Quality:** Traffic automatically steers to the underlay link possessing the lowest latency or jitter at that exact second.
2. **Lowest Cost (SLA-Compliant):** Traffic favors lower-cost commercial broadband as long as it satisfies the configured SLA threshold; switches to expensive MPLS only when broadband degrades.
3. **Load Balancing / Spillover:** Traffic distributes across multiple active links based on round-robin, bandwidth ratio, or session volume.

See also: [[FortiGate_NextGen_Firewalls]], [[BGP_Routing_Protocol]], [[Tailscale_and_WireGuard_Mesh_VPN]].
