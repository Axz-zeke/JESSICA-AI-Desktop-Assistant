# TLS 1.3 Handshake & PKI Certificate Architecture

## TLS 1.3 1-RTT Handshake Optimization
Unlike TLS 1.2 which required 2 full round-trips (2-RTT) to negotiate cipher suites and exchange keys, TLS 1.3 completes cryptographic negotiation in just **1-RTT** (and 0-RTT with Pre-Shared Key session resumption):
1. **ClientHello**: Client sends supported cipher suites AND its Diffie-Hellman key share guess in the very first message.
2. **ServerHello**: Server responds with selected cipher suite and its own key share. Both parties compute the shared secret immediately.

## PKI Chain of Trust
1. **Root CA**: Self-signed certificate baked directly into OS/browser trusted root stores.
2. **Intermediate CA**: Signed by Root CA; issues certificates to avoid exposing Root CA private keys online.
3. **End-Entity Certificate**: Leaf certificate bound to the domain name (verified via SAN - Subject Alternative Name).
