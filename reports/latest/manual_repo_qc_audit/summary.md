# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 02:50 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `6273114b4a14f561c64a647f3721eaff033933b8`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after `b70af343...` are audit-report-only unless a later application commit is explicitly named.
- Latest merged application/UI PR reviewed remains PR #96; PRs #92-#96 remain relevant to the current V5 UI/auth surface.
- No workflow run was returned for audit-report HEAD `6273114...`; this is not CI-failure proof, but it is also not same-revision readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt only.
- Audit posture: ANALYZER/PAPER. Live-money routing stays OFF. No audit action may enable, place, modify, cancel or route a live order.
- This Markdown is the single continuously maintained audit and remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Current application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision proof still required |
| Dashboard login HTTP contract | **FAIL / P0** | **READY TO PATCH** |
| Pre-auth protected polling | **FAIL / P1** | **READY TO PATCH** |
| Browser raw API-key storage | **FIX-REQUIRED / P1** | **READY TO PATCH** after cookie contract test |
| Global mode/safety truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| Readiness semantics | **FAIL / P0** | **READY TO PATCH** via semantic `GateTruth` |
| Option-chain truth | **FAIL / P0-P1** | warming/null fix READY TO PATCH; provenance contract READY TO DESIGN |
| Greeks UI/provenance | **INCOMPLETE / P1** | READY TO DESIGN/PATCH |
| Paper lifecycle/reconciliation | **NOT PROVEN / P0-P1** | READY TO DESIGN immutable lifecycle |
| Scanner metric truth | **FAIL / P0-P1** | **READY TO PATCH** |
| Portfolio risk display truth | **FAIL / P0-P1** | **READY TO PATCH** null/provenance semantics |
| Risk-policy authority | **FAIL / P0** | **READY TO PATCH** server-owned policy required |
| Pre-trade risk enforcement | **NOT PROVEN / P0** | **READY TO PATCH** canonical enforcement service |
| Execution guardrail fail-closed behavior | **FAIL / P0** | **READY TO PATCH** |
| Scenario/factor risk | **PENDING / REQUIRED** | READY TO DESIGN after risk authority fix |
| Google Cloud deployment provenance | **NOT PROVEN / P1** | READY TO DESIGN/PATCH |
| Real-money trade ready | **NO** | remains locked |

## 2. Mandatory solution-driven audit rule

