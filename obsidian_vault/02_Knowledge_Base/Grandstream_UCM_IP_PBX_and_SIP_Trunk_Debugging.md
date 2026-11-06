# Grandstream UCM IP-PBX and SIP Trunk Debugging

## SIP Architecture & Call Flow
Grandstream UCM6200/6300 series operate on an Asterisk core managing Session Initiation Protocol (SIP RFC 3261) and Real-time Transport Protocol (RTP RFC 3550).

```text
Caller IP Phone -----> UCM PBX -----> ITSP SIP Provider -----> PSTN
  INVITE ->             INVITE ->
  <- 100 Trying         <- 100 Trying
  <- 180 Ringing        <- 180 Ringing
  <- 200 OK             <- 200 OK
  ACK ->                ACK ->
  <============ 2-Way RTP Audio Stream (G.711 / G.729) ============>
```

## Troubleshooting SIP Registration & One-Way Audio
1. **NAT Traversal & STUN:** Configure external IP and local network exclusions in PBX Settings -> SIP -> NAT.
2. **SIP ALG Incompatibility:** Ensure SIP ALG is completely disabled on perimeter routers to prevent corrupted SDP headers.
3. **CLI Debugging:**
```bash
asterisk -rvvvvv
sip set debug on
rtp set debug on
pjsip show endpoints
```
