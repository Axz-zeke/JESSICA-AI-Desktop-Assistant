---
title: SOP - Network Outage & WAN Triage Protocol
date: 2026-10-31
tags: [sop, network, diagnostics, triage]
related: ["[[Network_Diagnostics]]", "[[Windows_Administration]]"]
---

# SOP - Network Outage & WAN Triage Protocol

### Purpose
Systematic diagnostics when WAN connectivity drops or socket latencies spike above baseline.

### Diagnosis Steps
1. **Local NIC Verification**:
   - Query `check_network_status()` and examine `active_interfaces`.
   - Verify local IPv4 address is assigned and not in the `169.254.x.x` APIPA range.
2. **Gateway Ping**:
   - Probe the default gateway identified in [[Network_Diagnostics]].
   - If gateway drops packets: Flag physical Ethernet cable or local Wi-Fi router failure.
3. **External DNS Resolution**:
   - Probe `1.1.1.1` and `8.8.8.8`.
   - If ping succeeds to IP but fails to domain names: Identify local DNS cache corruption (`ipconfig /flushdns`).
4. **Log State**:
   - Record outage duration and network adapter status in `obsidian_vault/03_Daily_Logs/`.
