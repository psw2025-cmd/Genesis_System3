# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 01:48 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `b827db03eee1a3f8bc2731363a1c44b2af99af70`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after `b70af343...` in this loop are audit-report changes only; application findings remain tied to `b70af343...` unless a later application commit is explicitly named.
- Recent PR review still shows PR #96 as latest merged application/UI PR; PRs #93-#96 remain the latest security/UI changes inspected in this loop.
- Combined status contexts for application HEAD `b70af343...` are empty. This is not proof of CI failure, but it is also not same-revision readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render is migration debt and must not be treated as current target architecture.
- Audit posture: ANALYZER/PAPER, live-money routing OFF. No audit step may enable, place, modify, cancel or route a live order.
- This file is the single continuously maintained audit authority. Duplicate findings are merged here.

## 1. Executive verdict

| Area | Verdict | Evidence status |
|---|---|---|
| Current application HEAD CI proof | **NOT PROVEN** | no same-revision status contexts proving application HEAD |
| Dashboard login HTTP contract | **FAIL / P0** | frontend omits required JSON `api_key` body |
| Pre-auth protected polling | **FAIL / P1** | `useData()` starts before AuthGate completes |
| Browser API-key exposure | **FIX-REQUIRED / P1** | raw key retained in `sessionStorage` |
| Server session expiry | **PARTIAL / P1** | cookie age exists; independent server expiry/revocation not proven |
| Global mode truth | **FAIL / P0** | PAPER/LIVE-OFF presentation is not sourced from one authoritative safety contract |
| Truth Control money readiness | **FAIL / P0** | missing live/order fields default safe; paper lifecycle is excluded from money-ready calculation |
| E2E “Trader Ready” semantics | **FAIL / P0** | endpoint HTTP success can satisfy readiness rows without proving lifecycle, expectancy or semantic correctness |
| Risk-gate truth | **FAIL / P0-P1** | gate object presence can substitute for underlying gate completion |
| Option-chain truth | **FAIL / P0-P1** | warming state can fabricate PCR=1 and Dhan verification lacks full provenance envelope |
| Greeks UI | **INCOMPLETE / P1** | full Greeks not exposed; units/provenance not end-to-end proven |
| Paper Trading safety truth | **FAIL / P0** | missing mode/live/order fields can default to PAPER SAFE |
| Paper market-data truth | **FAIL / P0** | default source string can make absent market data look live |
| Paper P&L truth | **FAIL / P1** | missing values are coerced to ₹0.00 / zero-valued statistics |
| Position provenance | **FAIL / P1** | missing row fields can be displayed as INTRADAY / PAPER_CLOUD_SIM / DHAN_LIVE defaults |
| Trade workspace semantics | **INCOMPLETE / P1-P2** | current Trade tab is scanner + option-chain feed, not a pre-trade paper order/risk workstation |
| Prediction audit | **PENDING / REQUIRED** | immutable production prediction ledger not proven |
| Factor/scenario risk | **PENDING / REQUIRED** | complete enforceable portfolio/factor/scenario layer not proven |
| Responsive/mobile UI | **NOT PROVEN / P2** | application-shell breakpoints not proven |
| Accessibility focus proof | **NOT PROVEN / P2** | complete focus-visible/keyboard behavior not proven |
| Cloud Run analyzer/live-off workflow flags | **PASS IN SOURCE ONLY** | source keeps live disabled; runtime deployment truth still unproven |
| Real-market paper lifecycle | **NOT PROVEN** | no exact-revision proof of candidate→paper order→fill→MTM→exit→reconcile lifecycle |
| Multi-day positive costed expectancy | **NOT PROVEN** | no same-revision reproducible proof |
| Real-money trade ready | **NO** | P0/P1 truth, lifecycle, risk, auth and runtime blockers remain |

## 2. Iteration delta — Trade / Paper Trades / Positions deep slice

### Newly verified

