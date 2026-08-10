# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-10 23:50–00:05 IST`

## 0. Scope lock and evidence baseline

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `271939175e39842312ebba17d747713508fd2b9c`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after `b70af343...` observed in this loop are audit-document changes only; application conclusions remain tied to `b70af343...` unless a later application commit is explicitly named.
- Combined commit-status contexts for `271939175...` were empty in this iteration; this does not prove CI failure, but it also provides no same-revision application readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt, not an accepted target.
- Audit posture: ANALYZER/PAPER, live-money routing OFF. No audit action may enable/place/modify/cancel a live order.
- End-state objective: architecture and UI may eventually support safe real-money trading, but readiness may only be declared from reproducible same-revision evidence.
- This file remains the single continuously refined master audit Markdown. Duplicate findings are merged here rather than creating parallel audit summaries.

## 1. Executive verdict

| Area | Verdict | Evidence status |
|---|---|---|
| Current application HEAD CI proof | **NOT PROVEN** | No same-revision status contexts proving current application HEAD |
| Dashboard login HTTP contract | **FAIL / P0** | LoginPage omits required JSON `api_key` body |
| Pre-auth data polling | **FAIL / P1** | `useData()` executes before AuthGate establishes authentication |
| Browser API-key exposure | **FIX-REQUIRED / P1** | raw dashboard key stored in `sessionStorage` and reinjected into requests |
| Server-side session expiry | **PARTIAL / P1** | cookie Max-Age exists, but server token lacks independent issuance/expiry enforcement |
| Global UI mode truth | **FAIL / P0** | PAPER/LIVE-OFF states are hard-coded in global chrome rather than sourced from runtime safety authority |
| Global proof bar truth | **FAIL / P0-P1** | UI “LIVE” can be derived from broker connectivity; unrelated safety domains are conflated |
| UI truthfulness generally | **FAIL / P0-P1** | absence-as-success, unsafe fallback and semantic-overclaim patterns remain |
| Option Chain truth | **FAIL / P0-P1** | warming payload can synthesize PCR=1 while marking proof pending=false; Dhan verification is not timestamp/schema-proofed |
| Greeks UI | **INCOMPLETE / P1** | calculator supports Delta/Gamma/Theta/Vega/Rho, while current chain UI renders neither full Greeks nor a provenance/unit contract |
| Options Intelligence | **INCOMPLETE / P1** | source/freshness envelope missing; ranking mislabeled as forecast; Greeks workspace not proven complete |
| Prediction audit | **PENDING / REQUIRED** | production prediction ledger is explicitly not wired |
| Factor/scenario risk | **PENDING / REQUIRED** | factor-risk and scenario services explicitly pending |
| Responsive/mobile UI | **NOT PROVEN / P2** | fixed sidebar and no proven application-shell breakpoint behavior |
| Accessibility focus proof | **NOT PROVEN / P2** | reduced-motion exists; complete keyboard focus-visible behavior not proven |
| Dhan endpoint truth in UI | **INCORRECT / P1** | Data Integrity uses misleading `web.dhan.co` operational API label |
| Audit artifact freshness | **FAIL / P1** | generated trackers can diverge from current source and must not be treated as runtime truth |
| Cloud Run analyzer/live-off workflow flags | **PASS IN SOURCE ONLY** | deployment workflow keeps live flags disabled and analyzer mode enabled |
| Real-market paper lifecycle | **NOT PROVEN** | historical blocker remains open |
| Multi-day positive costed expectancy | **NOT PROVEN** | no same-revision reproducible proof |
| Real-money trade ready | **NO** | P0/P1 blockers plus missing runtime, lifecycle, risk, Greeks and expectancy proof |

## 2. Iteration delta — Option Chain + Greeks deep slice

### Newly verified this iteration

