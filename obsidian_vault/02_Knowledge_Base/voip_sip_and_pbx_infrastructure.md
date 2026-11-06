# VoIP, SIP Protocol & PBX Infrastructure

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
