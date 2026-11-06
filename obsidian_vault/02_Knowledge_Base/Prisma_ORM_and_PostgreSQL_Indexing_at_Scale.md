# Prisma ORM and PostgreSQL Indexing at Scale

## High-Performance PostgreSQL Schema
Prisma bridges TypeScript models to relational tables. At high concurrency, missing indexes cause sequential full-table scans, driving CPU to 100%.

```prisma
model Order {
  id          String      @id @default(uuid())
  userId      String
  status      OrderStatus @default(PENDING)
  totalAmount Decimal     @db.Decimal(12, 2)
  createdAt   DateTime    @default(now())
  user        User        @relation(fields: [userId], references: [id], onDelete: Cascade)

  // Compound index for user query sorting
  @@index([userId, createdAt(sort: Desc)])
  // Partial index or status filter
  @@index([status])
}
```

## B-Tree vs GIN & GiST Indexes in Postgres
- **B-Tree (Default):** Optimal for equality (`=`), range queries (`<, <=, >, >=`), and sorting (`ORDER BY`).
- **GIN (Generalized Inverted Index):** Mandatory for JSONB keys, array membership, and Full-Text Search.
- **BRIN (Block Range Index):** Ultra-compact index for massive append-only sequential time-series tables.
