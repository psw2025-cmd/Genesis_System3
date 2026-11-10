# Production Broker Health Closure

**Verdict:** `BROKER_HEALTH_CONFIRMED`  
**Evidence window:** 2026-08-17 04:05–04:18 UTC (09:35–09:48 IST)  
**Production:** `genesis-system3-web`, `asia-south1`, project
`system3-openalgo-safe`

This is request-scoped evidence. It confirms Dhan broker health and read-only
market-data flow; it does not declare all strategy proof gates READY.

## Pre-recovery analysis

- Production SHA matched GitHub `main`:
  `4185162b2b6dd69beb034c4cf84aec4dda95900b`.
- `/api/broker/status`: disconnected with `DHAN_REQUEST_REJECTED_906`,
  canonical secret v261.
- `/api/health`: `not_ready`, broker disconnected.
- Scheduled Job was Ready and had executed successfully, but runtime validation
  still failed. A green execution alone was therefore insufficient.
- Safety locks passed: LIVE=false and order placement disabled.

## Recovery

- Used the canonical manual recovery workflow with bounded force input:
  https://github.com/psw2025-cmd/Genesis_System3/actions/runs/31993268520
- The workflow invoked `genesis-system3-dhan-token-rotate`, validated the minted
  token, created canonical secret v262, and proved dynamic reload.
- No order endpoint was called and no token value was exposed.

## Post-recovery checklist

- [x] Broker API: connected, no error, analyzer mode.
- [x] Secret source: `GCP_SECRET_MANAGER_DYNAMIC`, canonical v262.
- [x] Health API: `status=ok`, broker connected, market open, live data source.
- [x] Batch market data: health OK and broker connected.
- [x] Gain rank: current date, 25 rows, 25 verified spots.
- [x] NIFTY chain: positive Dhan spot and populated strike data.
- [x] BANKNIFTY chain: positive Dhan spot and populated strike data.
- [x] Fresh browser Overview: `Dhan · Connected`, market open, live spots.
- [x] Fresh browser Broker tab: Broker Connected and read-only account surfaces.
- [x] Fresh browser Option Chain: populated Dhan strikes/contracts.
- [x] Cloud Run revision `genesis-system3-web-00425-dec` receives 100% traffic.
- [x] Serving SHA equals GitHub `main`.
- [x] Scheduler enabled at 07:30 IST; rotation Job Ready.
- [x] Legacy aliases have quarantine labels, all inspected versions disabled,
  and no Cloud Run service/Job consumers.
- [x] GitHub repository has no Dhan token secret aliases.
- [x] LIVE=false; `order_placement_allowed=false`.

## Measured evidence

- Broker latency: 31 ms.
- NIFTY spot observed: 24,296.95.
- BANKNIFTY spot observed: 57,279.55.
- Fresh UI capture settled at 2026-08-17 04:10 UTC and agreed with API truth.
- Recovery secret v262 created at 2026-08-17 04:06:38 UTC.

## Remaining non-broker blockers

- Overall proof gates remain 6/7 in the presentation contract.
- ML Spearman has only 1 passing day against the required 5.
- Strategy/paper expectancy and other core gate evidence remain fail-closed in
  the detailed gate payload.
- `/api/system_health` reports no in-process scheduler daemon/jobs; the
  authoritative GCP token scheduler is enabled. This is a separate visibility
  contract, not a broker-auth failure.

## Acceptance result

`BROKER_HEALTH_CONFIRMED` because API, Dhan market data, UI, Secret Manager,
Cloud Run, GitHub provenance, scheduler/Job authority, and safety locks agree
within the same request-scoped evidence window.
