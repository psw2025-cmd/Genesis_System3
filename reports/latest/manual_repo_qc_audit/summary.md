# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 14:49 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `a8747ccb1bce1bafabb2eaaaf1423634b0c311c8`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after application HEAD remain audit-report commits only; no newer application implementation was promoted into the evidence baseline this iteration.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`.
- PR #96 remains the newest merged application/UI PR identified in the current GitHub evidence.
- GitHub returned no workflow runs for exact application SHA `b70af343...`; exact-revision CI/runtime readiness remains **NOT PROVEN**.
- Google Cloud is the only accepted deployment target. Render-era instructions are migration debt and must not remain operational authority.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing remain prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Canonical solution / implementation state |
|---|---|---|
| Exact application revision proof | **NOT PROVEN** | `DeploymentTruth` — READY TO PATCH |
| Dashboard auth/session | **FAIL / P0-P1** | `SessionTruth` — READY TO PATCH |
| Mutation authorization | **FAIL / P0-P1** | `MutationPolicy + CapabilityManifest` — READY TO PATCH |
| Global mode/order safety | **FAIL / P0** | `SafetyTruth + ExecutionEligibility` — READY TO PATCH |
| DB/shared state | **FAIL / P0-P1** | `StateTruth + domain CAS` — READY TO PATCH |
| WebSocket/REST truth | **FAIL / P0-P1** | `StreamTruth` — READY TO PATCH |
| Option chain/Greeks | **FAIL / P0-P1** | `OptionChainTruth` — READY TO PATCH |
| Scanner/ranker | **FAIL / P0-P1** | `ScannerTruth` — READY TO PATCH |
| Performance/concurrency | **FAIL / P0-P1** | `WorkCoordinator` — READY TO PATCH |
| Paper lifecycle | **FAIL / P0** | immutable command/event ledger — READY TO PATCH |
| Pre-trade risk authority | **FAIL / P0** | `PreTradeRiskService` mandatory for every paper/live-adjacent mutation |
| AI/prediction provenance | **MISSING / P0-P1** | `PredictionTruth` — READY TO PATCH/DESIGN |
| Accessibility/responsive browser proof | **FAIL / P1** | `AccessibleWorkstationShell` — READY TO PATCH |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 2. Audit invariant

Missing, stale, parse-failed, timed-out, unauthenticated, overloaded, contradictory or unproven evidence must never become PASS, LIVE, safe, fresh, zero-risk, zero-P&L, zero-Greek, calibrated confidence, broker-connected, deployed-current or trade-ready through defaults.

UI can display safety truth; it can never be its authority. Order/risk/safety checks must be enforced independently on the backend immediately before any state-changing paper or future live command.

## 3. Retained findings registry

