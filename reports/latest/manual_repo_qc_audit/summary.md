# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 12:48 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `b2fe6de80bd96a5ad48aa07c80b42a25ac360b96`.
- Latest application/source HEAD remains `b70af343340a73ed27ca548820d5893c779ab5bd`; subsequent observed commits are audit-report-only iterations.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main` and its proposed synthetic-P&L suppression still substitutes numeric zero rather than nullable typed truth.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Exact application-HEAD CI proof remains **NOT PROVEN**: GitHub returned no workflow runs and no combined status checks for application HEAD `b70af343...` in this iteration.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH via SessionTruth** |
| Mutation route authorization | **FAIL / P0-P1** | **READY TO PATCH via MutationPolicy** |
| CSRF / idempotency | **INCOMPLETE / P0-P1** | capability-based enforcement required |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH via SafetyTruth** |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH via StateTruth + domain-CAS** |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH via StreamTruth** |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH via OptionChainTruth** |
| Scanner/ranker freshness + stability | **FAIL / P0-P1** | **READY TO PATCH via ScannerTruth** |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH immutable lifecycle** |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN via PredictionTruth** |
| Responsive/accessibility | **FAIL / P1** | **READY TO PATCH** |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH via DeploymentTruth** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must record severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, security constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..011` OPEN: login contract mismatch, raw browser API-key storage, non-expiring deterministic token, logout without revocation, weak throttling, global secret injection, cookie-runtime uncertainty, incomplete CSRF/idempotency coverage.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, responsive/accessibility and deployment/build truth gaps.
- `CHAIN-001..014` OPEN: PCR warming false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `SCAN-001..010` OPEN: same-day stale rank acceptance, ignored refresh intent, auto-eligibility, invented live provenance, rotating-shard high-watermark retention, stale-row restamping, cache ambiguity, duplicate REST/WS writers, load-heavy rotation and UI freshness ambiguity.
- `READY-001..009` OPEN: false-safe evidence defaults, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN: default safety/data values, unproven paper mutation route, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrails, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.
- `ML-001..014` OPEN: missing immutable prediction ledger, overloaded model-proof boolean, dictionary-first model selection, rank→confidence misuse, unknown→zero metrics, tracker type bug, unsafe accuracy math, non-atomic persistence, temporal leakage risks, incomplete artifact identity, selection/evaluation leakage, missing calibration and no after-cost linkage.
- `A11Y-001..012` OPEN: fixed shell, clipped truth, keyboard inefficiency, non-semantic controls, color-only indicators, weak live regions, tiny text, fragile overflow, inconsistent focus and missing exact-browser proof.

## 4. Latest deep slice — complete mutation-route security boundary

### MUT-001 / P0 — live-approval endpoint mutates safety state without capability-specific hard lock

**Exact proof:** `dashboard/backend/app.py` exposes `POST /api/live-trading/approve`. The handler checks a fixed approval phrase and writes `live_trading_approved=true`, the approval phrase, timestamp and note into `config/kill_switch.json`.

**Symptom/root cause:** a generic authenticated POST can mutate live-approval state through file persistence. Authorization is route/method based rather than an explicit `LIVE_APPROVAL` capability with independent backend safety invariants.

**Real-money impact:** if future runtime/order code consumes this flag permissively, a UI/API action could become part of a live-enablement chain despite current policy requiring analyzer/paper/live-off.

**Exact files/routes likely to change:** `dashboard/backend/app.py:/api/live-trading/approve`, `dashboard/backend/security_policy.py`, live-gate/kill-switch readers, `config/kill_switch.json` migration logic, Security/Settings frontend.

**World-class target behavior:** live approval is not a mutable boolean. It is a signed/revision-bound approval evidence record that can never itself enable routing. Independent backend gates must still require deployed `LIVE_TRADING_ENABLED`, router hard lock state, fresh risk/safety truth, exact runtime revision and explicit operator authorization.

**Minimal safe design:** classify endpoint as `LIVE_APPROVAL`, deny by default in analyzer/paper builds, require privileged session scope + CSRF + idempotency + fresh SafetyTruth/DeploymentTruth evidence, write append-only approval event, never store approval phrase, and keep router hard-locked.

**Ordered implementation:** 1) add capability metadata; 2) make analyzer/paper deployments return 423/403 for `LIVE_APPROVAL`; 3) replace file boolean with append-only approval evidence; 4) remove stored phrase; 5) bind approval to runtime/source revision and expiry; 6) require independent backend live gate; 7) add security event + UI evidence drilldown.

**Schema/API:** `LiveApprovalEvidence {approval_id, principal, issued_at, expires_at, source_sha, runtime_revision, safety_evidence_id, risk_evidence_id, policy_revision, state}`. No secret phrase persisted.

