# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 04:51 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `b9a10ce5aa23284bbf5dd02d45667659b7125784`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd` (`fix(ui): final cleanup - remove all blocked/unavailable terminology`).
- Commits after `b70af343...` remain audit-report-only in the current evidence set.
- Recent PRs rechecked: PR #96 remains the newest merged application/UI PR; #92-#96 remain relevant to V5 UI/auth behavior. No newer application PR was found in this iteration.
- Workflow-run lookup for application HEAD `b70af343...` returned no runs through the connector. This is neither CI-failure proof nor exact-revision CI/runtime readiness proof.
- Deployment target: Google Cloud Run / Google Cloud services. Render references are migration debt only.
- Audit posture: ANALYZER/PAPER. Live-money routing remains OFF. No audit action may place, modify, cancel or route a live order.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision proof required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` + event ordering |
| Data/source/staleness truth | **FAIL / P0-P1** | **READY TO PATCH** via typed envelopes |
| Option chain / Greeks | **INCOMPLETE / P0-P1** | warming fix ready; provenance contract required |
| Paper UI mutation control | **FAIL / P0-P1** | **READY TO PATCH** capability-driven |
| Paper execution lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper restart/idempotency safety | **FAIL / P0-P1** | **READY TO PATCH** durable ledger |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| Google Cloud provenance | **NOT PROVEN / P1** | exact revision/image/runtime evidence required |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, schema/API changes, compatibility/migration notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation status `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, PAPER SAFE, LIVE, fresh-market-data, broker-connected or trade-ready through frontend/backend defaults.

## 3. Retained verified findings

### Authentication / session

- **AUTH-001 / P0:** frontend login request body does not match backend `api_key` contract.
- **AUTH-002 / P1:** protected data polling starts before auth is established.
- **AUTH-003 / P1:** raw dashboard key is stored in browser `sessionStorage` and re-injected.
- **AUTH-004 / P1:** independent server session expiry/revocation proof remains incomplete.

### Global UI / data truth

- **UI-001 / P0:** absence/error can become plausible valid-looking data.
- **UI-002 / P0-P1:** rank/score can be mislabeled as gain/forecast percentage.
- **UI-003 / P1:** source identity can be inferred from frontend fallbacks rather than backend provenance.
- **UI-004/UI-016 / P0-P1:** dashboard auth, Dhan auth, feed, freshness, account reads, router permission and deployment provenance are separate truth domains but are sometimes conflated.
- **UI-005 / P1:** permissive defaults collapse unknown into safe/neutral values.
- **UI-006 / P1:** empty state is not consistently distinguished from `PROVEN_EMPTY`, API/auth/schema/stale/no-run states.
- **UI-007 / P1:** shared market-data truth envelope is missing.
- **UI-009 / P0:** PAPER/LIVE/LOCKED is not driven by one authoritative runtime safety object.
- **UI-010 / P1:** immutable production prediction ledger remains unproven.
- **UI-011 / P1:** complete enforceable portfolio/factor/scenario risk remains unproven.
- **UI-012/UI-013/UI-014 / P2:** workspace rationalization, responsive/mobile and keyboard/focus behavior remain incomplete/unproven.
- **UI-018 / P1:** source/build labels are not deployment compatibility proof.
- **UI-019 / P1:** broker health requires a typed state machine.

### Option chain / Greeks

- **CHAIN-001 / P0:** warming/no-data chain can produce `PCR=1` instead of unknown.
- **CHAIN-002 / P1:** Dhan-looking chain verification lacks complete event-time/freshness/schema/normalizer/completeness proof.
- **CHAIN-003 / P1:** full Delta/Gamma/Theta/Vega are not displayed in Option Chain.
- **CHAIN-004 / P1:** Dhan row → normalized inputs → Greeks calculator → UI provenance is not proven end to end.
- **CHAIN-005 / P1:** IV unit/schema is implicit.

### Readiness / gates

