# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 16:58 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `5c0b43eb9ddd30dbe6014c8472fee2cbfceb585f`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Compare `b70af343... -> 5c0b43eb...`: 21 commits ahead, 0 behind, and only `reports/latest/manual_repo_qc_audit/summary.md` changed. Therefore no newer application implementation is promoted into this evidence baseline.
- PR #98 is OPEN at `74f5b68509b5af7ec94466831c2dd4d57365d868`, base `5c0b43eb...`. It changes `dashboard/style.css` and `core/brokers/dhan/token_manager.py`; it is not implemented on `main`. Its exact head has two observed PR-triggered successful workflows: `Genesis System3 Global Safety CI` run 1234 and `GCP Dhan Token Fix CI` run 55. Those results prove only that PR head checks completed successfully; they do not prove deployment/runtime readiness.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`.
- PR #96 remains the newest merged application/UI PR identified in current evidence.
- GitHub returned no workflow runs for exact application SHA `b70af343...` and no workflow runs for report-only HEAD `5c0b43eb...`; exact-revision application CI/runtime readiness remains **NOT PROVEN**.
- Google Cloud is the only accepted deployment target. Render-era operational assumptions are migration debt.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing remain prohibited.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Canonical solution / implementation state |
|---|---|---|
| Exact application revision proof | **NOT PROVEN** | `DeploymentTruth` — READY TO PATCH |
| Dashboard auth/session | **FAIL / P0-P1** | `SessionTruth` — READY TO PATCH |
| Mutation authorization | **FAIL / P0-P1** | `MutationPolicy + CapabilityManifest` — READY TO PATCH |
| Global mode/order safety | **FAIL / P0** | `SafetyTruth + ExecutionEligibility` — READY TO PATCH |
| Broker/account truth | **FAIL / P0-P1** | `SOL-21 AccountTruth + AccountSnapshotCoordinator` — READY TO PATCH |
| DB/shared state | **FAIL / P0-P1** | `StateTruth + domain CAS` — READY TO PATCH |
| WebSocket/REST truth | **FAIL / P0-P1** | `StreamTruth` — READY TO PATCH |
| Option chain/Greeks | **FAIL / P0-P1** | `OptionChainTruth` — READY TO PATCH |
| Scanner/ranker | **FAIL / P0-P1** | `ScannerTruth` — READY TO PATCH |
| Performance/concurrency | **FAIL / P0-P1** | `WorkCoordinator + SnapshotScheduler` — READY TO PATCH |
| Paper lifecycle/reconciliation | **FAIL / P0** | `SOL-20 PaperLedger + ReconciliationService` — READY TO PATCH |
| Pre-trade risk authority | **FAIL / P0** | `PreTradeRiskService` — READY TO PATCH |
| AI/prediction provenance | **MISSING / P0-P1** | `PredictionTruth + ModelArtifactManifest` — READY TO PATCH/DESIGN |
| Accessibility/responsive browser proof | **FAIL / P1** | `AccessibleWorkstationShell` — READY TO PATCH |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 2. System-wide audit invariant

Missing, stale, parse-failed, timed-out, unauthenticated, overloaded, contradictory, corrupt or unproven evidence must never become PASS, LIVE, safe, fresh, zero-risk, zero-P&L, zero-Greek, calibrated confidence, broker-connected, account-empty, deployed-current or trade-ready through defaults.

A successful profile/connectivity request proves connectivity only. It does not prove funds, holdings, positions, orders, margin, portfolio generation or risk-input freshness. Empty, zero, error and unknown are different states.

Files and dashboard DTOs are projections only. They must never be transaction authority. Every paper/live-adjacent state mutation must be backed by immutable server-issued decision/event IDs. UI can display safety truth; it can never be its authority.

## 3. Retained findings registry and canonical remediation groups

### AUTH-001..011 — Session/authentication authority

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED. `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`; other AUTH findings remain below 20.

**Root causes:** LoginPage/body contract mismatch; raw API-key persistence in browser storage; global key injection; deterministic session token; browser-only expiry; no authoritative server revocation record; incomplete auth throttling/CSRF/idempotency proof.

**Files/functions likely to change:** `dashboard/frontend/src/components/LoginPage.tsx`, `AuthUnlock.tsx`, `hooks/useAuth.ts`, `dashboard/backend/app.py` auth routes/middleware, `security_policy.py`.

**Target:** one `SessionTruth` contract with random opaque session ID, HttpOnly/Secure/SameSite cookie, authoritative `issued_at/expires_at/revoked_at`, principal/scope, policy revision, runtime revision and evidence ID. Browser stores no reusable API key after session creation.

**Implementation:** unify login contract; remove sessionStorage/localStorage API key; remove global request-key injection; add server session registry/revocation/expiry; add auth throttling; test exact cookie attributes behind Cloud Run.

**Migration:** support existing login route temporarily but issue only new-style session; invalidate deterministic legacy cookies.

**Security constraints:** never expose dashboard key, Dhan token, PIN/TOTP or worker token in UI/log/export.

**Regression risks:** existing API client assumes `X-API-Key`; replace with one authenticated client using cookie credentials.

