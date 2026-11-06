---
title: VLAN Segmentation, 802.1Q Trunking & Inter-VLAN Routing
category: Networking & Infrastructure
tags: [networking, switching, vlans, trunking, layer2]
created: 2026-11-01
status: ACTIVE
related: "[[IPv4_Subnetting_and_CIDR]], [[FortiGate_NextGen_Firewalls]], [[Zero_Trust_Network_Architecture]]"
---

# VLAN Segmentation, 802.1Q Trunking & Inter-VLAN Routing

A **Virtual Local Area Network (VLAN)** partitions a physical Layer 2 switch into logically isolated broadcast domains. Network segmentation prevents broadcast storms, restricts lateral movement during security breaches, and enforces micro-segmentation.

## 802.1Q Frame Tagging
When an Ethernet frame crosses an inter-switch trunk link, an IEEE 802.1Q 4-byte header is inserted between the Source MAC address and EtherType fields:
- **TPID (Tag Protocol Identifier):** Fixed at `0x8100` to indicate an 802.1Q tagged frame.
- **PCP (Priority Code Point):** 3 bits used for Layer 2 Quality of Service (Class of Service / CoS).
- **DEI (Drop Eligible Indicator):** 1 bit indicating frames eligible to be dropped during congestion.
- **VID (VLAN Identifier):** 12 bits defining the VLAN ID (values 1 to 4094; 0 and 4095 are reserved).

## Access vs Trunk Ports
- **Access Port:** Belongs to a single VLAN. Frames egress untagged toward end-user endpoints (PCs, printers, servers).
- **Trunk Port:** Carries traffic for multiple VLANs simultaneously, preserving 802.1Q tags across switches, firewalls, and hypervisors.
- **Native VLAN:** Frames belonging to the native VLAN traverse the trunk link without an 802.1Q tag (default is VLAN 1; best security practice is changing to an unused VLAN ID).

## Inter-VLAN Routing Architecture
1. **Router-on-a-Stick (RoaS):** A single physical link configured as an 802.1Q trunk carries multiple sub-interfaces with `encapsulation dot1q <vlan_id>`.
2. **Multilayer Switch (SVI):** Switch Virtual Interfaces (`interface Vlan 10`, `interface Vlan 20`) route packets in hardware (ASIC/TCAM) at wire speed.
3. **Next-Gen Firewall Subinterfaces:** Traffic between VLANs is routed through a firewall interface (e.g., FortiGate) to enforce stateful L7 inspection.

See also: [[IPv4_Subnetting_and_CIDR]], [[Zero_Trust_Network_Architecture]], [[FortiGate_NextGen_Firewalls]].
