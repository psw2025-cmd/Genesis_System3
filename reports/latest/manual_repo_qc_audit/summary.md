# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-10 22:39 IST`

## 0. Scope lock and evidence baseline

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Latest repository HEAD observed this iteration: `b6ce4a1654deea38a8f767d7c9fbaaa2f12789e4`.
- Latest application/source HEAD: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- `b6ce4a...` changes this audit report only; application conclusions below are tied to `b70af343...` unless a later application commit is named.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt, not a target.
- Safety posture during audit: ANALYZER/PAPER, live-money routing OFF. No audit step may enable/place/modify/cancel a live order.
- End-state objective: architecture and UI must be capable of safe real-money trading, but readiness may only be declared from same-revision reproducible proof.
- This is the single master audit Markdown. Findings are refined/merged here instead of spawning parallel summary files.

## 1. Current executive verdict

| Area | Verdict | Evidence status |
|---|---|---|
| Current application HEAD CI proof | **NOT PROVEN** | No combined status contexts returned for `b70af343...`; PR #96 green CI is an earlier checkpoint |
| Dashboard login HTTP contract | **FAIL / P0** | Frontend omits required JSON body |
| Pre-auth data polling | **FAIL / P1** | `useData()` executes outside/above the auth decision |
| Browser API-key exposure | **NEEDS HARDENING / P1** | raw key stored in `sessionStorage` and globally reinjected |
| Session expiry semantics | **PARTIAL / P1** | cookie Max-Age exists, server token is deterministic with no server-checked issuance expiry |
| UI truthfulness | **FAIL / P0-P1** | multiple absence-as-success and unsupported semantic labels found |
| Options Intelligence | **INCOMPLETE / P1** | truth/staleness checks missing; validated-forecast contradiction; Greeks not present in this workspace |
| Prediction audit | **PENDING / REQUIRED** | UI explicitly says production prediction ledger not wired |
| Factor/scenario risk | **PENDING / REQUIRED** | UI explicitly shows both services pending |
| Responsive/mobile UI | **NOT PROVEN / P2** | fixed sidebar and no viewport responsive breakpoint found in current frontend CSS |
| Accessibility focus proof | **NOT PROVEN / P2** | reduced-motion support exists; explicit focus-visible treatment not found |
| Dhan endpoint truth in UI | **INCORRECT / P1** | UI says `web.dhan.co`; official Dhan REST base is `api.dhan.co`, market feed is `api-feed.dhan.co` |
| Audit artifact freshness | **FAIL / P1** | generated audit text still contains old terminology not matching current source |
| Cloud Run analyzer/live-off deployment flags | **PASS IN WORKFLOW SOURCE** | live flags remain 0 and analyzer mode remains 1 |
| Real-market paper lifecycle | **NOT PROVEN** | historical blocker still open |
| Multi-day positive costed expectancy | **NOT PROVEN** | no same-revision reproducible proof |
| Real-money trade ready | **NO** | P0/P1 blockers and missing runtime/profitability proof |

## 2. Iteration delta — what changed from the previous report

### New verified findings

1. **P0 UI false-reassurance pattern:** `DecisionIntelligence` shows `✓ NO SYSTEM BLOCKERS` when `health.blockers` is absent as well as when it is a proven empty array.
2. **P0/P1 contradictory forecast semantics:** `OptionsIntelligence` calls gain-rank rows `System3 Top Forecasts`, while `PredictionAudit` explicitly states the scanner gain-rank list is **not a validated forecast**.
3. **P1 Dhan endpoint label error:** `DataIntegrity` hard-codes `web.dhan.co` as `API ENDPOINT`; official Dhan v2 REST examples use `https://api.dhan.co/v2/...` and live market feed uses `wss://api-feed.dhan.co`.
4. **P1 broker-auth/security conflation:** `DataIntegrity` renders `Session is active and secure` solely from `brokerConnected`.
5. **P1 freshness false-green risk:** any truthy `chain_age` or `top_age` is marked OK; no threshold or age unit contract is applied.
6. **P1 options truth defects:** zero-valued PCR/IV can render as missing because `||` is used; missing OI change is rendered as `STABLE` without evidence.
7. **P1 positions absence-vs-zero ambiguity:** `OptionsIntelligence` shows `NO ACTIVE DHAN POSITIONS` whenever parsed rows are empty, without proving broker/auth/API success.
8. **P1 mode truth defect:** `DecisionIntelligence` hard-codes `PAPER` / `LIVE OFF` instead of deriving the display from an authoritative runtime safety state.
9. **P2 responsive gap:** primary sidebar is fixed at `190px`; current `index.css` contains reduced-motion media handling but no viewport breakpoint for the application shell/sidebar.
10. **P2 accessibility gap:** no repository match for `focus-visible`; WCAG 2.2 focus appearance therefore remains unproven.
11. **P1/P2 information-architecture overload:** 22 sidebar destinations expose several overlapping truth/system/market workflows without progressive disclosure.

