# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 05:48 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `3ee93b792f76fa736bb0c72864bfdeb2fa54c6b0`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..3ee93b792f76fa736bb0c72864bfdeb2fa54c6b0` is 10 commits ahead and changes only `reports/latest/manual_repo_qc_audit/summary.md`; therefore latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- New PR #97 is OPEN, head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not on `main` and must not be treated as implemented production behavior.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Workflow-run lookup for repository HEAD `3ee93b...` returned no runs through the connector. Exact-revision CI/runtime readiness is therefore **NOT PROVEN**, not failed.
- Deployment authority: Google Cloud Run / Google Cloud services. Render-era instructions are migration debt only.
- Audit posture: ANALYZER/PAPER. Live order placement, modification, cancellation and routing remain prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision proof required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Data/source/staleness truth | **FAIL / P0-P1** | **READY TO PATCH** via typed envelopes |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Greeks provenance | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| Google Cloud provenance | **NOT PROVEN / P1** | exact revision/image/runtime evidence required |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, fresh-market-data, broker-connected or trade-ready through defaults.

## 3. Retained findings registry

### Auth/session
- `AUTH-001/P0` login request/backend contract mismatch.
- `AUTH-002/P1` protected polling before authentication.
- `AUTH-003/P1` raw dashboard key in browser `sessionStorage`.
- `AUTH-004/P1` independent session expiry/revocation proof incomplete.

### Global UI/data truth
- `UI-001/P0` absence/error can become plausible valid-looking data.
- `UI-002/P0-P1` rank/score can be mislabeled as gain/forecast percentage.
- `UI-003/P1` source identity can be inferred/defaulted rather than proven.
- `UI-004/UI-016/P0-P1` auth/feed/freshness/account/router/deployment truths are conflated in places.
- `UI-005/P1` permissive defaults collapse unknown into safe/neutral values.
- `UI-006/P1` `PROVEN_EMPTY` is not consistently distinguished from error/stale/no-data.
- `UI-007/P1` shared market-data truth envelope missing.
- `UI-009/P0` PAPER/LIVE/LOCKED lacks one authoritative runtime safety object.
- `UI-010/P1` immutable production prediction ledger unproven.
- `UI-011/P1` enforceable portfolio/factor/scenario risk incomplete.
- `UI-012/UI-013/UI-014/P2` navigation rationalization, responsive/mobile, keyboard/focus incomplete/unproven.
- `UI-018/P1` build labels are not deployment compatibility proof.
- `UI-019/P1` broker health requires typed state machine.

### Option chain/Greeks retained
- `CHAIN-001/P0` warming/no-data chain can produce `PCR=1` instead of unknown.
- `CHAIN-002/P1` Dhan-looking verification lacks event-time/freshness/schema/normalizer/completeness proof.
- `CHAIN-003/P1` full Delta/Gamma/Theta/Vega not displayed in Option Chain.
- `CHAIN-004/P1` Dhan row -> normalized inputs -> Greeks -> UI provenance not proven end to end.
- `CHAIN-005/P1` IV unit/schema implicit at UI boundary.

### Readiness/gates
- `READY-001/P0` missing live/order evidence can default safe.
- `READY-002/P0` money-ready excludes required paper lifecycle proof.
- `READY-003/P0-P1` gates can pass from object presence instead of semantic checks.
- `READY-004/P1` funds/holdings/positions success semantics weak.
- `READY-005/P0` trader-ready can pass transport checks without lifecycle/economic proof.
- `READY-006/P1` core E2E PASS is transport-level only.
- `READY-007/P1` Dhan proof lacks full freshness/schema envelope.
- `READY-008/P1` Live Gate retains Render-era instructions.
- `READY-009/P1` human approval lacks exact evidence revision/time provenance.

