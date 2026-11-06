---
title: IPv4 Subnetting, CIDR & Variable Length Subnet Masking
category: Networking & Infrastructure
tags: [networking, ipv4, subnetting, cidr, vlsm]
created: 2026-11-01
status: ACTIVE
related: "[[VLAN_Segmentation_and_Trunking]], [[OSPF_Routing_Protocol]], [[DNS_Architecture_and_Troubleshooting]]"
---

# IPv4 Subnetting, CIDR & Variable Length Subnet Masking

**IPv4 Subnetting** divides a continuous IPv4 address block into smaller, hierarchically managed logical sub-networks. **Classless Inter-Domain Routing (CIDR)** replaces obsolete Class A, B, and C boundaries with bit-length prefix notation (`/24`, `/28`).

## Binary Arithmetic & Bit Borrowing
An IPv4 address consists of 32 bits grouped into 4 octets. Subnet masks specify the division between network and host bits:
- **Usable Hosts Formula:** $N_{	ext{hosts}} = 2^{(32 - 	ext{prefix})} - 2$ (subtracting 2 for the Network ID and the Directed Broadcast Address).
- **Point-to-Point Links (/30 vs /31):**
  - `/30`: 4 total addresses, 2 usable host IPs (mask `255.255.255.252`).
  - `/31` (RFC 3021): Used on modern point-to-point links with 2 total addresses, both usable as host IPs without broadcast or network reservation.

## Common Subnet Cheat Sheet
- `/24` = `255.255.255.0` -> 254 hosts
- `/25` = `255.255.255.128` -> 126 hosts
- `/26` = `255.255.255.192` -> 62 hosts
- `/27` = `255.255.255.224` -> 30 hosts
- `/28` = `255.255.255.240` -> 14 hosts
- `/29` = `255.255.255.248` -> 6 hosts
- `/30` = `255.255.255.252` -> 2 hosts

## VLSM (Variable Length Subnet Masking)
VLSM allows allocating precisely sized subnets to branches and departments based on host count rather than assigning wastefully large `/24` blocks across WAN links.

See also: [[VLAN_Segmentation_and_Trunking]], [[BGP_Routing_Protocol]], [[DHCP_Operation_and_Relay_Agents]].
