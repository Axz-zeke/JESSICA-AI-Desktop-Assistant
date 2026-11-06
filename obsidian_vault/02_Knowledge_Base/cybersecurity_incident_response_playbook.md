# Cybersecurity Incident Response Playbook

## 6-Phase NIST Incident Response Framework
1. **Preparation**: Hardening assets, logging baselines, establishing access lists, and preparing offline forensic tools.
2. **Identification**: Detecting anomalies via SIEM, EDR alerts, IDS signatures, or unusual outbound beaconing.
3. **Containment**:
   - Short-Term: Isolate infected endpoint from network (disconnect VLAN/WiFi, disable switch port).
   - Long-Term: Revoke compromised AD credentials, reset Kerberos ticket (KRBTGT) twice, block malicious C2 IP/domain at perimeter firewall.
4. **Eradication**: Identify persistence mechanisms (scheduled tasks, registry run keys, unauthorized SSH keys, malicious WMI event subscriptions), remove malware binaries.
5. **Recovery**: Restore systems from verified clean offline backups, monitor network traffic closely.
6. **Lessons Learned**: Post-incident review, root cause documentation, defensive hardening.

## Triage Volatile Evidence Order (RFC 3227)
1. System Memory (RAM dump via LiME or WinPmem).
2. Active network connections and sockets (`netstat -ano`).
3. Running processes and memory mappings (`Get-Process`).
4. Non-volatile disk storage and log files.