**Tests/PASS:** valid login, invalid login, expiry, revocation, logout, CSRF, cross-origin denial, no browser secret, no API key on subsequent requests. 20 repeated invalid attempts must be rate-limited. PASS only when revoked/expired sessions cannot read protected data or mutate state.

**Rollback:** auth uncertainty => deny protected routes; live remains locked.

**Implementation status:** READY TO PATCH.

### MUT-001..008 — MutationPolicy + CapabilityManifest

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED.

**Root causes:** mutation routes have inconsistent auth/replay semantics; `/api/live-trading/approve` persists approval; idempotency is path-list based; worker replay protection is incomplete; HTTP auth is not domain eligibility.

**Files:** `dashboard/backend/app.py`, `security_policy.py`, scheduler/worker ingest routes, future `mutation_policy.py`.

**Target:** every POST/PUT/PATCH/DELETE declares one capability such as `SESSION_CREATE`, `SESSION_REVOKE_SELF`, `WORKER_INGEST`, `PREFERENCE_WRITE`, `PAPER_MUTATION`, `RISK_POLICY_WRITE`, `LIVE_APPROVAL`, `LIVE_MUTATION`.

**Implementation:** generate route inventory from `app.routes`; fail CI on unclassified write route; bind auth/CSRF/idempotency/domain-gate/audit rules to capability; forbid GET mutation and query-string secrets.

**Compatibility:** preserve route paths where possible while changing enforcement semantics.

**Safety:** `LIVE_MUTATION` hard denied in analyzer/paper deployments. `LIVE_APPROVAL` is evidence only, never router enablement.

**Tests/PASS:** unclassified writes=0; duplicate route owners=0; GET mutations=0; query-string secrets=0; analyzer/live mutation allowance=0.

**Rollback:** unknown mutation capability => 403/locked.

**Status:** READY TO PATCH.

### SAFE-001..008 + RISK-001..009 — SafetyTruth, ExecutionEligibility, PreTradeRiskService

**Severity/status:** P0, OPEN / FIX-REQUIRED.

**Root causes:** split kill-switch authorities; order creation gated mainly by kill state; risk analytics are not independently proven as mandatory transaction gate; scheduler/live-approval surfaces can create contradictory readiness semantics; browser/default risk values can collapse unknown to safe-looking numbers.

**Files:** `dashboard/backend/order_management.py`, `risk_management.py`, `app.py` safety/live/scheduler routes, kill-switch modules/files, future `safety_truth.py` and `pretrade_risk_service.py`.

**Target:** one server `SafetyTruth`; one immutable `ExecutionDecision` required for every paper/live-adjacent mutation; kill switch OK is necessary but never sufficient.

**Execution chain:** `Intent -> MutationPolicy -> SafetyTruth -> DeploymentTruth -> StateTruth generation -> Stream/OptionChain/AccountTruth -> PreTradeRiskService -> ExecutionDecision -> serialized paper worker`.

**Contract:** `ExecutionDecision {decision_id, intent_id, state: PASS|FAIL|UNKNOWN|ERROR, safety_revision, risk_policy_revision, account_snapshot_id, market_snapshot_ids, expires_at, evidence_ids[]}`.

**Safety:** UNKNOWN/STALE/ERROR always inhibit. UI never overrides backend gate. LIVE router remains independently hard locked.

**Tests/PASS:** no paper position/order/close can be created without current PASS decision; stale account/market/safety/risk input rejects; kill-switch conflict rejects; scheduler cannot bypass.

**Rollback:** decision service unavailable => paper mutation inhibited; read-only UI allowed.

**Status:** READY TO PATCH.

### STATE-001..012 — StateTruth + domain CAS

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED.

**Root causes:** local files/shared state/in-memory state can disagree; whole-snapshot writes can overwrite newer domains; local fallback can become authority; startup may promote plausible but stale state.

**Files:** runtime/state store, state sync service, Firestore adapter, app startup, frontend state projections.

**Target:** Firestore/shared state is production authority on GCP; domain revisions for broker/account/market/chain/scanner/risk/paper; every write carries writer ID, runtime revision, event ID and expected revision.

**Implementation:** domain CAS/transactions; startup generation validation; reject stale writer; local files diagnostic/projection only; fail closed if required shared backend unavailable.

**Tests/PASS:** concurrent writers cannot overwrite newer revisions; Firestore outage yields `STATE_AUTHORITY_ERROR` and read-only degraded mode, not local authority.

**Status:** READY TO PATCH.

### CHAIN-001..014 — OptionChainTruth

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED.

**Root causes:** null-to-zero conversion, incomplete Greeks/quotes, expiry-insensitive or weakly-proven caches, source invention, parser-error collapse and weak runtime provenance.

**Files:** Dhan chain acquisition/normalizer/cache, backend chain endpoints, frontend chain tables/TopBar, Greeks services.

**Target contract:** underlying/security ID/requested+resolved expiry/provider/source event time/receive time/age/TTL/schema+normalizer revision/cache identity/spot+quote quality/row evidence/Greeks provenance.

