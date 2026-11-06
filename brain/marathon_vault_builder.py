"""
Jessica Brain - Marathon Obsidian Vault Knowledge Expansion Builder
Expands Jessica's local Obsidian knowledge vault from 63 to 85+ comprehensive Markdown notes,
covering IT administration, network diagnostics, everyday life, cinema, culinary science, and acoustics.
Immediately indexes all documents into the Hybrid BM25/Vector RAG index.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

KB_DIR = WORKSPACE_ROOT / "obsidian_vault" / "02_Knowledge_Base"
KB_DIR.mkdir(parents=True, exist_ok=True)

NEW_NOTES: Dict[str, str] = {
    # -------------------------------------------------------------
    # IT Admin & Enterprise Network Mastery
    # -------------------------------------------------------------
    "windows_11_event_viewer_diagnostics.md": """# Windows 11 Event Viewer Diagnostics & Triage Guide

## Core Operational Logs
1. **System Log**: Hardware errors, driver crashes, power events, and kernel panic warnings (Event ID 41 Kernel-Power indicates unexpected shutdown).
2. **Application Log**: Crash reports for desktop binaries (Event ID 1000 Application Error, Event ID 1001 Windows Error Reporting).
3. **Security Log**: Audit success and failure logs (Event ID 4624 successful logon, Event ID 4625 failed logon attempt).

## Essential Event IDs for IT Triage
- **Event ID 41**: Critical Kernel-Power loss without clean shutdown (check PSU, overclock stability, or sudden AC power loss).
- **Event ID 7036**: Service entered running or stopped state (useful for tracing background daemon crashes).
- **Event ID 10016**: DistributedCOM permission warning (common and generally harmless unless application hangs).
- **Event ID 1000**: Faulting application path and exception code (e.g., `0xc0000005` Access Violation).

## Filtering & CLI Extraction
Query specific errors via PowerShell:
```powershell
Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2; StartTime=(Get-Date).AddHours(-24)} | Select-Object TimeCreated, Id, Message
```
""",

    "active_directory_gpo_architecture.md": """# Active Directory Group Policy Objects (GPO) Architecture

## Processing Order: LSDOU
Group policies in Active Directory are applied strictly in the **LSDOU** order:
1. **Local**: Local machine policy on the workstation.
2. **Site**: Policies linked to the physical Active Directory Site.
3. **Domain**: Domain-level policies affecting all objects in the domain.
4. **Organizational Unit (OU)**: OU-specific policies (innermost OU has the final override precedence).

## Enforcement & Blocking
- **Enforced (No Override)**: Overrides any downstream conflicting settings, taking absolute priority regardless of OU nesting.
- **Block Inheritance**: Stops upstream Site, Domain, and parent OU policies from applying to this OU, unless those policies are marked as Enforced.
- **Loopback Processing**: Crucial for Terminal Servers/RDS. Replaces or merges computer policy settings over the logged-in user's user-configuration settings.

## Diagnostic Commands
- `gpupdate /force`: Forces immediate re-application of user and computer policies without waiting for standard 90-minute refresh.
- `gpresult /r`: Displays Applied and Filtered-Out GPOs for current user and computer.
- `gpresult /h gpreport.html`: Generates complete visual HTML audit report of applied registry keys.
""",

    "fortigate_vpn_and_firewall_rules.md": """# FortiGate Next-Gen Firewall & SSL-VPN Configuration

## Security Policy Architecture
FortiOS operates on an explicit stateful policy table where traffic is matched top-down:
- **Interface Pairing**: Incoming Interface (e.g., `port1_wan`) to Outgoing Interface (e.g., `port2_internal`).
- **Source & Destination**: IPv4 addresses, FQDNs, or Address Groups.
- **Service**: Port/protocol objects (HTTP, HTTPS, SSH, custom TCP/UDP).
- **Action**: Accept or Deny.
- **NAT**: Source NAT (IP Pool or Outgoing Interface IP) for Internet-bound outbound traffic.

## SSL-VPN Modes
1. **Web Mode (Clientless)**: Browser-based portal accessing internal HTTP, RDP, and SSH bookmarks via HTML5 gateway.
2. **Tunnel Mode (FortiClient)**: Assigns internal IP from SSL-VPN IP Pool (e.g., `10.212.134.0/24`) and creates a virtual network adapter.