- **READY-001 / P0:** missing live/order evidence can default safe.
- **READY-002 / P0:** money-ready calculation excludes required paper lifecycle proof.
- **READY-003 / P0-P1:** gates can pass from object presence/shape instead of semantic checks.
- **READY-004 / P1:** funds/holdings/positions success semantics are too weak.
- **READY-005 / P0:** trader-ready can pass transport checks without lifecycle/expectancy proof.
- **READY-006 / P1:** core E2E PASS is transport-level only.
- **READY-007 / P1:** Dhan proof lacks full freshness/schema envelope.
- **READY-008 / P1:** active Live Gate contains Render-era instructions.
- **READY-009 / P1:** human approval lacks exact evidence revision/time provenance.

### Paper / Trade / Positions

- **PAPER-001 / P0:** missing safety fields can yield `PAPER SAFE`.
- **PAPER-002 / P0:** missing market source can yield live-looking Dhan state.
- **PAPER-003 / P1:** missing monetary fields can render `₹0.00`.
- **PAPER-004 / P1:** missing provenance can display plausible `INTRADAY/NSE_FNO/PAPER_CLOUD_SIM/DHAN_LIVE` defaults.
- **PAPER-005 / P1:** paper-safe proof relies heavily on negative evidence rather than simulator/ledger proof.
- **PAPER-006 / P1:** position performance defaults to zero.
- **PAPER-007 / P1:** empty positions lack explicit truth state.
- **PAPER-008 / P1:** Force Paper Tick lacks idempotency/correlation proof.
- **PAPER-009 / P1:** immutable lifecycle event chain is not exposed.
- **PAPER-010 / P0-P1:** Force Paper Tick calls an unproven `/api/paper/tick` capability.
- **PAPER-011 / P0:** direct `run_live_chain.py -> PaperExecutor.execute_trade()` bypasses canonical pre-trade risk authority.
- **PAPER-012 / P0-P1:** process-local executor IDs/state are restart-unsafe.
- **PAPER-013 / P1:** missing contract update can reuse last price for MTM/exit logic without explicit stale quality.
- **PAPER-014 / P1:** realized P&L is not proven after-cost/reconciled.
- **PAPER-015 / P1:** paper read APIs can collapse load/parse errors into empty/zero-looking truth.
- **PAPER-016 / P0-P1:** `paper_truth` statically declares safety instead of measured authority.
- **TRADE-001 / P1-P2:** current Trade tab is scanner/chain context, not a controlled paper-order/risk workstation.
- **TRADE-002 / P0-P1:** `gain_rank` can render as `GAIN %`.
- **TRADE-003 / P1:** `EOD/live` does not prove freshness.
- **LEGACY-001 / P0-P1:** legacy Streamlit UI retains mutation-oriented controls; deployment exposure remains UNPROVEN.

### Risk

- **RISK-001 / P0:** browser supplies risk limits instead of selecting server-owned policy.
- **RISK-002 / P0:** missing risk policy can use permissive defaults.
- **RISK-003 / P0-P1:** unavailable risk inputs can become zero risk.
- **RISK-004 / P1:** existing VaR is not a reproducible institutional portfolio VaR contract.
- **RISK-005 / P0:** execution guardrail fails open on missing market/instrument/trade-count evidence.
- **RISK-006 / P0:** canonical risk guardrail wiring into execution path is unproven.
- **RISK-007 / P1:** Risk & Scenarios uses a non-contract gate proxy.
- **RISK-008 / P0-P1:** lifecycle gate can promote from position shape instead of immutable lifecycle proof.
- **RISK-009 / P1:** auto-gate refresh/evaluation errors can retain old artifacts.

## 4. New deep-slice findings — WebSocket, polling, freshness and ordering

### WS-001 / P1 — transport OPEN is immediately labeled `live` before data freshness is proven

In `dashboard/frontend/src/hooks/useData.ts`, `ws.onopen` resets reconnect attempts and executes `setWsStatus('live')`. No heartbeat, market-data event, schema validation or event-age threshold is required before the product declares the WebSocket live.

**Root cause:** transport connectivity and data-stream health are represented by one string.

