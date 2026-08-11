# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 09:48 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `416cc5db5e4b077fd3b8924a20e58ce7990dff89`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..416cc5db5e4b077fd3b8924a20e58ce7990dff89` is **14 commits ahead** and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`. Its synthetic-P&L suppression still substitutes zero for unavailable/rejected P&L, so it does not close null/provenance concerns.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Exact application-HEAD workflow/runtime proof remains **NOT PROVEN**; the current GitHub connector returned no workflow runs bound to application HEAD `b70af343...`.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH** via `StateTruth` + domain-CAS |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN** via `PredictionTruth` |
| Model provenance / leakage control | **INCOMPLETE / P0-P1** | **READY TO PATCH** |
| Probability calibration / drift | **NOT PROVEN / P1** | **READY TO PATCH/DESIGN** |
| Responsive/mobile workstation | **FAIL / P1** | **READY TO PATCH** via responsive shell |
| Accessibility/keyboard/focus/live-state semantics | **FAIL / P1** | **READY TO PATCH** via `AccessibleWorkstationShell` |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH** via `DeploymentTruth` |
| Observability/runtime error truth | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..004` OPEN: login contract mismatch, pre-auth polling, raw browser API-key storage, incomplete session expiry/revocation proof.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, weak responsive/accessibility and deployment/build truth.
- `CHAIN-001..014` OPEN: warming PCR false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `READY-001..009` OPEN: missing safety evidence default-safe paths, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN: default safety/data values, unproven mutation route, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrail conditions, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.
- `ML-001..014` OPEN: missing immutable prediction ledger, overloaded model-proof boolean, dictionary-first model selection, rank→confidence misuse, ambiguous percentage units, unknown→zero metrics, tracker type bug, unsafe accuracy math, non-atomic tracker persistence, non-purged/non-global time split, incomplete artifact identity, selection/evaluation leakage, missing calibration and no prediction→after-cost linkage.

## 4. New deep slice — responsive, accessibility, keyboard and constrained-layout workstation behavior

### A11Y-001 / P1 — application shell is fixed-height/fixed-sidebar and has no responsive layout authority

**Exact proof:** `dashboard/frontend/src/App.tsx` uses a `100vh` flex column, a permanently rendered `Sidebar`, and a main region with `overflow:'hidden'`. `Sidebar.tsx` fixes navigation width to `190px` with 22 tab buttons. There is no breakpoint/drawer logic in these files.

**Symptom/root cause:** the desktop shell is treated as universal. A small viewport must fit a fixed sidebar plus workstation content instead of intentionally switching information architecture.

**Real-money impact:** critical status, risk, broker/data and order-safety controls can be clipped or forced below usable widths; an operator on tablet/mobile can miss authoritative warnings or select the wrong workspace.

**Exact files:** `dashboard/frontend/src/App.tsx`, `dashboard/frontend/src/components/Sidebar.tsx`, new responsive shell/layout primitives, relevant workspace tables.

**Target behavior:** desktop ≥1280px uses persistent navigation; tablet uses compact rail; mobile uses modal/drawer navigation and bottom quick-actions. Critical truth strip remains visible; secondary telemetry moves into drilldowns.

**Minimal safe implementation:** introduce `useViewportClass()` + CSS container/breakpoint tokens and a single `WorkstationShell`. Sidebar becomes `desktop | compact | drawer`; content regions receive explicit scroll ownership.

**Regression risks:** hiding controls at breakpoints, trapping focus in drawer, duplicate navigation state, content remount/data refetch.

**Closure tests/PASS:** Playwright viewport matrix 360×800, 390×844, 768×1024, 1024×768, 1366×768, 1920×1080; no clipped safety controls; all tabs reachable; no horizontal page scroll except deliberate data-table scrollers; active workspace survives orientation/layout change.

**Fail-safe:** when viewport rules fail, show a safe reduced control surface with live router still locked and truth/status visible.

**Status:** `READY TO PATCH`.

### A11Y-002 / P1 — TopBar hides overflow instead of prioritizing/reflowing critical controls

**Proof:** `TopBar.tsx` header sets `overflow:'hidden'`; index chips occupy a flex region also with `overflow:'hidden'`; owner identity, Cloud Build badge, clock, NIFTY/BANKNIFTY/FINNIFTY, sync age, market, Dhan, PAPER, LIVE OFF, WS and rho all compete for one fixed 56px row.

**Impact:** constrained width can silently remove market/broker/live/WS truth from view.

**Solution:** priority-tier header: Tier 0 always-visible safety (`MODE`, `LIVE LOCK`, market/session, broker/data age); Tier 1 index watch becomes horizontally scrollable; Tier 2 owner/build/rho moves to overflow/command panel. Never clip Tier 0.

**Tests:** screenshot/assert visibility at all supported widths; no Tier-0 element may have zero intersection with viewport.

**Status:** `READY TO PATCH`.

### A11Y-003 / P1 — navigation is technically button-based but not optimized for 22-tab keyboard operation

**Proof:** `Sidebar.tsx` renders every tab as a normal button, so keyboard users must traverse the entire 22-item sequence. There is no roving focus, group-level arrow navigation, workspace search or command palette.

**Impact:** slow navigation under incident/market pressure increases operator error and makes the workstation inefficient for keyboard-first use.

**Solution:** keep native buttons, add roving `tabIndex` within grouped navigation, Up/Down/Home/End movement, Left/Right group movement where appropriate, `Ctrl/Cmd+K` workspace command palette, and skip-to-content link. Preserve `aria-current=page`.

**Tests:** keyboard-only traversal of every workspace, focus order snapshot, no keyboard trap, command palette searchable by current and rationalized tab names.

**Status:** `READY TO PATCH`.

### A11Y-004 / P1 — broker TopBar navigation control is a clickable `span`, not an accessible control

**Proof:** `TopBar.tsx` uses `<span onClick={() => setActiveTab('broker')}>` with `cursor:'pointer'` for the Dhan broker status chip; it has no button role, no tab focus, and no Enter/Space behavior.

**Impact:** keyboard and assistive-technology operators cannot reliably activate a critical broker-health drilldown.

**Solution:** replace with native `<button type="button">`; preserve visual styling, add descriptive accessible name including broker quality, and maintain visible focus.

**Tests:** Tab reaches broker chip; Enter and Space open Broker workspace; axe has no interactive-role violation.

**Status:** `READY TO PATCH`.

### A11Y-005 / P1 — broker status in Sidebar has a color-only indicator

**Proof:** the Broker navigation item adds an unlabeled 7px colored dot based on `brokerConnected`; the button's text remains only `Broker`.

**Impact:** color-vision deficiency or screen-reader users do not receive the broker state represented by the dot.

**Solution:** decorative dot gets `aria-hidden=true`; accessible button name/description includes typed state (`Broker — connected`, `Broker — unknown`, etc.) sourced from broker truth, and visible text/badge uses words/icons as well as color.

**Status:** `READY TO PATCH`.

### A11Y-006 / P1 — login error/loading/status feedback lacks live-region semantics

**Proof:** `LoginPage.tsx` renders errors in a plain `<div>` with no `role="alert"`/`aria-live`; `AuthGate` loading text similarly has no status role. The login label has no `htmlFor`/input `id` relationship.

**Impact:** assistive technology may not announce authentication failure or loading changes; the field label association is weaker than required for a professional security surface.

**Solution:** `role="status" aria-live="polite"` for loading; `role="alert" aria-live="assertive"` for auth failures; explicit `label htmlFor`, input `id/name`, `aria-describedby`; use appropriate autocomplete policy and never expose the raw key after authentication.

**Security constraint:** this accessibility patch must align with `SOL-01`; the raw API key must be removed from `sessionStorage`, not made easier to persist.

**Status:** `READY TO PATCH`.

### A11Y-007 / P1-P2 — critical telemetry uses very small text sizes

**Proof:** `TopBar.tsx` and `Sidebar.tsx` use repeated `.45rem`, `.5rem`, `.52rem`, `.55rem`, `.6rem`, `9px`, and `10px` text for build identity, labels and status badges.

**Impact:** dense workstation information can become unreadable on high-DPI laptops/tablets and for low-vision users; status interpretation slows under pressure.

**Solution:** define minimum semantic type tokens: critical status ≥12px equivalent, secondary telemetry ≥11px, interactive labels ≥12px; support browser zoom 200% without loss of controls; use truncation only with accessible full text.

**Tests:** WCAG reflow at 200% zoom and 320 CSS px equivalent; no safety label clipped or hidden.

**Status:** `READY TO PATCH`.

### A11Y-008 / P1 — scroll ownership is fragile because body and main are both overflow-hidden

**Proof:** `index.css` sets `html, body { overflow:hidden }`; `App.tsx` also sets main `overflow:'hidden'`. Therefore every workspace must independently implement scrolling correctly or content becomes unreachable.

**Impact:** long tables, dialogs or error panels can become inaccessible, especially after zoom or on short-height screens.

**Solution:** one explicit shell scroll contract: app body stays fixed only if the active workspace root has guaranteed `overflow:auto`; use reusable `WorkspaceViewport` and `DataScroller`. Dialogs portal to body with their own scroll/focus lock.

**Tests:** automated content-height stress tests, 200% zoom, 600px viewport height and long-table fixtures; last interactive row/control remains reachable.

**Status:** `READY TO PATCH`.

### A11Y-009 / P1 — no consistent visible-focus design for workstation controls

**Proof:** `index.css` defines a custom focus border only for `select`; navigation and inline-styled critical controls do not use a shared `:focus-visible` token. Browser defaults may remain, but there is no product-level proof of consistent high-contrast focus.

**Impact:** keyboard operators can lose track of active control in a dense dark UI.

**Solution:** global `:focus-visible` ring token with ≥2px visible contrast, offset and no color-only ambiguity; native semantics first; modal focus trap/restoration standardized.

**Tests:** automated focus-outline snapshots across every interactive component and theme; no element with `outline:none` unless replaced by equal/stronger focus indicator.

**Status:** `READY TO PATCH`.

### A11Y-010 / P1 — dynamic market/broker/WS safety-state changes are not exposed through controlled live regions

**Proof:** TopBar updates market status, broker state, WS state and tick age visually but does not expose an accessibility announcement channel. ProductionProofBar has an `aria-label` but no `aria-live` state-change strategy.

**Impact:** a screen-reader user can remain unaware that market/data/broker state degraded or live-lock/readiness changed.

**Solution:** create a deduplicated `CriticalStatusAnnouncer` that announces only meaningful transitions (`HEALTHY→STALE`, `CONNECTED→ERROR`, `PAPER→UNKNOWN`, risk inhibit), not every market tick. Use `aria-live=polite`, escalating safety failures to assertive only when operator action is required.

**Tests:** transition-driven screen-reader DOM assertions; no announcement spam from per-second clock/tick updates.

**Status:** `READY TO PATCH`.

### A11Y-011 / P1 — status color semantics need text/icon redundancy and contrast proof

**Proof:** green/amber/red are heavily used for market, broker, WS, proof and sidebar states. Some controls contain text, but several micro-indicators and small labels rely strongly on hue.

**Solution:** every safety/data state includes icon + explicit word (`HEALTHY`, `STALE`, `UNKNOWN`, `ERROR`, `LOCKED`) and meets contrast targets. Do not encode direction/safety solely by red/green.

**Tests:** axe contrast checks plus monochrome/color-blind visual regression snapshots.

**Status:** `READY TO PATCH`.

### A11Y-012 / P1 — actual browser accessibility/runtime proof is absent

**Proof:** this iteration could statically inspect source but no exact-application-head browser/Playwright/axe workflow run exists in the current evidence set.

**Impact:** keyboard/focus/reflow/ARIA claims cannot be closed from code inspection alone.

**Solution:** add exact-revision `ui-accessibility-proof` workflow: build frontend, launch analyzer/paper backend with non-live fixtures, run Playwright + axe on every workspace at desktop/tablet/mobile/200%-zoom, capture console errors/screenshots/accessibility violations and bind artifact to source SHA.

**PASS criteria:** zero critical/serious axe violations; zero console runtime errors; all required workspaces keyboard reachable; no critical status clipped; modal focus restore works; live router remains locked.

**Status:** `READY TO PATCH/DESIGN`.

## 5. Positive foundations in this slice

- Sidebar uses native `<button>` elements for tabs, has `aria-label`, `aria-current`, and a named `<nav>` landmark.
- `ProductionProofBar` has an accessible label and explicit text values in addition to colors.
- `index.css` already honors `prefers-reduced-motion: reduce`; preserve this.
- Login uses a native `<form>`, password input and submit button.
- App contains a semantic `<main>` element.

These are foundations only; they do not prove responsive/accessibility completeness.

## 6. Canonical truth contracts

### 6.1 `SafetyTruth`
Mode, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 6.2 `DataTruthEnvelope` / `StreamTruth`
Source/session/instrument, source/backend/frontend timestamps, uncapped age/TTL, schema/normalizer versions, transport vs heartbeat vs stream state, sequence/rejected-old events, quality and evidence.

### 6.3 `OptionChainTruth`
Underlying/security ID/segment, requested+resolved expiry authority, provider/session, times/age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, source/runtime revision and evidence ID.

### 6.4 `DeploymentTruth`
Exact source/tree SHA, Cloud Build ID, immutable image digest, final Cloud Run revision/traffic, frontend/backend SHA, runtime app/service account, policy/config hash, secret/scheduler provenance, verified time and evidence ID.

### 6.5 `StateTruth`
Required shared backend, collection/document, shared-state health, runtime/instance ID, last shared read/write, per-domain revision/writer/event/time/schema/quality/evidence. Global version is diagnostic only.

### 6.6 `PredictionTruth`
`prediction_id`, immutable issue time, target/horizon, instrument key, model artifact ID/hash, dataset/feature schema hash, frozen data cutoff, raw score, calibrated probability, uncertainty, evidence/counter-evidence, input truth IDs, runtime/source revision, maturity rule/state, later append-only outcome/calibration links.

### 6.7 `AccessibleWorkstationState` — NEW
Viewport class, navigation mode, focused workspace/control ID, modal/drawer state, critical-status announcement queue and density preference. This state is **non-authoritative for trading**; it must never affect risk/safety truth or live routing.

## 7. Canonical remediation roadmap

- `SOL-01 Auth/session — READY TO PATCH`: correct login body; cookie-only auth; remove raw API key; auth-gate polling/WS; TTL/revocation tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: one backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production zero/plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser, expiry-aware cache, explicit provenance/IV units/full Greeks.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 Scanner contract — READY TO PATCH`: rank/score/probability/forecast/realized distinct and nullable.
- `SOL-08 DeploymentTruth + GCP least privilege — READY TO PATCH`: immutable digest/final revision/source SHA, one service mutation, dedicated identities, WIF-only auth.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; ordered REST/WS merge; uncapped age; true WS proof.
- `SOL-12 RuntimeEventEnvelope — READY TO PATCH/DESIGN`: incidents/logs bound to source SHA + digest + Cloud Run revision.
- `SOL-13 StateTruth + domain-CAS — READY TO PATCH`: Firestore required in GCP; sparse domain writes; no local authority fallback; restart/multi-writer proof.
- `SOL-14 PredictionTruth + ModelArtifactManifest — READY TO PATCH/DESIGN`: immutable prediction ledger, exact model/data identity, purged walk-forward, untouched holdout, calibrated probability, drift monitoring and after-cost outcome linkage.
- `SOL-15 AccessibleWorkstationShell — READY TO PATCH`: responsive shell, tiered truth header, drawer/compact navigation, command palette, keyboard model, focus-visible, live regions, table reflow and exact-revision Playwright/axe proof.