**Implementation:** null remains null; keyed singleflight per provider/security/expiry; source must be inherited from validated acquisition truth; complete Delta/Gamma/Theta/Vega/Rho/IV with units/method evidence.

**Tests/PASS:** stale/parse/error never appears live/zero; expiry collision impossible; one cold fetch per key; missing Greek is UNKNOWN not zero.

**Status:** READY TO PATCH.

### WS-001..011 — StreamTruth

**Severity/status:** P0-P1, OPEN/UNPROVEN.

**Root causes:** socket-open is treated too close to stream health; heartbeat/freshness/order validation weak; competing REST/WS writers can regress state; malformed events can fail silently.

**Target:** transport state separated from market-data state. Every event carries event time, backend receive time, frontend receive time, sequence, schema version, source revision and TTL. Older revisions cannot overwrite newer.

**Tests/PASS:** out-of-order/replayed/malformed/stale events rejected and counted; reconnect does not restamp old payload fresh.

**Status:** READY TO PATCH.

### SCAN-001..010 — ScannerTruth

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED.

**Root causes:** same-day rank accepted as current; high-watermark carryover can retain prior larger gain; old rows can be restamped; REST/WS writers compete; WATCH can be treated too close to eligibility; source/freshness can be manufactured by ranking layer.

**Target:** immutable scanner snapshot/cycle/session/universe generation; latest observation always replaces older even when gain falls; rank, gain and eligibility separate; stale rows evicted.

**Tests/PASS:** 40% -> 12% becomes 12%; absent/stale row evicts; older REST snapshot cannot overwrite newer WS; no risk PASS => not eligible.

**Status:** READY TO PATCH.

### PERF-001..009 — WorkCoordinator + SnapshotScheduler

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED. `PERF-004 2/20`.

**Root causes:** timeout waiter does not cancel OS thread; overlapping polls; chain stampede; overlapping paper ticks; false current-RSS telemetry; response buffering; event-loop blocking sync; cold batch fan-out; unbounded log-tail reads.

**Target:** bounded domain workers; singleflight; one serialized paper mutation worker; completion-driven browser polling; queue/event-loop/current+peak RSS observability; overload => `DEGRADED_READ_ONLY`.

**Tests/PASS:** 20 duplicate paper ticks yield one logical command; no overlapping cold chain fetch for same key; event loop remains responsive under injected slow provider; stale late result rejected.

**Status:** READY TO PATCH.

### ML-001..014 — PredictionTruth + ModelArtifactManifest

**Severity/status:** P0-P1, OPEN / FIX-REQUIRED.

**Root causes:** immutable prediction ledger absent; score/confidence semantics conflated; maturity stages weak; temporal leakage/calibration proof incomplete; prediction outcomes not linked to reconciled after-cost paper lifecycle.

**Target:** prediction ID, model/artifact hash, dataset hash, feature schema hash, source SHA, train/data cutoff, calibration revision, uncertainty, maturity state and later realized outcome linkage.

**Tests/PASS:** prediction is immutable; no future data leakage; calibrated probability separately proven; only reconciled after-cost outcomes enter forward-performance evidence.

**Status:** READY TO PATCH/DESIGN.

### A11Y-001..012 + UI-001..019 — Accessible workstation and UI truth

**Severity/status:** P1, OPEN. `UI-001` is `LOCKED-20X / FIX-REQUIRED`; `UI-005 17/20`, `UI-007 13/20`, `UI-016 14/20`.

**Root causes:** hard-coded/default-valid UI states; zero/empty ambiguity; weak provenance/freshness; fixed/clipped layouts; keyboard/focus/live-region gaps; no exact revision browser proof.

**Target workspaces:** Command Center; Market/Scanner; Options & Greeks; AI Decision Audit; Paper Lifecycle; Portfolio & Risk; Data & Broker; Readiness/Proof; Observability; Security/Settings.

**Implementation:** all status badges consume typed backend truth; desktop/tablet/mobile shell; command palette; focus-visible; keyboard navigation; aria-live critical changes; responsive tables/cards; no Tier-0 safety truth clipped.

**Tests/PASS:** Playwright + axe + console-error tests across all workspaces, desktop/tablet/mobile, 200% zoom, auth/error/loading/market-open/closed/stale states.

**Status:** READY TO PATCH.

## 4. Paper lifecycle deep slice — PAPER-017..024

### PAPER-017/018 — direct manual close + competing paper authorities

**Severity/status:** P0, READY TO PATCH / FIX-REQUIRED, 1/20 each.

**Proof/root cause:** `dashboard/backend/app.py::close_position(position_id)` edits `positions_live.json` directly, while `CloudPaperEngine` owns separate `self.open_positions`/`paper_engine_state.json` and later rewrites the projection. A manual close can therefore be overwritten/resurrected.

**Target:** `ClosePositionIntent` through MutationPolicy/SafetyTruth/fresh quote/risk/idempotent serialized paper worker, producing immutable close/fill/position events. Projection files become read-only outputs.

**Tests/PASS:** 20 duplicate closes -> one close; stale revision rejects; restart/tick cannot reopen closed lifecycle; no route directly writes positions projection.

**Rollback:** disable manual mutation, retain read-only positions.

