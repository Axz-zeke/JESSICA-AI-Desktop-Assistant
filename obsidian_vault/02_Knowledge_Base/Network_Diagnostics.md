---
title: Network Diagnostics & Connectivity Standards
date: 2026-10-31
tags: [networking, diagnostics, dns, latency, internet]
related: ["[[SOP_Network_Outage_Triage]]", "[[Windows_Administration]]"]
---

# Network Diagnostics & Connectivity Standards

Maintaining continuous verification of the host machine's uplink is critical for Jessica. Because Jessica's cognitive engine runs 100% locally on the RTX 4060, network access is primarily monitored to verify external synchronization and health metrics.

### Dual-Target Ping Triage
- **Primary DNS Probe**: `1.1.1.1` (Cloudflare Anycast DNS, Port 53 TCP/UDP). Average target latency is under 20ms.
- **Secondary DNS Probe**: `8.8.8.8` (Google Public DNS, Port 53 TCP/UDP). Target latency is under 25ms.
- **Default Gateway**: Verified by querying the host route table via `route print 0.0.0.0` or adapter discovery.

### Triage Matrix
| State | Gateway Status | Ping 1.1.1.1 | Action Directive |
| :--- | :--- | :--- | :--- |
| **Nominal** | Reachable (<2ms) | Reachable (<30ms) | No intervention required. |
| **WAN Outage** | Reachable (<2ms) | Unreachable (Timeout) | Trigger [[SOP_Network_Outage_Triage]]. |
| **NIC Down** | Unreachable | Unreachable | Inspect adapter power states in [[Windows_Administration]]. |

Refer to [[SOP_Network_Outage_Triage]] for remediation steps.

