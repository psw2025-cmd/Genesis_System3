# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 02:03 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this solution-driven iteration: `04fcfa790c70f6228116bfad48ad5cdabcd5dc85`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after `b70af343...` in this loop are audit-report-only changes unless a later application commit is explicitly named.
- Recent PR review still shows PR #96 as the latest merged application/UI PR inspected in this loop.
- Combined status contexts for application HEAD `b70af343...` are empty. This is not proof of CI failure, but it is also not same-revision readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt and must not be treated as current target architecture.
- Audit posture: ANALYZER/PAPER, live-money routing OFF. No audit step may enable, place, modify, cancel or route a live order.
- This file is the single continuously maintained audit authority. Duplicate findings and duplicate solution proposals must be merged here.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Current application HEAD CI proof | **NOT PROVEN** | READY TO DESIGN exact-revision CI/runtime proof |
| Dashboard login HTTP contract | **FAIL / P0** | **READY TO PATCH** |
| Pre-auth protected polling | **FAIL / P1** | **READY TO PATCH** |
| Browser API-key exposure | **FIX-REQUIRED / P1** | **READY TO PATCH** after cookie contract test |
| Server session expiry | **PARTIAL / P1** | READY TO DESIGN server-expiring session |
| Global mode truth | **FAIL / P0** | **READY TO PATCH** via canonical `SafetyTruth` |
| Truth Control money readiness | **FAIL / P0** | **READY TO PATCH** after `GateTruth` contract |
| E2E “Trader Ready” semantics | **FAIL / P0** | **READY TO PATCH** after semantic readiness service |
| Risk-gate truth | **FAIL / P0-P1** | READY TO PATCH after backend gate inventory |
| Option-chain truth | **FAIL / P0-P1** | **READY TO PATCH** warming/null semantics; provenance contract READY TO DESIGN |
| Greeks UI | **INCOMPLETE / P1** | READY TO DESIGN end-to-end calculator provenance |
| Paper Trading safety truth | **FAIL / P0** | **READY TO PATCH** with `SafetyTruth` |
| Paper market-data truth | **FAIL / P0** | **READY TO PATCH** with `DataTruthEnvelope` |
| Paper P&L truth | **FAIL / P1** | **READY TO PATCH** null/zero semantics |
| Position provenance | **FAIL / P1** | **READY TO PATCH** typed row provenance |
| Trade workspace semantics | **INCOMPLETE / P1-P2** | READY TO DESIGN paper-order workstation |
| Prediction audit | **PENDING / REQUIRED** | READY TO DESIGN immutable ledger |
| Factor/scenario risk | **PENDING / REQUIRED** | READY TO DESIGN enforceable portfolio risk contract |
| Responsive/mobile UI | **NOT PROVEN / P2** | READY TO TEST after desktop truth refactor |
| Accessibility focus proof | **NOT PROVEN / P2** | READY TO TEST after navigation refactor |
| Cloud Run analyzer/live-off workflow flags | **PASS IN SOURCE ONLY** | READY TO PROVE at exact runtime revision |
| Real-market paper lifecycle | **NOT PROVEN** | READY TO DESIGN immutable lifecycle + reconciliation |
| Multi-day positive costed expectancy | **NOT PROVEN** | BLOCKED on lifecycle/outcome evidence |
| Real-money trade ready | **NO** | Remains locked until all P0/P1 proof gates close |

## 2. Solution-driven audit rule — now mandatory

Every finding in this report must carry or map to a canonical remediation containing:

1. root cause;
2. exact known files/components/routes likely to change;
3. target behavior;
4. minimal safe implementation;
5. ordered implementation steps;
6. API/schema migration notes;
7. safety/security constraints;
8. regression risks;
9. exact tests and PASS criteria;
10. implementation status: `NOT STARTED`, `READY TO PATCH`, `PATCHED`, or `VERIFIED`.

When several findings share one root cause, they map to one canonical solution rather than receiving duplicate patches.

## 3. Verified findings retained

### Authentication / session

