# Instrument Tradability Proof — Phase 8

**Generated:** 2026-07-02 17:25 IST
**Status:** `MARKET_CLOSED_NO_EOD_DATA_YET` — `valid_option_contract_proven: false`

## What happened

`GET /api/chain/NIFTY` returned:
```json
{"underlying":"NIFTY","contracts":[],"spot":0,"pcr":1.0,"total_contracts":0,"data_source":"closed","status":"MARKET_CLOSED","message":"Market closed - live chain fetch skipped in REAL_ONLY mode"}
```

This is **correct, honest behavior** — the system refuses to serve stale/fake option data once the market closes, exactly as required ("Do NOT fake option-chain proof"). It is not a bug.

## Why no contract data is available right now

Market closed at 15:30 IST. The EOD/bhavcopy-derived fallback path is not yet populated because `bhavcopy_download` (scheduled 18:30 IST) hasn't fired yet today.

## Scope note

This blocker is specific to the **options trade path**. It does not block the separate equity forecast/prediction path (see `analyzer_signal_summary.md`), consistent with the required path separation: `CASH_ONLY` equity must not block prediction, only options trade execution.

## Next step

Re-check after 18:45 IST today (post `signal_engine_bhavcopy`), or during market hours tomorrow (2026-07-03) for live data.