### Refined previous findings

- Auth findings remain open and are now explicitly separated into HTTP-contract, pre-auth polling, browser-key exposure and server-expiry semantics.
- UI terminology cleanup is no longer treated as evidence of readiness; truth semantics are audited independently from wording.
- “World-class UI” target is now defined as an institutional task workflow with an always-visible truth strip, not a larger collection of tabs.

## 3. Verification counters

Independent verification means a different evidence path or contradiction test; rereading the same unchanged artifact does not increment the count.

| Finding ID | Conclusion | Counter | Lock state |
|---|---|---:|---|
| AUTH-001 | LoginPage/backend session payload mismatch | `3/20` | OPEN |
| AUTH-002 | `useData()` starts before authentication is established | `2/20` | OPEN |
| AUTH-003 | raw dashboard key persists in browser JS-accessible storage | `2/20` | OPEN |
| UI-001 | missing data can be presented as “no blockers” | `2/20` | OPEN |
| UI-002 | gain-rank is mislabeled as validated forecast in one workspace | `2/20` | OPEN |
| UI-003 | Dhan endpoint shown in Data Integrity is operationally misleading | `2/20` | OPEN |
| UI-004 | broker connectivity is incorrectly used as secure-session proof | `1/20` | OPEN |
| UI-005 | options fallback/default expressions can misstate zero/missing values | `1/20` | OPEN |
| UI-006 | empty positions rows are not distinguished from unproven broker response | `1/20` | OPEN |
| UI-007 | current shell lacks proven responsive navigation behavior | `2/20` | OPEN |
| UI-008 | explicit keyboard focus appearance is not proven | `2/20` | OPEN |
| UI-009 | factor/scenario risk services are pending | `1/20` | OPEN |
| UI-010 | immutable production prediction ledger is pending | `2/20` | OPEN |

No item has reached `LOCKED-20X` yet.

## 4. Critical authentication/security findings

### AUTH-001 — P0 — LoginPage HTTP request does not satisfy backend contract

**Status:** FIX-REQUIRED, verified.

**Frontend:** `dashboard/frontend/src/components/LoginPage.tsx:8-22`

```ts
fetch('/api/auth/session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'X-API-Key': key.trim() },
  credentials: 'include',
})
```

No body is sent.

**Backend:** `dashboard/backend/app.py:430-485`

```py
class DashboardAuthRequest(BaseModel):
    api_key: str
```

The endpoint reads `payload.api_key`. A real HTTP request without the body can fail Pydantic validation before key comparison.

**Independent cross-check:** `dashboard/frontend/src/components/AuthUnlock.tsx` already contains the correct pattern: `body: JSON.stringify({ api_key: apiKey.trim() })`.

**Why this matters for real money:** a broken login flow can cause operator lockout, unauthenticated polling noise, false broker-disconnected states and emergency-access failure during live operation.

**World-class fix:** use one typed auth API client; send the key once in a JSON body over HTTPS; establish cookie session; do not duplicate auth request construction across components.

**Closure proof:** browser integration test against FastAPI: valid body -> 200 + HttpOnly cookie; invalid key -> 401; missing body -> 422; refresh -> `/api/auth/status authenticated=true`; no key logged.

### AUTH-002 — P1 — Data polling begins before AuthGate decision

**Status:** FIX-REQUIRED.

**Source:** `dashboard/frontend/src/App.tsx:145-185`.

`App()` executes `useData()` and only then returns `<AuthGate>...`. Hooks run when `App` renders, so protected data polling can begin while the login page is being shown.