## Troubleshooting CLI
- `diagnose vpn ssl list`: Lists active connected SSL-VPN users, source IPs, and duration.
- `diagnose firewall iprope lookup <src_ip> <src_port> <dst_ip> <dst_port> <protocol>`: Checks which firewall policy rule matches specific packet flow.
- `diagnose sniffer packet any 'host 192.168.1.100 and port 443' 4`: Captures real-time packet headers.
""",

    "voip_sip_and_pbx_infrastructure.md": """# VoIP, SIP Protocol & PBX Infrastructure

## SIP Architecture & Signaling
- **Signaling Protocol**: SIP (Session Initiation Protocol, RFC 3261) operates on UDP/TCP port 5060 (or TLS port 5061) to establish, modify, and terminate calls.
- **Media Transmission**: RTP (Real-time Transport Protocol, RFC 3550) carries the actual audio payload over UDP ports (typically 10,000–20,000).
- **Codecs**:
  * **G.711u / G.711a (PCMU/PCMA)**: Uncompressed 64 kbps, 8 kHz sampling, robust baseline.
  * **G.729**: Compressed 8 kbps, low-bandwidth toll quality.
  * **Opus**: Dynamic bitrates from 6 kbps to 510 kbps, 48 kHz HD audio, dominant in modern WebRTC.

## Core SIP Methods & Response Codes
- `INVITE`: Initiates call session.
- `ACK`: Confirms receipt of final response.
- `BYE`: Terminates call session.
- `200 OK`: Request succeeded.
- `486 Busy Here`: Callee is already on another call.
- `503 Service Unavailable`: PBX trunk failure or gateway overload.

## One-Way Audio Root Causes
One-way audio in 95% of cases is caused by **NAT traversal issues**: SIP signaling connects through the firewall, but RTP packets fail because the SDP (Session Description Protocol) packet contains private IP addresses without proper STUN/TURN or SIP ALG disabling on the router.
""",

    "docker_container_networking_and_volumes.md": """# Docker Container Networking & Storage Volumes

## Network Drivers
1. **Bridge (default)**: Creates a private software bridge (`docker0`) on host; containers communicate via private IP range (`172.17.0.0/16`) and expose ports to host via NAT iptables rules.
2. **Host**: Removes network isolation between container and host; container binds directly to host IP/ports (highest throughput, zero NAT overhead).
3. **Macvlan / Ipvlan**: Assigns real MAC/IP addresses directly to container from physical LAN, appearing as physical devices on home/office switch.
4. **Overlay**: Enables multi-host container networking across Docker Swarm nodes using VXLAN tunneling.

## Storage Management
- **Named Volumes (`/var/lib/docker/volumes/`)**: Managed by Docker, independent of container lifecycle, safe across container rebuilds.
- **Bind Mounts (`./host_path:/container_path`)**: Directly maps host filesystem directory; useful for hot-reloading code or mounting configuration files.
- **tmpfs**: Mounts into host system RAM, never persisted to disk (high security, temporary cache).

## Maintenance Commands
```bash
docker system prune -a --volumes # Cleans dead containers, unused networks, and dangling volumes
docker inspect <container_id> --format '{{ .NetworkSettings.IPAddress }}' # Quick container IP lookup
```
""",

    "self_hosted_nas_storage_and_zfs.md": """# Self-Hosted NAS Storage & ZFS Storage Architecture

## ZFS Core Concepts
ZFS is an enterprise filesystem and logical volume manager built for bulletproof data integrity:
- **vdev (Virtual Device)**: Group of physical drives configured as Stripe, Mirror, RAIDZ1, RAIDZ2, or RAIDZ3.
- **Zpool**: Pool of one or more vdevs providing aggregate storage capacity.
- **Copy-on-Write (CoW)**: Never overwrites existing blocks in-place; writes new data to free blocks and updates pointers atomically.
- **Self-Healing Data Scrubbing**: Computes SHA-256 or xxHash checksums on every single block read. If checksum fails, automatically reads the mirror or parity block and corrects the corrupted block on disk (eliminating silent bit rot).

