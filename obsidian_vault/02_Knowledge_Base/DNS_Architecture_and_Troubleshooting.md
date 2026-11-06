---
title: Domain Name System (DNS) Architecture & Resolution Pipeline
category: Networking & Infrastructure
tags: [networking, dns, troubleshooting, active-directory]
created: 2026-11-01
status: ACTIVE
related: "[[DHCP_Operation_and_Relay_Agents]], [[Active_Directory_Domain_Services]], [[TCP_IP_Protocol_Suite_Deep_Dive]]"
---

# Domain Name System (DNS) Architecture & Resolution Pipeline

The **Domain Name System (DNS)** is the hierarchical, distributed naming system that translates human-friendly domain names (e.g., `github.com`) into numerical IP addresses (`140.82.112.4`).

## Resolution Hierarchy & Step-by-Step Pipeline
1. **Local Resolver Cache:** Client checks `hosts` file and local operating system DNS cache (`ipconfig /displaydns`).
2. **Recursive Resolver:** Query sent to ISP or configured resolver (`1.1.1.1`, `8.8.8.8`, or corporate DNS).
3. **Root Nameserver (`.`):** Directs the recursive resolver to the Top-Level Domain (TLD) server.
4. **TLD Nameserver (`.com`, `.net`, `.org`):** Directs resolver to the authoritative nameservers for the second-level domain.
5. **Authoritative Nameserver:** Holds the final zone records and returns the IP address.

## Critical Record Types
- **A & AAAA:** IPv4 (32-bit) and IPv6 (128-bit) host mapping.
- **CNAME:** Canonical name alias pointing one domain to another.
- **MX:** Mail Exchange records prioritized by preference value.
- **TXT:** Free-form text used for domain verification, SPF (`v=spf1 ...`), and DKIM.
- **SRV:** Service locator records critical for Active Directory domain controller discovery (`_ldap._tcp.dc._msdcs.<domain>`).
- **PTR:** Pointer record used for reverse DNS lookups (IP to domain).

See also: [[DHCP_Operation_and_Relay_Agents]], [[Active_Directory_Domain_Services]], [[check_network_status]].