**Why it matters:** unnecessary 401/403 calls can contaminate broker/UI state, increase noise and mask genuine authentication/broker failures.

**World-class fix:** move data subscriptions into an authenticated `DashboardRuntime` child or make `useData({enabled: authenticated})` fail closed.

**Closure proof:** Playwright/network test: before auth, only static/auth-status/session traffic; zero protected broker/chain/paper endpoints. After auth, subscriptions start once.

### AUTH-003 — P1 — Raw API key retained in `sessionStorage`

**Status:** FIX-REQUIRED.

**Source:** `LoginPage.tsx` stores `s3_api_key`; `useAuth.ts` reads it and patches global axios/fetch to add `X-API-Key`.

**Why it matters:** an XSS in any same-origin UI code can read the raw API key. A global fetch monkey-patch also broadens where credentials may be attached.

**World-class fix:** key is one-time bootstrap credential only; remove it from JS-accessible storage after session creation; use HttpOnly, Secure, SameSite cookie; use a scoped API client instead of patching `window.fetch` globally.

**Closure proof:** browser storage inspection shows no raw API key; protected API works through cookie; CSP/XSS tests; logout invalidates session.

### AUTH-004 — P1 — “12-hour” session is not independently server-expiring

**Status:** FIX-REQUIRED / design hardening.

**Source:** `dashboard/backend/app.py:430-485` derives the cookie token deterministically from `_API_KEY`; server compares token equality but does not encode/check issued-at or expiry.

Browser Max-Age limits normal cookie sending, but a copied token is not rejected based on age by server logic.

**World-class fix:** random opaque server-side session with TTL, or signed expiring token containing issued-at/expiry plus rotation/revocation support.

**Closure proof:** replay a captured expired session token after server TTL and prove 401; rotation invalidates older session.

## 5. Dashboard/UI truth findings — deep slice 1

### UI-001 — P0 — Absence of blocker data is displayed as success

**Status:** FIX-REQUIRED.

**Source A:** `DecisionIntelligence.tsx:30-115`:

```tsx
health?.blockers?.length > 0 ? ... : <div>✓ NO SYSTEM BLOCKERS</div>
```

If `health` or `blockers` is absent, the branch renders the same green success as a proven empty array.

**Source B:** `DataIntegrity.tsx:20-110` uses the same pattern for `health.errors`: missing error telemetry renders `✓ NO ACTIVE DATA BLOCKERS`.

**Real-money impact:** false-green is more dangerous than an explicit failure; an operator can trade while telemetry itself is missing.

**World-class solution:** three-state semantics everywhere: `PASS`, `FAIL`, `UNKNOWN/NO PROOF`. Success requires explicit schema-valid data plus fresh timestamp; absence must never equal success.

**Closure proof:** component tests for undefined, null, stale, empty-proven, non-empty-failure; only explicit fresh empty result may be green.

### UI-002 — P0/P1 — Gain-rank is labeled as “Top Forecasts” despite audit contract saying it is not a validated forecast

**Status:** FIX-REQUIRED.

**Source A:** `OptionsIntelligence.tsx:30-175` renders `System3 Top Forecasts vs Market Leaders` for `gainRank.rankings`.

**Source B:** `PredictionAudit.tsx` explicitly states: `the scanner's gain-rank list is not a validated forecast`.

**Real-money impact:** converts a ranking/scanner output into an apparently predictive claim. This can materially bias order decisions.

**World-class solution:** rename to `Scanner / Gain Rank` until a validated prediction artifact exists. A forecast badge may only appear when a prediction record has model version, frozen input cutoff, probability/confidence, uncertainty, calibration status and immutable ledger ID.

**Closure proof:** cross-workspace semantic contract test prevents `forecast/prediction` labels for unvalidated gain-rank payloads.

### UI-003 — P1 — Data Integrity shows wrong operational Dhan API endpoint

**Status:** FIX-REQUIRED.

**Source:** `DataIntegrity.tsx:20-110` hard-codes `API ENDPOINT = web.dhan.co`.

**Primary-source cross-check:** official Dhan v2 REST examples use `https://api.dhan.co/v2/...`; official live feed uses `wss://api-feed.dhan.co`.

