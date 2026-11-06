# RADIUS and 802.1X Enterprise Network Authentication

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
