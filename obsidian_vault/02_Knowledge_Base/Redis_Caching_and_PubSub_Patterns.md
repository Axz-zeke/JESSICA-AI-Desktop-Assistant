---
title: Redis In-Memory Architecture, Caching & Pub/Sub
category: Full-Stack & Systems Engineering
tags: [database, redis, caching, pubsub, performance]
created: 2026-11-01
status: ACTIVE
related: "[[PostgreSQL_Query_Optimization]], [[FastAPI_High_Performance_Design]], [[Microservices_vs_Modular_Monolith]]"
---

# Redis In-Memory Architecture, Caching & Pub/Sub

**Redis (Remote Dictionary Server)** is an open-source, in-memory data structure store used as a distributed cache, message broker, and streaming engine capable of executing over 100,000 operations per second.

## Core Data Structures & Applications
- **Strings:** Basic key-value pairs, atomic counters (`INCR`), rate limiting.
- **Hashes:** Storing structured objects with field-level access.
- **Sorted Sets (ZSET):** Real-time leaderboards and priority queues indexed by floating-point score.
- **Bitmaps & HyperLogLog:** Space-efficient probabilistic counting of millions of unique user sessions.

## Eviction Policies
When maxmemory is reached, Redis evicts keys according to configured policies: `allkeys-lru` (Least Recently Used), `volatile-lru` (evicts only keys with TTL set), or `noeviction` (returns out-of-memory errors on writes).

See also: [[PostgreSQL_Query_Optimization]], [[FastAPI_High_Performance_Design]], [[Microservices_vs_Modular_Monolith]].