`web.dhan.co` is used for the Dhan web login/user flow, not as the runtime REST trading API base shown by official v2 API examples.

**World-class solution:** show separate, runtime-derived endpoints:

- REST: `api.dhan.co` (sanitized host only)
- Market feed: `api-feed.dhan.co`
- connection mode/version
- last successful request/tick
- latency and auth status

Never hard-code operator health truth in presentation code.

**Closure proof:** UI value comes from backend connection metadata and matches actual configured host; integration test compares sanitized runtime host to displayed host.

### UI-004 — P1 — Broker connection is presented as secure dashboard session proof

**Status:** FIX-REQUIRED.

**Source:** `DataIntegrity.tsx:20-110`:

```tsx
{brokerConnected ? 'Session is active and secure.' : ...}
```

`brokerConnected` is a broker state; it does not prove dashboard-session security, cookie flags, session age, API-key protection, user identity or authorization.

**World-class solution:** split four states: `Dashboard Auth`, `Dhan Auth`, `Market Data Feed`, `Trading Permission`. Never derive one from another.

**Closure proof:** each badge uses a separate backend field with schema test and independent negative tests.

### UI-005 — P1 — Data freshness is marked OK from truthiness, not an SLA/age threshold

**Status:** FIX-REQUIRED.

**Source:** `DataIntegrity.tsx:20-110`:

```tsx
status={health?.data?.chain_age ? 'ok' : 'mut'}
status={health?.data?.top_age ? 'ok' : 'mut'}
```

Any truthy string/value can become green, even an old value.

**World-class solution:** normalize age to milliseconds/seconds and apply explicit market-state-aware thresholds. Show absolute event timestamp + age + source + allowed threshold. Market-closed snapshots need a separate semantic state, not live-green.

**Closure proof:** threshold boundary tests, market-open vs closed tests, stale feed test, clock-skew test.

### UI-006 — P1 — Options values use unsafe fallbacks that can fabricate semantics

**Status:** FIX-REQUIRED.

**Source:** `OptionsIntelligence.tsx:30-175`.

- `pcr_oi || '—'` hides a legitimate numeric zero.
- `pcr_vol || '—'` hides a legitimate numeric zero.
- `iv_percentile ? ... : 'PENDING'` turns zero into pending.
- `oi_change || 'STABLE'` fabricates `STABLE` when the field is absent.

**World-class solution:** use explicit nullish checks (`??`) plus schema validation. Never substitute directional/market semantics such as `STABLE` for missing data.

**Closure proof:** unit tests for `0`, `null`, `undefined`, `NaN`, valid positive/negative values; missing value must render `UNKNOWN/NO DATA` not a market conclusion.

### UI-007 — P1 — Option intelligence does not prove chain source/freshness before rendering analytics

**Status:** FIX-REQUIRED.

The workspace checks only whether `currentChain` is truthy before showing PCR/IV/OI. It does not locally require Dhan source, valid spot/contracts, non-stale/live-or-approved-snapshot semantics before displaying analytics.

**World-class solution:** one shared `DataTruthEnvelope` required by every analytic component: source, event timestamp, received timestamp, age, market state, snapshot/live, quality status, schema version. Render analytics only when envelope policy passes; otherwise show last-good snapshot with explicit age or no-proof state.

**Closure proof:** stale/fallback/mock payload cannot produce a normal analytics card.

### UI-008 — P1 — Empty positions can be confused with proven zero positions

**Status:** FIX-REQUIRED.

**Source:** `OptionsIntelligence.tsx:30-175` parses rows; if zero rows, it always renders `NO ACTIVE DHAN POSITIONS`.

A zero-row result may be a real empty account, but can also occur if response shape changes, auth is pending, API failed, or the store holds a pending fallback object.

**World-class solution:** distinguish `LOADING`, `AUTH_REQUIRED`, `API_ERROR`, `SCHEMA_ERROR`, `PROVEN_EMPTY`, `ROWS_PRESENT`, `STALE_LAST_GOOD`.

**Closure proof:** broker response metadata must explicitly prove a successful current read before `NO ACTIVE POSITIONS` is allowed.

### UI-009 — P1 — PAPER/LIVE state is hard-coded in Decision Intelligence

**Status:** FIX-REQUIRED despite current live-off safety intent.

