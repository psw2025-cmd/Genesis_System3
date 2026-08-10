# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 03:50 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `50d89073f9c554a7884ff10a031041e65d6b52c5`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd` (`fix(ui): final cleanup - remove all blocked/unavailable terminology`).
- Commits after `b70af343...` are audit-report-only in the current evidence set.
- Latest merged application/UI PR remains PR #96. Recent merged PRs #92-#96 were rechecked; no newer application PR was found in this run.
- Combined status checks for current audit-report HEAD returned no statuses; workflow-run lookup for application HEAD `b70af343...` returned no runs through the connector. This is not failure proof, but it is also not same-revision CI/runtime readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt only.
- Audit posture: ANALYZER/PAPER. Live-money routing stays OFF. No audit action may enable, place, modify, cancel or route a live order.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision proof required |
| Dashboard login contract | **FAIL / P0** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| Data/source/staleness truth | **FAIL / P0-P1** | **READY TO PATCH** via typed envelopes |
| Option chain / Greeks | **INCOMPLETE / P0-P1** | warming fix ready; full provenance contract required |
| Paper UI mutation control | **FAIL / P0-P1** | **READY TO PATCH** — dead/unproven route must not render |
| Paper execution lifecycle | **FAIL / P0** | **READY TO PATCH** canonical mutation service |
| Paper restart/idempotency safety | **FAIL / P0-P1** | **READY TO PATCH** immutable IDs + durable ledger |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | canonical lifecycle/reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned `RiskPolicy` + mandatory `PreTradeRiskService` |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| Legacy mutation UI residue | **FIX-REQUIRED / P0-P1** | quarantine/remove from deployment surface |
| Google Cloud provenance | **NOT PROVEN / P1** | exact revision/image/runtime evidence required |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must map to a canonical remediation containing root cause, exact files/routes, target behavior, minimal implementation, ordered patch steps, schema/API changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior and implementation status `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed or unproven evidence must never become green, PASS, zero-risk, zero-P&L, PAPER SAFE, live data or trade-ready through frontend/backend defaults.

## 3. Retained verified findings

### Authentication / session

- **AUTH-001 / P0:** frontend login request body does not match backend `api_key` contract.
- **AUTH-002 / P1:** protected data polling starts before auth is established.
- **AUTH-003 / P1:** raw dashboard key is stored in browser `sessionStorage` and re-injected.
- **AUTH-004 / P1:** independent server session expiry/revocation proof remains incomplete.

### Global UI / data truth

- **UI-001 / P0:** absence/error can become plausible valid-looking data.
- **UI-002 / P0-P1:** rank/score can be mislabeled as gain/forecast percentage.
- **UI-003 / P1:** source identity can be inferred from frontend fallbacks rather than backend provenance.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed, freshness, account reads, router permission and deployment provenance are separate truth domains but are sometimes conflated.
- **UI-005 / P1:** permissive defaults collapse unknown into safe/neutral values.
- **UI-006 / P1:** empty state is not consistently distinguished from `PROVEN_EMPTY`, API/auth/schema/stale/no-run states.
- **UI-007 / P1:** shared market-data truth envelope is missing.
- **UI-009 / P0:** PAPER/LIVE/LOCKED is not driven by one authoritative runtime safety object.
- **UI-010 / P1:** immutable production prediction ledger remains unproven.
- **UI-011 / P1:** full enforceable portfolio/factor/scenario risk remains unproven.
- **UI-012/UI-013/UI-014 / P2:** workspace rationalization, responsive/mobile and keyboard/focus behavior remain incomplete/unproven.
- **UI-018 / P1:** source/build labels are not deployment compatibility proof.
- **UI-019 / P1:** broker health needs a typed state machine.

### Option chain / Greeks

- **CHAIN-001 / P0:** warming/no-data chain can produce `PCR=1` instead of unknown.
- **CHAIN-002 / P1:** Dhan-looking chain verification lacks complete event-time/freshness/schema/normalizer/completeness proof.
- **CHAIN-003 / P1:** full Delta/Gamma/Theta/Vega are not displayed in Option Chain.
- **CHAIN-004 / P1:** Dhan row → normalized inputs → Greeks calculator → UI provenance is not proven end to end.
- **CHAIN-005 / P1:** IV unit/schema is implicit.

### Readiness / gates

- **READY-001 / P0:** missing live/order evidence can default safe.
- **READY-002 / P0:** money-ready calculation excludes required paper lifecycle proof.
- **READY-003 / P0-P1:** gates can pass from object presence/structural shape rather than all semantic checks.
- **READY-004 / P1:** funds/holdings/positions success semantics are too weak.
- **READY-005 / P0:** trader-ready can pass transport checks without lifecycle/expectancy proof.
- **READY-006 / P1:** core E2E PASS is transport-level only.
- **READY-007 / P1:** E2E Dhan proof lacks full freshness/schema envelope.
- **READY-008 / P1:** active Live Gate still contains Render-era instructions.
- **READY-009 / P1:** human approval lacks exact evidence revision/time provenance.

### Paper / Trade / Positions retained

- **PAPER-001 / P0:** missing safety fields can yield `PAPER SAFE`.
- **PAPER-002 / P0:** missing market source can yield live-looking Dhan state.
- **PAPER-003 / P1:** missing monetary fields can render `₹0.00`.
- **PAPER-004 / P1:** missing provenance can display `INTRADAY`, `NSE_FNO`, `PAPER_CLOUD_SIM`, `DHAN_LIVE` defaults.
- **PAPER-005 / P1:** paper-safe proof relies heavily on negative evidence rather than simulator/ledger proof.
- **PAPER-006 / P1:** position performance defaults to zero.
- **PAPER-007 / P1:** empty positions lack explicit truth state.
- **PAPER-008 / P1:** Force Paper Tick lacks visible idempotency/correlation proof.
- **PAPER-009 / P1:** immutable lifecycle event chain is not exposed.
- **TRADE-001 / P1-P2:** current Trade tab is scanner/chain context, not a controlled paper-order/risk workstation.
- **TRADE-002 / P0-P1:** `gain_rank` can be rendered as `GAIN %`.
- **TRADE-003 / P1:** `EOD/live` does not prove freshness.

### Risk retained

- **RISK-001 / P0:** browser supplies risk limits instead of selecting server-owned policy.
- **RISK-002 / P0:** missing risk policy can use permissive defaults.
- **RISK-003 / P0-P1:** unavailable risk inputs can become zero risk.
- **RISK-004 / P1:** existing VaR is not a reproducible institutional portfolio VaR contract.
- **RISK-005 / P0:** execution guardrail fails open on missing market/instrument/trade-count evidence.
- **RISK-006 / P0:** canonical risk guardrail wiring into execution path is unproven.
- **RISK-007 / P1:** Risk & Scenarios uses a non-contract `autoGates.active` proxy.
- **RISK-008 / P0-P1:** lifecycle gate can promote from position shape instead of immutable lifecycle proof.
- **RISK-009 / P1:** auto-gate refresh/evaluation errors can be swallowed and old artifacts retained.

## 4. New deep-slice findings — paper mutation, persistence and execution ownership

### PAPER-010 / P0-P1 — `Force Paper Tick` is an unproven/dead product control

`dashboard/frontend/src/components/PaperTrading.tsx` renders `Force Paper Tick` and calls `POST /api/paper/tick`. Repository-wide exact searches for `/api/paper/tick` and `paper_tick` found no backend implementation. The current `dashboard/backend/routers/trading.py` exposes `/api/paper`, `/api/pnl`, `/api/positions`, `/api/trades`, `/api/trades/today`, `/api/pnl/today` and other read endpoints, but no paper-tick mutation route.

**Symptom:** the UI advertises a mutation capability whose backend contract is not present in the audited route owner.

**Real-money/paper impact:** dead controls destroy operator trust; if later patched ad hoc, the mutation could bypass the canonical risk/idempotency/ledger design.

**Canonical solution:** capability-driven UI. Backend exposes a read-only `paper_mutation_capability` contract. The button is hidden/disabled unless the exact route, auth policy, `PreTradeRiskService`, idempotency store and lifecycle ledger are all available on the same runtime revision.

**Files:** `PaperTrading.tsx`, `dashboard/backend/routers/trading.py` or a new dedicated `paper_mutations.py`, API capability schema/tests.

**Closure tests:** route inventory test; browser test proving no dead control; negative route test; capability mismatch test; mutation unavailable => no button; no live-order APIs called.

**Status:** `READY TO PATCH`.

### PAPER-011 / P0 — actual paper position creation bypasses canonical pre-trade risk authority

`scripts/run_live_chain.py::run_cycle()` directly calls `self.paper_executor.execute_trade(...)` when QC passes and signal action is `TRADE`. It then persists an OPEN trade with `TradeHistoryStore`. No `risk_decision_id`, server-owned policy version, portfolio snapshot ID, market truth ID or idempotency key is required before position creation.

**Root cause:** signal/QC and execution are directly coupled; risk is not a mandatory independent authority.

**Solution:** replace direct executor invocation with `PaperMutationService.create_order(candidate_id, market_truth_id, ...)`. That service must call `PreTradeRiskService.evaluate()` and require a fresh explicit PASS before any fill/position event. `PaperExecutor` becomes a simulator behind the service, never a public mutation authority.

**Regression risk:** existing simulations that omit risk evidence will stop creating entries. This is desired fail-closed behavior; tests must add explicit policy/market/portfolio fixtures rather than restoring defaults.

**Status:** `READY TO PATCH`.

### PAPER-012 / P0-P1 — paper executor identity/state is process-local and restart-unsafe

`PaperExecutor.__init__()` initializes `self.positions = {}`, `self.trade_history = []`, and `self.next_position_id = 1`. Position IDs are generated as `POS_0001`, `POS_0002`, etc. The executor does not restore sequence/state from a durable ledger before new creation.

**Impact:** restart can lose in-memory lifecycle context and can reuse position IDs unless another layer prevents it. Exactly-once mutation and reconciliation are therefore not proven.

**Solution:** durable append-only lifecycle ledger owns IDs. Use UUID/ULID or database-generated immutable IDs plus `correlation_id`, `candidate_id`, `paper_order_id`, `fill_event_id`, `position_id`, `idempotency_key`. Rebuild materialized open positions from ledger on startup and verify ledger ↔ projection reconciliation before accepting new mutations.

**Status:** `READY TO PATCH`.

### PAPER-013 / P1 — stale/absent contract updates silently reuse the last price

`PaperExecutor.update_positions()` uses the position's last `current_price/current_mid` when the contract is missing from the current data. It then continues P&L calculation and stop/target evaluation without an explicit stale-quality state.

**Impact:** an operator can see apparently current MTM and lifecycle logic while the underlying contract quote is unavailable.

**Solution:** every MTM event requires `DataTruthEnvelope`. Missing contract => `price_quality=STALE_OR_MISSING`; preserve last-good price only for display with watermark and age, but do not trigger fresh-price SL/target logic after freshness TTL. Policy decides bounded stale behavior; default is no new lifecycle trigger.

**Status:** `READY TO PATCH`.

### PAPER-014 / P1 — realized P&L is gross and lifecycle costs/reconciliation are incomplete

On close, `PaperExecutor` records realized P&L from entry/current price × quantity. The audited path does not require exit slippage, fees/taxes, fill-quality evidence or an explicit `RECONCILED` terminal event before performance is consumed.

**Impact:** gross simulated P&L can overstate strategy economics and cannot support positive after-cost expectancy claims.

**Solution:** simulator versioned fill model on entry and exit, configurable slippage, fees/taxes, `gross_pnl`, `costs`, `net_pnl`, reconciliation status and immutable source event times. Performance/readiness consumes only reconciled after-cost outcomes.

**Status:** `READY TO DESIGN/PATCH`.

### PAPER-015 / P1 — paper read APIs swallow file/JSON errors into empty/zero-looking truth

`dashboard/backend/routers/trading.py::_load_json()` catches all exceptions and returns defaults. `/api/paper` and `/api/pnl` then construct zero/empty summaries when files are absent or invalid.

**Impact:** missing/corrupt state can look like valid zero P&L / zero trades / no positions.

**Solution:** `_load_json` returns a typed load result `{quality_state, error_code, source_file, mtime, parsed_value}`. Parse/file errors propagate as `ERROR/NO_DATA`; only an explicitly valid empty ledger can be `PROVEN_EMPTY`.

**Status:** `READY TO PATCH`.

### PAPER-016 / P0-P1 — `paper_truth` hard-codes negative safety claims instead of reporting measured authority

`dashboard/backend/routers/trading.py::_truth()` always returns `paper_order_mode="ANALYZER_PAPER_ONLY"`, `live_trading_allowed=False` and `broker_order_endpoints_called=False`. Those fields are static declarations, not execution telemetry tied to router state, safety revision or audited calls.

**Impact:** UI can treat declarations as proof and display green `PAPER SAFE` even when authoritative runtime safety is unavailable.

**Solution:** remove safety authority from `_truth()`. `paper_truth` contains ledger provenance only; global `SafetyTruth` owns mode/router/kill-switch. Broker-order call evidence, if required, comes from immutable router audit telemetry with revision/time/evidence ID.

**Status:** `READY TO PATCH`.

### LEGACY-001 / P0-P1 — legacy Streamlit UI still contains mutation-oriented controls

`dashboard/app.py` contains `Submit gated order`, `Square off all`, and `Cancel` controls wired to `/place-order`, `/emergency-exit` and order-delete calls. This run did not prove that this Streamlit surface is deployed, so runtime exposure is **UNPROVEN**, not asserted. Nevertheless it is dangerous deployment residue because it conflicts with the analyzer/paper/live-off product architecture.

**Solution:** classify `dashboard/app.py` as legacy/non-deployable or remove mutation controls entirely. CI/deployment guard must assert the production entrypoint does not include legacy mutation UI. Server mutation routes remain independently fail-closed even if a legacy client is accidentally deployed.

**Closure:** deployment-entrypoint test, route/control inventory, grep/AST guard for forbidden production mutation controls, Cloud Run exact revision proof, browser navigation proof showing only V5 product shell.

**Status:** `READY TO PATCH` for quarantine/guard; deployment exposure remains `UNPROVEN`.

## 5. Verification counters

Independent paths only; repeated reading of the same artifact does not increment.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `9/20` | OPEN — paper read-file fallback + stale MTM paths added |
| UI-002 | `3/20` | OPEN |
| UI-003 | `3/20` | OPEN |
| UI-005 | `8/20` | OPEN — paper router defaults added |
| UI-006 | `5/20` | OPEN — corrupt/missing ledger vs true empty added |
| UI-007 | `3/20` | OPEN — MTM data truth requirement added |
| UI-009 | `6/20` | OPEN — static `_truth()` safety declaration added |
| UI-011 | `3/20` | OPEN — execution insertion point mapped |
| UI-016 | `4/20` | OPEN |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `2/20` | OPEN |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `1/20` | OPEN |
| CHAIN-005 | `1/20` | OPEN |
| READY-001 | `4/20` | OPEN — static paper safety truth path added |
| READY-003 | `2/20` | OPEN |
| PAPER-001 | `2/20` | OPEN — backend `_truth()` independent path |
| PAPER-003 | `2/20` | OPEN — read API zero fallback independent path |
| PAPER-005 | `2/20` | OPEN — `_truth()` negative-evidence declaration path |
| PAPER-008 | `2/20` | OPEN — route capability absent/unproven |
| PAPER-009 | `2/20` | OPEN — executor/persistence path has no immutable event chain |
| PAPER-010..016 | `1/20` each | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| LEGACY-001 | `1/20` | OPEN / deployment exposure UNPROVEN |

No finding is `LOCKED-20X`.

## 6. Canonical truth contracts

### 6.1 `SafetyTruth`

```text
mode: ANALYZER | PAPER | LIVE | UNKNOWN
live_trading_enabled: boolean | null
auto_execute_enabled: boolean | null
order_router_state: DISABLED | ARMED | ENABLED | UNKNOWN
kill_switch_state: SAFE | TRIPPED | UNKNOWN
source_revision
cloud_run_revision
image_digest
policy_version
verified_at
age_ms
proof_status: PROVEN | STALE | UNKNOWN | ERROR
```

### 6.2 `DataTruthEnvelope`

```text
source
provider_session
instrument
source_event_time
backend_received_time
frontend_received_time
age_ms
freshness_threshold_ms
market_state
schema_version
normalizer_version
row_count
completeness_pct
quality_state: PROVEN | PROVEN_EMPTY | STALE | NO_DATA | API_ERROR | AUTH_REQUIRED | SCHEMA_ERROR | UNKNOWN
source_revision
runtime_revision
```

### 6.3 `PaperLifecycleTruth`

```text
correlation_id
candidate_id
prediction_evidence_id
paper_order_id
idempotency_key
simulator_id
simulator_version
fill_event_id
requested_price
fill_price
entry_slippage
exit_slippage
fees_taxes
market_truth_id
market_event_time
risk_decision_id
position_id
exit_trigger_id
exit_event_id
gross_pnl
net_pnl
reconciliation_status
ledger_revision
source_revision
runtime_revision
```

### 6.4 `GateTruth`

```text
gate_id
status: PASS | FAIL | PENDING | STALE | ERROR | UNKNOWN
threshold
observed_value
evidence_id
source_revision
runtime_revision
verified_at
age_ms
policy_version
reason
```

### 6.5 `RiskPolicy` — server-owned only

```text
policy_id
policy_version
policy_hash
environment
account_scope
strategy_scope
max_positions
max_gross_exposure
max_net_exposure
max_daily_loss
max_drawdown
max_concentration_pct
max_delta
max_gamma
max_vega
min_liquidity
max_spread_pct
max_data_age_ms
allowed_instruments
valid_from
valid_until
source_revision
```

### 6.6 `PreTradeRiskTruth`

```text
risk_decision_id
candidate_id
policy_id
policy_version
portfolio_snapshot_id
market_truth_id
evaluated_at
expires_at
enforcement_state: PASS | FAIL | UNKNOWN | ERROR
checks[]: {check_id,status,observed,threshold,evidence_id,reason}
source_revision
runtime_revision
```

### 6.7 `PaperMutationCapability`

```text
mutation_available: boolean
route_version
auth_policy_version
risk_service_version
ledger_version
idempotency_store_state
simulator_version
runtime_revision
proof_status: PROVEN | STALE | UNKNOWN | ERROR
reason
```

The frontend renders an actionable paper mutation control only when this capability is exact-revision `PROVEN` and live router remains disabled.

## 7. Canonical remediation roadmap

### SOL-01 — dashboard auth/session

Fix login body; cookie-only browser auth; remove raw-key `sessionStorage`; auth-gate all polling; add TTL/revocation/replay tests.

**Status:** `READY TO PATCH`.

### SOL-02 — authoritative safety truth

One backend `SafetyTruth` feeds TopBar, proof bar, Truth Control, E2E, Paper Trading and Live Gate. Missing/stale => UNKNOWN; UI never derives live/order safety.

**Status:** `READY TO PATCH`.

### SOL-03 — typed data/null semantics

Remove `||0`/plausible production defaults; add provenance/event time/receive time/age/schema/quality; only valid empty data becomes `PROVEN_EMPTY`.

**Status:** `READY TO PATCH` frontend/read APIs; backend envelope implementation required.

### SOL-04 — semantic readiness

HTTP 200/object presence never equals PASS. Paper lifecycle, reconciliation, risk and positive after-cost expectancy remain required; stale/error propagates.

**Status:** `READY TO PATCH`.

### SOL-05 — Option Chain + Greeks

Versioned chain row schema with bid/ask/LTP/OI/ΔOI/volume/IV/Delta/Gamma/Theta/Vega/Rho, explicit IV units and Greeks model/source assumptions; aggregate portfolio Greeks.

**Status:** warming/PCR `READY TO PATCH`; complete provenance contract `READY TO DESIGN/PATCH`.

### SOL-06 — immutable paper lifecycle and reconciliation

This run upgrades SOL-06 from design-only to an implementation-ready architecture.

**Exact ownership changes:**

- `dashboard/frontend/src/components/PaperTrading.tsx`: capability-driven mutation button; no direct optimistic assumptions.
- new `dashboard/backend/routers/paper_mutations.py` or equivalent dedicated mutation owner: authenticated paper-only mutation endpoint.
- new `dashboard/backend/paper_mutation_service.py`: orchestration authority.
- `src/trading/paper_executor.py`: simulator only; no direct identity authority; no process-local sequencing as canonical ID source.
- `scripts/run_live_chain.py`: call mutation service instead of direct `execute_trade()`.
- `src/storage/trade_history.py` or new durable ledger store: append-only lifecycle/idempotency ledger.
- `dashboard/backend/routers/trading.py`: read projections return typed ledger/data quality; no static safety authority.
- tests: route inventory, lifecycle, restart/replay, idempotency, stale quote, reconciliation, costed P&L.

**Ordered implementation:**

1. Introduce durable lifecycle schema and immutable IDs.
2. Add idempotency store and unique constraint on mutation key/candidate intent.
3. Add `PaperMutationCapability` endpoint.
4. Implement `PaperMutationService.create_order()`.
5. Require `PreTradeRiskTruth=PASS`, current `DataTruthEnvelope`, candidate/evidence IDs.
6. Call versioned simulator for fill; append `PAPER_ORDER_CREATED` then `SIM_FILL` then `POSITION_OPEN` atomically/transactionally where supported.
7. Replace direct `run_live_chain.py -> PaperExecutor.execute_trade` path.
8. Rebuild materialized positions from ledger on startup; reconcile before accepting new mutations.
9. MTM events carry source/time/age; stale/missing quote cannot trigger fresh-price SL/target logic.
10. Exit path records exit slippage/fees/taxes and `gross_pnl/net_pnl`; final state requires `RECONCILED`.
11. React Force Paper Tick renders only from proven capability; otherwise hidden/disabled with exact reason.
12. Remove safety declarations from `paper_truth`; consume global `SafetyTruth`.

**PASS criteria:** no paper position can exist without candidate ID, fresh risk PASS, market truth ID, idempotency key, order/fill events and durable ledger entry; restart cannot duplicate/reuse IDs; same idempotency key returns same result; stale quote cannot create a fresh exit; missing/corrupt ledger returns ERROR not zero/empty; after-cost P&L reconciles to events; live order endpoints remain uncalled.

**Rollback/fail-safe:** if ledger/risk/data capability is unavailable, inhibit new paper mutation and keep read-only last-good data explicitly stale; never fall back to direct executor creation.

**Status:** `READY TO PATCH`.

### SOL-07 — scanner metric contract

Distinct nullable rank/score/forecast/realized/probability fields; no rank→percent fallback; validated predictions require ledger evidence ID.

**Status:** `READY TO PATCH`.

### SOL-08 — Google Cloud provenance

Remove active Render instructions; expose backend/frontend commits, Cloud Run revision, image digest, deploy time and policy version; verify production entrypoint excludes legacy Streamlit mutation UI.

**Status:** wording/quarantine guard `READY TO PATCH`; runtime metadata proof required.

### SOL-09 — canonical pre-trade risk authority

Server-owned immutable `RiskPolicy`; `PreTradeRiskService.evaluate()` is mandatory before every paper mutation and any future live router. Missing policy/data/instrument/ledger state => UNKNOWN/ERROR and deny. Persist fresh `risk_decision_id` into lifecycle.

**Status:** `READY TO PATCH`; exact insertion point is now mapped to the replacement of direct `run_live_chain.py -> PaperExecutor.execute_trade()`.

### SOL-10 — legacy UI quarantine

Mark `dashboard/app.py` non-production/legacy, remove mutation controls or isolate behind non-deployable development packaging. Add CI guard that the Cloud Run entrypoint is the V5 FastAPI/React product and legacy Streamlit mutation controls are absent from deployed navigation/runtime.

**Status:** `READY TO PATCH`; actual runtime exposure remains `UNPROVEN` until Cloud Run revision/entrypoint proof is collected.

## 8. Prioritized implementation order

### P0 Wave 1 — false-green/fail-open elimination

1. SOL-01 auth body + auth-gated polling.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-09 server-owned risk + mandatory pre-trade authority.
4. SOL-06 lifecycle IDs/idempotency/ledger + remove direct executor mutation path.
5. PAPER-010 capability-driven removal of dead Force Paper Tick control.
6. SOL-04 semantic readiness/lifecycle gate repair.
7. SOL-03 remove zero/live/PCR/safety defaults.
8. SOL-10 legacy mutation UI quarantine.
9. SOL-07 rank-as-percent repair.

**Wave-1 success criterion:** no missing field/file/route/policy/quote, parse error, HTTP success, object existence, stale last-good value or browser default can create green safety/readiness/risk/P&L/mutation truth.

### P1 Wave 2 — prove paper/market/account economics

1. complete `DataTruthEnvelope`;
2. lifecycle restart/replay/reconciliation;
3. costed fills/P&L;
4. Option Chain + complete Greeks provenance;
5. portfolio/scenario risk;
6. exact Cloud Run runtime/source/entrypoint provenance.

### P2 Wave 3 — institutional operator quality

Responsive tablet/mobile, accessibility, command palette/search, drilldowns, observability/SLO/incidents, security/session settings and audit export.

## 9. Product information architecture target

1. **Command Center** — Overview + Decision Intel + authoritative truth strip.
2. **Market / Scanner** — watch, scanner, ranker, signals.
3. **Options & Greeks** — full chain, IV/OI/liquidity, complete Greeks.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + calibration/evidence.
5. **Paper / Trade Lifecycle** — capability-driven paper ticket/tick, immutable events, fills, positions, P&L, reconciliation.
6. **Portfolio & Risk** — server-owned policy, current risk decision, exposure, aggregate Greeks, scenarios.
7. **Data & Broker Health** — provenance/freshness/auth/read/feed truth.
8. **Readiness / Proof** — semantic gates, E2E proof, Live Gate.
9. **Observability** — alerts, logs, errors, latency, deployment/runtime truth.
10. **Security / Settings** — sessions, policy versions, permissions, audit export, non-authoritative UI preferences.

Current repo tabs remain represented through this rationalized hierarchy; no conceptual rename implies that backend capability already exists.

## 10. Product UI visual evolution — V7

New concept: **Paper Execution Control V7**.

Changes from V5 paper lifecycle concept:

- Force Paper Tick is no longer assumed to exist; it is hidden until backend capability is exact-revision proven.
- Mutation starts from candidate/evidence/risk/market/idempotency IDs, not direct position creation.
- Server validation pipeline visibly separates auth, mutation policy, market truth, pre-trade risk, duplicate protection, simulator and ledger append.
- Lifecycle is represented as immutable event stream rather than only a positions table.
- Restart reconciliation and duplicate-idempotency checks are first-class operator truth.
- Live order control is permanently locked.
- Missing route/risk/ledger capability is shown as PENDING/UNKNOWN, never a clickable dead button.

Visual artifact generated for this iteration: `Genesis_System3_Paper_Execution_Control_Target_V7.png`.

## 11. Positive foundations to preserve

- shared UI design tokens/numeric styling and reduced-motion direction;
- semantic sidebar/ARIA foundations;
- visible pending states in unfinished workspaces;
- scanner-vs-prediction distinction direction;
- wrong-symbol option-chain suppression;
- source/snapshot/stale messaging foundation;
- bid/ask <=0 rendered missing rather than fake;
- Live Gate approval does not automatically enable live trading;
- Paper Trading states that Dhan production is not a paper sandbox and local fills are simulated;
- `PaperExecutor` max-position guard remains useful as defense-in-depth after canonical risk enforcement.

These are foundations, not readiness proof.

## 12. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture, not a defect.

## 13. Closure standard

A finding becomes `CLOSED` only when evidence is tied to the exact changed revision: source fix inspected; positive/negative tests; build/static/type checks; unit/integration/browser tests; route inventory; network/console proof; frontend/backend schema reconciliation; restart/idempotency/reconciliation tests; runtime/deployment proof where required; analyzer/live-off unchanged; no contradictory independent evidence.

## 14. Next audit / solution slices

1. **WebSocket/polling truth** — reconnect/backoff, heartbeat, stale retention, ordering, duplicate subscriptions, event timestamps and browser polling interaction.
2. **Option-chain backend normalization** — exact Dhan normalizer, IV/Greeks owner, timestamp/schema path.
3. **Observability / Cloud Run provenance** — source/runtime revision, image digest, production entrypoint, latency/errors/browser failures/dependency truth.
4. **DB/state-store consistency** — `TradeHistoryStore`, JSON state files, SQLite/other stores, locking/concurrency, atomicity and duplicate state authorities.
5. **Responsive/accessibility** — desktop/tablet/mobile, keyboard/focus/live regions/dense-table behavior.

## 15. Hard safety rule

A green UI, successful build, endpoint HTTP 200, zero-valued risk/P&L, static `PAPER SAFE`, human approval, absent route error, missing market data or a process-local simulator never substitutes for source/freshness/lifecycle/enforceable risk/reconciliation/positive after-cost expectancy/exact runtime proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.
