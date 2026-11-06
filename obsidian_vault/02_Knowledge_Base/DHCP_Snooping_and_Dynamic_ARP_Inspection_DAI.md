# DHCP Snooping and Dynamic ARP Inspection (DAI)

## Layer 2 Man-in-the-Middle Mitigation
- **DHCP Snooping:** Categorizes switch ports as *Trusted* (facing authorized DHCP server) or *Untrusted* (facing end users). Drops rogue DHCP Offer/ACK packets originating from untrusted ports. Builds the **DHCP Snooping Binding Database** mapping MAC, IP, Lease, and Port.
- **Dynamic ARP Inspection (DAI):** Intercepts Address Resolution Protocol (ARP) packets on untrusted ports, validating them against the DHCP binding database to prevent ARP Poisoning / Spoofing attacks.
- **IP Source Guard (IPSG):** Verifies Layer 3 source IP against the binding database, dropping spoofed packets at the physical port level.
