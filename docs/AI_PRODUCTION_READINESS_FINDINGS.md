# AI Production Readiness Findings

**Purpose:** Single living audit file for Genesis System3 production-grade real trading readiness.

**Intended users:** Pritam, Claude, Cursor, Gemini, Codex, and future repo agents.

**Safety rule:** Never write secrets, access tokens, PINs, TOTP seeds, API keys, broker credentials, private account values, or raw sensitive broker data into this file.

---

## Communication rule for every chat/update

Every assistant/agent response about this project must include a small summary before or after tool work:

```text
Mini summary:
- What I analysed
- What I found
- What I wrote/updated
- What proof supports it
- What I will check next
```

This is mandatory so the user can continuously see what is being written, what is being analysed, and why the next step is selected.

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
| 2026-06-14 22:25 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | forensic gap framework | Added mandatory goal-to-core gap decomposition: data, signal, tradability, option-chain, broker, proof, dashboard, risk, execution, governance | this file | DONE |

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

# Root goal decomposition rule

When user gives a goal, agent must not jump directly to action. Agent must decompose the goal into all dependency gaps, prove current state, find missing proof, and only then recommend or patch.

Example user goal:

```text
Gain highest from option segment.
```

Correct agent process:

```text
Goal
→ data gaps
→ signal gaps
→ tradability gaps
→ option-chain gaps
→ broker gaps
→ proof gaps
→ dashboard gaps
→ risk gaps
→ execution gaps
→ governance gaps
→ validated action plan
→ paper proof
→ only then production consideration
```

---

# Mandatory forensic gap framework

## 1. Data gaps

**Question:** Is the system using real, fresh, complete data or stale/synthetic/fallback data?

**Must check:**

- spot/index/stock live quote
- option-chain live data
- timestamp freshness
- data source label
- fallback usage
- cache age
- missing symbols
- API errors
- market open/closed state

**Proof required:**

- `/api/state`
- `/api/health`
- `/api/gain_rank`
- endpoint coverage JSON
- data-source proof artifact

**Current known issue:** `/api/health` reports live data but `/api/state` reports `SYNTHETIC`, creating truth conflict.

**Status:** BLOCKER.

---

## 2. Signal gaps

**Question:** Is there a valid live signal, or only stale/fallback/no-trade output?

**Must check:**

- signal timestamp
- signal source
- confidence score
- underlying
- CE/PE direction
- entry logic
- reason for NO_TRADE
- prediction accuracy history
- stale signal rejection

**Proof required:**

- `/api/state.signals`
- `/api/gain_rank`
- signal ledger
- prediction ledger
- accuracy trend proof

**Current known issue:** `/api/state` reports `NO_TRADE`; dashboard still displays GainRank/Proof information that can appear stronger than actual state.

**Status:** BLOCKER until live market signal is proven.

---

## 3. Tradability gaps

**Question:** Can the selected underlying/contract actually be traded in options?

**Must check:**

- F&O eligibility
- broker instrument token
- expiry availability
- strike availability
- lot size
- tick size
- freeze quantity
- circuit/ban status
- liquidity
- bid/ask spread

**Proof required:**

- broker instruments file/proof
- option chain snapshot
- tradability validation report
- rejection list for non-option stocks

**Current known issue:** prior dashboard/prediction showed equity symbols where option tradability was not proven. `/api/state.qc.contracts_total=0` and `underlyings=0` in endpoint proof.

**Status:** BLOCKER.

---

## 4. Option-chain gaps

**Question:** Is the option-chain data complete enough for strike selection and risk?

**Must check:**

- bid
- ask
- LTP
- IV
- Greeks
- OI
- OI change
- volume
- expiry
- strike ladder
- spread
- option-chain latency
- data plan/API limits

**Proof required:**

- option-chain snapshot artifact
- quote timestamp
- Greeks calculation proof
- spread/liquidity filter proof

**Current known issue:** dashboard shows option/risk metrics but no committed proof confirms live option-chain contract validation.

**Status:** NOT_PROVEN.

---

## 5. Broker gaps

**Question:** Is broker connectivity enough for read-only proof, paper proof, and eventually live execution?

**Must check:**

- broker connected
- token valid
- credentials present without exposing secrets
- orderbook access
- tradebook access
- positions access
- quote access
- latency
- token refresh/watchdog
- rate limits

**Proof required:**

- `/api/broker/status`
- broker preflight report
- orderbook/tradebook/positions read-only proof
- token watchdog heartbeat

**Current known improvement:** Dhan broker status appears connected with error null in latest endpoint coverage.

**Current known gap:** positions source/reconciliation and broker tradebook/orderbook proof are not production-proven.

**Status:** PARTIAL_PASS / NEEDS_BROKER_RUNTIME.

---

## 6. Proof gaps

**Question:** Are PASS labels truthful, or are they hiding fallback/simulation?

**Must check:**

- proof status matrix
- lifecycle proof artifact
- market status at proof time
- dry_run/force flags
- fallback tokens
- simulated exit logic
- trade_ready flag
- warnings suppressed or not

**Proof required:**

