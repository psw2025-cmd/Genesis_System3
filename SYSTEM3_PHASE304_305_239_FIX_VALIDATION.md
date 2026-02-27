# SYSTEM3 PHASE 304/305/239 FIX VALIDATION (2025-12-08 16:25)

## Summary
- Forward signals regenerated (Phase 221) with auto-heal: **297 rows**, side normalized (BUY/SELL/HOLD).
- Reconciled signals regenerated (Phase 225): **297 rows**, **182** label discrepancies (expected from reconciliation rules).
- PnL enrichment (Phase 239) executed: **2950** virtual orders, **1253 matched (42.5%)**, **1697 unmatched** → status **ERROR** (match rate < 50%).
- Integrity tests: forward signals still have **200/297 valid timestamps** (97 missing), expiry NaN ~33.7%.

## Forward Signals Integrity
- File: `storage/live/angel_index_ai_signals_with_forward.csv`
- Rows: 297; Size: ~0.30 MB
- `ts` valid: **200/297** (97 NaN)
- `side` distribution: {SELL: 162, BUY: 134, HOLD: 1}
- Key columns NaN: expiry 33.7% (underlying/strike 0%)
- Forward returns: fwd_ret_1 populated for 38.4% rows (fwd_ret_3/5 empty in source)

## Reconciled Signals
- File: `storage/live/angel_index_ai_signals_reconciled.csv`
- Rows: 297; Discrepancies: 182
- Uses healed `ts` from Phase 221 output

## Virtual Orders
- File: `storage/live/angel_virtual_orders.csv`
- Total orders: **2950**
  - 2025-11-30: 105
  - 2025-12-06: 2639
  - 2025-12-07: 77
  - 2025-12-08: 129

## PnL Enrichment (Phase 239)
- Input orders: 2950
- Matched: **1253 (42.5%)**
- Unmatched: 1697
- Status: **ERROR** (due to match rate <50%)
- Join diagnostics created if match rate <10% (not triggered this run)
- Remaining blocker: **97 forward-signal rows missing ts + 33% expiry NaN** → prevents full join.

## Remaining Issues / Next Steps
1) **Fill remaining ts gaps (97 rows)** in `angel_index_ai_signals_curated.csv` (source) or upstream generator.
   - Root cause: source curated data has 97 missing ts; only 200/297 have timestamps.
2) **Reduce expiry NaN (33.7%)** to improve join keys.
3) Re-run Phases 221 → 225 → 239 after ts/expiry are fixed; expect match rate >80%.

## Commands Executed
- Phase 221: `venv\Scripts\python.exe core\engine\system3_phase221_forward_returns.py`
- Phase 225: `venv\Scripts\python.exe core\engine\system3_phase225_label_reconciliation.py`
- Integrity test: `venv\Scripts\python.exe tests\test_forward_signal_integrity.py`
- PnL enrichment: `venv\Scripts\python.exe system3_virtual_trades_enrichment.py`
- Per-date counts: `venv\Scripts\python.exe -c "... value_counts() ..."`

## Proof of Current State
- Forward signals: ts valid 200/297; side normalized BUY/SELL/HOLD; 97 ts missing remain.
- PnL: 2950 orders processed; 1253 matched (42.5%); unmatched 1697 → join still limited by missing ts/expiry in forward signals.