1. **CHAIN-001 / P0 — Cold/warming chain fabricates neutral PCR and marks proof as not pending.** In `dashboard/frontend/src/hooks/useData.ts`, the `CHAIN_CACHE_WARMING` / `NO_DHAN_DATA` branch creates `contracts: []`, `spot: 0`, `pcr: 1`, `stale: true`, `snapshot: true`, `live: false`, while setting `pendingProof: false`. A zero-row unproven chain therefore carries a valid-looking PCR value and a false “not pending” semantic.
2. **CHAIN-002 / P1 — `isRealDhanChainPayload()` proves only Dhan-looking metadata + positive spot/contracts, not complete provenance/freshness/schema truth.** The acceptance test rejects obvious fallback/synthetic strings and requires source/priority to look Dhan-like, `spot > 0`, and `contracts > 0`, but does not require authoritative event timestamp, received timestamp, age threshold, schema version, or per-field completeness. After acceptance, `verified_live_dhan` is set from snapshot/live flags rather than an explicit proof object.
3. **CHAIN-003 / P1 — Current Option Chain table does not expose the full Greeks required by the product target.** `OptionChain.tsx` contract typing carries `delta` and `theta`, but the visible table renders OI, ChgOI, volume, IV, LTP and bid/ask only. `gamma` and `vega` are absent from the local contract interface, and none of Delta/Gamma/Theta/Vega is displayed in the table.
4. **CHAIN-004 / P1 — The repository has a full Black-Scholes Greeks calculator, but chain-to-calculator provenance is not proven in this slice.** `src/metrics/greeks.py` calculates Delta, Gamma, Theta, Vega and Rho and can solve IV from market price. No evidence gathered in this iteration proves every displayed option-chain contract is normalized through this calculator (or through a broker-equivalent authoritative Greeks source) at a known version, risk-free-rate assumption and time-to-expiry convention.
5. **CHAIN-005 / P1 — IV unit semantics are implicit at the UI boundary.** `OptionChain.tsx` renders IV as `(iv * 100).toFixed(1) + '%'`, which assumes upstream IV is a decimal fraction. The current frontend contract does not carry an `iv_unit`, schema version or normalization provenance. A provider returning percentage points would be displayed 100x too large.
6. **Positive control:** wrong-symbol chain data are explicitly hidden when backend `underlying` does not match the selected symbol; bid/ask values <=0 are converted to no-value; stale/snapshot messaging is visibly surfaced. Preserve these behaviors while tightening proof semantics.

### Revalidated without counter inflation

- LoginPage/backend auth mismatch still reproduces on unchanged application source.
- `useData()` still runs before AuthGate establishes authenticated dashboard state.
- raw API key browser persistence still exists.
- global PAPER/LIVE-OFF state remains presentation-hard-coded.

## 3. Verification counters

A counter increases only when a materially independent evidence path reproduces the same conclusion. Reading the same unchanged artifact twice does not count.

| Finding | Conclusion | Counter | State |
|---|---|---:|---|
| AUTH-001 | LoginPage/backend session payload mismatch | `3/20` | OPEN |
| AUTH-002 | protected data hooks start before authentication | `2/20` | OPEN |
| AUTH-003 | raw dashboard key remains JS-accessible | `2/20` | OPEN |
| UI-001 | missing telemetry can be presented as success | `3/20` | OPEN — chain warming adds an independent absence-as-success path |
| UI-002 | gain-rank is mislabeled as validated forecast | `2/20` | OPEN |
| UI-003 | Dhan endpoint display is operationally misleading | `2/20` | OPEN |
| UI-004 | broker connectivity is conflated with secure dashboard session | `1/20` | OPEN |
| UI-005 | unsafe option-value fallback/default semantics | `2/20` | OPEN — independent PCR=1 warming fallback |
| UI-006 | empty positions are not distinguished from unproven response | `1/20` | OPEN |
| UI-007 | responsive navigation behavior is not proven | `2/20` | OPEN |
| UI-008 | explicit keyboard focus appearance is not proven | `2/20` | OPEN |
| UI-009 | authoritative PAPER/LIVE mode truth is missing | `3/20` | OPEN |
| UI-010 | immutable production prediction ledger is pending | `2/20` | OPEN |
| UI-011 | factor/scenario risk services are pending | `1/20` | OPEN |
| UI-016 | global UI/proof readiness is incorrectly derived from broker connection | `2/20` | OPEN |
| CHAIN-001 | warming chain fabricates PCR=1 / pendingProof=false | `1/20` | OPEN |
| CHAIN-002 | Dhan-looking payload lacks complete provenance envelope | `1/20` | OPEN |
| CHAIN-003 | full Greeks not exposed in Option Chain UI | `1/20` | OPEN |
| CHAIN-004 | chain-to-Greeks-calculator provenance not proven | `1/20` | OPEN |
| CHAIN-005 | IV units/schema contract not explicit | `1/20` | OPEN |

