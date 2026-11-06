# FortiGate Next-Gen Firewall & SSL-VPN Configuration

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