- `AUTH-001..011` OPEN: login contract mismatch, browser API-key persistence, deterministic cookie token, no server revocation/expiry record, weak auth throttling, global secret injection and incomplete CSRF/idempotency proof.
- `MUT-001..008` OPEN: incomplete capability inventory, file-backed live approval, route-list idempotency, worker replay gaps, duplicated route authority and weak separation between HTTP auth and domain eligibility.
- `UI-001..019` OPEN: false-valid defaults, weak provenance/freshness, contradictory modes, zero/empty ambiguity, incomplete responsive/accessibility and deployment truth.
- `CHAIN-001..014` OPEN: null→zero parsing, incomplete Greeks/quotes, expiry-insensitive cache, weak persisted-cache provenance, source invention, parser-error collapse and weak runtime proof.
- `SCAN-001..010` OPEN: stale same-day rank acceptance, high-watermark carryover, stale restamping, duplicate REST/WS writers, auto-eligibility and load-heavy scanner behavior.
- `READY-001..009` OPEN: weak semantic lifecycle/risk/economic readiness, account-success ambiguity, evidence-poor approval and stale deployment assumptions.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN except corrected `PAPER-010` route-absence claim: process-local lifecycle, duplicate mutation risk, stale-price handling, incomplete costs/reconciliation and legacy control residue.
- `RISK-001..009` OPEN: browser/default risk limits, zero-risk fallbacks, weak VaR/ES contract, fail-open semantics and no independently proven canonical pre-trade wiring.
- `WS-001..011` OPEN/UNPROVEN: transport-open ≠ healthy stream, weak heartbeat/freshness, stale re-stamping, competing writers, malformed-event silence and fake WebSocket proof.
- `GCP-001..011` OPEN: exact revision/digest missing, IAM separation gaps, deployment mutation ambiguity, weak secret/runtime provenance and incomplete Render retirement.
- `STATE-001..012` OPEN: local-file authority/fallback, whole-snapshot overwrite, missing per-domain CAS, startup local promotion, plausible green defaults, mixed-generation state and weak multi-writer tests.
- `ML-001..014` OPEN: immutable prediction ledger absent, model-maturity misuse, score→confidence misuse, temporal validation leakage risk, calibration missing and no after-cost outcome linkage.
- `A11Y-001..012` OPEN: fixed shell, clipped Tier-0 truth, keyboard/focus/live-region issues and no exact browser proof.
- `PERF-001..009` OPEN: orphaned timed-out work, overlapping polls, chain stampede, overlapping paper ticks, false RSS telemetry, response buffering, event-loop blocking sync, batch fan-out and unbounded log-tail reads.
- `SAFE-001..008` OPEN from this iteration: kill-only order gate, split kill-switch authorities, analytics risk disconnected from order eligibility, scheduler-trigger bypass surface, contradictory live-gate semantics, approval/state authority weakness, missing canonical execution-decision evidence and legacy/default execution truth.

## 4. Latest deep slice — paper/live-adjacent execution path and hard safety gate

### SAFE-001 / P0 — `OrderManagement.create_order()` does not call authoritative pre-trade risk or SafetyTruth

**Exact proof:** `dashboard/backend/order_management.py::create_order()` calls `run_phase113()` and rejects only when that result is `KILL`; otherwise it appends a PENDING order to `outputs/orders.jsonl`. It does not call `PreTradeRiskService`, account/funds truth, broker/data freshness, option-chain quote quality, position limits, paper lifecycle state or deployment revision.

**Symptom/root cause:** the order abstraction treats “kill switch not active” as sufficient admission to create an order object. The kill monitor is a narrow emergency stop, not a complete execution-eligibility service.

**Real-money impact:** if this abstraction were reused by a future live route, a request could pass merely because the kill file says `kill=false`, even when risk/data/account/deployment truth is UNKNOWN or stale. In paper mode it can still corrupt readiness evidence by creating orders without canonical risk evidence.

**Exact files/functions likely to change:** `dashboard/backend/order_management.py::create_order`, `dashboard/backend/risk_management.py`, future `dashboard/backend/pretrade_risk_service.py`, `dashboard/backend/safety_truth.py`, paper mutation route/service and any live router adapter.

**World-class target behavior:** every order-intent command receives one immutable `ExecutionDecision` created immediately before mutation. Decision is `ALLOW_PAPER | DENY | UNKNOWN`; live execution remains hard-denied in this project posture.

**Minimal safe design:** replace direct order creation with `OrderIntent -> MutationPolicy -> SafetyTruth -> DataTruth -> AccountTruth -> PreTradeRiskService -> idempotent paper command ledger`. Kill switch remains one mandatory input, not the decision itself.

**Ordered implementation:** 1) introduce typed `OrderIntent`; 2) introduce `ExecutionEligibility`; 3) require canonical snapshot IDs for market/chain/account/risk; 4) require idempotency and correlation IDs; 5) call `PreTradeRiskService`; 6) append immutable decision evidence; 7) only then enqueue paper mutation; 8) prohibit broker live adapter invocation.

**Schema/API:** `ExecutionDecision {decision_id, intent_id, capability, mode, safety_state, kill_state, account_state, market_state, quote_state, risk_state, reasons[], source_revisions{}, runtime_revision, evidence_id, decided_at}`.

**Migration/backward compatibility:** legacy `create_order()` may temporarily become a wrapper that always requires a passed-in `ExecutionDecision`; absence means DENY.

**Security/safety constraints:** UI cannot forge decision fields. Live capability remains disabled independently of decision contents.

