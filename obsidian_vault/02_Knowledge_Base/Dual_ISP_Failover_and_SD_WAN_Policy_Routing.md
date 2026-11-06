# Dual-ISP Failover and SD-WAN Policy Routing

## Design Overview
Dual-ISP deployment provides internet survivability and latency-sensitive path selection across Primary (e.g. Fiber DIA) and Secondary (e.g. Commercial Broadband / 5G Backup) connections.

```text
               +----------------------+
               |    Core FortiGate    |
               +----------+-----------+
                          |
              +-----------+-----------+
              |                       |
      [WAN1: Fiber 500M]      [WAN2: 5G/Coax 200M]
              |                       |
        ISP A (Primary)        ISP B (Secondary)
```

## Health Check & Performance SLA
Health probes measure packet loss, round-trip latency, and jitter via continuous ICMP/DNS requests.
```bash
config system sdwan
    config health-check
        edit "Google_DNS_Probe"
            set server "8.8.8.8" "1.1.1.1"
            set interval 500
            set probe-timeout 1000
            set failtime 3
            set recoverytime 5
            set members 1 2
        next
    end
end
```

## Service Rules
- VoIP/SIP Traffic: Lowest Jitter SLA across WAN1/WAN2.
- Web & Heavy Downloads: Dynamic Spillover / Volume Load-Balancing.
