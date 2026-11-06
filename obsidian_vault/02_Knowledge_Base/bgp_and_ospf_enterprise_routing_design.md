# BGP & OSPF Enterprise Routing Design

## OSPF (Open Shortest Path First) - Interior Gateway
- **Type**: Link-State IGP operating inside single Autonomous System.
- **Algorithm**: Dijkstra's Shortest Path First (SPF).
- **Hierarchical Design**: All areas (Area 1, Area 2) must connect to Area 0 (Backbone).
- **Metric**: Cost = `Reference_Bandwidth / Interface_Bandwidth` (default reference is 100 Mbps; in 10Gbps+ networks, must set `auto-cost reference-bandwidth 100000`).

## BGP (Border Gateway Protocol) - Exterior Gateway
- **Type**: Path-Vector EGP running between distinct Autonomous Systems (e.g., Enterprise to Dual-Homed ISPs).
- **Standard Port**: TCP 179.
- **Path Selection Hierarchy**:
  1. Highest **Weight** (Cisco proprietary, local to router).
  2. Highest **Local Preference** (advertised across entire AS).
  3. Locally originated routes.
  4. Shortest **AS-Path** length.
  5. Lowest **MED** (Multi-Exit Discriminator).
