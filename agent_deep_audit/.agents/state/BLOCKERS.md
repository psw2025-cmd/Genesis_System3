# Genesis System3 — Active Blockers & Risks
**Updated:** 2026-11-02 23:00 UTC

## Critical Blockers
- **None**: All 5 Priority 0 Requirements (R1–R5) are passing under independent Evidence Gate verification for turn `eee0a08069af47198b31da16189f3fd6`.

## Operational Notes
- **Dhan API Token Renewal**:
  - Live quote streaming from Dhan requires a valid 24-hour access token in `.secrets/dhan.env`.
  - Outside market hours (15:30 to 09:15 IST) or when the token expires, the system automatically falls back to authentic EOD settlement snapshots in `state/chain_cache/` (`BROKER_EOD_SETTLED`).
  - No synthetic or mock quotes are generated.
- **Port 8008 Persistent Daemon**:
  - Running via Python 3.12 uvicorn daemon (`PID active`).
  - Hard refresh (Ctrl + F5) in browser is recommended if Chrome served a cached version of `premium.html`.
