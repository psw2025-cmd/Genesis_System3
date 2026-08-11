# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 15:56 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `b69f2a483f32406f7998f37d03f304c6ee231730`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after application HEAD remain audit-report commits only; no newer application implementation was promoted into this evidence baseline.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`.
- PR #96 remains the newest merged application/UI PR identified in current evidence.
- GitHub returned no workflow runs for exact application SHA `b70af343...`; exact-revision CI/runtime readiness remains **NOT PROVEN**.
- Google Cloud remains the only accepted deployment target. Render-era instructions are migration debt, not operational authority.
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
| Paper lifecycle/reconciliation | **FAIL / P0** | `SOL-20 PaperLedger + ReconciliationService` — READY TO PATCH |
| Pre-trade risk authority | **FAIL / P0** | `PreTradeRiskService` mandatory for every paper/live-adjacent mutation |
| AI/prediction provenance | **MISSING / P0-P1** | `PredictionTruth` — READY TO PATCH/DESIGN |
| Accessibility/responsive browser proof | **FAIL / P1** | `AccessibleWorkstationShell` — READY TO PATCH |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 2. Audit invariant

Missing, stale, parse-failed, timed-out, unauthenticated, overloaded, contradictory, corrupt or unproven evidence must never become PASS, LIVE, safe, fresh, zero-risk, zero-P&L, zero-Greek, calibrated confidence, broker-connected, deployed-current or trade-ready through defaults.

Files and dashboard DTOs are projections only. They must never be transaction authority. Every paper/live-adjacent state mutation must be backed by immutable server-issued decision/event IDs. UI can display safety truth; it can never be its authority.

## 3. Retained findings registry and canonical solutions