### PAPER-019 — persistence failure silently becomes empty state

**Severity/status:** P0-P1, READY TO PATCH / FIX-REQUIRED, 1/20.

**Proof/root cause:** broad exception handling in paper state load/save/output paths can initialize/retain empty arrays/zero sequence rather than expose ledger failure.

**Target:** typed `LEDGER_ERROR`; event commit before projection acknowledgement; checksummed/versioned checkpoints; persistence failure inhibits paper mutations.

**Tests/PASS:** malformed state, permission denied, disk-full/mock write failure and interrupted snapshot never yield proven zero/empty portfolio.

### PAPER-020 — destructive day rollover and repeatable IDs

**Severity/status:** P1, READY TO PATCH, 1/20.

**Target:** global UUID/ULID event/position IDs; session boundary events; unresolved overnight position => `RECONCILE_REQUIRED`, never silent reset.

**Tests/PASS:** IDs never repeat across 20 simulated sessions; unresolved position survives as reconciliation blocker.

### PAPER-021/022/023 — explicit fill/cost/quantity provenance

**Severity/status:** P1, READY TO PATCH, 1/20 each.

**Root causes:** LTP used directly as simulated fill; no immutable order/fill/quote chain; hard-coded cost constants return opaque net; quantity can be recomputed with a different fallback multiplier.

**Target:** `PAPER_ORDER_ACCEPTED -> PAPER_FILL -> POSITION_*`; fill stores actual signed quantity, quote snapshot, fill-model revision and `CostPolicy` revision. Gross, brokerage, fees/taxes, slippage, total cost and net are individually persisted.

**Tests/PASS:** exactly one opening and closing fill per lifecycle; stored quantity drives P&L; gross-cost=net; policy change never rewrites old event values; unsupported instrument metadata inhibits fill.

### PAPER-024 — no authoritative reconciliation chain

**Severity/status:** P1, READY TO PATCH, 1/20.

**Root cause:** engine state, positions JSON, P&L JSON/summary and CSV history lack one common immutable generation/event sequence.

**Target contract:** `ReconciliationTruth {state: RECONCILED|DRIFT|ERROR|UNKNOWN, ledger_seq, projection_generations, orphan_ids, duplicate_ids, evidence_id, checked_at}`.

**Tests/PASS:** projection deletion/edit/truncation deterministically rebuilds from ledger; mismatch => DRIFT, never PASS.

## 5. Canonical solution — SOL-20 PaperLedger + ReconciliationService

**Status:** READY TO PATCH.

### Authoritative lifecycle

`PaperCommand / ClosePositionIntent -> MutationPolicy -> SafetyTruth -> DeploymentTruth + StateTruth generation -> StreamTruth / OptionChainTruth / AccountTruth -> PreTradeRiskService -> immutable ExecutionDecision -> serialized/idempotent PaperMutationWorker -> PAPER_ORDER_ACCEPTED -> PAPER_FILL -> POSITION_OPENED/UPDATED/CLOSED -> P&L valuation event -> RECONCILIATION_CHECKPOINT`.

Projection files such as `positions_live.json`, `pnl_live.json`, `paper_pnl_summary.json` and CSV exports are projections only.

### Core contracts

- `PaperCommand {command_id, correlation_id, intent_id, decision_id, idempotency_key, capability, expected_generation, created_at}`
- `PaperOrderEvent {order_event_id, command_id, instrument_id, side, qty, order_type, quote_snapshot_id, state}`
- `PaperFill {fill_id, order_event_id, qty, fill_price, quote_snapshot_id, fill_model_revision, cost_policy_revision, filled_at}`
- `PositionEvent {position_id, position_revision, parent_fill_id, state, event_id, event_time}`
- `CostBreakdown {gross, brokerage, taxes_fees, slippage, total_cost, net, policy_revision}`
- `ReconciliationTruth {state, ledger_seq, projection_generations, orphan_ids, duplicate_ids, evidence_id, checked_at}`

### Ordered implementation

1. Add durable append-only event store and global IDs.
2. Add one serialized mutation worker with idempotency.
3. Convert `/api/paper/tick` to command enqueue.
4. Convert manual close to ClosePositionIntent.
5. Add explicit order/fill/position events bound to quote/risk evidence.
6. Store actual fill quantity/instrument metadata.
7. Add versioned CostPolicy and component P&L.
8. Replace destructive date reset with session/EOD events.
9. Make persistence errors fatal to mutation authority.
10. Build all UI/JSON/CSV projections from reducers.
11. Reconcile on startup, after command, before readiness statistics.
12. Surface lifecycle/cost/reconciliation evidence in Paper workspace.

**PASS:** every Paper position/P&L/history row is reconstructible from immutable events and a RECONCILED checkpoint.

## 6. Latest deep slice — Dhan broker/account truth, funds, holdings, positions and portfolio consistency

### ACCOUNT-001 / P0-P1 — positions/holdings can return success=true for Dhan failure payloads

**Exact proof:** `core/brokers/dhan/dhan_readonly.py::get_funds()` explicitly checks `_auth_failure_payload(data)` for SDK and REST responses. `get_positions()` and `get_holdings()` do not perform the same payload-level failure check; an SDK/REST JSON body that represents broker failure but arrives without transport exception can be wrapped as `{success: True, source: ..., data: ...}`.

