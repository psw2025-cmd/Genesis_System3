# AI Production Readiness Findings

**Purpose:** Single living audit file for Genesis System3 production-grade real trading readiness.

**Intended users:** Pritam, Claude, Cursor, Gemini, Codex, and future repo agents.

**Safety rule:** Never write secrets, access tokens, PINs, TOTP seeds, API keys, broker credentials, private account values, or raw sensitive broker data into this file.

---

## Communication rule for every chat/update

Every assistant/agent response about this project must include a small summary:

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
| 2026-06-14 22:35 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | original vision gap matrix | Added original System3 design vision vs current implementation gap matrix | this file | DONE |
| 2026-06-14 22:45 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | multi-validation batch 1 | Added backend runtime truth, SSOT, dashboard hardcoded proof, CORS/security, and position reconciliation findings | this file | DONE |

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

# Original System3 design vision

The original System3 design was intended as a complete **AI trading control system**, not just a dashboard or a prediction script. Core principles:

1. **Analyzer/Paper before Live** — live orders stay blocked until multi-day proof passes.
2. **Real data truth** — no fake, stale, synthetic, or fallback data can be shown as production truth.
3. **Full signal lifecycle** — data → scanner → signal → rank → tradability → paper order → exit → net P&L → learning.
4. **Options-first tradability** — only option-tradable symbols/contracts with valid strike, expiry, token, spread, and liquidity can reach trade stage.
5. **Broker proof** — broker status, quote access, orderbook, tradebook, positions, and token watchdog must be proven.
6. **Ultra dashboard** — dashboard must be a command center showing real truth, not attractive green placeholders.
7. **Risk-first execution** — every order must pass max loss, daily loss, slippage, spread, lot size, and kill-switch gates.
8. **Proof-first governance** — every PASS must come from committed artifacts, browser proof, broker proof, or runtime logs.
9. **Self-learning loop** — daily prediction vs actual result, missed-trade analysis, model drift, and retraining policy.
10. **Fail-closed production** — when uncertain, stale, synthetic, or unproven, the system must block trade and clearly say why.

---

# Current proof-truth snapshot

| Area | Current truth | Proof path | Status |
|---|---|---|---|
| Master matrix | 8 gates published, but `trade_ready=false`, verdict `ANALYZER_READY_PROOF_INCOMPLETE` | `reports/latest/proof_status_matrix/proof_status_matrix.json` | NOT_PRODUCTION_READY |
| Full pipeline | Blocker remains: `live_market_analyzer_paper_trade_not_proven` | `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json` | NOT_TRADE_READY |
| Broker | `/api/broker/status` shows Dhan connected, error null, order placement blocked | `reports/latest/dashboard_endpoint_coverage/endpoint_coverage_summary.json` | ANALYZER_OK |
| Health | `/api/health` can show `data_source=live`, status ok, broker connected, even with market closed | `dashboard/backend/app.py` | PARTIAL_PASS |
| State | `/api/state` can show synthetic/not-ready, no signal, no positions, contracts_total 0, underlyings 0 | `dashboard/backend/runtime_state_store.py` + endpoint coverage | BLOCKER |
| Lifecycle | Summary marks PASS, but latest artifact is weekend/fallback/simulated paper flow | `reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_162812.json` | FALSE_PASS_RISK |
| Model | Fresh training metrics proven, but `promotion_allowed=false` | `reports/latest/model_training_load_proof/summary.json` | PASS_WITH_WARNINGS |
| Backtest | Costed walk-forward proven, but only 8 trades / 8 walk pairs | `reports/latest/recent_backtest_walkforward_proof/summary.json` | SMALL_SAMPLE_PASS |
| Dashboard | Frontend has hardcoded proof gates and can overstate PASS | `dashboard/app.js` | BLOCKER |
| Browser truth | Endpoint proof exists, but browser visual truth and API/DB reconciliation are false | `reports/latest/dashboard_truth_proof/summary.json` | PASS_WITH_WARNINGS |
| Position reconciliation | Broker positions fetch is TODO and returns empty list | `dashboard/backend/position_reconciliation.py` | HARD_BLOCKER |
| Live execution | Dhan live wrapper is skeleton and returns NOT_IMPLEMENTED outside dry-run | `core/broker/dhan_live_order_wrapper.py` | HARD_BLOCKER |
| Render runtime | Web + worker configured; live flags hardcoded off; persistent disk commented | `render.yaml` | ANALYZER_ONLY |
| Security | CORS allows all origins with credentials and public docs are exposed unless externally protected | `dashboard/backend/app.py` | BLOCKER |

---

# Original vision vs current implementation gap matrix