### SOL-15 ordered implementation

1. Add viewport/layout tokens and `WorkstationShell` with explicit desktop/tablet/mobile modes.
2. Refactor Sidebar to persistent/compact/drawer modes with one source of active-tab truth.
3. Refactor TopBar into Tier-0 safety truth, Tier-1 market watch and Tier-2 overflow telemetry; never hide Tier-0.
4. Replace clickable non-semantic spans with native controls.
5. Add skip link, roving navigation keys and `Ctrl/Cmd+K` command palette.
6. Add shared `:focus-visible` design token and modal/drawer focus trap + restore.
7. Add `CriticalStatusAnnouncer` with transition deduplication; never announce per-tick noise.
8. Raise minimum type/touch-target sizing and preserve reduced-motion support.
9. Add reusable `WorkspaceViewport`, `DataScroller`, sticky table headers and mobile column-priority/card views.
10. Add explicit loading/empty/error/auth/market-closed/stale states with semantic roles.
11. Run Playwright + axe across all existing repo tabs, breakpoints, 200% zoom and keyboard-only scenarios.
12. Bind proof artifacts to exact source SHA/runtime revision; no PASS from static inspection alone.

**SOL-15 PASS criteria:** all current navigation destinations are reachable by keyboard and mobile; no Tier-0 safety truth is clipped; no dead/non-semantic interactive element remains; visible focus is consistent; critical state transitions are announced without spam; 200% zoom/reflow works; zero critical/serious axe violations and zero browser console runtime errors on the exact revision.

