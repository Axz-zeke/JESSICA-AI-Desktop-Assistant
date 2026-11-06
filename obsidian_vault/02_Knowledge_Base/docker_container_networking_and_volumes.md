# Docker Container Networking & Storage Volumes

## Network Drivers
1. **Bridge (default)**: Creates a private software bridge (`docker0`) on host; containers communicate via private IP range (`172.17.0.0/16`) and expose ports to host via NAT iptables rules.
2. **Host**: Removes network isolation between container and host; container binds directly to host IP/ports (highest throughput, zero NAT overhead).
3. **Macvlan / Ipvlan**: Assigns real MAC/IP addresses directly to container from physical LAN, appearing as physical devices on home/office switch.
4. **Overlay**: Enables multi-host container networking across Docker Swarm nodes using VXLAN tunneling.

## Storage Management
- **Named Volumes (`/var/lib/docker/volumes/`)**: Managed by Docker, independent of container lifecycle, safe across container rebuilds.
- **Bind Mounts (`./host_path:/container_path`)**: Directly maps host filesystem directory; useful for hot-reloading code or mounting configuration files.
- **tmpfs**: Mounts into host system RAM, never persisted to disk (high security, temporary cache).

## Maintenance Commands
```bash
docker system prune -a --volumes # Cleans dead containers, unused networks, and dangling volumes
docker inspect <container_id> --format '{{ .NetworkSettings.IPAddress }}' # Quick container IP lookup
```