- **AUTH-001 / P0:** `LoginPage.tsx` POSTs `/api/auth/session` without required JSON `api_key` body while `dashboard/backend/app.py` requires `DashboardAuthRequest(api_key)`.
- **AUTH-002 / P1:** `App.tsx` invokes `useData()` before `AuthGate` confirms authentication.
- **AUTH-003 / P1:** `LoginPage.tsx` stores raw key in `sessionStorage`; `useAuth.ts` globally reinjects it into axios/fetch.
- **AUTH-004 / P1:** cookie max-age exists, but independent server-side expiry/revocation is not proven.

### Global UI / truth

- **UI-001 / P0:** missing telemetry/data can be shown as success or plausible data.
- **UI-002 / P0-P1:** rank/score can be mislabeled as validated percentage/forecast.
- **UI-003 / P1:** Dhan/data-source truth can be inferred from UI defaults rather than backend provenance.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed, freshness, account reads, order permission and deployment provenance are independent domains but are sometimes conflated.
- **UI-005 / P1:** unsafe fallback/default semantics convert missing values to neutral/safe values.
- **UI-006 / P1:** account/position empty states do not distinguish proven-empty from auth/API/schema/stale/no-run states.
- **UI-007 / P1:** shared market-data truth envelope is missing.
- **UI-009 / P0:** PAPER/LIVE/LOCKED badges do not come from one authoritative runtime safety object.
- **UI-010 / P1:** immutable production prediction ledger is not proven.
- **UI-011 / P1:** factor/scenario risk and enforceable limits are not proven.
- **UI-012/UI-013/UI-014 / P2:** workspace rationalization, responsive/mobile and complete keyboard/focus behavior remain incomplete/unproven.
- **UI-018 / P1:** build badge is not deployment compatibility proof.
- **UI-019 / P1:** broker state machine must distinguish auth/read/feed/degraded/stale/API/schema states.

### Option chain / Greeks

- **CHAIN-001 / P0:** warming chain can fabricate `PCR=1`; warming/no-data must use null/unknown semantics.
- **CHAIN-002 / P1:** Dhan-looking chain verification lacks immutable provenance envelope with timestamps, age, schema, normalizer and completeness.
- **CHAIN-003 / P1:** full Delta/Gamma/Theta/Vega are not exposed in the Option Chain workspace.
- **CHAIN-004 / P1:** chain-to-Greeks calculation provenance is not proven end-to-end.
- **CHAIN-005 / P1:** IV unit/schema is implicit rather than typed.

### Readiness / live gate

- **READY-001 / P0:** missing live/order fields can default safe.
- **READY-002 / P0:** money-ready calculation excludes paper lifecycle.
- **READY-003 / P0-P1:** risk gate can PASS from object presence rather than all underlying gates passing.
- **READY-004 / P1:** funds/holdings/positions success semantics are too weak.
- **READY-005 / P0:** E2E trader-ready can pass transport without lifecycle/expectancy proof.
- **READY-006 / P1:** E2E core PASS is transport-level.
- **READY-007 / P1:** E2E Dhan proof lacks full freshness/schema envelope.
- **READY-008 / P1:** Live Gate still contains Render-era instructions.
- **READY-009 / P1:** human approval display lacks exact evidence revision/timestamp provenance.

### Paper / Trade / Positions

- **PAPER-001 / P0:** missing safety fields can yield `PAPER SAFE`.
- **PAPER-002 / P0:** missing data source can yield live-looking Dhan state because `DHAN_LIVE_MARK_TO_MARKET` is a fallback.
- **PAPER-003 / P1:** missing monetary fields can render as valid `₹0.00`.
- **PAPER-004 / P1:** missing row provenance can display plausible defaults such as `INTRADAY`, `NSE_FNO`, `PAPER_CLOUD_SIM`, `DHAN_LIVE`.
- **PAPER-005 / P1:** paper-safe proof relies mainly on negative evidence instead of a proven simulator/ledger chain.
- **PAPER-006 / P1:** position performance defaults to zero.
- **PAPER-007 / P1:** empty positions lack explicit truth state.
- **PAPER-008 / P1:** Force Paper Tick lacks visible idempotency/correlation proof.
- **PAPER-009 / P1:** immutable event-chain lifecycle is not exposed.
- **TRADE-001 / P1-P2:** current Trade tab lacks order/pre-trade lifecycle controls.
- **TRADE-002 / P0-P1:** `gain_rank` can be rendered under `GAIN %`.
- **TRADE-003 / P1:** `EOD/live` freshness wording is ambiguous.

