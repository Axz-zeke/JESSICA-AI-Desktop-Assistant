# eBPF and XDP High Speed Packet Processing Architecture

## 1. Extended Berkeley Packet Filter (eBPF)
- An in-kernel virtual machine in Linux that executes sandboxed bytecode at designated hook points without modifying kernel source code or loading external kernel modules.
- Verification engine performs static code analysis ensuring memory safety, loop bounds, and bounded runtime before code executes.
- Intercepts system calls, network tracepoints, tracepoints, and perf events with near-zero overhead.

## 2. eXpress Data Path (XDP)
- Executes eBPF bytecode at the lowest level of the network subsystem, directly inside the device driver before `sk_buff` allocation.
- Allows line-rate packet drops, forwarding (XDP_TX / XDP_REDIRECT), and packet manipulation directly on NIC ingress rings.
- Achieves over 24 million packets per second (Mpps) per core, drastically outperforming standard kernel IP stack routing for DDoS mitigation and L4 load balancing.

## 3. Map Data Structures
- Hash Maps, Array Maps, LRU Maps, and Ring Buffers provide bidirectional communication between kernel-space eBPF programs and user-space control daemons.

Related: [[BGP_Routing_Protocol_Architecture]] | [[Enterprise_VLAN_Trunking_802.1Q]]