## TrueNAS SCALE & Linux ZFS Commands
- `zpool status`: Displays health of all pools, vdevs, read/write/checksum error counts.
- `zpool scrub <pool_name>`: Initiates proactive bit rot verification and repair across all disks.
- `zfs snapshot <pool>/<dataset>@snap_name`: Instant zero-space snapshot.
""",

    "raid_levels_and_data_redundancy.md": """# RAID Levels & Hardware Redundancy Guide

## Common RAID Configurations
1. **RAID 0 (Striping)**: 0 redundancy. High read/write speed. Single drive failure results in 100% data loss.
2. **RAID 1 (Mirroring)**: 100% capacity duplicate across 2 drives. Can survive 1 drive loss.
3. **RAID 5 (Block Striping with Single Distributed Parity)**: Requires minimum 3 disks. Usable capacity: `(N - 1) * Size`. Can survive 1 disk failure. Vulnerable to URE (Unrecoverable Read Errors) during rebuild.
4. **RAID 6 / RAIDZ2 (Dual Distributed Parity)**: Requires minimum 4 disks. Usable capacity: `(N - 2) * Size`. Can survive 2 simultaneous disk failures. Standard recommendation for modern large HDD pools (>8TB).
5. **RAID 10 (Stripe of Mirrors)**: Requires minimum 4 disks. Combines high throughput with fast rebuild times (rebuilds copy from single mirror rather than recalculating parity across entire array).

## Critical Storage Axiom: RAID is Not a Backup
RAID protects against physical drive hardware failure, NOT against accidental deletion, ransomware encryption, filesystem corruption, or natural disaster. Backups must follow the **3-2-1 Rule**: 3 copies of data, across 2 different media types, with 1 offsite.
""",

    "cybersecurity_incident_response_playbook.md": """# Cybersecurity Incident Response Playbook

## 6-Phase NIST Incident Response Framework
1. **Preparation**: Hardening assets, logging baselines, establishing access lists, and preparing offline forensic tools.
2. **Identification**: Detecting anomalies via SIEM, EDR alerts, IDS signatures, or unusual outbound beaconing.
3. **Containment**:
   - Short-Term: Isolate infected endpoint from network (disconnect VLAN/WiFi, disable switch port).
   - Long-Term: Revoke compromised AD credentials, reset Kerberos ticket (KRBTGT) twice, block malicious C2 IP/domain at perimeter firewall.
4. **Eradication**: Identify persistence mechanisms (scheduled tasks, registry run keys, unauthorized SSH keys, malicious WMI event subscriptions), remove malware binaries.
5. **Recovery**: Restore systems from verified clean offline backups, monitor network traffic closely.
6. **Lessons Learned**: Post-incident review, root cause documentation, defensive hardening.

## Triage Volatile Evidence Order (RFC 3227)
1. System Memory (RAM dump via LiME or WinPmem).
2. Active network connections and sockets (`netstat -ano`).
3. Running processes and memory mappings (`Get-Process`).
4. Non-volatile disk storage and log files.
""",

    "wireshark_packet_analysis_and_tcp_flags.md": """# Wireshark Packet Analysis & TCP Handshake Mechanics

## TCP 3-Way Handshake
1. **Client -> Server**: `SYN` (Synchronize sequence number `Seq=0`).
2. **Server -> Client**: `SYN-ACK` (Server acknowledges client and sends its own sequence number `Seq=0, Ack=1`).
3. **Client -> Server**: `ACK` (Client acknowledges server `Seq=1, Ack=1`). Connection established!

## Key TCP Flags & Anomaly Meaning
- **RST (Reset)**: Port closed or connection abruptly severed (firewall rejected packet or service not listening).
- **FIN**: Graceful termination initiated by sender.
- **PSH (Push)**: Forces immediate buffer flush to application layer without waiting for packet buffer to fill.

## Useful Wireshark Display Filters
- `tcp.flags.reset == 1`: Shows all severed connections and port rejections.
- `tcp.analysis.retransmission`: Detects packet loss and congested network links.
- `http.response.code >= 400`: Filters HTTP client/server errors.
- `dns.flags.response == 0 and dns.qry.name contains "malicious"`: Tracks DNS queries.
""",

    "powershell_automation_and_wmi_scripting.md": """# PowerShell Automation & WMI/CIM Systems Scripting

