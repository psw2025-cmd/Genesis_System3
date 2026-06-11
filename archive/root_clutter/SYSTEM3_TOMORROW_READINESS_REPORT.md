# SYSTEM3 TOMORROW READINESS REPORT

- Generated at: `2025-12-08T22:08:41`
- Repo root: `C:\Genesis_System3`

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Paths & venv python | ✅ OK | C:\Genesis_System3\venv\Scripts\python.exe |
| Venv dependencies  | ✅ OK | OK:all_deps_present |
| Safety flags / live-trading guard | ✅ OK | LIVE_TRADING_ENABLED=None |
| Production pipeline dry-run | ✅ OK | script=C:\Genesis_System3\system3_production_pipeline_clean.py |
| Continuous validators one-shot | ⚠️ CHECK | script=C:\Genesis_System3\phase_e_watchdog.py |
| Overall readiness | ⚠️ CHECK | DRY-RUN only, real-money still blocked |

## Safety / Live-Trading Guards

- `LIVE_TRADING_ENABLED`: `None`
- `USE_LIVE_EXECUTION_ENGINE`: `None`
- `AUTO_EXECUTE_TRADES`: `None`
- `PAPER_TRADING_MODE`: `None`
- `SYSTEM3_LIVE_TRADING_ALLOWED` env: `None`

**Safety issues detected:**
- LIVE_TRADING_ENABLED not found in configs.
- USE_LIVE_EXECUTION_ENGINE not found in configs.
- AUTO_EXECUTE_TRADES not found in configs.

## Production Pipeline Dry-Run

- Script: `C:\Genesis_System3\system3_production_pipeline_clean.py`
- Exit code: `0`

<details><summary>stdout</summary>

```text
[2025-12-08 22:08:39] Normalizing SIGNALS merge keys...
```
</details>

<details><summary>stderr</summary>