**Source:** `DecisionIntelligence.tsx:30-115` hard-codes `MODE=PAPER`, `LIVE=OFF` and prose stating trading is inhibited.

**Why this matters:** if deployment/runtime configuration ever drifts, the UI could continue saying `LIVE OFF`. For real-money trading, safety state must be runtime truth, not static copy.

**World-class solution:** authoritative backend safety object with redundant fields (`mode`, `live_enabled`, `auto_execute`, `order_router_state`, `last_verified_at`, revision). UI fails closed to `UNKNOWN / DO NOT TRADE` if unavailable.

**Closure proof:** controlled test payloads verify display changes; unknown backend state never shows live-off certainty or trade-ready success.

### UI-010 — P1 — Prediction Audit is an explicit required placeholder

**Status:** FIX-REQUIRED before predictive real-money use.

**Source:** `PredictionAudit.tsx` says no production prediction ledger is wired and renders `PREDICTION LEDGER PENDING` / `DATA SERVICE PENDING`.

**Required institutional target:** append-only prediction record including target, horizon, model/version/hash, probability, uncertainty, evidence/counter-evidence, data cutoff, feature schema, decision, realized outcome, fees/slippage, calibration bucket and tamper-evident audit ID.

**Closure proof:** immutable write/read path, hash/sequence integrity check, prediction-to-outcome reconciliation, model-version lineage, retention/export test.

### UI-011 — P1 — Factor risk and scenario engine are explicit required placeholders

**Status:** FIX-REQUIRED for real-money readiness.

**Source:** `RiskAndScenarios.tsx` displays `FACTOR RISK SERVICE PENDING` and `SCENARIO ENGINE PENDING`.

**Required target:** for options/futures, minimum risk view should include net/gross exposure, concentration, underlying/expiry buckets, portfolio Greeks, gap/stress scenarios, max-loss/defined-risk truth where applicable, margin utilization, drawdown limits and pre-trade limit headroom.

**Closure proof:** deterministic scenario fixtures, Greek aggregation reconciliation, margin/risk endpoint integration, stale-price rejection, boundary/limit tests.

### UI-012 — P2 — Navigation is dense and task-fragmented

**Status:** RECOMMENDED redesign; not by itself a trading blocker.

**Source:** `Sidebar.tsx` exposes 22 destinations across Command, Market Data, Trading, Analysis and System. Several workflows overlap: `Decision Intel/Overview`, `Truth/E2E/Data Integrity/Broker/System`, `Options Intel/Option Chain`, `Performance/ML/Prediction Audit`.

**World-class target:** primary task navigation of ~8-10 workspaces, with sub-tabs/drilldowns inside each workspace. Preserve all proven capabilities; consolidate surfaces, not data.

Recommended primary IA:

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

### UI-013 — P2 — Responsive/mobile behavior is not proven

**Status:** FIX/PROOF REQUIRED.

**Source A:** `Sidebar.tsx` uses fixed `width: 190px`.

**Source B:** `index.css` includes `@media (prefers-reduced-motion: reduce)` but no viewport-width responsive shell/sidebar rule was found.

**World-class solution:** desktop multi-pane workstation + tablet collapsible rail + mobile read-only priority view. Order-capable controls, if ever introduced, require intentional mobile-safe flows rather than desktop controls compressed onto a phone.

**Closure proof:** Playwright viewport matrix (desktop 1920/1440, laptop 1366, tablet, mobile); zero inaccessible essential controls, zero uncontrolled horizontal shell overflow, screenshot diffs.

### UI-014 — P2 — Keyboard focus appearance is not proven

**Status:** FIX/PROOF REQUIRED.

Repository search found no `focus-visible`. `select:focus` changes border, but there is no demonstrated consistent high-visibility keyboard focus treatment for all interactive controls.

WCAG 2.2 includes stronger focus appearance expectations and keyboard-visible focus is especially important in a dense operational dashboard.

**World-class solution:** global `:focus-visible` token with high-contrast outline, no focus suppression, logical tab order, skip-to-content, table/grid keyboard strategy, aria-live for status changes where appropriate.

**Closure proof:** automated accessibility scan plus manual keyboard-only walkthrough of every primary workflow.

## 6. Positive UI evidence retained