**Rollback/fail-safe:** if responsive/accessibility shell fails, render a reduced read-only layout with SafetyTruth/DataTruth visible and all trading mutation/live controls inhibited.

## 8. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `16/20` | OPEN |
| UI-002 | `4/20` | OPEN |
| UI-003 | `8/20` | OPEN — constrained-layout clipping adds another source/state visibility path |
| UI-005 | `14/20` | OPEN |
| UI-006 | `9/20` | OPEN |
| UI-007 | `9/20` | OPEN — top-level stream/broker state lacks complete accessible transition semantics |
| UI-009 | `6/20` | OPEN |
| UI-011 | `4/20` | OPEN |
| UI-016 | `10/20` | OPEN — fixed shell + hidden overflow independently reproduce responsive incompleteness |
| UI-018 | `2/20` | OPEN |
| CHAIN-001..014 | retained previous counters | OPEN |
| READY-001 | `5/20` | OPEN |
| READY-003 | `3/20` | OPEN |
| READY-008 | `2/20` | OPEN |
| PAPER-001..016 | retained previous counters | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN |
| GCP-001..011 | `1/20` each | OPEN |
| STATE-001..012 | `1/20` each | OPEN |
| ML-001..014 | `1/20` each | OPEN |
| A11Y-001..012 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 9. Prioritized implementation order