**Impact:** an idle, stalled or semantically broken socket can look healthy to the operator.

**Solution:** create `StreamTruth` with separate `transport_state`, `heartbeat_state`, `event_flow_state`, `last_event_at`, `age_ms`, `freshness_threshold_ms`, `schema_state`, `source_state`, `sequence_state`. `onopen` may set only `TRANSPORT_CONNECTED`; `STREAM_HEALTHY` requires fresh valid heartbeat plus fresh domain events.

**Files:** `dashboard/frontend/src/hooks/useData.ts`, store schema, TopBar/Data Integrity/Broker panels; backend stream envelope/heartbeat owner.

**Tests:** open socket with zero events => not LIVE; stale heartbeat => STALE; malformed message => SCHEMA_ERROR; valid heartbeat + fresh event => HEALTHY.

**Status:** `READY TO PATCH`.

### WS-002 / P0-P1 — heartbeat logic can false-green `live`

Current heartbeat handling sets error only when `m.market_open && m.stream_ok === false`; every other heartbeat executes `setWsStatus('live')`. Therefore `stream_ok` missing/undefined, market closed, or structurally incomplete heartbeat can still paint LIVE.

**Root cause:** boolean negative check instead of an explicit heartbeat contract.

**Solution:** heartbeat schema must require `stream_ok`, `market_state`, `source`, `server_time`, `last_source_event_time`, `sequence`, `schema_version`, `runtime_revision`. Missing required fields => `UNKNOWN/SCHEMA_ERROR`, never LIVE. Market closed becomes `MARKET_CLOSED`, not LIVE.

**Status:** `READY TO PATCH`.

### WS-003 / P1 — REST polling and WS writes have no monotonic ordering guard

`useData()` keeps REST core polling active every 20s/60s while the WebSocket simultaneously writes health, paper, P&L, chain, scanner/ranker and market state. State updates do not compare source event time, sequence number, revision or receive time before overwriting each other.

**Impact:** an older REST response can overwrite a newer WS event, or vice versa, producing time-travel/contradictory UI state.

**Solution:** every domain update carries `{event_id, sequence, source_event_time, backend_received_time, snapshot_revision}`. Store reducers accept an update only if it is newer according to domain ordering rules. REST is fallback/snapshot truth, not an unversioned competing writer.

**Regression risk:** previously accepted out-of-order updates will be rejected; diagnostics must expose rejected-old-event counts.

**Status:** `READY TO PATCH`.

### WS-004 / P1 — chain spot WS update can retain an old spot and still mark it live

`chain_spots_update` computes `spot: Number(info.spot || prev.spot || 0)`, falls back source to `'dhan'`, stamps a new `stream_tick_at`, and sets `live` from the UI market-open flag. If the incoming event lacks spot/source, an old spot can be retained while the new envelope appears current/live.

**Solution:** do not stamp freshness when the field was not supplied by the event. Track field-level provenance or reject incomplete chain-spot events. `live=true` requires fresh source event time and validated Dhan provenance, not merely market-open state.

**Status:** `READY TO PATCH`.

### WS-005 / P1 — market-top WS events become `status:'ok'` without freshness/schema proof

`market_top_update` builds rankings and stores `status:'ok'`, source `ws_market_top_micro`, and recommendation `WATCH` without validating event age, sequence, schema version or provenance completeness.

**Solution:** validate `MarketTopEnvelope`; ranking remains `UNKNOWN/STALE` when provenance/freshness is incomplete. Scanner rank stays distinct from prediction probability and realized gain.

**Status:** `READY TO PATCH`.

### WS-006 / P1 — malformed WebSocket payloads are silently ignored

The WS message handler catches JSON/processing failures and performs no alert/status transition.

**Impact:** schema drift or corrupted events can silently stop updating some panels while transport remains green.

**Solution:** increment typed parse/schema error counters, preserve redacted sample metadata, set affected domain to `SCHEMA_ERROR`, surface alert/observability entry, and trip stream health after a bounded threshold.