## 4. Verification counters

Independent evidence only; rereading the same unchanged artifact does not increment.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `6/20` | OPEN |
| UI-002 | `3/20` | OPEN |
| UI-003 | `3/20` | OPEN |
| UI-004 | `2/20` | OPEN |
| UI-005 | `6/20` | OPEN |
| UI-006 | `3/20` | OPEN |
| UI-007 | `2/20` | OPEN |
| UI-008 | `2/20` | OPEN |
| UI-009 | `5/20` | OPEN |
| UI-010 | `2/20` | OPEN |
| UI-011 | `1/20` | OPEN |
| UI-016 | `3/20` | OPEN |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `2/20` | OPEN |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `1/20` | OPEN |
| CHAIN-005 | `1/20` | OPEN |
| READY-001 | `2/20` | OPEN |
| READY-002 | `1/20` | OPEN |
| READY-003 | `1/20` | OPEN |
| READY-004 | `1/20` | OPEN |
| READY-005 | `1/20` | OPEN |
| READY-006 | `1/20` | OPEN |
| READY-007 | `1/20` | OPEN |
| READY-008 | `1/20` | OPEN |
| READY-009 | `1/20` | OPEN |
| PAPER-001..009 | `1/20` each | OPEN |
| TRADE-001..003 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 5. Canonical solution contracts

### 5.1 `SafetyTruth` — authoritative runtime safety contract

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

**Rule:** missing safety fields => `UNKNOWN — DO NOT TRADE`. Never coerce missing to false and then render green.

### 5.2 `DataTruthEnvelope` — all market/broker/account datasets

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
quality_state: PROVEN | STALE | NO_DATA | API_ERROR | AUTH_REQUIRED | SCHEMA_ERROR | UNKNOWN
source_revision
runtime_revision
```

### 5.3 `PaperLifecycleTruth` — immutable simulator/event chain

```text
correlation_id
candidate_id
prediction_evidence_id
paper_order_id
simulator_id
simulator_version
created_at
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

A paper position or P&L number is not proven unless traceable to this lifecycle chain.

### 5.4 `GateTruth` — semantic readiness contract

Every gate requires:

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

Object presence or HTTP 200 is never PASS.

### 5.5 Readiness hierarchy

`transport_ok` < `schema_ok` < `source_proven` < `fresh` < `semantically_valid` < `reconciled` < `risk_passed` < `paper_lifecycle_proven` < `expectancy_proven` < `human_approval` < `live_router_armed`.

A higher state may never be inferred from a lower state.

## 6. Canonical remediation roadmap

### SOL-01 — Repair dashboard login/session architecture

**Maps findings:** AUTH-001, AUTH-002, AUTH-003, AUTH-004.

**Root cause:** login HTTP contract, authentication sequencing and browser credential handling are split across `LoginPage.tsx`, `useAuth.ts`, `App.tsx` and `dashboard/backend/app.py` without one tested end-to-end session contract.

**Known files/components likely to change:**

- `dashboard/frontend/src/components/LoginPage.tsx`
- `dashboard/frontend/src/hooks/useAuth.ts`
- `dashboard/frontend/src/App.tsx`
- `dashboard/backend/app.py`
- existing dashboard auth smoke/browser tests plus new HTTP integration tests

**Minimal safe implementation:**

1. Add `body: JSON.stringify({ api_key: key.trim() })` to the login POST. Preserve the current header only until middleware behavior is contract-tested; then remove redundant raw-key propagation if unnecessary.
2. On HTTP 200, rely on the HttpOnly session cookie. Do not save raw API key in `sessionStorage`.
3. Remove global raw-key reinjection from axios and `window.fetch` after cookie authentication is proven.
4. Move `useData()` into an authenticated child component or add explicit `enabled=authenticated` so protected polling cannot start before auth.
5. Replace deterministic non-expiring session proof with an opaque server-side TTL session or signed token containing a server-validated expiry, with rotation/revocation support.