1. **PAPER-001 / P0 — Paper Trading can declare PAPER SAFE from missing safety fields.** `PaperTrading.tsx` computes `liveTradingAllowed` from `String(state.live_trading_enabled || '0') === '1'`. Missing `live_trading_enabled` therefore becomes false. `orderCalled` is also false unless explicitly true. `paperTruthOk = !liveTradingAllowed && !orderCalled` can therefore become true when authoritative safety fields are absent. The default mode is also `PAPER`.
2. **PAPER-002 / P0 — Missing market-data source can become “live” by default.** `dataSource` defaults to `DHAN_LIVE_MARK_TO_MARKET`. `isLiveMarketSource()` treats any string containing `DHAN` as live, so absent backend source truth can make `marketLive=true` and produce `CHAIN LIVE` even with no authoritative feed proof.
3. **PAPER-003 / P1 — Missing monetary fields render as valid ₹0.00.** `money(v)` uses `Number(v || 0)`, and realized/unrealized/total P&L calculations also use zero fallbacks. Missing, schema-invalid or not-yet-proven values therefore collapse into legitimate-looking zeros rather than `UNKNOWN` / `NOT PROVEN`.
4. **PAPER-004 / P1 — Per-position provenance can be fabricated by UI fallbacks.** When position fields are absent, the Paper Trading table can display `INTRADAY`, `NSE_FNO`, `PAPER_CLOUD_SIM` and `DHAN_LIVE` as defaults. These are plausible production labels but are not proof that the row actually has those attributes.
5. **PAPER-005 / P1 — Paper safety proof is only negative evidence.** `paperTruthOk` requires live trading not detected and broker order endpoint not detected, but it does not require a proven paper ledger, explicit simulator identity/version, event correlation ID, fill engine version, freshness, reconciliation, or exact revision. “No live call seen” is necessary but insufficient paper lifecycle proof.
6. **PAPER-006 / P1 — Position page converts unproven summary state to numeric performance.** `Positions.tsx` defaults total P&L to 0, win rate to 0 and total trades to 0; an absent or not-yet-populated paper state can therefore look like a valid zero-performance account rather than a data-quality state.
7. **PAPER-007 / P1 — Empty positions are not provenance-aware.** `Positions.tsx` renders “No open positions” and “Paper engine generates positions during market hours” without proving whether the true state is `PROVEN_EMPTY`, `API_ERROR`, `AUTH_REQUIRED`, `STALE_LAST_GOOD`, `SCHEMA_ERROR`, `MARKET_CLOSED`, or `NO_LIFECYCLE_RUN`.
8. **TRADE-001 / P1-P2 — Current Trade tab is not an actual trade lifecycle workspace.** `TradeTab.tsx` contains scanner rankings, equity-options rows and the Option Chain. It has no paper order ticket, no quantity/entry/SL/TP controls, no pre-trade validation summary, no candidate/evidence ID, no duplicate/idempotency guard display, no paper-router state and no risk-budget confirmation. For a professional operator console, “Trade” should either be renamed or become the paper order + pre-trade risk workspace.
9. **TRADE-002 / P0-P1 — Rank can be displayed as a percentage.** `ScannerRow` displays `fmt(row.gain_pct ?? row.gain_rank ?? 0, 1)}%`. If `gain_pct` is missing but `gain_rank` exists, a rank integer is labeled as `GAIN %`. This independently reinforces the existing scanner-rank/validated-metric truth defect.
10. **TRADE-003 / P1 — Equity-options freshness label is ambiguous.** The Trade tab uses `liveOk > 0 ? "N live" : "EOD/live"`. `EOD/live` does not communicate event time, age, market state or whether the displayed rows are current, cached or fallback data.
11. **PAPER-008 / P1 — Force Paper Tick is a mutation without visible idempotency/correlation proof.** The UI exposes `POST /api/paper/tick` and then refreshes data, but the screen does not show correlation ID, request idempotency key, tick result event count, simulator version, affected positions, before/after state, or duplicate-run protection. This is analyzer/paper-safe only if the backend enforces those semantics; that enforcement is not proven in this slice.
12. **PAPER-009 / P1 — Paper lifecycle events are presented as tables, not an immutable event chain.** Open positions and today entries/exits are useful views, but the UI does not expose an event timeline linking candidate → decision → paper order → simulated fill → MTM updates → exit trigger → closure → reconciliation with one correlation/evidence ID.

### Positive controls to preserve

- Paper Trading explicitly states Dhan production tokens do not provide a paper sandbox and that fills are local simulation.
- Paper Trading exposes whether broker order endpoints were called and states that broker orders must remain off.
- The “Force Paper Tick” action is visibly labeled as paper and does not expose live-order routing in this UI.
- Position tables already contain useful fields such as entry, LTP, unrealized P&L, SL, target and provenance placeholders; these can be upgraded rather than replaced.
- Current Trade tab already co-locates scanner context and option chain, which is useful input context for a future pre-trade workspace.

