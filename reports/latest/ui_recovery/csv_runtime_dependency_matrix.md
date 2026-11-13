# Genesis System3 — CSV, JSONL & SQLite Runtime Dependency Matrix (`OBS-004..006`, `SRC-020..028`, `PEND-028..031`)
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`

## 1. Audited Runtime & Fallback File Readers/Writers
| ID | File:Line | Storage Type | Current Role | Classification & Migration Status |
|---|---|---|---|---|
| `OBS-004a` | `dashboard/backend/app.py:5622,5758` | CSV (`pd.read_csv(chain_file)`) | Last-resort fallback when DSM live fetch fails; explicitly labeled `STALE_CSV_FALLBACK` (`stale: True`) | **GUARDED FALLBACK**: Port 8008 uses `state/chain_cache/*.json` (`VERIFIED_EXCHANGE_SNAPSHOT`). Full PostgreSQL migration tracked under `PEND-029` (`BLOCKED` on local PostgreSQL instance). |
| `OBS-004b` | `dashboard/backend/app.py:6099` | CSV (`pnl_csv`) | Legacy dashboard P&L CSV reader | Port 8008 `/api/paper/ledger` uses reconciled `analyzer_paper_lifecycle_proof/summary.json` with itemized charges. |
| `OBS-004c` | `dashboard/backend/app.py:6362` | CSV (`signals_csv`) | Legacy signal CSV reader | Port 8008 `/api/ml/prediction-audit` & `/api/ml/forecast-vs-actual` read structured `state/gain_rank_history.json`. |
| `OBS-004d` | `dashboard/backend/app.py:10732` | CSV (`_compat_csv_records`) | Generic compatibility helper | Used only by legacy compatibility routes; optional CSV exports at `9470,9495` preserved (`SRC-028`). |
| `OBS-005` | `dashboard/backend/paper_pipeline_v8.py:1-70` | JSON/JSONL | Paper pipeline state & dedup helper (`_append_jsonl_once`) | IST date bug (`REP-016`) fixed (`ZoneInfo("Asia/Kolkata")` + `+05:30` fallback). |
| `OBS-006` | `dashboard/backend/equity_option_scanner.py:36` | CSV (`*_fo_bhavcopy.csv`) | Historical EOD NSE F&O bhavcopy ingestion | **VALID INGESTION FORMAT**: EOD bhavcopy CSV is exchange reference input, never labeled as live ticks. |
| `SRC-020..026` | `order_management.py:42`, `trade_journal.py:22`, `alerts_system.py:66`, `proof_ledger_service.py:22` | JSONL (`outputs/*.jsonl`) | Local append-only audit/journal logs | Preserved for local paper/audit durability; PostgreSQL SSOT migration requires external DB provisioning (`PEND-029`). |
| `REP-012..014` | `dashboard/backend/app.py:160`, `index_history_service.py:9`, `sandbox/engine.py:12` | SQLite (`sqlite3`) | Local sandbox order engine (`sandbox.db`) & index history cache | Active local relational store for `SandboxEngine` (`PAPER_MODE=1`). |
