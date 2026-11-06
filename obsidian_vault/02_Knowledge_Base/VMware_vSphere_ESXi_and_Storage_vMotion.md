# VMware vSphere ESXi and Storage vMotion

## vMotion & Storage vMotion Mechanics
vMotion migrates active VM state between ESXi hosts with zero downtime using pre-copy memory iterative synchronizations and fast stun/resume (<100ms).
Storage vMotion moves virtual disk VMDK files across storage datastores (VMFS / NFS / vSAN) using snapshot mirroring and block-level change tracking.

```text
[ESXi Host 01] -------- 10GbE / 25GbE vMotion Network --------> [ESXi Host 02]
      |                                                              |
[Datastore A (SAN)] ======= Block-level Mirroring (FDM) ======> [Datastore B (NVMe)]
```

## ESXi CLI Diagnostics
```bash
# View network adapters and uplink link states
esxcli network nic list

# Monitor VM latency and disk queue metrics
esxtop
# (Press 'd' for disk adapter, 'u' for disk device, 'n' for network)

# Check storage paths and multipathing status
esxcli storage nmp device list
```