No finding has reached `LOCKED-20X`.

## 4. Critical authentication/security findings

### AUTH-001 — P0 — Login request does not satisfy backend contract

**Status:** FIX-REQUIRED.

Frontend `dashboard/frontend/src/components/LoginPage.tsx` POSTs `/api/auth/session` with headers and credentials but no JSON body. Backend requires a Pydantic payload containing `api_key`.

**Real-money impact:** operator lockout and auth noise during a trading incident are unacceptable.

**Target solution:** one typed auth client; send bootstrap API key exactly once in JSON body over HTTPS; establish HttpOnly cookie session; remove duplicated request construction.

**Closure proof:** browser integration: valid key -> 200 + authenticated cookie; invalid -> 401; missing body -> 422; refresh -> authenticated; no raw key logged.

### AUTH-002 — P1 — Protected polling begins before authentication

`App()` invokes `useData()` before AuthGate decides whether to show LoginPage.

**Target solution:** authenticated runtime child owns all protected subscriptions, or every protected hook receives fail-closed `enabled=authenticated`.

**Closure proof:** pre-login network capture shows zero protected broker/chain/paper requests; subscriptions start once only after successful auth.

### AUTH-003 — P1 — Raw API key stored in `sessionStorage`

**Target solution:** bootstrap credential must not remain in JS-accessible storage. Use HttpOnly/Secure/SameSite cookie plus scoped client; remove global raw-key reinjection.

### AUTH-004 — P1 — Session token lacks independent server expiry

**Target solution:** random opaque server-side session with TTL or signed expiring token with rotation/revocation.

## 5. Dashboard/UI truth findings

### UI-001 — P0 — Absence of telemetry/data can render as success or valid data

Independent patterns now include Decision Intelligence/Data Integrity “no blockers” behavior and chain warming `pcr: 1` with `pendingProof: false`.

**Required world-class rule:** operational values and conclusions need at least `PROVEN`, `FAIL`, `UNKNOWN/NO-PROOF`, `STALE`, `NOT_IMPLEMENTED`. Absence is never green and absence never receives a market statistic.

### UI-002 — P0/P1 — Scanner rank presented as forecast

Use `Scanner / Gain Rank` until immutable prediction records exist with model version, frozen cutoff, probability, uncertainty, calibration and realized after-cost outcome.

### UI-003 — P1 — Dhan endpoint label misleading

Show sanitized configured REST/feed hosts separately, derived from backend connection metadata rather than hard-coded `web.dhan.co`.

### UI-004 / UI-016 — P1/P0 — Broker truth overloaded into unrelated security/UI truth

Required separation:

- Dashboard authentication
- Dhan REST authentication
- Market-data feed
- Data freshness
- Account-read health
- Trading permission/order-router state
- Frontend revision
- Backend revision

No badge may infer another domain.

### UI-005 — P1 — Unsafe option/default semantics

Use nullish/schema-aware handling. `UNKNOWN/NO DATA` must replace neutral/directional conclusions fabricated from missing values.

### UI-006 — P1 — Empty positions need explicit proof state

Required states: `LOADING`, `AUTH_REQUIRED`, `API_ERROR`, `SCHEMA_ERROR`, `PROVEN_EMPTY`, `ROWS_PRESENT`, `STALE_LAST_GOOD`.

### UI-007 — P1 — Options analytics need shared DataTruthEnvelope

Required envelope:

```text
source
provider_session_id / source_instance
symbol / expiry
source_event_time
backend_received_time
frontend_received_time
age_ms
freshness_threshold_ms
market_state
live_or_snapshot
schema_version
normalizer_version
quality_state
last_good_provenance
```

Any missing critical field downgrades analytics to `UNKNOWN/NOT PROVEN`.

### UI-009 / UI-015 / UI-017 — P0 — Global mode safety hard-coded

Presentation code independently emits PAPER/LIVE-OFF rather than receiving one authoritative `SafetyTruth` object.

Required backend contract:

```text
mode: ANALYZER | PAPER | LIVE | UNKNOWN
live_trading_enabled: boolean | null
auto_execute_enabled: boolean | null
order_router_state: DISABLED | ARMED | ENABLED | UNKNOWN
kill_switch_state
source_revision
cloud_run_revision
verified_at
age_ms
policy_version
proof_status: PROVEN | STALE | UNKNOWN
```

Unavailable/stale truth => `UNKNOWN — DO NOT TRADE`, never static green.

### UI-010 — P1 — Prediction ledger pending

Required append-only prediction ID, contract, horizon, model hash/version, frozen cutoff, probability, uncertainty, evidence/counter-evidence, realized outcome, cost/slippage, calibration bucket and integrity chain.

### UI-011 — P1 — Factor/scenario risk pending

Before live-money assessment, prove net/gross exposure, concentration, expiry buckets, aggregate Greeks, stress scenarios, margin utilization, drawdown headroom and enforceable pre-trade limits.

### UI-012 — P2 — Navigation task-fragmented

Target product IA should consolidate current tabs into 8–10 operator workspaces without deleting capability:

1. Command Center
2. Market / Scanner
3. Options & Greeks
4. AI Decision Audit
5. Paper / Trade Lifecycle
6. Portfolio & Risk
7. Data & Broker Health
8. Readiness / Proof
9. Observability
10. Security / Settings

### UI-013 — P2 — Responsive/mobile not proven

Desktop is primary. Tablet gets collapsible rail. Mobile begins as high-priority read-only operational view; mobile live-order entry remains OPTIONAL until desktop truth and safety are proven.

### UI-014 — P2 — Keyboard focus proof not complete

Required: consistent `:focus-visible`, logical tab order, skip-to-content, grid/table keyboard strategy, aria-live for critical transitions and non-color-only states.

### UI-018 — P1 — “CLOUD BUILD” green does not prove deployment compatibility

Required provenance badge: frontend commit, backend commit, Cloud Run revision, image digest, build/deploy/health times, compatibility/schema version and freshness.

### UI-019 — P1 — Broker good state can come from response existence

Required broker state machine: `UNKNOWN`, `AUTH_REQUIRED`, `AUTHENTICATED_READ_OK`, `FEED_OK`, `DEGRADED`, `STALE`, `API_ERROR`, `SCHEMA_ERROR`. Trading permission remains separate.

## 6. Option Chain + Greeks findings and target

### CHAIN-001 — P0 — Warming state carries fabricated PCR=1

**Current behavior:** `useData.ts` creates a warming object with no contracts/spot, yet `pcr: 1` and `pendingProof: false`.

**Root cause:** placeholder object mixes transport/cache state with analytical values.

**Real-money impact:** downstream panels can interpret neutral PCR as genuine market structure or infer proof completion from `pendingProof=false`.

**Required fix:** use `pcr: null`; `pendingProof: true`; `quality_state: NO_DATA`; analytics disabled until a proven chain exists. Preserve last-good data only with explicit stale provenance and original source timestamp.

**Closure proof:** unit tests for cold cache, market closed, 429/5xx, auth failure and no-contract response; no analytic field becomes numeric unless source rows exist.

### CHAIN-002 — P1 — Dhan verification needs proof envelope, not string heuristics

**Current behavior:** payload is considered real Dhan if source/priority text looks Dhan-like and spot/contracts are positive, with some fallback rejection.

**Required fix:** backend emits immutable chain provenance containing provider, request/stream ID, event/received timestamps, market state, schema/normalizer version, row count, required-field completeness and freshness evaluation. Frontend consumes backend `proof_status`; it does not mint `verified_live_dhan` from heuristics.

**Closure proof:** replay tests with Dhan-looking stale payload, wrong timestamp, incomplete schema, wrong underlying and malformed rows; all fail closed.

### CHAIN-003 — P1 — Full Greeks missing from current chain screen

**Current behavior:** visible table omits Delta/Gamma/Theta/Vega. Local contract interface lacks Gamma/Vega even though repository calculator can compute them.

**Required product behavior:** optional compact columns or expandable strike rows for Delta/Gamma/Theta/Vega, plus position overlay and aggregate portfolio Greeks. Operators must be able to switch dense/expanded modes.

