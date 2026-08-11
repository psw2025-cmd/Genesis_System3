# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 07:50 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `220fdcf3fa3c684170889f2045c0e0baedbd1b6d`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..220fdcf3fa3c684170889f2045c0e0baedbd1b6d` is **12 commits ahead** and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- GitHub connector returned no workflow runs for repository HEAD `220fdcf3fa3c684170889f2045c0e0baedbd1b6d`; exact-revision CI/runtime readiness remains **NOT PROVEN**, not failed.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH** via `StateTruth` + domain-revision store |
| Restart/concurrency consistency | **FAIL / P0-P1** | shared-cloud authority + idempotent replay required |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Data/source/staleness truth | **FAIL / P0-P1** | **READY TO PATCH** via typed truth envelopes |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Greeks provenance | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH** via `DeploymentTruth` |
| Observability/runtime error truth | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

### Auth/session
`AUTH-001..004` remain OPEN: login contract mismatch, pre-auth polling, raw browser key storage, session expiry/revocation proof incomplete.

### Global UI/data truth
`UI-001..019` remain OPEN as previously recorded, including false-valid defaults, source inference, `PROVEN_EMPTY` ambiguity, missing authoritative PAPER/LIVE truth, incomplete prediction/risk truth, responsive/accessibility gaps and deployment/build-label ambiguity.

### Option chain/Greeks
`CHAIN-001..014` remain OPEN: warming PCR false-data, weak Dhan proof, incomplete Greeks display/provenance, implicit IV units, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented Dhan source, generic expiry fallback, parser error collapse and legacy multi-source residue.

### Readiness/gates
`READY-001..009` remain OPEN: missing safety evidence can default safe, semantic lifecycle/risk/economic gates incomplete, account success semantics weak, Render-era Live Gate copy and evidence-poor human approval.

### Paper/trade/positions
`PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` remain OPEN: static/default safety, missing-data→zero, unproven paper mutation capability, direct executor bypass, process-local lifecycle state, stale-price handling, incomplete cost/reconciliation and legacy mutation UI residue.

### Risk
`RISK-001..009` remain OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrail conditions, unproven canonical wiring, UI proxy gate and stale gate artifacts.

### WebSocket/stream
`WS-001..011` remain OPEN/UNPROVEN: socket-open≠healthy stream, incomplete heartbeat false-green, REST/WS ordering, re-stamped stale values, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped tick age and route-owner uncertainty.

### Google Cloud/deployment
`GCP-001..011` remain OPEN: exact-revision proof missing, immutable digest absent, frontend SHA weak, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, typed safety evidence incomplete, cosmetic build markers, weak incident/revision binding and incomplete Render retirement.

### DB/state-store — NEW
- `STATE-001/P0-P1` Cloud Run deployment does not set `SYSTEM3_STATE_BACKEND=firestore`; runtime-store default is `file`, so cloud shared-state authority is not established by deployed configuration.
- `STATE-002/P0-P1` Firestore mode is optional by default (`SYSTEM3_STATE_BACKEND_REQUIRED=0`); Firestore initialization/read/write failure can fall back to local files instead of failing closed.
- `STATE-003/P0-P1` Firestore transaction merges a **whole incoming process snapshot** over remote state. A stale process can overwrite newer domain fields even while global `state_version` remains monotonic.
- `STATE-004/P1` state version is one global integer; there is no per-domain writer/revision/CAS metadata for broker, market, positions, P&L, risk, chain or worker-owned fields.
- `STATE-005/P0-P1` startup calls `get_state_store(...)->load_state()` and immediately `sync_from_files()`. Any local output files available to the process can overwrite freshly loaded remote/shared state during startup.
- `STATE-006/P1` default initialized state contains plausible green/neutral values such as `qc.status=PASS`, `risk.limits.status=PASS`, zero P&L/Greeks/exposure and empty positions before those domains are proven.
- `STATE-007/P1` duplicated method definitions exist for `_enforce_safety_invariants`, `_save_local_state`, and repeated Firestore-load logic; this increases maintenance/patch divergence risk in the supposed SSOT layer.
- `STATE-008/P1` broker/internal position readers collapse many import/API/read/parse failures to `[]`; reconciliation can therefore confuse error with proven-empty/no-position state.
- `STATE-009/P1` reconciliation uses `trading_symbol/symbol` versus internal `position_id` as identity without one canonical instrument/position identity contract; quantity mismatch logic also defaults missing quantities to zero.
- `STATE-010/P1` state-sync readers parse multiple JSON files independently with no generation/correlation ID, so positions/P&L/signals/QC can come from different cycles and be merged into one dashboard snapshot.
- `STATE-011/P1` local writes are atomic per file, which is positive, but there is no cross-file transaction across runtime state, positions, P&L, signals and QC artifacts.
- `STATE-012/P1` Firestore tests verify merge/version behavior and path validation but do not test two stale writers, lost updates, startup replay, backend-required failure, domain revisions or failover semantics.

