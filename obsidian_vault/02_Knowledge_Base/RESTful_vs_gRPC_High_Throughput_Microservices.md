# RESTful vs gRPC High-Throughput Microservices

## Protocol Comparison
- **REST (HTTP/1.1 + JSON):** Human-readable, text-based serialization, high compatibility, but higher header overhead and JSON parsing costs.
- **gRPC (HTTP/2 + Protocol Buffers):** Binary serialization via Protobuf, multiplexed bidirectional streaming on single TCP connections, strongly typed interfaces generated from `.proto` definitions.

## Throughput & Serialization Performance
Protobuf binary packing reduces wire payload sizes by 40-70% compared to equivalent JSON payloads, cutting CPU serialization overhead by up to 5x.