**Status:** `READY TO PATCH`.

### WS-007 / P1 — last-good retention preserves the previous status label

`keepLastGood()` sets `stale:true` but retains `status: previous.status || 'TRANSIENT_CACHE'`. A previously `ok/live` status can therefore coexist with stale data if downstream components key on status rather than the stale flag.

**Solution:** stale wrapper has authoritative quality state `STALE_LAST_GOOD`; original status is moved to `last_good_status` for diagnostics only. Rendering must use quality state first.

**Status:** `READY TO PATCH`.

### WS-008 / P1 — standalone `useWebSocket.ts` duplicates connection/fallback policy and appears unused

The repository contains a second WebSocket hook with different reconnect cadence, market-hours behavior and polling fallback. Repository search found its definition but no independent consumer in the current V5 frontend evidence set.

**Impact:** duplicate connection policies create drift/dead-code risk and make future use likely to reintroduce inconsistent stream semantics.

**Solution:** remove/quarantine the unused hook or make a single `StreamTransportService` the only transport owner. CI should reject a second direct `new WebSocket(...)` owner outside approved transport modules.

**Status:** `READY TO PATCH` after import/build proof confirms no consumer.

### WS-009 / P0-P1 — WebSocket health proof does not actually prove a WebSocket connection

`scripts/websocket_tick_health_proof.py` fetches `/api/state`, reads `last_tick_age_sec`, broker state and refresh interval, and can PASS using REST polling. It defines `/ws/stream` only as a string and never opens a WebSocket. The script note explicitly allows REST SSOT polling for analyzer PASS.

**Impact:** a proof named WebSocket Tick Health can pass without WebSocket transport/e2e event evidence; this cannot support institutional streaming-readiness claims.

**Solution:** split proof into `REST_SSOT_FRESHNESS` and `WEBSOCKET_STREAM_HEALTH`. WS proof must authenticate, connect, receive server hello/heartbeat plus at least one valid event during market conditions or a deterministic test fixture, verify sequence/time/schema/source, calculate event age and reconnect behavior, then store exact runtime revision evidence.

**Status:** `READY TO PATCH`.

### WS-010 / P0-P1 — backend `last_tick_age_sec` is artificially capped and parse failures can appear bounded

`dashboard/backend/state_sync_service.py` derives age from state timestamps, but on parse failure substitutes `_sync_interval`, then publishes `last_tick_age_sec = min(age_sec, _sync_interval * 2)`. An arbitrarily old source can therefore never report older than twice the sync interval through this metric.

**Impact:** stale state can look bounded/fresh enough for downstream proofs; current `websocket_tick_health_proof.py` consumes this field.

**Solution:** never cap source age. Publish separate `source_event_age_sec`, `state_sync_age_sec`, `last_successful_source_event_at`, `last_successful_sync_at`; parse error => `age=null`, `quality=SCHEMA_ERROR`. Proofs must use uncapped source-event age.

**Status:** `READY TO PATCH`.

### WS-011 / P1 — `/ws/stream` backend capability is not proven by current repository search

Frontend code and reports refer to `/ws/stream`, but this iteration's repository searches did not locate a concrete FastAPI WebSocket route implementation. This is recorded as **UNPROVEN**, not asserted absent, because search indexing can miss route construction/import indirection.

**Solution:** route inventory must enumerate WebSocket routes from the actual ASGI app at test/runtime, record owning module, auth policy and message schema. UI connection controls depend on this capability result.

**Status:** `UNPROVEN / READY TO VERIFY`.

### Existing runtime artifact regression check

`reports/latest/websocket_tick_health/summary.md` at application HEAD reports `Pass: False` and tick age `5.03`. This confirms the repository's latest stored WebSocket-health artifact is not a PASS; it does not establish current runtime state.

## 5. Canonical truth contracts

### 5.1 `SafetyTruth`

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