**Regression/safety risks:** accidental lockout if middleware still requires `X-API-Key`; duplicate interceptor installation; cookie behavior behind Cloud Run proxy; session logout/rotation edge cases.

**Closure tests:**

- valid key POST with JSON body -> 200 + HttpOnly session;
- invalid key -> 401;
- missing body -> expected 422 only in negative test;
- `/api/auth/status` succeeds using cookie with no browser-stored raw key;
- protected polling count before auth = 0;
- logout invalidates session;
- expiry/replay test proves session invalid after TTL;
- frontend build + auth unit/integration/browser tests PASS.

**Status:** `READY TO PATCH` for client payload/auth sequencing; server-expiry design `READY TO DESIGN`.

---

### SOL-02 — One authoritative safety truth service

**Maps findings:** UI-001, UI-004, UI-005, UI-009, UI-016, READY-001, PAPER-001, PAPER-005.

**Root cause:** multiple components infer mode/safety independently, often from defaults or negative evidence.

**Known frontend surfaces to change:** `App.tsx` `ProductionProofBar`, `TopBar.tsx`, `SystemTruthControl`/Truth Control workspace, `EndToEndProof.tsx`, `PaperTrading.tsx`, `LiveTradingGate.tsx`, and shared store/hooks.

**Backend target:** one authenticated read-only safety endpoint/service returning `SafetyTruth`. If an existing state endpoint already owns all underlying fields, it should become the single normalized source rather than introducing duplicate authority.

**Minimal safe implementation:**

1. Define a strict backend schema for `SafetyTruth` with nullable fields and explicit `UNKNOWN/STALE/ERROR` states.
2. Compute it server-side from actual runtime flags/order-router authority/kill-switch state; UI does not recompute it.
3. Add source/runtime revision, image digest, policy version and proof time.
4. Store one parsed `SafetyTruth` object in frontend state.
5. Replace all hard-coded PAPER/LIVE-OFF/SAFE badges with this object.
6. Missing or stale truth renders amber/red `UNKNOWN — DO NOT TRADE`, never green.
7. UI approval never mutates live routing; backend order router remains independently fail-closed.

**Regression risks:** components currently expecting booleans; older payloads; brief startup unknown state; duplicate safety sources.

**Closure tests:** missing each field individually must never render green; stale truth must render STALE; contradictory flags must FAIL; live-off analyzer state must match backend runtime; browser screenshot/network proof must show all global badges driven by one payload.

**Status:** `READY TO PATCH` after backend route-owner inventory confirms canonical source.

---

### SOL-03 — Typed data provenance and null semantics everywhere

**Maps findings:** UI-001, UI-003, UI-005, UI-006, UI-007, UI-019, CHAIN-001, CHAIN-002, CHAIN-005, READY-004, READY-007, PAPER-002, PAPER-003, PAPER-004, PAPER-006, PAPER-007, TRADE-003.

**Root cause:** frontend fallbacks invent plausible values instead of representing missing/stale/error states.

**Known frontend surfaces to change:** `useData.ts`, `OptionChain.tsx`, `PaperTrading.tsx`, `Positions.tsx`, `TradeTab.tsx`, broker/data-integrity views and shared store types.

**Minimal safe implementation:**

1. Wrap chain, positions, funds, holdings, scanner, P&L and broker datasets in `DataTruthEnvelope`.
2. Replace `|| 0`, default `DHAN_*`, default `PAPER_*`, default `INTRADAY`, and mixed `EOD/live` labels with nullish-aware typed values.
3. Warming/no-chain state: `pcr=null`, `quality_state=NO_DATA|UNKNOWN`, never `pcr=1`.
4. Money formatter accepts `number | null`; null -> `— / NOT PROVEN`; only actual numeric zero -> `₹0.00`.
5. Empty positions require explicit `PROVEN_EMPTY`; otherwise show AUTH/API/STALE/SCHEMA/NO_RUN state.
6. Every live/snapshot label must show source event time, backend receive time, age, freshness threshold, market state and schema version.
7. Make IV canonical: `iv_decimal` internally or explicit value+unit field; no implicit `*100` contract.