**Compatibility/migration:** existing `live_trading_approved` file value must be treated as legacy/untrusted and migrated to `UNKNOWN/EXPIRED`, never promoted.

**Security/safety:** endpoint cannot place/modify/cancel/route orders; router remains hard locked. Unknown evidence denies.

**Regression tests:** analyzer/paper mode always rejects; missing privilege/CSRF/idempotency rejects; stale revision rejects; duplicate idempotency key returns same result; legacy file cannot authorize; router remains disabled after approval event.

**PASS:** no route or stored flag can independently change order-routing authority; live approval evidence is revision-bound and expiring.

**Rollback/fail-safe:** remove/disable endpoint and keep `LIVE_TRADING_ENABLED=0`, router locked, legacy approvals ignored.

**Status:** `READY TO PATCH`.

### MUT-002 / P1 — live-approval route still embeds Render as the operational authority

**Exact proof:** the endpoint docstring says `LIVE_TRADING_ENABLED` must be manually set on the Render dashboard.

**Root cause/impact:** stale deployment instructions create contradictory operator guidance even though Google Cloud is the sole target. This can lead to wrong runbooks and unverifiable readiness state.

**Solution:** remove Render-era text from executable code and expose deployment authority only through `DeploymentTruth` (`GCP_CLOUD_RUN`). Add CI grep across active code/docs for Render operational instructions, with explicit archival allow-list only.

**Tests/PASS:** active runtime/UI/runbook contains no Render activation instructions; deployment authority reads `GCP_CLOUD_RUN` from typed provenance.

**Status:** `READY TO PATCH`.

### MUT-003 / P1 — security policy recognizes idempotency for paths that are not part of the audited active app route set

**Exact proof:** `IDEMPOTENCY_REQUIRED_PATHS` contains `/api/orders/create` and `/place-order`, while the active `dashboard/backend/app.py` mutation decorators identified in this slice are `/api/auth/session`, `/api/auth/logout`, `/api/scheduler/health/push`, `/api/chain/push`, and `/api/live-trading/approve`.

**Symptom/root cause:** replay protection is a manually curated path list that can drift away from the actual FastAPI route inventory.

**Impact:** developers can add a financially meaningful mutation without adding it to the separate idempotency list; conversely stale route names create false assurance.

**Solution:** generate route inventory from `app.routes` at startup/test time and require explicit capability metadata on every non-safe method. Capability—not path string—determines authentication, CSRF, idempotency, privilege and analyzer/live policy.

**Tests/PASS:** CI enumerates all POST/PUT/PATCH/DELETE routes; every route has exactly one capability classification; unknown mutation fails CI and startup in production strict mode.

**Status:** `READY TO PATCH`.

### MUT-004 / P1 — logout is public and state-mutating but security policy bypasses mutation checks

**Exact proof:** `/api/auth/logout` is in `PUBLIC_EXACT`; `evaluate_request()` immediately allows public exact paths before mutation classification. The route currently deletes only the browser cookie and does not revoke a server session.

**Root cause:** logout was treated as harmless/public while future SessionTruth makes it a real server-side revocation mutation.

**Target:** logout may be unauthenticated-idempotent for cookie cleanup, but when a valid session exists it must revoke that exact session server-side using a dedicated `SESSION_REVOKE_SELF` capability and same-origin/CSRF policy appropriate to browser logout.

**Tests/PASS:** cross-site logout cannot revoke another session; repeated logout is harmless; copied cookie is rejected after server revocation.

**Status:** `READY TO PATCH` together with `AUTH-005`.

### MUT-005 / P1 — worker ingestion is separately authenticated but lacks canonical event idempotency/replay semantics

**Exact proof:** `/api/scheduler/health/push` and `/api/chain/push` are protected by `X-Worker-Token` through `WORKER_PUSH_PATHS`, but `IDEMPOTENCY_REQUIRED_PATHS` does not include worker ingestion.

**Impact:** retries, duplicate deliveries or delayed events can mutate shared dashboard truth more than once or overwrite newer state unless downstream state/version checks independently reject them.

**Solution:** `WORKER_INGEST` requires `event_id`, producer/runtime revision, source event time, sequence/domain revision and idempotency record. Security policy verifies worker identity; StateTruth/StreamTruth rejects duplicate/out-of-order events.

**Tests/PASS:** duplicate event ID is no-op; older sequence cannot overwrite newer; wrong worker token fails; token never enters logs.

**Status:** `READY TO PATCH`.

### MUT-006 / P0-P1 — route-level security cannot substitute for domain safety enforcement

**Exact proof:** `security_policy.evaluate_request()` decides access using request method/path, dashboard access, worker token, Origin and optional idempotency key. It does not know SafetyTruth, risk state, paper/live mode, runtime revision, account state or mutation-domain prerequisites.