### 5.2 `DataTruthEnvelope`

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
quality_state: PROVEN | PROVEN_EMPTY | STALE | NO_DATA | API_ERROR | AUTH_REQUIRED | SCHEMA_ERROR | UNKNOWN
source_revision
runtime_revision
```

### 5.3 `StreamTruth` — NEW

```text
transport_state: DISCONNECTED | CONNECTING | CONNECTED | ERROR
stream_state: HEALTHY | STALE | MARKET_CLOSED | DEGRADED | UNKNOWN | SCHEMA_ERROR
heartbeat_state: FRESH | STALE | MISSING | INVALID
last_heartbeat_at
last_source_event_at
last_backend_receive_at
last_frontend_receive_at
event_age_ms
freshness_threshold_ms
last_sequence
rejected_old_events
parse_error_count
schema_version
source
provider_session
rest_fallback_state
rest_snapshot_revision
runtime_revision
source_revision
```

### 5.4 `PaperLifecycleTruth`

`correlation_id`, candidate/prediction IDs, paper order/fill/position/exit IDs, idempotency key, simulator version, market truth ID/time, risk decision ID, entry/exit slippage, fees/taxes, gross/net P&L, reconciliation state, ledger/runtime/source revisions.

### 5.5 `GateTruth`, `RiskPolicy`, `PreTradeRiskTruth`, `PaperMutationCapability`

Retain the existing fail-closed contracts: semantic gate status with evidence/revision/age; server-owned immutable risk policy; fresh pre-trade risk decision; capability-driven paper mutation only when exact-revision proof is `PROVEN`.

## 6. Canonical remediation roadmap

- **SOL-01 Auth/session — READY TO PATCH:** correct login body, cookie-only browser auth, remove raw API key storage, gate all polling/WS startup behind auth, add TTL/revocation tests.
- **SOL-02 SafetyTruth — READY TO PATCH:** one backend safety authority for TopBar/Truth/E2E/Paper/Live Gate; missing/stale => UNKNOWN.
- **SOL-03 DataTruthEnvelope — READY TO PATCH:** remove production `||0`/plausible defaults; explicit provenance/time/age/schema/quality; only valid empty ledger/account result becomes `PROVEN_EMPTY`.
- **SOL-04 Semantic readiness — READY TO PATCH:** HTTP 200/object presence never equals PASS; lifecycle, reconciliation, enforceable risk and positive after-cost expectancy remain mandatory.
- **SOL-05 Options/Greeks — READY TO DESIGN/PATCH:** complete row schema, explicit IV units/model assumptions, full Greeks and portfolio aggregation.
- **SOL-06 Immutable paper lifecycle — READY TO PATCH:** canonical paper mutation service, durable IDs/idempotency/event ledger, restart replay/reconciliation, costed P&L, stale MTM inhibition.
- **SOL-07 Scanner contract — READY TO PATCH:** nullable distinct rank/score/probability/forecast/realized fields; no rank→percent fallback.
- **SOL-08 GCP provenance — READY TO PATCH/DESIGN:** remove Render instructions; exact frontend/backend commit, Cloud Run revision, image digest, deploy time, policy/entrypoint proof.
- **SOL-09 PreTradeRiskService — READY TO PATCH:** server-owned policy and mandatory fresh PASS before every paper mutation; UNKNOWN/ERROR denies.
- **SOL-10 Legacy UI quarantine — READY TO PATCH:** production entrypoint guard; no legacy mutation controls in deployed navigation/runtime.
- **SOL-11 StreamTruth + ordered state merge — NEW / READY TO PATCH:** consolidate WebSocket transport ownership; separate transport from stream health; validate heartbeat/event schemas; monotonic per-domain merge; uncapped event age; typed REST fallback; stale watermark; observability counters.

### SOL-11 ordered implementation

1. Define backend `StreamEventEnvelope` and frontend `StreamTruth` types.
2. Require event ID/sequence/source event time/backend receive time/schema/source/runtime revision on WS domain events.
3. Change WS `onopen` to `TRANSPORT_CONNECTED`, never `live`.
4. Validate heartbeat schema; missing fields => UNKNOWN/SCHEMA_ERROR.
5. Add domain reducers with monotonic sequence/time/revision checks so REST cannot overwrite newer WS data.
6. Replace `keepLastGood` status preservation with `STALE_LAST_GOOD` quality state.
7. Reject/inhibit incomplete `chain_spots_update`; never refresh timestamp using retained old spot.
8. Validate market-top envelope before `status=ok`.
9. Surface parse/schema errors; no silent catch.
10. Remove/quarantine unused duplicate `useWebSocket.ts` or make it the sole approved transport service.
11. Replace capped backend tick age with uncapped source-event age + independent sync age.
12. Split REST freshness proof from true WS proof and add ASGI WebSocket route-inventory test.
13. UI Data/Broker Health screen displays transport, heartbeat, event age, sequence, source, REST fallback and rejected-old-event counts separately.

**SOL-11 PASS criteria:** connected socket with no data is not LIVE; incomplete heartbeat never green; source-event age is uncapped; malformed events surface error; stale last-good is visibly stale; older REST/WS update cannot overwrite newer domain state; no duplicate WebSocket transport owner; WS proof actually opens the socket; exact route/auth/schema owner is proven; live router stays locked.

**Rollback/fail-safe:** if envelope/schema/order capability is absent, keep read-only last-good data visibly STALE and inhibit any mutation. Never fall back to an unversioned live label.

## 7. Verification counters

Independent paths only; rereading the same artifact does not increment.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `11/20` | OPEN — WS stale-retention + capped-age paths added |
| UI-002 | `3/20` | OPEN |
| UI-003 | `4/20` | OPEN — chain spot WS fallback source path added |
| UI-005 | `9/20` | OPEN — WS live/default semantics added |
| UI-006 | `5/20` | OPEN |
| UI-007 | `6/20` | OPEN — WS/REST ordering and freshness paths added |
| UI-009 | `6/20` | OPEN |
| UI-011 | `3/20` | OPEN |
| UI-016 | `5/20` | OPEN — transport vs source/feed truth added |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `3/20` | OPEN — WS chain spot provenance gap added |
| CHAIN-003..005 | `1/20` each | OPEN |
| READY-001 | `4/20` | OPEN |
| READY-003 | `2/20` | OPEN |
| PAPER-001 | `2/20` | OPEN |
| PAPER-003 | `2/20` | OPEN |
| PAPER-005 | `2/20` | OPEN |
| PAPER-008 | `2/20` | OPEN |
| PAPER-009 | `2/20` | OPEN |
| PAPER-010..016 | `1/20` each | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| LEGACY-001 | `1/20` | OPEN / exposure UNPROVEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN / verify route inventory |

No finding is `LOCKED-20X`.

## 8. Prioritized implementation order

### P0 Wave 1 — eliminate false-green/fail-open behavior

1. SOL-01 auth body + auth-gated polling/stream startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-11 transport/stream separation, heartbeat schema, uncapped age and ordered merge.
4. SOL-09 server-owned risk + mandatory pre-trade authority.
5. SOL-06 durable lifecycle/idempotency/ledger and remove direct executor mutation path.
6. capability-driven removal of dead/unproven Paper Tick control.
7. SOL-04 semantic readiness repair.
8. SOL-03 remove zero/live/PCR/safety defaults.
9. SOL-10 legacy mutation UI quarantine.
10. SOL-07 rank-as-percent repair.

**Wave-1 success:** no missing field/file/route/policy/quote, parse error, HTTP success, object existence, socket OPEN, incomplete heartbeat, stale last-good value, out-of-order REST response or browser default can create green safety/readiness/risk/P&L/stream/mutation truth.

### P1 Wave 2 — prove market/account/paper economics

Complete market/broker provenance; restart-safe lifecycle reconciliation; costed fills/P&L; Options + full Greeks provenance; portfolio/scenario risk; exact Cloud Run runtime/source/entrypoint provenance; true WebSocket runtime proof.

### P2 Wave 3 — institutional operator quality

Responsive tablet/mobile, accessibility, keyboard/focus, command palette/search, drilldowns, observability/SLO/incidents, security/session settings and audit export.

## 9. Product information architecture target

1. **Command Center** — Overview + Decision Intel + authoritative truth strip.
2. **Market / Scanner** — watch, scanner, ranker, signals.
3. **Options & Greeks** — full chain, IV/OI/liquidity, Greeks.
4. **AI Decision Audit** — Genesis Brain + Prediction Audit + calibration/evidence.
5. **Paper / Trade Lifecycle** — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. **Portfolio & Risk** — server-owned policy, exposure, aggregate Greeks, scenarios.
7. **Data & Broker Health** — transport/heartbeat/source/freshness/auth/account reads and fallback truth.
8. **Readiness / Proof** — semantic E2E gates + Live Gate.
9. **Observability** — alerts, logs, schema/parse errors, latency, stream reconnects and deployment truth.
10. **Security / Settings** — sessions, policy versions, permissions, audit export and non-authoritative UI preferences.

Current repository tabs remain represented through this rationalized hierarchy; a conceptual rename never implies implemented backend capability.

## 10. Product UI visual evolution — V8

New concept: **Data Stream & Broker Health V8**.

Changes driven by this slice:

- separates WebSocket transport connected from data stream healthy;
- exposes heartbeat, last source event, event age and freshness TTL;
- separates Dhan REST auth, feed/session, option cache, account reads and market state;
- makes REST fallback visible instead of silently competing with WS;
- adds event sequence/schema/source/quality columns;
- stale data is watermarked and cannot refresh itself by reusing old values;
- malformed payload becomes SCHEMA_ERROR/alert instead of silent ignore;
- execution eligibility is INHIBITED when stream truth is unknown/stale;
- live router remains locked.

Visual artifact: `Genesis_System3_Data_Stream_Broker_Health_Target_V8.png`.

## 11. Positive foundations to preserve

- WS reconnect uses exponential backoff + jitter in the main V5 data hook;
- REST polling intervals are already reduced relative to earlier Dhan-stampede behavior;
- shared UI tokens/numeric styling and reduced-motion direction;
- visible pending states in unfinished workspaces;
- scanner-vs-prediction distinction direction;
- wrong-symbol chain suppression;
- source/snapshot/stale messaging foundation;
- Live Gate approval does not automatically enable live trading;
- Paper Trading states Dhan production is not a paper sandbox and local fills are simulated.

These are foundations, not readiness proof.

## 12. Historical open real-money gates

Remain open until exact-revision proof closes them:

- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture, not a defect.

## 13. Closure standard

A finding becomes `CLOSED` only when evidence is tied to the exact changed revision: source fix inspected; positive/negative tests; static/type/build checks; unit/integration/browser tests; route inventory; console/network proof; schema reconciliation; ordering/reconnect/staleness tests where applicable; restart/idempotency/reconciliation tests; runtime/deployment proof where required; analyzer/live-off unchanged; no contradictory independent evidence.

## 14. Next audit / solution slices

1. **Option-chain backend normalization** — exact Dhan normalizer, timestamps, cache ownership, IV/Greeks computation and schema.
2. **Observability / Cloud Run provenance** — source/runtime revision, image digest, production entrypoint, browser/runtime errors and dependencies.
3. **DB/state-store consistency** — TradeHistoryStore, JSON/state store, locking/concurrency, atomicity and duplicate authorities.
4. **Responsive/accessibility** — desktop/tablet/mobile, keyboard/focus/live regions/dense tables.
5. **AI/ML/prediction ledger** — calibration, frozen cutoff, model/hash, drift and realized after-cost outcomes.

## 15. Hard safety rule

A green UI, successful build, endpoint HTTP 200, socket OPEN, heartbeat object existence, zero-valued risk/P&L, static `PAPER SAFE`, human approval, stale last-good value, capped age metric, missing market data or a process-local simulator never substitutes for authoritative source/freshness/ordering/lifecycle/enforceable risk/reconciliation/positive after-cost expectancy/exact runtime proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.