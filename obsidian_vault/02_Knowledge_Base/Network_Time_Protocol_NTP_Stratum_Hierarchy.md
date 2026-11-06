# Network Time Protocol (NTP) Stratum Hierarchy

## Precision Time Architecture
Accurate clock synchronization is mandatory for Active Directory Kerberos tickets (max skew: 5 minutes), forensic log correlation, and database distributed transactions.

```text
[Stratum 0: Atomic Clock / GPS Satellites]
                  |
[Stratum 1: Primary Time Servers (Directly Attached)]
                  |
[Stratum 2: Enterprise Core Switches / Active Directory PDC]
                  |
[Stratum 3: Edge Switches, Virtual Machines, Workstations]
```

## NTP UDP Port 123 Configuration
```bash
# Verify synchronization status on Linux
chronyc tracking
chronyc sources -v

# Windows Server PDC Emulator Time Source Configuration
w32tm /config /manualpeerlist:"pool.ntp.org,0x8" /syncfromflags:manual /reliable:yes /update
w32tm /resync /rediscover
w32tm /query /status
```
