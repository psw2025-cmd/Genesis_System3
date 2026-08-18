# Broker Recovery Live Proof

Observation window UTC: `2026-08-18T09:22:10Z` to `2026-08-18T09:24:58Z`

## Recovery action

- Workflow: `GCP Dhan Token Rotation Manual Recovery`
- Run: `32121086079`
- Result: `success`
- Recovery path: canonical bounded manual rotation with dynamic reload proof

## Historical closure warning

This pack proved a temporary connected window. It is **not** a permanent 906 fix.

At `2026-08-18T10:02:39Z` the same serving SHA recurred to:

- `connected=false`
- `error=DHAN_REQUEST_REJECTED_906`
- `auth_classification=null`
- JWT still valid (`hours_remaining=23.28`, secret version 269)
- probe attempts: docs access-token-only 906, then SDK dhanClientId 906

Permanent correction: do not rotate on 906; do not retry Profile with `dhanClientId` after 906; UI must not paint 906 as token expiry and must not treat `connected=true` as broker-reliability PASS.

## Fresh production API proof

- `GET /api/deploy/info`
  - `git_sha=06103b4abf1ebcb530a43369cff9b8dafc9f5f30`
- `GET /api/broker/status`
  - `connected=true`
  - `auth_classification=AUTH_OK`
  - `profile_source=rest`
  - `live_trading_enabled=false`
  - `order_placement_allowed=false`
- `GET /api/health`
  - `status=ok`
  - `mode=PAPER`
  - `broker_status=connected`
  - `qc_status=PASS`
- `GET /api/auto_gates`
  - `broker_connected=true`
- `GET /api/broker/holdings`
  - `count=11`
- `GET /api/broker/positions/live`
  - `count=1`

## Fresh production UI proof

Production URL: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker`

Fresh broker-tab snapshot showed:

- `Broker Connected`
- `Broker Connection - Dhan`
- `Equity Holdings (11)`
- `Dhan Live Positions (1)`

## Health probe authority note

For this Cloud Run deployment, use `/health` or `/api/health` as the
authoritative application health route.

`/healthz` is platform-intercepted and may return a Google 404 page before the
request reaches FastAPI, so it must not be treated as current app-health truth.

## Safety state

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- No order placement was performed.
