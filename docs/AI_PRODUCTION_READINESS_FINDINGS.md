# AI Production Readiness Findings

**Purpose:** Single living audit file for micro-level observations, blockers, warnings, dashboard findings, recommendations, proof-truth rules, and action protocol for Genesis System3 production-grade real trading readiness.

**Safety rule:** This file must not contain secrets, tokens, broker credentials, PINs, TOTP seeds, access keys, private account values, or raw personal/broker data.

**Intended users:** Pritam, Claude, Cursor, Gemini, Codex, and any future repo agent.

---

## Living file update protocol

Every agent must update this same file instead of scattering conclusions across chat, temporary logs, or untracked files.

### Required update format

Each new update must append under `Update log` using this format:

```text
YYYY-MM-DD HH:MM IST | agent | commit/ref checked | area | finding/action | proof path | status
```

### Required proof rule

No PASS may be written unless the proof is one of:

- committed repo proof artifact path
- Render endpoint response path/artifact
- CI/job log artifact
- local command output copied into a committed proof file
- user-provided screenshot/log clearly identified as user-provided runtime evidence

If proof is not available, use one of these statuses:

- `NOT_PROVEN`
- `NEEDS_RUNTIME_PROOF`
- `NEEDS_RENDER_LOGS`
- `NEEDS_MARKET_OPEN`
- `NEEDS_BROKER_RUNTIME`

---

## Update log

| Time IST | Agent | Commit/ref checked | Area | Finding/action | Proof path | Status |
|---|---|---|---|---|---|---|
| 2026-06-14 21:58 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | initial audit | Created living production readiness audit file | `docs/AI_PRODUCTION_READINESS_FINDINGS.md` | DONE |
| 2026-06-14 22:02 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | Claude protocol | Added proof-truth, self-verification, dashboard, and action rules for Claude/agents | this file | DONE |

---

## Audit baseline

- **Repo:** `psw2025-cmd/Genesis_System3`
- **Baseline `main` commit inspected:** `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01`
- **Primary observed mode:** Analyzer/Paper.
- **Observed live trading state:** Disabled.
- **Current high-level verdict:** Cloud Analyzer/Paper readiness is improving, but production-grade real-money trading is not ready.

---

## Capability and limitation statement

### What can be checked from GitHub/repo proof

- Latest committed code and reports.
- Proof matrices and generated JSON artifacts.
- Render configuration stored in `render.yaml`.
- Dashboard backend/frontend source.
- Scheduler configuration and job-runner compatibility.
- Safety flags, hardcoded live-disabled settings, and placeholder execution modules.
- Public endpoint coverage artifacts committed to repo.

### What cannot be fully proven from repo alone

- Current Render secret values.
- Current Dhan token value or expiry internals.
- Render worker live logs unless exported/provided.
- True market-open behavior before market opens.
- Broker orderbook/tradebook/position truth without broker runtime proof.
- Real live order placement, because live trading is disabled and wrapper is placeholder.

---

# Current truth summary

## Current PASS / improvement items

- Render backend is reachable.
- Dashboard UI loads.
- Dhan broker connectivity appears fixed in latest endpoint coverage.
- `/api/broker/status` proof shows broker connected and no broker error in latest endpoint coverage.
- Live trading is off.
- Real order placement is blocked.
- Proof matrix has 8 published gates.
- Backtest/walk-forward proof now reports PASS with cost/slippage included.
- Model training/load proof reports fresh training metrics proven, but promotion remains blocked.
- Dashboard endpoint coverage exists.
- HEAD `/` 405 issue was reportedly fixed by latest Claude commit.

## Current production-grade blockers