| Original design target | Current implementation truth | Gap status | Required next action |
|---|---|---|---|
| Full AI trading control system | Current repo has Analyzer/Paper dashboard plus proof reports, but not full trade-ready control system | PARTIAL | Keep developing toward proof-first command center |
| Analyzer/Paper before Live | Live trading is disabled and order placement blocked | GOOD / SAFETY PASS | Keep disabled until all proof gates pass |
| Real data truth | `/api/health` can show live while `/api/state` shows synthetic/not-ready | BLOCKER | One authoritative runtime data-source truth |
| Full signal lifecycle | `/api/state` can show `NO_TRADE`; lifecycle proof can pass fallback/weekend simulation | BLOCKER | Require real market signal-to-paper-P&L proof |
| Options-first tradability | Option token/strike/expiry/liquidity proof not complete; `contracts_total=0` in state proof | BLOCKER | Add option tradability gate before any trade candidate |
| Broker proof | Broker connected proof exists, but orderbook/tradebook/position reconciliation is not production-proven | PARTIAL | Add broker read-only reconciliation proof |
| Ultra dashboard command center | Current dashboard is visually good but has hardcoded proof gates and can overstate PASS | BLOCKER | Replace hardcoded proof with real proof matrix/API truth |
| Risk-first execution | Risk dashboard exists, but real option quote based risk proof is incomplete | NOT_PROVEN | Add risk proof based on live quote, spread, lot size, loss cap |
| Paper/live separation | Live disabled is good; paper lifecycle proof still misclassified | PARTIAL | Fix lifecycle PASS governance |
| Production execution path | Dhan live order wrapper is skeleton / NOT_IMPLEMENTED outside dry-run | HARD_BLOCKER | Do not implement live until paper proof; later add wrapper safely |
| Proof-first governance | Proof matrix exists, but false PASS risk remains in lifecycle/dashboard accuracy | BLOCKER | Fail/Warning for fallback/simulated/weak accuracy |
| Daily learning loop | Accuracy trend exists but only weak/limited evidence; model promotion blocked | PARTIAL | Add 20-day validation and model promotion policy |
| Dashboard browser truth | Endpoint proof exists, but browser visual truth and API/DB reconciliation not proven | BLOCKER | Add Playwright/DOM/API comparison proof |
| Persistent audit | Render disk is commented; runtime output may not be durable | BLOCKER | Add persistent storage or external DB proof |
| Worker reliability | Worker configured but logs/heartbeats not proven | NOT_PROVEN | Add durable worker heartbeat proof |
| Security/governance | CORS wildcard and public docs/dashboard hardening not production-proven | BLOCKER | Add auth, restricted CORS, protected docs, security headers |

---

# Multi-Validation Batch 1 — repo forensic findings

## MV1-01 — Backend synthetic/live truth is split

**Evidence:** `dashboard/backend/app.py` imports synthetic data generators and also has `REAL_ONLY` logic.

**Observation:** The backend has two competing concepts:

- `REAL_ONLY=True` by default, which says synthetic data should not be used for production.
- synthetic generator modules still exist and fallback branches can return synthetic health if real-only is disabled.
- `/api/status` can derive data source from market-hours logic rather than the same SSOT used by `/api/state`.

**Impact:** different endpoints can describe the same runtime differently.

**Required fix:** define one authoritative runtime data-source enum: `LIVE_BROKER`, `LIVE_PUBLIC`, `BHAVCOPY_EOD`, `SYNTHETIC`, `FALLBACK`, `NOT_READY`. Every endpoint and dashboard card must use this same value.

**Status:** BLOCKER.

---

## MV1-02 — `/api/health` can say analyzer ready even when market proof is absent

**Evidence:** `dashboard/backend/app.py` returns broker-connected `ANALYZER_READY` state in REAL_ONLY mode when Dhan is connected.

**Observation:** This is acceptable as broker/analyzer status, but it is unsafe if UI/agents read it as production readiness.

**Required fix:** split statuses clearly:

- `broker_ready`
- `analyzer_ready`
- `paper_market_ready`
- `production_trade_ready`

`ANALYZER_READY` must never imply `trade_ready`.

**Status:** PARTIAL_PASS / NEEDS_LABEL_FIX.

---

## MV1-03 — Runtime state store depends on output files and can become stale/incomplete

**Evidence:** `dashboard/backend/runtime_state_store.py` syncs state from `outputs/health.json`, positions file, PnL file, and `top_trade_signal.json`.

**Observation:** If those files are stale/missing, `/api/state` can become incomplete even while `/api/broker/status` reports connected.

**Required fix:** add freshness age and source provenance to every state field:

- `source_file`
- `source_timestamp`
- `age_seconds`
- `is_stale`
- `proof_status`

**Status:** BLOCKER for dashboard truth.

---

## MV1-04 — Position reconciliation is not broker-truth yet

**Evidence:** `dashboard/backend/position_reconciliation.py` says broker is truth, but `get_broker_positions()` is TODO and returns an empty list.

**Observation:** The system cannot honestly claim broker position reconciliation while broker positions are not fetched.

**Required fix:** implement read-only Dhan positions fetch, then compare broker positions vs internal ledger and dashboard state. Until then, show:

```text
BROKER POSITION RECONCILED: NO / NOT IMPLEMENTED
```

**Status:** HARD_BLOCKER.

---

## MV1-05 — Dashboard proof gates are hardcoded and can overstate readiness