**Regression risks:** many components rely on current permissive payloads; charts/tables may need nullable handling; historical proof fixtures may fail until migrated.

**Closure tests:** null/missing/zero/stale/error/auth fixtures for every dataset; no false Dhan-live label from absent source; no false PCR; no false zero P&L; exact source/time/age visible in browser proof.

**Status:** `READY TO PATCH` for frontend null/default fixes; backend envelope `READY TO DESIGN/PATCH` after endpoint inventory.

---

### SOL-04 — Semantic gate/readiness engine, never HTTP-success readiness

**Maps findings:** READY-001..009, UI-016, UI-018, historical trade-ready blockers.

**Root cause:** transport success, object presence and UI approval are allowed to stand in for semantic proof.

**Known frontend surfaces:** `SystemTruthControl`, `EndToEndProof.tsx`, `LiveTradingGate.tsx`, `ProductionProofBar`.

**Backend target:** canonical read-only readiness service producing `GateTruth[]` and a derived overall state; pre-route risk enforcement remains separate and authoritative.

**Minimal safe implementation:**

1. Define required gates explicitly: auth, broker/data, chain freshness, schema, paper lifecycle, reconciliation, risk, positive after-cost expectancy, multi-day stability, deployment revision and live-router permission.
2. Each gate requires semantic observed value + threshold + evidence/revision/time.
3. `moneyReady` must include paper lifecycle, reconciliation, risk and expectancy; no gate can PASS from object existence or HTTP 200.
4. Separate `TRANSPORT_OK` from `SEMANTIC_PASS` visually and in schema.
5. Human approval is only an acknowledgement step after technical gates; it cannot enable live routing.
6. Remove all Render-era activation instructions and reference only Google Cloud authority.

**Regression risks:** existing green UI may become PENDING/UNKNOWN until evidence is produced; tests relying on old booleans need migration.

**Closure tests:** HTTP 200 with semantically failing payload must FAIL; missing gate -> UNKNOWN; stale evidence -> STALE; paper lifecycle missing -> money-ready false; Render wording search = 0 in active UI; exact-revision proof links present.

**Status:** `READY TO PATCH` after backend auto-gate route inventory.

---

### SOL-05 — Option chain + Greeks production contract

**Maps findings:** CHAIN-001..005.

**Root cause:** UI chain, Dhan normalization and Greeks calculation are not joined by one typed/provenance contract.

**Known files/components:** `dashboard/frontend/src/components/OptionChain.tsx`, `dashboard/frontend/src/hooks/useData.ts`, `src/metrics/greeks.py`; exact backend option-chain normalizer/route must be mapped before code change.

**Minimal safe implementation:**

1. Normalize each option row into one versioned schema with symbol, expiry, strike, side, bid/ask/LTP, volume, OI, ΔOI, `iv_decimal`, Delta/Gamma/Theta/Vega/Rho and row quality.
2. Attach source/provider/event time/receive time/age/schema/normalizer version.
3. Attach Greeks provenance: calculator/provider, version, risk-free-rate source, dividend assumption, expiry convention, spot source/time, IV source, calculation time.
4. Expose complete Greeks in UI plus aggregate portfolio Greeks and scenario P&L.
5. Missing Greek/IV stays null/unknown; never fabricate.

**Closure tests:** deterministic Greeks fixtures; unit contract for IV; wrong-symbol suppression; stale/no-chain states; row completeness; UI columns; backend/frontend schema test; exact Dhan provenance proof.

**Status:** `READY TO DESIGN`; warming-PCR fix independently `READY TO PATCH`.

---

### SOL-06 — Immutable paper lifecycle + reconciliation

**Maps findings:** PAPER-003..009, TRADE-001, real-paper-lifecycle blockers.

**Root cause:** the UI presents tables/summaries, but no immutable event chain proves candidate→paper order→sim fill→position→exit→reconciliation.