## 4. New deep slice — DB/state-store consistency, restart and concurrency

### STATE-001 / P0-P1 — production deployment does not establish shared-state backend authority

**Exact proof:** `RuntimeStateStore` defaults `SYSTEM3_STATE_BACKEND` to `file`; only explicit value `firestore` instantiates `FirestoreStateBackend`. The inspected Cloud Run deploy script/workflow sets analyzer/live-off/auth/token/memory/public URL variables but does not set `SYSTEM3_STATE_BACKEND=firestore` or `SYSTEM3_STATE_BACKEND_REQUIRED=1`.

**Symptom/root cause:** code contains a cloud shared-state implementation, but deployment configuration does not make it authoritative.

**Real-money impact:** process/restart-local state can diverge from worker/job state; dashboard positions/P&L/risk/readiness may depend on whichever instance filesystem currently serves the request.

**Exact files:** `dashboard/backend/runtime_state_store.py`, `dashboard/backend/firestore_state_backend.py`, `scripts/gcp_cloud_run_auto_deploy.py`, `.github/workflows/cloud-run-auto-deploy.yml`.

**Target behavior:** in GCP production, state authority is explicit and typed: `backend=FIRESTORE_REQUIRED`, with local disk used only as non-authoritative diagnostics/cache.

**Minimal safe implementation:** add `SYSTEM3_STATE_BACKEND=firestore`, `SYSTEM3_STATE_BACKEND_REQUIRED=1`, explicit project/collection/document env, startup capability proof and a `/api/state/provenance` read-only contract.

**Ordered steps:** configure Firestore + IAM; make backend required in Cloud Run; start service only after read/write transaction self-test; expose backend/document/revision metadata; mark local mirror `DIAGNOSTIC_ONLY`; block readiness when shared backend unavailable.

**Tests/PASS:** missing Firestore credentials/project/document, permission denied, unavailable backend, restart, and new revision must all produce `STATE_AUTHORITY_ERROR` rather than local-authoritative operation. PASS only when exact serving revision proves shared backend read/write and backend-required=true.

**Rollback/fail-safe:** analyzer UI may show a read-only degraded page, but paper mutation/readiness are inhibited.

**Status:** `READY TO PATCH`.

### STATE-002 / P0-P1 — optional Firestore fallback can silently split cloud truth

**Exact proof:** `SYSTEM3_STATE_BACKEND_REQUIRED` defaults false. Firestore constructor/load/save exceptions print warnings and fall back to local files when required=false.

**Root cause:** availability fallback is treated as equivalent persistence authority.

**Impact:** one process can continue on local state while another process/job writes Firestore; both may look internally coherent.

**Solution:** cloud mode must fail closed on shared-state failure. `StateTruth.quality=ERROR`, no mutations, no readiness, no account/position green state. Local file mirror remains diagnostic and carries `authoritative=false`.

**Tests:** Firestore 403/timeout/unavailable/transaction abort => no local-authoritative mutation; UI shows shared-state unavailable; restart cannot promote mirror to authority.

**Status:** `READY TO PATCH`.

### STATE-003 / P0-P1 — Firestore transaction is atomic but can still lose domain updates

**Exact proof:** `FirestoreStateBackend.save(state)` clones the caller's entire state, loads current remote document transactionally, deep-merges **incoming over existing**, then increments the single `state_version`. `RuntimeStateStore._save_state()` passes `self._state`, not a sparse update/expected-domain revision.

**Root cause:** transaction protects write atomicity but not stale-writer semantics.

**Example failure:** process A reads state version 10; process B updates broker to version 11; process A later submits its full stale snapshot containing old broker plus a new P&L value. Transaction merges A's old broker over B's newer broker, then publishes version 12. Global version increased while broker truth regressed.

**Real-money impact:** stale process state can overwrite fresher broker/market/risk/position domains while the monotonic version falsely suggests forward progress.

