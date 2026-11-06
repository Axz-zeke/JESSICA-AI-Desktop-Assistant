---
title: TCP/IP Protocol Suite, Flow Control & Windowing
category: Networking & Infrastructure
tags: [networking, tcp, transport, sliding-window, flow-control]
created: 2026-11-01
status: ACTIVE
related: "[[BGP_Routing_Protocol]], [[Network_Diagnostics]], [[Linux_CLI_and_System_Administration]]"
---

# TCP/IP Protocol Suite, Flow Control & Windowing

The **Transmission Control Protocol (TCP)** operates at Layer 4 (Transport) providing connection-oriented, ordered, and error-checked delivery of byte streams between hosts.

## Three-Way Handshake & Teardown
- **Establishment:**
  1. Client sends `SYN` (initial sequence number $x$).
  2. Server responds with `SYN-ACK` (sequence number $y$, ACK $x+1$).
  3. Client sends `ACK` (ACK $y+1$).
- **Connection Teardown:** Four-way handshake utilizing `FIN` and `ACK` flags, terminating with a `TIME_WAIT` state on the active closing host to ensure stray packets dissipate.

## Sliding Window & Flow Control
- **Receive Window (`RWIN`):** Advertised by the receiver indicating how many unacknowledged bytes it can buffer without overflowing.
- **Congestion Window (`CWND`):** Maintained dynamically by the sender to prevent overwhelming intermediate routers. Algorithms include Reno, Cubic, and BBR (Bottleneck Bandwidth and RTT).
- **Window Scaling (RFC 1323):** Expands the 16-bit window field up to 1GB to saturate high-bandwidth, high-latency WAN pipes (Bandwidth-Delay Product / BDP).

See also: [[BGP_Routing_Protocol]], [[Network_Diagnostics]], [[Python_Asyncio_Internals]].
