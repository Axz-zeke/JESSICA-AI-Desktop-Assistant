---
title: Border Gateway Protocol (BGP) Architecture
category: Networking & Infrastructure
tags: [networking, routing, bgp, autonomous-systems]
created: 2026-11-01
status: ACTIVE
related: "[[OSPF_Routing_Protocol]], [[MPLS_Architecture_and_Label_Switching]], [[SDWAN_Architecture_and_Failover]]"
---

# Border Gateway Protocol (BGP) Architecture

The **Border Gateway Protocol (BGP)** is the primary exterior gateway protocol (EGP) powering inter-domain routing across the global Internet and large-scale enterprise WANs. Operating at the application layer over TCP port 179, BGP exchanges reachability information between distinct [[Autonomous_Systems]].

## Core Characteristics & Concepts
- **Path Vector Protocol:** Unlike distance-vector or link-state protocols, BGP advertises the complete path of autonomous system numbers (the `AS_PATH` attribute) required to reach a destination network prefix, inherently preventing routing loops.
- **eBGP vs iBGP:**
  - **External BGP (eBGP):** Exchanged between peers in different autonomous systems (TTL default is 1, requiring direct Layer 3 adjacency unless eBGP multihop is explicitly configured).
  - **Internal BGP (iBGP):** Exchanged between routers within the same autonomous system to distribute exterior routes internally. Requires a full mesh topology or the deployment of Route Reflectors (RRs) / BGP Confederations.
- **TCP Reliability:** BGP relies on TCP port 179 for stateful session establishment, handling acknowledgment, sequencing, and retransmission natively.

## The BGP Decision Process
When multiple paths exist to the same IP prefix, BGP evaluates attributes in strict descending order:
1. **Weight:** Cisco-proprietary, local to the router (highest wins).
2. **Local Preference (`LOCAL_PREF`):** Distributed throughout the local AS (highest wins).
3. **Locally Originated:** Prefer routes originated locally via `network` or `aggregate` statements.
4. **AS Path Length (`AS_PATH`):** Shortest AS sequence wins.
5. **Origin Code:** IGP < EGP < Incomplete (`?`).
6. **Multi-Exit Discriminator (`MED`):** Metric advertised between neighboring ASes (lowest wins).
7. **eBGP over iBGP:** Prefer external paths over internal paths.
8. **IGP Metric to Next Hop:** Lowest interior metric to the advertised BGP `NEXT_HOP`.
9. **Oldest Route:** Prefer the path that has been known longest (reduces route flapping).
10. **Router ID:** Lowest neighboring BGP Router ID (IP address).

## Operational Tuning & Troubleshooting
- **Prefix Filtering:** Use prefix-lists and route-maps to enforce inbound and outbound route policies.
- **Soft Reconfiguration & Route Refresh:** Enables dynamic policy recalculation without tearing down active TCP sessions (`clear ip bgp * soft`).
- **Telemetry Verification:** Use `check_network_status` to ensure TCP port 179 reachability and evaluate local BGP neighbor peering states.

See also: [[OSPF_Routing_Protocol]], [[SDWAN_Architecture_and_Failover]], [[Zero_Trust_Network_Architecture]].