### P0 Wave 1 — eliminate false-green/fail-open authorities
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline.
4. SOL-13 shared `StateTruth` authority + domain-CAS.
5. SOL-05 OptionChainTruth null/cache/expiry correction.
6. SOL-11 StreamTruth and ordered REST/WS merge.
7. SOL-09 server-owned risk + mandatory pre-trade authority.
8. SOL-06 durable lifecycle/idempotency/reconciliation.
9. SOL-14 model maturity split + score/confidence correction + immutable PredictionTruth foundation.
10. SOL-04 semantic readiness.
11. SOL-03 remaining zero/live/default-safe fallbacks.
12. SOL-10 legacy mutation UI quarantine.

### P1 Wave 2 — operator safety + statistical/economic proof
1. **SOL-15 responsive/accessibility shell and exact-revision browser proof.**
2. Purged walk-forward + untouched holdout, calibration, drift, model/data hashes.
3. Prediction→paper→after-cost outcome linkage.
4. Full Greeks/model provenance and true WebSocket proof.
5. GCP IAM split/WIF-only auth and revision-bound runtime incidents.

### P2 Wave 3 — institutional operator quality
Advanced command palette/search, customizable density, saved workspace layouts, richer drilldowns, security/session settings and audit export. These remain secondary to truth/safety.