**Closure proof:** schema contract tests + screenshot/browser tests across CE/PE, ATM/ITM/OTM, zero/missing Greeks, stale chain, and position overlays.

### CHAIN-004 — P1 — Greeks provenance/assumptions not proven end-to-end

`src/metrics/greeks.py` supports Black-Scholes Delta/Gamma/Theta/Vega/Rho and IV solving from market price. The UI requires explicit metadata per Greeks snapshot:

- calculation/provider source
- calculator/model version
- risk-free rate and source/time
- time-to-expiry convention and exchange timezone
- IV source/solver/version
- underlying/spot source and event time
- calculation timestamp
- stale threshold

**Closure proof:** contract sample from backend -> normalized chain -> UI row, with known-value tests against independent reference cases.

### CHAIN-005 — P1 — IV unit contract implicit

**Current behavior:** frontend assumes decimal IV and multiplies by 100.

**Required fix:** canonical API schema: `iv_decimal` (0.20) or explicit `iv_value` + `iv_unit`. Do not use ambiguous `iv` across providers.

**Closure proof:** schema tests for 0, null, 0.2, 20, extreme values and provider normalization.

## 7. Positive foundations to preserve

- shared design tokens and tabular numeric styling;
- reduced-motion preference;
- semantic sidebar navigation/ARIA attributes;
- visible pending states in several unfinished workspaces;
- Prediction Audit correctly distinguishes scanner rank from validated forecast proof;
- wrong-symbol option chain is hidden rather than shown;
- chain status/source/snapshot messaging exists;
- bid/ask <=0 becomes missing rather than fake price;
- analyzer/live-off intent is highly visible;
- TopBar attempts to surface market, broker, websocket and tick-age context.

These are foundations only, not readiness proof.

## 8. World-class institutional target UI — baseline V3

### 8.1 Always-visible truth strip — REQUIRED

Every screen shows source-backed:

- operational mode
- order-router permission
- dashboard auth
- Dhan REST auth
- feed connection
- market session
- last source event + received time + age
- frontend/backend commits
- Cloud Run revision/image digest
- risk gate
- reconciliation state
- critical incident count

States: `PROVEN`, `DEGRADED`, `FAIL`, `STALE`, `UNKNOWN`, `NOT_IMPLEMENTED`.

### 8.2 Command Center — REQUIRED

Answers immediately: safe now? authoritative/fresh data? top scanner candidates? validated predictions vs ranks? paper positions? risk headroom? exact live gate blocker? what changed recently?

### 8.3 Market / Scanner — REQUIRED

Watchlists, saved views, source/freshness beside every quote, rule/model version, filters, search, symbol drilldown, clear scanner-vs-prediction separation.

### 8.4 Options & Greeks — REQUIRED

- underlying and expiry selector
- strike ladder
- bid/ask/LTP/spread/depth
- volume/OI/OI change
- IV with explicit units/provenance
- Delta/Gamma/Theta/Vega per contract
- aggregate portfolio Greeks
- PCR/IV percentile only when validated
- ATM/ITM/OTM hierarchy
- source/freshness/live-vs-snapshot
- position overlay
- scenario P&L / Greek shocks
- schema/quality warnings
- last-good stale watermark rather than silent retention

### 8.5 AI Decision Audit — REQUIRED before AI-driven live money

Scanner-vs-prediction distinction, probability + uncertainty, evidence/counter-evidence, model hash/version, frozen cutoff, calibration, ledger ID, realized after-cost outcome, drift and feature quality.

### 8.6 Paper / Trade Lifecycle — REQUIRED

Intent -> validation -> risk -> paper order -> fill simulation -> position -> exit -> realized P&L -> reconciliation, with correlation IDs and timestamps through every stage.

### 8.7 Portfolio & Risk — REQUIRED

Funds/margin, realized/unrealized P&L, broker-stamped positions, concentration, expiry exposure, aggregate Greeks, daily loss/drawdown headroom, stress scenarios, reconciliation, enforceable limits and authoritative kill-switch state.

### 8.8 Data & Broker Health — REQUIRED

Dhan REST/feed health, per-stream event age, schema/normalization health, rate limits, last successful funds/positions/holdings, fallback provenance.

### 8.9 Readiness / Proof — REQUIRED