**Impact:** an authenticated request can pass HTTP security even when domain truth is unknown/stale unless each handler independently implements correct hard guards.

**Canonical solution:** two layers are mandatory: `MutationPolicy` handles identity/origin/replay/capability; domain service (`PaperMutationService`, `PreTradeRiskService`, `SafetyTruth`, `StateTruth`) independently decides whether mutation is semantically allowed. UI is never authority.

**PASS:** every state-changing handler calls its domain service after security middleware; unit tests prove valid auth + invalid domain state still fails closed.

**Status:** `READY TO PATCH`.

### MUT-007 / P1 — active mutation inventory is concentrated in monolithic `app.py`, while disabled modular routers create future drift risk

**Exact proof:** `app.py` comments that broker/chain/ml modular routers are disabled because they duplicated 19 routes and overrode richer endpoint versions. Broker router is currently read-only, but duplicate route architecture is explicitly acknowledged in source.

**Impact:** re-enabling routers during refactor can silently alter route contracts/security behavior or create duplicate mutation owners.

**Solution:** one route owner per path/method enforced by route-inventory CI. Modularization must MOVE handlers from `app.py`, not duplicate them. Security capability metadata travels with the canonical route definition.

**Tests/PASS:** route `(method,path)` uniqueness assertion; expected owner module manifest; startup fails on duplicates in strict production mode.

**Status:** `READY TO PATCH/DESIGN`.

### MUT-008 / P1/UI — Security / Settings needs explicit mutation capability visibility, not generic auth status

**Symptom:** operators cannot currently see which capabilities are permitted, inhibited, or hard-locked by server policy.

**Target UI:** Security / Settings presents read-only capability matrix for `READ_DATA`, `SESSION_REVOKE_SELF`, `PREFERENCE_WRITE`, `PAPER_MUTATION`, `RISK_POLICY_WRITE`, `WORKER_INGEST`, `LIVE_APPROVAL`, `LIVE_MUTATION`, with auth method, CSRF requirement, idempotency requirement, domain gate, policy revision and current state.

**Safety:** controls never create authority; they display server-enforced policy. Live mutation remains `LOCKED` unless separately proven in future.

**Tests/PASS:** UI states originate from a signed/typed capability endpoint; unknown capability renders UNKNOWN/INHIBITED, never enabled.

**Status:** `READY TO PATCH/DESIGN`.

## 5. Canonical mutation solution — `SOL-17 MutationPolicy + CapabilityManifest`

**Status:** `READY TO PATCH`.

`CapabilityManifest` is the only mutation classification authority. Each route declares:

`capability`, `auth_methods`, `required_scope`, `csrf_policy`, `idempotency_policy`, `domain_gate`, `analyzer_policy`, `paper_policy`, `live_policy`, `audit_classification`, `runtime_revision`.

Required capability classes:

- `READ_DATA` — safe methods only.
- `SESSION_CREATE` — public credential exchange with throttling.
- `SESSION_REVOKE_SELF` — idempotent session revocation.
- `WORKER_INGEST` — worker identity + event idempotency + sequence.
- `PREFERENCE_WRITE` — authenticated browser + CSRF.
- `PAPER_MUTATION` — privileged session + CSRF + idempotency + PaperMutationService + PreTradeRiskService.
- `RISK_POLICY_WRITE` — privileged scope + immutable policy versioning + idempotency.
- `LIVE_APPROVAL` — disabled in analyzer/paper deployment; revision-bound evidence only.
- `LIVE_MUTATION` — hard backend lock; no active route permitted until separately proven.

### Implementation steps

1. Add route decorator/helper carrying capability metadata.
2. Build startup route inventory from FastAPI `app.routes`.
3. Fail CI on any unclassified POST/PUT/PATCH/DELETE.
4. Fail strict production startup on duplicate `(method,path)` owners.
5. Replace path-based idempotency set with capability policy.
6. Add centralized same-origin/CSRF enforcement for browser mutations.
7. Add shared idempotency store in Firestore/state authority with TTL and response replay.
8. Add worker event IDs + domain sequences.
9. Move domain authorization into canonical services; security middleware cannot authorize trading semantics.
10. Replace live-approval file mutation with append-only evidence and hard analyzer/paper deny.
11. Emit sanitized `MutationAuditEvent` with request ID, capability, principal hash, policy/runtime revision, decision and evidence ID.
12. Expose read-only capability matrix to Security / Settings.

### Exact test matrix

