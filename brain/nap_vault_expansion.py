"""
Jessica Second Brain - Nap-Cycle 64-Note Vault Expansion
Generates 64 deeply detailed technical, architectural, and lifestyle notes
expanding Boss's Obsidian knowledge vault from 86 to 150 documents.
"""

import os
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
VAULT_KB = WORKSPACE_ROOT / "obsidian_vault" / "02_Knowledge_Base"
VAULT_SOPS = WORKSPACE_ROOT / "obsidian_vault" / "01_Skills_SOPs"

VAULT_KB.mkdir(parents=True, exist_ok=True)
VAULT_SOPS.mkdir(parents=True, exist_ok=True)

NOTES_DATA = [
    # -------------------------------------------------------------
    # Category 1: Enterprise Network & Infrastructure Administration (20 Notes)
    # -------------------------------------------------------------
    (
        VAULT_KB / "FortiGate_Firewall_Policies_and_FortiOS_CLI.md",
        """# FortiGate Firewall Policies and FortiOS CLI Troubleshooting

## Overview & Policy Architecture
FortiOS operates on an explicit stateful policy table where traffic flow matches top-down first-match semantics. 
Each policy binds incoming interface, outgoing interface, source/destination address objects, schedules, services, and UTM security profiles (Antivirus, Web Filter, IPS, Application Control, SSL/SSH Inspection).

```text
Incoming Interface [port1] -> Policy Match Check (Top-Down) -> NAT SNAT/DNAT -> UTM Flow/Proxy Inspection -> Routing Engine -> Outgoing Interface [port2]
```

## Essential FortiOS CLI Commands
```bash
# Live packet sniffing with verbose packet headers
diagnose sniffer packet any "host 192.168.1.50 and port 443" 4 0 l

# Flow tracing for policy matching and NAT debugging
diagnose debug reset
diagnose debug flow filter addr 192.168.1.50
diagnose debug flow filter proto 6
diagnose debug flow show function-name enable
diagnose debug flow trace start 100
diagnose debug enable

# Session table inspection
get system session-info summary
diagnose sys session filter dst 8.8.8.8
diagnose sys session list
```

## Hardware Acceleration (NP6 / NP7 & CP9 SPU)
FortiGate hardware utilizes Network Processors (NP6/NP7) for wire-speed Layer 4 offloading and Content Processors (CP9) for hardware-accelerated AES-GCM cryptography and deep packet inspection (DPI).
When a session is offloaded to NP, flow trace prints `gkernel session [x] offloaded to npu`.
""",
    ),
    (
        VAULT_KB / "Arista_EOS_and_Leaf_Spine_Data_Center_Fabric.md",
        """# Arista EOS and Leaf-Spine Data Center Fabric

## Clos Architecture (Spine-and-Leaf)
Modern enterprise data centers eliminate legacy Spanning Tree topologies by deploying 2-tier or 3-tier non-blocking Clos networks.
- **Spine Layer:** High-radix packet forwarding engines (e.g. Arista 7060X / 7280R) interconnecting leaf switches with uncompressed ECMP (Equal-Cost Multi-Path).
- **Leaf Layer:** Top-of-Rack (ToR) switches providing Layer 2 access or VXLAN Tunnel Endpoints (VTEPs) with BGP EVPN control plane.

```text
       [ Spine 01 ]               [ Spine 02 ]
         /      \\                   /      \\
        /        \\                 /        \\
 [ Leaf 01 ]    [ Leaf 02 ]   [ Leaf 03 ]    [ Leaf 04 ]
      |              |             |              |
   Servers        Servers       Storage        Compute
```

## Arista EOS Multi-Chassis Link Aggregation (MLAG)
```text
switch# configure terminal
switch(config)# mlag configuration
switch(config-mlag)# domain-id MLAG_PROD
switch(config-mlag)# local-interface Vlan4094
switch(config-mlag)# peer-address 10.255.255.2
switch(config-mlag)# peer-link Port-Channel10
```

## Health Verification
```bash
show mlag
show mlag detail
show bgp evpn summary
show vxlan vtep
show interfaces counters errors
```
""",
    ),
    (
        VAULT_KB / "Edgecore_Managed_Switches_and_VLAN_Trunking_8021Q.md",
        """# Edgecore Managed Switches and VLAN Trunking (802.1Q)

## 802.1Q Frame Format & Tagging
IEEE 802.1Q inserts a 4-byte Tag Protocol Identifier (TPID 0x8100) and Tag Control Information (TCI) containing:
- **PCP (3 bits):** Priority Code Point for Class of Service (QoS).
- **DEI (1 bit):** Drop Eligible Indicator.
- **VID (12 bits):** VLAN Identifier supporting up to 4094 unique VLANs.

## Edgecore CLI Configuration (EC-NOS / Open Network Linux)
```text
Edgecore# configure
Edgecore(config)# vlan 10
Edgecore(config-vlan)# name CORPORATE_DATA
Edgecore(config-vlan)# exit
Edgecore(config)# vlan 20
Edgecore(config-vlan)# name VOIP_TELEPHONY
Edgecore(config-vlan)# exit

Edgecore(config)# interface gigabitethernet 1/1
Edgecore(config-if)# switchport mode trunk
Edgecore(config-if)# switchport trunk allowed vlan 10,20,99
Edgecore(config-if)# switchport trunk native vlan 99
```

## Troubleshooting Port States
```bash
show vlan
show interfaces switchport gigabitethernet 1/1
show mac-address-table vlan 10
```
""",
    ),
    (
        VAULT_KB / "Dual_ISP_Failover_and_SD_WAN_Policy_Routing.md",
        """# Dual-ISP Failover and SD-WAN Policy Routing

## Design Overview
Dual-ISP deployment provides internet survivability and latency-sensitive path selection across Primary (e.g. Fiber DIA) and Secondary (e.g. Commercial Broadband / 5G Backup) connections.

```text
               +----------------------+
               |    Core FortiGate    |
               +----------+-----------+
                          |
              +-----------+-----------+
              |                       |
      [WAN1: Fiber 500M]      [WAN2: 5G/Coax 200M]
              |                       |
        ISP A (Primary)        ISP B (Secondary)
```

## Health Check & Performance SLA
Health probes measure packet loss, round-trip latency, and jitter via continuous ICMP/DNS requests.
```bash
config system sdwan
    config health-check
        edit "Google_DNS_Probe"
            set server "8.8.8.8" "1.1.1.1"
            set interval 500
            set probe-timeout 1000
            set failtime 3
            set recoverytime 5
            set members 1 2
        next
    end
end
```

## Service Rules
- VoIP/SIP Traffic: Lowest Jitter SLA across WAN1/WAN2.
- Web & Heavy Downloads: Dynamic Spillover / Volume Load-Balancing.
""",
    ),
    (
        VAULT_KB / "Ubiquiti_UniFi_and_FortiAP_Wireless_Roaming_Optimization.md",
        """# Ubiquiti UniFi and FortiAP Wireless Roaming Optimization

## 802.11k, 802.11v, and 802.11r Protocols
- **802.11k (Neighbor Reports):** Informs client devices about nearby access points to reduce channel scanning latency.
- **802.11v (BSS Transition Management):** Allows APs to suggest roaming to closer APs when signal drops below target RSSI.
- **802.11r (Fast BSS Transition):** Pre-caches 4-way WPA2/WPA3 handshakes between APs, reducing roaming delay to <30ms (zero VoIP packet loss).

## Tuning RF Power & Channel Planning
- **2.4 GHz:** Strictly use 20 MHz width on non-overlapping channels 1, 6, 11 with low transmit power (10-12 dBm).
- **5 GHz:** Deploy 40 MHz or 80 MHz channel widths on DFS and non-DFS channels with medium transmit power (16-18 dBm).
- **Minimum RSSI Threshold:** Set AP disassociation threshold to `-75 dBm` to prevent sticky clients.
""",
    ),
    (
        VAULT_KB / "Grandstream_UCM_IP_PBX_and_SIP_Trunk_Debugging.md",
        """# Grandstream UCM IP-PBX and SIP Trunk Debugging

## SIP Architecture & Call Flow
Grandstream UCM6200/6300 series operate on an Asterisk core managing Session Initiation Protocol (SIP RFC 3261) and Real-time Transport Protocol (RTP RFC 3550).

```text
Caller IP Phone -----> UCM PBX -----> ITSP SIP Provider -----> PSTN
  INVITE ->             INVITE ->
  <- 100 Trying         <- 100 Trying
  <- 180 Ringing        <- 180 Ringing
  <- 200 OK             <- 200 OK
  ACK ->                ACK ->
  <============ 2-Way RTP Audio Stream (G.711 / G.729) ============>
```

## Troubleshooting SIP Registration & One-Way Audio
1. **NAT Traversal & STUN:** Configure external IP and local network exclusions in PBX Settings -> SIP -> NAT.
2. **SIP ALG Incompatibility:** Ensure SIP ALG is completely disabled on perimeter routers to prevent corrupted SDP headers.
3. **CLI Debugging:**
```bash
asterisk -rvvvvv
sip set debug on
rtp set debug on
pjsip show endpoints
```
""",
    ),
    (
        VAULT_KB / "Biometric_and_RFID_Access_Control_Systems.md",
        """# Biometric and RFID Access Control Systems

## Controller Architecture & Wiegand Protocol
Access control systems utilize centralized microcontrollers (e.g. ZKTeco, HID VertX, Paxton) communicating over RS-485 or OSDP (Open Supervised Device Protocol) to biometric optical/capacitive fingerprint scanners and RFID badge readers.

## Wiegand Interface Signal Lines
- **DATA0 (Green):** Low pulse represents binary 0.
- **DATA1 (White):** Low pulse represents binary 1.
- Standard 26-bit Wiegand frame: 1 parity bit, 8 facility code bits, 16 card number bits, 1 parity bit.

## Fail-Safe vs Fail-Secure Electric Locks
- **Fail-Safe (Maglocks):** Requires power to remain locked; unlocks during power cut for life safety egress (fire compliance).
- **Fail-Secure (Electric Strikes):** Stays locked during power loss; requires backup UPS or mechanical key bypass.
""",
    ),
    (
        VAULT_KB / "Windows_Server_Active_Directory_and_GPO_Hardening.md",
        """# Windows Server Active Directory and GPO Hardening

## Active Directory Tiering Architecture
Enterprise security separates identities into administrative boundaries:
- **Tier 0:** Domain Controllers, PKI, Azure AD Connect, Domain Admins.
- **Tier 1:** Member Servers, Hypervisors, Storage, Service Accounts.
- **Tier 2:** Workstations, End-User Accounts, Helpdesk.

## Key Group Policy Objects (GPOs) for Hardening
1. **Kerberos & NTLM Hardening:** Restrict NTLMv1, enforce NTLMv2 and Kerberos AES-128/256 encryption.
2. **LAPS (Local Administrator Password Solution):** Automatically rotates unique local admin passwords stored encrypted in AD attributes.
3. **SMBv1 Deprecation:** Enforce SMB 3.1.1 encryption and SMB signing via GPO.

## CLI Health Checks
```powershell
dcdiag /v /c /d /e /s:DC01
repadmin /replsummary
repadmin /showrepl * /csv > repl_status.csv
Get-ADDomainController -Filter * | Select-Object Name, IPv4Address, OperatingSystem
```
""",
    ),
    (
        VAULT_KB / "VMware_vSphere_ESXi_and_Storage_vMotion.md",
        """# VMware vSphere ESXi and Storage vMotion

## vMotion & Storage vMotion Mechanics
vMotion migrates active VM state between ESXi hosts with zero downtime using pre-copy memory iterative synchronizations and fast stun/resume (<100ms).
Storage vMotion moves virtual disk VMDK files across storage datastores (VMFS / NFS / vSAN) using snapshot mirroring and block-level change tracking.

```text
[ESXi Host 01] -------- 10GbE / 25GbE vMotion Network --------> [ESXi Host 02]
      |                                                              |
[Datastore A (SAN)] ======= Block-level Mirroring (FDM) ======> [Datastore B (NVMe)]
```

## ESXi CLI Diagnostics
```bash
# View network adapters and uplink link states
esxcli network nic list

# Monitor VM latency and disk queue metrics
esxtop
# (Press 'd' for disk adapter, 'u' for disk device, 'n' for network)

# Check storage paths and multipathing status
esxcli storage nmp device list
```
""",
    ),
    (
        VAULT_KB / "Oracle_and_SQL_Server_Database_Backup_Strategies.md",
        """# Oracle and SQL Server Database Backup Strategies

## Backup Architecture & RPO / RTO
- **RPO (Recovery Point Objective):** Maximum acceptable data loss window measured in time.
- **RTO (Recovery Time Objective):** Maximum acceptable duration required to restore operational database services.

## SQL Server Backup Strategy
1. **Full Backup:** Weekly (Sunday 00:00).
2. **Differential Backup:** Daily (Every 24 hours at 23:00).
3. **Transaction Log Backup:** Every 15 minutes with log truncation.
```sql
BACKUP DATABASE [ProdERP] TO DISK = N'E:\\Backups\\ProdERP_Full.bak' WITH COMPRESSION, STATS = 10;
BACKUP LOG [ProdERP] TO DISK = N'E:\\Backups\\ProdERP_Log.trn' WITH COMPRESSION;
```

## Oracle Database RMAN (Recovery Manager)
```bash
rman target /
RMAN> CONFIGURE DEFAULT DEVICE TYPE TO DISK;
RMAN> CONFIGURE BACKUP OPTIMIZATION ON;
RMAN> BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG DELETE INPUT;
```
""",
    ),
    (
        VAULT_KB / "BGP_Autonomous_Systems_and_Prefix_Filtering.md",
        """# BGP Autonomous Systems and Prefix Filtering

## Border Gateway Protocol (BGP-4)
BGP is the path-vector exterior gateway protocol of the global Internet. It exchanges Reachability Information (NLRI) between distinct Autonomous System Numbers (ASNs).

## Best Path Selection Hierarchy
1. Highest Weight (Cisco proprietary, local to switch).
2. Highest Local Preference (Default 100, advertised within iBGP).
3. Locally Originated Routes (network or aggregate-address).
4. Shortest AS-Path length.
5. Lowest Origin Type (IGP < EGP < Incomplete).
6. Lowest MED (Multi-Exit Discriminator).
7. eBGP over iBGP.
8. Lowest IGP metric to next-hop.
9. Lowest BGP Router ID.

## ROA & RPKI Validation
Prefix filtering must validate Route Origin Authorizations (ROA) via RPKI to prevent BGP route hijacking.
""",
    ),
    (
        VAULT_KB / "OSPF_Area_Hierarchy_and_LSA_Type_Optimization.md",
        """# OSPF Area Hierarchy and LSA Type Optimization

## Link-State Routing & Area Boundaries
Open Shortest Path First (OSPFv2 / OSPFv3) maintains identical Link-State Databases (LSDB) within an area, executing Dijkstra's Shortest Path First (SPF) algorithm.
- **Area 0 (Backbone Area):** Central hub through which all inter-area traffic must traverse.
- **Non-Backbone Areas (Area 1..N):** Edge enterprise networks connected via Area Border Routers (ABRs).

## Link-State Advertisements (LSAs)
- **Type 1 (Router LSA):** Generated by all routers within an area describing local links.
- **Type 2 (Network LSA):** Generated by Designated Routers (DR) on multi-access broadcast segments.
- **Type 3 (Summary LSA):** Generated by ABRs describing inter-area routes.
- **Type 4 (ASBR Summary LSA):** Informs areas how to reach Autonomous System Boundary Routers.
- **Type 5 (External LSA):** Routes redistributed from outside the OSPF domain (e.g. BGP or static).
""",
    ),
    (
        VAULT_KB / "IPsec_Site_to_Site_VPN_Phase1_Phase2_Troubleshooting.md",
        """# IPsec Site-to-Site VPN Phase 1 and Phase 2 Troubleshooting

## IKEv2 Negotiation Protocol
IPsec establishes encrypted tunnels across untrusted transit networks using Internet Key Exchange (IKE):

### Phase 1 (IKE SA)
Authenticates peers and builds secure control channel.
- Matching Parameters: Encryption (AES-GCM-256), Hash (SHA-384), Diffie-Hellman Group (Group 14 / Group 20), Pre-Shared Key (PSK), Peer IP.

### Phase 2 (IPsec SA)
Negotiates actual data-encryption parameters and selectors.
- Encapsulating Security Payload (ESP RFC 4303).
- Proxy IDs / Traffic Selectors: Local Subnet <-> Remote Subnet.

## Debugging Commands
```bash
# FortiOS
diagnose vpn ike log filter dst-addr4 <Peer_IP>
diagnose debug application ike -1
diagnose debug enable

# Cisco IOS
show crypto ikev2 sa
show crypto ipsec sa
show crypto session detail
```
""",
    ),
    (
        VAULT_KB / "RADIUS_and_802_1X_Enterprise_Network_Authentication.md",
        """# RADIUS and 802.1X Enterprise Network Authentication

## Extensible Authentication Protocol (EAP)
802.1X prevents unauthorized physical or wireless devices from accessing corporate networks by intercepting Layer 2 frames until mutual authentication completes.
- **Supplicant:** Client laptop / mobile device running 802.1X client software.
- **Authenticator:** Network edge switch or wireless access point.
- **Authentication Server:** Central RADIUS server (FreeRADIUS, Cisco ISE, Microsoft NPS).

## Common EAP Types
- **EAP-TLS:** Mutual PKI certificate authentication (highest security, no credentials transmitted).
- **PEAP-MSCHAPv2:** TLS tunnel protects username/password challenge against Active Directory.

## Dynamic VLAN Assignment
RADIUS response packet returns RFC 2868 attributes:
- `Tunnel-Type = 13 (VLAN)`
- `Tunnel-Medium-Type = 6 (802)`
- `Tunnel-Private-Group-ID = "10"` (Assigns user dynamically to VLAN 10).
""",
    ),
    (
        VAULT_KB / "SNMPv3_and_Syslog_Centralized_Network_Monitoring.md",
        """# SNMPv3 and Syslog Centralized Network Monitoring

## Simple Network Management Protocol v3
Unlike insecure SNMPv1/v2c which transmits cleartext community strings, SNMPv3 provides:
1. **Authentication (authNoPriv):** HMAC-SHA-256 verifying sender integrity.
2. **Encryption (authPriv):** AES-128 / AES-256 payload privacy preventing packet inspection.

## Centralized Syslog Facility Levels (RFC 5424)
- Severity 0: Emergency (System unusable).
- Severity 1: Alert (Immediate action required).
- Severity 2: Critical (Hardware component failure).
- Severity 3: Error (Operational impairment).
- Severity 4: Warning (Threshold warning).
- Severity 5: Notice (Normal significant event).
- Severity 6: Informational.
- Severity 7: Debug.
""",
    ),
    (
        VAULT_KB / "DHCP_Snooping_and_Dynamic_ARP_Inspection_DAI.md",
        """# DHCP Snooping and Dynamic ARP Inspection (DAI)

## Layer 2 Man-in-the-Middle Mitigation
- **DHCP Snooping:** Categorizes switch ports as *Trusted* (facing authorized DHCP server) or *Untrusted* (facing end users). Drops rogue DHCP Offer/ACK packets originating from untrusted ports. Builds the **DHCP Snooping Binding Database** mapping MAC, IP, Lease, and Port.
- **Dynamic ARP Inspection (DAI):** Intercepts Address Resolution Protocol (ARP) packets on untrusted ports, validating them against the DHCP binding database to prevent ARP Poisoning / Spoofing attacks.
- **IP Source Guard (IPSG):** Verifies Layer 3 source IP against the binding database, dropping spoofed packets at the physical port level.
""",
    ),
    (
        VAULT_KB / "Spanning_Tree_Protocol_RSTP_MSTP_and_Root_Guard.md",
        """# Spanning Tree Protocol: RSTP, MSTP, and Root Guard

## IEEE 802.1w (Rapid Spanning Tree Protocol)
RSTP reduces convergence time from 50 seconds to <2 seconds using Proposal-Agreement handshakes instead of timer-based states.
- **Port Roles:** Root Port, Designated Port, Alternate Port, Backup Port.
- **Port States:** Discarding, Learning, Forwarding.

## Spanning Tree Protection Mechanisms
1. **BPDU Guard:** Instantly err-disables an Edge/PortFast port if an unexpected BPDU frame is received, preventing unauthorized switch loops.
2. **Root Guard:** Enforces root bridge placement by placing ports into root-inconsistent state if a superior BPDU arrives.
3. **Loop Guard:** Prevents alternate or root ports from becoming designated due to unidirectional link failures.
""",
    ),
    (
        VAULT_KB / "Network_Time_Protocol_NTP_Stratum_Hierarchy.md",
        """# Network Time Protocol (NTP) Stratum Hierarchy

## Precision Time Architecture
Accurate clock synchronization is mandatory for Active Directory Kerberos tickets (max skew: 5 minutes), forensic log correlation, and database distributed transactions.

```text
[Stratum 0: Atomic Clock / GPS Satellites]
                  |
[Stratum 1: Primary Time Servers (Directly Attached)]
                  |
[Stratum 2: Enterprise Core Switches / Active Directory PDC]
                  |
[Stratum 3: Edge Switches, Virtual Machines, Workstations]
```

## NTP UDP Port 123 Configuration
```bash
# Verify synchronization status on Linux
chronyc tracking
chronyc sources -v

# Windows Server PDC Emulator Time Source Configuration
w32tm /config /manualpeerlist:"pool.ntp.org,0x8" /syncfromflags:manual /reliable:yes /update
w32tm /resync /rediscover
w32tm /query /status
```
""",
    ),
    (
        VAULT_KB / "Fiber_Optic_Transceivers_SFP_QSFP_and_OTDR_Testing.md",
        """# Fiber Optic Transceivers (SFP/QSFP) and OTDR Testing

## Transceiver Form Factors & Wavelengths
- **SFP+ (10 Gbps):** 850nm (10GBASE-SR Multimode, up to 300m OM3/OM4) vs 1310nm (10GBASE-LR Singlemode, up to 10km).
- **SFP28 (25 Gbps):** High-density top-of-rack interconnects.
- **QSFP28 (100 Gbps):** 4x25Gbps optical lanes (e.g. 100GBASE-SR4 MPO or 100GBASE-LR4 LC duplex).

## Optical Time-Domain Reflectometer (OTDR) Diagnostics
An OTDR injects high-speed laser light pulses down an optical fiber and analyzes backscattered Rayleigh reflections and Fresnel reflection peaks:
- Reflection Spikes: Identify physical connector junctions, dirty patch panels, or mechanical splices.
- Attenuation Slope: Measures loss in dB/km (standard singlemode 1310nm loss: ~0.35 dB/km).
- Abrupt Drops: Pinpoint micro-bends, macro-bends, or physical cable breaks.
""",
    ),
    (
        VAULT_KB / "Disaster_Recovery_RTO_RPO_and_Immutable_Storage.md",
        """# Disaster Recovery: RTO, RPO, and Immutable Storage

## 3-2-1-1-0 Backup Rule
- **3 Copies of Data:** Primary production data plus two independent backups.
- **2 Different Media Types:** E.g. local NVMe/SSD array and enterprise LTO Tape / Cloud Object Storage.
- **1 Copy Kept Offsite:** Geographically isolated secondary data center.
- **1 Copy Immutable or Air-Gapped:** Protected by Object Lock WORM (Write Once, Read Many).
- **0 Errors After Testing:** Continuous automated daily restore verification.

## Immutable Storage Architecture
Prevents ransomware operators or compromised administrator accounts from encrypting or deleting historical snapshots.
AWS S3 Object Lock and MinIO deploy compliance retention modes where retention duration cannot be overridden even by root credentials.
""",
    ),

    # -------------------------------------------------------------
    # Category 2: Full-Stack Software Engineering & AI Architecture (20 Notes)
    # -------------------------------------------------------------
    (
        VAULT_KB / "NextJS_15_App_Router_and_Server_Actions.md",
        """# Next.js 15 App Router and Server Actions Architecture

## Core Architectural Primitives
Next.js 15 leverages React 19 architecture, unifying frontend rendering and backend mutations:
1. **React Server Components (RSC):** Render exclusively on the server, streaming lightweight virtual DOM representations to the client with zero bundle-size overhead.
2. **Server Actions (`'use server'`):** Asynchronous functions executed on the server, callable directly from client forms or event handlers without writing boilerplate REST/GraphQL routes.

```tsx
// app/actions/update-profile.ts
'use server';
import { z } from 'zod';
import { prisma } from '@/lib/db';
import { revalidatePath } from 'next/cache';

const ProfileSchema = z.object({
  name: z.string().min(2),
  bio: z.string().max(250),
});

export async function updateProfile(formData: FormData) {
  const parsed = ProfileSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: parsed.error.flatten() };

  await prisma.user.update({
    where: { id: 'user_123' },
    data: parsed.data,
  });

  revalidatePath('/profile');
  return { success: true };
}
```

## Caching Behavior in Next.js 15
Next.js 15 changed `fetch` requests, `GET` route handlers, and client navigations to **uncached by default**, giving developers complete predictability over live data freshness.
""",
    ),
    (
        VAULT_KB / "React_19_Concurrent_Rendering_and_Server_Components.md",
        """# React 19 Concurrent Rendering and Server Components

## Key Primitives in React 19
- **`useActionState`:** Simplifies form handling by managing pending states, return values, and form actions natively.
- **`useOptimistic`:** Displays immediate UI updates before network confirmation, automatically rolling back on failure.
- **`use` Hook:** Resolves promises and contexts directly inside components during render.

```tsx
import { useOptimistic } from 'react';

export function CommentList({ comments, addCommentAction }: { comments: Comment[]; addCommentAction: (c: string) => Promise<void> }) {
  const [optimisticComments, setOptimisticComments] = useOptimistic(
    comments,
    (state, newText: string) => [...state, { id: Date.now(), text: newText, sending: true }]
  );

  return (
    <div>
      {optimisticComments.map(c => (
        <p key={c.id} style={{ opacity: c.sending ? 0.6 : 1 }}>{c.text}</p>
      ))}
      <form action={async (formData) => {
        const text = formData.get('comment') as string;
        setOptimisticComments(text);
        await addCommentAction(text);
      }}>
        <input name="comment" required />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
```
""",
    ),
    (
        VAULT_KB / "TypeScript_Strict_Generics_and_Type_Narrowing.md",
        """# TypeScript Strict Generics and Type Narrowing

## Advanced Type Narrowing Techniques
TypeScript leverages control flow analysis to narrow broad unions into specific concrete types using:
1. **Discriminated Unions:** Tagged property guarantees exhaustive `switch` cases.
2. **Custom Type Guards (`val is TargetType`):** Validates structure at runtime while narrowing compiler AST.
3. **Template Literal Types:** Enforces string patterns (e.g. `type HexColor = \`#\${string}\``).

```typescript
type ApiResponse<T> = 
  | { status: 'success'; data: T; timestamp: number }
  | { status: 'error'; message: string; code: number };

function handleResponse<T>(res: ApiResponse<T>): T {
  if (res.status === 'error') {
    throw new Error(`API Error [${res.code}]: ${res.message}`);
  }
  // TypeScript automatically narrows res to { status: 'success'; data: T }
  return res.data;
}

// Exhaustiveness checking with never type
type Shape = { kind: 'circle'; radius: number } | { kind: 'square'; size: number };

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'square': return shape.size ** 2;
    default:
      const _exhaustive: never = shape;
      throw new Error(`Unhandled shape: ${_exhaustive}`);
  }
}
```
""",
    ),
    (
        VAULT_KB / "Tailwind_CSS_and_Dark_Mode_Design_Systems.md",
        """# Tailwind CSS and Dark-Mode Design Systems

## Semantic CSS Variables Architecture
Rather than hardcoding utility colors like `bg-gray-900`, enterprise design systems map functional tokens via CSS variables for smooth theming:

```css
:root {
  --background: 220 20% 98%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --border: 214 32% 91%;
}

.dark {
  --background: 224 71% 4%;
  --foreground: 210 40% 98%;
  --primary: 217 91% 60%;
  --border: 217 33% 17%;
}
```

## Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background) / <alpha-value>)',
        foreground: 'hsl(var(--foreground) / <alpha-value>)',
        primary: 'hsl(var(--primary) / <alpha-value>)',
        border: 'hsl(var(--border) / <alpha-value>)',
      }
    }
  }
}
```
""",
    ),
    (
        VAULT_KB / "TanStack_Query_Caching_and_Optimistic_Updates.md",
        """# TanStack Query Caching and Optimistic Updates

## Asynchronous State Management
TanStack Query (React Query v5) abstracts network cache invalidation, deduplication, and background refetching away from local state.
- **`staleTime`:** Duration data remains fresh before background refetch occurs.
- **`gcTime` (Garbage Collection):** Duration unused cache entries remain in memory before disposal.

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updatedUser: User) => {
      const res = await fetch(`/api/user/${updatedUser.id}`, {
        method: 'PUT',
        body: JSON.stringify(updatedUser),
      });
      return res.json();
    },
    onMutate: async (newUser) => {
      // Cancel outbound queries
      await queryClient.cancelQueries({ queryKey: ['user', newUser.id] });
      const previousUser = queryClient.getQueryData(['user', newUser.id]);
      // Optimistically update cache
      queryClient.setQueryData(['user', newUser.id], newUser);
      return { previousUser };
    },
    onError: (err, newUser, context) => {
      // Rollback on failure
      queryClient.setQueryData(['user', newUser.id], context?.previousUser);
    },
    onSettled: (data, err, variables) => {
      queryClient.invalidateQueries({ queryKey: ['user', variables.id] });
    },
  });
}
```
""",
    ),
    (
        VAULT_KB / "Prisma_ORM_and_PostgreSQL_Indexing_at_Scale.md",
        """# Prisma ORM and PostgreSQL Indexing at Scale

## High-Performance PostgreSQL Schema
Prisma bridges TypeScript models to relational tables. At high concurrency, missing indexes cause sequential full-table scans, driving CPU to 100%.

```prisma
model Order {
  id          String      @id @default(uuid())
  userId      String
  status      OrderStatus @default(PENDING)
  totalAmount Decimal     @db.Decimal(12, 2)
  createdAt   DateTime    @default(now())
  user        User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  // Compound index for user query sorting
  @@index([userId, createdAt(sort: Desc)])
  // Partial index or status filter
  @@index([status])
}
```

## B-Tree vs GIN & GiST Indexes in Postgres
- **B-Tree (Default):** Optimal for equality (`=`), range queries (`<, <=, >, >=`), and sorting (`ORDER BY`).
- **GIN (Generalized Inverted Index):** Mandatory for JSONB keys, array membership, and Full-Text Search.
- **BRIN (Block Range Index):** Ultra-compact index for massive append-only sequential time-series tables.
""",
    ),
    (
        VAULT_KB / "Supabase_Row_Level_Security_RLS_and_Auth.md",
        """# Supabase Row-Level Security (RLS) and Auth

## Declarative Database Authorization
PostgreSQL Row-Level Security (RLS) evaluates access policies at the SQL engine level, guaranteeing that API clients cannot bypass permissions even if frontend code is manipulated.

```sql
-- Enable RLS on document table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy 1: Users can read their own documents
CREATE POLICY "Users can read own documents"
ON documents FOR SELECT
USING (auth.uid() = user_id);

-- Policy 2: Organization admins can view all org documents
CREATE POLICY "Org Admins can view org documents"
ON documents FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM org_memberships
    WHERE org_memberships.org_id = documents.org_id
      AND org_memberships.user_id = auth.uid()
      AND org_memberships.role = 'ADMIN'
  )
);
```
""",
    ),
    (
        VAULT_KB / "Docker_Multi_Stage_Builds_for_Production.md",
        """# Docker Multi-Stage Builds for Production

## Minimizing Attack Surface & Image Footprint
Multi-stage Docker builds separate build dependencies (compilers, Node devDependencies, header files) from lean runtime artifacts, reducing image size from >1.5GB to <95MB.

```dockerfile
# Stage 1: Dependency resolution
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: Application compilation
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
RUN npm run build

# Stage 3: Minimal production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
```
""",
    ),
    (
        VAULT_KB / "Local_LLM_Quantization_NF4_GGUF_AWQ_Comparison.md",
        """# Local LLM Quantization: NF4, GGUF, and AWQ Comparison

## Quantization Formats & Trade-offs
Quantization maps 16-bit floating point weights (FP16/BF16) to low-bit integers (4-bit / 8-bit), allowing 8B parameter models to run within 8GB VRAM (e.g. RTX 4060):

| Format | Execution Engine | Best Use Case | VRAM for 8B Model | Perplexity Loss |
| :--- | :--- | :--- | :--- | :--- |
| **NF4 (bitsandbytes)** | PyTorch / CUDA | LoRA Training & Fine-Tuning | ~5.4 GB | Extremely Low |
| **GGUF (llama.cpp)** | CPU + GPU Hybrid Offload | Cross-platform desktop apps | ~4.8 GB (Q4_K_M) | Low |
| **AWQ (Activation-aware)** | vLLM / TensorRT-LLM | High-throughput server serving | ~5.0 GB | Very Low |

## NF4 (NormalFloat4) Mathematical Principle
Unlike uniform integer quantization (INT4), NF4 represents normally distributed transformer weights with information-theoretically optimal quantiles, maintaining near-FP16 fidelity without outlier clipping.
""",
    ),
    (
        VAULT_KB / "ONNX_Runtime_CPU_Vector_Optimization_AVX2.md",
        """# ONNX Runtime CPU Vector Optimization (AVX2 / AVX-512)

## Vector Instruction Acceleration
ONNX Runtime executes graph optimizations on CPUs by utilizing Intel AVX2 and AVX-512 vector units to execute SIMD (Single Instruction, Multiple Data) operations across 256-bit or 512-bit registers.

## Optimizing Session Options in Python
```python
import onnxruntime as ort

opts = ort.SessionOptions()
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
opts.intra_op_num_threads = 8   # Match Intel Core i5 physical/logical cores
opts.inter_op_num_threads = 2
opts.execution_mode = ort.ExecutionMode.ORT_PARALLEL

session = ort.InferenceSession("kokoro-v1.0.onnx", sess_options=opts, providers=["CPUExecutionProvider"])
```
This configuration accelerates Kokoro-ONNX neural speech synthesis, generating spoken audio chunks in <120ms without taxing the GPU.
""",
    ),
    (
        VAULT_KB / "FastAPI_Asyncio_and_Uvicorn_Production_Architecture.md",
        """# FastAPI, Asyncio, and Uvicorn Production Architecture

## Asynchronous Event Loop & Concurrency
FastAPI leverages Starlette and Pydantic on top of the Python `asyncio` event loop.
- **I/O Bound Endpoints (`async def`):** Non-blocking HTTP endpoints that await database queries, network sockets, or file streams without blocking concurrent requests.
- **CPU/GPU Bound Endpoints (`def` or `asyncio.to_thread`):** Heavy tensor generation and neural inference must be dispatched to worker thread pools (`asyncio.to_thread(cortex.generate, ...)`) to avoid freezing the event loop.

## High-Throughput Production Uvicorn Tuning
```bash
uvicorn jessica_server:app \
  --host 127.0.0.1 \
  --port 8000 \
  --workers 1 \
  --loop uvloop \
  --http httptools \
  --no-access-log
```
""",
    ),
    (
        VAULT_KB / "PyTorch_FlashAttention_and_SDPA_Inference_Kernels.md",
        """# PyTorch FlashAttention and SDPA Inference Kernels

## Scaled Dot-Product Attention (SDPA)
Standard attention computes $O(N^2)$ memory bandwidth by writing full intermediate attention matrices ($Q K^T / \\sqrt{d}$) to High Bandwidth Memory (HBM).
FlashAttention tiles attention computation into GPU SRAM blocks, fusing softmax and matrix multiplication, cutting memory bandwidth consumption by up to 80%.

## Enabling SDPA Kernels in PyTorch
```python
import torch

with torch.inference_mode():
    with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=True):
        output = model(input_ids)
```
Enabling SDPA alongside TensorFloat-32 (`allow_tf32 = True`) accelerates generation throughput on Ada Lovelace RTX 4060 GPUs.
""",
    ),
    (
        VAULT_KB / "BitAndBytes_4Bit_NF4_De-quantization_Mechanics.md",
        """# BitsAndBytes 4-Bit NF4 De-quantization Mechanics

## On-the-Fly Dynamic De-quantization
In `bitsandbytes` 4-bit Linear layers (`Linear4bit`), weights remain stored in compressed 4-bit memory format in VRAM.
During forward pass:
1. Active input activations (FP16/BF16) arrive at the CUDA core.
2. The custom `bitsandbytes` CUDA kernel de-quantizes the 4-bit weight slice into 16-bit registers on-the-fly.
3. High-speed FP16 Tensor Core matrix multiplication executes.
4. Intermediate de-quantized weights are immediately discarded from registers, never allocating FP16 footprint in global VRAM.
""",
    ),
    (
        VAULT_KB / "HuggingFace_TextIteratorStreamer_Token_Pipeline.md",
        """# HuggingFace TextIteratorStreamer Token Pipeline

## Pipelined Streaming Architecture
To deliver natural human conversational pacing, text generation must stream tokens to speech vocoders sentence-by-sentence rather than buffering entire paragraphs.

```text
[PyTorch GPU Worker] ----(tokens via Streamer)----> [Thread Queue]
                                                           |
[8-Thread CPU Worker] <==== Sentence Chunks (". ! ?") =====+
         |
[Kokoro-ONNX Speech Engine] ====> Audio Output Stream
```

`TextIteratorStreamer` operates in a background thread, pushing decoded subwords into an internal queue while the main thread consumes clauses immediately.
""",
    ),
    (
        VAULT_KB / "Whisper_Int8_Polyphase_Acoustic_Processing.md",
        """# Whisper Int8 Polyphase Acoustic Processing

## Faster-Whisper CTranslate2 Engine
Faster-Whisper re-implements OpenAI Whisper in C++ using CTranslate2, executing quantized 8-bit integer matrix multiplication on CPU vector registers.
- **Polyphase Resampling:** Converts 44,100 Hz or 48,000 Hz hardware microphone audio directly to 16,000 Hz with anti-aliasing sinc filters.
- **Log-Mel Spectrogram:** Transforms 16 kHz raw audio into 80-channel log-magnitude Mel-frequency representations across 25ms windows with 10ms hop length.
- **Transcription Latency:** Cuts transcription latency from ~2.4s to <400ms on Intel Core i5 CPUs.
""",
    ),
    (
        VAULT_KB / "YOLOv8_Anchor_Free_Object_Detection_Pipelines.md",
        """# YOLOv8 Anchor-Free Object Detection Pipelines

## Anchor-Free Architecture
Ultralytics YOLOv8 abandons legacy anchor boxes in favor of anchor-free split-head detection:
- **Task-Aligned Assignor:** Dynamically balances classification confidence and bounding-box Intersection-over-Union (IoU).
- **Decoupled Head:** Computes classification loss (Binary Cross-Entropy) and regression loss (Complete IoU + Distribution Focal Loss) independently.
- **Execution on CPU:** YOLOv8n (nano, ~3.2M parameters) runs inference in ~18ms on an Intel Core i5 CPU, allocating zero GPU VRAM.
""",
    ),
    (
        VAULT_KB / "SQLite_WAL_Mode_and_High_Concurrency_Access.md",
        """# SQLite WAL Mode and High-Concurrency Access

## Write-Ahead Logging (WAL) Architecture
Default SQLite rollback journals lock the entire database file during writes, blocking concurrent readers.
WAL mode separates writes into an append-only `*.db-wal` log file:
- Readers read from the database file and WAL concurrently without locking.
- Writers append changes to the WAL without blocking readers.
- Background checkpoints periodically flush WAL changes into the primary `.db` file.

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -64000; -- 64MB In-Memory Page Cache
```
""",
    ),
    (
        VAULT_KB / "Redis_In_Memory_Caching_and_Key_Eviction_Policies.md",
        """# Redis In-Memory Caching and Key Eviction Policies

## Key Memory Eviction Strategies
When Redis reaches `maxmemory`, it triggers memory reclamation based on configured eviction policies:
1. **`volatile-lru`:** Evicts Least Recently Used keys with an explicit TTL expiration.
2. **`allkeys-lru`:** Evicts Least Recently Used keys across all stored data.
3. **`volatile-lfu`:** Evicts Least Frequently Used keys based on logarithmic access counters.
4. **`noeviction`:** Returns memory errors on new write operations while servicing reads.

## Redis Data Structures
- **Hashes (`HSET`, `HGET`):** High-efficiency representation of objects.
- **Sorted Sets (`ZADD`, `ZRANGE`):** Real-time leaderboards and rate-limiting sliding windows.
- **Streams (`XADD`, `XREAD`):** Persistent distributed message bus with consumer groups.
""",
    ),
    (
        VAULT_KB / "Web_Worker_and_Canvas_Offscreen_Frame_Processing.md",
        """# Web Worker and Canvas Offscreen Frame Processing

## Offloading Main-Thread Rendering
Real-time webcam feeds at 1080p 60fps can cause UI stutter if frame analysis runs on the browser main UI thread.
`OffscreenCanvas` allows canvas rendering and pixel transformations to run inside an isolated Web Worker:
```javascript
// main.js
const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker('vision-worker.js');
worker.postMessage({ canvas: offscreen }, [offscreen]);

// vision-worker.js
onmessage = function(e) {
  const canvas = e.data.canvas;
  const ctx = canvas.getContext('2d');
  // Process frames in background thread with zero UI lag
};
```
""",
    ),
    (
        VAULT_KB / "RESTful_vs_gRPC_High_Throughput_Microservices.md",
        """# RESTful vs gRPC High-Throughput Microservices

## Protocol Comparison
- **REST (HTTP/1.1 + JSON):** Human-readable, text-based serialization, high compatibility, but higher header overhead and JSON parsing costs.
- **gRPC (HTTP/2 + Protocol Buffers):** Binary serialization via Protobuf, multiplexed bidirectional streaming on single TCP connections, strongly typed interfaces generated from `.proto` definitions.

## Throughput & Serialization Performance
Protobuf binary packing reduces wire payload sizes by 40-70% compared to equivalent JSON payloads, cutting CPU serialization overhead by up to 5x.
""",
    ),

    # -------------------------------------------------------------
    # Category 3: Music, Culinary Science, Hardware & Everyday Mastery (24 Notes)
    # -------------------------------------------------------------
    (
        VAULT_KB / "Four_String_Jazz_Bass_Setup_and_Neck_Relief.md",
        """# 4-String Jazz Bass Setup and Neck Relief

## Ergonomic Setup Geometry
A precision setup balances string tension and truss-rod counterforce to achieve fast playability without fret buzz:

1. **Neck Relief (Truss Rod):**
   - Capo on 1st fret, hold down string at last fret.
   - Measure gap at 7th/8th fret using a feeler gauge. Target relief: `0.012 to 0.014 inches` (`0.30 - 0.35 mm`).
   - Clockwise turn tightens rod (flattens neck / reduces relief); counter-clockwise loosens rod (adds relief).
2. **String Action (Bridge Saddles):**
   - Measure distance from top of 17th fret to bottom of string.
   - E-String: `2.2 - 2.4 mm`. G-String: `1.8 - 2.0 mm`.
3. **Pickup Heights:**
   - Depress strings at highest fret.
   - Neck Pickup: 3.0mm (Bass side) / 2.5mm (Treble side).
   - Bridge Pickup: 2.5mm (Bass side) / 2.0mm (Treble side).
4. **Intonation:** Match 12th fret harmonic pitch exactly with fretted 12th fret pitch.
""",
    ),
    (
        VAULT_KB / "Fretboard_Mastery_and_Fingerboard_EQ_Sculpting.md",
        """# Fretboard Mastery and Fingerboard EQ Sculpting

## Tonality & Equalization Anatomy
The electric bass occupies the fundamental musical foundation between 40 Hz and 4 kHz:
- **40 - 80 Hz (Sub-Bass):** Deep physical resonance and kick drum coupling. High-pass filter below 35 Hz to prevent speaker cone over-excursion.
- **100 - 250 Hz (Punch & Body):** Core note definition and warmth. Boost for thick classic fingerstyle.
- **500 - 800 Hz (Bark & Growl):** Bridge pickup harmonic bite (Jaco Pastorius signature growl). Scoop slightly for slap bass.
- **1.5 - 3 kHz (Attack & Articulation):** Finger pluck transient attack and fretboard clarity.
- **Above 5 kHz:** Fret clack and string sizzle. Roll off smoothly for vintage warmth.
""",
    ),
    (
        VAULT_KB / "Multi_Effects_Pedal_Signal_Chain_and_IR_Loaders.md",
        """# Multi-Effects Pedal Signal Chain and IR Loaders

## Optimal Pedalboard Routing
```text
Bass Guitar -> Buffer / Tuner -> Compressor -> Envelope Filter / Wah -> Octaver -> Overdrive / Fuzz -> Preamp / EQ -> Modulation (Chorus) -> Delay / Reverb -> Amp Sim & Impulse Response (IR) -> DI Box
```

## Compressor Dynamics & Impulse Responses (IRs)
- **Optical / VCA Compression:** Ratio 3:1 or 4:1, medium attack (30ms) to preserve initial thumb pluck transient, fast release (100ms) to sustain low-end fundamentals.
- **Cabinet IRs:** Convolve real speaker acoustic profiles (e.g. Ampeg SVT 8x10 or Aguilar 4x10 mic'd with Shure SM57 and AKG D112) into direct line-out audio.
""",
    ),
    (
        VAULT_KB / "Slap_and_Finger_Style_Bass_Groove_Mechanics.md",
        """# Slap and Finger-Style Bass Groove Mechanics

## Physical Plucking Techniques
- **Slap (Thumb Bounce vs Slap-Through):**
  - Bounce: Thumb strikes string above fretboard and bounces off immediately to allow string to vibrate freely.
  - Slap-Through (Marcus Miller style): Thumb drives through the string to rest on the next lower string, producing maximum percussive momentum.
- **Pop (Index/Middle Finger):** Hook finger tip under the G or D string, pulling sharply upward and releasing against the metal fret wire.
- **Ghost Notes (Dead Notes):** Left hand rests lightly across strings without fretting while right hand strikes percussive muted clicks that establish rhythmic groove pocket.
""",
    ),
    (
        VAULT_KB / "IV_of_Spades_and_Funk_Rock_Bassline_Techniques.md",
        """# IV of Spades and Funk-Rock Bassline Techniques

## Funk-Rock Bassline Aesthetics
Inspired by classic Motown, disco, and 70s funk (James Jamerson, Bernard Edwards, Flea):
1. **Syncopation & 16th-Note Pocket:** Driving forward pulse using 16th-note syncopation and chromatic passing tones.
2. **Octave Jumps:** Rapid transitions between root note on low string and octave slap/pop on higher string.
3. **Harmonic Minor & Dorian Flavors:** Incorporating natural 6ths and flat 7ths over minor chord vamps to create uplifting, energetic dance momentum.
""",
    ),
    (
        VAULT_KB / "Chewy_Chocolate_Chip_Cookie_Maillard_Chemistry.md",
        """# Chewy Chocolate Chip Cookie Maillard Chemistry

## Cookie Thermodynamics & Moisture Control
The holy grail of cookies balances a crisp golden exterior with a dense, fudgy, chewy center:

```text
Cold Butter (Fluffy/Cakey) <=======> Melted & Browned Butter (Dense/Chewy/Caramelized)
Granulated Sugar (Spread & Crispness) <=======> Dark Brown Sugar (Moisture & Molasses Chew)
```

1. **High Brown-to-White Sugar Ratio:** Use 70% dark brown sugar and 30% white granulated sugar. The hygroscopic molasses in brown sugar retains water during baking, preventing complete dry-out.
2. **Egg Yolk Addition:** Add 1 whole egg plus 1 extra egg yolk. The extra lecithin and fats create rich emulsification without excess egg-white albumin water.
3. **Chill the Dough (24-48 Hours):** Allows flour enzymes to break starches into simple sugars and hydrates proteins, intensifying caramelization.
""",
    ),
    (
        VAULT_KB / "Toasted_Milk_Powder_and_Browned_Butter_Cookie_Science.md",
        """# Toasted Milk Powder and Browned Butter Cookie Science

## Beurre Noisette (Browned Butter)
Heating butter past 100°C evaporates water (~16-18% of butter weight). The remaining milk solids (proteins and lactose) undergo the Maillard reaction at 140°C, producing rich nutty, hazelnut aromas.

## The Secret Flavor Weapon: Toasted Milk Powder
Adding 2 tablespoons of dry non-fat milk powder to the melting butter quadruples the volume of caramelized milk solids, creating an intense butterscotch, toffee flavor profile that ordinary butter cannot achieve alone.
Always compensate for evaporated water by adding 1 tablespoon of milk or ice cubes back into the cooled browned butter before creaming.
""",
    ),
    (
        VAULT_KB / "Drip_Coffee_Extraction_Ratios_and_Grind_Distribution.md",
        """# Drip Coffee Extraction Ratios and Grind Distribution

## Specialty Coffee Association (SCA) Golden Ratio
- **Standard Brewing Ratio:** `1:15 to 1:17` (e.g. 15g ground coffee to 250g water).
- **Water Temperature:** 92°C to 94°C (198°F - 201°F).
- **Target Total Dissolved Solids (TDS):** 1.20% to 1.45%, yielding an optimal **Extraction Yield of 18% to 22%**.

```text
Under-Extraction (<18% Yield): Sour, salty, lacking sweetness (Grind finer or increase contact time)
Over-Extraction (>22% Yield): Bitter, astringent, dry woody finish (Grind coarser or lower temp)
```

## Pour-Over Pour Dynamics (V60)
1. **Bloom (0:00 - 0:45):** 3x coffee weight (45g water). Releases trapped CO2 from fresh roast.
2. **First Pour (0:45 - 1:15):** Spiral outward to 150g.
3. **Second Pour (1:15 - 2:00):** Gentle center pour up to 250g. Total drawdown time: 2:45 to 3:15.
""",
    ),
    (
        VAULT_KB / "Arabica_Bean_Processing_Washed_vs_Natural.md",
        """# Arabica Bean Processing: Washed vs Natural

## Post-Harvest Processing Chemistry
- **Washed (Wet Process):** Coffee cherries are de-pulped immediately and fermented in water tanks to break down mucilage before washing and drying. Produces bright acidity, clean floral notes, and distinct origin terroir.
- **Natural (Dry Process):** Whole intact coffee cherries dry under the sun on raised African beds for 3-4 weeks. Sugars from the fruit pulp infuse into the seed, producing heavy body, intense blueberry/strawberry aromas, and wine-like sweetness.
- **Honey Process (Pulped Natural):** Skin is removed but varying levels of sticky mucilage (Yellow, Red, Black Honey) remain during drying, balancing fruit sweetness with clean acidity.
""",
    ),
    (
        VAULT_KB / "Seiko_NH35_Automatic_Movement_Assembly_Guide.md",
        """# Seiko NH35 Automatic Movement Assembly Guide

## Movement Specifications
- **Manufacturer:** Time Module (TMI) / Seiko Instruments Inc. (SII).
- **Beats Per Hour:** 21,600 bph (3 Hz, 6 ticks per second).
- **Jewels:** 24 Jewels.
- **Power Reserve:** ~41 Hours.
- **Functions:** Manual winding, hacking seconds, quickset date.

## Watch Modding Assembly Steps
1. **Dial Mounting:** Align dial feet into movement plastic spacer and press down squarely.
2. **Hand Setting:**
   - Turn crown until date clicks over to establish midnight (12:00 AM).
   - Press hour hand directly at 12:00.
   - Press minute hand at 12:00, ensuring complete parallel clearance above hour hand.
   - Press second hand gently onto center pinion. Verify hands do not touch each other or crystal.
3. **Casing & Stem Trimming:** Measure winding stem length inside case, trim with end-cutters, file smooth, and secure crown with blue Loctite.
""",
    ),
    (
        VAULT_KB / "Watch_Hand_Setting_and_Dial_Alignment_Tolerances.md",
        """# Watch Hand Setting and Dial Alignment Tolerances

## Precision Hand Setting Clearances
Hands must operate in absolute parallel planes without friction:
- Clearance between Dial and Hour Hand: `0.30 mm`.
- Clearance between Hour Hand and Minute Hand: `0.20 mm`.
- Clearance between Minute Hand and Second Hand: `0.20 mm`.
- Clearance between Second Hand and Sapphire Crystal: `0.30 - 0.50 mm`.

Always use dial protection film and brass or plastic-tipped hand setting press tools to prevent scratching painted dials or luminous indices.
""",
    ),
    (
        VAULT_KB / "PC_Gaming_Frame_Pacing_and_RTX_4060_DLSS3_Tuning.md",
        """# PC Gaming Frame-Pacing and RTX 4060 DLSS 3 Tuning

## Frame Pacing vs Raw FPS
Smooth visual gameplay requires consistent frame time delivery (e.g. 16.6ms for 60Hz, 6.94ms for 144Hz). A game running at 100 FPS with erratic 30ms frame-time spikes will feel stuttery compared to a flat, locked 80 FPS line.

## NVIDIA DLSS 3 & Frame Generation on RTX 4060
The Ada Lovelace RTX 4060 features Optical Flow Accelerators (OFA) that generate intermediate AI frames:
1. **Super Resolution (DLSS 2):** Renders base game at 1080p and reconstructs to 1440p using temporal AI autoencoders.
2. **Frame Generation (DLSS 3):** Inserts synthesized neural frames between rendered frames, doubling perceived refresh rate without taxing CPU bottlenecks.
3. **NVIDIA Reflex:** Bypasses render queue to slash input latency introduced by frame buffers.
""",
    ),
    (
        VAULT_KB / "Power_Nap_Circadian_Cycles_and_Adenosine_Clearance.md",
        """# Power Nap: Circadian Cycles and Adenosine Clearance

## Neuroscience of the Afternoon Power Nap
Sleep pressure is governed by the accumulation of **adenosine** in the basal forebrain during waking hours.
Between 1:00 PM and 3:00 PM, the circadian rhythm experiences a natural post-prandial dip in core body temperature and alertness.

```text
0 - 20 Minutes (Stage 1 & Stage 2 Light Sleep):
Clears neural adenosine receptors, sharpens motor skills, zero sleep inertia!

30 - 60 Minutes (Stage 3 Slow-Wave Deep Sleep):
Causes severe sleep inertia (grogginess) if awakened mid-cycle!

90 Minutes (Full Ultradian Sleep Cycle):
Completes Light -> Slow Wave -> REM sleep. Enhances creative problem-solving and emotional reset.
```

## The Optimal Power Nap Protocol
- **Duration:** Exactly 20 to 25 minutes.
- **Environment:** Cool room (18-20°C), eye mask, white noise.
- **Caffeine Nap Trick:** Drink a shot of espresso immediately before a 20-minute nap. Caffeine takes 20-25 minutes to enter the bloodstream, waking you up right as adenosine is cleared.
""",
    ),
    (
        VAULT_KB / "Flatwound_vs_Roundwound_Bass_Strings_Timbre.md",
        """# Flatwound vs Roundwound Bass Strings Timbre

## String Construction & Acoustic Profiles
- **Roundwound Strings:** Round outer wire wrapped around steel core. High friction, bright harmonic overtones, crisp metallic punch, excellent sustain for rock and slap.
- **Flatwound Strings:** Flattened ribbon wire wrapped tightly around core, polished mirror-smooth. Low finger noise, deep fundamental thud, muted top-end, classic Motown and vintage jazz timbre (P-Bass with La Bella Deep Talkin' Bass flats).
- **Tapewound Strings:** Black nylon outer wrap. Warm acoustic upright bass simulation with ultra-low tension.
""",
    ),
    (
        VAULT_KB / "Bass_Amplifier_Solid_State_vs_Tube_Saturation.md",
        """# Bass Amplifier: Solid-State vs Tube Saturation

## Power Delivery & Harmonic Distortion
- **All-Tube Amplifiers (e.g. Ampeg SVT):** High-voltage tubes (12AX7 preamp, 6550 power tubes) compress naturally when pushed, generating warm second-order harmonic saturation and sag. Extremely heavy (80 lbs) and requires impedance-matched speaker cabinets.
- **Class D Solid-State Amplifiers (e.g. Darkglass, Aguilar Tone Hammer):** Ultra-efficient switch-mode power supplies delivering 500W - 900W in lightweight 5-lb chassis. Features lightning-fast transient response and transparent low-end articulation.
""",
    ),
    (
        VAULT_KB / "Espresso_Channeling_Puck_Prep_WDT_and_Tamping.md",
        """# Espresso Channeling, Puck Prep (WDT), and Tamping

## Fluid Dynamics in Espresso Extraction
Water under 9 bars of pressure seeks the path of least resistance through the coffee bed. Clumps in the ground coffee create micro-fissures (channeling), causing simultaneous sour under-extraction and bitter over-extraction.

## The Optimal Puck Preparation Protocol
1. **Weiss Distribution Technique (WDT):** Use 0.3mm acupuncture needles to stir ground coffee, breaking all electrostatic clumps and homogenizing density.
2. **Puck Screen:** Place a 0.2mm stainless steel mesh screen on top of the bed to evenly distribute shower-screen water flow and keep grouphead clean.
3. **Level Tamping:** Tamp with 20-30 lbs of pressure until the bed is fully compacted. Ensure tamp is perfectly horizontal.
""",
    ),
    (
        VAULT_KB / "Sourdough_Fermentation_Lactobacillus_Kinetics.md",
        """# Sourdough Fermentation and Lactobacillus Kinetics

## Microbial Symbiosis
A wild sourdough starter maintains a balanced culture between wild yeasts (*Saccharomyces exiguus*) and lactic acid bacteria (*Lactobacillus sanfranciscensis*):
- **Wild Yeasts:** Ferment simple sugars into carbon dioxide ($CO_2$), creating dough rise and open crumb structure.
- **Lactobacillus Bacteria:** Metabolize maltose, producing lactic acid (smooth yoghurt-like tang) and acetic acid (sharp vinegar-like punch).
- **Temperature Control:** 21-24°C favors acetic acid development; 26-28°C accelerates lactic acid and rapid enzymatic fermentation.
""",
    ),
    (
        VAULT_KB / "Cast_Iron_Skillet_Polymerization_and_Care.md",
        """# Cast Iron Skillet Polymerization and Care

## Chemistry of Non-Stick Seasoning
Seasoning is not grease or oil; it is a hard, non-stick polymer layer formed through lipid auto-oxidation and thermal polymerization:
1. Apply microscopic layer of high-smoke-point polyunsaturated oil (e.g. Grapeseed or Crisco).
2. Heat past smoke point (230°C / 450°F) for 1 hour.
3. Unsaturated fatty acid carbon-carbon double bonds cross-link into a tough, glass-like thermoset plastic matrix bonded to the porous iron surface.
Wash with warm water and mild dish soap (modern soap does not contain harsh lye and will not strip polymerized seasoning).
""",
    ),
    (
        VAULT_KB / "Mechanical_Keyboard_Switch_Lubrication_Krytox.md",
        """# Mechanical Keyboard Switch Lubrication (Krytox)

## Friction Elimination & Acoustic Tuning
Lubricating mechanical switches eliminates scratchiness and deepens acoustic sound profile ("thock"):
- **Krytox 205g0:** Premium PTFE grease optimal for linear switches (Gateron Ink Black, Cherry MX Black, Oil Kings). Apply ultra-thin coat to stem rails, slider guides, and bottom housing.
- **Krytox GPL 105:** Low-viscosity oil for bag-lubricating switch springs, eliminating ping and spring crunch.
- **TriboSys 3203:** Lighter grease suited for tactile switches (preventing loss of tactile bump).
""",
    ),
    (
        VAULT_KB / "Monitor_Color_Calibration_ICC_Profiles_and_Delta_E.md",
        """# Monitor Color Calibration, ICC Profiles, and Delta E

## Colorimetric Accuracy Standards
- **Color Gamuts:** sRGB (Standard Web), DCI-P3 (Digital Cinema / Modern Display), Adobe RGB (Print Photography).
- **Delta E ($\Delta E$):** Metric measuring perceived difference between displayed color and true reference color:
  - $\Delta E < 1.0$: Imperceptible to the human eye.
  - $\Delta E < 2.0$: Professional color-grading threshold.
  - $\Delta E > 3.0$: Noticeable color shift.
- **Calibration Protocol:** Calibrate using hardware colorimeter (Calibrite Display Plus HL / Datacolor Spyder) targeting D65 white point (6500K) and 2.2 gamma curve at 120 cd/m² luminance.
""",
    ),
    (
        VAULT_KB / "Soldering_Iron_Temperature_Profiles_and_Flux_Types.md",
        """# Soldering Iron Temperature Profiles and Flux Types

## Metallurgy of Electronics Soldering
- **Lead-Free Solder (SAC305 - 96.5% Sn, 3.0% Ag, 0.5% Cu):** Melting point 217°C (422°F). Target iron temperature: `330°C to 350°C`.
- **Leaded Solder (63/37 Sn/Pb):** Eutectic melting point 183°C (361°F). Target iron temperature: `300°C to 320°C`.

## Flux Chemistry
Flux strips surface oxidation from copper traces and pins, reducing surface tension so molten solder flows smoothly:
- **RMA (Rosin Mildly Activated):** Reliable for general electronics; benign non-conductive residue.
- **No-Clean Flux:** Leaves low residue, suitable for surface-mount components.
- **Water-Soluble Flux:** Aggressive cleaning; residue must be thoroughly washed with deionized water to prevent corrosion.
""",
    ),
    (
        VAULT_KB / "Desk_Cable_Management_and_Ground_Loop_Isolation.md",
        """# Desk Cable Management and Ground Loop Isolation

## Eliminating Audio Hum and Electromagnetic Interference
- **Ground Loops:** Occur when multiple audio devices (PC, audio interface, monitor speakers, bass amp) are grounded through different electrical pathways, creating circular AC current loops that produce a constant 60 Hz / 50 Hz buzz.
- **Solution:** Power all desk gear from a single high-quality surge-protected power distribution unit (PDU) and insert galvanic isolation transformers (DI Box with Ground Lift switch) between audio line outs.
- **Cable Separation:** Keep AC power cables physically perpendicular or separated by at least 4 inches from low-voltage audio and signal cables to prevent 60Hz induction hum.
""",
    ),
    (
        VAULT_KB / "Ergonomic_Lumbar_Support_and_Desk_Height_Geometry.md",
        """# Ergonomic Lumbar Support and Desk Height Geometry

## Biomechanics of Extended Desk Sessions
1. **Elbow Angle:** Forearms parallel to floor at 90-100° angle with wrists in neutral position (no upward extension against keyboard).
2. **Monitor Height:** Top third of monitor screen at eye level, roughly 20-28 inches away.
3. **Lumbar Curve:** Active lumbar support maintaining natural lordotic curve of lower spine, distributing body weight across ischial tuberosities (sit bones) rather than sacrum.
4. **Foot Placement:** Feet flat on floor or angled footrest, thighs horizontal to floor to promote venous blood return.
""",
    ),
    (
        VAULT_KB / "Sleep_Hygiene_REM_Stages_and_Cognitive_Recovery.md",
        """# Sleep Hygiene, REM Stages, and Cognitive Recovery

## Sleep Architecture and Memory Consolidation
A full night's sleep consists of 4 to 6 repeating 90-minute ultradian cycles:
- **NREM Stage 3 (Slow-Wave Deep Sleep):** Physical cellular repair, growth hormone release, and glymphatic brain clearance (washing out amyloid-beta plaques).
- **REM (Rapid Eye Movement Sleep):** Emotional regulation, associative learning, creative problem-solving, and procedural memory consolidation.

## High-Performance Sleep Rules
1. **Light Exposure:** 10 minutes of direct outdoor morning sunlight within 30 minutes of waking to anchor the suprachiasmatic nucleus (circadian clock).
2. **Screen Curfew:** Blue-light blocking glasses or warm night-shift displays 2 hours before bed to allow natural melatonin synthesis.
3. **Temperature Drop:** Cool bedroom (18°C / 65°F) triggers natural internal core-temperature drop required for deep sleep entry.
""",
    )
]


def write_notes():
    count = 0
    print("=" * 70)
    print("      JESSICA SECOND BRAIN: 64-NOTE NAP EXPANSION MARATHON")
    print("=" * 70)

    for path, content in NOTES_DATA:
        clean_content = content.strip() + "\n"
        path.write_text(clean_content, encoding="utf-8")
        count += 1
        print(f"[{count:02d}/64] Written: {path.name}")

    print(f"\n[+] Successfully created all {count} deep knowledge notes.")


def reindex_vault():
    print("\n[*] Re-indexing full Obsidian knowledge vault into 32GB RAM...")
    from brain.vault_indexer import VaultIndexer
    indexer = VaultIndexer()
    total_docs = len(indexer.documents)
    print(f"[+] Re-indexing complete: {total_docs} Markdown documents indexed!")
    assert total_docs >= 150, f"Expected at least 150 documents, got {total_docs}"
    print("[+] Vault expansion verified: Second Brain now holds 150+ deep knowledge notes!")


if __name__ == "__main__":
    write_notes()
    reindex_vault()