**Known frontend surfaces:** `PaperTrading.tsx`, `Positions.tsx`, `TradeTab.tsx`.

**Backend discovery required before patch:** exact owner of `/api/paper/tick`, paper state persistence, simulator/fill model and P&L/reconciliation logic must be recursively mapped; do not guess filenames.

**Minimal safe implementation:**

1. Add immutable event IDs and one correlation ID per lifecycle.
2. Add idempotency key to mutation requests such as paper tick/order creation.
3. Persist simulator ID/version, requested/fill price, fill model, slippage, fees, market source/event time and source/runtime revision.
4. Use explicit state machine: `CANDIDATE → VALIDATED → PAPER_ORDER_CREATED → SIM_FILL → OPEN → MTM_UPDATE → EXIT_TRIGGER → CLOSED → RECONCILED`.
5. Reconciliation independently checks event count, open quantity, realized P&L before/after costs, duplicate/missing events.
6. Build a paper-only order ticket with quantity, entry, SL, target/trailing, maximum ₹ risk, data age, candidate/evidence ID and pre-trade gate summary.
7. Live-router selection is absent while live proof is incomplete.

**Regression risks:** schema/storage migration; duplicate historical rows; simulator outcome changes; UI summaries may differ once costs/slippage are explicit.

**Closure tests:** duplicate mutation is no-op/idempotent; crash/restart replay produces same state; every position traces to events; every P&L traces to fills/fees; reconciliation detects deliberate missing/duplicate event; no broker live-order path called.

**Status:** `READY TO DESIGN`; backend owner inventory is next required step.

---

### SOL-07 — Trade/scanner metric contract repair

**Maps findings:** UI-002, TRADE-002, TRADE-003.

**Root cause:** `gain_rank`, `gain_pct`, forecast/probability and freshness labels are not strongly typed/separated.

**Known frontend surface:** `TradeTab.tsx` and scanner/ranker displays.

**Minimal safe implementation:**

- define distinct fields: `rank`, `score`, `forecast_return_pct`, `realized_return_pct`, `probability`, each nullable and with metric type/version;
- never fall back from rank to percentage;
- validated prediction requires prediction ledger/evidence ID;
- freshness comes only from `DataTruthEnvelope`.

**Closure tests:** rank-only row cannot render `%`; missing forecast renders `—`; scanner candidate visually distinguished from validated prediction; stale/EOD state shows event time + age.

**Status:** `READY TO PATCH`.

---

### SOL-08 — Google Cloud deployment provenance and Render retirement

**Maps findings:** READY-008, UI-018, deployment/runtime proof gaps.

**Root cause:** active UI/workflow history still contains legacy Render-era wording and build/source revision is not equivalent to deployed runtime proof.

**Known areas:** `LiveTradingGate.tsx`, `TopBar.tsx`, `.github/workflows/cloud-run-auto-deploy.yml`, deployment/runtime evidence tooling.

**Minimal safe implementation:**

1. Remove active Render instructions/labels.
2. Expose backend source commit, frontend source commit, Cloud Run revision, container image digest, deployment time and environment/policy version from a read-only runtime metadata endpoint.
3. Dashboard compares source/runtime compatibility but never infers safety from a matching commit alone.
4. Keep Cloud Run analyzer/live-off flags unchanged during audit.
5. Require authenticated runtime proof after each deployment.

**Closure tests:** active-source search finds no Render deployment instructions; runtime endpoint values match Cloud Run deployment; frontend/backend revisions displayed; authenticated broker/data proof tied to same runtime revision; live flags remain disabled.

**Status:** `READY TO PATCH` for wording; runtime provenance `READY TO DESIGN/PATCH`.

## 7. Prioritized implementation order

### P0 Wave 1 — eliminate false-green safety and broken auth

1. SOL-01 login POST body + auth-gated polling.
2. SOL-02 authoritative `SafetyTruth` and remove hard-coded/default-safe badges.
3. SOL-03 remove false live/PCR/zero/provenance defaults.
4. SOL-04 semantic readiness: no HTTP/object-presence PASS.
5. SOL-07 fix rank-as-percent immediately.