- Route inventory: all non-safe routes classified; no duplicate path/method owner.
- Auth matrix: anonymous, expired, revoked, wrong scope, service header, cookie session.
- CSRF: missing Origin, forged Origin, cross-site form, valid same-origin.
- Idempotency: missing key, duplicate key same payload, duplicate key different payload, expiry/replay.
- Worker replay: duplicate event, stale sequence, wrong revision, bad token.
- Domain fail-closed: valid HTTP auth with UNKNOWN SafetyTruth/risk/state still rejects mutation.
- Analyzer invariant: `LIVE_APPROVAL` and `LIVE_MUTATION` are denied and router remains locked.
- Audit redaction: no API key, cookie, Dhan token, PIN/TOTP, worker token or approval phrase in events.

**PASS:** every mutation is explicitly classified, replay-safe where state-significant, domain-gated, revision-evidenced and independently fail-closed. No UI or generic authenticated POST can become live-routing authority.

## 6. Regression check of critical facts

- `security_policy.py` still fails mutations when dashboard auth is disabled/unconfigured: positive foundation retained.
- Worker push routes still have separate worker-token policy: positive foundation retained, but replay semantics are missing.
- Idempotency remains path-specific and therefore incomplete.
- The live-approval handler still writes approval state to `config/kill_switch.json`, stores the phrase, and contains Render-era activation wording.
- Modular broker router remains read-only and disabled from `app.py`; route duplication debt remains explicit.
- Exact application-head workflow/runtime proof remains absent.

## 7. Prioritized remediation roadmap

### P0
1. Fix `AUTH-001` login request contract.
2. Remove raw browser API-key persistence/global injection (`AUTH-002/003`).
3. Implement server-enforced SessionTruth expiry/revocation.
4. Implement `SOL-17 MutationPolicy + CapabilityManifest`; hard-deny live capabilities in analyzer/paper.
5. Replace file-based live approval with revision-bound evidence; ignore legacy approval flags.
6. Establish authoritative SafetyTruth.
7. Establish DeploymentTruth exact source SHA + immutable image digest + final Cloud Run revision.
8. Establish StateTruth/domain-CAS shared-state authority.
9. Make PreTradeRiskService mandatory before any paper mutation.

### P1
1. Add worker ingest idempotency/sequence enforcement.
2. OptionChainTruth null/cache/expiry correction.
3. StreamTruth heartbeat/freshness/ordering.
4. ScannerTruth latest-observation semantics and worker isolation.
5. Durable paper event ledger/reconciliation and after-cost P&L.
6. PredictionTruth/model provenance/calibration.
7. Exact browser accessibility/runtime proof.
8. Retire all active Render-era operational instructions.

### P2
1. Advanced institutional drilldowns, performance optimization, optional operator analytics and non-authoritative convenience features after P0/P1 truth contracts are proven.

## 8. Independent verification counters

Counters require independent reproductions and never advance merely because text was copied forward.

- `AUTH-001 4/20`, `AUTH-002 3/20`, `AUTH-003 3/20`, `AUTH-004 2/20`; remaining `AUTH-*` at least `1/20`.
- `UI-001 18/20`, `UI-005 15/20`, `UI-007 11/20`, `UI-016 12/20`.
- `MUT-001..008 1/20` — new independent mutation-route slice.
- Previously established `CHAIN`, `SCAN`, `WS`, `GCP`, `STATE`, `ML`, `A11Y`, `PAPER`, `RISK`, `READY` counters remain below 20.
- **No finding is `LOCKED-20X`.**

## 9. Product-design track — Security / Capability Control V16

This iteration's product design is the real System3 `Security / Settings` workspace, not an audit-status page. It must show authoritative SessionTruth plus a server-owned mutation capability matrix, with LIVE approval/mutation hard-locked, worker-ingest replay health, policy/runtime revisions, idempotency status, security events and redacted evidence drilldowns. Unknown states render `UNKNOWN/INHIBITED`, never enabled.

Required UI classifications:

- **REQUIRED:** session expiry/revocation, capability matrix, CSRF/idempotency truth, live hard lock, worker replay state, policy/runtime revision, evidence IDs, redacted event timeline.
- **RECOMMENDED:** active device/session list, emergency revoke-all/session epoch rotation, policy diff drilldown, security-event filters/search.
- **OPTIONAL:** operator convenience exports and non-authoritative security analytics after core controls are proven.

## 10. Closure discipline

No finding is CLOSED without exact application revision, exact runtime/deployment revision where applicable, reproducible tests, evidence IDs and independent verification. UI completeness, trade readiness, profitability, broker truth, deployment success and live safety remain unproven unless separately evidenced.

## 11. Next deep slice

Performance/memory/concurrency under market-open load: blocking calls, orphaned timed-out threads, executor saturation, duplicate scanner/chain work, cache ownership, request fan-out, Cloud Run single-instance memory pressure, event-loop stalls, frontend polling amplification and whether load can make stale data appear fresh or suppress safety/observability errors.
