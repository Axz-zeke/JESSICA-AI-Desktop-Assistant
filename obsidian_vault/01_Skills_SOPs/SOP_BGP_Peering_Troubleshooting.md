---
title: SOP: BGP Neighbor Down Triage & Route Leak Isolation
category: Skills & Standard Operating Procedures
tags: [sop, networking, bgp, triage, routing]
created: 2026-11-01
status: ACTIVE
related: "[[BGP_Routing_Protocol]], [[SOP_Network_Outage_Triage]], [[check_network_status]]"
---

# Standard Operating Procedure: BGP Neighbor Down Triage & Route Leak Isolation

## Objective
Quickly diagnose, isolate, and restore failed BGP peerings between autonomous systems.

## Diagnostic Workflow
1. **Layer 3 Reachability Check:**
   Ping the remote BGP peer IP address. If ping fails, isolate intermediate Layer 1/2 fiber link or ISP outage.
2. **TCP Port 179 Socket Test:**
   Verify TCP port 179 is open and not blocked by intermediate firewall ACLs:
   ```bash
   telnet <neighbor_ip> 179
   ```
3. **Inspect Neighbor State:**
   ```bash
   show ip bgp summary
   show ip bgp neighbors <neighbor_ip>
   ```
   - `Idle`: Router is resetting connection or local route to peer is missing.
   - `Connect` / `Active`: TCP handshake is attempting to establish or failing due to mismatched AS number, MD5 password, or TTL expiration.
   - `OpenSent` / `OpenConfirm`: Version or parameter mismatch.
   - `Established`: BGP session is healthy and exchanging NLRI prefixes.

See also: [[BGP_Routing_Protocol]], [[SOP_Network_Outage_Triage]], [[check_network_status]].
