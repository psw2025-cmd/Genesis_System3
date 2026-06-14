# AI Production Readiness Findings

**Purpose:** Single living audit file for Genesis System3 production-grade real trading readiness.

**Intended users:** Pritam, Claude, Cursor, Gemini, Codex, and future repo agents.

**Safety rule:** Never write secrets, access tokens, PINs, TOTP seeds, API keys, broker credentials, private account values, or raw sensitive broker data into this file.

---

## Update protocol

All agents must update this same file after every major proof, patch, or finding. Do not leave important conclusions only in chat.

### Required update row format

```text
YYYY-MM-DD HH:MM IST | agent | commit/ref checked | area | finding/action | proof path | status
```

### Allowed proof sources

A PASS can only be written when supported by one of:

- committed repo proof artifact
- committed command output file
- Render endpoint proof artifact
- CI/job log artifact
- browser screenshot/DOM proof artifact
- user-provided screenshot/log clearly marked as user-provided runtime evidence

### Allowed non-pass statuses

Use these when proof is incomplete:

- `NOT_PROVEN`
- `NEEDS_MARKET_OPEN`
- `NEEDS_RENDER_LOGS`
- `NEEDS_BROKER_RUNTIME`
- `NEEDS_BROWSER_PROOF`
- `PASS_WITH_WARNINGS`
- `BLOCKED`

---

## Update log

| Time IST | Agent | Commit/ref checked | Area | Finding/action | Proof path | Status |
|---|---|---|---|---|---|---|
| 2026-06-14 21:58 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | initial audit | Created living production readiness audit file | `docs/AI_PRODUCTION_READINESS_FINDINGS.md` | DONE |
| 2026-06-14 22:02 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | Claude protocol | Added proof-truth, self-verification, dashboard, and action rules | this file | DONE |
| 2026-06-14 22:15 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | continuous master | Rebuilt file as continuous master with action pack, dashboard pack, proof map, issue map, and Claude update protocol | this file | DONE |

---

# Current baseline truth

- **Repo:** `psw2025-cmd/Genesis_System3`
- **Baseline main commit inspected:** `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01`
- **Mode:** Analyzer/Paper.
- **Live trading:** Disabled.
- **Order placement:** Blocked.
- **Broker:** Dhan appears connected in latest endpoint coverage proof.
- **Official readiness:** Not trade-ready.
- **Production-grade real trading:** Not ready.

---

# Current proof-truth snapshot

| Area | Current truth | Proof path | Status |
|---|---|---|---|
| Master matrix | 8 gates published, but `trade_ready=false`, verdict `ANALYZER_READY_PROOF_INCOMPLETE` | `reports/latest/proof_status_matrix/proof_status_matrix.json` | NOT_PRODUCTION_READY |
| Full pipeline | Blocker remains: `live_market_analyzer_paper_trade_not_proven` | `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json` | NOT_TRADE_READY |
| Broker | `/api/broker/status` shows Dhan connected, error null, order placement blocked | `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json` | ANALYZER_OK |
| Health | `/api/health` says `data_source=live`, status ok, broker connected | `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json` | PARTIAL_PASS |
| State | `/api/state` says `data_source=SYNTHETIC`, no signal, no positions, contracts_total 0, underlyings 0 | `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json` | BLOCKER |
| Lifecycle | Summary marks PASS, but latest artifact is weekend/fallback/simulated paper flow | `reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_162812.json` | FALSE_PASS_RISK |
| Model | Fresh training metrics proven, but `promotion_allowed=false` | `reports/latest/model_training_load_proof/summary.json` | PASS_WITH_WARNINGS |
| Backtest | Costed walk-forward proven, but only 8 trades / 8 walk pairs | `reports/latest/recent_backtest_walkforward_proof/summary.json` | SMALL_SAMPLE_PASS |
| Dashboard | Endpoint coverage exists; browser visual truth and API/DB reconciliation are false | `reports/latest/dashboard_truth_proof/summary.json` | PASS_WITH_WARNINGS |
| Live execution | Dhan live wrapper is skeleton and returns NOT_IMPLEMENTED outside dry-run | `core/broker/dhan_live_order_wrapper.py` | HARD_BLOCKER |
| Render runtime | Web + worker configured; live flags hardcoded off; persistent disk commented | `render.yaml` | ANALYZER_ONLY |
| PR #35 | Scheduler fix PR exists but became non-mergeable after main moved | PR #35 | NEEDS_REBASE_OR_REAPPLY |

---

# Final production-grade verdict

```text
NOT PRODUCTION-GRADE FOR REAL MONEY TRADING.
```

Current system is cloud Analyzer/Paper capable, and broker connectivity appears improved, but production real trading is blocked because:

1. `trade_ready=false`.
2. Full pipeline still has `live_market_analyzer_paper_trade_not_proven`.
3. Real Dhan order wrapper is skeleton / NOT_IMPLEMENTED.
4. Live trading flags are disabled in source and Render.
5. `/api/state` still reports `SYNTHETIC` data.
6. `/api/health` and `/api/state` disagree on data source.
7. Lifecycle proof can falsely pass fallback/weekend/simulated data.
8. Real live option contract tradability is not proven.
9. Real market-day signal -> paper order -> real LTP exit -> charges -> net P&L is not proven.
10. Browser visual dashboard truth is not proven.
11. API/DB/report reconciliation is not proven.
12. Model promotion remains blocked.
13. Persistent storage is not enabled.
14. Worker runtime logs and heartbeats are not proven.
15. Production auth/security hardening is not proven.

---

# Non-negotiable rules for Claude and all agents

## Rule 1 - Never call simulated lifecycle proof production proof

A lifecycle proof is **not production-grade** if any are true:

- market is weekend/holiday/pre-market/post-market/closed
- `dry_run=true`
- `force=true`
- token is `DRY_RUN_TOKEN`, `FALLBACK_TOKEN`, missing, or not broker verified
- source is fallback/synthetic/mock/dry-run/sample/fixture
- exit price is generated by formula, such as fixed +5%
- fill has no real quote timestamp
- exit has no real quote/LTP timestamp
- broker connection is only public status, not linked to quote/tradebook proof

If any are true, status must be at most:

```text
PASS_WITH_WARNINGS
```

It must not clear production readiness.

## Rule 2 - Real market paper lifecycle PASS requirements

A real market paper lifecycle PASS requires all:

- market open
- broker connected
- real live quote or option-chain data
- non-fallback signal
- real broker/NSE option instrument token
- valid expiry and strike
- bid/ask/LTP fresh
- spread/liquidity check
- lot size and quantity check
- paper entry using real quote timestamp
- paper fill based on quote/LTP, not fixed formula
- exit based on real quote/LTP snapshot
- charges, brokerage, slippage, gross P&L, net P&L
- order/fill/exit/P&L reconciliation
- dashboard count and P&L match proof report
- no live order placed

## Rule 3 - Official readiness authority

Production real trading is blocked unless all are true:

