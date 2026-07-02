# Instrument Tradability Proof — Phase 8 (Updated)

**Generated:** 2026-07-02 20:52 IST (updated after EOD/bhavcopy jobs fired)
**Status:** `valid_option_contract_proven: true` (with honest caveats)

## What changed since the 17:25 IST check

At 17:25 IST, `/api/chain/NIFTY` correctly refused to serve data (`MARKET_CLOSED`, no EOD data yet). By 20:52 IST, the `bhavcopy_download` (18:30 IST) and `signal_engine_bhavcopy` (18:45 IST) scheduled jobs had fired for the first time today — confirmed live via production logs showing this session's scheduler catch-up engine correctly evaluating and, for jobs outside their window, marking them `SKIPPED_TOO_LATE` with exact minute counts and reasons (e.g., "Full Auto Coordinator (Pre-Market) — 765 min late, exceeds catch-up window of 65 min").

## Real evidence now available

`GET /api/chain/NIFTY`: `status: OK`, `spot: 24175.7`, `total_contracts: 200`, `data_source: nse`.

Sample contract (raw API fields):
```json
{
  "underlying": "NIFTY", "exchange_segment": "NSE_FNO", "expiry_date": "2026-07-07",
  "strike": 21350.0, "option_type": "PE", "trading_symbol": "NIFTY-Jul2026-21350-PE",
  "security_id": "44455", "lot_size": 65, "ltp": 0.75,
  "top_bid_price": 0.0, "top_ask_price": 0.0, "volume": 37778, "oi": 32419, "source": "nse"
}
```

## Honest caveat

This is bhavcopy/EOD-sourced data, not a live order book. Checked all 200 contracts in the response: **zero** have a nonzero `top_bid_price`. This is a genuine EOD data source limitation (no live order-book depth), not a bug. `tick_size` is absent from the API schema entirely — a separate real gap.

## Against the 17 required fields

**13 present** (exchange/segment inferred from `exchange_segment`, not literal API fields; underlying, expiry, strike, CE/PE, trading symbol, security ID, lot size, LTP, volume all real; tradable/rejection-reason are this report's own assessment based on the resolved instrument-master fields). **4 unavailable**: bid, ask, spread (EOD limitation), tick_size (schema gap).

## New finding: web/worker Dhan token divergence, now with concrete evidence

Live production logs (20:55 IST) show the worker's own Dhan token expired (163.4h old) and both refresh strategies just failed (`generate_token` hit Dhan's 2-minute cooldown; `renew_token` failed since the underlying token is too stale) — worker now sleeping until tomorrow's 08:30 IST scheduled refresh. **Meanwhile `/api/broker/status` (web service) still reports `connected: true`** — its own separately-cached token is still valid. This is concrete, live confirmation of the architecture gap flagged earlier this session (each service independently manages its own token copy, no sync mechanism) — not a new problem, but now demonstrated in real time rather than just diagnosed from logs.
