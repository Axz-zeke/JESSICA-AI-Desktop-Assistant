# SNMPv3 and Syslog Centralized Network Monitoring

## Simple Network Management Protocol v3
Unlike insecure SNMPv1/v2c which transmits cleartext community strings, SNMPv3 provides:
1. **Authentication (authNoPriv):** HMAC-SHA-256 verifying sender integrity.
2. **Encryption (authPriv):** AES-128 / AES-256 payload privacy preventing packet inspection.

## Centralized Syslog Facility Levels (RFC 5424)
- Severity 0: Emergency (System unusable).
- Severity 1: Alert (Immediate action required).
- Severity 2: Critical (Hardware component failure).
- Severity 3: Error (Operational impairment).
- Severity 4: Warning (Threshold warning).
- Severity 5: Notice (Normal significant event).
- Severity 6: Informational.
- Severity 7: Debug.