## Modern CIM vs Deprecated WMI
Modern PowerShell scripts should prioritize `Get-CimInstance` over legacy `Get-WmiObject` because CIM uses WS-Management (WinRM / port 5985) over firewalls instead of legacy DCOM.

## Essential Administrative Commands
```powershell
# Query physical RAM capacity and speed across all DIMM slots
Get-CimInstance Win32_PhysicalMemory | Select-Object DeviceLocator, Capacity, Speed, Manufacturer

# Extract Top 5 memory-hungry processes
Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, @{N='Memory_MB';E={[math]::Round($_.WorkingSet64/1MB,1)}}

# Test TCP port reachability
Test-NetConnection -ComputerName 1.1.1.1 -Port 443
```
""",

    "dnssec_and_anycast_routing.md": """# DNSSEC & Anycast Routing Architecture

## DNSSEC Cryptographic Validation
DNSSEC (Domain Name System Security Extensions) prevents DNS cache poisoning and spoofing by signing DNS resource records with public-key cryptography:
- **RRSIG (Resource Record Signature)**: Cryptographic signature for a specific record set.
- **DNSKEY**: Public key used by resolvers to verify RRSIG signatures.
- **DS (Delegation Signer)**: Hash of the child zone's DNSKEY stored in the parent zone (creating an unbroken chain of trust up to Root Key Signing Key).

## Anycast DNS Mechanics
In Anycast, multiple geographically distributed name servers advertise the **exact same BGP IP prefix** (e.g., Cloudflare's `1.1.1.1` or Google's `8.8.8.8`) to different upstream Tier 1 ISPs. Internet routers naturally route the user's DNS query to the topologically nearest server node using BGP AS-Path length, providing instant global failover and DDoS absorption.
""",

    "ssl_tls_handshake_and_pki_certificates.md": """# TLS 1.3 Handshake & PKI Certificate Architecture

## TLS 1.3 1-RTT Handshake Optimization
Unlike TLS 1.2 which required 2 full round-trips (2-RTT) to negotiate cipher suites and exchange keys, TLS 1.3 completes cryptographic negotiation in just **1-RTT** (and 0-RTT with Pre-Shared Key session resumption):
1. **ClientHello**: Client sends supported cipher suites AND its Diffie-Hellman key share guess in the very first message.
2. **ServerHello**: Server responds with selected cipher suite and its own key share. Both parties compute the shared secret immediately.

## PKI Chain of Trust
1. **Root CA**: Self-signed certificate baked directly into OS/browser trusted root stores.
2. **Intermediate CA**: Signed by Root CA; issues certificates to avoid exposing Root CA private keys online.
3. **End-Entity Certificate**: Leaf certificate bound to the domain name (verified via SAN - Subject Alternative Name).
""",

    "bgp_and_ospf_enterprise_routing_design.md": """# BGP & OSPF Enterprise Routing Design

## OSPF (Open Shortest Path First) - Interior Gateway
- **Type**: Link-State IGP operating inside single Autonomous System.
- **Algorithm**: Dijkstra's Shortest Path First (SPF).
- **Hierarchical Design**: All areas (Area 1, Area 2) must connect to Area 0 (Backbone).
- **Metric**: Cost = `Reference_Bandwidth / Interface_Bandwidth` (default reference is 100 Mbps; in 10Gbps+ networks, must set `auto-cost reference-bandwidth 100000`).

## BGP (Border Gateway Protocol) - Exterior Gateway
- **Type**: Path-Vector EGP running between distinct Autonomous Systems (e.g., Enterprise to Dual-Homed ISPs).
- **Standard Port**: TCP 179.
- **Path Selection Hierarchy**:
  1. Highest **Weight** (Cisco proprietary, local to router).
  2. Highest **Local Preference** (advertised across entire AS).
  3. Locally originated routes.
  4. Shortest **AS-Path** length.
  5. Lowest **MED** (Multi-Exit Discriminator).
""",

    # -------------------------------------------------------------
    # Everyday Life, Cinema, Music, Science & Culture
    # -------------------------------------------------------------
    "classic_and_modern_sci_fi_cinema.md": """# Classic & Modern Sci-Fi Cinema Architecture