### Paper/trade/positions
- `PAPER-001/P0` missing safety fields can yield PAPER SAFE.
- `PAPER-002/P0` missing market source can yield live-looking Dhan state.
- `PAPER-003/P1` missing monetary fields can render `₹0.00`.
- `PAPER-004/P1` plausible provenance defaults can be invented.
- `PAPER-005/P1` paper-safe proof over-relies on negative evidence.
- `PAPER-006/P1` performance defaults to zero.
- `PAPER-007/P1` empty positions lack explicit truth state.
- `PAPER-008/P1` Force Paper Tick lacks idempotency/correlation proof.
- `PAPER-009/P1` immutable lifecycle event chain not exposed.
- `PAPER-010/P0-P1` `/api/paper/tick` capability unproven.
- `PAPER-011/P0` direct executor path bypasses canonical pre-trade authority.
- `PAPER-012/P0-P1` process-local IDs/state restart-unsafe.
- `PAPER-013/P1` last price can be reused without explicit stale quality.
- `PAPER-014/P1` realized P&L not proven after-cost/reconciled.
- `PAPER-015/P1` paper read errors can collapse to empty/zero truth.
- `PAPER-016/P0-P1` paper truth statically declares safety.
- `TRADE-001/P1-P2` Trade tab is not a controlled paper-order/risk workstation.
- `TRADE-002/P0-P1` `gain_rank` can render as `GAIN %`.
- `TRADE-003/P1` `EOD/live` does not prove freshness.
- `LEGACY-001/P0-P1` legacy mutation UI exists; deployment exposure unproven.

### Risk
- `RISK-001/P0` browser supplies risk limits.
- `RISK-002/P0` missing policy can use permissive defaults.
- `RISK-003/P0-P1` unavailable inputs can become zero risk.
- `RISK-004/P1` VaR contract not institutional/reproducible.
- `RISK-005/P0` execution guardrail has fail-open conditions.
- `RISK-006/P0` canonical guardrail wiring unproven.
- `RISK-007/P1` risk UI uses non-contract gate proxy.
- `RISK-008/P0-P1` lifecycle gate can promote from position shape.
- `RISK-009/P1` refresh/evaluation errors can retain old artifacts.

### WebSocket/stream
- `WS-001/P1` socket OPEN immediately labeled live.
- `WS-002/P0-P1` incomplete heartbeat can false-green live.
- `WS-003/P1` REST/WS writes lack monotonic ordering.
- `WS-004/P1` old spot can be retained and re-stamped current.
- `WS-005/P1` market-top WS event can become `status:ok` without provenance.
- `WS-006/P1` malformed WS payload silently ignored.
- `WS-007/P1` stale last-good can retain prior live/ok status.
- `WS-008/P1` duplicate/unused WebSocket transport policy risk.
- `WS-009/P0-P1` WebSocket proof does not actually open a WebSocket.
- `WS-010/P0-P1` backend tick age capped; parse failure can appear bounded.
- `WS-011/P1` actual `/ws/stream` route owner remains unproven by current search.

## 4. New deep slice — Dhan option-chain normalization, expiry, cache and Greeks truth

### CHAIN-006 / P0-P1 — parser converts missing/invalid market fields and Greeks to numeric zero

**Exact proof:** `core/data/dhan_option_chain_parser.py` uses `_safe_float(..., default=0.0)` and `_safe_int(..., default=0)` for LTP, OI, bid, ask, IV and nested Greeks. `tests/test_dhan_option_chain_parser.py::test_missing_null_values_safe` explicitly asserts null LTP/OI/delta/spread become zero.

**Symptom/root cause:** parser uses numeric sentinel values for schema absence and parse failure.

**Real-money impact:** unavailable quote/Greek can become indistinguishable from a genuine zero; downstream spread, risk, ranking and UI can consume false neutral values.

**Files:** `core/data/dhan_option_chain_parser.py`, `tests/test_dhan_option_chain_parser.py`, downstream serializer/API/UI consumers.

**Target:** nullable typed fields plus per-row/field quality. Missing Dhan values remain `null` with reason `MISSING_PROVIDER_FIELD | INVALID_TYPE`; only a provider-supplied numeric zero remains zero.

**Implementation:** replace `_safe_*` zero defaults for market/risk fields with nullable coercion; add `field_quality`; calculate derived fields only when all inputs are valid; require schema validator before row becomes `PROVEN`.

**Tests/PASS:** missing LTP -> null, not 0; missing delta -> null; genuine provider 0 stays 0; invalid numeric string -> SCHEMA_ERROR; UI renders `—/UNKNOWN`, not `0.00`.

