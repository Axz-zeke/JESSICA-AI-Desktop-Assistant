# Self-Hosted NAS Storage & ZFS Storage Architecture

## ZFS Core Concepts
ZFS is an enterprise filesystem and logical volume manager built for bulletproof data integrity:
- **vdev (Virtual Device)**: Group of physical drives configured as Stripe, Mirror, RAIDZ1, RAIDZ2, or RAIDZ3.
- **Zpool**: Pool of one or more vdevs providing aggregate storage capacity.
- **Copy-on-Write (CoW)**: Never overwrites existing blocks in-place; writes new data to free blocks and updates pointers atomically.
- **Self-Healing Data Scrubbing**: Computes SHA-256 or xxHash checksums on every single block read. If checksum fails, automatically reads the mirror or parity block and corrects the corrupted block on disk (eliminating silent bit rot).

## TrueNAS SCALE & Linux ZFS Commands
- `zpool status`: Displays health of all pools, vdevs, read/write/checksum error counts.
- `zpool scrub <pool_name>`: Initiates proactive bit rot verification and repair across all disks.
- `zfs snapshot <pool>/<dataset>@snap_name`: Instant zero-space snapshot.