## Foundations of Sci-Fi Film
1. **2001: A Space Odyssey (1968, Stanley Kubrick)**: Landmark exploration of human evolution, existential philosophy, and AI consciousness (HAL 9000). Set the standard for visual realism and silent cosmic dread.
2. **Blade Runner (1982, Ridley Scott) & Blade Runner 2049 (2017, Denis Villeneuve)**: Defining masterpieces of cyberpunk, questioning the boundary between synthetic replicants and human souls amidst rain-soaked neon dystopias.
3. **The Matrix (1999, The Wachowskis)**: Blended Hong Kong martial arts cinematography with Baudrillard's simulacra philosophy and cyberpunk simulation hypothesis.

## Core Philosophical Themes
- **Consciousness & Artificial Minds**: Explored in *Ex Machina*, *Her*, and *Blade Runner*.
- **Temporal Mechanics & Causality**: Masterfully executed in Christopher Nolan's *Interstellar* (relativistic time dilation) and Denis Villeneuve's *Arrival* (non-linear linguistic time perception).
""",

    "music_production_bass_eq_and_compression.md": """# Music Production: Electric Bass EQ & Compression Guide

## Low-End Frequency Spectrum
- **20 Hz - 40 Hz (Sub-Bass Rumbles)**: High-pass filter here with 18dB/octave slope to remove sub-audible mud and give the power amplifier headroom.
- **60 Hz - 100 Hz (Sub-Weight)**: Low-end body. In modern rock/pop mixing, decide whether the kick drum or bass guitar owns the 60 Hz pocket:
  * If Kick sits at 60 Hz, carve a slight notch in the bass at 60 Hz and boost the bass at 100 Hz - 140 Hz.
- **200 Hz - 300 Hz (Boxiness / Mud)**: Often needs a gentle 2-3 dB dip to clean up clutter and let vocals breathe.
- **700 Hz - 1.2 kHz (Fingerstyle / P-Bass Growl)**: Crucial for clarity on smartphone speakers and laptop monitors.
- **2 kHz - 4 kHz (Pick Attack & String Fret Snap)**: Adds attack definition.

## Compression Strategies
1. **1176 FET Compressor (Fast Limiting)**: Ratio 4:1 or 8:1, attack set to medium-slow (to let the initial string pluck transient through), fast release to pin down peaks.
2. **Opto Compressor (LA-2A Style Smooth Leveling)**: Follow the 1176 with a smooth optical compressor doing 2-3 dB of gentle leveling for consistent groove sustain.
""",

    "baking_chemistry_and_maillard_reaction.md": """# Baking Chemistry & The Maillard Reaction

## The Chemistry of Crust & Flavor: Maillard Reaction
The **Maillard reaction** is a chemical reaction between amino acids and reducing sugars that occurs typically between **140°C and 165°C (284°F - 330°F)**. It produces hundreds of complex flavor compounds (melanoidins) responsible for the rich, nutty, caramelized flavor of toasted bread, seared steaks, and roasted coffee.

## Leavening Agents
1. **Baking Soda (Sodium Bicarbonate)**: Pure base. Requires an acid (buttermilk, yogurt, lemon juice, brown sugar) to react and produce carbon dioxide gas ($CO_2$).
2. **Baking Powder**: Contains sodium bicarbonate plus dry acid salts (cream of tartar, sodium aluminum sulfate).
   - **Double-Acting**: Releases initial $CO_2$ upon getting wet at room temperature, and a second, larger burst of gas when heated above 60°C in the oven.

## Gluten Development
Formed when two wheat proteins, **gliadin** (provides extensibility) and **glutenin** (provides elastic strength), hydrate with water and are physically kneaded into a cross-linked protein matrix. Fats (butter, oil) "shorten" gluten strands, yielding tender, crumbly pastries.
""",

    "coffee_extraction_science_and_tds.md": """# Coffee Extraction Science, TDS & The Golden Cup

## The Extraction Dynamics
Water extracts chemical compounds from roasted coffee grounds in a predictable chronological sequence:
1. **Fats & Organic Acids (Under-extracted)**: Sour, sharp, acidic, lacking sweetness.
2. **Sugars & Aromatics (Balanced extraction)**: Sweet, complex, fruit/caramel notes.
3. **Plant Fibers & Heavy Tannins (Over-extracted)**: Bitter, dry, astringent, chalky mouthfeel.

