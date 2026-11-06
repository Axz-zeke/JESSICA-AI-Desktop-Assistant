# Spanning Tree Protocol: RSTP, MSTP, and Root Guard

## IEEE 802.1w (Rapid Spanning Tree Protocol)
RSTP reduces convergence time from 50 seconds to <2 seconds using Proposal-Agreement handshakes instead of timer-based states.
- **Port Roles:** Root Port, Designated Port, Alternate Port, Backup Port.
- **Port States:** Discarding, Learning, Forwarding.

## Spanning Tree Protection Mechanisms
1. **BPDU Guard:** Instantly err-disables an Edge/PortFast port if an unexpected BPDU frame is received, preventing unauthorized switch loops.
2. **Root Guard:** Enforces root bridge placement by placing ports into root-inconsistent state if a superior BPDU arrives.
3. **Loop Guard:** Prevents alternate or root ports from becoming designated due to unidirectional link failures.