**Regression risks:** stricter checks may block paper ticks during incomplete data; this is intended fail-closed behavior.

**Tests:** call order creation with kill OK but risk UNKNOWN, chain STALE, account ERROR, wrong revision and duplicate idempotency key; all must deny. Proven PAPER conditions with valid risk may create exactly one ledger command. Mock live broker adapter and assert zero calls.

**PASS:** no order/paper mutation is reachable without one server-generated immutable decision ID.

**Rollback/fail-safe:** disable mutation path and retain read-only analyzer UI.

**Status:** `READY TO PATCH`.

### SAFE-002 / P0 — two different kill-switch files create split safety authority

**Exact proof:** `dashboard/backend/order_management.py` imports `core.engine.system3_phase113_kill_switch_monitor.run_phase113()`. That monitor reads `storage/live/kill_switch.json`. Separately, `/api/live-trading/approve` in `dashboard/backend/app.py` writes approval fields to `config/kill_switch.json`.

**Symptom/root cause:** emergency-stop state and human live-approval state live in different files with different owners and schemas. Neither is a typed, revision-bound shared SafetyTruth record.

**Real-money impact:** operators and code can believe they are looking at one “kill switch” while different execution paths read different files. File locality also makes Cloud Run multi-instance/restart truth unsafe.

**Exact files:** `core/engine/system3_phase113_kill_switch_monitor.py`, `dashboard/backend/order_management.py`, `dashboard/backend/app.py:/api/live-trading/approve`, both kill-switch JSON locations, deployment/state-store code.

**Target:** one canonical backend-owned `SafetyTruth` record with explicit fields for emergency stop, analyzer/paper/live capability, approval state, policy revision, runtime revision, source and evidence IDs.

**Implementation:** 1) define SafetyTruth schema; 2) make emergency kill fail-closed and authoritative in shared store; 3) migrate approval into a separate append-only approval event referenced by SafetyTruth; 4) prohibit direct file reads in execution code; 5) leave local files diagnostic-only during migration.

**Schema:** `SafetyTruth {state: UNKNOWN|SAFE_PAPER|KILLED|ERROR, emergency_kill, live_capability: LOCKED, approval_ref?, policy_revision, updated_at, runtime_revision, evidence_id}`.

**Compatibility:** read both legacy files only through a migration adapter that returns UNKNOWN on disagreement.

**Tests:** conflicting files => SafetyTruth UNKNOWN/KILLED, never ALLOW; missing/corrupt file => KILLED/ERROR; restart/multi-instance consistency test.

**PASS:** exactly one authoritative safety record is consumed by every mutation service; file disagreement cannot produce green.

**Rollback:** force KILLED and disable mutations.

**Status:** `READY TO PATCH`.

### SAFE-003 / P0-P1 — current `RiskManagement` is analytics, not an independently enforced pre-trade gate

**Exact proof:** `dashboard/backend/risk_management.py` calculates VaR/ES/exposure and `check_risk_limits()`, using fallback limits (`max_positions=5`, `max_exposure=100000`, `max_loss=-5000`, concentration=50%) and returning PASS when no breaches exist. When positions/returns are missing it produces numeric zero risk. `OrderManagement.create_order()` does not call it.

**Root cause:** dashboard risk computation and transaction admission are separate concepts but no canonical PreTradeRiskService bridges them. Missing inputs collapse to plausible numerical values.

**Impact:** a risk panel can show low/zero risk while execution eligibility is actually UNKNOWN; a future order path can bypass risk entirely.

**Files:** `dashboard/backend/risk_management.py`, risk endpoints/components, `order_management.py`, paper engine, future broker router.

**Target:** immutable server policy + explicit input-quality validation. Risk decision must return `PASS | FAIL | UNKNOWN | ERROR`, never infer PASS from absent positions/returns/Greeks/account data.

**Implementation:** 1) move limits into versioned server `RiskPolicy`; 2) require AccountTruth/PositionTruth/QuoteTruth; 3) validate numeric completeness; 4) compute exposures/scenarios; 5) issue `RiskDecision`; 6) execution service accepts only explicit PASS for PAPER and hard-denies LIVE.

