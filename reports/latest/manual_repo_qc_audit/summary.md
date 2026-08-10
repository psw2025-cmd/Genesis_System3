# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-10 22:49–23:05 IST`

## 0. Scope lock and evidence baseline

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed before this report update: `9eb6d150fa4ed35b8b6ac3164f9283a7fcf4aad9`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- `9eb6d150...` is an audit-document-only change; application conclusions remain tied to `b70af343...` unless a later application commit is named.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt, not an accepted target.
- Audit safety posture: ANALYZER/PAPER, live-money routing OFF. No audit action may enable/place/modify/cancel a live order.
- End-state objective: architecture and UI must eventually be capable of safe real-money trading, but readiness may only be declared from reproducible, same-revision evidence.
- This is the single continuously refined master audit Markdown. Duplicate findings are merged here rather than creating parallel audit summaries.

## 1. Executive verdict

| Area | Verdict | Evidence status |
|---|---|---|
| Current application HEAD CI proof | **NOT PROVEN** | No combined status contexts returned for current application HEAD |
| Dashboard login HTTP contract | **FAIL / P0** | LoginPage omits required JSON `api_key` body |
| Pre-auth data polling | **FAIL / P1** | `useData()` executes before AuthGate establishes authentication |
| Browser API-key exposure | **FIX-REQUIRED / P1** | raw dashboard key stored in `sessionStorage` and reinjected into requests |
| Server-side session expiry | **PARTIAL / P1** | cookie Max-Age exists, but server token lacks independent issuance/expiry enforcement |
| Global UI mode truth | **FAIL / P0** | PAPER/LIVE-OFF states are hard-coded in global chrome rather than sourced from runtime safety authority |
| Global proof bar truth | **FAIL / P0-P1** | UI “LIVE” can be derived from broker connectivity; proof labels conflate different safety domains |
| UI truthfulness generally | **FAIL / P0-P1** | multiple absence-as-success, unsafe fallback and semantic-overclaim patterns remain |
| Options Intelligence | **INCOMPLETE / P1** | source/freshness envelope missing; ranking mislabeled as forecast; Greeks workspace not proven complete |
| Prediction audit | **PENDING / REQUIRED** | production prediction ledger is explicitly not wired |
| Factor/scenario risk | **PENDING / REQUIRED** | factor-risk and scenario services explicitly pending |
| Responsive/mobile UI | **NOT PROVEN / P2** | fixed sidebar and no proven application-shell breakpoint behavior |
| Accessibility focus proof | **NOT PROVEN / P2** | reduced-motion exists; complete keyboard focus-visible behavior not proven |
| Dhan endpoint truth in UI | **INCORRECT / P1** | Data Integrity uses misleading `web.dhan.co` operational API label |
| Audit artifact freshness | **FAIL / P1** | historical/generated trackers can diverge from current source and must not be treated as runtime truth |
| Cloud Run analyzer/live-off workflow flags | **PASS IN SOURCE ONLY** | deployment workflow keeps live flags disabled and analyzer mode enabled |
| Real-market paper lifecycle | **NOT PROVEN** | historical blocker remains open |
| Multi-day positive costed expectancy | **NOT PROVEN** | no same-revision reproducible proof |
| Real-money trade ready | **NO** | P0/P1 blockers plus missing runtime, lifecycle, risk and expectancy proof |

## 2. Iteration delta — newest refinements

### Newly verified this iteration