- `trade_ready` remains false.
- Full pipeline still blocks on `live_market_analyzer_paper_trade_not_proven`.
- Real live order wrapper is still a skeleton / NOT_IMPLEMENTED.
- `/api/state` still reports `data_source: SYNTHETIC` in latest endpoint coverage.
- Health/state source truth is inconsistent: health says live, state says synthetic.
- Lifecycle proof can mark fallback/weekend/simulated paper path as PASS.
- Live option-chain/tradability proof is missing.
- Real market-day signal -> paper order -> real LTP exit -> charges -> net P&L is not proven.
- Dashboard browser visual truth remains not proven.
- API/DB/report reconciliation remains not proven.
- Model promotion policy is missing/blocked.
- Persistent storage is not enabled in `render.yaml`.
- Worker runtime logs and heartbeats are not proven from repo alone.
- Dashboard/API production auth is not proven.
- Public docs remain reachable unless protected outside the repo.

---

# Claude / agent self-verification protocol

Claude must read this section before making any future readiness claim.

## Rule 1 - Never call simulated proof production proof

A lifecycle proof is **not production-grade** if any of these are true:

- `market_status` contains weekend, holiday, pre-market, post-market, or closed.
- `dry_run=true`.
- `force=true`.
- `instrument_token` is `DRY_RUN_TOKEN`, `FALLBACK_TOKEN`, missing, or not broker-verified.
- `source` contains fallback, synthetic, mock, dry-run, sample, seeded, or fixture.
- exit price is generated by formula instead of real market quote/LTP.
- broker connection is checked only by public status endpoint and not linked to real quote/tradebook proof.
- paper fill has no quote timestamp and no live LTP timestamp.

If any are true, lifecycle status can be at most:

```text
PASS_WITH_WARNINGS
```

It must not clear production readiness.

## Rule 2 - Production-ready lifecycle PASS requirements

A real market analyzer/paper lifecycle proof requires all of the following:

- Market is open during NSE/BSE options market hours.
- Broker is connected.
- Real live quote or option-chain data is present.
- Signal source is non-fallback and non-synthetic.
- Instrument token is verified against broker/NSE option universe.
- Expiry and strike are valid and tradable.
- Bid/ask or LTP exists and is fresh.
- Spread and liquidity are checked.
- Paper order is created with real quote timestamp.
- Paper fill is simulated using real quote/LTP, not fixed formula.
- Exit price is based on real quote/LTP stream or a documented market quote snapshot.
- Charges, brokerage, slippage, gross P&L, and net P&L are calculated.
- Order/fill/exit/P&L are reconciled.
- Dashboard shows the same counts and P&L as the report.
- No live order is placed.

## Rule 3 - Production dashboard PASS requirements

Dashboard is not production-grade unless it visibly shows:

- Broker connection: connected/disconnected.
- Data source: broker-live/synthetic/fallback.
- Market status: open/closed/holiday.
- Live trading: off/on.
- Real order placement: blocked/allowed.
- Latest quote timestamp and age.
- Latest signal timestamp and source.
- Current contract validation: underlying, expiry, strike, token, lot size, bid, ask, spread.
- Latest paper lifecycle status.
- Broker/order/position reconciliation.
- Daily P&L and risk limits.
- Proof matrix status.
- Production readiness status.

The UI must show red/not-ready if:

- data source is synthetic
- broker disconnected
- market closed
- no live signal
- no real option contract proof
- proof matrix trade_ready is false

## Rule 4 - Official `trade_ready` is the final authority

Even if a component says PASS, production real trading is blocked unless all of these are true:

- `reports/latest/proof_status_matrix/proof_status_matrix.json` has `trade_ready: true`
- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json` has `trade_ready: true`
- live order wrapper is implemented and tested
- risk manager passes
- dashboard truth passes
- broker reconciliation passes
- explicit user approval exists

## Rule 5 - Do not enable live trading from automation

No agent should set these to true/1 without explicit user instruction and complete proof trail:

- `LIVE_TRADING_ENABLED`
- `USE_LIVE_EXECUTION_ENGINE`
- `SYSTEM3_LIVE_TRADING_ALLOWED`

---

# Detailed findings

## A. Hard blockers for production-grade real trading

### B01 - Live trading is intentionally disabled

**Evidence paths:**

- `config/live_trade_config.py`
- `render.yaml`
- `reports/latest/proof_status_matrix/proof_status_matrix.json`

**Observation:** Live trading flags remain off by design:

- `LIVE_TRADING_ENABLED = False`
- `USE_LIVE_EXECUTION_ENGINE = False`
- Render env keeps `LIVE_TRADING_ENABLED=0` and `SYSTEM3_LIVE_TRADING_ALLOWED=0`.

**Impact:** Production real trade cannot occur until a controlled approval process enables live trading after proof gates pass.

**Recommendation:** Do not enable live flags until 5+ market-day analyzer/paper proofs, broker reconciliation, model acceptance, risk controls, and dashboard truth are proven.

---

### B02 - Real Dhan order execution wrapper is not implemented

**Evidence path:**

- `core/broker/dhan_live_order_wrapper.py`

**Observation:** The wrapper is still a skeleton. It returns dry-run IDs in dry mode and returns `NOT_IMPLEMENTED - Real DhanHQ integration pending` outside dry-run.

**Impact:** Even if live flags are turned on, real order placement/cancel/status is not production implemented.

**Recommendation:** Implement Dhan order placement, cancel, and status refresh only after analyzer/paper proof is stable. Add mandatory safety gates before any real order call.

---

### B03 - Official pipeline still says trade-ready false

**Evidence path:**

- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`

**Observation:** Latest report still shows:

- `trade_ready: false`
- `verdict: NOT_TRADE_READY_UNTIL_BLOCKERS_PROVEN_CLEAR`
- blocker: `live_market_analyzer_paper_trade_not_proven`

**Impact:** The system's own official readiness gate blocks real trading.

**Recommendation:** Keep final readiness blocked until real market-day paper lifecycle is proven with broker connected, non-fallback signal, real quote/LTP, real option token, and reconciled net P&L.

---

## B. Market/data blockers

### D01 - `/api/state` still shows synthetic data

**Evidence path:**

- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`

**Observation:** Broker connection is shown as connected in endpoint coverage, but `/api/state` reports `data_source: SYNTHETIC`.

**Impact:** Production trade decisioning must not rely on synthetic state.

**Recommendation:** Enforce a hard production blocker if `/api/state.data_source` is not real broker/live-confirmed. Add visible dashboard red banner: `SYNTHETIC DATA - NOT TRADE READY`.

---

### D02 - Health and state data-source truth are inconsistent

**Evidence path:**

- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`

**Observation:** `/api/health` says data source is live, but `/api/state` says data source is synthetic.

**Impact:** Production trading requires a single source of truth. Inconsistent health/state can mislead the operator.

**Recommendation:** Define authoritative runtime state and make all endpoints derive from it. Fail dashboard readiness if endpoint truth disagrees.

---

### D03 - Live option-chain tradability proof is missing

**Evidence path:**

- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`

**Observation:** Current state does not prove non-zero contracts, underlyings, live option tokens, spreads, expiry, or strike tradability.

**Impact:** Options trading can fail or select non-tradable/illiquid contracts.

**Recommendation:** Before any trade-ready status, prove: underlying, expiry, strike, instrument token, bid/ask/ltp, spread, lot size, freeze quantity, and F&O eligibility.

---

## C. Lifecycle proof governance blockers

### L01 - Lifecycle proof can pass fallback/weekend simulated flow

**Evidence paths:**

- `scripts/paper_lifecycle_proof.py`
- `reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_162812.json`
- `reports/latest/analyzer_paper_lifecycle_proof/summary.json`

**Observation:** A lifecycle artifact is marked `PASS` even though it used:

- `market_status: Weekend (Sunday)`
- `instrument_token: FALLBACK_TOKEN`
- `source: BHAVCOPY_FALLBACK`
- simulated paper exit

**Impact:** This can falsely clear readiness even without real market, real contract, or real LTP/exit proof.

**Recommendation:** Update proof logic so `PASS` requires all of:

- market open
- broker connected
- non-fallback signal
- real instrument token
- real quote/LTP timestamp
- real paper fill model
- real exit price from quote stream
- full charges and net P&L calculation
- no `--force` and no dry-run

Fallback/weekend/simulation should be `PASS_WITH_WARNINGS` at best and must not clear production readiness.

---

### L02 - Mandatory lifecycle fields are incomplete

**Evidence path:**

- `scripts/paper_lifecycle_proof.py`

**Observation:** Current mandatory field check is weaker than production lifecycle needs.

**Impact:** A lifecycle proof can pass without full execution audit fields.

**Recommendation:** Mandatory proof fields should include:

- `signal_id`
- `symbol`
- `underlying`
- `instrument_token`
- `expiry`
- `strike`
- `option_type`
- `qty`
- `lot_size`
- `entry_time`
- `entry_quote_ts`
- `entry_price`
- `order_id`
- `fill_status`
- `exit_time`
- `exit_quote_ts`
- `exit_price`
- `charges`
- `gross_pnl`
- `net_pnl`
- `proof_status`
- `source_type`
- `tradability_status`

---

## D. Model/prediction blockers

### M01 - Model promotion remains blocked

**Evidence path:**

- `reports/latest/model_training_load_proof/summary.json`

**Observation:** Fresh training pipeline proof exists, but `promotion_allowed: false` and warning `model_promotion_remains_blocked_without_policy` remains.

**Impact:** Prediction model is not production-promoted.

**Recommendation:** Define promotion policy requiring multiple market days, minimum sample size, costed P&L, drawdown, stability, and no data leakage.

---

### M02 - Dashboard accuracy is weak / insufficient history

**Evidence source:** Dashboard screenshot provided by operator.

**Observation:** Dashboard shows Spearman rho around `0.200`, status `WEAK`, and only `1 day` of accuracy history.

**Impact:** This is insufficient for production-grade strategy confidence.

**Recommendation:** Require a rolling validation window with minimum 20 trading days or clearly label predictions as experimental.

---

## E. Dashboard/product safety blockers

### U01 - Dashboard endpoint coverage passes, but browser truth is not proven

**Evidence paths:**

- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`
- `reports/latest/dashboard_truth_proof/summary.json`

**Observation:** Required and optional API endpoints are reachable, but browser visual truth remains unproven in CI.

**Impact:** UI values may not match backend truth.

**Recommendation:** Add Playwright/screenshot/DOM proof that checks visible status cards against `/api/state`, `/api/health`, and `/api/broker/status`.

---

### U02 - UI wording can mislead operator

**Evidence source:** Dashboard screenshot provided by operator.

**Observation:** Dashboard shows `BROKER LIVE` while also showing `LIVE TRADING OFF`. The word `LIVE` may be confused with real trading.

**Impact:** Operator can misread broker connectivity as live trading enabled.

**Recommendation:** Rename card to `BROKER CONNECTED`, and separately show `REAL ORDER PLACEMENT: BLOCKED`.

---

### U03 - Synthetic data must be a hard red dashboard blocker

**Evidence paths:**