- `reports/latest/proof_status_matrix/proof_status_matrix.json`
- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`
- `reports/latest/analyzer_paper_lifecycle_proof/*.json`

**Current known issue:** lifecycle proof is marked PASS even though latest artifact used weekend, `FALLBACK_TOKEN`, `BHAVCOPY_FALLBACK`, and simulated exit.

**Status:** FALSE_PASS_RISK.

---

## 7. Dashboard gaps

**Question:** Does dashboard show the actual truth, or only attractive/green status?

**Must check:**

- production-ready banner
- trade_ready status
- data source status
- synthetic/fallback warning
- broker connected vs live trading wording
- order placement blocked status
- proof matrix from backend, not hardcoded
- browser screenshot/DOM proof
- API vs UI vs report reconciliation

**Proof required:**

- dashboard source audit
- Playwright/browser screenshot proof
- DOM text dump
- API-vs-DOM comparison JSON

**Current known issues:** frontend has hardcoded proof gates, hardcoded 8/8 proof badge, and ML Accuracy marked PASS despite weak rho and low days.

**Status:** BLOCKER / NEEDS_BROWSER_PROOF.

---

## 8. Risk gaps

**Question:** Is max loss controlled before any order can be placed?

**Must check:**

- max loss per trade
- daily loss cap
- position size
- lot size
- slippage
- spread
- time stop
- stop loss
- trailing rule
- capital exposure
- margin requirement
- kill switch

**Proof required:**

- risk config
- risk gate report
- paper trade risk proof
- simulated worst-case loss report

**Current known issue:** live order is disabled, but production-grade risk proof against real option quotes and paper fills is not complete.

**Status:** NOT_PROVEN.

---

## 9. Execution gaps

**Question:** Can the system go from signal to order to fill to exit to P&L correctly?

**Must check:**

- order wrapper implementation
- paper order logic
- fill model
- exit logic
- order status refresh
- cancel/modify handling
- broker orderbook reconciliation
- tradebook reconciliation
- charges and net P&L

**Proof required:**

- order lifecycle proof
- broker wrapper tests
- paper fill proof
- reconciliation proof

**Current known issue:** Dhan live order wrapper is skeleton and returns NOT_IMPLEMENTED outside dry-run.

**Status:** HARD_BLOCKER.

---

## 10. Governance gaps

**Question:** Who or what is allowed to declare production-ready?

**Must check:**

- final proof authority
- live enablement approval
- rollback plan
- model promotion policy
- manual override policy
- audit trail
- multi-agent verification
- persistent logs
- no secret leakage

**Proof required:**

- proof matrix
- live enablement policy
- model promotion policy
- audit file update trail
- user approval record

**Current known issue:** model promotion is blocked, live enablement policy is not complete, and proof gates can still be misclassified.

**Status:** BLOCKER.

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

---

# Final production-grade verdict

```text
NOT PRODUCTION-GRADE FOR REAL MONEY TRADING.
```

Current system is cloud Analyzer/Paper capable, and broker connectivity appears improved, but production real trading is blocked because the 10 forensic gap families are not all closed and proven.

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

If any are true, status must be at most `PASS_WITH_WARNINGS` and must not clear production readiness.

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

- proof matrix has `trade_ready=true`
- full pipeline has `trade_ready=true`
- live order wrapper implemented and tested
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

Claude must not patch blindly if local HEAD does not match intended branch.

## Step A - Re-check official reports

```bash
cat reports/latest/proof_status_matrix/proof_status_matrix.json
cat reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json
cat reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json
cat reports/latest/dashboard_truth_proof/summary.json
cat reports/latest/analyzer_paper_lifecycle_proof/summary.json
```

## Step B - Patch lifecycle proof governance

Files:

- `scripts/paper_lifecycle_proof.py`
- `scripts/system3_master_proof_orchestrator.py`

Required behavior:

- weekend/fallback/simulated lifecycle cannot become clean PASS
- fallback token means production lifecycle false
- fallback/synthetic/dry-run signal means production lifecycle false
- formula exit means production lifecycle false
- `trade_ready` remains false until real market-day lifecycle is proven

## Step C - Fix runtime truth reconciliation

Endpoints that must agree:

- `/api/health`
- `/api/state`
- `/api/broker/status`
- `/api/gain_rank`

Problem to fix:

- health says `data_source=live`
- state says `data_source=SYNTHETIC`

## Step D - Dashboard production verification

Dashboard must show:

- `PRODUCTION READY: NO` when `trade_ready=false`
- `DATA SOURCE: SYNTHETIC` as red/blocker
- `BROKER CONNECTED`, not misleading `BROKER LIVE`
- `LIVE TRADING OFF`
- `ORDER PLACEMENT BLOCKED`
- `MARKET CLOSED` when closed
- latest proof matrix status

## Step E - Model promotion policy

Model must remain experimental until policy proves:

- enough market days
- enough paper trades
- costed net P&L
- drawdown control
- drift checks
- rollback plan

## Step F - Infrastructure proof

Need durable heartbeat artifact:

- token daemon
- watchdog
- scheduler
- last job
- next job
- crash count
- restart count
- uptime
- last broker status

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

The system is cloud Analyzer/Paper capable and Dhan broker connectivity appears healthy in endpoint proof. It is **not production-grade for real trade** because data gaps, signal gaps, tradability gaps, option-chain gaps, broker gaps, proof gaps, dashboard gaps, risk gaps, execution gaps, and governance gaps are not all closed with objective proof.
