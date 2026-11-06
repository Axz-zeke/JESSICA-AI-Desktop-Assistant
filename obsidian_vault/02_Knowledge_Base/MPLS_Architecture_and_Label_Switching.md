---
title: Multi-Protocol Label Switching (MPLS) Fundamentals
category: Networking & Infrastructure
tags: [networking, mpls, carrier, vrf, l3vpn]
created: 2026-11-01
status: ACTIVE
related: "[[BGP_Routing_Protocol]], [[SDWAN_Architecture_and_Failover]], [[OSPF_Routing_Protocol]]"
---

# Multi-Protocol Label Switching (MPLS) Fundamentals

**Multi-Protocol Label Switching (MPLS)** is a high-performance telecommunications technique that routes data packets using short path labels rather than complex IP routing table lookups at each intermediate hop.

## Label Architecture & Shim Header
The 32-bit MPLS label (shim header) sits between Layer 2 and Layer 3:
- **Label Value (20 bits):** The actual lookup key (values 0-15 are reserved).
- **Traffic Class / EXP (3 bits):** Quality of Service (QoS) and DiffServ mapping.
- **Bottom of Stack (S-bit, 1 bit):** Set to 1 if this is the innermost label in a label stack.
- **TTL (Time to Live, 8 bits):** Decremented at each hop to prevent loops.

## Router Roles in an MPLS Network
- **Label Edge Router (LER / Ingress/Egress PE):** Pushes the initial label onto incoming native IP packets or pops the label before delivering to the customer.
- **Label Switch Router (LSR / Provider P):** Swaps incoming labels with outgoing labels based on its Label Forwarding Information Base (LFIB).
- **Penultimate Hop Popping (PHP):** The second-to-last router pops the outer label so the egress LER only performs a single Layer 3 IP lookup.

See also: [[BGP_Routing_Protocol]], [[SDWAN_Architecture_and_Failover]], [[OSPF_Routing_Protocol]].