**Rollback/fail-safe:** rows with missing required execution/risk fields remain display-only and execution-ineligible.

**Status:** `READY TO PATCH`.

### CHAIN-007 / P1 — bid/ask spread can become synthetic zero or negative on incomplete quotes

`parse_dhan_leg()` computes `top_ask - top_bid` after missing bid/ask are coerced to zero. Missing both becomes spread `0.0`; missing ask with a valid bid can become a negative spread.

**Impact:** liquidity/spread quality can be materially wrong and may influence opportunity/risk filters.

**Solution:** calculate spread only when bid and ask are both valid, non-negative and `ask >= bid`; otherwise `spread=null`, `quote_quality=INCOMPLETE|CROSSED|INVALID`.

**Tests:** missing ask/bid, crossed market, both zero supplied by provider, normal quote.

**Status:** `READY TO PATCH`.

### CHAIN-008 / P0-P1 — in-memory option-chain cache key ignores expiry

`DataSourceManager.fetch_option_chain(symbol, expiry)` caches under `self._cache[sym]` only. A second request for the same underlying but a different expiry inside the TTL can receive the previously cached expiry.

**Impact:** wrong-expiry contracts can appear under an operator-selected expiry, corrupting Greeks, strikes and paper decision context.

**Solution:** canonical cache key `(provider, underlying_security_id, segment, expiry, schema_version, normalizer_version)`; cache record stores source event/receive time and row expiry; read validates requested expiry against every row.

**Tests:** fetch NIFTY expiry A then expiry B within TTL must never return A; cache mismatch -> reject/refresh.

**Status:** `READY TO PATCH`.

### CHAIN-009 / P0-P1 — disk chain-cache fallback has no age/provenance/schema/expiry validation

When live sources fail, `fetch_option_chain()` reads `state/chain_cache/{sym}.json`, accepts `spot` plus `strikes/contracts`, and returns them without checking cached event time, age, requested expiry, provider/source, schema version, normalizer version or completeness.

**Impact:** arbitrarily stale or wrong-expiry rows can be promoted into the normal chain path.

**Solution:** replace bare JSON fallback with `OptionChainCacheEnvelope`; reject mismatched expiry/schema/provider and expired TTL. Last-good may be displayed only as `STALE_LAST_GOOD` with original event time and age, never treated current/execution-eligible.

**Tests:** stale cache, missing timestamp, wrong expiry, unknown source, schema mismatch all fail closed; valid fresh matching cache returns `PROVEN_CACHE` with age.

**Status:** `READY TO PATCH`.

### CHAIN-010 / P0-P1 — `get_option_chain()` can label fallback data `source: dhan` without proof

`DataSourceManager.get_option_chain()` returns `source: "dhan"` for any non-empty result from `fetch_option_chain()`. The latter can return disk-cache data and contains legacy alternate-source routing shims.

**Impact:** UI/backend consumers can receive a Dhan provenance label that was not carried from the actual data record.

**Solution:** source is mandatory immutable metadata returned by acquisition/normalization; serializer must never invent provider identity. Disk cache must preserve the original provider/session/source event time.

**Tests:** disk cache without source -> UNKNOWN, not Dhan; Dhan response -> Dhan only when validated; test shim/non-Dhan source cannot serialize as Dhan.

**Status:** `READY TO PATCH`.

### CHAIN-011 / P1 — generic calendar expiry fallback is not symbol-specific and is silently authoritative

`_nearest_expiry()` calculates the next Monday and is used as the last-resort expiry for all symbols when broker expiry discovery fails. It does not encode symbol/exchange-specific expiry calendars, holidays or broker-declared series availability.

**Impact:** a broker-expiry failure can redirect chain requests to an incorrect series instead of becoming an explicit expiry-resolution error.

**Solution:** broker `expiry_list` is authoritative. If it fails, use a versioned exchange-calendar service only when independently validated for that symbol; otherwise return `EXPIRY_UNKNOWN` and no current chain. Manual override must be explicit and visibly labeled.

**Tests:** broker expiry failure, holiday-adjusted expiry fixture, per-underlying calendars, explicit override provenance.

