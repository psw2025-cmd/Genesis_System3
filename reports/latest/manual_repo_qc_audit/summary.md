# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 01:03 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `5d1ec87a43c5778f6d010b91dc3adcd6a22ae797`.
- Latest application/source HEAD remains: `b70af343340a73ed27ca548820d5893c779ab5bd`.
- Commits after `b70af343...` in this loop are audit-report changes only; application findings remain tied to `b70af343...` unless a later application commit is explicitly named.
- Combined commit-status contexts for `5d1ec87...` were empty. This is not proof of CI failure, but it is also not same-revision readiness proof.
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
| E2E “Trader Ready” semantics | **FAIL / P0** | endpoint HTTP success can satisfy several readiness rows without proving lifecycle, expectancy or semantic correctness |
| Risk-gate truth in System Truth | **FAIL / P0-P1** | presence of `auto_gates` object can mark risk gate PASS without proving individual gates passed |
| Funds/holdings/positions truth | **FAIL / P1** | batch response existence can be accepted unless `success === false`; explicit positive proof is not required |
| Live Gate UX/source truth | **FAIL / P1** | still carries Render-era instructions; approval UI can appear when technical rows pass, but displayed pass semantics need stronger provenance |
| Option-chain truth | **FAIL / P0-P1** | warming state can fabricate PCR=1 and Dhan verification lacks full provenance envelope |
| Greeks UI | **INCOMPLETE / P1** | full Greeks not exposed; units/provenance not end-to-end proven |
| Prediction audit | **PENDING / REQUIRED** | immutable production prediction ledger not proven |
| Factor/scenario risk | **PENDING / REQUIRED** | complete enforceable portfolio/factor/scenario layer not proven |
| Responsive/mobile UI | **NOT PROVEN / P2** | application-shell breakpoints not proven |
| Accessibility focus proof | **NOT PROVEN / P2** | complete focus-visible/keyboard behavior not proven |
| Cloud Run analyzer/live-off workflow flags | **PASS IN SOURCE ONLY** | source keeps live disabled; runtime deployment truth still unproven |
| Real-market paper lifecycle | **NOT PROVEN** | historical blocker remains |
| Multi-day positive costed expectancy | **NOT PROVEN** | no same-revision reproducible proof |
| Real-money trade ready | **NO** | P0/P1 truth, lifecycle, risk, auth and runtime blockers remain |

## 2. Iteration delta — System Truth / E2E Proof / Live Gate deep slice

### Newly verified