1. **UI-015 / P0 — ProductionProofBar hard-codes safety state.** `dashboard/frontend/src/App.tsx` constructs `['LIVE','OFF',true]` and `['MODE','PAPER',true]`; both are permanently rendered as safe/green regardless of runtime configuration.
2. **UI-016 / P0-P1 — Proof-bar UI readiness is conflated with broker connectivity.** `cloudUiOk = Boolean(brokerConnected || health?.broker_status === 'connected')`, then `UI` becomes `LIVE` and green. Broker connectivity does not prove frontend deployment integrity, browser health, UI revision provenance, authenticated session quality, data freshness, or trade-safety state.
3. **UI-017 / P1 — TopBar independently hard-codes `PAPER` and `LIVE OFF`.** This confirms global mode truth is duplicated across presentation components rather than coming from one authoritative safety contract.
4. **UI-018 / P1 — Cloud build badge can imply healthy/proven deployment from existence of a build epoch only.** `CloudBuildBadge` turns green whenever `build_epoch` exists; it does not verify commit SHA, Cloud Run revision, image digest, age/freshness, backend compatibility or same-revision health.
5. **UI-019 / P1 — Broker badge can become green from “API responded” rather than a fully proven connected/authenticated state.** In `TopBar`, `brokerGood = brokerConnected || (brokerApiResponded && !brokerHasError)`. A non-error response is useful evidence but is not equivalent to authenticated broker readiness, feed health or trading permission.
6. **Repository/document freshness:** newest repository commit before this update was `9eb6d150...`; current application code remains `b70af343...`. CI status contexts for the audit-only head are empty and therefore do not provide application readiness proof.

### Revalidated without counter inflation

The following still reproduce, but rereading unchanged evidence is not counted as an independent verification:

- LoginPage still omits the required JSON body and persists the raw API key in browser storage.
- `App()` still calls `useData()` before AuthGate returns authenticated content.
- current application HEAD remains later than the last historically proven PR checkpoint.

## 3. Verification counters

A counter increases only when a materially independent evidence path reproduces the same conclusion. Reading the same unchanged artifact twice does not count.

| Finding | Conclusion | Counter | State |
|---|---|---:|---|
| AUTH-001 | LoginPage/backend session payload mismatch | `3/20` | OPEN |
| AUTH-002 | protected data hooks start before authentication | `2/20` | OPEN |
| AUTH-003 | raw dashboard key remains JS-accessible | `2/20` | OPEN |
| UI-001 | missing telemetry can be presented as “no blockers” | `2/20` | OPEN |
| UI-002 | gain-rank is mislabeled as validated forecast | `2/20` | OPEN |
| UI-003 | Dhan endpoint display is operationally misleading | `2/20` | OPEN |
| UI-004 | broker connectivity is conflated with secure dashboard session | `1/20` | OPEN |
| UI-005 | unsafe option-value fallback/default semantics | `1/20` | OPEN |
| UI-006 | empty positions are not distinguished from unproven response | `1/20` | OPEN |
| UI-007 | responsive navigation behavior is not proven | `2/20` | OPEN |
| UI-008 | explicit keyboard focus appearance is not proven | `2/20` | OPEN |
| UI-009 | authoritative PAPER/LIVE mode truth is missing | `3/20` | OPEN — independently reproduced in DecisionIntelligence, ProductionProofBar and TopBar |
| UI-010 | immutable production prediction ledger is pending | `2/20` | OPEN |
| UI-011 | factor/scenario risk services are pending | `1/20` | OPEN |
| UI-016 | global UI/proof readiness is incorrectly derived from broker connection | `2/20` | OPEN — Data Integrity + ProductionProofBar |

No finding has reached `LOCKED-20X`.

## 4. Critical authentication/security findings

### AUTH-001 — P0 — Login request does not satisfy backend contract

**Status:** FIX-REQUIRED.

Frontend `dashboard/frontend/src/components/LoginPage.tsx` POSTs `/api/auth/session` with headers and credentials but no JSON body. Backend `dashboard/backend/app.py` requires a Pydantic payload containing `api_key`.

**Why it matters:** operator lockout and auth-noise during a real-money incident are unacceptable.

**World-class solution:** one typed authentication client; send the bootstrap API key exactly once in the JSON body over HTTPS; establish an HttpOnly cookie session; remove duplicated request-construction paths.

**Closure proof:** browser integration test: valid key -> 200 + authenticated cookie; invalid -> 401; missing body -> 422; refresh -> authenticated; no raw key logged.

