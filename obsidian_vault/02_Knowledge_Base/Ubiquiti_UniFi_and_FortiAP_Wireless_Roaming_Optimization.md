# Ubiquiti UniFi and FortiAP Wireless Roaming Optimization

## 802.11k, 802.11v, and 802.11r Protocols
- **802.11k (Neighbor Reports):** Informs client devices about nearby access points to reduce channel scanning latency.
- **802.11v (BSS Transition Management):** Allows APs to suggest roaming to closer APs when signal drops below target RSSI.
- **802.11r (Fast BSS Transition):** Pre-caches 4-way WPA2/WPA3 handshakes between APs, reducing roaming delay to <30ms (zero VoIP packet loss).

## Tuning RF Power & Channel Planning
- **2.4 GHz:** Strictly use 20 MHz width on non-overlapping channels 1, 6, 11 with low transmit power (10-12 dBm).
- **5 GHz:** Deploy 40 MHz or 80 MHz channel widths on DFS and non-DFS channels with medium transmit power (16-18 dBm).
- **Minimum RSSI Threshold:** Set AP disassociation threshold to `-75 dBm` to prevent sticky clients.
