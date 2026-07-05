# Runtime Authority Summary

**Branch:** `fix/scheduler-catchup-and-market-proof`
**Base commit:** `95dbec4` — fix: add missing timezone import causing scheduler-health-push to crash (#52)
**Generated:** 2026-07-01 22:45 IST / 17:15 UTC

## Authoritative Runtime Paths

| Component | Path |
|---|---|
| Backend web service | `dashboard/backend/app.py` (Dockerfile: `dashboard/backend/Dockerfile`) |
| Worker service | `scripts/cloud_worker.py` (same Dockerfile, `dockerCommand: python scripts/cloud_worker.py`) |
| Scheduler | `core/engine/system3_phase82_job_scheduler.py` |
| Scheduler config | `config/system3_job_scheduler.json` |
| Scheduler state | `storage/ultra/ph76_ph100/phase82_job_scheduler_state.json` |
| Frontend | `dashboard/frontend` (Vite, served from `dist/` at `/ui`) |
| Reports output | `reports/latest` |

No relational database — state is JSON-file-based.

## Duplicate/Stale Path Check

Checked for archive/backup/duplicate runtime paths that could shadow the real ones:

- `proof/archive` — historical archive, not imported by any entrypoint
- `scripts/proof_run.ps1.backup`, `scripts/verify_proof_pack.ps1.backup` — backup files, not imported
- `system3_autorun_master.py.backup`, `system3_watchdog.py.backup` — pre-cloud-deployment backups, superseded by `cloud_worker.py`'s threads, not imported

**Verification:** grepped all four active runtime entrypoints for references to each backup/archive path — zero matches.

**Conclusion:** No archive/backup/stale duplicate runtime path is imported by any active service.