### AUTH-002 — P1 — Protected polling begins before authentication

`App()` invokes `useData()` before the AuthGate decides whether to show LoginPage.

**World-class solution:** authenticated runtime child (`<DashboardRuntime/>`) owns all protected subscriptions, or every protected data hook receives a fail-closed `enabled=authenticated` control.

**Closure proof:** browser network capture before login shows zero protected broker/chain/paper requests; subscriptions start once only after successful auth.

### AUTH-003 — P1 — Raw API key stored in `sessionStorage`

LoginPage stores `s3_api_key`; auth utilities read and reinject it into requests.

**World-class solution:** bootstrap credential is not persisted in JS-accessible storage. Use HttpOnly/Secure/SameSite cookie plus a scoped API client; avoid global `window.fetch` monkey-patching.

**Closure proof:** browser storage contains no raw key; protected requests work through session cookie; CSP/XSS checks; logout invalidates session.

### AUTH-004 — P1 — Session token lacks independent server expiry

Server token equality is deterministic from the API key and does not itself encode/check issue time or expiry.

**World-class solution:** random opaque server-side session with TTL or signed expiring token with rotation/revocation.

**Closure proof:** replay after server TTL returns 401; key/session rotation invalidates old sessions.

## 5. Dashboard/UI truth findings

### UI-001 — P0 — Absence of blocker/error telemetry can render as success

`DecisionIntelligence` and `DataIntegrity` contain conditional branches where missing arrays can collapse into “NO ... BLOCKERS”.

**World-class rule:** every operational state is three-valued or richer: `PASS`, `FAIL`, `UNKNOWN/NO-PROOF`, plus `STALE` when applicable. Absence is never green.

### UI-002 — P0/P1 — Scanner rank is presented as “Top Forecasts”

`OptionsIntelligence` labels gain-rank rows as forecasts while `PredictionAudit` explicitly says gain-rank is not a validated forecast.

**Fix:** call it `Scanner / Gain Rank` until immutable prediction records exist with model version, data cutoff, probability/confidence, uncertainty, calibration and realized outcome.

### UI-003 — P1 — Dhan endpoint label is misleading

Data Integrity hard-codes `web.dhan.co` as API endpoint. Runtime operator health should instead show sanitized configured REST/feed hosts separately and derive them from backend connection metadata.

### UI-004 / UI-016 — P1/P0 — Broker truth is overloaded into unrelated security/UI truth

Current UI uses broker connectivity to support phrases such as secure session or UI-live/proven state.

**Required split:**

- Dashboard authentication
- Dhan REST authentication
- Market-data feed
- Data freshness
- Broker account read health
- Trading permission/order-router state
- Frontend revision/provenance
- Backend revision/provenance

No badge may infer another domain.

### UI-005 — P1 — Freshness can become green from truthiness rather than threshold

Age/freshness fields need normalized units and explicit market-state-aware thresholds.

**Required display:** source event time, received time, age, allowed threshold, market open/closed, live/snapshot, clock-skew state.

### UI-006 — P1 — Unsafe numeric fallbacks can alter meaning

Examples retained from audit: `pcr_oi || '—'`, `pcr_vol || '—'`, falsy IV percentile, and missing OI change becoming `STABLE`.

**Fix:** schema validation + nullish handling; missing data renders `UNKNOWN/NO DATA`, never a directional market conclusion.

### UI-007 — P1 — Options analytics are not gated by a shared data-truth envelope

A valid-looking chain object can render analytics without locally requiring authoritative source/freshness/schema quality.

**Required `DataTruthEnvelope`:** source, symbol, event timestamp, received timestamp, age, live/snapshot, market state, schema version, quality state and last-good provenance.

### UI-008 — P1 — Empty positions can be confused with proven zero positions

Required states: `LOADING`, `AUTH_REQUIRED`, `API_ERROR`, `SCHEMA_ERROR`, `PROVEN_EMPTY`, `ROWS_PRESENT`, `STALE_LAST_GOOD`.

