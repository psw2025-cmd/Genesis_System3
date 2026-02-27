# SYSTEM3 PHASES 331-360: GATE STATUS (POST 13:45 UTC RUN)

**Latest block test:** PASS (2025-12-07 13:45 UTC) — OK 23, WARN 7, ERROR 0. DRY-RUN enforced.
**Log:** `logs/block_test_331_360_20251207_134502.log`
**Verifier:** `verify_phases_331_360_implementation.py` PASS at 13:45 UTC.

## Phase Status Snapshot
- OK (23): 331, 333, 335, 336, 337, 341, 342, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360.
- WARN (7): 332, 334, 338, 339, 340, 343, 344.
- ERROR: none.

## WARN Reasons (actionable)
- 332 Signal Volume: total 5 rows (<50 threshold); per-index shortfalls (SENSEX 2, MIDCPNIFTY 2, FINNIFTY 1); missing NIFTY/BANKNIFTY.
- 334 Model Drift Snapshot: small sample (5 rows) -> WARN.
- 338 Correlation: insufficient data (5 valid rows).
- 339 Daily Pipeline Summary: propagates low-volume WARNs; unable to read `model_drift_daily.csv` cleanly.
- 340 Regression Guard: DRY-RUN low-volume WARN path triggered (5 < 30); no blocking errors.
- 343 Signals Freshness: signals CSV age ~128 minutes; marked WARN.
- 344 Pipeline Schema Guard: missing columns in `angel_virtual_orders.csv` (`order_id`, `signal`, `qty`, `entry_price`) and `angel_index_ai_pnl_log.csv` (`pnl`).

## Outstanding Data Gaps
- `model_drift_report.csv` still missing (output check).
- Signal set is extremely small (5 curated rows), causing cascading WARNs and low-volume gate WARN in 340.
- Stale inputs flagged in 343 and schema gaps in 344.

## Next Steps
1) Backfill/ingest more signals to clear 332/334/338/339/340 volume warnings.
2) Restore required columns in `angel_virtual_orders.csv` and `angel_index_ai_pnl_log.csv`.
3) Refresh signals feed to clear freshness warning (343) and regenerate `model_drift_report.csv`.
4) Re-run: `& .\venv\Scripts\python.exe tools\run_phases_331_360_block_test.py` and `& .\venv\Scripts\python.exe verify_phases_331_360_implementation.py`.