These are useful foundations and should be preserved:

- `index.css` defines consistent design tokens and tabular numeric font behavior.
- reduced-motion preference is explicitly respected.
- `Sidebar` uses semantic `<nav>`, `aria-label`, button labels and `aria-current`.
- workspaces use explicit PENDING states rather than fabricated data in several unfinished services.
- Prediction Audit correctly warns that gain-rank is not a validated forecast.
- Risk workspace states there are no executable controls in that workspace.
- analyzer/live-off intent is visible throughout the UI.

Positive evidence is not promoted to readiness until runtime truth and integration tests prove it.

## 7. World-class target UI architecture — design baseline V1

### 7.1 Always-visible truth strip — REQUIRED

Every screen should display, from authoritative runtime data:

- mode: Analyzer / Paper / Live
- live-order router: disabled/enabled/unknown
- Dhan REST auth status + token expiry
- market feed status + source
- market open/closed
- last tick/event timestamp + age
- Cloud Run revision + application commit
- risk gate state
- reconciliation state
- open critical incidents/blockers

Unknown must be visibly different from pass/fail.

### 7.2 Command Center — REQUIRED

One-screen operational answer to:

- Is the system safe to use?
- Is data live, fresh and Dhan-sourced?
- What is the strongest current scanner/AI evidence?
- What positions/paper positions exist?
- What is portfolio risk?
- Which gate prevents real-money execution?
- What changed recently?

### 7.3 Market / Scanner — REQUIRED

- configurable watchlists
- real-time quotes/volume and market status
- scanner ranking with source, timestamp, model/rule origin
- market-leader comparison clearly separated from forecasts
- filtering/sorting/search with saved views
- drilldown to symbol workspace

Primary reference cross-check: TradingView Trading Platform documents watchlists, details widgets, news, account manager and event/subscription based UI composition. These are design-pattern references only; they are not claims that System3 has these capabilities.

### 7.4 Options & Greeks — REQUIRED

- expiry selector and strike ladder
- bid/ask/LTP/spread/volume/OI/OI change/IV
- Delta/Gamma/Theta/Vega and portfolio aggregate Greeks
- PCR, IV percentile only when validated
- ATM/ITM/OTM visual hierarchy
- source + freshness per chain
- snapshot/live distinction
- scanner context and position overlay
- scenario P&L / Greek shift view

### 7.5 AI Decision Audit — REQUIRED before AI-driven live money

- candidate vs validated prediction distinction
- probability/confidence and uncertainty
- evidence + counter-evidence
- model version/hash
- frozen data cutoff
- calibration metrics
- prediction ledger ID
- realized outcome and after-cost result
- explanation must never replace quantitative evidence

### 7.6 Portfolio / Risk — REQUIRED

- funds, margin, exposure, realized/unrealized P&L
- positions with broker timestamp
- concentration and expiry exposure
- aggregate Greeks
- max daily loss/drawdown headroom
- stress scenarios
- reconciliation state
- kill-switch status as display only until a separately audited execution-control program exists

### 7.7 Observability — REQUIRED

Google Cloud guidance supports dashboards that combine service health/SLO status, alerts and logs. System3 should surface operator-level versions of:

- API availability SLI/SLO
- broker read success ratio
- market-feed freshness SLI
- p50/p95/p99 endpoint latency
- websocket reconnect/disconnect counts
- event-loop lag / memory / CPU
- Cloud Run revision/image/commit provenance
- recent incidents and error-budget burn

### 7.8 Accessibility / operator ergonomics — REQUIRED

- WCAG 2.2-aligned keyboard/focus behavior
- color is never the sole status signal
- tabular numerics
- UTC/IST policy explicit; market timestamps consistently labeled
- dangerous controls separated from informational controls
- no animation required to understand state
- high-density mode plus comfortable mode
- saved layout preferences

## 8. Feature priority matrix

### REQUIRED before live-money readiness can even be assessed

- truthful authentication and session state
- authoritative live/paper mode indicator
- Dhan REST/feed health and freshness
- no absence-as-success UI states
- validated option-chain + Greeks display
- proven positions/funds/margin truth
- paper lifecycle + reconciliation
- factor/portfolio/scenario risk
- prediction ledger for AI-driven decisions
- immutable auditability
- pre-trade risk gates
- latency/freshness observability
- incident/error display
- responsive safe operator layout
- keyboard/accessibility baseline
- same-revision deployment provenance