## 3. Verification counters

Independent evidence only; rereading the same unchanged code does not increment.

| Finding | Conclusion | Counter | State |
|---|---|---:|---|
| AUTH-001 | LoginPage/backend session payload mismatch | `3/20` | OPEN |
| AUTH-002 | protected data starts before auth | `2/20` | OPEN |
| AUTH-003 | raw dashboard key remains JS-accessible | `2/20` | OPEN |
| UI-001 | missing telemetry/data can be shown as success/valid data | `6/20` | OPEN — Paper safety + paper market-source defaults add independent paths |
| UI-002 | rank/score mislabeled as validated percentage/forecast | `3/20` | OPEN — TradeTab `gain_rank`→`GAIN %` adds path |
| UI-003 | Dhan endpoint/source display misleading | `3/20` | OPEN — default `DHAN_LIVE_MARK_TO_MARKET` adds path |
| UI-004 | broker connectivity conflated with other truth domains | `2/20` | OPEN — Paper market-live combines source label/broker connection |
| UI-005 | unsafe fallback/default semantics | `6/20` | OPEN — PAPER/live/source/provenance defaults add independent paths |
| UI-006 | empty account/position data not distinguished from unproven response | `3/20` | OPEN — Positions empty-state adds path |
| UI-007 | responsive navigation not proven | `2/20` | OPEN |
| UI-008 | focus-visible/keyboard proof incomplete | `2/20` | OPEN |
| UI-009 | authoritative PAPER/LIVE truth missing | `5/20` | OPEN — Paper Trading safety calculation adds path |
| UI-010 | immutable production prediction ledger pending | `2/20` | OPEN |
| UI-011 | factor/scenario risk pending | `1/20` | OPEN |
| UI-016 | global readiness derived from weak proxy signals | `3/20` | OPEN |
| CHAIN-001 | warming chain fabricates PCR=1 | `1/20` | OPEN |
| CHAIN-002 | Dhan-looking chain lacks complete provenance envelope | `2/20` | OPEN |
| CHAIN-003 | full Greeks not exposed in Option Chain UI | `1/20` | OPEN |
| CHAIN-004 | chain-to-Greeks provenance not proven | `1/20` | OPEN |
| CHAIN-005 | IV unit/schema contract implicit | `1/20` | OPEN |
| READY-001 | missing live/order truth defaults safe | `2/20` | OPEN — PaperTrading independently reproduces default-safe logic |
| READY-002 | moneyReady excludes paper lifecycle | `1/20` | OPEN |
| READY-003 | risk-gate PASS from object presence | `1/20` | OPEN |
| READY-004 | account-read success semantics too weak | `1/20` | OPEN |
| READY-005 | trader-ready can pass transport without lifecycle/expectancy | `1/20` | OPEN |
| READY-006 | core PASS is transport-level only | `1/20` | OPEN |
| READY-007 | E2E Dhan proof lacks envelope | `1/20` | OPEN |
| READY-008 | Render-era wording remains in Live Gate | `1/20` | OPEN |
| READY-009 | approval gate proof lacks revision/timestamp provenance | `1/20` | OPEN |
| PAPER-001 | missing safety fields can yield PAPER SAFE | `1/20` | OPEN |
| PAPER-002 | missing data source can yield CHAIN LIVE | `1/20` | OPEN |
| PAPER-003 | missing money fields become ₹0.00 | `1/20` | OPEN |
| PAPER-004 | position provenance defaults can fabricate attributes | `1/20` | OPEN |
| PAPER-005 | paper-safe proof relies on negative evidence only | `1/20` | OPEN |
| PAPER-006 | position performance defaults to zero | `1/20` | OPEN |
| PAPER-007 | empty positions lack explicit truth state | `1/20` | OPEN |
| PAPER-008 | paper tick lacks visible idempotency/correlation proof | `1/20` | OPEN |
| PAPER-009 | immutable event-chain lifecycle not exposed | `1/20` | OPEN |
| TRADE-001 | Trade tab lacks order/pre-trade lifecycle controls | `1/20` | OPEN |
| TRADE-002 | gain rank can render as GAIN % | `1/20` | OPEN |
| TRADE-003 | EOD/live label lacks freshness truth | `1/20` | OPEN |

No finding is `LOCKED-20X`.

## 4. Critical authentication/security findings retained

