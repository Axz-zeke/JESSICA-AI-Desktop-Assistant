# Wireshark Packet Analysis & TCP Handshake Mechanics

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