Every gate links to evidence, revision and timestamp. Gate states: `PASS`, `FAIL`, `BLOCKED`, `STALE`, `UNKNOWN`, `NOT_RUN`.

### 8.10 Observability — REQUIRED

API SLI/SLO, broker-read ratio, feed freshness, p50/p95/p99 latency, WS reconnects, event-loop lag, memory/CPU, Cloud Run provenance, incident timeline, error budget, browser errors and failed API calls.

### 8.11 Security / Settings — REQUIRED

Session age/expiry, auth method, role/permission model when multi-user, audit-log export, read-only safety configuration, no secret values in browser storage.

## 9. Feature priority matrix

### REQUIRED before live-money readiness can be assessed

- correct auth/session contract
- no raw API key in browser storage
- authoritative safety/mode contract
- no absence-as-success states
- Dhan REST/feed truth + freshness
- chain DataTruthEnvelope
- validated full Greeks + units/provenance
- proven funds/positions/margin
- end-to-end paper lifecycle/reconciliation
- portfolio/factor/scenario risk
- enforceable pre-trade gates
- immutable prediction ledger for AI decisions
- deployment/source provenance
- latency/freshness observability
- incident/error visibility
- responsive operator-safe layout
- keyboard/accessibility baseline

### RECOMMENDED

- consolidated task-based navigation
- multi-monitor presets
- saved watchlists/workspaces
- linked underlying/options views
- advanced chart annotations
- configurable density
- incident timeline/custom alerts

### OPTIONAL until core truth is proven

- social/news sentiment enrichment
- cosmetic theme breadth
- large drawing-tool ecosystem
- extensive multi-chart mosaics
- mobile live-order entry

## 10. Google Cloud / deployment findings retained

- Google Cloud Run is target deployment authority.
- root `render.yaml` is absent.
- residual Render-era terminology remains migration debt.
- Cloud Run workflow source keeps live trading disabled and analyzer mode enabled.
- production runtime proof still requires exact frontend/backend commit, Cloud Run revision, image digest, authenticated health, Dhan status, required chains, funds/positions/holdings, browser proof and safety flags.

## 11. Historical open real-money gates

Carry forward until same-revision evidence closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is required audit posture, not a defect.

## 12. Closure standard for every finding

A finding becomes `CLOSED` only when applicable evidence is tied to the exact changed revision:

1. source/config fix inspected;
2. positive and negative tests added;
3. build/compile/type/static checks pass;
4. unit/integration/browser tests pass;
5. deployment proof exists for runtime-dependent findings;
6. analyzer/live-off safety has no regression;
7. stale trackers regenerated;
8. browser screenshot/network/console proof exists for UI findings;
9. frontend/backend schema fields reconcile;
10. no contradictory independent evidence remains.

## 13. Next audit slices

1. **System Truth / E2E Proof / LiveTradingGate** — locate additional false-green or duplicated safety semantics.
2. **Paper Trading + Trade + Positions** — lifecycle transitions, reconciliation, P&L truth, zero-vs-error semantics.
3. **Risk + auto-gates** — determine displayed limits vs genuinely enforced pre-route gates.
4. **WebSocket/polling** — stale retention, reconnect/backoff, out-of-order events, heartbeat and timestamp semantics.
5. **Observability/Cloud Run provenance** — revision, image, latency, runtime health and browser errors.
6. **Responsive/accessibility matrix** — desktop/tablet/mobile, keyboard, focus and status announcements.
7. **Option-chain backend normalization follow-through** — prove exact source of Greeks/IV fields, timestamps and normalizer versions rather than inferring from frontend shape.

## 14. Visual-design iteration rule

Each audit iteration improves or rotates the target PRODUCT UI visual. It must never be an audit-progress dashboard. Unproven values are labeled `CONCEPT`, `TARGET`, `PENDING`, `UNKNOWN` or `NOT PROVEN`. No fabricated P&L, profitability, broker-ready, trade-ready or PASS metrics.

## 15. Hard safety rule

UI quality, green badges, successful builds or attractive design never substitute for broker/data/risk/runtime proof. Any future live-order capability must be separately designed, independently audited, staged and proven before activation. During this audit, live order placement/modification/cancellation/routing remains prohibited.
