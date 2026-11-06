# Arista EOS and Leaf-Spine Data Center Fabric

## Clos Architecture (Spine-and-Leaf)
Modern enterprise data centers eliminate legacy Spanning Tree topologies by deploying 2-tier or 3-tier non-blocking Clos networks.
- **Spine Layer:** High-radix packet forwarding engines (e.g. Arista 7060X / 7280R) interconnecting leaf switches with uncompressed ECMP (Equal-Cost Multi-Path).
- **Leaf Layer:** Top-of-Rack (ToR) switches providing Layer 2 access or VXLAN Tunnel Endpoints (VTEPs) with BGP EVPN control plane.

```text
       [ Spine 01 ]               [ Spine 02 ]
         /      \                   /      \
        /        \                 /        \
 [ Leaf 01 ]    [ Leaf 02 ]   [ Leaf 03 ]    [ Leaf 04 ]
      |              |             |              |
   Servers        Servers       Storage        Compute
```

## Arista EOS Multi-Chassis Link Aggregation (MLAG)
```text
switch# configure terminal
switch(config)# mlag configuration
switch(config-mlag)# domain-id MLAG_PROD
switch(config-mlag)# local-interface Vlan4094
switch(config-mlag)# peer-address 10.255.255.2
switch(config-mlag)# peer-link Port-Channel10
```

## Health Verification
```bash
show mlag
show mlag detail
show bgp evpn summary
show vxlan vtep
show interfaces counters errors
```