- `AUTH-001..011` OPEN: login contract mismatch, browser API-key persistence, deterministic cookie token, no server revocation/expiry record, weak auth throttling, global secret injection and incomplete CSRF/idempotency proof. Canonical solution: `SessionTruth`.
- `MUT-001..008` OPEN: incomplete capability inventory, file-backed live approval, route-list idempotency, worker replay gaps, duplicated route authority and weak separation between HTTP auth and domain eligibility. Canonical solution: `MutationPolicy + CapabilityManifest`.
- `UI-001..019` OPEN: false-valid defaults, weak provenance/freshness, contradictory modes, zero/empty ambiguity, incomplete responsive/accessibility and deployment truth. `UI-001` is `LOCKED-20X / FIX-REQUIRED`, not closed.
- `CHAIN-001..014` OPEN: null→zero parsing, incomplete Greeks/quotes, expiry-insensitive cache, weak persisted-cache provenance, source invention, parser-error collapse and weak runtime proof. Canonical solution: `OptionChainTruth`.
- `SCAN-001..010` OPEN: stale same-day rank acceptance, high-watermark carryover, stale restamping, duplicate REST/WS writers, auto-eligibility and load-heavy scanner behavior. Canonical solution: `ScannerTruth`.
- `READY-001..009` OPEN: weak semantic lifecycle/risk/economic readiness, account-success ambiguity, evidence-poor approval and stale deployment assumptions.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` remain OPEN except corrected `PAPER-010` route-absence claim. Earlier paper findings remain covered by immutable lifecycle/reconciliation design below.
- `RISK-001..009` OPEN: browser/default risk limits, zero-risk fallbacks, weak VaR/ES contract, fail-open semantics and no independently proven canonical pre-trade wiring. Canonical solution: `PreTradeRiskService`.
- `WS-001..011` OPEN/UNPROVEN: transport-open ≠ healthy stream, weak heartbeat/freshness, stale restamping, competing writers, malformed-event silence and fake WebSocket proof. Canonical solution: `StreamTruth`.
- `GCP-001..011` OPEN: exact revision/digest missing, IAM separation gaps, deployment mutation ambiguity, weak secret/runtime provenance and incomplete Render retirement. Canonical solution: `DeploymentTruth`.
- `STATE-001..012` OPEN: local-file authority/fallback, whole-snapshot overwrite, missing per-domain CAS, startup local promotion, plausible green defaults, mixed-generation state and weak multi-writer tests. Canonical solution: `StateTruth + domain CAS`.
- `ML-001..014` OPEN: immutable prediction ledger absent, model-maturity misuse, score→confidence misuse, temporal validation leakage risk, calibration missing and no after-cost outcome linkage. Canonical solution: `PredictionTruth + ModelArtifactManifest`.
- `A11Y-001..012` OPEN: fixed shell, clipped Tier-0 truth, keyboard/focus/live-region issues and no exact browser proof. Canonical solution: `AccessibleWorkstationShell`.
- `PERF-001..009` OPEN: orphaned timed-out work, overlapping polls, chain stampede, overlapping paper ticks, false RSS telemetry, response buffering, event-loop blocking sync, batch fan-out and unbounded log-tail reads. Canonical solution: `WorkCoordinator + SnapshotScheduler`.
- `SAFE-001..008` OPEN: kill-only order gate, split kill-switch authorities, analytics risk disconnected from order eligibility, scheduler-trigger bypass surface, contradictory live-gate semantics, approval/state authority weakness, missing canonical execution-decision evidence and legacy/default execution truth. Canonical solution: `SafetyTruth + ExecutionEligibility + PreTradeRiskService`.

## 4. Latest deep slice — paper lifecycle, manual close, restart/replay and P&L provenance

### PAPER-017 / P0 — manual close mutates `positions_live.json` outside the paper engine ledger

**Exact proof:** `dashboard/backend/app.py::close_position(position_id)` reads `outputs/positions_live.json`, changes the matching row to `CLOSED`, sets `exit_reason=MANUAL_CLOSE`, sets `exit_price` from `current_price`/`entry_price`, then removes all CLOSED rows and directly rewrites the JSON file. It does not call `CloudPaperEngine`, `PreTradeRiskService`, an idempotent command queue or reconciliation service.

**Symptom/root cause:** the UI/API projection file is being treated as transaction authority. Manual close is implemented as file surgery rather than a lifecycle command.

**Real-money/readiness impact:** a manual close can disappear from engine memory and from realized-P&L history; the next engine tick can re-publish its own still-open in-memory position and effectively resurrect the manually removed row. The response says “marked for closure” although the row is immediately removed from the projection.

**Files/functions likely to change:** `dashboard/backend/app.py::close_position`, `dashboard/backend/cloud_paper_engine.py`, future `paper_command_service.py`, `pretrade_risk_service.py`, frontend Paper/Positions controls.

**World-class target:** `ClosePositionIntent` is authenticated, CSRF/idempotency protected, bound to one current position generation and fresh quote, risk/safety checked, then serialized through the same paper mutation worker as opens/exits.

**Minimal safe design / steps:** 1) remove direct JSON mutation; 2) POST close intent with idempotency key and expected position revision; 3) validate SessionTruth/MutationPolicy/SafetyTruth; 4) require fresh quote/chain truth; 5) issue `ExecutionDecision`; 6) append `CLOSE_INTENT`; 7) append simulated fill and `POSITION_CLOSED`; 8) rebuild projection files from ledger.

**Schema/API:** `ClosePositionIntent {intent_id, correlation_id, position_id, expected_position_revision, reason, idempotency_key}`; response returns command/decision state, never a fabricated fill.

**Migration/compatibility:** keep the route path temporarily but change semantics to command submission. Projection files become read-only compatibility outputs.

**Safety/security:** manual close must never invoke a live broker API in analyzer/paper mode; LIVE capability stays hard-locked.

**Regression risks:** existing UI may expect immediate disappearance; replace with `CLOSE_PENDING` then confirmed close event.

**Tests / PASS:** 20 duplicate close requests produce one close event; stale position revision rejects; missing quote/risk truth inhibits; restart between close intent and fill replays exactly once; no direct write to positions projection from route code.

**Rollback/fail-safe:** disable manual mutation and keep read-only position display.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-018 / P0 — manual close can be overwritten by the engine's separate in-memory/state-file authority

**Exact proof:** `CloudPaperEngine` loads `paper_engine_state.json` into `self.open_positions` and later `_write_outputs()` rewrites `positions_live.json` from `self.open_positions`. The manual-close route modifies only `positions_live.json`; it does not update `paper_engine_state.json` or `self.open_positions`.

**Root cause:** two mutable authorities exist for the same position lifecycle: engine state and dashboard projection file.

**Impact:** lost update/resurrection, inconsistent P&L and misleading UI state after a later tick/restart.

**Files:** `cloud_paper_engine.py::_load_state/_save_state/_write_outputs`, `app.py::close_position`, state-store/reconciliation service.

**Target/design:** one append-only ledger is authoritative; engine memory and JSON files are rebuildable projections keyed by immutable event sequence and position revision.

**Implementation:** introduce event store; give each position a monotonic revision; projection writer consumes committed events; forbid direct position-file mutation; detect projection generation mismatch.

**Compatibility:** legacy files may be imported once through a migration tool with explicit evidence/generation and then frozen as historical artifacts.

**Tests / PASS:** manual close followed by engine tick/restart can never reopen the same lifecycle; projection reconstruction from ledger is deterministic.

**Rollback:** ledger unavailable => paper mutation inhibited; read-only last-good projection marked STALE.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-019 / P0-P1 — corrupt/missing paper engine state silently becomes an empty portfolio

**Exact proof:** `CloudPaperEngine._load_state()` catches any exception and silently initializes `open_positions=[]`, `closed_positions=[]`, `seq=0`, `session_date=''`. `_save_state()`, `_append_trade_csv()` and `_write_outputs()` also swallow exceptions.

**Root cause:** persistence failures are treated as absence rather than `LEDGER_ERROR`.

**Impact:** corrupted/unwritable state can appear as a healthy empty portfolio, lose open/closed lifecycle evidence and later overwrite projections with empty/partial truth.

**Files:** `cloud_paper_engine.py` persistence methods; observability/readiness UI.

**Target/design:** durable ledger errors are first-class. No write acknowledgement is emitted until event persistence succeeds. Corrupt state causes `LEDGER_ERROR`, `PAPER_MUTATION_INHIBITED`, and explicit recovery workflow.

**Implementation:** stop broad exception swallowing; typed persistence errors; checksummed/versioned snapshots; append-only event commit before projection; atomic snapshot checkpoint; metrics/alerts for write/read failures.

**Migration:** attempt one forensic import of old state/CSV files; never auto-promote unreadable files to empty.

**Tests / PASS:** malformed JSON, permission denied, disk-full/mock write failure and interrupted snapshot all inhibit mutations and surface ERROR; none yields `open_count=0` as proven truth.

**Rollback:** read-only last-good snapshot with STALE watermark and zero mutation.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-020 / P1 — daily reset destroys active/closed in-memory lifecycle continuity and resets sequence IDs

**Exact proof:** `_reset_if_new_day()` replaces `open_positions` and `closed_positions` with empty lists and resets `seq=0` whenever stored `session_date` differs from today. New positions use IDs such as `POS_0001` derived only from that resettable sequence.

**Root cause:** date rollover is modeled as destructive state reset rather than session boundary/reconciliation event.

**Impact:** unreconciled positions can disappear across date change; closed history is no longer available to engine state; position IDs can repeat across days, weakening correlation and replay safety.

**Files:** `cloud_paper_engine.py::_reset_if_new_day`, position-ID creation, reconciliation/UI history.

**Target:** globally unique immutable IDs; session rollover appends `SESSION_CLOSED/SESSION_OPENED`; any open prior-session position must be explicitly reconciled or marked orphaned before new mutations.

**Implementation:** UUID/ULID IDs; preserve full event history; session ID independent from position ID; EOD reconciliation checkpoint; prohibit silent reset when positions remain unresolved.

**Tests / PASS:** restart/date rollover with an open position yields ORPHAN/RECONCILE_REQUIRED, not disappearance; IDs never repeat across 20 simulated days.

**Rollback:** if rollover cannot reconcile, freeze mutations and retain prior positions as unresolved.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-021 / P1 — paper engine has no immutable order/fill objects; LTP is treated as entry/exit price

**Exact proof:** when opening a position, `entry_price` is simply `round(best['ltp'], 2)`. On close, `exit_price` is the current chain LTP. The CSV contains OPEN/CLOSE rows but there is no immutable order event, fill ID, quote event ID, bid/ask/depth snapshot, fill timestamp provenance or parent correlation chain.

**Root cause:** position simulation skips explicit order→fill lifecycle.

**Impact:** slippage/liquidity behavior cannot be reproduced or audited; duplicate fills cannot be detected; PredictionTruth and risk evidence cannot be linked to realized outcome.

**Files:** `cloud_paper_engine.py::step/_append_trade_csv`, scanner/chain truth, future paper ledger.

**Target/design:** `PAPER_ORDER_ACCEPTED -> PAPER_FILL -> POSITION_OPENED`, and corresponding close lifecycle. Fill model consumes a specific quote snapshot and records model revision.

**Implementation:** canonical order/fill schemas, parent IDs, immutable event timestamps, quote snapshot IDs, deterministic fill model and idempotent commit.

**Tests / PASS:** every position has exactly one opening fill; every closed position has exactly one closing fill; all fills trace to quote and decision evidence.

**Rollback:** no valid quote/fill model => command remains pending/rejected; never synthesize a hidden fill.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-022 / P1 — after-cost P&L is opaque and policy/version provenance is absent

**Exact proof:** `_compute_net_pnl()` hard-codes brokerage, STT, exchange transaction charge, GST and `SLIPPAGE_PCT`. It returns only one net number. `_write_outputs()` stores aggregate realized/unrealized P&L but no cost components, rate-policy version, quote/fill provenance or model revision.

**Root cause:** cost assumptions are module constants rather than a versioned `CostPolicy` attached to each fill/valuation.

**Impact:** economic validation cannot prove which fee/slippage assumptions produced a reported net P&L; historical results can silently change when constants change.

**Files:** `cloud_paper_engine.py::_compute_net_pnl/_write_outputs`, Performance/P&L UI, future `cost_policy.py`.

**Target:** `gross_pnl`, brokerage, taxes/fees, modeled slippage, total costs and net P&L are separately stored with policy revision and calculation evidence ID. Current regulatory/broker rates must be updated only through a versioned policy, not ad hoc constants.

**Implementation:** create immutable CostPolicy; calculate per-fill and per-close components; persist components; aggregate only from closed ledger events; show gross/cost/net in UI.

**Migration:** old trades without components remain `COST_PROVENANCE_UNKNOWN`, never retroactively claimed proven without explicit recalculation artifact.

**Tests / PASS:** deterministic cost fixtures; sum(components)=total_cost; gross-total_cost=net; changing policy revision never rewrites old event values.

**Rollback:** if policy unavailable, mark P&L economic quality UNKNOWN and exclude from readiness evidence.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-023 / P1 — quantity source and P&L multiplier can diverge for unknown/equity underlyings

**Exact proof:** opening quantity uses `LOT_SIZES.get(best['underlying'], DEFAULT_EQUITY_LOT)` where `DEFAULT_EQUITY_LOT=1`; `_compute_net_pnl()` separately uses `LOT_SIZES.get(symbol, 50)`. For a symbol absent from `LOT_SIZES`, lifecycle quantity can be 1 while P&L is multiplied by 50.

**Root cause:** quantity is recomputed from an independent fallback instead of using the actual fill quantity.

**Impact:** latent P&L distortion if the engine is reused for an unsupported/equity underlying. Current `/api/paper/tick` passes index chains and `include_equity=False`, so this is not claimed as currently realized equity P&L corruption; it is still unsafe reusable logic.

**Files:** `cloud_paper_engine.py::_compute_net_pnl` and open-position construction.

**Target/design:** P&L accepts actual signed fill quantity; instrument master/contract multiplier is captured once in the fill evidence and never inferred later.

**Tests / PASS:** arbitrary quantity/lot fixtures, including unknown symbol, must produce P&L from stored fill quantity exactly; no hidden fallback multiplier.

**Rollback:** unsupported instrument metadata => execution/paper fill inhibited.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

### PAPER-024 / P1 — no authoritative reconciliation chain between engine state, JSON projections, CSV trades and dashboard P&L

**Exact proof:** engine state is persisted in `paper_engine_state.json`; positions are separately projected to `positions_live.json`; P&L to `pnl_live.json` and `paper_pnl_summary.json`; trades append to `paper_trades_live.csv`. The engine does not prove one common generation/event sequence across all four artifacts, and the manual close route can alter one projection independently.

**Root cause:** several denormalized files are treated as semi-independent truth rather than projections of one event ledger.

**Impact:** restart/write failure/manual edits can make positions, trade history and P&L disagree without a canonical reconciliation verdict.

**Files:** all cloud-paper persistence paths, `get_positions`, `get_pnl`, state sync, Paper/Performance UI.

**Target/design:** `ReconciliationService` compares ledger event sequence, position state and P&L projection; publishes `RECONCILED | DRIFT | ERROR | UNKNOWN` with evidence ID. Only RECONCILED outcomes count toward readiness/economic statistics.

**Implementation:** event sequence high-watermark; deterministic reducers; projection revision IDs; startup replay; reconciliation after every command and before readiness aggregation; drift alert/drilldown.

**Tests / PASS:** delete/truncate/edit each projection independently and verify ledger replay restores it; inject duplicate event and ensure idempotent reducer; mismatched sequence must be DRIFT, never PASS.

**Rollback:** reconciliation failure => paper mutations inhibited, live already locked.

**Status:** `READY TO PATCH / FIX-REQUIRED`.

## 5. Canonical solution — `SOL-20 PaperLedger + ReconciliationService`

**Status:** `READY TO PATCH`.

### Authoritative lifecycle

`PaperCommand / ClosePositionIntent`
→ `MutationPolicy`
→ `SafetyTruth`
→ `DeploymentTruth + StateTruth generation`
→ `StreamTruth / OptionChainTruth / AccountTruth`
→ `PreTradeRiskService`
→ immutable `ExecutionDecision`
→ serialized/idempotent `PaperMutationWorker`
→ `PAPER_ORDER_ACCEPTED`
→ `PAPER_FILL`
→ `POSITION_OPENED/UPDATED/CLOSED`
→ `P&L valuation event`
→ `RECONCILIATION_CHECKPOINT`.

Files such as `positions_live.json`, `pnl_live.json`, `paper_pnl_summary.json` and CSV exports become projections only. No route edits them directly.

### Required event/contracts

- `PaperCommand {command_id, correlation_id, intent_id, decision_id, idempotency_key, capability, expected_generation, created_at}`.
- `PaperOrderEvent {order_event_id, command_id, instrument_id, side, qty, order_type, quote_snapshot_id, state}`.
- `PaperFill {fill_id, order_event_id, qty, fill_price, quote_snapshot_id, fill_model_revision, cost_policy_revision, filled_at}`.
- `PositionEvent {position_id, position_revision, parent_fill_id, state, event_id, event_time}`.
- `CostBreakdown {gross, brokerage, taxes_fees, slippage, total_cost, net, policy_revision}`.
- `ReconciliationTruth {state: RECONCILED|DRIFT|ERROR|UNKNOWN, ledger_seq, projection_generations, orphan_ids[], duplicate_ids[], evidence_id, checked_at}`.

### Ordered implementation

1. Add durable append-only event store and globally unique IDs.
2. Add one serialized paper mutation worker with command idempotency.
3. Refactor `/api/paper/tick` into command enqueue; no free-form background `engine.step()` mutation.
4. Refactor manual close into `ClosePositionIntent`; remove direct JSON writes.
5. Create explicit order/fill/position events bound to exact quote/decision evidence.
6. Replace P&L lot fallback with stored fill quantity/instrument metadata.
7. Introduce versioned `CostPolicy` and component-level after-cost P&L.
8. Replace destructive date reset with session-boundary and EOD reconciliation events.
9. Make state/projection write errors fatal to mutation authority, not silent empty state.
10. Build JSON/CSV/UI outputs only from deterministic ledger reducers.
11. Run reconciliation on startup, after each command and before readiness/economic aggregation.
12. Surface lifecycle, cost and reconciliation evidence in the real Paper workspace.

### Security/safety constraints

- LIVE broker adapters remain unreachable/unwired.
- UI cannot supply decision/risk/fill truth.
- Missing shared ledger, quote, risk, state or reconciliation truth => paper mutation inhibited.
- Every close/open command requires idempotency and expected revision/generation.
- No historical P&L may be counted as proven if cost/reconciliation provenance is UNKNOWN.

### Exact closure tests

- 20 duplicate paper ticks => one logical command/fill lifecycle.
- 20 duplicate manual closes => one closing fill/event.
- Restart between each lifecycle transition => deterministic replay, no duplicate fill.
- Corrupt `paper_engine_state.json`/projection => LEDGER_ERROR/DRIFT, never empty-green.
- Manual close then next tick => position remains closed; never resurrects.
- Date rollover with unresolved position => RECONCILE_REQUIRED, not silent reset.
- Projection deletion/truncation => deterministic regeneration from ledger.
- Cost fixture => gross - exact component sum = net and policy revision persists.
- Unsupported instrument metadata => fill inhibited; no fallback quantity multiplier.
- Mock all broker mutation adapters and assert place/modify/cancel call count remains zero.

**PASS:** every Paper UI position/P&L/history row is reconstructible from immutable event IDs, exact decision/data/cost revisions and a RECONCILED checkpoint.

**Rollback/fail-safe:** ledger/reconciliation unavailable => read-only degraded mode; paper mutations inhibited; LIVE remains locked.

## 6. Regression checks this iteration

- Application/source SHA remains `b70af343...`; no application change was merged during the report-only audit loop.
- PR #97 remains open and cannot close synthetic-P&L findings on `main`.
- Exact application-head workflow runs remain absent.
- `/api/paper/tick` still schedules a background `_run_tick()` that invokes `engine.step()` without command idempotency or serialization; `PERF-004` therefore still reproduces.
- `get_paper()` still labels the engine as `paper_cloud_sim` and states broker order endpoints are intentionally not called — positive paper/live separation foundation retained.
- `CloudPaperEngine` still performs atomic temp-file replacement for JSON outputs — positive single-file crash-safety foundation retained, but not lifecycle/reconciliation authority.
- Manual close still edits `positions_live.json` directly and does not update engine state.
- Persistence exceptions in the paper engine remain silently swallowed.
- LIVE remains prohibited; no live order was enabled, placed, modified, cancelled or routed.

## 7. Findings upgraded/downgraded/closed

- `PAPER-017..024`: NEW, all `FIX-REQUIRED`; `PAPER-017/018/019` are P0 or P0-P1.
- Existing `PERF-004` overlapping-paper-tick finding is independently reproduced again and advances to `2/20`.
- Existing paper reconciliation/correlation concerns are upgraded in confidence by direct inspection of `cloud_paper_engine.py` and manual close route.
- Positive foundation: cloud paper engine explicitly states PAPER ONLY and no broker order calls; this does not close lifecycle correctness.
- `PAPER-010` remains CLOSED/CORRECTED only for the earlier route-absence claim.
- No readiness, profitability, reconciliation or deployment finding is closed in this iteration.

## 8. Prioritized remediation roadmap

### P0

1. `SessionTruth`: fix login contract; remove raw reusable API key from browser; enforce server expiry/revocation.
2. `MutationPolicy + CapabilityManifest`: generated route inventory, CSRF/replay/capability enforcement.
3. `SafetyTruth + ExecutionEligibility + PreTradeRiskService`.
4. `SOL-20 PaperLedger + ReconciliationService`: eliminate direct file mutation and free-form engine-step lifecycle authority.
5. Remove split kill-switch authority and make shared safety state fail closed.
6. `DeploymentTruth` exact SHA→digest→Cloud Run revision proof.
7. `StateTruth` domain-CAS shared authority.
8. Bounded `WorkCoordinator` so overloaded truth services cannot fabricate freshness.

### P1

1. `OptionChainTruth` + per-symbol/expiry singleflight.
2. `StreamTruth` heartbeat/event-age/order validation.
3. `ScannerTruth` latest-observation semantics and stale-row eviction.
4. Versioned paper `CostPolicy`, explicit fills and component-level after-cost P&L.
5. Replace scheduler URL secret with GCP IAM/OIDC and explicit job capabilities.
6. `PredictionTruth` model/data/cutoff/calibration ledger linked to reconciled after-cost paper outcomes.
7. Exact responsive/accessibility/browser-console proof.
8. Retire remaining Render-era operational comments/instructions.

### P2

Institutional analytics, advanced drilldowns and tuning controls only after authoritative P0/P1 truth contracts are proven.

## 9. Independent verification counters

Counters advance only on independent reproduction.

- `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`; other AUTH findings remain below 20.
- `UI-001` remains `LOCKED-20X / FIX-REQUIRED`; counter completion proves reproducibility only, not closure.
- `UI-005 17/20`, `UI-007 13/20`, `UI-016 14/20` remain unchanged this slice.
- `PERF-004` advances to `2/20` by independent direct reproduction of the non-idempotent background paper-tick path.
- `PAPER-017..024 1/20` each.
- `PAPER-010 route-absence` remains CLOSED/CORRECTED and cannot be LOCKED.
- No new finding reaches `LOCKED-20X` this iteration.

## 10. Product-design track — Paper Lifecycle & Reconciliation V19

This iteration's visual belongs to the real `Paper Lifecycle` trading workspace, not an audit-status report.

### REQUIRED

- Tier-0 market/session, Dhan, chain age, paper-engine, ledger/reconciliation state and LIVE LOCKED.
- Immutable correlation/command/order/fill/position/reconciliation IDs.
- Manual close shown as `Close Intent`, never file-edit behavior.
- Fill detail with exact quote snapshot, fill model revision and cost-policy revision.
- Gross P&L, each cost component and net after-cost P&L with quality/provenance.
- Restart/replay state, last committed event sequence, orphan/missing-fill/duplicate-event detection.
- Reconciliation state `RECONCILED | DRIFT | ERROR | UNKNOWN` and evidence drilldown.
- `LEDGER_ERROR/DRIFT` visibly inhibits paper mutations.

### RECOMMENDED

- Lifecycle timeline from candidate/prediction through risk, order, fill, position, close and outcome.
- Projection-generation comparison across positions/P&L/history.
- Redacted evidence export and reconciliation repair preview.

### OPTIONAL

- Advanced simulator what-if fills/cost scenarios, strictly isolated from authoritative historical ledger.

## 11. Closure discipline

`LOCKED-20X` means independently reproduced 20 times; it does not mean fixed. CLOSED requires a patch on an exact source revision, exact runtime/deployment proof where applicable, required tests, reproducible evidence IDs and independent verification. Trade-readiness, profitability, deployment success and live safety may never be inferred from UI labels or counters.

## 12. Next deep slice

Broker/account truth and portfolio reconciliation: trace Dhan funds/holdings/positions normalization, success/error/empty semantics, timestamps/provenance, account-generation consistency, portfolio/P&L projections and whether broker/account errors can collapse into zero/empty or disagree with paper state/risk views.