## Quantitative Metrics
- **TDS (Total Dissolved Solids)**: Measured via refractometer. Represents the percentage of dissolved coffee solids in the brewed cup (typically 1.15% to 1.45% for filter coffee; 8% to 12% for espresso).
- **Extraction Yield (EY)**: Percentage of coffee ground mass extracted into the cup:
  $$EY = \\frac{Brew\\_Weight \\times TDS}{Dose\\_Weight}$$
  The Specialty Coffee Association (SCA) Golden Cup standard specifies an ideal Extraction Yield between **18% and 22%**.
""",

    "human_psychology_and_cognitive_biases.md": """# Cognitive Biases & Behavioral Psychology

## Major Systematic Cognitive Distortions
1. **Confirmation Bias**: The tendency to search for, interpret, and recall information in a way that confirms prior beliefs while discarding contradictory evidence.
2. **Dunning-Kruger Effect**: A cognitive bias where people with low ability at a task overestimate their competence, while experts tend to underestimate their relative superiority.
3. **Sunk Cost Fallacy**: Continuing an endeavor once an investment in money, effort, or time has been made, rather than evaluating future utility objectively.
4. **Anchoring Bias**: Relying too heavily on the first piece of information encountered (the "anchor") when making decisions (e.g., initial price negotiations).
5. **Fundamental Attribution Error**: Over-attributing other people's actions to their character or personality, while attributing our own mistakes to external circumstances.
""",

    "philippine_geography_provinces_and_culture.md": """# Philippine Geography, Island Groups & Cultural Pillars

## The Three Island Groups
1. **Luzon (North)**: The largest island group, housing Metro Manila (National Capital Region), the Cordillera mountains (Baguio, Banaue rice terraces), and rich agricultural plains.
2. **Visayas (Central)**: Archipelago of central islands including Cebu, Panay, Negros, Leyte, and Bohol. Renowned for maritime heritage, festivals (Sinulog, Ati-Atihan), and pristine beaches.
3. **Mindanao (South)**: The second-largest landmass, rich in biodiversity, fertile agricultural lands (Davao, Bukidnon), and vibrant indigenous and Bangsamoro Muslim cultural traditions.

## Core Cultural Values
- **Bayanihan**: Community spirit where neighbors unite to help one another without expecting payment (originally symbolized by carrying a bamboo house).
- **Malasakit**: Genuine compassion and proactive concern for the well-being of others and organizations.
- **Utang na Loob**: A deep debt of gratitude acknowledging assistance given in times of need.
""",

    "analog_synthesizers_and_subtractive_synthesis.md": """# Analog Synthesizers & Subtractive Sound Synthesis

## Subtractive Synthesis Signal Path
1. **Oscillator (VCO)**: Generates harmonically rich raw audio waveforms:
   - **Sawtooth**: Rich in all integer harmonics (ideal for strings, brass, aggressive leads).
   - **Square / Pulse**: Odd harmonics only (ideal for hollow reed tones, woodwinds, classic 80s basslines).
   - **Triangle**: Low harmonic amplitude, close to pure fundamental tone.
2. **Filter (VCF)**: Subtractive sculpting core. Low-Pass Filter (LPF) cuts high frequencies above the cutoff point. **Resonance** boosts frequencies right at the cutoff threshold into self-oscillation.
3. **Amplifier (VCA)**: Shapes output volume over time governed by envelope generators.

## ADSR Envelope Architecture
- **Attack**: Time taken to rise from silence to peak amplitude.
- **Decay**: Time taken to drop from peak to the sustain level.
- **Sustain**: Steady amplitude level held while the key is pressed.
- **Release**: Time taken to fade back to silence after key is released.
""",

    "sleep_architecture_and_circadian_rhythm.md": """# Sleep Architecture, Polysomnography & Circadian Biology