Every finding must map to a canonical remediation containing root cause, exact files/routes, target behavior, minimal implementation, ordered patch steps, schema/API changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior and status `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing/unknown/stale safety or risk evidence must never become green, PASS, zero-risk, paper-safe or live-ready through frontend defaults.

## 3. Verified findings retained

### Authentication / session

- **AUTH-001 / P0:** `LoginPage.tsx` POSTs `/api/auth/session` without the required JSON `api_key` body while the backend expects `DashboardAuthRequest(api_key)`.
- **AUTH-002 / P1:** `App.tsx` invokes `useData()` before `AuthGate` confirms authentication.
- **AUTH-003 / P1:** raw dashboard key is stored in `sessionStorage` and re-injected by browser interceptors.
- **AUTH-004 / P1:** server-side independent expiry/revocation is not proven.

### Global UI / data truth

- **UI-001 / P0:** missing telemetry/data can become plausible success or valid-looking data.
- **UI-002 / P0-P1:** rank/score can be mislabeled as a validated percentage/forecast.
- **UI-003 / P1:** Dhan/data source can be inferred from frontend fallback labels rather than backend provenance.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed health, freshness, account reads, order permission and deployment provenance are independent domains but are sometimes conflated.
- **UI-005 / P1:** permissive defaults collapse unknown into neutral/safe values.
- **UI-006 / P1:** empty account/position states do not distinguish `PROVEN_EMPTY` from auth/API/schema/stale/no-run conditions.
- **UI-007 / P1:** shared market-data truth envelope is missing.
- **UI-009 / P0:** PAPER/LIVE/LOCKED status is not driven by one authoritative runtime safety object.
- **UI-010 / P1:** immutable production prediction ledger is not proven.
- **UI-011 / P1:** complete factor/scenario risk and enforceable portfolio limits are not proven.
- **UI-012/UI-013/UI-014 / P2:** workspace rationalization, responsive/mobile and complete keyboard/focus behavior remain incomplete/unproven.
- **UI-018 / P1:** build/source labels are not deployment compatibility proof.
- **UI-019 / P1:** broker state machine must distinguish auth/read/feed/degraded/stale/API/schema states.

### Option chain / Greeks

- **CHAIN-001 / P0:** warming chain can fabricate `PCR=1`; warming/no-data must be null/unknown.
- **CHAIN-002 / P1:** Dhan-looking verification lacks complete timestamp/freshness/schema/normalizer/completeness provenance.
- **CHAIN-003 / P1:** full Delta/Gamma/Theta/Vega are not exposed in Option Chain.
- **CHAIN-004 / P1:** chain-to-Greeks calculator provenance is not proven end-to-end.
- **CHAIN-005 / P1:** IV unit/schema is implicit.

### Readiness / live gate

- **READY-001 / P0:** missing live/order fields can default safe.
- **READY-002 / P0:** money-ready calculation excludes paper lifecycle.
- **READY-003 / P0-P1:** risk gate can PASS from object presence instead of all required gates passing.
- **READY-004 / P1:** funds/holdings/positions success semantics are too weak.
- **READY-005 / P0:** E2E trader-ready can pass transport without lifecycle/expectancy proof.
- **READY-006 / P1:** E2E core PASS is transport-level only.
- **READY-007 / P1:** E2E Dhan proof lacks full freshness/schema envelope.
- **READY-008 / P1:** active Live Gate still contains Render-era instructions.
- **READY-009 / P1:** human-approval display lacks exact evidence revision/time provenance.

### Paper / Trade / Positions

- **PAPER-001 / P0:** missing safety fields can yield `PAPER SAFE`.
- **PAPER-002 / P0:** missing market-data source can yield live-looking Dhan state.
- **PAPER-003 / P1:** missing monetary fields can render as valid `₹0.00`.
- **PAPER-004 / P1:** missing row provenance can display plausible defaults such as `INTRADAY`, `NSE_FNO`, `PAPER_CLOUD_SIM`, `DHAN_LIVE`.
- **PAPER-005 / P1:** paper-safe proof relies mainly on negative evidence instead of a simulator/ledger chain.
- **PAPER-006 / P1:** position performance defaults to zero.
- **PAPER-007 / P1:** empty positions lack explicit truth state.
- **PAPER-008 / P1:** Force Paper Tick lacks visible idempotency/correlation proof.
- **PAPER-009 / P1:** immutable lifecycle event chain is not exposed.
- **TRADE-001 / P1-P2:** current Trade tab is scanner/chain context, not a pre-trade paper order/risk workstation.
- **TRADE-002 / P0-P1:** `gain_rank` can be rendered under `GAIN %`.
- **TRADE-003 / P1:** `EOD/live` does not prove freshness.

## 4. New deep-slice findings — Risk / auto-gates / enforcement

### RISK-001 / P0 — risk policy is currently client-supplied in the UI

`RiskDashboard.tsx` POSTs `/api/risk/check-limits` with fixed values from the browser: `max_positions=5`, `max_exposure=100000`, `max_loss=-5000`, `max_concentration_pct=50`. A professional pre-trade policy cannot be authoritative when the client chooses the limits. Even if the endpoint is read-only today, this architecture must never be reused as live/paper enforcement authority.

**Root cause:** risk-policy ownership is inverted: the presentation layer supplies policy instead of selecting a server-owned immutable policy version.

**Solution:** browser sends no raw safety limits. Backend loads `RiskPolicy` by environment/account/strategy and returns policy ID/version/hash plus evaluation. Operator-adjustable scenario limits, if supported, must be clearly labeled simulation and must never change enforcement policy.

**Status:** `READY TO PATCH`.

### RISK-002 / P0 — missing risk policy silently falls back to permissive defaults

`dashboard/backend/risk_management.py::check_risk_limits()` defaults missing limits to `5`, `100000`, `-5000`, `50`. A missing/corrupt policy can therefore still return `PASS`.

**Solution:** enforcement API requires a complete validated `RiskPolicy`; absent/invalid policy => `UNKNOWN/ERROR`, `execution_allowed=false`, reason `RISK_POLICY_UNAVAILABLE`. No enforcement default values.

**Status:** `READY TO PATCH`.

### RISK-003 / P0-P1 — risk data absence is converted to zero risk

`calculate_portfolio_risk()` returns zero exposure/P&L/VaR/ES/concentration when positions are absent, and missing entry/qty/P&L/Greeks fields default to zero. `RiskDashboard.tsx` also converts missing SSOT risk values to zero and renders green/neutral numeric cards.

**Impact:** API failure, incomplete positions or missing Greeks can visually look like low/zero risk.

**Solution:** add `RiskTruthEnvelope` with `quality_state`, source/time/age/completeness and nullable metrics. Only `PROVEN_EMPTY` may legitimately show zero exposure; missing fields render `UNKNOWN`.

**Status:** `READY TO PATCH`.

### RISK-004 / P1 — current VaR is not a production portfolio VaR contract

`calculate_portfolio_risk()` builds a small vector from each position's `(current-entry)/entry` and treats that cross-sectional vector as returns history. Parametric VaR also samples `np.random.normal(...)`, producing nondeterministic intermediate output. This is not reproducible institutional portfolio VaR.

**Solution:** until historical scenario data is available, rename it explicitly `position_return_dispersion_proxy` and prevent readiness use. Production VaR should use versioned historical return series/scenarios, current notionals/Greeks, deterministic quantiles, lookback window, confidence, valuation timestamp and policy version.

**Status:** `READY TO DESIGN`; current metric must not gate trading.

### RISK-005 / P0 — execution guardrail fails open on missing evidence

`core/engine/dhan_execution_guardrail.py::validate_execution_request()` sets `slippage_check=True` when market data is absent and `limit_check=True` when underlying is absent. `_get_daily_trade_count()` returns `0` when the log is missing, empty, malformed or read fails. `enforce_execution_limits()` returns `True` when limit `<=0`.

**Impact:** precisely the conditions that should inhibit execution can become PASS.

**Solution:** all missing/invalid market, instrument, policy and trade-count evidence fails closed. Return typed checks with `PASS|FAIL|UNKNOWN|ERROR`, never booleans with permissive defaults. `execution_allowed=True` only when every required check is explicit `PASS` and evidence is fresh.

**Status:** `READY TO PATCH`.

### RISK-006 / P0 — guardrail wiring into execution path is not proven

Repository search found `validate_execution_request` only in its defining module and documentation, not a proven execution call path. `src/trading/paper_executor.py::execute_trade()` independently enforces only `max_positions` before sizing/creating a position; it does not call a canonical exposure/loss/concentration/freshness/policy service.

**Impact:** displayed risk checks can be advisory while paper/future order creation follows a separate path.

**Solution:** introduce one backend `PreTradeRiskService.evaluate(candidate, portfolio, market_truth, policy)` and require it synchronously before **every** paper order creation and any future live-order router. The route/executor accepts a signed/immutable `risk_decision_id` generated from current evidence; stale/reused decisions fail.

**Status:** `READY TO PATCH` after exact paper route owner is mapped.

### RISK-007 / P1 — Risk & Scenarios gate status uses a non-contract field

`RiskAndScenarios.tsx` uses `autoGates?.active` to display `ARMED/LOCKED` and `ACTIVE/INHIBITED`, while the current `auto_gates_service.py` payload exposes fields such as `gates`, `trade_ready`, `analyzer_ready`, blockers and proof gates, not a documented authoritative `active` safety field.

**Impact:** absent field becomes a benign-looking `LOCKED/INHIBITED` state without proving risk-engine authority.

**Solution:** remove `autoGates.active`; render canonical `PreTradeRiskTruth.enforcement_state = ENFORCED|INHIBITED|UNKNOWN|ERROR` with policy/evidence IDs and backend source.

**Status:** `READY TO PATCH`.

### RISK-008 / P0-P1 — auto-gate lifecycle can be promoted from position shape rather than immutable lifecycle proof

`system3_gate_evaluator.py::eval_lifecycle_gate()` can set `full_proven=True` when broker is connected and positions merely contain `strike`, `entry_price` and `position_id`. That is insufficient to prove candidate→paper order→fill→MTM→exit→reconciliation.

**Solution:** remove structural promotion. `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` may PASS only from immutable lifecycle evidence with simulator/version, market timestamps, fill/slippage/fees, exit and reconciliation proof tied to exact source/runtime revision.

**Status:** `READY TO PATCH`.

### RISK-009 / P1 — auto-gate exceptions are swallowed and old artifacts may remain authoritative-looking

`auto_gates_service.py` catches failures from runtime proof refresh/evaluation with bare `except: pass`, then may fall back to existing JSON. Although artifact age is checked in one path, the returned contract does not expose evaluation error state/evidence freshness strongly enough to make refresh failure impossible to mistake for current proof.

**Solution:** capture evaluator/proof errors, propagate `quality_state=ERROR|STALE`, artifact timestamp/age and evaluation revision. A gate with failed refresh cannot remain PASS unless policy explicitly permits a bounded last-good TTL, in which case UI shows `STALE_LAST_GOOD`, not PASS.

**Status:** `READY TO PATCH`.

## 5. Verification counters

Independent paths only; rereading unchanged code does not increment.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `7/20` | OPEN — risk zero/default path added |
| UI-002 | `3/20` | OPEN |
| UI-003 | `3/20` | OPEN |
| UI-004 | `2/20` | OPEN |
| UI-005 | `7/20` | OPEN — risk defaults added |
| UI-006 | `4/20` | OPEN — zero-risk vs unproven added |
| UI-007 | `2/20` | OPEN |
| UI-008 | `2/20` | OPEN |
| UI-009 | `5/20` | OPEN |
| UI-010 | `2/20` | OPEN |
| UI-011 | `2/20` | OPEN — risk service deep slice |
| UI-016 | `4/20` | OPEN — RiskAndScenarios proxy gate added |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `2/20` | OPEN |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `1/20` | OPEN |
| CHAIN-005 | `1/20` | OPEN |
| READY-001 | `3/20` | OPEN — execution guardrail missing-data fail-open |
| READY-002 | `1/20` | OPEN |
| READY-003 | `2/20` | OPEN — lifecycle structural promotion |
| READY-004 | `1/20` | OPEN |
| READY-005 | `1/20` | OPEN |
| READY-006 | `1/20` | OPEN |
| READY-007 | `1/20` | OPEN |
| READY-008 | `1/20` | OPEN |
| READY-009 | `1/20` | OPEN |
| PAPER-001..009 | `1/20` each | OPEN |
| TRADE-001..003 | `1/20` each | OPEN |
| RISK-001..009 | `1/20` each | OPEN |

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
simulator_id
simulator_version
fill_event_id
fill_model
requested_price
fill_price
slippage
fees
market_source
market_event_time
position_id
exit_trigger_id
exit_event_id
realized_pnl_before_costs
realized_pnl_after_costs
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

No enforcement endpoint accepts authoritative limit values from the browser.

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

Order/paper creation is allowed only when required checks are explicit PASS and the decision is fresh/current.

## 7. Canonical remediation roadmap

### SOL-01 — dashboard login/session repair

**Files:** `LoginPage.tsx`, `useAuth.ts`, `App.tsx`, backend auth route/session code.

**Patch:** send required JSON body; cookie-only authenticated browser session; remove raw-key `sessionStorage`; start polling only after auth; add server TTL/revocation.

**Closure:** valid/invalid/missing-body tests, cookie-only status, zero protected requests pre-auth, logout/expiry/replay tests, frontend build/browser tests.

**Status:** `READY TO PATCH`.

### SOL-02 — authoritative `SafetyTruth`

**Files/surfaces:** backend state/safety owner, store/useData, `TopBar`, `ProductionProofBar`, Truth Control, E2E, Paper Trading, Live Gate.

**Patch:** one backend-derived safety object; missing/stale => UNKNOWN/DO NOT TRADE; UI never recomputes or enables router.

**Status:** `READY TO PATCH`.

### SOL-03 — typed `DataTruthEnvelope` + null semantics

**Surfaces:** chain, positions, funds, holdings, scanner, P&L, broker, risk metrics.

**Patch:** remove `||0` and plausible production defaults; add source/time/age/schema/quality state; explicit `PROVEN_EMPTY`; IV unit contract.

**Status:** frontend defaults `READY TO PATCH`; backend envelope `READY TO DESIGN/PATCH`.

### SOL-04 — semantic `GateTruth` readiness

**Patch:** no HTTP/object-presence PASS; paper lifecycle/reconciliation/risk/expectancy mandatory; stale/error propagates; human approval never activates routing; Google Cloud only.

**Status:** `READY TO PATCH`.

### SOL-05 — Option Chain + Greeks contract

Versioned row schema with bid/ask/LTP/OI/ΔOI/volume/IV/Delta/Gamma/Theta/Vega/Rho, provenance, calculator/version/assumptions and aggregate portfolio Greeks.

**Status:** warming-PCR `READY TO PATCH`; full contract `READY TO DESIGN/PATCH`.

### SOL-06 — immutable paper lifecycle + reconciliation

One correlation ID and immutable events: `CANDIDATE → VALIDATED → PAPER_ORDER_CREATED → SIM_FILL → OPEN → MTM_UPDATE → EXIT_TRIGGER → CLOSED → RECONCILED`; idempotency, simulator/fill/slippage/fees, market timestamps, restart-safe replay, P&L traceability.

**Status:** `READY TO DESIGN`; route/storage owner mapping remains required.

### SOL-07 — scanner metric contract

Distinct nullable `rank`, `score`, `forecast_return_pct`, `realized_return_pct`, `probability`; no rank→percent fallback; validated prediction requires ledger evidence ID.

**Status:** `READY TO PATCH`.

### SOL-08 — Google Cloud deployment provenance

Remove active Render instructions; expose backend/frontend source commits, Cloud Run revision, image digest, deployment time and policy version; compare exact runtime but never infer safety from revision alone.

**Status:** wording `READY TO PATCH`; runtime metadata `READY TO DESIGN/PATCH`.

### SOL-09 — canonical server-side pre-trade risk authority

**Maps:** UI-011, READY-003, RISK-001..009, PAPER lifecycle risk gaps.

**Known files likely to change:**

- `dashboard/backend/risk_management.py`
- `dashboard/frontend/src/components/RiskDashboard.tsx`
- `dashboard/frontend/src/components/workspaces/RiskAndScenarios.tsx`
- `dashboard/backend/auto_gates_service.py`
- `scripts/system3_gate_evaluator.py`
- `core/engine/dhan_execution_guardrail.py`
- `src/trading/paper_executor.py`
- exact `/api/risk/*` and `/api/paper/*` route owners after recursive mapping
- new server-owned `RiskPolicy` config/schema and tests

**Minimal safe implementation:**

1. Create validated immutable `RiskPolicy` loaded server-side; browser cannot submit authoritative limits.
2. Create `PreTradeRiskService.evaluate()` as the only pre-trade risk decision authority.
3. Require explicit fresh market truth, portfolio snapshot, instrument identity, policy version and account/session state.
4. Checks include position count, gross/net exposure, daily loss/drawdown, concentration, liquidity/spread, data freshness, duplicate/idempotency, margin when available, Greeks limits and kill-switch.
5. Missing policy/data/underlying/trade-count state => `UNKNOWN/ERROR`, never PASS.
6. Wire service synchronously before paper position creation. Any future live router must use the same service plus stricter live-only gates.
7. Persist `risk_decision_id` with paper lifecycle event and reject stale/reused decisions.
8. Risk dashboard becomes a read-only display of server evaluation and policy metadata; scenario controls are visually separate and never authoritative.
9. Replace current pseudo-VaR readiness usage; implement deterministic historical/scenario VaR later with explicit model version.
10. Auto-gate risk PASS must consume `PreTradeRiskTruth`, not object existence.

**Backward compatibility:** existing UI may temporarily show UNKNOWN until server policy/evidence exists; preserve analyzer/paper live-off posture. Existing historical rows without risk decision IDs are labeled legacy/unproven, not silently upgraded.

**Regression risks:** stricter fail-closed logic will block paper ticks previously allowed with incomplete data; test fixtures that omit policy/market data will fail and must be corrected rather than weakened.

**Exact closure tests / PASS criteria:**

- browser cannot alter enforced limits by request body;
- missing/corrupt policy => execution denied;
- missing market data => denied;
- missing underlying => denied;
- missing/corrupt daily trade ledger => denied or explicit policy-approved bounded degraded mode, never silent zero;
- stale market truth => denied;
- exposure/loss/concentration breach => denied with exact observed/threshold evidence;
- within-policy candidate => PASS only with complete evidence;
- same `risk_decision_id` replay after expiry/state change => denied;
- paper executor cannot create a position without fresh PASS risk decision;
- deliberate risk-service failure cannot be bypassed by UI endpoint or executor;
- auto-gate risk row cannot PASS from object presence;
- UI shows UNKNOWN instead of ₹0/green on missing risk metrics;
- analyzer/live-off flags unchanged;
- unit + integration + browser + restart/idempotency tests PASS at exact revision.

**Rollback/fail-safe:** if new risk service errors, remain ANALYZER/PAPER with new paper entries inhibited; never fall back to old permissive execution.

**Status:** `READY TO PATCH` for fail-open guardrail/defaults/client-policy removal; full wiring `READY TO PATCH` after exact route-owner inventory.

## 8. Prioritized implementation order

### P0 Wave 1 — eliminate false-green and fail-open safety

1. SOL-01 auth payload + auth-gated polling.
2. SOL-02 `SafetyTruth`.
3. SOL-09 fail-closed execution guardrail + server-owned `RiskPolicy` + pre-trade authority.
4. SOL-04 semantic readiness and lifecycle gate repair.
5. SOL-03 remove false live/zero/PCR/risk defaults.
6. SOL-07 rank-as-percent repair.

**Wave-1 success criterion:** no missing field, missing file, parse error, absent market data, absent policy, HTTP 200, object existence or frontend default can create green safety/readiness/risk/financial truth.

### P1 Wave 2 — prove paper/market/account truth

1. backend `DataTruthEnvelope`;
2. immutable paper lifecycle/idempotency/reconciliation;
3. Option Chain + complete Greeks provenance;
4. risk-decision persistence and portfolio/scenario risk;
5. exact Cloud Run runtime provenance.

### P2 Wave 3 — institutional operator quality

Navigation/workspace rationalization, responsive tablet/mobile, accessibility, command palette/search/drilldowns, observability/SLI/SLO/incidents/security settings.

## 9. Product information architecture target

1. **Command Center** — Overview + Decision Intel + authoritative truth strip.
2. **Market / Scanner** — watch, scanner, ranker, signals.
3. **Options & Greeks** — full chain, IV/OI/liquidity, complete Greeks.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + calibration/evidence.
5. **Paper / Trade Lifecycle** — paper ticket, fills, positions, P&L, reconciliation.
6. **Portfolio & Risk** — server-owned policy, current risk decision, exposures, aggregate Greeks, scenarios.
7. **Data & Broker Health** — provenance/freshness/auth/read/feed truth.
8. **Readiness / Proof** — semantic gates, E2E proof, Live Gate.
9. **Observability** — alerts, logs, errors, latency, deployment/runtime truth.
10. **Security / Settings** — sessions, policy versions, permissions, audit export, non-authoritative UI preferences.

## 10. Positive foundations to preserve

- shared design tokens and numeric styling;
- reduced-motion preference;
- semantic sidebar navigation/ARIA attributes;
- visible pending states in unfinished workspaces;
- scanner-vs-prediction distinction direction;
- wrong-symbol option-chain suppression;
- source/snapshot/stale messaging foundation;
- bid/ask <=0 rendered missing rather than fake;
- bounded-concurrency E2E probes;
- Live Gate approval does not automatically enable live trading;
- Paper Trading identifies local simulated fills rather than a Dhan paper sandbox;
- `PaperExecutor` already hard-stops new entries at configured `max_positions`, which should be retained as a local defense-in-depth check after canonical risk enforcement is added.

These are foundations, not readiness proof.

## 11. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is required audit posture, not a defect.

## 12. Closure standard

A finding becomes `CLOSED` only when applicable evidence is tied to the exact changed revision: source fix inspected; positive/negative tests; build/static/type checks; unit/integration/browser tests; runtime/deployment proof where required; no analyzer/live-off regression; screenshot/network/console proof for UI; frontend/backend schema reconciliation; no contradictory independent evidence.

## 13. Next audit / solution slices

1. **Paper backend route/storage owner mapping** — locate `/api/paper/tick`, persistence, fill model, mutation idempotency and exact insertion point for `PreTradeRiskService`.
2. **WebSocket/polling** — reconnect/backoff, heartbeat, stale retention, ordering, duplicate subscriptions, event timestamps.
3. **Option-chain backend normalization** — exact Dhan normalizer, IV/Greeks owner, timestamp/schema path.
4. **Observability / Cloud Run provenance** — source/runtime revision, image digest, latency/errors/browser failures/dependency truth.
5. **Responsive/accessibility** — desktop/tablet/mobile, keyboard/focus/live regions/dense-table behavior.

## 14. Hard safety rule

A green UI, successful build, endpoint HTTP 200, zero-valued risk/P&L, `PAPER SAFE`, human approval, absent risk-policy error or missing market data never substitutes for source, freshness, lifecycle, enforceable risk, reconciliation, expectancy and exact runtime proof. Live order placement/modification/cancellation/routing remains prohibited during this audit.