**Symptom/root cause:** transport success is conflated with semantic broker success for positions/holdings.

**Real-money/readiness impact:** downstream normalizers can turn a broker failure payload into an empty list and the system can then treat zero positions/holdings as valid account truth. Pre-trade exposure/margin decisions could be materially wrong.

**Files/functions:** `core/brokers/dhan/dhan_readonly.py::get_positions/get_holdings/get_funds/get_orders_readonly`, Dhan semantic classifier, broker/account service.

**World-class target:** every broker read uses one semantic response validator returning `PASS|EMPTY|ERROR|AUTH_ERROR|RATE_LIMITED|STALE|UNKNOWN`, provider request ID/status, account identity hash, event/receive times and evidence ID.

**Minimal safe implementation:** centralize `_classify_dhan_response`; require expected payload schema before `success=true`; apply consistently to profile/funds/holdings/positions/orders; never normalize failure payload as empty account.

**Contract change:** replace loose `{success,data,error}` with `BrokerReadResult<T> {state, data, empty_proven, source, provider_status, provider_request_id, account_id_hash, event_time, received_at, age_ms, schema_revision, evidence_id, error}`.

**Migration:** compatibility serializers may expose legacy fields but must preserve `state` and never map ERROR/UNKNOWN to success/empty.

**Safety:** AccountTruth ERROR/UNKNOWN inhibits PreTradeRiskService and paper/live-adjacent mutations.

**Regression risks:** UI currently interprets lists/counts directly; update frontend together with contract.

**Tests/PASS:** inject HTTP-200 failure payload, DH-906 payload, malformed payload, true empty positions, true one-position payload; only true empty can yield `EMPTY` with count 0. Failure never yields proven zero exposure.

**Rollback:** account semantic validator unavailable => AccountTruth UNKNOWN and risk inhibited.

**Status:** READY TO PATCH / FIX-REQUIRED.

### ACCOUNT-002 / P0-P1 — Dhan normalizer converts missing/malformed holdings values to numeric zero

**Exact proof:** `dhan_payload_normalizer.py::normalize_holding_row()` uses `... or 0` for quantity/average/LTP and on any conversion exception sets all three to `0.0`. It then computes current value/P&L from those zeros. `normalize_position_row()` similarly defaults quantity/LTP/P&L fields to zero and uses direct `float(...)` conversions for several fields.

**Root cause:** parser convenience defaults are being used as financial truth.

**Impact:** unavailable or malformed broker market/account data can become apparently valid ₹0 / zero exposure / zero P&L rows.

**Files:** `core/brokers/dhan/dhan_payload_normalizer.py`, BrokerPanel, broker truth validator.

**Target:** nullable typed fields plus per-field quality: `VALID|MISSING|INVALID|STALE`; financial zero is accepted only when explicitly present and schema-valid.

**Implementation:** parse each field independently; preserve raw value; null on missing/invalid; add `field_errors`; calculate derived current value/P&L only when all required inputs valid.

**Tests/PASS:** malformed one field does not zero unrelated fields; missing LTP => P&L UNKNOWN, not zero; explicit broker zero remains valid zero.

**Rollback:** parser uncertainty => row quality ERROR/UNKNOWN.

**Status:** READY TO PATCH / FIX-REQUIRED.

### ACCOUNT-003 / P0 — broker truth validator can certify empty/zero account fields as VALID after semantic parsing loss

**Exact proof:** `broker_truth_validator.py::_field_status()` allows zero by default and treats an empty list as valid for required list type. `build_broker_truth_report()` derives holdings/positions counts from normalized lists and uses 0 for holdings value and position P&L when API response reports success. If semantic failure/malformed shape has already been wrapped as success, the validator can count those zeros as valid and potentially reach `VALID`/`PASS_WITH_WARNINGS`.

**Root cause:** validator trusts upstream boolean success and validates plausible numeric shape rather than provenance/semantic completeness.

**Impact:** false-green account/risk evidence.

**Files:** `broker_truth_validator.py`, `dhan_readonly.py`, normalizer, readiness/risk consumers.

**Target:** validator consumes typed BrokerReadResult and AccountSnapshot; EMPTY is only valid if `empty_proven=true` from correct broker schema. Aggregates require one account generation and domain evidence IDs.

**Implementation:** remove validity derived solely from zero/count; require semantic state + schema proof; overall `PASS` only when mandatory domains are PASS/EMPTY_PROVEN and same generation.

**Tests/PASS:** HTTP-200 error body, malformed body and wrong schema must produce NOT_VALID/ERROR; only broker-defined empty schema can produce zero counts as valid.

**Rollback:** ambiguity => AccountTruth UNKNOWN.

**Status:** READY TO PATCH / FIX-REQUIRED.

### ACCOUNT-004 / P1 — funds/holdings/positions lack event time, receive time, TTL and common account generation