**Tests:** missing positions source, missing Greeks, stale account, malformed limits and insufficient history must return UNKNOWN/ERROR, not zero PASS. Policy boundary tests and position-concentration scenarios required.

**PASS:** no mutation service can instantiate an order without a server risk decision from the same state generation.

**Rollback:** risk UNKNOWN => mutation inhibited.

**Status:** `READY TO PATCH`.

### SAFE-004 / P0-P1 — scheduler API can trigger arbitrary configured jobs via GET/POST using a query-string secret

**Exact proof:** `dashboard/backend/app.py` exposes `@app.api_route('/api/scheduler/run/{job_id}', methods=['GET','POST'])`. It accepts `secret: Optional[str]` as a query parameter, verifies it against `SCHEDULER_SECRET`, loads any matching enabled/configured job ID, and starts `run_single_job(job_id)` in a background task.

**Symptom/root cause:** a state-changing scheduler trigger supports GET and transports a reusable secret in the URL. Job authorization is based on possession of one shared secret and config membership, not a typed capability or per-job safety classification.

**Real-money impact:** URLs can leak through browser history, proxy/access logs and monitoring. More importantly, if any configured job is or becomes paper/live-adjacent, the scheduler path can bypass the dashboard SessionTruth/CSRF/idempotency/PreTradeRiskService boundary.

**Exact files:** `dashboard/backend/app.py:trigger_scheduler_job`, `core/engine/system3_phase82_job_scheduler.py`, scheduler config, GCP Scheduler/IAM deployment code, `MutationPolicy`.

**Target:** no GET mutations; Google Cloud Scheduler invokes a POST endpoint using IAM/OIDC identity or a dedicated non-browser worker identity. Every job declares capability `READ_ONLY | DATA_REFRESH | PAPER_MUTATION | ADMIN`; paper mutation enters the same command/risk/safety gate as UI/API requests.

**Implementation:** 1) remove GET; 2) remove URL secrets; 3) use OIDC/service-account auth; 4) introduce job capability allowlist; 5) add event/job idempotency; 6) block unknown capability; 7) route paper jobs through canonical mutation queue; 8) permanently reject LIVE_MUTATION.

**Tests:** GET => 405; missing/invalid OIDC => deny; unknown job capability => deny; duplicate Scheduler delivery => one logical job; paper-adjacent job without current SafetyTruth/RiskDecision => inhibit.

**PASS:** no scheduler-triggered state change can bypass capability, replay and domain-safety checks.

**Rollback:** disable remote job trigger and run only explicitly safe read/data jobs through internal worker schedule.

**Status:** `READY TO PATCH`.

### SAFE-005 / P1 — live-gate wording can imply readiness although execution authority is elsewhere and hard-locked

**Exact proof:** the live-gate response in `dashboard/backend/app.py` returns `verdict='LIVE_TRADING_ALLOWED'` when its local gate list passes and message `All gates pass — ready for live trading after human approval`. Elsewhere `/api/health` forces `live_allowed=False`, and the approval endpoint separately records approval while saying an environment change would still be required.

**Root cause:** several partial gates independently express “live” semantics without one canonical typed authority.

**Impact:** UI/operator contradiction: one panel may state LIVE_TRADING_ALLOWED while global runtime remains locked. This is unacceptable for an institutional trading workstation.

**Files/components:** live-gate endpoint, health/state endpoints, TopBar/Readiness/Proof views, approval endpoint, SafetyTruth service.

**Target:** only SafetyTruth may emit execution capability. Readiness gates emit evidence states, never `LIVE_TRADING_ALLOWED`.

**Implementation:** rename gate output to `evidence_state = PASS|FAIL|UNKNOWN`; expose `execution_capability=LOCKED` separately from SafetyTruth; UI shows `EVIDENCE PASS` and `LIVE LOCKED` simultaneously when appropriate.

**Tests:** even with all readiness evidence mocked PASS, analyzer deployment must still report LIVE LOCKED and live mutation must return hard denial.

**PASS:** no endpoint except SafetyTruth owns execution-capability wording.

**Rollback:** force all live labels to LOCKED/NOT AUTHORIZED.

