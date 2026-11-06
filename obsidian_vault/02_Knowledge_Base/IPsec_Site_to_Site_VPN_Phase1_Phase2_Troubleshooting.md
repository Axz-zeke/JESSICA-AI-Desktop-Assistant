# IPsec Site-to-Site VPN Phase 1 and Phase 2 Troubleshooting

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