**Exact proof:** read-only adapter returns source/data/error without authoritative event/receive timestamps; `broker_truth_validator` adds only report `generated_utc`; modular `/api/broker/truth` creates a response timestamp after sequentially calling status/funds/holdings/positions. There is no per-domain source age, snapshot revision or account generation.

**Root cause:** retrieval time is being used as a loose proxy for source consistency.

**Impact:** risk/portfolio views can combine funds from one moment, positions from another and profile connectivity from another while appearing as one current account.

**Files:** Dhan adapter, account coordinator, broker API DTOs, frontend store/BrokerPanel, PreTradeRiskService.

**Target:** `AccountSnapshot {snapshot_id, account_id_hash, token_generation, started_at, completed_at, domains{profile,funds,holdings,positions,orders}, consistency_state, evidence_id}`; each domain has event/receive time, age, TTL, provider request ID and schema revision.

**Implementation:** coordinate bounded reads; stamp backend receive time immediately; derive account snapshot generation; enforce maximum skew; publish `CONSISTENT|PARTIAL|STALE|ERROR|UNKNOWN`.

**Tests/PASS:** deliberately delay one domain beyond skew/TTL and verify risk inhibited; mixed token generation rejected; all domains trace to snapshot ID.

**Status:** READY TO PATCH.

### ACCOUNT-005 / P1 — profile CONNECTED can remain green while account domains fail or are stale

**Exact proof:** `get_status()` caches only a connected profile result for `_STATUS_RESULT_TTL_S`. `BrokerPanel` derives `brokerTruthConnected` from broker/profile connected state and can display `READ-ONLY BROKER PROOF OK` even though holdings/positions are independently fetched and may be in error. The panel's `Broker Blocker` row is driven mainly by token/broker connectivity, not one authoritative account consistency verdict.

**Root cause:** connectivity proof and account-data proof are conflated in UI hierarchy.

**Impact:** operator may infer usable account/risk state from a green broker connection while funds/positions are stale/failed.

**Files:** `dhan_readonly.py::get_status`, frontend `BrokerPanel.tsx`, store/useData, future AccountTruth endpoint.

**Target UI:** separate `DHAN PROFILE CONNECTIVITY` from `ACCOUNT SNAPSHOT`. Connected profile may be green while AccountTruth is PARTIAL/STALE/ERROR; risk remains inhibited.

**Tests/PASS:** profile succeeds while positions fails => header shows connectivity OK but account snapshot ERROR/PARTIAL and no risk eligibility.

**Status:** READY TO PATCH.

### ACCOUNT-006 / P1/UI — BrokerPanel still renders financial unknowns as zero-derived values

**Exact proof:** `BrokerPanel.tsx` helper functions default average/entry to 0, holdings LTP/quantity to 0, compute P&L from those values, and position LTP/P&L fallback to 0. It also considers Holdings API `RESPONDED` whenever a holdings object exists and no interpreted error is present, including zero rows.

**Root cause:** frontend presentation layer contains independent financial fallback logic instead of rendering typed backend field truth.

**Impact:** unknown/missing market/account values can look like real zeros; browser-derived P&L can disagree with backend/account truth.

**Files:** `BrokerPanel.tsx`, `useData.ts`, store types, reusable money/quality cells.

**Target:** backend owns normalized financial fields and quality; UI renders `— / UNKNOWN / STALE / ERROR` and evidence/age. No browser P&L reconstruction for authoritative broker rows.

**Tests/PASS:** null/missing values never render `₹0.00`, `0.00%` or green success; explicit broker zero does. Browser and API P&L must match exact evidence ID.

**Status:** READY TO PATCH.

### ACCOUNT-007 / P1 — disabled modular broker router contains false-zero compatibility behavior and is a future reactivation hazard

**Exact proof:** `dashboard/backend/routers/broker.py` is currently disabled in `app.py` because modular routers duplicate active rich endpoints. Its funds route defaults missing balances to 0 and exceptions to all-zero balances; holdings/positions exceptions return empty lists/count 0. `/api/broker/truth` sequentially combines those responses.

**Root cause:** duplicate broker API contracts remain in the source tree with weaker truth semantics.

**Impact:** future modularization/re-enable could silently reintroduce zero/empty-on-error behavior and conflicting route ownership.

**Files:** `dashboard/backend/routers/broker.py`, `dashboard/backend/app.py`, route-inventory tests.

**Target:** one canonical broker/account service and route owner. Delete or refactor legacy duplicate router before re-enabling; no separate normalization/default logic.

**Tests/PASS:** unique `(method,path)` owner; same AccountTruth schema from every public account endpoint; error cannot become zero/empty.

**Status:** READY TO PATCH / FIX-REQUIRED before router re-enable.

### ACCOUNT-008 / P1 — account truth is not yet bound into canonical PreTradeRiskService

**Exact proof:** current broker/account validator is primarily reporting/validation logic; prior risk audit already proved no independently authoritative PreTradeRiskService is wired to every mutation. No immutable `account_snapshot_id` is required before paper tick/close/order intent.

**Root cause:** account display truth and execution eligibility are separate concerns without a mandatory join.

**Impact:** even a future correct account panel would not by itself stop stale/partial account data from being used by transaction logic.