- Dashboard screenshot provided by operator.
- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`.

**Observation:** Dashboard shows `DATA SOURCE: SYNTHETIC`, but proof gates show `8/8`, which can create false confidence.

**Impact:** Operator may think the system is ready while the runtime state is synthetic.

**Recommendation:** Add a production readiness banner:

`PRODUCTION READY: NO - data source is SYNTHETIC`

The UI should not show green production status while synthetic data is active.

---

### U04 - Dashboard cards need clearer production-grade semantics

**Evidence source:** Dashboard screenshot provided by operator.

**Observation:** Current overview cards are useful but insufficient for production trading decisions.

**Required dashboard cards before production:**

- Broker connection: connected/disconnected
- Real data source: broker-live/synthetic/fallback
- Market status: open/closed/holiday
- Live trading: off/on
- Order placement: blocked/allowed
- Current contract validation: expiry, token, strike, lot size, bid/ask, spread
- Latest quote timestamp and freshness age
- Last signal timestamp and source
- Latest paper order lifecycle state
- Latest broker orderbook/tradebook reconciliation
- Risk limit status
- Daily loss limit status
- Proof matrix status

---

### U05 - Public dashboard/API hardening not proven

**Evidence paths:**

- `dashboard/backend/app.py`
- Public `/ui` and `/docs` observations

**Observation:** Public dashboard and Swagger docs are accessible. CORS has previously been development-grade.

**Impact:** Production trading dashboard should not be publicly accessible without authentication.

**Recommendation:** Require authentication, disable public docs in production, restrict CORS to approved origins, and add rate-limits/security headers.

---

## F. Infrastructure/runtime blockers

### I01 - Persistent storage is not enabled in Render config

**Evidence path:**

- `render.yaml`

**Observation:** Persistent disk block is commented out.

**Impact:** Runtime state, paper ledgers, and logs may be lost across restarts/redeploys unless external storage is used.

**Recommendation:** Use persistent disk or external DB for all proof, order, signal, and audit ledgers.

---

### I02 - Worker runtime proof needs live Render logs

**Evidence path:**

- `render.yaml`

**Observation:** Worker service is configured, but repo alone does not prove live worker loop health, restart recovery, daemon uptime, or scheduler fire history.

**Impact:** Production trading requires proven continuous background processing.

**Recommendation:** Export worker logs or write worker heartbeats to a durable location. Required heartbeat fields: token daemon, watchdog, scheduler, last job run, next job, crash count, restart count.

---

## G. Security/production blockers

### S01 - Public docs should not remain open for production trading

**Evidence path:**

- `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`

**Observation:** `/docs` is reachable in endpoint proof.

**Impact:** Public API docs increase exposure for a trading dashboard.

**Recommendation:** Disable docs in production or protect with authentication.

---

### S02 - Authentication proof is missing

**Evidence source:** Public dashboard loads at `/ui`.

**Observation:** No repo proof confirms login/session requirement for dashboard access.

**Impact:** Production trading dashboard state should not be publicly visible.

**Recommendation:** Add auth middleware before production trading features.

---

# Action checklist for Claude

Claude should run these checks before any patch:

```bash
cd /workspaces/Genesis_System3
git fetch origin
git status --short --untracked-files=all
git rev-parse HEAD
git rev-parse origin/main
```

Claude should not patch blindly if local HEAD does not match the intended branch.

## Priority 1 - Proof governance correction

Files:

- `scripts/paper_lifecycle_proof.py`
- `scripts/system3_master_proof_orchestrator.py`

Required result:

- Weekend/fallback/simulated lifecycle cannot become clean `PASS`.
- `trade_ready` stays false until market-day real data paper lifecycle is proven.

## Priority 2 - Runtime truth reconciliation

Endpoints:

- `/api/health`
- `/api/state`
- `/api/broker/status`
- `/api/gain_rank`

Required result:

- one authoritative state source
- synthetic data produces red blocker
- health/state cannot disagree on data source

## Priority 3 - Dashboard production safety

Files:

- `dashboard/app.js`
- `dashboard/index.html`
- `dashboard/backend/app.py`

Required result:

- UI must show `PRODUCTION READY: NO` when synthetic/fallback/no-contract/no-market-proof is active.
- `BROKER LIVE` should be renamed to `BROKER CONNECTED`.
- `LIVE TRADING OFF` and `ORDER PLACEMENT BLOCKED` must remain clearly visible.

## Priority 4 - Infrastructure proof

Required result:

- worker heartbeat proof
- scheduler fire proof
- token watchdog proof
- persistent audit/log storage proof

---

## Current final statement

The system is currently **cloud Analyzer/Paper ready**, with Dhan broker connectivity now appearing healthy in latest endpoint proof. It is **not production-grade for real trade** because live execution is disabled/not implemented, `/api/state` still reports synthetic data, lifecycle proof can pass fallback/weekend simulated flows, dashboard browser truth is incomplete, model promotion is blocked, public hardening is not proven, persistent storage is not enabled, worker runtime proof is incomplete, and official `trade_ready` remains false.