**Status:** `READY TO PATCH`.

### SAFE-006 / P1 — live approval is persistent file mutation but not an execution decision

**Exact proof:** `/api/live-trading/approve` requires a phrase, then writes `live_trading_approved`, the phrase, timestamp and note into `config/kill_switch.json`. The response itself says approval does not enable live trading.

**Root cause:** human approval, deployment configuration and execution eligibility are conflated in one config artifact rather than modeled as independent evidence.

**Impact:** stale approval can survive code/config changes and can be interpreted by future code without proving source SHA, runtime revision, policy revision, account/risk state or expiry.

**Target:** append-only `ApprovalEvidence` with principal/session, issued/expiry times, policy/runtime/source revisions and explicit scope. SafetyTruth references it but still independently enforces LIVE LOCKED for analyzer builds.

**Tests:** approval from old SHA/revision or expired approval cannot satisfy current gate; approval cannot alter router lock; approval secret/phrase never appears in exported logs/UI.

**PASS:** approval is evidence only, not mutable kill/config truth and not router authority.

**Rollback:** ignore all legacy approval fields and keep LIVE LOCKED.

**Status:** `READY TO PATCH`.

### SAFE-007 / P1 — execution evidence is not correlation-complete across order, risk, lifecycle and audit

**Exact proof:** `OrderManagement` creates time-derived order IDs and appends JSON lines. `app.py::log_event()` separately creates short event IDs from current time + event type. Neither proof shows immutable linkage among candidate/snapshot, order intent, risk decision, paper fill, position and reconciliation.

**Root cause:** IDs are generated independently at each layer rather than from one command/lifecycle correlation model.

**Impact:** an operator cannot prove which exact market snapshot/risk decision caused one order/fill or detect duplicate/replayed mutation with confidence.

**Target:** immutable identifiers: `correlation_id`, `intent_id`, `decision_id`, `command_id`, `order_event_id`, `fill_id`, `position_id`, `reconciliation_id`, all carrying runtime/source revisions and evidence IDs.

**Implementation:** build append-only lifecycle event schema; every later event references parent IDs; never rewrite issued prediction/risk/order evidence.

**Tests:** full paper lifecycle trace must be reconstructible from one correlation ID; duplicate command produces no duplicate logical fill; restart replay preserves IDs.

**PASS:** every paper P&L row is traceable back to exact candidate/data/risk evidence.

**Rollback:** disable mutation if evidence ledger unavailable.

**Status:** `READY TO PATCH`.

### SAFE-008 / P1 — several read models still generate plausible default safety/market values that cannot feed execution decisions

**Exact proof:** `app.py` contains numerous slim/fallback helpers that default mode to PAPER, live flags false, P&L/rank fields to zero/empty and state calls to fallback payloads when upstream calls time out. This is acceptable only as UI degradation if clearly typed; it is unsafe if reused as execution input.

**Root cause:** read-model compatibility defaults are not formally separated from mutation-authority contracts.

**Impact:** future code may accidentally consume UI-compatible zeros/defaults as real account/risk/market truth.

**Target:** `DisplayProjection` objects are explicitly non-authoritative. Mutation services accept only strongly typed Truth/Decision objects and reject plain dashboard DTOs.

**Implementation:** create separate schemas/modules and type boundaries; mark fallback projections with `quality=UNKNOWN|STALE|ERROR`; prohibit imports from dashboard projection helpers into execution services via architecture tests.

**Tests:** static dependency test plus runtime validation that a dashboard DTO cannot instantiate PreTradeRiskService inputs.

**PASS:** UI fallback data has no code path into order eligibility.

**Rollback:** mutation disabled whenever authoritative truth contract unavailable.

**Status:** `READY TO PATCH`.

## 5. Canonical solution — `SOL-19 SafetyTruth + ExecutionEligibility + PreTradeRiskService`

**Status:** `READY TO PATCH`.

### Authoritative pipeline

`OrderIntent / PaperTick / SchedulerCommand`
→ `MutationPolicy`
→ `SafetyTruth`
→ `DeploymentTruth`
→ `StateTruth generation`
→ `StreamTruth / OptionChainTruth / AccountTruth`
→ `PreTradeRiskService`
→ immutable `ExecutionDecision`
→ idempotent single paper mutation worker
→ order/fill/position ledger
→ reconciliation/P&L provenance.

