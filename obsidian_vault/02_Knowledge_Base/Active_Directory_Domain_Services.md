---
title: Active Directory Domain Services (AD DS) & Kerberos
category: Networking & Infrastructure
tags: [windows, sysadmin, active-directory, kerberos, gpo]
created: 2026-11-01
status: ACTIVE
related: "[[Windows_Server_Administration_Mastery]], [[DNS_Architecture_and_Troubleshooting]], [[Zero_Trust_Network_Architecture]]"
---

# Active Directory Domain Services (AD DS) & Kerberos

**Active Directory Domain Services (AD DS)** is Microsoft’s directory service providing centralized identity management, resource authorization, and policy enforcement across enterprise Windows environments.

## Hierarchical Structure
- **Objects & Organizational Units (OUs):** Logical containers holding users, security groups, and computer accounts.
- **Domains & Trees:** Logical grouping of resources sharing a common directory database.
- **Forests:** The top-most security boundary sharing a global catalog, schema, and directory partition.

## Kerberos v5 Authentication Protocol
Active Directory relies on Kerberos ticket-based authentication over UDP/TCP port 88:
1. **AS-REQ / AS-REP:** Client sends timestamp encrypted with user password hash to the Authentication Service (AS) and receives a Ticket Granting Ticket (TGT).
2. **TGS-REQ / TGS-REP:** Client presents TGT to the Ticket Granting Service (TGS) requesting access to a specific service principal (SPN), receiving a Service Ticket.
3. **AP-REQ / AP-REP:** Client presents Service Ticket directly to the target application server.

See also: [[Windows_Server_Administration_Mastery]], [[DNS_Architecture_and_Troubleshooting]], [[Zero_Trust_Network_Architecture]].