## 10. Product information architecture target

1. Command Center — Overview + Decision Intel + authoritative truth strip.
2. Market / Scanner — watch, scanner, ranker, signals.
3. Options & Greeks — chain, expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + model provenance + calibration/drift + evidence/outcome linkage.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — state authority, domain revisions, transport/heartbeat/source/freshness/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, incidents, logs, schema/parse errors, latency/reconnects and revision-bound evidence.
10. Security / Settings — sessions, IAM/policies, permissions, audit export and non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 11. Product UI visual evolution — V13

New concept: **Responsive Command Center V13** — actual System3 Command Center shown in desktop/tablet and mobile/constrained layouts.

Changes driven by this iteration:
- fixed 190px sidebar evolves into persistent desktop navigation, compact tablet rail and mobile drawer;
- Tier-0 truth (`MARKET`, `DHAN`, `WS`, `PAPER`, `LIVE LOCK`) is never hidden by header overflow;
- index watch and secondary telemetry are separately scrollable/overflow-managed;
- mobile uses priority cards instead of squeezing dense desktop tables;
- keyboard model is explicit: Tab/Shift+Tab, arrow navigation, Enter drilldown, Escape close, `Ctrl/Cmd+K` command palette;
- visible focus, 44px touch targets, text+icon status and critical live-region announcements are target requirements;
- execution remains inhibited when truth is unknown or viewport/shell proof fails;
- live router remains locked.

