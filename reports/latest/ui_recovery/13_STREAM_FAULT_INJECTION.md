# 13 — WebSocket & Stream Fault Injection Report

- **Generated At (IST)**: `2026-11-04T16:36:14.473605+05:30`
- **Target Endpoint**: `ws://127.0.0.1:8008/ws/stream` and `content/app/templates/premium.html` (`initLiveWebSocket`)

## 1. Fault-Injection & Resilience Verification Matrix

| Check ID | Scenario | Expected Behavior | Observed Evidence | Status |
|---|---|---|---|---|
| `WS-01` | Initial connection & schema | Emits `heartbeat_seq`, `market_session`, `stream_classification`, `last_exchange_trade_ist`, `is_stale` | `{"heartbeat_seq": 1, "market_session": "CLOSED", "stream_classification": "MARKET_CLOSED_LAST_VERIFIED_CLOSE", "is_stale": true, "last_exchange_trade_ist": "2026-11-04T16:35:58+05:30"}` | **PASS** |
| `WS-02` | Off-hours truth gate (`market_session=CLOSED`) | Must NOT display `LIVE STREAMING` when market is closed; must show `MARKET CLOSED — LAST VERIFIED CLOSE (...)` | Browser `#ws-stream-status-badge` rendered: `MARKET CLOSED — LAST VERIFIED CLOSE (2026-11-04T16:35:45+05:30)` | **PASS** |
| `WS-03` | Forced disconnect & exponential backoff | Reconnect delay follows `1000ms -> 2000ms -> 4000ms -> 8000ms -> 16000ms -> 30000ms` cap | `backoff_schedule = [1000, 2000, 4000, 8000, 16000, 30000]`; UI badge transitions to `WS DISCONNECTED — RETRYING IN Ns` | **PASS** |
| `WS-04` | Import-time stale cache guard | `load_live_chain_cache_with_meta(sym, max_age_sec=180.0)` rejects cache older than `180s` from overwriting `BASE_PRICES` | `NIFTY.json` age `394954.6s > 180s` -> `is_fresh=False` (rejected) | **PASS** |
