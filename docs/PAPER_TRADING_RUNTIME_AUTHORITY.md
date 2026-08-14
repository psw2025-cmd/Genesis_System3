# Paper Trading Runtime Authority

**Authority rule:** This file defines how Paper Trading status is determined. It does **not** itself declare production success.

## Current authority

Paper Trading is considered **PROVEN** only when all of these facts are true for the same deployed Git SHA on the authoritative Google Cloud runtime:

1. `GET /api/paper` returns HTTP 200 with:
   - `positions_source = FIRESTORE_PAPER_LEDGER`
   - `paper_truth.durable = true`
   - `live_trading_enabled = false`
   - `broker_order_endpoints_called = false`
2. The bounded Cloud Run job `genesis-system3-paper` has a successful execution for the deployed image/SHA.
3. Cloud Scheduler `genesis-system3-paper-market` matches the scheduler SSOT contract and invokes only that bounded job.
4. Firestore recovers the same Paper state after a fresh process/job instance; container-local files are not production authority.
5. A real Paper lifecycle event is not claimed unless immutable Firestore evidence proves the event. No signal→entry→exit→PnL success may be inferred from an HTTP 200 or an empty UI.
6. The deployed browser proof opens the Paper tab and reaches `data-paper-proof-state="settled"` with `data-paper-ledger-source="FIRESTORE_PAPER_LEDGER"` on desktop and mobile.
7. The proof rejects persistent `Loading…`, network/error text, thin/blank content, synthetic/fallback truth, and missing Firestore provenance.
8. LIVE broker order placement/modification/cancellation remains disabled. Paper fills are local simulation only; Dhan is read-only market-data/provenance input.

## Runtime components

| Purpose | Authoritative component |
|---|---|
| Paper execution tick | `scripts/gcp_paper_job.py` → `dashboard/backend/durable_paper_job.py` |
| Durable ledger | `dashboard/backend/paper_ledger_backend.py` / Firestore |
| Public Paper API | `dashboard/backend/secure_app.py` → `/api/paper` |
| Paper UI | `dashboard/frontend/src/components/PaperTrading.tsx` |
| Deployed semantic proof | `scripts/gcp_ui_tab_visual_proof.py` |
| Scheduler contract | `dashboard/backend/scheduler_contract.py` |
| Canonical GCP deploy | `.github/workflows/cloud-run-auto-deploy.yml` |

## Forbidden success shortcuts

The following are **not sufficient** to declare Paper Trading successful:

- a Markdown file containing `COMPLETE`, `READY`, or `SUCCESS`;
- source files merely existing;
- a Vite/frontend build succeeding;
- `/api/paper` returning HTTP 200 without durable fields;
- a screenshot existing while the tab still says `Loading`;
- container-local `positions_live.json`, `pnl_live.json`, or `paper_engine_state.json`;
- a signal being generated without a proven paper entry/exit lifecycle;
- historical simulation/replay results being presented as current Cloud Run truth.

## Historical documentation

The January 31, 2026 files below are historical snapshots only and are explicitly superseded as current-status authorities:

- `docs/CURRENT_STATUS_PAPER_TRADING.md`
- `docs/PAPER_TRADING_INTEGRATION_COMPLETE.md`

Their contradictory claims were the reason this authority rule was created. Git history preserves their original contents.

## Safety lock

Production remains ANALYZER/PAPER only:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`

No documentation, test fixture, retry/self-heal mechanism, monitoring alert, or UI state may override those locks.
