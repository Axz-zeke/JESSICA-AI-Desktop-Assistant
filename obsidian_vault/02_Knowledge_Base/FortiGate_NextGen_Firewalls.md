---
title: FortiGate Next-Generation Firewall Security Architecture
category: Networking & Infrastructure
tags: [security, firewall, fortigate, utm, ips]
created: 2026-11-01
status: ACTIVE
related: "[[Zero_Trust_Network_Architecture]], [[SDWAN_Architecture_and_Failover]], [[VLAN_Segmentation_and_Trunking]]"
---

# FortiGate Next-Generation Firewall Security Architecture

**Fortinet FortiGate** firewalls deliver ASIC-accelerated Layer 3 through Layer 7 stateful security, unified threat management (UTM), and zero-trust network access (ZTNA).

## Processing Architecture & Acceleration
- **SPU (Security Processing Unit):** Proprietary ASICs offload intensive cryptographic and packet filtering workloads:
  - **NP (Network Processor):** Offloads IPv4/IPv6 Layer 3 routing, NAT, IPsec encryption/decryption, and link aggregation at wire speed.
  - **CP (Content Processor):** Accelerates pattern matching for IPS, AntiVirus deep scanning, and TLS/SSL cryptographic inspection.

## Security Inspection Modes
1. **Flow-Based Inspection:** Scans packets on the fly without buffering the complete payload. Low latency, optimal throughput.
2. **Proxy-Based Inspection:** Buffers complete payload (e.g. files in HTTP/FTP/SMTP) before executing deep anti-malware and DLP scanning. Highest security fidelity with slight latency trade-off.

## Central Policy & ZTNA Concepts
- **Explicit Policies:** Inbound traffic is dropped by default unless matched against an active policy evaluating Source Interface, Destination Interface, Source User/IP, Destination IP, Service/Port, and Security Profiles (AV, IPS, Web Filter, Application Control).
- **SSL/TLS Deep Inspection:** Terminates TLS client handshake, decrypts traffic for malware inspection, and re-encrypts using a local CA certificate.

See also: [[Zero_Trust_Network_Architecture]], [[SDWAN_Architecture_and_Failover]], [[Tailscale_and_WireGuard_Mesh_VPN]].