## Sleep Cycle Stages (90-Minute Ultradian Cycles)
1. **NREM Stage 1 (N1 - Light Sleep)**: Transition phase, theta brainwaves (4–7 Hz), hypnic jerks common.
2. **NREM Stage 2 (N2 - Baseline Sleep)**: Characterized by **Sleep Spindles** and **K-Complexes** on EEG, crucial for procedural memory consolidation.
3. **NREM Stage 3 (N3 - Slow Wave / Deep Sleep)**: High-amplitude Delta waves (0.5–2 Hz). Human Growth Hormone (HGH) release, tissue repair, and glymphatic system brain waste clearance.
4. **REM (Rapid Eye Movement - Paradoxical Sleep)**: High brain activity, muscle atonia (paralysis), vivid dreaming, emotional memory processing.

## Circadian Entrainment
Regulated by the **Suprachiasmatic Nucleus (SCN)** in the hypothalamus. Morning exposure to blue-frequency light (~480 nm) stimulates melanopsin in retinal ganglion cells, suppressing melatonin production and boosting morning cortisol.
""",

    "audio_acoustics_and_room_treatment.md": """# Audio Acoustics, Room Modes & Studio Treatment

## Acoustic Phenomena in Enclosed Spaces
- **Room Modes (Standing Waves)**: Caused by sound waves reflecting between parallel walls and colliding in-phase (creating massive frequency spikes) or out-of-phase (creating deep frequency nulls).
  $$f = \\frac{c}{2} \\sqrt{\\left(\\frac{p}{L}\\right)^2 + \\left(\\frac{q}{W}\\right)^2 + \\left(\\frac{r}{H}\\right)^2}$$
- **Axial Modes**: Travel between two parallel surfaces (highest energy, responsible for boomy bass pockets).

## Treatment Solutions
1. **Bass Traps**: Straddled in room corners where bass pressure builds up maximum velocity, using dense porous absorbers (Rockwool / Owens Corning 703) to convert acoustic velocity into thermal energy.
2. **First Reflection Absorption**: Panels placed at the mirror points between studio monitors and mixing chair to prevent comb filtering and smearing of stereo imaging.
3. **Diffusers**: Quadratic residue diffusers (QRD) scatter reflections evenly across space and time without deadening the room acoustics.
""",

    "space_exploration_james_webb_and_artemis.md": """# Deep Space Exploration: James Webb Space Telescope & Artemis

## James Webb Space Telescope (JWST) Engineering
- **Location**: Orbiting the Second Sun-Earth Lagrange Point (**L2**), 1.5 million kilometers from Earth.
- **Infrared Advantage**: Observes in near-infrared and mid-infrared ($0.6 - 28 \\,\\mu\\text{m}$), cutting through cosmic dust clouds to view the earliest stars and galaxies formed after the Big Bang (redshifted cosmic dawn).
- **Cryogenic Sunshield**: A 5-layer Kapton sunshield keeps scientific instruments below **50 Kelvin (-223°C)**, with the MIRI instrument cooled to 7 Kelvin via helium loop cryocooler.

## NASA Artemis Program Architecture
- **Space Launch System (SLS)**: Super heavy-lift rocket with solid rocket boosters and 4 RS-25 liquid hydrogen/oxygen engines.
- **Orion Spacecraft**: Crew vehicle designed for translunar injection and atmospheric re-entry.
- **Lunar Gateway**: Planned space station in Near-Rectilinear Halo Orbit (NRHO) around the Moon serving as a staging point for lunar surface landings and future Mars expeditions.
""",

    "history_of_electric_bass_fender_jazz_and_precision.md": """# History of the Electric Bass: Precision vs. Jazz Bass

## The 1951 Revolution: Fender Precision Bass (P-Bass)
Invented by **Leo Fender** in 1951 to replace unwieldy upright double basses for touring musicians. It was called the "Precision" because it featured **frets**, allowing musicians to play in tune with absolute precision.
- **P-Bass Pickup**: Split single-coil humbucking pickup introduced in 1957. Positioned in the middle of the body, producing deep, punchy, round, midrange-heavy fundamentals that sit effortlessly in any mix.