**Canonical solution:** domain-scoped compare-and-set writes. Every mutable domain carries `domain_revision`, `writer_id`, `event_time`, `updated_at`, `source_revision`, `quality`. Writers send only owned domain patches plus expected revision. Firestore transaction rejects older/equal writer revision or stale event-time where policy requires monotonic events.

**Tests:** two stale writers, concurrent broker+P&L writers, retry after conflict, out-of-order event, Cloud Run revision overlap. PASS only with zero lost updates in deterministic concurrency tests.

**Status:** `READY TO PATCH`.

### STATE-004 / P1 — one global version cannot prove domain freshness or ownership

**Proof:** state document exposes one `state_version`; no per-domain revision/CAS metadata is required by persistence layer.

**Solution:** introduce `DomainEnvelope<T>`: `state`, `domain_revision`, `writer_id`, `event_id`, `source_event_time`, `received_at`, `quality`, `schema_version`, `runtime_revision`, `evidence_id`.

**UI target:** every Data/Broker/Positions/P&L/Risk panel can drill into writer, revision, event age and state quality; global state version is diagnostic only.

**Status:** `READY TO PATCH/DESIGN`.

### STATE-005 / P0-P1 — startup file sync can overwrite freshly loaded shared state

**Exact proof:** app startup creates `state_store = get_state_store(OUTPUTS_DIR)`; the singleton calls `load_state()`, then app immediately invokes `state_store.sync_from_files()`. That bridge reads health, positions, P&L and signals from local output files and calls `update_state()`.

**Impact:** local/migratory artifacts can become newer authoritative cloud state during startup even after a successful remote load.

**Solution:** remove unconditional production startup import. Introduce a one-time migration command with explicit `--source`, snapshot ID, age limits, schema validation and human-reviewed evidence. Runtime service must never automatically promote local migration files into shared truth.

**Tests:** remote newer than local; local newer timestamp but wrong revision; malformed local; restart with old local files. All must preserve remote authority.

**Status:** `READY TO PATCH`.

### STATE-006 / P1 — initialized SSOT starts with plausible PASS/zero values

**Exact proof:** defaults include `qc.status='PASS'`, `risk.limits.status='PASS'`, zero P&L/exposure/Greeks and empty positions before those domains are proven.

**Impact:** startup/degraded state can look genuinely safe/zero rather than unproven.

**Solution:** initialize every externally meaningful domain as `UNKNOWN` with nullable measurements; only explicit proven-empty may show zero/empty. Safety flags remain independently fail-closed.

**Tests:** fresh boot without files/broker/Firestore must display UNKNOWN/PENDING, never PASS or zero-value performance/risk cards.

**Status:** `READY TO PATCH`.

### STATE-007 / P1 — duplicated SSOT methods increase patch divergence risk

**Proof:** `runtime_state_store.py` contains duplicate `_enforce_safety_invariants`, duplicate `_save_local_state`, and duplicated Firestore-load blocks.

**Impact:** future fixes can land in one copy while runtime dispatch uses the later definition; reviewers can misread which implementation is active.

**Solution:** deduplicate methods; add structural test rejecting duplicate method names in `RuntimeStateStore`; split persistence, safety and migration responsibilities into smaller modules.

**Status:** `READY TO PATCH`.

### STATE-008 / P1 — position errors collapse to empty lists

**Proof:** broker import/API exceptions return `[]`; internal file missing/parse errors also return `[]`. Reconciliation can emit `NO_POSITIONS` from an absence that is not proven-empty.

**Solution:** typed `PositionSourceResult`: `PROVEN`, `PROVEN_EMPTY`, `AUTH_ERROR`, `API_ERROR`, `SCHEMA_ERROR`, `STALE`, `UNKNOWN`; reconciliation may produce `NO_POSITIONS` only from explicit `PROVEN_EMPTY`.

**Status:** `READY TO PATCH`.

### STATE-009 / P1 — position identity/reconciliation contract is weak

**Proof:** broker position ID is derived from `trading_symbol or symbol`; internal identity expects `position_id`; quantity comparison defaults missing values to zero.

**Solution:** canonical immutable instrument key (`exchange_segment + security_id + expiry + strike + option_type`) plus lifecycle position UUID. Symbol is display metadata, not identity. Missing quantity is UNKNOWN/SCHEMA_ERROR.

**Status:** `READY TO PATCH/DESIGN`.

### STATE-010 / P1 — multi-file snapshots are not cycle-consistent

**Proof:** `state_sync_service.py` reads positions, P&L, signals, health and QC from separate JSON files independently and then merges them into one state update without a shared cycle/generation ID.