**Files:** future `account_truth_service.py`, `pretrade_risk_service.py`, PaperMutationWorker, risk UI.

**Target:** every ExecutionDecision records one current AccountTruth snapshot ID; required domains and TTL are policy-defined. Missing/partial/stale account truth => risk state UNKNOWN/FAIL.

**Tests/PASS:** mutate account generation after risk evaluation => decision expires/rejects; missing positions/funds => no paper mutation; explicit proven-empty account can pass only if policy permits.

**Status:** READY TO PATCH.

## 7. Canonical solution — SOL-21 AccountTruth + AccountSnapshotCoordinator

**Status:** READY TO PATCH.

### Contract

`BrokerReadResult<T> {domain, state: PASS|EMPTY_PROVEN|STALE|AUTH_ERROR|RATE_LIMITED|ERROR|UNKNOWN, data, account_id_hash, token_generation, provider, provider_request_id, source_event_at, received_at, age_ms, ttl_ms, schema_revision, evidence_id, field_quality, error}`.

`AccountTruth {snapshot_id, state: CONSISTENT|PARTIAL|STALE|ERROR|UNKNOWN, account_id_hash, token_generation, started_at, completed_at, max_domain_skew_ms, domains, totals, reconciliation, runtime_revision, evidence_id}`.

### Ordered implementation

1. Build one Dhan semantic response classifier and apply to profile/funds/holdings/positions/orders.
2. Refactor normalizer to nullable per-field parsing with quality/errors; remove financial `or 0` defaults.
3. Create `AccountSnapshotCoordinator` with bounded/singleflight account reads and one generation ID.
4. Stamp receive times, provider request IDs where available, age/TTL and schema/normalizer revisions.
5. Define broker-proven empty payloads separately from malformed/error payloads.
6. Rebuild `broker_truth_validator` on AccountTruth; zero counts valid only for EMPTY_PROVEN.
7. Replace duplicate/disabled broker router semantics with one canonical service before modular router reactivation.
8. Update frontend store/useData/BrokerPanel to consume AccountTruth only; no browser financial reconstruction.
9. Bind `account_snapshot_id` to PreTradeRiskService and ExecutionDecision.
10. Add broker-vs-paper/risk reconciliation view and evidence drilldown.

### Migration/backward compatibility

Legacy response fields may remain temporarily, but they must be derived from AccountTruth and carry state/evidence. Never preserve legacy `0` on error semantics.

### Security/safety

- Read-only Dhan adapter remains the only broker interface for this audit scope.
- Existing place/modify/cancel blockers remain intact.
- AccountTruth UNKNOWN/PARTIAL/STALE/ERROR inhibits risk-dependent paper mutations.
- No raw account credential/token is emitted; use redacted account identity hash.

### Regression risks

- Components expecting numeric zeros may need nullable types.
- Existing tests that assert empty arrays on transport error must be changed to typed ERROR.
- Read coordination can increase latency; use bounded WorkCoordinator and last-good STALE display, never stale-as-current.

### Exact closure tests

1. HTTP 200 semantic error for holdings/positions => ERROR, not empty.
2. True broker empty positions => EMPTY_PROVEN/count 0.
3. Missing/malformed qty/LTP/avg => null + field error, not 0.
4. Funds PASS + positions timeout => AccountTruth PARTIAL/ERROR and risk inhibited.
5. Profile connected + holdings auth error => connectivity green only; account snapshot red/amber.
6. Domain age beyond TTL => STALE and risk inhibited.
7. Token/account generation changes mid-snapshot => snapshot rejected/retried.
8. Browser renders missing financial values as `—/UNKNOWN`, never zero.
9. Broker and Paper P&L remain explicitly separate sources; cross-source comparison never merges them.
10. 20 repeated identical reads preserve one canonical generation semantics and no false-green zero state.
11. Mock broker mutation methods remain zero calls.

**PASS:** every funds/holdings/positions/risk display traces to one AccountTruth snapshot/evidence ID; no broker error, parse loss or stale domain can appear as valid zero/empty current account state.

**Rollback/fail-safe:** keep last-good account snapshot read-only and mark STALE; PreTradeRisk and paper mutation inhibited; LIVE locked.

## 8. Regression checks this iteration

- Application/source SHA remains `b70af343...`; newest `main` at iteration start is report-only `5c0b43eb...`.
- PR #98 is open, not main. Its token-manager Cloud Run detection change and v-cloak CSS cannot close any `main` finding yet.
- PR #97 remains open and does not close synthetic-P&L issues on main.
- Exact application-head workflow runs remain absent.
- Modular broker router remains disabled due duplicate route ownership; duplicate weaker broker contract still exists in source.
- Dhan adapter remains read-only and explicitly blocks place/modify/cancel/super/forever/slice methods — positive safety foundation retained.
- Funds semantic auth-failure classification exists — positive foundation — but positions/holdings do not yet share the same classifier.
- `broker_truth_validator` still permits zero values/empty lists as valid based on upstream success.
- `BrokerPanel` still derives several account financial values/P&L with zero fallbacks.
- Existing `PERF-004` paper-tick concurrency and SOL-20 lifecycle findings remain unresolved.
- LIVE remains prohibited; no live order was enabled, placed, modified, cancelled or routed.