```text
2025-12-08 22:08:38,754 [INFO] ======================================================================
2025-12-08 22:08:38,754 [INFO] PRODUCTION PIPELINE ORCHESTRATOR - STARTING
2025-12-08 22:08:38,754 [INFO] ======================================================================
2025-12-08 22:08:38,754 [INFO] ======================================================================
2025-12-08 22:08:38,755 [INFO] PHASE 220: HISTORICAL SIGNAL AGGREGATION
2025-12-08 22:08:38,755 [INFO] ======================================================================
2025-12-08 22:08:38,758 [INFO] Found 31 archive files
2025-12-08 22:08:39,400 [INFO] Loaded 5655 total rows from 31 files
2025-12-08 22:08:39,426 [INFO] Removed 4932 duplicates (87.2%)
2025-12-08 22:08:39,437 [WARNING] Dropped 73 rows with NULL timestamps
2025-12-08 22:08:39,527 [INFO] \u2713 Phase 220 complete: C:\Genesis_System3\storage\live\forward\phase220_aggregated_signals.csv
2025-12-08 22:08:39,527 [INFO]   Output: 650 rows across 7 unique dates
2025-12-08 22:08:39,527 [INFO]   Duration: 0.77s
2025-12-08 22:08:39,527 [INFO] \u2713 Phase 220 completed in 0.77s (within 2.00s target)
2025-12-08 22:08:39,533 [INFO] ======================================================================
2025-12-08 22:08:39,533 [INFO] PHASE 221: FORWARD RETURNS COMPUTATION
2025-12-08 22:08:39,533 [INFO] ======================================================================
2025-12-08 22:08:39,578 [INFO] Loaded 650 rows from Phase 220
2025-12-08 22:08:39,597 [INFO]   fwd_ret_1: 468/650 (72.0%)
2025-12-08 22:08:39,597 [INFO]   fwd_ret_2: 406/650 (62.5%)
2025-12-08 22:08:39,598 [INFO]   fwd_ret_5: 296/650 (45.5%)
2025-12-08 22:08:39,598 [INFO]   fwd_ret_10: 142/650 (21.8%)
2025-12-08 22:08:39,599 [INFO]   fwd_ret_15: 22/650 (3.4%)
2025-12-08 22:08:39,746 [INFO] \u2713 Phase 221 complete: C:\Genesis_System3\storage\live\forward\phase221_forward_returns.csv
2025-12-08 22:08:39,746 [INFO]   Output: 650 rows with 5 horizons
2025-12-08 22:08:39,746 [INFO]   Duration: 0.21s
2025-12-08 22:08:39,746 [INFO] \u2713 Phase 221 completed in 0.21s (within 2.00s target)
2025-12-08 22:08:39,747 [INFO] ======================================================================
2025-12-08 22:08:39,747 [INFO] PHASE 239: PNL ENRICHMENT (4-STAGE JOIN)
2025-12-08 22:08:39,747 [INFO] ======================================================================
2025-12-08 22:08:39,803 [WARNING] Normalization failed: 'charmap' codec can't encode character '\u2713' in position 24: character maps to <undefined> — using raw data
2025-12-08 22:08:39,903 [INFO] After validation: 550 signals, 2950 orders
2025-12-08 22:08:39,903 [INFO] Stage 1: Exact match on 5 keys...
2025-12-08 22:08:39,926 [INFO]   0 matches in 0.02s
2025-12-08 22:08:39,928 [INFO] Stage 2: AsOf join (±2s) for 2950 remaining orders...
2025-12-08 22:08:39,960 [WARNING] AsOf merge failed: incompatible merge keys [4] dtype('<M8[ns]') and datetime64[ns, UTC], must be the same type
2025-12-08 22:08:39,961 [INFO]   0 matches in 0.03s
2025-12-08 22:08:39,963 [INFO] Stage 3: Date-only match for 2950 remaining orders...
2025-12-08 22:08:39,987 [INFO]   0 matches in 0.02s
2025-12-08 22:08:39,990 [INFO] Stage 4: Nearest timestamp (±5s) for 2950 remaining orders...
2025-12-08 22:08:40,012 [WARNING] AsOf merge failed: incompatible merge keys [2] dtype('<M8[ns]') and datetime64[ns, UTC], must be the same type
2025-12-08 22:08:40,012 [INFO]   0 matches in 0.02s
2025-12-08 22:08:40,012 [INFO] \u2713 Total matches: 0, Unique enriched orders: 0
2025-12-08 22:08:40,013 [INFO]   Enrichment rate: 0.0%
2025-12-08 22:08:40,100 [INFO] \u2713 Phase 239 complete: C:\Genesis_System3\storage\live\enriched\angel_virtual_orders_with_pnl.csv
2025-12-08 22:08:40,101 [INFO]   Output: 2950 rows
2025-12-08 22:08:40,102 [INFO]   Duration: 0.35s
2025-12-08 22:08:40,102 [INFO] \u2713 Phase 239 completed in 0.35s (within 3.00s target)
2025-12-08 22:08:40,110 [INFO] ======================================================================
2025-12-08 22:08:40,110 [INFO] PIPELINE COMPLETE in 1.35s
2025-12-08 22:08:40,110 [INFO] Report saved: C:\Genesis_System3\storage\live\meta\pipeline_execution_report_20251208_220840.json
2025-12-08 22:08:40,110 [INFO] Phases executed: Phase 220, Phase 221, Phase 239
2025-12-08 22:08:40,110 [INFO] Performance alerts: 0
2025-12-08 22:08:40,110 [INFO] Warnings: 4
2025-12-08 22:08:40,110 [INFO] Errors: 0
2025-12-08 22:08:40,110 [INFO] ======================================================================
```
</details>

## Continuous Validators One-Shot

- Script: `C:\Genesis_System3\phase_e_watchdog.py`
- Exit code: `2`

_stderr:_

```text
usage: phase_e_watchdog.py [-h] [--interval INTERVAL]
                           [--max-checks MAX_CHECKS] [--lock-venv]
                           [--no-lock-venv] [--watch-dir WATCH_DIR]
                           [--log-level {DEBUG,INFO,WARNING,ERROR}]
phase_e_watchdog.py: error: unrecognized arguments: --one-shot
```

**Validator issues:**
- phase_e_watchdog one-shot exited with non-zero status.

## Tomorrow Market-Time Behaviour (Simulation)

- Tomorrow (IST): `2025-12-09`
- Trading day (Mon–Fri): `True`

| Time (IST) | Within 09:15–15:30? |
|-----------|----------------------|
| 2025-12-09T09:10:00+05:30 | No |
| 2025-12-09T09:20:00+05:30 | Yes |
| 2025-12-09T12:00:00+05:30 | Yes |
| 2025-12-09T15:25:00+05:30 | Yes |
| 2025-12-09T15:35:00+05:30 | No |

> Note: Based on static 09:15–15:30 IST rule; real code may add holidays.