### RECOMMENDED

- consolidated task-based navigation
- multi-monitor layout presets
- saved watchlists/workspaces
- advanced chart annotations
- crosshair-linked option/underlying views
- custom alerts and incident timeline
- comparison of scanner signal vs market leaders
- configurable data-density modes

### OPTIONAL until core truth/safety is proven

- news/sentiment enrichment
- catalyst enrichment
- social sentiment
- cosmetic themes beyond accessible dark/light
- extensive drawing-tool ecosystem
- advanced multi-chart layouts
- mobile order entry

Optional breadth must never delay or obscure required truth/safety work.

## 9. Historical verified checkpoints retained

### V5 consolidation snapshot

`docs/audit/V5_CONSOLIDATION_VALIDATION.md` recorded:

- direct backend routes `183 -> 183`, removed `0`
- navigation tabs `16 -> 22`
- frontend production build PASS
- dashboard tests `7/7 PASS`
- security/deployment contract tests `24/24 PASS`
- syntax checks PASS
- production npm vulnerabilities `0`
- embedded reusable frontend API key removed
- live trading disabled

This is historical evidence only; later code changed.

### PR checkpoints

- PR #93 login/session feature: configured blocking CI passed, but integration coverage did not catch the actual LoginPage HTTP-body mismatch.
- PR #95 broker-status CI auth: CI-only auth proof change.
- PR #96 UI status cleanup: workflows passed at that checkpoint.
- application HEAD `b70af343...` is later than PR #96 merge and is not marked current-HEAD CI-proven by this audit.

## 10. Google Cloud / deployment findings retained

- Cloud Run workflow is the deployment source of truth.
- root `render.yaml` absent.
- residual Render terminology remains in frontend/backend comments/status handling.
- Cloud Run deploy env string contains duplicate `REQUIRE_API_KEY=true` entry.
- workflow source preserves: `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, `ANALYZE_MODE=1`, `SYSTEM3_MODE=ANALYZER`.
- production runtime still requires exact-revision proof: revision, image digest, commit, health, authenticated broker status, funds/positions/holdings, required chains, browser proof and safety flags.

## 11. Historical open trading gates

Carry forward until new proof closes them:

- `real_market_analyzer_paper_lifecycle_not_proven`
- `nse_comparison_proof_missing`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is a required safety state during this audit, not a defect.

## 12. Closure standard for every finding

A finding may be `CLOSED` only when all relevant evidence is tied to the exact changed commit:

1. code/config fix inspected;
2. negative and positive tests added;
3. build/compile/type/static checks pass;
4. applicable unit/integration/browser tests pass;
5. deployment proof for the same revision when runtime-dependent;
6. no safety regression in analyzer/live-off flags;
7. stale/old audit trackers regenerated;
8. screenshot/browser proof for UI findings;
9. cross-contract verification for frontend/backend fields;
10. no contradictory evidence from another independent path.

## 13. Next audit slices

Priority sequence for subsequent iterations:

1. **Option Chain + Greeks implementation and field truth** — compare `OptionChain`, backend chain routes, greeks calculators and Dhan payload normalization.
2. **TopBar / ProductionProofBar / Truth Control / E2E Proof** — hunt contradictory global states and false-green readiness.
3. **Paper Trading + Trade + Positions** — lifecycle, reconciliation, P&L truth, zero-vs-error semantics.
4. **RiskDashboard + Auto Gates** — map risk limits to actual enforceable backend gates.
5. **WebSocket/polling architecture** — reconnect, stale cache, out-of-order messages, timestamps and heartbeat semantics.
6. **Observability / Cloud Run provenance** — SLO, logs, metrics, error budgets, revision truth.
7. **Responsive/accessibility browser proof** — viewport matrix, keyboard, focus, screen-reader/status semantics.

## 14. Hard safety rule

UI wording, design quality, green badges or successful builds can never substitute for broker/data/risk/runtime proof. Any future live-order capability must be separately designed, independently audited, gated, staged and proven before activation. During this audit, live order placement/modification/cancellation/routing remains prohibited.