**Impact:** UI can show position set from cycle N with P&L from cycle N-1 and QC/signal from another generation.

**Solution:** writers publish one atomic `CycleSnapshot` manifest referencing immutable domain artifacts by checksum/generation; state sync accepts only a complete compatible generation. Longer term, write lifecycle domains directly to the shared store/event ledger instead of filesystem fan-in.

**Tests:** staggered writes, partial files, old P&L/new positions, interrupted cycle, duplicate generation. No mixed-generation state may be published as PROVEN.

**Status:** `READY TO PATCH`.

### STATE-011 / P1 — atomic file writes do not provide cross-file transactionality

**Positive proof:** `runtime_state_store._atomic_write_json()` uses temp-file + `os.replace`, so one file is protected from partial-write corruption.

**Gap:** positions/P&L/signals/QC/runtime-state files are still independently committed.

**Solution:** preserve atomic single-file helper for diagnostics; authoritative lifecycle/state uses Firestore transaction/event ledger + cycle manifest.

**Status:** `READY TO PATCH/DESIGN`.

### STATE-012 / P1 — Firestore tests miss adversarial multi-writer/restart cases

**Proof:** existing test verifies worker-field merge + monotonic global version and path-injection rejection. It does not model stale full-snapshot writers or backend-required failure.

**Solution tests:** add deterministic stale-writer, same-domain CAS conflict, independent-domain merge, transaction retry, service restart, overlapping revisions, unavailable Firestore, startup migration prevention and proven-empty semantics.

**PASS:** no lost updates, no local-authority fallback, no green defaults, deterministic replay.

**Status:** `READY TO PATCH`.

## 5. Canonical truth contracts

### 5.1 `SafetyTruth`
`mode`, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 5.2 `DataTruthEnvelope`
`source`, provider session, instrument, source/backend/frontend times, age/TTL, market state, schema/normalizer versions, row count/completeness, quality state, source/runtime revisions.

### 5.3 `StreamTruth`
Separate transport/stream/heartbeat state, last-event times, uncapped event age, TTL, sequence, rejected-old events, parse errors, source/session/schema, REST fallback and revisions.

### 5.4 `OptionChainTruth`
Underlying/security id/segment, requested+resolved expiry and authority, provider/session, source/receive times, age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, quality state, source/runtime revision and evidence ID.

### 5.5 `DeploymentTruth`
Exact source/tree SHA, Cloud Build ID, image tag+digest, final Cloud Run revision/traffic, frontend/backend SHA, runtime app/service account, policy/config hash, secret-reference metadata, scheduler/job provenance, verified time, quality and evidence ID.

### 5.6 `StateTruth` — NEW

```text
backend: FIRESTORE | LOCAL_DIAGNOSTIC
backend_required: bool
collection/document
shared_state_health: PROVEN | DEGRADED | ERROR | UNKNOWN
global_state_version  # diagnostic only
runtime_revision
instance_id
last_shared_read_at
last_shared_write_at
local_mirror_authoritative: false
domains:
  broker/market/positions/pnl/risk/chain/signals/qc/...:
    domain_revision
    writer_id
    writer_runtime_revision
    event_id
    source_event_time
    received_at
    schema_version
    quality: PROVEN | PROVEN_EMPTY | STALE | ERROR | UNKNOWN
    evidence_id
```

**Invariant:** no whole-process stale snapshot may overwrite a newer domain revision. Cloud shared-state failure never promotes local disk to authority.

### 5.7 `PaperLifecycleTruth`, `GateTruth`, `RiskPolicy`, `PreTradeRiskTruth`
Retain immutable lifecycle, semantic evidence gates, server-owned policy and fail-closed pre-trade decision contracts.

## 6. Canonical remediation roadmap

