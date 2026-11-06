# FortiGate Firewall Policies and FortiOS CLI Troubleshooting

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