1. **READY-001 / P0 — Missing live-trading fields can default to a false-safe PASS in System Truth Control.** `SystemTruthControl.tsx` computes `liveFlag` and `orderAllowed` with `?? false`. If authoritative fields are absent from both state and broker responses, both become false and the `Live-money safety lock` row becomes PASS. Absence therefore means safe rather than UNKNOWN.
2. **READY-002 / P0 — `moneyReady` excludes paper/analyzer lifecycle.** The `Paper/analyzer lifecycle` row is created with `requiredForMoney: false`, while `moneyReady` is the `every(PASS)` result only across `requiredForMoney` rows. A system can therefore become money-ready even when no paper lifecycle proof exists.
3. **READY-003 / P0-P1 — Risk-gate PASS is based on object presence, not semantic gate completion.** `mapped.gates.ok` is true when batch market data contains any truthy `auto_gates` object. The `Risk gates and automation status` row then becomes PASS from that boolean without requiring each required risk gate to pass or checking stale/failed sub-gates.
4. **READY-004 / P1 — Funds, holdings and positions accept weak success semantics.** In `SystemTruthControl.tsx`, funds/holdings/positions are considered `ok` when the batch endpoint itself succeeded and nested `success !== false`. Missing `success`, partial payloads, stale last-good payloads or schema-incomplete responses can therefore be treated as successful unless another explicit error field is present.
5. **READY-005 / P0 — E2E `TRADER READY` can pass based on HTTP success instead of trading proof.** In `EndToEndProof.tsx`, the paper/analyzer P&L row passes on `pnl?.ok`, today lifecycle passes on `trades?.ok`, and gate visibility passes on `gates?.ok`. There is no requirement here for non-empty real paper lifecycle, reconciliation, positive after-cost expectancy, gate-by-gate pass truth or exact-revision provenance.
6. **READY-006 / P1 — E2E core PASS is transport-level.** `corePass` is `core.every(p => p.ok)`. HTTP 2xx across endpoints is useful transport evidence but not proof that returned state is authoritative, fresh, semantically valid or internally consistent.
7. **READY-007 / P1 — E2E Dhan chain proof still lacks authoritative freshness/schema envelope.** `isDhanChain()` rejects obvious bad source strings and requires source `dhan`, positive contracts and spot, but does not require event time, received time, age threshold, schema/normalizer version, row completeness or backend-issued proof status.
8. **READY-008 / P1 — Live Gate retains Render-era operator instruction.** `LiveTradingGate.tsx` says live enablement must be manually changed on Render and its footer also names Render. This contradicts the Google Cloud target and creates operator confusion in a critical safety screen.
9. **READY-009 / P1 — Live Gate approval UI is safer than automatic activation, but proof provenance is incomplete.** The UI explicitly states that human approval does not automatically enable live trading, which is positive. However the decision to reveal approval is driven by the gate rows supplied by `/api/live-trading/gate`; the UI does not display gate evidence revision, timestamp, age or policy version, so a pass cannot yet be tied to exact current runtime proof.

### Important positive controls to preserve

- Live Gate does **not** automatically turn on live trading after approval.
- E2E probes use bounded concurrency, timeout, retry handling and `cache: no-store`.
- System Truth separates required and optional chain symbols.
- After-hours Dhan snapshot intent is explicitly recognized.
- Critical screens are designed as proof/read-only surfaces rather than order-placement surfaces.

## 3. Verification counters

Independent evidence only; rereading the same unchanged code does not increment.

| Finding | Conclusion | Counter | State |
|---|---|---:|---|
| AUTH-001 | LoginPage/backend session payload mismatch | `3/20` | OPEN |
| AUTH-002 | protected data starts before auth | `2/20` | OPEN |
| AUTH-003 | raw dashboard key remains JS-accessible | `2/20` | OPEN |
| UI-001 | missing telemetry can be shown as success | `4/20` | OPEN — System Truth missing live/order fields add independent path |
| UI-002 | rank mislabeled as validated forecast | `2/20` | OPEN |
| UI-003 | Dhan endpoint display misleading | `2/20` | OPEN |
| UI-004 | broker connectivity conflated with other truth domains | `1/20` | OPEN |
| UI-005 | unsafe fallback/default semantics | `3/20` | OPEN — live/order `?? false` adds independent default-safe path |
| UI-006 | empty account data not distinguished from unproven response | `2/20` | OPEN |
| UI-007 | responsive navigation not proven | `2/20` | OPEN |
| UI-008 | focus-visible/keyboard proof incomplete | `2/20` | OPEN |
| UI-009 | authoritative PAPER/LIVE truth missing | `4/20` | OPEN — System Truth defaults add another independent path |
| UI-010 | immutable production prediction ledger pending | `2/20` | OPEN |
| UI-011 | factor/scenario risk pending | `1/20` | OPEN |
| UI-016 | global readiness incorrectly derived from weak proxy signals | `3/20` | OPEN |
| CHAIN-001 | warming chain fabricates PCR=1 | `1/20` | OPEN |
| CHAIN-002 | Dhan-looking chain lacks complete provenance envelope | `2/20` | OPEN — E2E chain proof independently repeats weakness |
| CHAIN-003 | full Greeks not exposed in Option Chain UI | `1/20` | OPEN |
| CHAIN-004 | chain-to-Greeks provenance not proven | `1/20` | OPEN |
| CHAIN-005 | IV unit/schema contract implicit | `1/20` | OPEN |
| READY-001 | missing live/order truth defaults safe | `1/20` | OPEN |
| READY-002 | moneyReady excludes paper lifecycle | `1/20` | OPEN |
| READY-003 | risk-gate PASS from object presence | `1/20` | OPEN |
| READY-004 | account-read success semantics too weak | `1/20` | OPEN |
| READY-005 | trader-ready can pass transport without lifecycle/expectancy | `1/20` | OPEN |
| READY-006 | core PASS is transport-level only | `1/20` | OPEN |
| READY-007 | E2E Dhan proof lacks envelope | `1/20` | OPEN |
| READY-008 | Render-era wording remains in Live Gate | `1/20` | OPEN |
| READY-009 | approval gate proof lacks revision/timestamp provenance | `1/20` | OPEN |