**Wave-1 success criterion:** no missing field, empty response, HTTP 200 or frontend default can produce a green safety/readiness/live-data/financial result.

### P1 Wave 2 — prove market/account/paper truth

1. `DataTruthEnvelope` backend normalization.
2. immutable paper lifecycle/idempotency/reconciliation.
3. option-chain + complete Greeks provenance.
4. account-state truth and proven-empty semantics.
5. runtime/deployment provenance.

### P2 Wave 3 — institutional operator quality

1. workspace/navigation rationalization;
2. responsive tablet/mobile read-only experience;
3. keyboard/focus/status-announcement accessibility;
4. command palette/search/drilldowns;
5. observability/SLI/SLO/incidents/security settings.

## 8. Product information architecture target

1. **Command Center** — Overview + Decision Intel + authoritative safety strip.
2. **Market / Scanner** — market watch, scanner, ranked opportunities, signals.
3. **Options & Greeks** — Options Intel + Option Chain + full Greeks/IV/OI/liquidity.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + explainability/calibration.
5. **Paper / Trade Lifecycle** — paper order ticket + lifecycle + fills + positions + reconciliation/P&L.
6. **Portfolio & Risk** — funds/margin + positions exposure + scenarios + aggregate Greeks.
7. **Data & Broker Health** — Data Integrity + Broker + feed/source/freshness.
8. **Readiness / Proof** — Truth Control + E2E Proof + Live Gate.
9. **Observability** — Alerts + System + logs/SLI/SLO/incidents.
10. **Security / Settings** — sessions, permissions, policy, audit export, safe settings.

## 9. Positive foundations to preserve

- shared design tokens and numeric styling;
- reduced-motion preference;
- semantic sidebar navigation/ARIA attributes;
- visible pending states in unfinished workspaces;
- scanner-vs-prediction distinction in Prediction Audit direction;
- wrong-symbol option-chain suppression;
- source/snapshot/stale messaging foundation;
- bid/ask <=0 rendered missing rather than fake;
- bounded-concurrency E2E probes;
- Live Gate approval does not automatically enable live trading;
- Paper Trading states local simulated fills rather than implying a Dhan paper sandbox;
- analyzer/live-off design intent remains visible.

These are foundations, not readiness proof.

## 10. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is required audit posture, not a defect.

## 11. Closure standard

A finding becomes `CLOSED` only when applicable evidence is tied to the exact changed revision:

1. source/config fix inspected;
2. positive and negative tests added;
3. build/type/static checks pass;
4. unit/integration/browser tests pass;
5. runtime/deployment proof exists when required;
6. analyzer/live-off safety has no regression;
7. stale trackers regenerated;
8. screenshot/network/console evidence exists for UI changes;
9. frontend/backend schema reconciles;
10. no contradictory independent evidence remains.

## 12. Next audit / solution slices

1. **Risk + auto-gates backend** — map actual enforcement path; determine whether paper creation or any future order route can bypass displayed limits; define exact patch files/tests.
2. **Paper tick/backend lifecycle** — locate `/api/paper/tick`, simulator, DB/state store, fill model, idempotency and reconciliation owners before implementation.
3. **WebSocket/polling** — reconnect/backoff, stale retention, ordering, heartbeat, event timestamps and duplicate subscriptions; produce remediation plan.
4. **Option-chain backend normalization** — exact Greeks/IV source, timestamp, normalizer and schema owners; produce exact patch map.
5. **Observability / Cloud Run provenance** — runtime revision, image digest, latency, errors, browser failures and dependency truth.
6. **Responsive/accessibility** — desktop/tablet/mobile, keyboard, focus, live-region status announcements and dense-table behavior.

## 13. Hard safety rule

A green UI, successful build, endpoint HTTP 200, zero-valued P&L, `PAPER SAFE` badge or human approval never substitutes for source, freshness, lifecycle, risk, reconciliation, expectancy and runtime proof. During this audit, live order placement/modification/cancellation/routing remains prohibited.