LIVE is a separate capability and remains `LOCKED` regardless of readiness evidence.

### Required server contracts

- `SafetyTruth`: `UNKNOWN | SAFE_PAPER | KILLED | ERROR`, emergency kill, live capability LOCKED, policy/runtime revision, evidence ID.
- `RiskPolicy`: immutable versioned limits and scenarios.
- `RiskDecision`: `PASS | FAIL | UNKNOWN | ERROR`, input revisions and reasons.
- `ExecutionDecision`: complete decision bundle bound to one intent and state generation.
- `ApprovalEvidence`: append-only, scoped, expiring, revision-bound; never router authority.
- `LifecycleEvent`: immutable correlation/event IDs for command/order/fill/position/reconciliation.

### Ordered implementation

1. Create `SafetyTruth` service backed by shared state; legacy kill files become migration inputs only.
2. Make conflicting/missing kill state fail closed.
3. Create immutable server `RiskPolicy` and `PreTradeRiskService`.
4. Introduce `OrderIntent`, `ExecutionDecision` and correlation IDs.
5. Refactor `OrderManagement.create_order()` to require a server decision.
6. Route `/api/paper/tick` through idempotent serialized command processing.
7. Remove scheduler GET trigger/query secret; use GCP IAM/OIDC and per-job capabilities.
8. Replace live-gate `LIVE_TRADING_ALLOWED` wording with evidence-only state.
9. Convert live approval to expiring append-only evidence, not config mutation.
10. Add architecture tests prohibiting dashboard read DTOs/direct broker adapters in mutation services.
11. Keep all live broker mutation adapters disabled/unwired.

### Exact closure tests

- Kill file disagreement, absence or corruption => KILLED/UNKNOWN; zero mutation.
- Kill OK + risk UNKNOWN => deny.
- Risk PASS + stale quote/account/stream => deny.
- 20 duplicate paper commands => one logical lifecycle.
- Scheduler duplicate delivery => one command; GET rejected.
- All readiness gates PASS => LIVE remains LOCKED in analyzer build.
- Old/expired approval => does not satisfy current SafetyTruth.
- Attempt to call broker place/modify/cancel in test harness => mock call count remains zero.
- Restart/multi-instance test => identical SafetyTruth and decision outcome for same state generation.
- Every realized paper P&L row traces to intent, decision, fill and reconciliation evidence IDs.

**PASS:** no paper/live-adjacent state mutation can occur without exact-revision server safety+risk evidence, and live broker mutation remains unreachable.

## 6. Regression checks this iteration

- Application/source SHA remains `b70af343...`; no application changes were merged during the audit-report loop.
- PR #97 remains open and cannot close synthetic-P&L findings on main.
- Exact application-head workflow runs remain absent.
- `OrderManagement` still uses the Phase113 kill monitor as its only explicit admission check.
- Phase113 kill monitor remains fail-closed on read/parse exception — **positive foundation retained**.
- RiskManagement still returns numerical zero on missing data and default policy values and is not proven wired to order admission.
- `/api/live-trading/approve` remains file-backed evidence, not router authority.
- `/api/scheduler/run/{job_id}` remains GET/POST with query secret and background job execution.
- LIVE remains prohibited by audit policy; nothing was enabled, placed, modified, cancelled or routed.

## 7. Findings upgraded/downgraded/closed

- `SAFE-001..008`: NEW, all `FIX-REQUIRED`; `SAFE-001/002/003/004` are P0 or P0-P1.
- Existing `RISK-006/007` canonical-wiring concern is **upgraded in confidence** because `OrderManagement.create_order()` was directly inspected and contains no PreTradeRiskService call.
- Existing `MUT` route inventory concern is **upgraded** by direct scheduler trigger inspection.
- `PAPER-010` remains CLOSED/CORRECTED only for the old route-absence claim; the real `/api/paper/tick` concurrency/lifecycle risk remains open under `PERF-004` and paper findings.
- No safety, risk, readiness or deployment finding is CLOSED this iteration.