**Status:** `READY TO PATCH`.

### CHAIN-012 / P1 — parser suppresses schema/normalization exceptions into empty chain + spot zero

`parse_option_chain_to_df()` catches broad `Exception` and returns `(empty DataFrame, 0.0)`. Unknown official payloads similarly collapse to empty/zero without a structured parse error.

**Impact:** provider schema drift can look identical to a legitimate no-data state; monitoring cannot distinguish schema failure from empty chain.

**Solution:** parser returns typed `ParseResult` containing rows, spot, `quality_state`, errors, schema version and normalizer version; no broad silent catch at the truth boundary. API maps parse failure to `SCHEMA_ERROR`, not empty live data.

**Tests:** malformed nested Greeks, unexpected wrapper, invalid strike key, wrong types, legitimate empty chain.

**Status:** `READY TO PATCH`.

### CHAIN-013 / P1 — historical schema audit PASS is narrower than production truth requirements

`reports/latest/dhan_option_chain_schema_audit/summary.md` reports PASS/no blockers because it verifies field-name mappings and parser tests. Those tests explicitly approve null->zero behavior and do not prove cache expiry identity, freshness, provider session, normalizer version, disk-cache semantics or end-to-end UI provenance.

**Impact:** a historical PASS can be over-read as complete chain readiness.

**Solution:** rename/scope the proof to `DHAN_FIELD_MAPPING_SCHEMA_PASS`; create separate `OPTION_CHAIN_RUNTIME_TRUTH` gate requiring source/expiry/event time/age/schema/normalizer/completeness/cache state and UI contract checks.

**Status:** `READY TO PATCH`.

### CHAIN-014 / P2 — legacy multi-source fallback list remains in a Dhan-only manager

The module header says Dhan-only, but `fetch_option_chain()` still enumerates `nse`, `nsepython`, `bhavcopy`, `jugaad`, `yfinance`, `synthetic`. Current `_try_*` shims all return `(None, None)`, so this run does **not** claim active synthetic fallback. The residue is nevertheless confusing and regression-prone.

**Solution:** remove production multi-source list or put test adapters behind dependency injection unavailable in production. CI asserts only approved Dhan acquisition owner is wired for production chain truth.

**Status:** `READY TO PATCH` after compatibility test inventory.

### Regression note — PR #97

PR #97 correctly recognizes synthetic/simulated P&L contamination risk, but its proposed suppression replaces ignored synthetic values with numeric zeros. Because the PR is OPEN it does not change main. Before merge, the safer contract is `quality_state=SYNTHETIC_REJECTED`, nullable P&L and explicit UI suppression, not `0.0` values that can be mistaken for genuine flat P&L.

## 5. Canonical truth contracts

### 5.1 `SafetyTruth`
`mode`, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 5.2 `DataTruthEnvelope`
`source`, provider session, instrument, source/backend/frontend times, age/TTL, market state, schema/normalizer versions, row count/completeness, quality state, source/runtime revisions.

### 5.3 `StreamTruth`
separate transport/stream/heartbeat state, last event times, uncapped event age, TTL, sequence, rejected-old events, parse errors, source/session/schema, REST fallback and revisions.

### 5.4 `OptionChainTruth` — NEW

```text
underlying
underlying_security_id
segment
requested_expiry
resolved_expiry
expiry_resolution_source: DHAN_EXPIRY_LIST | VALIDATED_CALENDAR | MANUAL_OVERRIDE | UNKNOWN
provider: DHAN | UNKNOWN
provider_session_id
source_event_time
backend_received_time
age_ms
freshness_threshold_ms
cache_state: LIVE_FETCH | FRESH_CACHE | STALE_LAST_GOOD | MISS | REJECTED
cache_key
schema_version
normalizer_version
spot: nullable
rows[]: nullable market/Greek fields + field_quality
row_count
completeness_pct
quality_state: PROVEN | PROVEN_EMPTY | STALE | NO_DATA | AUTH_ERROR | API_ERROR | SCHEMA_ERROR | EXPIRY_UNKNOWN | UNKNOWN
source_revision
runtime_revision
evidence_id
```

