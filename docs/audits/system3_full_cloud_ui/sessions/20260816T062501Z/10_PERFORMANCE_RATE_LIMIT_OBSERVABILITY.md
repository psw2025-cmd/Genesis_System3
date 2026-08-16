# Performance / Rate-limit / Observability

## Live API

- OpenAPI path count: **182**
- Canonical chain path: `/api/chain/{underlying}` (NOT `/api/option_chain` — 404 is wrong probe)
- Broker status latency observed ~33ms; cache_hit true
- Concurrent multi-symbol chain fetch can produce `CHAIN_FETCH_TIMEOUT` / `NO_DHAN_DATA` (F-003)

## Code pacing (main SHA)

- DSM option-chain min gap ~3.4s process-wide
- index_chain_micro_loop round-robin indices; closed-market sleep ~20s
- Dashboard middleware can 429 anonymous non-exempt paths; broker reads exempt when authenticated

## GCP logs (sample)

- Observed **Cloud Run capacity 429** ("no available instance") on genesis optional routes — distinct from Dhan market-data 429.
- Dhan direct OHLC/LTP 429: **NOT_PROVEN in this audit window**.

## Observability gaps

| Event | Detected? | Logged? | Metric? | Alert? | UI? |
|-------|-----------|---------|---------|--------|-----|
| Broker disconnected | yes | likely | partial | NOT_PROVEN | yes |
| Token rotation failed | yes historically | yes | partial | NOT_PROVEN | broker panel |
| Dhan 429 | partial | partial | NOT_PROVEN | NOT_PROVEN | weak |
| Chain incomplete | yes (NO_DHAN_DATA) | yes | partial | NOT_PROVEN | chain strip |
| Serving SHA drift | yes via deploy/info | n/a | no | no | SHA chip |
| Model stale | weak | weak | no | no | WAITING |
