# SYSTEM3 PHASES 331-360: DATA PROFILE (LOW-VOLUME ANALYSIS)

**Date:** 2025-12-07
**Purpose:** Describe current live data feeding phases 339/340 and explain Phase 340 failure condition.

## Key CSV Snapshots (read-only)
- `storage/live/angel_index_ai_signals.csv`: rows=100, cols=90 (rich feature set, includes fwd_ret_1/3/5, etc.)
- `storage/live/angel_index_ai_signals_curated.csv`: rows=5, cols=90
- `storage/live/angel_index_ai_signals_with_forward.csv`: rows=5, cols=90
- `storage/live/angel_virtual_orders.csv`: rows=2,686, cols=15
- `storage/live/angel_index_ai_pnl_log.csv`: rows=3, cols=15
- `storage/live/diagnostics/model_drift_report.csv`: **missing**

## Low-Volume Finding
- Phase 340 currently reads signal volume from Phase 332 summary → total_rows=5 (from curated/with_forward signals), which is **below the threshold 30**.
- As of the latest block test, this triggered `Signal count too low: 5 < 30` in Phase 340 and blocked the suite.
- Data is structurally present (no tokenization errors), but sample size is too small for regression guard confidence.

## Columns (signal CSVs)
- 90 columns present (not the trimmed 72-column schema). Includes feature set: greeks, technicals, forward returns (fwd_ret_1/3/5), timestamps, probabilities, labels, expiry, etc.

## Conclusion (root cause for 340)
- **Root cause:** Only 5 qualifying signals available (threshold=30). This is a low-signal-day scenario, not corruption.
- **Missing artifact:** `model_drift_report.csv` absent; not required for low-volume decision but flagged in health summary.