**Invariant:** no source, expiry, timestamp, schema or required quote/Greek field may be invented by the serializer/UI. Missing numeric value remains null.

### 5.5 `PaperLifecycleTruth`, `GateTruth`, `RiskPolicy`, `PreTradeRiskTruth`
Retain immutable lifecycle, semantic evidence gates, server-owned policy and fail-closed pre-trade decision contracts from prior iterations.

## 6. Canonical remediation roadmap

- `SOL-01 Auth/session — READY TO PATCH`: correct login body; cookie-only browser auth; remove raw API key; auth-gate polling/WS; TTL/revocation tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: single backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production `||0` and plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser fields; validated spread; symbol+expiry cache; freshness/provenance envelope; explicit IV units; full Greeks; normalizer/model version; portfolio aggregation.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 Scanner contract — READY TO PATCH`: rank/score/probability/forecast/realized distinct and nullable.
- `SOL-08 GCP provenance — READY TO PATCH/DESIGN`: exact frontend/backend/source/image/Cloud Run revision and production entrypoint; remove Render instructions.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; monotonic REST/WS merge; uncapped event age; true WS proof.

### SOL-05 ordered implementation

1. Introduce `OptionChainTruth`/`OptionChainCacheEnvelope` schemas backend-first.
2. Replace parser zero coercion with nullable coercion + typed field-quality errors.
3. Validate bid/ask and derive spread only from complete sane quotes.
4. Make IV unit explicit (`PERCENT_PROVIDER`, normalized decimal field separately); never infer in UI.
5. Preserve Dhan-provided Greeks as provider Greeks with provider/schema/version; if calculated Greeks are added, store them in separate fields with model/version/rate/dividend/time assumptions.
6. Cache by provider+security_id+segment+expiry+schema+normalizer, never symbol alone.
7. Store source event/receive timestamps and expiry in cache envelope; reject stale/mismatched cache.
8. Remove serializer-added `source:'dhan'`; source must originate in the envelope.
9. Replace generic expiry fallback with authoritative Dhan expiry list -> validated calendar -> explicit UNKNOWN.
10. Replace broad parser catches with typed parse result/error metrics.
11. Expand tests to null-vs-zero, wrong expiry, stale cache, schema drift, crossed/missing quotes, IV units and full Greek completeness.
12. UI Options & Greeks renders source, expiry, event age, cache state, schema/normalizer version and `—/UNKNOWN` for absent values.
13. Update historical proof naming so field mapping PASS cannot imply runtime truth PASS.

**SOL-05 PASS criteria:** requested expiry always matches returned rows; stale/wrong-expiry cache cannot become current; missing quote/Greek never becomes zero; source cannot be fabricated; parser schema failure is visible; IV units explicit; every displayed chain row exposes age/provenance/completeness; live router remains locked.

**Rollback/fail-safe:** if new envelope fields are absent, mark chain `UNKNOWN/SCHEMA_ERROR`, allow only visibly stale/read-only display where safe, and inhibit mutation/risk decisions.

## 7. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `13/20` | OPEN — parser null->zero + unvalidated cache paths added |
| UI-002 | `3/20` | OPEN |
| UI-003 | `6/20` | OPEN — serializer Dhan label + cache provenance added |
| UI-005 | `11/20` | OPEN — parser/cache zero/default semantics added |
| UI-006 | `7/20` | OPEN — parse/cache no-data vs error ambiguity added |
| UI-007 | `7/20` | OPEN — chain truth envelope path added |
| UI-009 | `6/20` | OPEN |
| UI-011 | `3/20` | OPEN |
| UI-016 | `6/20` | OPEN — chain provider/cache truth separation added |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `5/20` | OPEN — parser + cache paths independently confirm provenance gap |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `2/20` | OPEN — provider Greek parser lacks runtime/model provenance envelope |
| CHAIN-005 | `2/20` | OPEN — parser normalizes IV while UI contract remains implicit |
| CHAIN-006..014 | `1/20` each | OPEN |
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
| WS-011 | `1/20` | UNPROVEN |

No finding is `LOCKED-20X`.

## 8. Prioritized implementation order

### P0 Wave 1 — false-green/fail-open elimination
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-05 parser null-safety + expiry-aware/provenance-aware chain cache.
4. SOL-11 StreamTruth, uncapped age and ordered REST/WS merge.
5. SOL-09 server-owned risk + mandatory pre-trade authority.
6. SOL-06 durable lifecycle/idempotency/reconciliation.
7. remove dead/unproven paper mutation control.
8. SOL-04 semantic readiness.
9. SOL-03 remaining zero/live/default-safe fallbacks.
10. SOL-10 legacy mutation UI quarantine.
11. SOL-07 rank-as-percent repair.

### P1 Wave 2 — market/account/paper economics
Full Dhan/account provenance, IV/Greeks model truth, costed fills/P&L, portfolio risk, exact GCP runtime/deployment proof, real WebSocket proof.

### P2 Wave 3 — institutional operator quality
Responsive/mobile, accessibility/keyboard/focus, command palette/search, deep drilldowns, observability/SLO/incidents, security/session settings and audit export.

## 9. Product information architecture target

1. Command Center — Overview + Decision Intel + truth strip.
2. Market / Scanner — watch, scanner, ranker, signals.
3. Options & Greeks — chain, explicit expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + calibration/evidence.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — transport/heartbeat/source/freshness/auth/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — alerts, logs, schema/parse errors, latency, reconnects, deployment truth.
10. Security / Settings — sessions, policy versions, permissions, audit export, non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 10. Product UI visual evolution — V9

New concept: **Option Chain Truth Workstation V9**.

Changes driven by this iteration:
- source/expiry/event-age/cache-age are first-class chain truth;
- cache key is visibly symbol+expiry aware;
- missing market/Greek data displays `—/UNKNOWN`, never zero;
- incomplete/crossed bid-ask is invalid rather than artificial spread;
- cache/expiry mismatch is rejected;
- stale rows are watermarked;
- chain quality shows CE/PE pairing, quote/Greek completeness and expiry match;
- provider field -> normalized field drilldown exposes schema/normalizer/runtime/evidence IDs;
- live router remains locked.

Visual artifact: `Genesis_System3_Option_Chain_Truth_Target_V9.png`.

## 11. Positive foundations to preserve

- Canonical parser uses official Dhan field names and nested Greeks rather than known wrong aliases.
- Parser computes `change_in_oi` from `oi - previous_oi` and uses top bid/ask fields.
- Dhan option-chain traffic is process-serialized and rate paced.
- Dhan expiry-list discovery is attempted before calendar fallback.
- Current alternate-source `_try_*` shims return none; this run found no active synthetic option-chain fallback through them.
- WS reconnect has backoff+jitter foundation.
- Live Gate approval does not automatically enable live trading.
- Wrong-symbol chain suppression and stale/snapshot messaging are useful foundations.

These are foundations, not readiness proof.

## 12. Historical proof/open-gate interpretation

The historical `dhan_option_chain_schema_audit` PASS is retained as **field-mapping/unit-test proof only**. It must not be used as runtime freshness/cache/expiry/provenance/Greeks-readiness proof.

Remain open:
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `NSE_COMPARISON_PROOF_MISSING`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 13. Closure standard

A finding becomes `CLOSED` only on exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; expiry/cache/freshness/order/reconnect tests as applicable; restart/idempotency/reconciliation tests; runtime/deployment proof where required; analyzer/live-off unchanged; and no contradictory independent evidence.

## 14. Next audit/solution slices

1. Observability + Cloud Run provenance: source/runtime revision, image digest, production entrypoint, browser/runtime errors and dependencies.
2. DB/state-store consistency: locking/concurrency/atomicity/duplicate authorities.
3. AI/ML/prediction ledger: calibration, frozen cutoff, model/hash, drift and realized after-cost outcome.
4. Responsive/accessibility: desktop/tablet/mobile, keyboard/focus/live regions/dense tables.
5. Scanner/ranker contracts and performance/memory/concurrency under market-open load.

## 15. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser PASS, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, symbol-only cache hit, inferred Dhan source, human approval or process-local simulator never substitutes for authoritative source+expiry+event time+freshness+schema+normalizer+ordering+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact runtime proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.
