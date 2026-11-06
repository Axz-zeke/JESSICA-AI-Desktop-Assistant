---
title: Dynamic Host Configuration Protocol (DHCP) & IPAM
category: Networking & Infrastructure
tags: [networking, dhcp, ipam, broadcast, udp]
created: 2026-11-01
status: ACTIVE
related: "[[DNS_Architecture_and_Troubleshooting]], [[VLAN_Segmentation_and_Trunking]], [[IPv4_Subnetting_and_CIDR]]"
---

# Dynamic Host Configuration Protocol (DHCP) & IPAM

**DHCP (Dynamic Host Configuration Protocol)** operates over UDP ports 67 (server) and 68 (client) to dynamically automate IP address assignment, subnet masks, default gateways, and DNS settings.

## The 4-Way DORA Handshake
1. **Discover (Client -> Broadcast):** Client sends `DHCPDISCOVER` to `255.255.255.255`.
2. **Offer (Server -> Unicast/Broadcast):** Server responds with `DHCPOFFER` containing an available IP, lease duration, and options.
3. **Request (Client -> Broadcast):** Client announces acceptance of the specific offer via `DHCPREQUEST`.
4. **Acknowledge (Server -> Client):** Server commits the lease into its database and sends `DHCPACK`.

## DHCP Relay Agents (IP Helper-Address)
Because DHCP Discover messages are Layer 2 broadcasts (`FF:FF:FF:FF:FF:FF`), they cannot traverse standard Layer 3 routers. An **IP Helper-Address** converts incoming Layer 2 broadcast Discover messages into directed Layer 3 unicast packets forwarded to a centralized enterprise DHCP server, inserting the client's ingress gateway address (GIADDR / Option 82).

See also: [[IPv4_Subnetting_and_CIDR]], [[DNS_Architecture_and_Troubleshooting]], [[Active_Directory_Domain_Services]].
