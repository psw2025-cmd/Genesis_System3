# Backup and Restore — Genesis System3

**Purpose:** Protect critical data and enable recovery after failure.

---

## Critical Paths to Backup

| Path | Contents | Frequency |
|------|----------|-----------|
| `outputs/` | health.json, positions_live.json, signals, QC, state snapshots | Daily |
| `config/` | Thresholds, regime config, live trade config | On change |
| `logs/` | Backend logs, inspector artifacts | Weekly (or retention policy) |

---

## Backup Script (PowerShell)

```powershell
# Example: backup to outputs_backup/YYYYMMDD
$date = Get-Date -Format "yyyyMMdd"
$dest = "outputs_backup\$date"
New-Item -ItemType Directory -Path $dest -Force
Copy-Item -Path outputs\* -Destination $dest -Recurse -Force
Copy-Item -Path config\* -Destination "$dest\config" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## Restore

1. Restore `outputs/` from backup: `Copy-Item outputs_backup\YYYYMMDD\* outputs\ -Recurse -Force`
2. Restore `config/` if needed.
3. Restart backend: `docker compose restart backend` or restart uvicorn.
4. Verify: `Invoke-WebRequest http://localhost:8000/api/health -UseBasicParsing`

---

## Retention

- Keep last 7 days of daily backups (align with log rotation).
- Archive monthly snapshots for compliance/audit if required.

---

## Disaster Recovery

- **Full restore:** Restore outputs + config; run `pip install -r requirements_runtime.txt`; start services.
- **DB corruption:** Replace SQLite DB from backup; ensure `outputs/` is writable.
- **Broker mismatch:** Run `position_reconciliation.py` after restore to reconcile broker vs positions_live.json.