### UI-009 / UI-015 / UI-017 — P0 — Global mode safety is hard-coded in three presentation surfaces

Independent code paths currently present PAPER/LIVE-OFF as static truth:

1. Decision Intelligence
2. ProductionProofBar
3. TopBar

ProductionProofBar additionally marks the two static values as safe/green (`true`).

**Real-money impact:** if configuration or routing state ever drifts, the dashboard can keep showing “LIVE OFF” while actual runtime permission differs. This is a catastrophic operator-trust failure mode.

**World-class solution — authoritative `SafetyTruth` backend contract:**

```text
mode: ANALYZER | PAPER | LIVE | UNKNOWN
live_trading_enabled: boolean | null
auto_execute_enabled: boolean | null
order_router_state: DISABLED | ARMED | ENABLED | UNKNOWN
kill_switch_state: ...
source_revision: commit SHA
cloud_run_revision: revision
verified_at: RFC3339
age_ms: integer
policy_version: string
proof_status: PROVEN | STALE | UNKNOWN
```

Frontend must fail closed: unavailable/stale safety truth => `UNKNOWN — DO NOT TRADE`, never static green.

### UI-010 — P1 — Prediction ledger is an explicit required placeholder

This is acceptable as transparent unfinished functionality but blocks AI-driven live-money readiness.

**Required ledger:** append-only prediction ID, symbol/contract, horizon, model/version/hash, frozen input cutoff, probability, uncertainty, evidence/counter-evidence, decision, realized outcome, costs/slippage, calibration bucket and integrity chain/hash.

### UI-011 — P1 — Factor/scenario risk is explicitly pending

Before any live-money assessment, portfolio view must prove net/gross exposure, concentration, expiry buckets, aggregate Greeks, stress/gap scenarios, margin utilization, drawdown headroom and enforceable pre-trade limits.

### UI-012 — P2 — Navigation is task-fragmented

Current sidebar exposes roughly twenty-plus destinations with overlapping truth/system/market workflows.

**Target primary IA (8–10 workspaces):**

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

Capabilities should be consolidated, not deleted.

### UI-013 — P2 — Responsive/mobile behavior not proven

Desktop workstation is primary. Tablet gets collapsible rail. Mobile should initially be high-priority read-only operational view; mobile live order entry is OPTIONAL and should not be introduced before desktop truth/safety is fully proven.

### UI-014 — P2 — Keyboard focus appearance not proven

Required: consistent `:focus-visible`, logical tab order, skip-to-content, table/grid keyboard strategy, aria-live for critical status updates, high-contrast non-color-only status indicators.

### UI-018 — P1 — “CLOUD BUILD” green does not prove deployment compatibility

`CloudBuildBadge` becomes green when a build epoch exists.

**World-class provenance badge must prove together:** frontend commit, backend commit, Cloud Run revision, image digest, build time, deploy time, health-check time, compatibility/schema version and freshness. Any mismatch is amber/red/unknown, not green.

### UI-019 — P1 — Broker “good” state can come from response existence

`TopBar` considers broker good when any broker API object has responded and no obvious error string is detected.

**World-class broker state machine:** `UNKNOWN`, `AUTH_REQUIRED`, `AUTHENTICATED_READ_OK`, `FEED_OK`, `DEGRADED`, `STALE`, `API_ERROR`, `SCHEMA_ERROR`. Trading permission remains a separate field.

## 6. Positive UI foundations to preserve

- shared design tokens and tabular numeric behavior exist;
- reduced-motion preference is respected;
- sidebar uses semantic navigation/ARIA attributes;
- several unfinished workspaces explicitly show pending state instead of fabricating results;
- Prediction Audit correctly warns that scanner gain-rank is not validated prediction proof;
- analyzer/live-off intent is highly visible;
- TopBar does attempt to expose market, broker, websocket and tick-age context.

These are foundations only, not readiness proof.

## 7. World-class institutional target UI — design baseline V2

### 7.1 Always-visible authoritative truth strip — REQUIRED

