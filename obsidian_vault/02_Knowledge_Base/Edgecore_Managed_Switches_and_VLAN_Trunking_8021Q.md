# Edgecore Managed Switches and VLAN Trunking (802.1Q)

## 802.1Q Frame Format & Tagging
IEEE 802.1Q inserts a 4-byte Tag Protocol Identifier (TPID 0x8100) and Tag Control Information (TCI) containing:
- **PCP (3 bits):** Priority Code Point for Class of Service (QoS).
- **DEI (1 bit):** Drop Eligible Indicator.
- **VID (12 bits):** VLAN Identifier supporting up to 4094 unique VLANs.

## Edgecore CLI Configuration (EC-NOS / Open Network Linux)
```text
Edgecore# configure
Edgecore(config)# vlan 10
Edgecore(config-vlan)# name CORPORATE_DATA
Edgecore(config-vlan)# exit
Edgecore(config)# vlan 20
Edgecore(config-vlan)# name VOIP_TELEPHONY
Edgecore(config-vlan)# exit

Edgecore(config)# interface gigabitethernet 1/1
Edgecore(config-if)# switchport mode trunk
Edgecore(config-if)# switchport trunk allowed vlan 10,20,99
Edgecore(config-if)# switchport trunk native vlan 99
```

## Troubleshooting Port States
```bash
show vlan
show interfaces switchport gigabitethernet 1/1
show mac-address-table vlan 10
```
