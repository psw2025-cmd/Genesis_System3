# Genesis System3 — Target Local Architecture (post-GCP-exit)

**Companion to:** `GENESIS_SYSTEM3_LOCAL_MIGRATION_MASTER_PLAN.md`, `GENESIS_SYSTEM3_STATE_ROOT_INVENTORY.csv`, `GENESIS_SYSTEM3_LOCAL_MIGRATION_CHECKLIST.md`

## 1. Current state (as audited 2026-09-01, after-hours)

```
GitHub (psw2025-cmd/Genesis_System3, main = code authority)
        │
        ▼
C:\Genesis_System3_Clean  (exact-main checkout, target canonical code root)
        │
        ├── dashboard/backend/app.py ──uvicorn──▶ http://127.0.0.1:8000
        │                                          │
        │                                          ├─▶ core/utils/env_loader.py
        │                                          │     └─▶ core/security/windows_secret_vault.py (DPAPI)
        │                                          │           └─▶ Dhan broker (read-only, PAPER only)
        │                                          │
        │                                          └─▶ state/*, outputs/*, logs/* (written directly
        │                                              under the code checkout — NOT yet under the
        │                                              target runtime root)
        │
        ├── config/system3_job_scheduler.json  (25 jobs defined, NOT running)
        ├── core/engine/system3_phase82_job_scheduler.py  (daemon exists, NOT registered/running)
        ├── scripts/gcp_dhan_token_rotation_job.py  (real logic, GCP-Secret-Manager-only persistence)
        └── scripts/system3_laptop_supervisor.py  (partial, ad hoc paper-tick loop, untracked)

C:\Genesis_System3_Runtime  (target runtime root — created, EMPTY, nothing points at it yet)

Google Cloud (system3-openalgo-safe) — being exited
        ├── genesis-system3-web        min=0/max=1, scale-down done, NOT deleted
        ├── 9 Cloud Run Jobs           idle (schedulers paused)
        ├── 9 Cloud Schedulers         ALL PAUSED (verified live)
        ├── Secret Manager (11)       still authoritative for anything not yet in the local vault
        └── Firestore/Storage/etc.     one Firestore export pulled locally, not yet reconciled
```

## 2. Target state

```
GitHub main (code authority, unchanged)
        │
        ▼
C:\Genesis_System3_Clean  (code only — no runtime writes land here anymore)
        │
        ├── dashboard/backend/app.py ──uvicorn──▶ http://127.0.0.1:<configured-port>/ui
        │        SYSTEM3_RUNTIME_ROOT=C:\Genesis_System3_Runtime
        │        SYSTEM3_STATE_BACKEND=local
        │
        ├── core/engine/system3_phase82_job_scheduler.py
        │        registered as ONE Windows Scheduled Task ("Genesis_System3_Local_Scheduler"),
        │        runs run_daemon() continuously, duplicate-worker lock in
        │        C:\Genesis_System3_Runtime\locks\scheduler.lock
        │        reads config/local_scheduler_registry.yaml (reconciled superset of
        │        config/system3_job_scheduler.json + the migrated token-rotation job)
        │
        └── scripts/gcp_dhan_token_rotation_job.py (or a local-adapter twin)
                 persistence swapped to core.security.windows_secret_vault
                 scheduled inside the phase82 daemon at */5 * * * * (Asia/Kolkata)

C:\Genesis_System3_Runtime          (single writable runtime root)
        ├── state\        <- authoritative runtime state / checkpoints
        ├── db\           <- historical_market_data.db, option_chain.db, system3_metrics.sqlite (moved here)
        ├── logs\         <- rotating logs (7 days full, 30 days compact incident summaries)
        ├── evidence\     <- bounded per-checkpoint proof bundles
        ├── backups\      <- SHA-256-manifested archives (supersedes ad hoc Desktop zips)
        ├── models\       <- ML model artifacts
        ├── market_data\  <- durable market/instrument history
        ├── cache\        <- rebuildable, safe to delete
        ├── tmp\          <- disposable scratch, auto-cleaned same work cycle
        └── locks\        <- PID/lease files, duplicate-worker prevention

%USERPROFILE%\.genesis_vault\secrets.bin   (DPAPI, unchanged — already correct)

GitHub main
        └── reports/runtime/latest/*.json|.md  (compact, sanitized, updated on material change —
             the only thing agents-without-laptop-access read; never raw logs/DBs/media)

Google Cloud (system3-openalgo-safe)
        └── every resource remains PAUSED/scaled-down until the corresponding local piece above
            is proven, per the do-not-delete-yet checklist — then deleted, not just paused
```

## 3. Ownership boundaries (who writes what)

| Concern | Owner | Notes |
|---|---|---|
| Code | GitHub `main`, PR-reviewed | No agent commits directly to main |
| Scheduling | `core/engine/system3_phase82_job_scheduler.py` daemon, one Windows Scheduled Task | Not Cloud Scheduler, not ad hoc scripts, not a second competing loop |
| Secrets | `%USERPROFILE%\.genesis_vault` (DPAPI) | Secret Manager is a fallback only until fully retired, never the normal path |
| Runtime state/DB/logs | `C:\Genesis_System3_Runtime\*` | Not the code checkout, not scattered across `state/`, `outputs/`, `logs/` inside `C:\Genesis_System3_Clean` |
| GitHub-visible status | `reports/runtime/latest/*` + Issue #188 comments | Never raw logs/DBs/media |
| Legacy/dirty checkouts | `E:\Genesis_System3`, `C:\openalgo-main`, the original `C:\Users\ADMIN\...\Genesis_System3` | Read-only archive, explicitly out of active-reconciliation scope this pass |

## 4. Why this design (not an alternative)

- **One scheduler daemon, not six new scripts**: the phase82 engine already exists, is already tested against market-holiday/weekday logic, and is already wired into the dashboard's status reporting — building six new ad hoc local jobs would duplicate working code and create exactly the kind of "two competing loops" risk the operating standard warns about (see `scripts/system3_laptop_supervisor.py` vs. phase82 in the CSV).
- **Runtime root separate from code root**: keeps `git status` on the code checkout clean (no more DB/log churn showing as dirty files, which is what made every existing checkout hard to reconcile in the first place) and makes a future `git pull` on the code root safe without touching runtime state.
- **DPAPI vault as the default, Secret Manager as fallback-only until retirement**: matches the owner's zero-GCP-billing goal without an all-or-nothing cutover that could strand the broker session if something in the vault path fails before it's proven over a full trading day.
