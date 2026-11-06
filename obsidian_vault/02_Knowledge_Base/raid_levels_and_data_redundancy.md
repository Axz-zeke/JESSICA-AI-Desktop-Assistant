# RAID Levels & Hardware Redundancy Guide

## Common RAID Configurations
1. **RAID 0 (Striping)**: 0 redundancy. High read/write speed. Single drive failure results in 100% data loss.
2. **RAID 1 (Mirroring)**: 100% capacity duplicate across 2 drives. Can survive 1 drive loss.
3. **RAID 5 (Block Striping with Single Distributed Parity)**: Requires minimum 3 disks. Usable capacity: `(N - 1) * Size`. Can survive 1 disk failure. Vulnerable to URE (Unrecoverable Read Errors) during rebuild.
4. **RAID 6 / RAIDZ2 (Dual Distributed Parity)**: Requires minimum 4 disks. Usable capacity: `(N - 2) * Size`. Can survive 2 simultaneous disk failures. Standard recommendation for modern large HDD pools (>8TB).
5. **RAID 10 (Stripe of Mirrors)**: Requires minimum 4 disks. Combines high throughput with fast rebuild times (rebuilds copy from single mirror rather than recalculating parity across entire array).

## Critical Storage Axiom: RAID is Not a Backup
RAID protects against physical drive hardware failure, NOT against accidental deletion, ransomware encryption, filesystem corruption, or natural disaster. Backups must follow the **3-2-1 Rule**: 3 copies of data, across 2 different media types, with 1 offsite.
