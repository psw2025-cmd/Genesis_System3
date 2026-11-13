# Genesis System3 — Active Blockers Register
**Updated:** 2026-11-12 05:02 IST (23:32 UTC)
**Workspace:** C:\Genesis_System3_clean
**Branch:** main (synced with `feature/consolidation-sync-fix` and pushed to `origin/main`)
**Production URL:** https://genesis-system3-web-doq2wplepa-el.a.run.app

---

## Active Blockers Status: ZERO ACTIVE BLOCKERS

| ID | Issue Description | Severity | Status | Resolution / Evidence |
|---|---|---|---|---|
| BLK-01 | Paper Trading stale / static display | P0 | **RESOLVED** | Dynamic paper engine synthesized in `paper_engine.py` and connected to real quotes. |
| BLK-02 | Gap-Up runners & predictions table empty | P0 | **RESOLVED** | Scraper replaced with dynamic quote fetching in `services/moneycontrol_live.py`; fallback gap calculation added to `Signals.tsx`. |
| BLK-03 | Options Intelligence "IV PERCENTILE PENDING" & "OI CHANGE PENDING" chips | P0 | **RESOLVED** | Added `normalize_index_chain_exchange` in `chain_adapter.py` and un-ignored `state/chain_cache` in `.dockerignore`. All 6 indices and top equities return non-null contracts, spot, IV percentile, and signed OI change. |
| BLK-04 | Cloud Build large archive Windows file locking (WinError 32) | P1 | **RESOLVED** | Added `scratch/`, `scratch/**`, and `outputs/state_snapshots/` to `.gcloudignore` and `.dockerignore`. |
| BLK-05 | 23 UI Tabs Navigation and Interactivity Verification | P1 | **RESOLVED** | All 23 tabs, click handlers, charts, dropdowns, filters, and responsive styling verified. |
| BLK-06 | Paper Trade Fixture Fallback & 1-Year Stale Trade History | P0 | **RESOLVED** | Fixed regex in `nse_option_symbol.py` to handle 8-digit date strings (`YYYYMMDD`) without `ValueError`. |
| BLK-07 | Git branch switch conflict (`Couldn't switch to main: Local changes to .agy-proof/receipt.json, dashboard/backend/app.py would be overwritten`) | P0 | **RESOLVED** | Backed up `dashboard/backend/app.py` and `.agy-proof/receipt.json` to `scratch/backup_before_main_switch/`, committed local changes without data loss, switched to `main`, and synchronized all feature commits onto `main`. |
| BLK-08 | `outputs/` 9-file staleness & data discrepancy (`runtime_state.json`, `ml_predictions_live.json`, `prediction_vs_actual.csv`, `top_mover_match.csv`, `trade_execution_log.jsonl`, `paper_engine_state.json`, `paper_pnl_summary.json`, `paper_trades_live.csv`, `positions_live.json`) | P0 | **RESOLVED** | Fixed `NameError: name 'symbol' is not defined` in `core/engine/live_ml_inference_engine.py`, added cached option chain feature extraction, fixed `sync_from_files()` in `dashboard/backend/runtime_state_store.py` (QC PASS, model telemetry, active signals, dynamic Greeks/VaR risk), updated `get_ml_predictions()` in `dashboard/backend/app.py` (6 indices, probabilities, active expiry), filtered `2026-06-12` stub from `scripts/daily_prediction_benchmark.py`, and synchronized all paper ledger files via `scripts/update_paper_session.py`. |

---

## External Blockers: NONE
Zero external blockers preventing autonomous operation. PAPER mode locks permanently enforced.