- `reports/latest/proof_status_matrix/proof_status_matrix.json` has `trade_ready=true`
- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json` has `trade_ready=true`
- real order wrapper implemented and tested
- risk manager passes
- dashboard truth passes
- broker orderbook/tradebook/position reconciliation passes
- explicit user approval exists

## Rule 4 - Do not enable live trading from automation

Do not set these true/1 from automation:

- `LIVE_TRADING_ENABLED`
- `USE_LIVE_EXECUTION_ENGINE`
- `SYSTEM3_LIVE_TRADING_ALLOWED`

---

# Continuous Claude execution pack

Claude must start every session with:

```bash
cd /workspaces/Genesis_System3
git fetch origin
echo "LOCAL=$(git rev-parse HEAD)"
echo "MAIN=$(git rev-parse origin/main)"
git status --short --untracked-files=all
```

Claude must not patch blindly if local HEAD does not match the intended branch.

## Step A - Re-check current official reports

```bash
cd /workspaces/Genesis_System3
cat reports/latest/proof_status_matrix/proof_status_matrix.json
cat reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json
cat reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json
cat reports/latest/dashboard_truth_proof/summary.json
cat reports/latest/analyzer_paper_lifecycle_proof/summary.json
```

Expected current blocker:

```text
live_market_analyzer_paper_trade_not_proven
```

## Step B - Patch lifecycle proof governance

Files:

- `scripts/paper_lifecycle_proof.py`
- `scripts/system3_master_proof_orchestrator.py`

Required behavior:

- Weekend/fallback/simulated lifecycle cannot become clean PASS.
- If market closed, status must be `PASS_WITH_WARNINGS` or `SKIPPED`.
- If token is fallback/dry-run, production lifecycle false.
- If signal is fallback/synthetic/dry-run, production lifecycle false.
- If exit price is formula-generated, production lifecycle false.
- `trade_ready` remains false until real market-day paper lifecycle is proven.

Required proof after patch:

```bash
python scripts/paper_lifecycle_proof.py --force || true
python scripts/system3_master_proof_orchestrator.py --auto-fix || true
cat reports/latest/analyzer_paper_lifecycle_proof/summary.json
cat reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json
cat reports/latest/proof_status_matrix/proof_status_matrix.json
```

Acceptance target outside market hours:

```json
{
  "full_lifecycle_proven": false,
  "status": "PASS_WITH_WARNINGS",
  "trade_ready": false
}
```

## Step C - Fix runtime truth reconciliation

Endpoints that must agree:

- `/api/health`
- `/api/state`
- `/api/broker/status`
- `/api/gain_rank`

Current problem:

- health says `data_source=live`
- state says `data_source=SYNTHETIC`

Required behavior:

- one authoritative state source
- if `/api/state.data_source=SYNTHETIC`, all readiness outputs must say not production ready
- if contracts_total = 0 or underlyings = 0, option trading readiness false
- no dashboard green production status while synthetic/no-contract/no-signal state exists

Required proof:

```bash
python scripts/dashboard_endpoint_coverage_proof.py
cat reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json
cat reports/latest/dashboard_truth_proof/summary.json
```

## Step D - Dashboard production verification

Layer 1 API check:

```bash
curl -sS https://genesis-system3-backend.onrender.com/api/health | python -m json.tool
curl -sS https://genesis-system3-backend.onrender.com/api/state | python -m json.tool
curl -sS https://genesis-system3-backend.onrender.com/api/broker/status | python -m json.tool
curl -sS https://genesis-system3-backend.onrender.com/api/gain_rank | python -m json.tool
```

Layer 2 browser truth must prove:

- UI shows `PRODUCTION READY: NO` when `trade_ready=false`
- UI shows `DATA SOURCE: SYNTHETIC` as red/blocker
- UI uses `BROKER CONNECTED`, not misleading `BROKER LIVE`
- UI shows `LIVE TRADING OFF`
- UI shows `ORDER PLACEMENT BLOCKED`
- UI shows `MARKET CLOSED` if market closed
- UI shows latest proof matrix status

Required proof artifacts:

- screenshot path
- DOM text dump path
- API-vs-DOM comparison JSON

Layer 3 API/DB/report reconciliation:

| Field | API source | UI source | Report source | Must match? |
|---|---|---|---|---|
| broker connected | `/api/broker/status` | broker card | endpoint coverage | yes |
| live trading | `/api/health` | safety card | proof matrix | yes |
| data source | `/api/state` | data source card | endpoint coverage | yes |
| trade ready | pipeline report | production banner | proof matrix | yes |
| signal | `/api/state` or `/api/gain_rank` | signal card | lifecycle proof | yes |
| P&L | `/api/pnl` | P&L card | paper lifecycle | yes |

## Step E - Reapply scheduler PR safely

PR #35 became non-mergeable after main moved. Claude should re-check current scheduler config and reapply only if needed.

Required check:

```bash
cat config/system3_job_scheduler.json
sed -n '90,170p' core/engine/system3_phase82_job_scheduler.py
```

Correct job format should use:

```json
{
  "id": "paper_lifecycle_proof",
  "script": "scripts/paper_lifecycle_proof.py",
  "args": [],
  "weekdays_only": true,
  "schedule_time": "09:30",
  "timezone": "Asia/Kolkata"
}
```

Do not use unsupported `function`, `kwargs`, or unrecognized `days` unless scheduler code explicitly supports them.

## Step F - Model promotion policy

Current proof says fresh metrics exist, but `promotion_allowed=false`.

Claude must create or update a promotion policy requiring:

- minimum 20 market days or explicitly justified smaller sample
- minimum paper trade count
- costed net P&L positive after brokerage/slippage
- max drawdown threshold
- stability across regimes
- no data leakage check
- shadow model comparison
- rollback plan

Until then dashboard should show:

```text
MODEL STATUS: EXPERIMENTAL / NOT PROMOTED
```

## Step G - Infrastructure proof

Render config has worker service, but runtime proof is incomplete.

Claude must produce a durable worker heartbeat artifact containing:

- token daemon status
- token watchdog status
- scheduler status
- last job run
- next scheduled job
- crash count
- restart count
- uptime
- last broker status

Persistent storage is not enabled because Render disk is commented. Claude must not claim production persistence until disk or external DB proof exists.

---

# Dashboard production cards required

Before production trading, dashboard must show all of these clearly:

1. Production Ready: YES/NO
2. Trade Ready: YES/NO
3. Broker Connected: YES/NO
4. Data Source: LIVE/SYNTHETIC/FALLBACK
5. Market Status: OPEN/CLOSED/HOLIDAY
6. Live Trading: OFF/ON
7. Order Placement: BLOCKED/ALLOWED
8. Current Underlying
9. Current Option Token
10. Expiry
11. Strike
12. Option Type CE/PE
13. Bid
14. Ask
15. LTP
16. Spread
17. Quote timestamp
18. Quote age seconds
19. Liquidity status
20. Signal source
21. Signal timestamp
22. Signal confidence
23. Paper order status
24. Paper fill status
25. Exit status
26. Gross P&L
27. Charges
28. Net P&L
29. Broker orderbook reconciliation
30. Broker tradebook reconciliation
31. Position reconciliation
32. Risk limit status
33. Daily loss status
34. Proof matrix verdict
35. Last proof generation time

---

# Detailed issue map

## B01 - Live trading intentionally disabled

Evidence: `config/live_trade_config.py`, `render.yaml`, `reports/latest/proof_status_matrix/proof_status_matrix.json`.

Observation: Live flags are OFF. Render keeps live disabled.

Recommendation: Keep off until all proof gates pass.

## B02 - Real Dhan order execution not implemented

Evidence: `core/broker/dhan_live_order_wrapper.py`.

Observation: Wrapper is skeleton and returns NOT_IMPLEMENTED outside dry-run.

Recommendation: Implement only after analyzer/paper is stable.

## B03 - Official pipeline is not trade-ready

Evidence: `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`.

Observation: `trade_ready=false`, `proven_live_market_paper_trade_today=false`.

Recommendation: Need market-day real broker-connected paper lifecycle proof.

## D01 - `/api/state` reports synthetic data

Evidence: `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`.

Observation: `/api/state.data_source=SYNTHETIC`, signals `NO_TRADE`, contracts_total 0, underlyings 0.

Recommendation: Synthetic must force `PRODUCTION READY: NO`.

## D02 - Health/state source truth conflict

Evidence: `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`.

Observation: `/api/health.data_source=live`; `/api/state.data_source=SYNTHETIC`.

Recommendation: One authoritative runtime state.

## D03 - Live option-chain tradability missing

Evidence: `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json`.

Observation: no proof of tradable expiry, strike, broker token, bid/ask, spread, lot size, or liquidity.

Recommendation: Add tradability gate.

## L01 - Lifecycle false PASS risk

Evidence: `scripts/paper_lifecycle_proof.py`, `reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_162812.json`.

Observation: PASS despite weekend, fallback token, fallback source, simulated exit.

Recommendation: Change PASS logic.

## L02 - Mandatory lifecycle fields incomplete

Evidence: `scripts/paper_lifecycle_proof.py`.

Observation: missing qty/order_id/fill_status/charges/gross_pnl/quote timestamps/tradability status/proof status.

Recommendation: Expand mandatory fields.

## M01 - Model promotion blocked

Evidence: `reports/latest/model_training_load_proof/summary.json`.

Observation: `fresh_training_metrics_proven=true`, `promotion_allowed=false`.

Recommendation: Add promotion policy.

## M02 - Accuracy history insufficient

Evidence: user dashboard screenshot.

Observation: weak Spearman and only 1 day history.

Recommendation: label experimental until rolling validation passes.

## U01 - Browser visual truth not proven

Evidence: `reports/latest/dashboard_truth_proof/summary.json`.

Observation: `browser_visual_truth_proven=false`, `api_db_report_reconciliation_proven=false`.

Recommendation: Add browser screenshot/DOM/API comparison proof.

## U02 - Dashboard wording can mislead

Evidence: user dashboard screenshot.

Observation: `BROKER LIVE` can be confused with live trading.

Recommendation: Rename to `BROKER CONNECTED` and show `REAL ORDER PLACEMENT: BLOCKED`.

## U03 - Synthetic data must be hard red blocker

Evidence: screenshot and endpoint coverage.

Observation: UI can show 8/8 gates while data is synthetic.

Recommendation: add red banner `PRODUCTION READY: NO - data source is SYNTHETIC`.

## U04 - Public dashboard/API hardening not proven

Evidence: public `/ui` and `/docs` behavior.

Recommendation: Add auth, disable/protect docs, restrict CORS, add security headers and rate limits.

## I01 - Persistent storage not enabled

Evidence: `render.yaml` disk block commented.

Recommendation: use persistent disk or external DB.

## I02 - Worker runtime proof missing

Evidence: `render.yaml` config only.

Recommendation: add worker heartbeat artifact.

---

# Claude action-result update format

After every Claude action, append one update row and list:

- modified source files
- proof JSON files
- screenshot/DOM proof files
- command output files
- commit SHA
- final status

Example:

```text
2026-06-15 09:45 IST | Claude | <commit> | lifecycle | Ran market paper lifecycle with broker connected and non-fallback token | reports/latest/analyzer_paper_lifecycle_proof/<file>.json | PASS_WITH_WARNINGS
```

---

## Current final statement

The system is cloud Analyzer/Paper capable and Dhan broker connectivity appears healthy in endpoint proof. It is **not production-grade for real trade** because live execution is disabled/not implemented, `/api/state` still reports synthetic data, lifecycle proof can pass fallback/weekend/simulated flows, dashboard browser truth is incomplete, API/DB/report reconciliation is incomplete, model promotion is blocked, public hardening is not proven, persistent storage is not enabled, worker runtime proof is incomplete, and official `trade_ready` remains false.
