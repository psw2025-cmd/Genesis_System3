# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 13:49 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `7cb3a5f01c2a8062e9c5a8e45052ddb72f8759d7`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`; compare from application HEAD to audit-start HEAD is 18 commits ahead and changes only this master Markdown.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`. Its proposed synthetic-P&L suppression still substitutes numeric zero rather than nullable typed truth.
- PR #96 is merged; current evidence still identifies it as the newest merged application/UI PR.
- Exact application-HEAD CI proof remains **NOT PROVEN**: GitHub returned no workflow runs and no combined status checks for `b70af343...` in this iteration.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH via SessionTruth** |
| Mutation route authorization | **FAIL / P0-P1** | **READY TO PATCH via MutationPolicy** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH via SafetyTruth** |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH via StateTruth + domain-CAS** |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH via StreamTruth** |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH via OptionChainTruth** |
| Scanner/ranker freshness + stability | **FAIL / P0-P1** | **READY TO PATCH via ScannerTruth** |
| Market-open performance/concurrency | **FAIL / P0-P1** | **READY TO PATCH via WorkCoordinator** |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH immutable lifecycle** |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN via PredictionTruth** |
| Responsive/accessibility | **FAIL / P1** | **READY TO PATCH** |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH via DeploymentTruth** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must record severity, exact proof, symptom, root cause, real-money impact, exact files/routes/components, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, security constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, timed-out, parse-failed, unauthenticated, overloaded or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..011` OPEN: login contract mismatch, raw browser API-key storage, deterministic non-expiring server token, logout without revocation, weak auth throttling, global secret injection, cookie-runtime uncertainty and incomplete CSRF/idempotency coverage.
- `MUT-001..008` OPEN: capability inventory gaps, file-backed live approval, path-list idempotency, worker replay semantics, route duplication and domain-gate separation.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, responsive/accessibility and deployment/build truth gaps.
- `CHAIN-001..014` OPEN: PCR warming false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `SCAN-001..010` OPEN: same-day stale rank acceptance, ignored refresh intent, auto-eligibility, invented live provenance, rotating-shard high-watermark retention, stale-row restamping, cache ambiguity, duplicate REST/WS writers, load-heavy rotation and UI freshness ambiguity.
- `READY-001..009` OPEN: false-safe evidence defaults, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN except `PAPER-010` corrected below: default safety/data values, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrails, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.
- `ML-001..014` OPEN: missing immutable prediction ledger, overloaded model-proof boolean, dictionary-first model selection, rank→confidence misuse, unknown→zero metrics, tracker type bug, unsafe accuracy math, non-atomic persistence, temporal leakage risks, incomplete artifact identity, selection/evaluation leakage, missing calibration and no after-cost linkage.
- `A11Y-001..012` OPEN: fixed shell, clipped truth, keyboard inefficiency, non-semantic controls, color-only indicators, weak live regions, tiny text, fragile overflow, inconsistent focus and missing exact-browser proof.
- `PERF-001..009` OPEN from this iteration: orphaned timed-out work, frontend overlap, chain stampede, overlapping paper ticks, false memory telemetry, response buffering, event-loop blocking state sync, batch fan-out and unbounded log-tail reads.

## 4. Latest deep slice — market-open performance, memory and concurrency truth

### PERF-001 / P0-P1 — timed-out `asyncio.to_thread()` work can continue invisibly and saturate the shared executor

**Exact proof:** `dashboard/backend/app.py::_run_blocking()` wraps `asyncio.to_thread(fn, ...)` in `asyncio.wait_for()`. The source itself documents the key runtime fact: `wait_for()` timing out does **not** cancel the underlying OS thread. Scanner work may wait 60–180 seconds, broker/truth work up to 45 seconds, and several runtime-QC/chain paths also use blocking worker calls.

**Symptom/root cause:** request timeout bounds the caller's wait, not the actual blocking function. Repeated slow broker/scanner/provider calls can leave old worker threads running after responses have already returned timeout/degraded states. The default asyncio executor is shared across unrelated domains.

**Real-money impact:** event processing, Dhan reads, scanner refreshes, risk/proof reads and UI APIs can starve behind invisible old work. Stale last-good values may remain visible while fresh work is queued, producing apparent liveness without current data.

**Exact files/functions likely to change:** `dashboard/backend/app.py::_run_blocking`, broker/scanner/chain/runtime-QC call sites, provider adapters under `core/brokers/dhan/` and `core/data/`.

**World-class target behavior:** blocking domains run through bounded named executors or async-native clients with cooperative provider timeouts. Scanner, Dhan chain and state-store work have separate concurrency budgets so one domain cannot starve another.

**Minimal safe design:** introduce `WorkCoordinator` with per-domain bounded capacity, queue timeout, execution timeout, singleflight key and metrics. Prefer provider-level socket/connect/read timeouts so underlying work actually terminates. Treat timeout as `ERROR/STALE`, never as proof of fresh truth.

**Ordered implementation:** 1) inventory all `to_thread`/blocking provider call sites; 2) create `scanner`, `chain`, `broker`, `state` bounded pools/semaphores; 3) add queue/execution deadlines; 4) add singleflight keys; 5) add cooperative HTTP timeouts; 6) emit active/queued/timed-out/orphan-risk counters; 7) inhibit mutation eligibility when authoritative data work exceeds freshness budgets.

**Schema/API:** `WorkTruth {domain, operation_id, request_id, singleflight_key, queued_at, started_at, finished_at, queue_age_ms, run_age_ms, timeout_policy_ms, state, runtime_revision, evidence_id}`.

**Migration/backward compatibility:** existing endpoints keep payload shape initially; add `work_truth` metadata. No execution behavior becomes more permissive.

**Security/safety:** executor backpressure may degrade reads but must never enable or route live orders. Overload forces read-only degraded behavior.

**Regression risks:** over-tight limits can reduce refresh frequency; mitigate with per-domain budgets and last-good stale display.

**Tests:** deliberately hang scanner and Dhan adapters; issue repeated requests; assert bounded worker/queue counts, unrelated `/api/state` latency remains within SLO, timed-out work cannot create fresh evidence after caller timeout, and no mutation eligibility advances.

**PASS:** worker/thread count remains bounded under repeated timeouts and every domain exposes queue/run truth.

**Rollback/fail-safe:** reduce concurrency to one per heavy domain and serve typed stale/unknown snapshots.

**Status:** `READY TO PATCH`.

### PERF-002 / P1 — frontend core polling can overlap under degradation

**Exact proof:** `dashboard/frontend/src/hooks/useData.ts` uses a 20-second market-open core interval but `fetchJSON('/api/batch/market-data', 25000)` allows a 25-second timeout. `setInterval(poll, ...)` has no in-flight guard, request generation ID or cancellation-before-retry.

**Symptom/root cause:** when backend latency exceeds 20 seconds, a second market-data request starts before the first has completed. Each browser can therefore maintain overlapping core requests during the exact period when the backend is already degraded.

**Impact:** load amplification, response reordering and stale-over-new store writes. Multiple open browsers multiply the pressure.

**Exact files/components:** `dashboard/frontend/src/hooks/useData.ts`, store reducers, `/api/batch/market-data`.

**Target:** completion-driven scheduling (`setTimeout` after request completion), visibility-aware pause, one in-flight request per domain, request/snapshot revision rejection and exponential backoff with jitter.

**Implementation:** replace core `setInterval` with recursive completion scheduler; abort superseded requests where safe; tag request generation; reject response older than store snapshot revision; pause low-priority polling on hidden tabs while maintaining critical safety heartbeat.

**API changes:** batch payload gains immutable `snapshot_id`, `generated_at`, `source_event_at`, `runtime_revision`, `evidence_id`.

**Tests:** delay batch response beyond 20s; prove max in-flight core request per browser = 1 and older response cannot overwrite newer WS/store revision.

**PASS:** no polling overlap and no stale response time-travel.

**Rollback:** fall back to slower completion-driven polling only.

**Status:** `READY TO PATCH`.

### PERF-003 / P0-P1 — chain cache miss has no per-symbol singleflight and can stampede Dhan

**Exact proof:** `/api/chain/{underlying}` checks pushed cache then TTL cache, then directly awaits `_get_chain_uncached()`. No per-symbol lock/singleflight is present around the cache-miss live fetch. Browser boot independently starts `/api/batch/chains` and the active `/api/chain/{symbol}` request; multiple clients can hit the same cold symbol simultaneously.

**Root cause:** cache protects only after a completed fetch; it does not coalesce concurrent misses.

**Impact:** concurrent Dhan option-chain calls increase throttling, thread backlog and stale/fallback responses; market truth can degrade under user load.

**Files/functions:** `dashboard/backend/app.py:get_chain`, `_get_chain_uncached`, Dhan chain adapter, frontend `useData.ts` boot/chain timers.

**Target:** one active fetch per canonical `(provider, security_id, expiry)` key; all concurrent readers await the same future or receive typed `PENDING/STALE_LAST_GOOD`.

**Implementation:** keyed `SingleFlight` registry, expiry-aware canonical cache key, max waiter count/deadline, provider token bucket, event/source timestamp preserved from fetch result.

**Tests:** 20 concurrent requests for same chain on cold cache produce exactly one provider call; other symbols obey bounded parallelism; failed fetch does not poison cache.

**PASS:** provider call count matches unique singleflight keys, not request count.

**Rollback:** deny inline fetch under overload and serve stale-last-good/pending only.

**Status:** `READY TO PATCH` with `OptionChainTruth`.

### PERF-004 / P0 — `POST /api/paper/tick` can schedule overlapping heavy paper-engine ticks

**Exact proof:** `dashboard/backend/app.py` contains `POST /api/paper/tick`. It obtains a shared paper engine, then `background_tasks.add_task(_run_tick)`. `_run_tick` sequentially loads four index chains, optionally runs the scanner and finally calls `engine.step(...)`. The route has no tick idempotency key, singleflight lock, queue depth check or engine mutation lock.

**Symptom/root cause:** repeated POSTs return `accepted` immediately and can schedule multiple background ticks against the same process-local engine and files.

**Real-money/paper impact:** duplicated opens, conflicting close/open lifecycle writes, inconsistent P&L and non-deterministic evidence. Although PAPER only, bad paper truth invalidates readiness metrics and risk calibration.

**Exact files/routes:** `dashboard/backend/app.py:/api/paper/tick`, `dashboard/backend/cloud_paper_engine.py`, paper state files, `MutationPolicy`, `PreTradeRiskService`.

**World-class target:** paper tick is a durable/idempotent `PAPER_MUTATION` command with exactly-once logical semantics per cycle/snapshot; only one mutation worker owns the engine state.

**Minimal design:** require `Idempotency-Key`, `candidate/snapshot IDs`, server risk decision, enqueue immutable command, process in a single paper mutation worker, ledger order/fill/position events transactionally, expose tick status rather than spawning free-form request background tasks.

**Tests:** submit same key 20 times => one logical tick; submit different keys concurrently => serialized deterministic ledger order; restart during tick => replay/reconcile exactly once; no live broker method invoked.

**PASS:** zero concurrent `engine.step()` calls and deterministic ledger result.

**Rollback:** disable Force Paper Tick UI/route mutation and retain read-only paper monitoring.

**Status:** `READY TO PATCH`.

### PERF-005 / P1 — memory telemetry uses peak RSS as if it were current RSS

**Exact proof:** `dashboard/backend/middleware/memory_guard.py::_rss_mb()` uses `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss` when Python `resource` is available. On Linux this is a process high-water mark, not current RSS. `/proc/self/status` current-RSS logic is used only if `resource` import fails.

**Symptom/root cause:** after one peak, `rss_after` can remain high forever even after GC releases memory. GC and warning decisions therefore operate on historical maximum rather than current pressure.

**Impact:** misleading operator health, repeated unnecessary GC every cooldown, latency spikes and inability to distinguish recovered memory from active leak.

**Files:** `dashboard/backend/middleware/memory_guard.py`, `/api/health` memory display and Observability UI.

**Target:** expose both `current_rss_mb` and `peak_rss_mb`; trigger GC/backpressure from current RSS only.

**Implementation:** read current RSS from `/proc/self/status` or a vetted process-metrics library; retain `ru_maxrss` only as `peak_rss_mb`; add cgroup/container memory limit/usage when available.

**Tests:** allocate then free a large buffer; current RSS must fall while peak remains; GC trigger uses current value; UI labels distinguish both.

**PASS:** no current-memory decision is driven by peak RSS.

**Rollback:** disable automated GC action and expose metrics only if current RSS cannot be proven.

**Status:** `READY TO PATCH`.

### PERF-006 / P1-P2 — chain truth middleware buffers and recopies entire response bodies

**Exact proof:** `_enforce_dhan_only_chain_response()` iterates `response.body_iterator` and repeatedly executes `body += chunk`, then parses/re-serializes JSON. This occurs for `/api/chain/*` responses and can duplicate large option-chain payloads in memory.

**Root cause:** data-source safety validation is implemented after response serialization in middleware rather than in the chain truth service before response construction.

**Impact:** unnecessary allocation/copying and GC pressure during exactly the high-frequency option-chain path; response truth can also differ from service-internal truth.

**Files:** `dashboard/backend/middleware/memory_guard.py`, chain service/endpoint.

**Target:** validate `OptionChainTruth` before serialization; middleware observes metadata only.

**Implementation:** move Dhan/source/freshness validation into chain normalizer/service; return typed blocked payload directly; remove response-body interception. If temporary interception remains, use bounded bytearray/list-join with hard max size.

**Tests:** large-chain response memory delta bounded; endpoint and UI receive identical truth state; invalid source rejected before serialization.

**PASS:** no chain response-body buffering middleware in production path.

**Rollback:** cap body inspection size and block oversized/unknown payloads fail-closed.

**Status:** `READY TO PATCH` with `OptionChainTruth`.

### PERF-007 / P0-P1 — async state-sync loop performs synchronous broker/state/file work on the event loop

**Exact proof:** `StateSyncService._sync_loop()` awaits `sync_state()`, but `sync_state()` directly calls `state_store.get_state()` multiple times, invokes Dhan `_probe_dhan()` directly when broker appears disconnected, performs many synchronous file reads, and calls `state_store.update_state(updates)` directly.

**Root cause:** an async loop wraps synchronous I/O without offloading or async-native store/provider APIs.

**Impact:** a slow Firestore/state call, Dhan probe, filesystem stall or large JSON parse can pause FastAPI/WebSocket event-loop progress, delaying heartbeats and causing the UI to look stale/disconnected for a reason unrelated to actual broker state.

**Files:** `dashboard/backend/state_sync_service.py`, runtime state store, Dhan readonly adapter.

**Target:** state sync has a bounded runtime budget and never blocks the event loop. One sync runs at a time; skipped/late cycles are observable.

**Implementation:** make state store async or offload through dedicated state executor; move broker probe to broker worker/service; coalesce file reads into one generation snapshot; enforce sync deadline; record `sync_started/finished/late/skipped` and source generation IDs.

**Tests:** inject 5s blocking store and Dhan probe; WebSocket heartbeat and `/api/health` remain responsive; no overlapping sync cycles; late cycle marked DEGRADED.

**PASS:** event-loop lag remains within SLO under slow state/provider I/O.

**Rollback:** disable direct broker probing from sync loop and reduce sync to local non-blocking metadata until shared state worker is healthy.

**Status:** `READY TO PATCH` with `StateTruth`.

### PERF-008 / P1 — batch endpoints aggregate multiple domain calls without server-wide singleflight

**Exact proof:** `/api/batch/market-data` concurrently gathers health, state, paper, gain rank, P&L, alerts and gates with per-call timeouts; `/api/batch/positions-holdings` concurrently gathers Dhan status, funds, holdings and positions. The 8-second in-process cache reduces repeats only after a request has completed; simultaneous cold requests can each execute the fan-out.

**Root cause:** TTL cache lacks promise/snapshot coalescing and is process-local per Cloud Run instance.

**Impact:** cold start or multiple operator browsers can duplicate broker/scanner/file work, causing latency spikes and cache races.

**Files:** `dashboard/backend/app.py:batch_market_data`, `batch_positions_holdings`, `_API_CACHE`, deployment scaling policy.

**Target:** batch reads consume already-produced domain snapshots; request handlers do not trigger heavy provider work. Cold cache uses singleflight per batch/domain snapshot.

**Implementation:** add per-key async singleflight; materialize broker/scanner/chain/state snapshots in workers; batch endpoint performs cheap revision-consistent joins; include domain revisions and mixed-generation detection.

**Tests:** 50 simultaneous cold batch requests trigger one build per cache key; batch response domains share compatible generation IDs; p95 remains bounded.

**PASS:** batch request count does not multiply provider work.

**Rollback:** serve `PENDING/STALE_LAST_GOOD` while a single refresh is active.

**Status:** `READY TO PATCH`.

### PERF-009 / P2 — log-tail endpoint reads the entire latest log file into memory

**Exact proof:** `/api/logs/tail` calls `f.readlines()` and only afterward slices `[-lines:]`.

**Root cause:** tail semantics implemented as full-file load.

**Impact:** large production logs can create avoidable memory spikes and GC pressure when an operator opens Observability during an incident.

**Files:** `dashboard/backend/app.py:/api/logs/tail`, Observability UI.

**Target:** bounded reverse-tail read by bytes/lines with response-size cap and redaction.

**Implementation:** seek from end in bounded blocks or use rotating structured log backend; enforce max lines/max bytes; return truncation metadata.

**Tests:** multi-GB synthetic log fixture; process memory delta stays bounded; returned last N lines correct and secrets redacted.

**PASS:** endpoint memory use is O(response cap), not O(log file size).

**Rollback:** disable local log-tail endpoint and rely on Cloud Logging links/export.

**Status:** `READY TO PATCH`.

## 5. Canonical performance solution — `SOL-18 WorkCoordinator + SnapshotScheduler`

**Status:** `READY TO PATCH`.

One canonical solution covers the shared root cause: heavy work is currently request-triggered, partially cached, timeout-bounded only at the waiter, and not consistently revision/singleflight aware.

### Required contracts

`WorkTruth {operation_id, domain, key, request_id, state, queued_at, started_at, finished_at, queue_age_ms, run_age_ms, timeout_ms, worker_id, runtime_revision, evidence_id}`

`SnapshotTruth {snapshot_id, domain_revision, source_event_at, received_at, generated_at, age_ms, ttl_ms, provenance, schema_version, runtime_revision, evidence_id, quality}`

### Implementation order

1. Inventory every blocking/provider/file-heavy function used by API, background tasks and state sync.
2. Introduce bounded executors/semaphores by domain: `broker`, `chain`, `scanner`, `state`, `paper`.
3. Add keyed singleflight for chain, scanner, batch snapshot and paper mutation commands.
4. Replace request-triggered scanner/chain fan-out with scheduled snapshot producers.
5. Make browser polling completion-driven, visibility-aware and revision rejecting.
6. Separate current RSS from peak RSS; add event-loop lag, queue depth and worker counters.
7. Move chain truth validation before response serialization.
8. Make state sync non-blocking to the event loop and generation-aware.
9. Serialize paper mutation through durable command/ledger processing with idempotency and PreTradeRiskService.
10. Add overload state `DEGRADED_READ_ONLY`; stale/unknown data inhibits mutation eligibility.
11. Expose all runtime-pressure truth through Observability and command-center Tier-0 header.

### Exact closure tests

- 100 concurrent cold `/api/chain/NIFTY` requests => one provider fetch for the canonical key.
- Repeated scanner timeouts => bounded worker/thread count and no starvation of `/api/state`/WebSocket heartbeat.
- Market-data response delayed 30s => browser keeps one core request in flight and rejects older response revision.
- 20 duplicate paper ticks => one logical command; different ticks serialize and reconcile deterministically.
- Slow Firestore/Dhan probe => event-loop lag remains under declared SLO and sync marks itself late/degraded.
- Allocate/free memory => current RSS recovers while peak RSS remains separately visible.
- 50 simultaneous batch requests => one snapshot build per cache key/generation.
- Large chain and log responses => memory remains under bounded response caps.
- No overload/error condition may alter live-router lock, authorize live mutation or fabricate fresh market truth.

**PASS:** work concurrency is bounded and observable, refreshes are revision-consistent, provider call count is workload-derived rather than browser-count-derived, and overload degrades to typed read-only truth.

## 6. Regression check and finding correction

### `PAPER-010` correction — previous route-absence claim is CLOSED as an audit discovery error

A deeper direct source read now proves `dashboard/backend/app.py` **does contain** `POST /api/paper/tick`. Therefore the earlier statement that the frontend Force Paper Tick control called an absent backend route was incorrect.

- **Prior status:** FIX-REQUIRED because route was believed absent.
- **Current status:** **CLOSED / CORRECTED** for route existence only.
- **Replacement risk:** `PERF-004` plus existing paper-lifecycle findings remain **FIX-REQUIRED** because the actual route schedules overlapping un-idempotent background paper mutation work.
- **Counter discipline:** the old route-absence counter must not advance further and can never reach LOCKED-20X.

### Mutation inventory correction

The deeper source slice also proves additional active mutations not included in the previous short route list, including `/api/paper/tick` and `/api/positions/{position_id}/close`. `SOL-17 CapabilityManifest` therefore becomes even more important: route discovery must be generated from `app.routes`, not manual grep/search evidence.

### Critical prior findings rechecked

- Application source HEAD remains unchanged at `b70af343...`.
- PR #97 remains open and therefore cannot close synthetic-P&L findings on `main`.
- Exact application-head workflow/status evidence remains absent.
- `useData.ts` still has overlapping-poll risk and REST/WS competing writers.
- `StateSyncService` still has synchronous I/O inside its async sync loop.
- `memory_guard.py` still uses peak RSS for current-pressure decisions.
- Live router remains required to stay OFF/LOCKED; nothing in this iteration enables live order routing.

## 7. Prioritized remediation roadmap

### P0
1. Fix `AUTH-001` login request contract and remove raw browser API-key persistence/global injection.
2. Implement server-enforced SessionTruth expiry/revocation.
3. Implement `SOL-17 MutationPolicy + CapabilityManifest`; generate mutation inventory from `app.routes`.
4. Hard-deny live approval/mutation in analyzer/paper and replace file-backed approval authority.
5. Establish authoritative SafetyTruth and DeploymentTruth.
6. Establish StateTruth/domain-CAS shared-state authority.
7. Implement `PERF-004` serialized/idempotent paper mutation and mandatory PreTradeRiskService.
8. Implement bounded WorkCoordinator for blocking provider/scanner/state domains (`PERF-001/007`).

### P1
1. Add per-symbol/expiry chain singleflight (`PERF-003`) and OptionChainTruth.
2. Replace overlapping frontend intervals with completion-driven revision-aware polling (`PERF-002`).
3. Add batch/snapshot singleflight and worker-produced scanner/chain snapshots (`PERF-008`).
4. Correct current-vs-peak memory telemetry and expose event-loop/executor pressure (`PERF-005`).
5. Move chain response truth enforcement out of body-buffering middleware (`PERF-006`).
6. StreamTruth heartbeat/freshness/ordering.
7. ScannerTruth latest-observation semantics and worker isolation.
8. Durable paper event ledger/reconciliation and after-cost P&L.
9. PredictionTruth/model provenance/calibration.
10. Exact browser accessibility/runtime proof.
11. Retire all active Render-era operational instructions.

### P2
1. Bounded log-tail/Cloud Logging integration (`PERF-009`).
2. Advanced institutional drilldowns and non-authoritative convenience analytics after P0/P1 truth contracts are proven.

## 8. Independent verification counters

Counters require independent reproductions and never advance merely because text was copied forward.

- `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`; remaining `AUTH-*` at least `1/20`.
- `UI-001 19/20`, `UI-005 16/20`, `UI-007 12/20`, `UI-016 13/20`.
- `MUT-001..008` remain at least `1/20`; route-inventory completeness is explicitly NOT LOCKED.
- `PERF-001..009 1/20` — first independent performance/concurrency slice.
- `PAPER-010 route-absence claim` is **CLOSED/CORRECTED**, not LOCKED; replacement `PERF-004 1/20` is open.
- Previously established `CHAIN`, `SCAN`, `WS`, `GCP`, `STATE`, `ML`, `A11Y`, `PAPER`, `RISK`, `READY` counters remain below 20.
- **No finding is `LOCKED-20X`.**

## 9. Product-design track — Performance & Concurrency Control V17

This iteration's actual Genesis System3 product design belongs to the `Observability` workspace and is not an audit-status report.

### REQUIRED

- Tier-0 market/Dhan/WS/last-event truth plus PAPER mode and LIVE LOCKED.
- Event-loop lag, current RSS, peak RSS, active/queued work and timeout counters.
- Per-domain executor/queue/singleflight state for broker, chain, scanner, state and paper.
- Request/job timeline with request ID, operation ID, timeout policy and evidence ID.
- Cache/snapshot revision, event age, TTL and stale-write rejection.
- Frontend poll/WS revision state and old-REST overwrite rejection.
- Paper tick queue/active/idempotency/engine-lock/risk state.
- DEGRADED_READ_ONLY state when backpressure/freshness limits are exceeded.

### RECOMMENDED

- p50/p95/p99 endpoint latency, cache-hit ratio, provider-call budget, queue wait histogram, worker saturation trend and dropped stale write count.
- Drilldown from scanner/chain/paper event to exact runtime revision and source snapshot.
- Browser/client count and hidden-tab polling suppression visibility.

### OPTIONAL

- Historical capacity-planning charts and operator tuning controls only after limits are server-policy bound and cannot weaken safety.

## 10. Closure discipline

No finding is CLOSED without exact application revision, exact runtime/deployment revision where applicable, reproducible tests, evidence IDs and independent verification. A corrected audit-discovery error may be closed only for the incorrect claim itself; newly exposed underlying defects remain separately open. UI completeness, trade readiness, profitability, broker truth, deployment success and live safety remain unproven unless separately evidenced.

## 11. Next deep slice

Risk/live-gate/order-safety integration: trace every paper/live-adjacent mutation from UI/API through risk checks, kill switch, account state, broker adapter and final router boundary; verify whether any endpoint, legacy module, scheduler job or direct executor path can bypass the canonical PreTradeRiskService/SafetyTruth hard gate, while keeping live routing strictly OFF.