- `SOL-01 Auth/session — READY TO PATCH`: correct login body; cookie-only browser auth; remove raw API key; auth-gate polling/WS; TTL/revocation tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: single backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production zero/plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser fields; validated spread; expiry-aware cache; freshness/provenance; explicit IV units; full Greeks/model version.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 Scanner contract — READY TO PATCH`: rank/score/probability/forecast/realized distinct and nullable.
- `SOL-08 DeploymentTruth + GCP least privilege — READY TO PATCH`: immutable digest/final revision/source SHA/frontend/backend identity, one authoritative service mutation, dedicated service accounts, WIF-only auth, exact-revision evidence.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; monotonic REST/WS merge; uncapped age; true WS proof.
- `SOL-12 RuntimeEventEnvelope — READY TO PATCH/DESIGN`: logs/metrics/incidents bound to source SHA + digest + Cloud Run revision.
- `SOL-13 StateTruth + domain-CAS store — READY TO PATCH`: Firestore required in GCP; no local-authority fallback; sparse domain patches; per-domain revisions/writers; startup migration removed; cycle-consistent snapshots; proven-empty semantics.

### SOL-13 ordered implementation

1. Add `StateTruth`/`DomainEnvelope` schemas and API contract.
2. Set `SYSTEM3_STATE_BACKEND=firestore` and `SYSTEM3_STATE_BACKEND_REQUIRED=1` in the single final Cloud Run deployment mutation.
3. Grant only required Firestore permissions to explicit web/worker identities.
4. Replace whole-state `save(self._state)` with `save_domain_patch(domain, patch, expected_revision, writer_id, event_id)`.
5. Reject stale/out-of-order same-domain writers transactionally; preserve independent domains.
6. Remove production local-file fallback; local mirror becomes diagnostics-only and non-authoritative.
7. Remove unconditional `sync_from_files()` from runtime startup; move migration to explicit one-shot command.
8. Change fresh defaults from PASS/zero/empty to typed UNKNOWN/null, retaining separate hard live-off invariants.
9. Introduce canonical position/instrument identity and typed broker/internal source results.
10. Add cycle/generation IDs or atomic manifests for any remaining filesystem fan-in.
11. Deduplicate runtime state-store methods/load blocks.
12. Add adversarial two-writer, restart, overlapping-revision, Firestore-unavailable, stale-file and mixed-generation tests.
13. Expose read-only state provenance/drilldown in Data & Broker Health / Observability.
14. Add alert when domain writer revision or event time regresses; execution/readiness remains inhibited.

**SOL-13 PASS criteria:** exact Cloud Run revision proves Firestore-required authority; two stale writers cannot lose newer domain data; shared backend outage never promotes local disk; restart preserves/replays state deterministically; no mixed-generation snapshot is PROVEN; fresh boot is UNKNOWN not green; position/P&L/risk domains carry writer/revision/evidence metadata.

**Rollback/fail-safe:** preserve last proven shared state as `STALE_LAST_GOOD` read-only; reject new mutations and readiness until shared authority recovers.

## 7. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `15/20` | OPEN — state defaults + position empty/error collapse add independent reproductions |
| UI-002 | `3/20` | OPEN |
| UI-003 | `7/20` | OPEN — state backend/source authority adds independent proof |
| UI-005 | `13/20` | OPEN — state/risk/QC default semantics independently reproduce |
| UI-006 | `9/20` | OPEN — reconciliation error/empty collapse independently reproduced |
| UI-007 | `8/20` | OPEN |
| UI-009 | `6/20` | OPEN |
| UI-011 | `3/20` | OPEN |
| UI-016 | `8/20` | OPEN — state backend authority now separated from UI/runtime claims |
| UI-018 | `2/20` | OPEN |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `5/20` | OPEN |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `2/20` | OPEN |
| CHAIN-005 | `2/20` | OPEN |
| CHAIN-006..014 | `1/20` each | OPEN |
| READY-001 | `5/20` | OPEN — fresh state initializes plausible PASS/zero domains |
| READY-003 | `2/20` | OPEN |
| READY-008 | `2/20` | OPEN |
| PAPER-001 | `2/20` | OPEN |
| PAPER-003 | `3/20` | OPEN — startup/state P&L zero defaults reproduce |
| PAPER-005 | `2/20` | OPEN |
| PAPER-008 | `2/20` | OPEN |
| PAPER-009 | `2/20` | OPEN |
| PAPER-010..016 | `1/20` each | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| LEGACY-001 | `1/20` | OPEN / exposure UNPROVEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN |
| GCP-001..011 | `1/20` each | OPEN |
| STATE-001..012 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 8. Prioritized implementation order

### P0 Wave 1 — false-green/fail-open/state-authority elimination
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline.
4. **SOL-13 shared `StateTruth` authority + domain-CAS store.**
5. SOL-05 parser null-safety + expiry-aware/provenance-aware chain cache.
6. SOL-11 StreamTruth, uncapped age and ordered REST/WS merge.
7. SOL-09 server-owned risk + mandatory pre-trade authority.
8. SOL-06 durable lifecycle/idempotency/reconciliation.
9. remove dead/unproven paper mutation control.
10. SOL-04 semantic readiness.
11. SOL-03 remaining zero/live/default-safe fallbacks.
12. SOL-10 legacy mutation UI quarantine.
13. SOL-07 rank-as-percent repair.

### P1 Wave 2 — runtime/account/paper economics
Domain writer observability, GCP IAM split + WIF-only auth, RuntimeEventEnvelope, full Dhan/account provenance, IV/Greeks model truth, costed fills/P&L, portfolio risk, true WebSocket proof.

### P2 Wave 3 — institutional operator quality
Responsive/mobile, accessibility/keyboard/focus, command palette/search, deep drilldowns, SLO/incidents, security/session settings and audit export.

## 9. Product information architecture target

1. Command Center — Overview + Decision Intel + truth strip.
2. Market / Scanner — watch, scanner, ranker, signals.
3. Options & Greeks — chain, explicit expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + calibration/evidence.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — **shared-state authority, domain writers/revisions**, transport/heartbeat/source/freshness/auth/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, state/store incidents, alerts, runtime events, logs, schema/parse errors, latency, reconnects and revision-filtered evidence.
10. Security / Settings — sessions, IAM/policy versions, permissions, audit export, non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 10. Product UI visual evolution — V11

New concept: **State & Ledger Integrity V11** inside the actual `Data & Broker Health` product workspace.

Changes driven by this iteration:
- shared-state backend authority shown explicitly as FIRESTORE/ERROR/UNKNOWN rather than hidden implementation detail;
- local mirror visibly marked diagnostic/non-authoritative;
- every domain displays writer ID, domain revision, event age and evidence quality;
- no global version is allowed to imply all domains are current;
- stale-writer/conflict counters and rejected updates are operator-visible;
- startup/restart recovery and last proven shared revision are explicit;
- positions/P&L/risk carry generation/correlation IDs so mixed-cycle state is visible;
- `PROVEN_EMPTY` is distinct from `UNKNOWN/API_ERROR/SCHEMA_ERROR`;
- state backend outage forces execution/readiness `INHIBITED`;
- live router remains locked.

Visual artifact: `Genesis_System3_State_Ledger_Integrity_Target_V11.png`.

## 11. Positive foundations to preserve

- `_atomic_write_json()` uses temp-file + `os.replace`, preventing partial single-file writes.
- Firestore persistence already uses a transaction and keeps a monotonic global state version.
- state reads return JSON-cloned snapshots instead of mutable references.
- hard safety invariant forces PAPER/live-off in persisted state and should remain as defense-in-depth.
- corrupt local runtime state is quarantined rather than silently overwritten.
- Cloud Run is explicitly documented as runtime/scheduler authority.
- active workflow allow-list rejects Render runtime references, self-hosted runners, scheduled GitHub workflows and live-trading enable flags.
- Dhan option-chain traffic remains serialized/rate paced; WS reconnect has backoff+jitter foundation.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness or consistency proof.

## 12. Historical proof/open-gate interpretation

PR descriptions, workflow configuration, unit tests, atomic local writes, Firestore transaction existence, build strings and historical PASS artifacts remain scoped evidence only. They cannot prove current shared-state/runtime truth unless tied to exact source SHA + immutable image digest + final serving Cloud Run revision + domain revision/evidence.

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
- `SHARED_STATE_AUTHORITY_NOT_PROVEN`
- `RESTART_CONSISTENCY_NOT_PROVEN`
- `MULTI_WRITER_LOST_UPDATE_PROTECTION_NOT_PROVEN`
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 13. Closure standard

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; concurrency/CAS/restart/failover tests; expiry/cache/freshness/order/reconnect tests as applicable; restart/idempotency/reconciliation tests; immutable image digest + final Cloud Run revision/runtime proof where required; analyzer/live-off unchanged; and no contradictory independent evidence.

## 14. Next audit/solution slices

1. AI/ML/prediction ledger: calibration, frozen cutoff, model/hash, drift and realized after-cost outcome.
2. Responsive/accessibility: desktop/tablet/mobile, keyboard/focus/live regions/dense tables.
3. Scanner/ranker contracts and performance/memory/concurrency under market-open load.
4. Security/session detail: cookie policy, CSRF, session revocation, command/settings permissions and audit export.
5. DB follow-up: exact paper/event persistence files and any SQLite/JSON/Firestore duplicate authorities not yet mapped.

## 15. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser PASS, image tag, UI badge, workflow success description, global state version, Firestore transaction, local atomic write, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval or process-local simulator never substitutes for authoritative source+event time+domain revision+writer+freshness+schema+ordering+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.