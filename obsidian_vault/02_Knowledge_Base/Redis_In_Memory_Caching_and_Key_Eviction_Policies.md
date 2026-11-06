# Redis In-Memory Caching and Key Eviction Policies

## Key Memory Eviction Strategies
When Redis reaches `maxmemory`, it triggers memory reclamation based on configured eviction policies:
1. **`volatile-lru`:** Evicts Least Recently Used keys with an explicit TTL expiration.
2. **`allkeys-lru`:** Evicts Least Recently Used keys across all stored data.
3. **`volatile-lfu`:** Evicts Least Frequently Used keys based on logarithmic access counters.
4. **`noeviction`:** Returns memory errors on new write operations while servicing reads.

## Redis Data Structures
- **Hashes (`HSET`, `HGET`):** High-efficiency representation of objects.
- **Sorted Sets (`ZADD`, `ZRANGE`):** Real-time leaderboards and rate-limiting sliding windows.
- **Streams (`XADD`, `XREAD`):** Persistent distributed message bus with consumer groups.
