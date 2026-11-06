---
title: SOP: FortiGate Firewall Policy & Security Profile Audit
category: Skills & Standard Operating Procedures
tags: [sop, security, firewall, fortigate, audit]
created: 2026-11-01
status: ACTIVE
related: "[[FortiGate_NextGen_Firewalls]], [[Zero_Trust_Network_Architecture]], [[SOP_Daily_System_Audits]]"
---

# Standard Operating Procedure: FortiGate Firewall Policy & Security Profile Audit

## Objective
To regularly verify that firewall rules adhere to least-privilege principles, unneeded legacy ports are closed, and threat inspection profiles are operating effectively.

## Step-by-Step Execution
1. **Review Inactive Policies:** Query FortiOS CLI for zero-hitcount policies:
   ```bash
   diagnose firewall iprope show 0 0
   ```
2. **Inspect SSL/TLS Inspection Certificates:** Ensure intermediate CA certificates have not expired and deep inspection is active on high-risk outbound interfaces.
3. **Verify UTM Profile Bindings:** Every public-facing policy must bind:
   - Antivirus (Flow or Proxy)
   - IPS (Client-side / Server-side signatures)
   - Web Filtering (Block Botnets, Malware, and Newly Registered Domains)
4. **Log Forwarding Verification:** Confirm Syslog/FortiAnalyzer connectivity is active.

See also: [[FortiGate_NextGen_Firewalls]], [[Zero_Trust_Network_Architecture]], [[SOP_Daily_System_Audits]].