**Evidence:** `dashboard/app.js` contains static `proofGates` and static `readinessLadder` values.

**Observation:** The UI can show proof PASS even if official proof matrix has warnings or `trade_ready=false`. ML Accuracy can be shown as PASS despite weak rho and insufficient validation days.

**Required fix:** dashboard proof tab must be driven from backend proof matrix and pipeline reports, not frontend hardcoded arrays.

**Status:** BLOCKER.

---

## MV1-06 — Dashboard lacks hard production-ready computation

**Evidence:** `dashboard/app.js` did not show a clear runtime computation for `PRODUCTION READY: NO` based on trade-ready, data source, market state, contract count, signal, broker reconciliation, and execution readiness.

**Required fix:** add a backend endpoint or frontend computed value:

```text
production_ready = trade_ready && data_live && market_open && valid_contract && signal_live && risk_pass && broker_reconciled && execution_supported && user_approved
```

If any condition is false, dashboard must show red `PRODUCTION READY: NO` with exact blockers.

**Status:** BLOCKER.

---

## MV1-07 — Security is not production-dashboard grade

**Evidence:** `dashboard/backend/app.py` configures CORS with `allow_origins=["*"]` and `allow_credentials=True`; root endpoint advertises `/docs`.

**Observation:** This is acceptable for development/analyzer only, not for production trading control.

**Required fix:** add auth, restrict CORS origins, protect or disable docs in production, add security headers and rate limiting.

**Status:** BLOCKER.

---

## MV1-08 — Source-of-truth naming is still confusing

**Observation:** Current system uses terms like `live`, `real`, `synthetic`, `not_ready`, `PAPER`, `ANALYZER_READY`, `BROKER LIVE`, and `trade_ready` in overlapping ways.

**Impact:** agents and users can misread connectivity as trading readiness.

**Required fix:** standardize vocabulary:

| Term | Meaning |
|---|---|
| `BROKER_CONNECTED` | Dhan read-only status works |
| `DATA_LIVE` | fresh usable market/option data exists |
| `ANALYZER_READY` | safe monitoring/prediction only |
| `PAPER_READY` | real market paper lifecycle possible |
| `TRADE_READY` | all production proof gates pass |
| `LIVE_ENABLED` | real order placement explicitly allowed |

**Status:** BLOCKER until UI/API labels are normalized.

---

# Mandatory forensic gap framework

## 1. Data gaps

**Question:** Is the system using real, fresh, complete data or stale/synthetic/fallback data?

**Current status:** BLOCKER due source-truth conflict and missing freshness proof.

## 2. Signal gaps

**Question:** Is there a valid live signal, or only stale/fallback/no-trade output?

**Current status:** BLOCKER until live market signal is proven.

## 3. Tradability gaps

**Question:** Can the selected underlying/contract actually be traded in options?

**Current status:** BLOCKER because contract/token/liquidity path is not fully proven.

## 4. Option-chain gaps

**Question:** Is option-chain data complete enough for strike selection and risk?

**Current status:** NOT_PROVEN.

## 5. Broker gaps

**Question:** Is broker connectivity enough for read-only proof, paper proof, and eventual execution?

**Current status:** PARTIAL_PASS / NEEDS_BROKER_RUNTIME.

## 6. Proof gaps

**Question:** Are PASS labels truthful, or hiding fallback/simulation?

**Current status:** FALSE_PASS_RISK.

## 7. Dashboard gaps

**Question:** Does dashboard show actual truth or attractive/green status?

**Current status:** BLOCKER / NEEDS_BROWSER_PROOF.

## 8. Risk gaps

**Question:** Is max loss controlled before any order can be placed?

**Current status:** NOT_PROVEN.

## 9. Execution gaps

**Question:** Can the system go from signal to order to fill to exit to P&L correctly?

**Current status:** HARD_BLOCKER.

## 10. Governance gaps

**Question:** Who or what is allowed to declare production-ready?

**Current status:** BLOCKER.

---

# Non-negotiable rules for Claude and all agents

1. Never call simulated/fallback/weekend lifecycle proof production proof.
2. Any fallback, synthetic, stale, closed-market, or non-token proof must be at most `PASS_WITH_WARNINGS`.
3. Official trade-ready authority is proof matrix + full pipeline + dashboard truth + broker reconciliation + user approval.
4. Do not enable live trading from automation.
5. Every goal must be decomposed into the 10 gap framework before action.
6. Every agent must update this file after material findings, fixes, or proof runs.
7. Dashboard must distinguish broker connectivity, analyzer readiness, paper readiness, trade readiness, and live enablement.

---

# Current final statement

The current System3 is a useful Analyzer/Paper foundation, but it has not yet reached the original design target of a proof-first, option-tradability-aware, broker-reconciled, risk-controlled, self-learning, ultra-dashboard-governed production trading system. Multi-validation Batch 1 adds concrete backend and dashboard evidence that source-of-truth, proof classification, position reconciliation, dashboard hardcoded PASS logic, and security governance remain open blockers.
