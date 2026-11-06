---
title: PostgreSQL Query Optimization, Indexing & EXPLAIN ANALYZE
category: Full-Stack & Systems Engineering
tags: [database, postgresql, sql, indexing, performance]
created: 2026-11-01
status: ACTIVE
related: "[[NextJS_App_Router_Architecture]], [[Redis_Caching_and_PubSub_Patterns]], [[FastAPI_High_Performance_Design]]"
---

# PostgreSQL Query Optimization, Indexing & EXPLAIN ANALYZE

**PostgreSQL** is an advanced open-source object-relational database system known for reliability, data integrity, and powerful query planning engines.

## Reading EXPLAIN (ANALYZE, BUFFERS)
- **Seq Scan vs Index Scan:** Sequential scans read every disk page in a table. Index scans traverse a B-Tree to fetch matching row pointers (TIDs).
- **Bitmap Index Scan:** Used when fetching a moderate percentage of rows, combining multiple indexes using boolean bitwise operations before reading heap blocks.
- **Cost Estimates:** Expressed in arbitrary disk page fetch units (`cost=startup..total`).

## Index Types & Best Practices
1. **B-Tree:** Default balanced tree index optimal for equality (`=`) and range (`<`, `>`, `BETWEEN`) queries.
2. **GIN (Generalized Inverted Index):** Essential for array containment, full-text search, and JSONB queries (`@>`, `?`).
3. **Partial Indexes:** Indexes only rows satisfying a specific WHERE condition (`WHERE active = true`), reducing index size by up to 90%.

See also: [[Redis_Caching_and_PubSub_Patterns]], [[FastAPI_High_Performance_Design]], [[NextJS_App_Router_Architecture]].