### AUTH-001 — P0 — Login request does not satisfy backend contract
Frontend POSTs `/api/auth/session` without required JSON body containing `api_key`.

### AUTH-002 — P1 — Protected polling begins before authentication
Move protected subscriptions under authenticated runtime or require `enabled=authenticated` fail-closed behavior.

### AUTH-003 — P1 — Raw API key stored in browser sessionStorage
Remove persistence/reinjection after server session establishment.

### AUTH-004 — P1 — Server-side independent session expiry/revocation not proven
Use opaque server-side TTL session or signed expiring token with rotation/revocation.

## 5. Global truth and readiness contracts

### REQUIRED `SafetyTruth`

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
proof_status: PROVEN | STALE | UNKNOWN
```

Missing safety fields => `UNKNOWN — DO NOT TRADE`. Never coerce missing to false and then render green.

### REQUIRED `DataTruthEnvelope`

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

### REQUIRED `PaperLifecycleTruth`

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

A paper position or P&L number is not proven unless it is traceable to this lifecycle chain.

### REQUIRED `GateTruth`

Every gate requires `gate_id`, semantic status, threshold/value, evidence ID, exact source/runtime revision, verification time/age and policy version. Object presence or HTTP 200 is not PASS.

### REQUIRED readiness hierarchy

`transport_ok` < `schema_ok` < `source_proven` < `fresh` < `semantically_valid` < `reconciled` < `risk_passed` < `paper_lifecycle_proven` < `expectancy_proven` < `human_approval` < `live_router_armed`.

A higher state may never be inferred from a lower one.

## 6. Dashboard/UI truth findings retained

- **UI-001 / P0:** absence of telemetry/data can render as success or valid market/trading data.
- **UI-002 / P0-P1:** scanner/gain rank must not be presented as validated prediction or gain percentage without a typed metric contract.
- **UI-003 / P1:** operational Dhan REST/feed source truth must come from sanitized backend metadata, not UI defaults.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed, freshness, account reads, order permission and deployment provenance are independent domains.
- **UI-005 / P1:** nullish/schema-aware semantics required; missing values never become neutral market conclusions, safe booleans, money zeros or provenance labels.
- **UI-006 / P1:** account/position views need `LOADING`, `AUTH_REQUIRED`, `API_ERROR`, `SCHEMA_ERROR`, `PROVEN_EMPTY`, `ROWS_PRESENT`, `STALE_LAST_GOOD`, `MARKET_CLOSED`.
- **UI-007 / P1:** shared `DataTruthEnvelope` required for market/options analytics.
- **UI-009 / P0:** one authoritative runtime safety object must drive all PAPER/LIVE/LOCKED badges.
- **UI-010 / P1:** immutable production prediction ledger required for AI decisions.
- **UI-011 / P1:** factor/scenario risk and enforceable limits required before live-money assessment.
- **UI-012 / P2:** navigation should rationalize into operator workspaces rather than many isolated tabs.
- **UI-013 / P2:** responsive/mobile behavior not proven; mobile should begin read-only.
- **UI-014 / P2:** full keyboard/focus-visible behavior not proven.
- **UI-018 / P1:** build badge is not deployment compatibility proof.
- **UI-019 / P1:** broker state machine must distinguish auth/read/feed/degraded/stale/API/schema states.

## 7. Option Chain + Greeks findings retained

- **CHAIN-001 / P0:** warming state fabricates PCR=1. Use `pcr:null`, pending/no-data quality state.
- **CHAIN-002 / P1:** Dhan verification needs immutable provenance envelope with timestamps, age, schema, normalizer and completeness.
- **CHAIN-003 / P1:** expose Delta/Gamma/Theta/Vega with position overlay and aggregate portfolio Greeks.
- **CHAIN-004 / P1:** display Greeks calculation provenance: model/provider/version, rate source, expiry convention, IV source, spot source/time and calculation time.
- **CHAIN-005 / P1:** use canonical `iv_decimal` or explicit value+unit contract.

## 8. Readiness / Live Gate findings retained

- **READY-001 / P0:** missing live/order fields can default safe.
- **READY-002 / P0:** money-ready calculation excludes paper lifecycle.
- **READY-003 / P0-P1:** risk gate can PASS from object presence.
- **READY-004 / P1:** funds/holdings/positions success semantics are too weak.
- **READY-005 / P0:** E2E trader-ready can pass transport without lifecycle/expectancy proof.
- **READY-006 / P1:** E2E core PASS is transport-level.
- **READY-007 / P1:** E2E Dhan proof lacks full freshness/schema envelope.
- **READY-008 / P1:** Live Gate still contains Render-era instructions.
- **READY-009 / P1:** human approval display lacks exact evidence revision/timestamp provenance.

## 9. Paper / Trade Lifecycle target screen — REQUIRED

The current `Trade`, `Paper Trades`, and `Positions` capabilities should converge into one professional lifecycle workspace while retaining drill-down tabs.

### A. Paper order ticket

Candidate/evidence ID, contract, side, quantity, entry rule, SL, target/trailing, maximum risk, data age, market state, selected strategy, simulator identity and **paper router only**. Live router selection must not exist while safety proof is incomplete.

### B. Pre-trade validation

Before creating a paper order, show semantic checks for authentication, market/session truth, current tick/chain freshness, contract schema, duplicate/idempotency guard, risk budget, position conflict, margin simulation, SL/TP validity and kill-switch state.

### C. Immutable event lifecycle

`CANDIDATE → VALIDATED → PAPER_ORDER_CREATED → SIM_FILL → OPEN → MTM_UPDATE → EXIT_TRIGGER → CLOSED → RECONCILED`.

Every event needs event ID, correlation ID, timestamp, source revision, runtime revision, simulator version and evidence link.

### D. Position/P&L truth

Every displayed number must distinguish missing from zero. `₹0.00` is allowed only when a schema-valid proven numeric zero was returned. Rows must show market-data source/time/age and lifecycle provenance.

### E. Reconciliation

Expose ledger rows vs UI rows, open quantity reconciliation, realized/after-cost P&L reconciliation, missing events, duplicate events and stale last-good data.

### F. Force Paper Tick safety

If retained, display request correlation ID, idempotency key/result, simulator version, affected event count, before/after state and whether the request was a no-op duplicate. Never expose any live broker-order side effect.

## 10. World-class product information architecture

1. **Command Center** — Overview + Decision Intel summary + authoritative safety strip.
2. **Market / Scanner** — market watch, scanner, ranked opportunities, signals.
3. **Options & Greeks** — Options Intel + Option Chain + full Greeks/IV/OI/liquidity.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + explainability/calibration.
5. **Paper / Trade Lifecycle** — paper order ticket + lifecycle + fills + Positions + reconciliation/P&L.
6. **Portfolio & Risk** — funds/margin + positions exposure + scenarios + aggregate Greeks.
7. **Data & Broker Health** — Data Integrity + Broker + feed/source/freshness.
8. **Readiness / Proof** — Truth Control + E2E Proof + Live Gate.
9. **Observability** — Alerts + System + logs/SLI/SLO/incidents.
10. **Security / Settings** — sessions, permissions, policy, audit export, safe settings.

## 11. Positive foundations to preserve

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

## 12. Google Cloud / deployment findings

- Google Cloud Run remains deployment authority.
- root `render.yaml` is absent.
- Render wording in Live Gate remains a UI/safety migration blocker.
- Cloud Run workflow source keeps live disabled/analyzer mode enabled.
- Runtime closure requires exact frontend commit, backend commit, Cloud Run revision, image digest, authenticated health, Dhan truth, chains, funds/positions/holdings, browser proof and safety flags.

## 13. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is required audit posture, not a defect.

## 14. Closure standard

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

## 15. Next audit slices

1. **Risk + auto-gates backend** — displayed limits vs genuinely enforced pre-route gates and whether paper order creation can bypass them.
2. **WebSocket/polling** — reconnect/backoff, stale retention, ordering, heartbeat, event timestamps and duplicate subscriptions.
3. **Observability / Cloud Run provenance** — runtime revision, image digest, latency, errors, browser failures and service dependency truth.
4. **Responsive/accessibility** — desktop/tablet/mobile, keyboard, focus, status announcements and dense-table behavior.
5. **Option-chain backend normalization** — exact Greeks/IV source, timestamp, normalizer and schema proof.
6. **Paper tick/backend lifecycle** — idempotency, simulator fill model, event ledger, reconciliation and no-live-order enforcement.

## 16. Hard safety rule

A green UI, successful build, endpoint HTTP 200, zero-valued P&L, “PAPER SAFE” badge or human approval never substitutes for source, freshness, lifecycle, risk, reconciliation, expectancy and runtime proof. During this audit, live order placement/modification/cancellation/routing remains prohibited.