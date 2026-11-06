# Disaster Recovery: RTO, RPO, and Immutable Storage

## 3-2-1-1-0 Backup Rule
- **3 Copies of Data:** Primary production data plus two independent backups.
- **2 Different Media Types:** E.g. local NVMe/SSD array and enterprise LTO Tape / Cloud Object Storage.
- **1 Copy Kept Offsite:** Geographically isolated secondary data center.
- **1 Copy Immutable or Air-Gapped:** Protected by Object Lock WORM (Write Once, Read Many).
- **0 Errors After Testing:** Continuous automated daily restore verification.

## Immutable Storage Architecture
Prevents ransomware operators or compromised administrator accounts from encrypting or deleting historical snapshots.
AWS S3 Object Lock and MinIO deploy compliance retention modes where retention duration cannot be overridden even by root credentials.
