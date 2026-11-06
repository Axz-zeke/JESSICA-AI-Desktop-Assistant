# DNSSEC & Anycast Routing Architecture

## DNSSEC Cryptographic Validation
DNSSEC (Domain Name System Security Extensions) prevents DNS cache poisoning and spoofing by signing DNS resource records with public-key cryptography:
- **RRSIG (Resource Record Signature)**: Cryptographic signature for a specific record set.
- **DNSKEY**: Public key used by resolvers to verify RRSIG signatures.
- **DS (Delegation Signer)**: Hash of the child zone's DNSKEY stored in the parent zone (creating an unbroken chain of trust up to Root Key Signing Key).

## Anycast DNS Mechanics
In Anycast, multiple geographically distributed name servers advertise the **exact same BGP IP prefix** (e.g., Cloudflare's `1.1.1.1` or Google's `8.8.8.8`) to different upstream Tier 1 ISPs. Internet routers naturally route the user's DNS query to the topologically nearest server node using BGP AS-Path length, providing instant global failover and DDoS absorption.
