# Oracle and SQL Server Database Backup Strategies

## Backup Architecture & RPO / RTO
- **RPO (Recovery Point Objective):** Maximum acceptable data loss window measured in time.
- **RTO (Recovery Time Objective):** Maximum acceptable duration required to restore operational database services.

## SQL Server Backup Strategy
1. **Full Backup:** Weekly (Sunday 00:00).
2. **Differential Backup:** Daily (Every 24 hours at 23:00).
3. **Transaction Log Backup:** Every 15 minutes with log truncation.
```sql
BACKUP DATABASE [ProdERP] TO DISK = N'E:\Backups\ProdERP_Full.bak' WITH COMPRESSION, STATS = 10;
BACKUP LOG [ProdERP] TO DISK = N'E:\Backups\ProdERP_Log.trn' WITH COMPRESSION;
```

## Oracle Database RMAN (Recovery Manager)
```bash
rman target /
RMAN> CONFIGURE DEFAULT DEVICE TYPE TO DISK;
RMAN> CONFIGURE BACKUP OPTIMIZATION ON;
RMAN> BACKUP AS COMPRESSED BACKUPSET DATABASE PLUS ARCHIVELOG DELETE INPUT;
```