Visual artifact: `Genesis_System3_Responsive_Command_Center_Target_V13.png`.

## 12. Positive foundations to preserve

- Native Sidebar buttons, named navigation landmark and `aria-current`.
- ProductionProofBar accessible label and text status values.
- `prefers-reduced-motion` support in `index.css`.
- Semantic login form and main landmark.
- Prediction Audit's refusal to present gain-rank as a validated forecast.
- ML router's `ready_for_live=False` safety intent.
- Firestore transaction/local temp+replace foundations.
- Serialized/rate-paced Dhan option-chain traffic and WS reconnect backoff+jitter foundations.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness/accessibility/profitability proof.

## 13. Historical proof/open-gate interpretation

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
- `SHARED_STATE_AUTHORITY_NOT_PROVEN`
- `RESTART_CONSISTENCY_NOT_PROVEN`
- `MULTI_WRITER_LOST_UPDATE_PROTECTION_NOT_PROVEN`
- `PREDICTION_LEDGER_NOT_PROVEN`
- `MODEL_ARTIFACT_IDENTITY_NOT_PROVEN`
- `PURGED_WALKFORWARD_NOT_PROVEN`
- `PROBABILITY_CALIBRATION_NOT_PROVEN`
- `MODEL_DRIFT_MONITORING_NOT_PROVEN`
- `PREDICTION_AFTER_COST_LINKAGE_NOT_PROVEN`
- `RESPONSIVE_WORKSTATION_NOT_PROVEN`
- `KEYBOARD_NAVIGATION_NOT_PROVEN`
- `ACCESSIBILITY_AXE_BROWSER_PROOF_NOT_PROVEN`
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 14. Closure standard

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; model/data hashes and frozen-cutoff proof where applicable; leakage/purged-walk-forward/calibration/drift tests for ML; prediction→paper→after-cost reconciliation; concurrency/CAS/restart/failover tests; expiry/cache/freshness/order/reconnect tests as applicable; responsive viewport + 200%-zoom + keyboard + axe/console checks; immutable image digest + final Cloud Run revision/runtime proof; analyzer/live-off unchanged; and no contradictory independent evidence.

## 15. Next audit/solution slices

1. Scanner/ranker contracts and performance/memory/concurrency under market-open load.
2. Security/session detail: cookie policy, CSRF, session revocation, command/settings permissions and audit export.
3. ML follow-up: exact market-validation file semantics and whether gain-rank post-market validation has frozen prediction IDs/cutoffs or look-ahead paths.
4. DB follow-up: exact paper/event persistence files and any SQLite/JSON/Firestore duplicate authorities not yet mapped.
5. Browser implementation follow-up once SOL-15 lands: exact Playwright/axe/console proof across every workspace.

## 16. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser/training PASS, AUC/accuracy, rank-derived confidence, image tag, UI badge, workflow success description, global state version, Firestore transaction, local atomic write, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval, accessible-looking static markup or process-local simulator never substitutes for authoritative source+event time+domain revision+writer+freshness+schema+ordering+immutable prediction/model/data evidence+calibration+forward validation+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.