## 8. Prioritized remediation roadmap

### P0

1. `SessionTruth`: fix login contract; remove raw reusable API key from browser; enforce server expiry/revocation.
2. `MutationPolicy + CapabilityManifest`: generated route inventory, CSRF/replay/capability enforcement.
3. `SOL-19 SafetyTruth + ExecutionEligibility + PreTradeRiskService`.
4. Remove split kill-switch authority and make shared safety state fail closed.
5. Serialize/idempotently ledger every paper mutation; no free-form background `engine.step()`.
6. `DeploymentTruth` exact SHA→digest→Cloud Run revision proof.
7. `StateTruth` domain-CAS shared authority.
8. Bounded `WorkCoordinator` so overloaded truth services cannot fabricate freshness.

### P1

1. `OptionChainTruth` + per-symbol/expiry singleflight.
2. `StreamTruth` heartbeat/event-age/order validation.
3. `ScannerTruth` latest-observation semantics and stale-row eviction.
4. Replace scheduler URL secret with GCP IAM/OIDC and explicit job capabilities.
5. Durable paper lifecycle/reconciliation/after-cost P&L.
6. `PredictionTruth` model/data/cutoff/calibration ledger.
7. Exact responsive/accessibility/browser-console proof.
8. Retire all Render-era operational comments/instructions from active runtime code/docs.

### P2

- Institutional analytics, advanced drilldowns and tuning controls only after authoritative P0/P1 truth contracts are proven.

## 9. Independent verification counters

Counters advance only on independent reproduction.

- `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`; other AUTH findings remain below 20.
- `UI-001` advances to `20/20` by another independent direct source slice, but **is NOT auto-closed**: counter completion means reproducibility only; closure still requires patched exact-revision evidence. Mark `UI-001 LOCKED-20X / FIX-REQUIRED`.
- `UI-005 17/20`, `UI-007 13/20`, `UI-016 14/20`.
- `RISK canonical-wiring finding` advances by one independent direct execution-path reproduction; remains below 20.
- `MUT scheduler/capability inventory` advances by one independent direct route reproduction; remains below 20.
- `SAFE-001..008 1/20`.
- `PERF-001..009` remain below 20.
- `PAPER-010 route-absence` remains CLOSED/CORRECTED and cannot be LOCKED.
- **Only `UI-001` reaches LOCKED-20X reproducibility; it remains FIX-REQUIRED, not CLOSED.**

## 10. Product-design track — Execution Safety & Risk Control V18

This iteration's product visual belongs to the real `Portfolio & Risk / Readiness` workstation surface, not an audit-status page.

### REQUIRED

- Tier-0 market/session, Dhan, stream age, PAPER mode and LIVE LOCKED.
- One server `ExecutionEligibility` card showing `UNKNOWN/INHIBITED/PASS` with evidence IDs.
- Emergency kill state from canonical SafetyTruth, not local files.
- RiskPolicy revision, account generation, quote/chain snapshot and source age.
- Per-intent decision timeline: intent → safety → data → account → risk → paper command → fill/reconciliation.
- Scheduler command source/capability/idempotency visibility.
- Approval evidence shown separately from router state.
- No button can enable LIVE; live router remains locked.

### RECOMMENDED

- Scenario shocks, concentration/liquidity/Greeks exposure, risk reason drilldowns, rejected duplicate/stale commands and evidence export with redaction.

### OPTIONAL

- Advanced what-if optimizers only after they cannot modify policy or execution capability.

## 11. Closure discipline

`LOCKED-20X` means a finding reproduced independently 20 times; it does not mean fixed. CLOSED requires a patch on an exact source revision, exact runtime/deployment proof where applicable, required tests, reproducible evidence IDs and independent verification. Trade-readiness/profitability/live safety may never be inferred from UI labels or counters.

## 12. Next deep slice

Paper ledger and reconciliation internals: inspect `cloud_paper_engine`, position-close mutation, fills, P&L cost/slippage/tax treatment, restart/replay behavior and whether any manual/legacy close path can mutate positions without the new canonical correlation/idempotency/risk evidence model.