No finding is `LOCKED-20X`.

## 4. Critical authentication/security findings

### AUTH-001 — P0 — Login request does not satisfy backend contract

Frontend POSTs `/api/auth/session` without required JSON body containing `api_key`.

**Target:** one typed bootstrap auth client; credential used once over HTTPS; establish HttpOnly/Secure/SameSite session; no raw-key persistence.

**Closure:** valid key 200 + session; invalid 401; missing body 422; refresh remains authenticated; zero key leakage in logs/devtools storage.

### AUTH-002 — P1 — Protected polling begins before authentication

Move protected subscriptions under authenticated runtime or require `enabled=authenticated` fail-closed behavior.

### AUTH-003 — P1 — Raw API key stored in browser sessionStorage

Remove persistence/reinjection after server session establishment.

### AUTH-004 — P1 — Server-side independent session expiry/revocation not proven

Use opaque server-side TTL session or signed expiring token with rotation/revocation.

## 5. Global truth and readiness contract

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

**Rule:** missing safety fields => `UNKNOWN — DO NOT TRADE`. Never coerce missing to false and then render green.

### REQUIRED `GateTruth`

Every gate must contain:

```text
gate_id
status: PASS | FAIL | BLOCKED | STALE | UNKNOWN | NOT_RUN
required_for_live_money
value
threshold
source
evidence_id
source_revision
runtime_revision
verified_at
age_ms
policy_version
```

No UI may mark risk/gate PASS merely because an object or HTTP endpoint exists.

### REQUIRED readiness hierarchy

`transport_ok` < `schema_ok` < `source_proven` < `fresh` < `semantically_valid` < `reconciled` < `risk_passed` < `paper_lifecycle_proven` < `expectancy_proven` < `human_approval` < `live_router_armed`.

A higher state may never be inferred from a lower one.

## 6. Dashboard/UI truth findings retained

- **UI-001 / P0:** absence of telemetry/data can render as success or a valid market statistic.
- **UI-002 / P0-P1:** scanner/gain rank must not be called validated prediction until immutable prediction proof exists.
- **UI-003 / P1:** operational Dhan REST/feed hosts must come from sanitized backend metadata, not misleading labels.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed, freshness, account reads, order permission and deployment provenance are independent domains.
- **UI-005 / P1:** nullish/schema-aware semantics required; missing values never become neutral market conclusions or safe booleans.
- **UI-006 / P1:** account views need `LOADING`, `AUTH_REQUIRED`, `API_ERROR`, `SCHEMA_ERROR`, `PROVEN_EMPTY`, `ROWS_PRESENT`, `STALE_LAST_GOOD`.
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

### CHAIN-001 — P0 — Warming state fabricates PCR=1

Use `pcr: null`, `pendingProof: true`, `quality_state: NO_DATA`; disable analytics until proven source rows exist.

### CHAIN-002 — P1 — Dhan verification needs immutable provenance envelope

Require provider/session, underlying/expiry, source event time, backend received time, frontend received time, age, freshness threshold, market state, schema version, normalizer version, row completeness and backend-issued proof status.

### CHAIN-003 — P1 — Full Greeks missing in current chain screen

