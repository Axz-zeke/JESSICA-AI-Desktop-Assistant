# BGP Autonomous Systems and Prefix Filtering

## Border Gateway Protocol (BGP-4)
BGP is the path-vector exterior gateway protocol of the global Internet. It exchanges Reachability Information (NLRI) between distinct Autonomous System Numbers (ASNs).

## Best Path Selection Hierarchy
1. Highest Weight (Cisco proprietary, local to switch).
2. Highest Local Preference (Default 100, advertised within iBGP).
3. Locally Originated Routes (network or aggregate-address).
4. Shortest AS-Path length.
5. Lowest Origin Type (IGP < EGP < Incomplete).
6. Lowest MED (Multi-Exit Discriminator).
7. eBGP over iBGP.
8. Lowest IGP metric to next-hop.
9. Lowest BGP Router ID.

## ROA & RPKI Validation
Prefix filtering must validate Route Origin Authorizations (ROA) via RPKI to prevent BGP route hijacking.
