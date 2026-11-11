# Genesis System3 — Active Blockers & Risks
**Updated:** 2026-11-04 09:27 UTC (14:57 IST)

## Active External Blockers & Future Observation Windows (`10 BLOCKED`, `7 NOT_VERIFIED`)
1. **Cloud Deployment, Cloud Scheduler & Remote GCP Mutations (`PEND-032`, `PEND-033`, `PEND-043`, `PEND-044`, `PEND-073`, `PEND-092`, `G18`, `G19`, `G24` — `BLOCKED`)**:
   - Blocked by **Owner Instruction 9** (*"Do not merge, deploy, rotate credentials, or modify cloud resources without explicit approval"*) and **AGENTS.md Rule 0** (*"Local First, Cloud Second"*).
   - **Next Safe Action**: When ready to promote the verified local port 8008 codebase (`fix/scanner-219-equity-rotate`) to Cloud Run (`asia-south1`), owner provides explicit approval for cloud deployment.
2. **Local PostgreSQL/TimescaleDB & Redis Provisioning (`PEND-029`, `PEND-030`, `G17`, `G25` — `BLOCKED`)**:
   - No local PostgreSQL (`127.0.0.1:5432`) or Redis (`127.0.0.1:6379`) server is provisioned on the laptop; local runtime uses SQLite (`sandbox.db`) + SHA-256 verified JSON snapshots (`state/chain_cache/*.json`, `state/gain_rank_history.json`).
3. **Multi-Day Future Market Observation Windows (`PEND-015`, `PEND-016`, `PEND-019`, `PEND-020`, `PEND-042`, `G09`, `G12` — `NOT_VERIFIED`)**:
   - `state/gain_rank_history.json` has `58` pre-event predictions across `15` batches (`2026-11-02`), and `analyzer_paper_lifecycle_proof` has `1` completed paper trade (`Net -₹15.00`).
   - Accumulating `>=5` closed paper trades across `5+` live trading days and maturing post-session directional hit rates requires future live market sessions (never fabricated or time-accelerated).

## Resolved Local Blockers (`103 PASS`)
- **GET `/api/v1/placeorder` HTTP 405 Method Not Allowed (Resolved)**: Returns HTTP 200 gateway status on `GET` and HTTP 403 Safety Gate Block on `POST`.
- **Main Chart `ReferenceError: niftyResp is not defined` & Broken `.command-grid` Layout (Resolved)**: Restored 60-candle chart, live ticking clock, 3-column layout, and `/ws/stream` on port 8008 with 0 console errors.
- **Dhan Holdings & Funds Double-Nested SDK Unwrapping (Resolved)**: All 11 live Demat holdings (`₹3,49,655.36` current, `₹3,21,609.62` invested, `+₹28,045.74 / +8.72%` P&L) populate Tab 2.
- **Port 8008 Prototype Endpoints & 404s on `/api/chain/NIFTY` and `/api/market/top-gainers` (Resolved)**: Reconciled `/api/health`, `/api/market/inventory`, `/api/data/provenance`, `/api/ml/prediction-audit`, `/api/paper/ledger`, `/api/options/gainers`, `/api/chain/{symbol}`, and `/api/market/top-gainers`.
- **Bare-Except Zero-P&L Masking & Naive Timestamps (Resolved)**: Fixed in `dashboard/backend/app.py`, `greeks_calculator.py`, `paper_pipeline_v8.py`, `runtime_state_store.py`, and `services/moneycontrol_live.py`.

## Constitutional Safety Posture
- `ANALYZE_MODE=1`
- `PAPER_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `LIVE_ORDER_AUTHORITY=0`