Expose Delta/Gamma/Theta/Vega with compact/expanded modes, position overlay and aggregate portfolio Greeks.

### CHAIN-004 — P1 — Greeks calculation provenance not proven

Display calculator/provider source, model version, risk-free-rate source/time, expiry/timezone convention, IV source/solver, spot source/time, calculation time and stale threshold.

### CHAIN-005 — P1 — IV unit contract implicit

Use canonical `iv_decimal` or explicit `iv_value + iv_unit` and provider normalization tests.

## 8. World-class product information architecture

Current repo capabilities should be rationalized, not deleted:

1. **Command Center** — Overview + Decision Intel summary + authoritative safety strip.
2. **Market / Scanner** — market watch, scanner, ranked opportunities, signals.
3. **Options & Greeks** — Options Intel + Option Chain + full Greeks/IV/OI/liquidity.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + explainability/calibration.
5. **Paper / Trade Lifecycle** — Trade + Paper Trades with event/correlation trace.
6. **Portfolio & Risk** — Positions + funds/margin + scenarios + aggregate Greeks.
7. **Data & Broker Health** — Data Integrity + Broker + feed/source/freshness.
8. **Readiness / Proof** — Truth Control + E2E Proof + Live Gate.
9. **Observability** — Alerts + System + logs/SLI/SLO/incidents.
10. **Security / Settings** — sessions, permissions, policy, audit export, safe settings.

## 9. Readiness / Proof target screen — REQUIRED

The target screen must separate five layers visually:

### Layer A — Runtime safety

Mode, live flag, auto-execute flag, router state, kill switch, runtime revision, proof age.

### Layer B — Data/broker truth

Dashboard auth, Dhan REST auth, feed state, market session, last event age, funds/holdings/positions read truth, chain source/age/schema.

### Layer C — Trading proof

Scanner candidate proof, prediction-ledger proof, paper order/fill lifecycle, reconciliation, after-cost expectancy, multi-day stability.

### Layer D — Risk proof

Daily loss headroom, margin, concentration, portfolio Greeks, scenario limits, enforceable pre-trade gates.

### Layer E — Human/live activation

Human approval is the final administrative step only after all required technical/economic proof is current. It never substitutes for proof and never auto-enables routing.

Every row links to evidence ID, revision, verified time and age. Any stale/missing proof immediately downgrades the overall state.

## 10. Positive foundations to preserve

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
- analyzer/live-off design intent remains visible.

These are foundations, not readiness proof.

## 11. Google Cloud / deployment findings

- Google Cloud Run remains deployment authority.
- root `render.yaml` is absent.
- Render wording in Live Gate is now a specific UI/safety migration blocker: `READY-008`.
- Cloud Run workflow source keeps live disabled/analyzer mode enabled.
- Runtime closure requires exact frontend commit, backend commit, Cloud Run revision, image digest, authenticated health, Dhan truth, chains, funds/positions/holdings, browser proof and safety flags.

## 12. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` is required audit posture, not a defect.

## 13. Closure standard

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

## 14. Next audit slices

1. **Paper Trading + Trade + Positions** — lifecycle transitions, fill/reconciliation/P&L truth, zero-vs-error semantics.
2. **Risk + auto-gates backend** — displayed limits vs genuinely enforced pre-route gates.
3. **WebSocket/polling** — reconnect/backoff, stale retention, ordering, heartbeat, event timestamps.
4. **Observability / Cloud Run provenance** — runtime revision, image, latency, errors, browser failures.
5. **Responsive/accessibility** — desktop/tablet/mobile, keyboard, focus, status announcements.
6. **Option-chain backend normalization** — exact Greeks/IV source, timestamp, normalizer and schema proof.

## 15. Hard safety rule

A green UI, successful build, endpoint HTTP 200 or human approval never substitutes for source, freshness, lifecycle, risk, reconciliation, expectancy and runtime proof. During this audit, live order placement/modification/cancellation/routing remains prohibited.