Every screen must show compact, source-backed status for:

- operational mode
- order-router permission
- dashboard auth
- Dhan REST auth
- market-feed connection
- market open/closed
- source + last event timestamp + age
- frontend commit
- backend commit
- Cloud Run revision/image digest
- risk gate
- reconciliation state
- critical incident count

The visual language must distinguish `PROVEN`, `DEGRADED`, `FAIL`, `STALE`, `UNKNOWN`, and `NOT IMPLEMENTED`.

### 7.2 Command Center — REQUIRED

One screen must answer:

- Is the system safe to use now?
- Is data authoritative, fresh and Dhan-sourced?
- Which scanner candidates exist and what evidence supports them?
- Which outputs are validated predictions vs rankings only?
- What paper positions exist?
- What portfolio/risk headroom exists?
- Which exact gate prevents real-money activation?
- What changed in the last session/hour?

### 7.3 Market / Scanner — REQUIRED

- watchlists and saved views
- source/freshness next to every quote
- ranker/scanner origin and rule/model version
- filtering/sorting/search
- market-leader comparison separated from model predictions
- symbol drilldown
- explicit stale/snapshot behavior

### 7.4 Options & Greeks — REQUIRED

- expiry selector and strike ladder
- bid/ask/LTP/spread/volume/OI/OI change/IV
- Delta/Gamma/Theta/Vega per contract
- portfolio aggregate Greeks
- PCR/IV percentile only when validated
- ATM/ITM/OTM visual hierarchy
- chain source/freshness/live-vs-snapshot
- position overlay
- scenario P&L and Greek shifts
- schema/quality warning when contract data are incomplete

### 7.5 AI Decision Audit — REQUIRED before AI-driven live money

- scanner candidate versus validated prediction distinction
- probability/confidence + uncertainty
- evidence and counter-evidence
- model version/hash
- frozen data cutoff
- calibration metrics
- immutable ledger ID
- realized outcome and after-cost result
- model drift and feature-quality state

### 7.6 Paper / Trade Lifecycle — REQUIRED

- intent -> validation -> risk decision -> paper order -> fill simulation -> position -> exit -> realized P&L -> reconciliation
- timestamps and correlation IDs through every stage
- rejected/failed transitions visible
- no “zero trades” success state unless the lifecycle API is proven healthy

### 7.7 Portfolio & Risk — REQUIRED

- funds/margin
- realized/unrealized P&L
- positions with broker timestamp/source
- concentration and expiry exposure
- aggregate Greeks
- daily loss/drawdown headroom
- stress scenarios
- reconciliation status
- risk-limit headroom
- kill-switch status displayed from authority, not as a cosmetic control

### 7.8 Data & Broker Health — REQUIRED

- Dhan REST host/auth/read health
- Dhan feed host/connection/reconnect state
- per-stream last event time and latency
- schema/normalization health
- rate-limit state
- last successful funds/positions/holdings read
- source provenance and fallback status

### 7.9 Readiness / Proof — REQUIRED

Every gate links to evidence, revision and timestamp. No generic green check without proof object. Gate states: `PASS`, `FAIL`, `BLOCKED`, `STALE`, `UNKNOWN`, `NOT RUN`.

### 7.10 Observability — REQUIRED

- API availability SLI/SLO
- broker-read success ratio
- market-feed freshness SLI
- p50/p95/p99 endpoint latency
- websocket reconnect/disconnect counts
- worker/event-loop lag
- memory/CPU
- Cloud Run revision/image/commit provenance
- incident timeline and error-budget burn
- frontend browser errors and failed API calls

### 7.11 Security / Settings — REQUIRED

- session age/expiry
- auth method and security posture without exposing secrets
- role/permission model when multi-user is introduced
- audit-log export
- safety configuration shown read-only unless separately authorized
- no secret values in browser storage or UI

## 8. Feature priority matrix

### REQUIRED before live-money readiness can be assessed