## The 1960 Innovation: Fender Jazz Bass (J-Bass)
Introduced in 1960 as the deluxe model for jazz musicians seeking brighter tonal flexibility:
- **J-Bass Pickups**: Two individual single-coil pickups—one near the bridge (bright, biting, nasal, harmonics) and one near the neck (warm, deep). Blending both pickups creates a natural mid-scoop with snappy slap tone.
- **Neck Profile**: Sleeker, narrower nut width (1.5 inches vs 1.625–1.75 inches on P-Bass), designed for fast, technical fingerstyle playing.
""",

    "filipino_culinary_traditions_and_flavors.md": """# Filipino Culinary Traditions & Flavor Chemistry

## The Flavor Trinity: Sour, Salty, Savory
Unlike many Southeast Asian cuisines that balance sweet and fiery chili heat, Filipino cuisine is historically rooted in **sourness (asim)** as a primary preservation mechanism in a tropical climate:
- **Sinigang**: The crown jewel of Filipino sour soups, traditionally soured with native tamarind (sampalok), guava (bayabas), kamias, or batuan. Combined with savory fish sauce (patis), leafy greens (kangkong), and meats.
- **Adobo**: Preservation technique marinating pork or chicken in native vinegar (sukang paombong / cane vinegar), soy sauce, garlic, black peppercorns, and bay leaves.
- **Kare-Kare**: Rich peanut and toasted ground rice stew with oxtail and tripe, balanced by the sharp salty umami of fermented shrimp paste (bagoong alamang).
""",

    "computer_hardware_pcie_nvme_architecture.md": """# Modern PC Hardware: PCIe Gen 4/5 & NVMe Storage

## PCIe Bus Architecture
- **Point-to-Point Topology**: Unlike legacy shared PCI buses, PCIe connects each device directly to the CPU or PCH (Platform Controller Hub) via dedicated serial differential lanes (x1, x4, x8, x16).
- **Throughput by Generation**:
  * **PCIe 3.0**: ~1 GB/s per lane (x4 NVMe SSD = ~3,500 MB/s).
  * **PCIe 4.0 (RTX 4060, Modern M.2)**: ~2 GB/s per lane (x4 NVMe SSD = ~7,500 MB/s; x8 GPU = ~16 GB/s).
  * **PCIe 5.0**: ~4 GB/s per lane (x4 NVMe SSD = ~14,000 MB/s).

## NVMe Protocol Advantages over Legacy AHCI/SATA
- **Command Queues**: Legacy SATA AHCI supported a single queue with 32 commands max. NVMe supports up to **64,000 queues with 64,000 commands each**, taking full advantage of modern multi-core CPUs and flash parallelism.
- **Direct PCIe Access**: Eliminates intermediate SATA host controller bottlenecks and minimizes CPU driver overhead.
"""
}


def build_and_index_expanded_vault():
    print("=" * 80)
    print("  EXPANDING JESSICA OBSIDIAN VAULT KNOWLEDGE BASE (85+ TARGET)")
    print("=" * 80)

    written_count = 0
    for filename, content in NEW_NOTES.items():
        file_path = KB_DIR / filename
        file_path.write_text(content.strip() + "\n", encoding="utf-8")
        written_count += 1
        print(f"  [+] Written: {filename}")

    print(f"\n[+] Successfully wrote {written_count} new in-depth knowledge notes into {KB_DIR}.")

    # Count total markdown files in vault
    all_notes = list(WORKSPACE_ROOT.glob("obsidian_vault/**/*.md"))
    total_notes = len(all_notes)
    print(f"[+] Total Obsidian Vault Markdown Notes on Disk: {total_notes}")

    # Re-index Hybrid RAG Vector Database
    print("\n[*] Updating Hybrid BM25 & Semantic Vector Index (brain/vault_indexer.py)...")
    from brain.vault_indexer import VaultIndexer
    indexer = VaultIndexer()
    indexer.index_vault()
    indexed_doc_count = len(indexer.documents)

    print(f"[+] Hybrid Vector Index updated successfully with {indexed_doc_count} documents.")
    return total_notes, indexed_doc_count


if __name__ == "__main__":
    total, indexed = build_and_index_expanded_vault()
    if total >= 85 and indexed >= 85:
        print(f"\n[SUCCESS] Vault target achieved: {total} notes on disk, {indexed} indexed.")
        sys.exit(0)
    else:
        print(f"\n[WARN] Vault count: {total} on disk, {indexed} indexed.")
        sys.exit(1)