## 9. Findings upgraded/downgraded/closed

- `ACCOUNT-001..008`: NEW, `1/20` each, FIX-REQUIRED; ACCOUNT-001/002/003 are P0-P1/P0 because they can understate exposure/account truth.
- `UI-001`: independently reproduced again through broker/account zero-default behavior; remains `LOCKED-20X / FIX-REQUIRED` (counter stays capped at 20/20).
- `READY account-success ambiguity`: upgraded in confidence and now concretely owned by `SOL-21 AccountTruth`.
- `RISK` account-input concern: upgraded in confidence because current account reads lack common generation/TTL.
- Positive finding: Dhan read-only order methods remain hard blocked; no downgrade of live-off safety posture.
- `PAPER-010` remains CLOSED/CORRECTED only for the old route-absence claim.
- No readiness, profitability, deployment, account, paper or risk finding is closed in this iteration.

## 10. Prioritized remediation roadmap

### P0

1. `SessionTruth`: fix login contract; remove browser reusable API key; authoritative server expiry/revocation.
2. `MutationPolicy + CapabilityManifest`: classify every write route; CSRF/idempotency/capability enforcement.
3. `SafetyTruth + ExecutionEligibility + PreTradeRiskService`.
4. `SOL-21 AccountTruth`: semantic Dhan reads, nullable normalization, one account generation; bind to risk.
5. `SOL-20 PaperLedger + ReconciliationService`: eliminate direct file mutation/free-form engine state authority.
6. Remove split kill-switch authority and make missing safety truth fail closed.
7. `DeploymentTruth` exact SHA -> image digest -> Cloud Run revision.
8. `StateTruth + domain CAS` shared authority.
9. Bounded `WorkCoordinator` and serialized paper/account work.

### P1

1. `OptionChainTruth` + per-symbol/expiry singleflight.
2. `StreamTruth` event/heartbeat/order/freshness validation.
3. `ScannerTruth` latest-observation semantics and stale eviction.
4. Versioned Paper CostPolicy, explicit fills and after-cost P&L.
5. Replace scheduler URL secret with GCP IAM/OIDC and job capabilities.
6. `PredictionTruth` linked to reconciled paper outcomes.
7. Account-vs-paper-vs-risk reconciliation UI and evidence exports.
8. Responsive/accessibility/browser-console proof.
9. Retire remaining Render-era operational instructions/comments.

### P2

Institutional analytics, what-if scenarios, advanced drilldowns and tuning controls only after P0/P1 truth contracts are proven.

## 11. Independent verification counters

- `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`.
- `UI-001` remains `LOCKED-20X / FIX-REQUIRED`; reproducibility does not equal closure.
- `UI-005 17/20`, `UI-007 13/20`, `UI-016 14/20`.
- `PERF-004 2/20`.
- `PAPER-017..024 1/20` each.
- `ACCOUNT-001..008 1/20` each.
- `PAPER-010 route-absence` remains CLOSED/CORRECTED and cannot be LOCKED.
- No new finding reaches LOCKED-20X this iteration.

## 12. Product-design track — Data & Broker / Account Truth V20

This iteration's required visual is the real `Data & Broker` product workspace, not an audit-status report.

### REQUIRED

- Tier-0 market/session, Dhan profile connectivity, account snapshot state, funds/positions age, analyzer/paper state and LIVE LOCKED.
- Account snapshot ID, redacted account identity, token generation, broker event/receive times, age/TTL, schema revision and evidence ID.
- Separate domain states for PROFILE/FUNDS/HOLDINGS/POSITIONS/ORDERS READONLY.
- Funds table that displays unknown/malformed values as `— / UNKNOWN`, never ₹0.
- Holdings/positions tables with per-row source event, age, quality and evidence.
- Account-generation consistency state; mixed generation visibly inhibits risk.
- Broker-vs-paper-vs-risk reconciliation panel; sources must remain separate.
- Read-only broker adapter and place/modify/cancel prohibition visible as safety truth.

### RECOMMENDED

- Drilldown from any funds/position row to raw redacted provider response, normalizer revision and field-quality evidence.
- Account snapshot history/diff with generation changes.
- Margin/exposure scenario view only from proven AccountTruth.

### OPTIONAL

- Advanced portfolio attribution and historical account snapshots after durable provenance is proven.

## 13. Closure discipline

`LOCKED-20X` means independently reproduced 20 times; it does not mean fixed. CLOSED requires a patch on an exact source revision, exact runtime/deployment proof where applicable, unit/integration/browser/runtime tests, reproducible evidence IDs and independent verification. Trade-readiness, profitability, deployment success, broker truth and live safety may never be inferred from UI labels, workflow green alone or counters.

## 14. Next deep slice

Google Cloud deployment/runtime provenance and operational authority: trace `cloud-run-auto-deploy.yml`, build/image digest/revision/traffic, IAM/service-account separation, Secret Manager use, Scheduler invoker identity, runtime SHA endpoints and remaining Render-era instructions. Regression-check that no deployment path can set live/order flags or present a tag/HTTP-200 as exact-revision proof.