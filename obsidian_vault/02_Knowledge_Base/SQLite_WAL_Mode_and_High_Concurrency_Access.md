# SQLite WAL Mode and High-Concurrency Access

## Write-Ahead Logging (WAL) Architecture
Default SQLite rollback journals lock the entire database file during writes, blocking concurrent readers.
WAL mode separates writes into an append-only `*.db-wal` log file:
- Readers read from the database file and WAL concurrently without locking.
- Writers append changes to the WAL without blocking readers.
- Background checkpoints periodically flush WAL changes into the primary `.db` file.

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA cache_size = -64000; -- 64MB In-Memory Page Cache
```