- correct auth/session contract
- no browser-persisted raw API key
- authoritative runtime safety/mode contract
- no absence-as-success states
- Dhan REST/feed truth and freshness
- validated option-chain + Greeks
- proven funds/positions/margin
- end-to-end paper lifecycle and reconciliation
- portfolio/factor/scenario risk
- enforceable pre-trade risk gates
- immutable prediction ledger for AI-driven decisions
- deployment/source provenance
- latency/freshness observability
- incident/error visibility
- responsive operator-safe layout
- keyboard/accessibility baseline

### RECOMMENDED

- task-based consolidated navigation
- multi-monitor layout presets
- saved watchlists/workspaces
- linked underlying/options views
- advanced chart annotations
- configurable density
- incident timeline and custom alerts

### OPTIONAL until core safety/truth is proven

- social/news sentiment enrichment
- cosmetic theme breadth
- large drawing-tool ecosystem
- extensive multi-chart mosaics
- mobile live order entry

Optional breadth must never delay core truth, risk, lifecycle or security work.

## 9. Historical proof retained with strict scope

Earlier V5 validation recorded successful builds/tests and security/deployment checks at specific historical revisions. PR #93/#95/#96 checkpoints also had green workflows at their respective heads. These are valuable regression references only; they do not prove application HEAD `b70af343...` because later code changed and current same-revision CI/runtime proof is incomplete.

## 10. Google Cloud / deployment findings retained

- Google Cloud Run is the target deployment authority.
- root `render.yaml` is absent.
- residual Render-era terminology remains migration debt.
- Cloud Run workflow source keeps live trading disabled and analyzer mode enabled.
- a production runtime claim still requires exact-revision proof: frontend/backend commit, Cloud Run revision, image digest, authenticated health, Dhan status, required chains, funds/positions/holdings, browser proof and all safety flags.

## 11. Historical open real-money gates

Carry forward until same-revision evidence closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is the required safety posture during this audit, not a defect.

## 12. Closure standard for every finding

A finding may be marked `CLOSED` only when all applicable evidence is tied to the exact changed revision:

1. source/config fix inspected;
2. positive and negative tests added;
3. build/compile/type/static checks pass;
4. unit/integration/browser tests pass;
5. deployment proof exists for runtime-dependent findings;
6. analyzer/live-off safety has no regression;
7. stale trackers regenerated;
8. browser screenshot/network/console proof exists for UI findings;
9. frontend/backend contract fields reconcile;
10. no contradictory independent evidence remains.

## 13. Next audit slices

1. **Option Chain + Greeks end-to-end field truth** — frontend table, backend routes, Dhan normalization, calculator provenance, units and stale handling.
2. **System Truth / End-to-End Proof / LiveTradingGate** — locate additional global false-green or duplicated safety semantics.
3. **Paper Trading + Trade + Positions** — lifecycle transitions, reconciliation, P&L truth, zero-vs-error semantics.
4. **Risk + auto-gates** — determine which displayed limits are actually enforced before an order route.
5. **WebSocket/polling** — reconnect, backoff, stale cache, out-of-order data, heartbeat and event timestamp semantics.
6. **Observability/Cloud Run provenance** — source revision, SLO, logs, latency, runtime health.
7. **Responsive/accessibility browser matrix** — desktop/tablet/mobile, keyboard, focus and status announcement proof.

## 14. Visual-design iteration rule

Each subsequent audit iteration should improve or rotate the target UI visual without pretending conceptual elements are implemented. Every unproven value in design concepts must be marked `CONCEPT`, `TARGET`, `PENDING`, `UNKNOWN` or `NOT PROVEN`. No fabricated P&L, profitability, broker-ready, trade-ready or PASS metrics are permitted.

## 15. Hard safety rule

UI quality, green badges, successful builds or attractive design can never substitute for broker/data/risk/runtime proof. Any future live-order capability must be separately designed, independently audited, staged and proven before activation. During this audit, live order placement/modification/cancellation/routing remains prohibited.
