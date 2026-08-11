# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 06:49 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `11cfbbc759248a3e8298be9de4f694f9be6d1567`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..11cfbbc759248a3e8298be9de4f694f9be6d1567` is 11 commits ahead and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`.
- PR #96 remains the newest merged application/UI PR in this evidence set.
- GitHub connector returned no workflow runs and no combined commit statuses for application HEAD `b70af343340a73ed27ca548820d5893c779ab5bd`; exact-revision CI/runtime readiness is **NOT PROVEN**, not failed.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
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

### Option chain/Greeks
- `CHAIN-001/P0` warming/no-data chain can produce `PCR=1` instead of unknown.
- `CHAIN-002/P1` Dhan-looking verification lacks event-time/freshness/schema/normalizer/completeness proof.
- `CHAIN-003/P1` full Delta/Gamma/Theta/Vega not displayed in Option Chain.
- `CHAIN-004/P1` Dhan row -> normalized inputs -> Greeks -> UI provenance not proven end to end.
- `CHAIN-005/P1` IV unit/schema implicit at UI boundary.
- `CHAIN-006/P0-P1` parser converts missing/invalid quote/Greek fields to numeric zero.
- `CHAIN-007/P1` incomplete bid/ask can create artificial zero/negative spread.
- `CHAIN-008/P0-P1` in-memory cache key ignores expiry.
- `CHAIN-009/P0-P1` disk cache lacks age/provider/schema/expiry validation.
- `CHAIN-010/P0-P1` serializer can label fallback data `source:dhan` without source proof.
- `CHAIN-011/P1` generic Monday expiry fallback is not symbol/calendar authoritative.
- `CHAIN-012/P1` parser exceptions collapse into empty chain + zero spot.
- `CHAIN-013/P1` historical schema PASS is narrower than runtime chain truth.
- `CHAIN-014/P2` legacy multi-source fallback residue remains in Dhan-only manager.

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

## 4. New deep slice — Google Cloud deployment provenance, entrypoint and observability

### GCP-001 / P0-P1 — exact application SHA has no connector-visible CI/status proof

**Exact proof:** workflow-run lookup and combined-status lookup for application HEAD `b70af343340a73ed27ca548820d5893c779ab5bd` returned no runs/statuses. The deployment workflow is path-filtered, and later audit-only commits do not change application source.

**Symptom/root cause:** repository configuration can describe a deployment process, but there is no exact-revision evidence in the available GitHub run/status channel proving that this application SHA passed CI and became the current Cloud Run runtime.

**Real-money impact:** UI/runtime safety claims cannot be tied to the source revision being audited. A green dashboard could belong to a different image/revision.

**Files/dependencies:** `.github/workflows/cloud-run-auto-deploy.yml`, `scripts/gcp_cloud_run_auto_deploy.py`, `scripts/gcp_runtime_evidence.py`, Cloud Run service metadata, Artifact Registry image metadata.

**Target behavior:** every deploy emits one immutable `DeploymentTruth` record binding source SHA -> build ID -> image digest -> Cloud Run revision -> runtime service URL -> frontend SHA -> backend SHA -> policy/config hash -> evidence ID.

**Implementation:** add a post-deploy exact-revision gate that reads immutable image digest and the serving Cloud Run revision after all service mutations; compare `DEPLOY_GIT_SHA`, image OCI labels, frontend provenance and runtime endpoint provenance. Store sanitized JSON as workflow artifact and expose read-only subset in Observability UI.

**Tests/PASS:** exact SHA mismatch, digest mismatch, revision superseded, frontend/backend mismatch, missing evidence, stale evidence all fail; PASS only when all identities agree on the same final serving revision.

**Rollback/fail-safe:** deployment may remain running, but readiness becomes `DEPLOYMENT_TRUTH_UNKNOWN` and all real-money readiness remains inhibited.

**Status:** `READY TO PATCH`.

### GCP-002 / P1 — deploy path uses mutable tag identity without proving immutable image digest

**Exact proof:** `scripts/gcp_cloud_run_auto_deploy.py` builds an image tag `${sha[:12]}-${timestamp}` and prints `IMAGE`, `revision`, and `sha`. In the inspected file, it does not resolve, record, or compare the immutable Artifact Registry digest after build/deploy.

**Root cause:** tag + SHA are used as deployment identity even though a digest is the immutable container identity.

**Impact:** tag/revision evidence is insufficient to prove the exact image bytes serving the product.

**Solution:** after Cloud Build success, resolve `IMAGE@sha256:...`; patch Cloud Run by digest or immediately capture the resolved digest; require service `containerStatuses[].imageDigest` / equivalent final metadata to match; include digest in `DeploymentTruth` and UI.

**Regression risks:** Cloud Run v1/v2 metadata field differences and delayed reconciliation.

**Tests:** digest available, digest mismatch, image tag reused, build succeeded but wrong service image, final revision not ready.

**PASS:** one immutable digest agrees across Artifact Registry, Cloud Run final revision and evidence artifact.

**Status:** `READY TO PATCH`.

### GCP-003 / P1 — frontend deploy provenance does not contain the Git source SHA

**Exact proof:** `dashboard/backend/Dockerfile` writes `dist/assets/deploy-provenance.json` containing schema, `sidebar_sha256`, feature booleans and a static/default `SYSTEM3_FRONTEND_BUILD_EPOCH=20260806_gcp_token_rotation_proof`. It does not embed the 40-character source SHA or image digest.

**Impact:** the built browser artifact cannot independently prove it came from the same exact source revision as the backend/runtime.

**Solution:** Cloud Build passes `SYSTEM3_GIT_SHA` and optional build ID as Docker build args; provenance JSON contains full SHA, frontend tree hash, build ID and schema version. Backend `/api/build/provenance` exposes backend SHA/runtime revision/digest; UI compares both and displays `MATCH / MISMATCH / UNKNOWN`.

**Tests:** frontend old/backend new, backend old/frontend new, missing provenance file, malformed SHA.

**PASS:** frontend SHA == backend SHA == `DEPLOY_GIT_SHA` == DeploymentTruth source SHA.

**Status:** `READY TO PATCH`.

### GCP-004 / P1 — workflow performs a second service mutation after deploy script's READY revision

**Exact proof:** `gcp_cloud_run_auto_deploy.py` patches scaling to `minInstanceCount=1,maxInstanceCount=10`, waits for a ready revision and prints `READY`. The subsequent `cloud-run-auto-deploy.yml` step executes `gcloud run services update` with `--min-instances=0 --max-instances=1` plus environment/secret updates, which can create/supersede the revision just printed by the deploy script.

**Impact:** the deploy script's reported `READY revision` is not guaranteed to be the final serving revision used by post-deploy proof. Provenance can split across two revisions.

**Canonical solution:** perform exactly one authoritative Cloud Run service mutation per release, containing image digest, scaling, env and secret references. If a second mutation is unavoidable, discard the first revision identity and collect evidence only after the final mutation and traffic convergence.

**Tests:** assert one final revision after deploy; service traffic 100% to expected revision; expected scaling/env/secret refs on that same revision.

**PASS:** no intermediate revision is reported as authoritative.

**Status:** `READY TO PATCH`.

### GCP-005 / P1 — WIF still has a legacy long-lived service-account-key fallback

**Exact proof:** `cloud-run-auto-deploy.yml` uses keyless WIF when variables exist, but falls back to `secrets.GCP_SA_KEY` when WIF configuration is absent.

**Impact:** long-lived deploy credentials remain a security and provenance risk; an accidental variable regression can silently re-enable key auth.

**Solution:** complete WIF bootstrap, make WIF mandatory, remove `GCP_SA_KEY` fallback and secret, and add workflow guard rejecting `credentials_json` in active deploy workflows.

**Migration:** first prove one WIF-only deployment plus runtime artifact, then delete/disable old key.

**Tests:** missing WIF vars fails closed; no `GCP_SA_KEY`/`credentials_json` in active workflows; principal identity recorded as non-secret metadata.

**Status:** `READY TO PATCH` after one WIF-only proof.

### GCP-006 / P0-P1 — runtime IAM grants Secret Manager access broadly to the service runtime identity

**Exact proof:** deployment workflow grants the Cloud Run runtime service account `roles/secretmanager.secretAccessor` on Dhan client ID, access token, PIN, TOTP, dashboard API key and worker push token; it also grants `secretVersionAdder` on the Dhan token. The same runtime identity is then used for the rotation job when no separate identity is resolved.

**Impact:** the web service identity can inherit credentials needed only by the token rotator, increasing blast radius and violating least privilege.

**Solution:** split identities: `system3-web-runtime` gets only secrets required for web read/runtime; `system3-dhan-rotator` gets PIN/TOTP/client-id/token write permissions; Scheduler uses a dedicated invoker identity; deploy/evidence identities are separate. Never default to the Compute Engine default service account.

**Tests:** IAM policy matrix denies web runtime access to PIN/TOTP and token-version-add; rotator cannot deploy service; scheduler can invoke only rotation job; evidence identity is read-only.

**PASS:** least-privilege matrix independently verified from IAM policy metadata.

**Status:** `READY TO PATCH/DESIGN`.

### GCP-007 / P1 — fallback to default Compute Engine service account is unsafe authority ambiguity

**Exact proof:** if Cloud Run service account is empty, the workflow constructs `${PROJECT_NUMBER}-compute@developer.gserviceaccount.com` and uses it as `RUNTIME_SA` for secret bindings, job service account and Scheduler OAuth identity.

**Impact:** deployments can silently attach broad legacy/default IAM authority instead of failing on missing explicit service-account configuration.

**Solution:** remove fallback. Missing explicit web runtime/rotator/scheduler identities is a deploy blocker.

**Tests/PASS:** empty serviceAccountName -> deployment fails with typed prerequisite error; no default compute SA accepted by deployment-contract tests.

**Status:** `READY TO PATCH`.

### GCP-008 / P1 — runtime evidence safety booleans can still derive truth from missing env values

**Exact proof:** `scripts/gcp_runtime_evidence.py::evaluate_safety()` calculates `live_trading_enabled = not is_off(env.get(...))`; missing values therefore evaluate as enabled/unsafe, which is fail-closed and should be preserved. However `api_key_required` similarly becomes true for any non-off unknown string and the current structure is boolean rather than typed `PROVEN/UNKNOWN/ERROR` with source/revision metadata.

**Impact:** evidence can state boolean outcomes without explaining whether the underlying env field was present, parsed, stale, or from the final serving revision.

**Solution:** replace boolean-only safety summary with typed field observations: `present`, raw normalized enum, source revision, final revision, evidence time, parse state. `PASS` requires explicit allowed value, not merely truthy/non-off evaluation.

**Tests:** absent, malformed, duplicate env name, secret ref/plain value collision, final revision mismatch.

**Status:** `READY TO PATCH`.

### GCP-009 / P1 — frontend build marker can become cosmetic deployment proof

**Exact proof:** Docker build checks for literal UI strings (`Sim Live`, `CLOUD BUILD`, `SESSION SNAPSHOT`, `TOKEN ROTATION PROOF`) and stores booleans in deploy provenance. These prove bundle content exists, not that backend contracts, source revision or runtime revision are compatible.

**Impact:** visible badges/strings may be over-read as deployment completeness.

**Solution:** retain string checks only as smoke tests; never feed them into readiness. Add route/schema contract hash and frontend/backend SHA compatibility proof.

**Status:** `READY TO PATCH`.

### GCP-010 / P1 — observability collector summarizes logs but product lacks an exact-revision incident/drilldown contract

**Exact proof:** `gcp_runtime_evidence.py` already categorizes startup, crash/restart, OOM, Dhan auth, option-chain, Firestore, scheduler/worker and unhandled exceptions and derives HTTP/latency summaries. Current product information architecture has no proven exact-revision evidence timeline binding these events to source SHA + image digest + Cloud Run revision.

**Impact:** operators can see health/performance without knowing whether incidents belong to the exact code revision under review.

**Solution:** introduce `RuntimeEventEnvelope` with `event_id`, observed time, domain, severity, Cloud Run revision, image digest, source SHA, route/request correlation ID, redacted summary and evidence link. Observability screen filters by revision and cannot mix revisions by default.

**Tests:** multi-revision logs, missing revision label, redaction, correlation IDs, 4xx/5xx separation, OOM/restart event classification.

**Status:** `READY TO PATCH/DESIGN`.

### GCP-011 / P1 — deployment target is GCP but Render retirement is enforced only inside active workflow files

**Exact proof:** `workflow_priority_guard.py` rejects `render.com`/`api.render.com` references in active `.github/workflows`, but does not prove the rest of the product UI/docs/runtime code is free from operational Render instructions. Existing `READY-008` already found Render-era instructions in Live Gate.

**Impact:** an operator can follow a stale deployment instruction despite the workflow control plane being GCP-only.

**Solution:** repository-wide production-path Render retirement test over dashboard/runtime/deploy/docs used by UI help, with explicit allow-list only for archived historical reports. Live Gate copy must reference Google Cloud deployment authority only.

**Status:** `READY TO PATCH`; `READY-008` independently reproduced and moves to `2/20`.

## 5. Canonical truth contracts

### 5.1 `SafetyTruth`
`mode`, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 5.2 `DataTruthEnvelope`
`source`, provider session, instrument, source/backend/frontend times, age/TTL, market state, schema/normalizer versions, row count/completeness, quality state, source/runtime revisions.

### 5.3 `StreamTruth`
separate transport/stream/heartbeat state, last event times, uncapped event age, TTL, sequence, rejected-old events, parse errors, source/session/schema, REST fallback and revisions.

### 5.4 `OptionChainTruth`
underlying/security id/segment, requested+resolved expiry and authority, provider/session, source/receive times, age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, quality state, source/runtime revision and evidence ID.

### 5.5 `DeploymentTruth` — NEW

```text
source_sha
source_tree_hash
cloud_build_id
image_repository
image_tag
image_digest
cloud_run_service
cloud_run_revision
traffic_percent
frontend_source_sha
frontend_tree_hash
backend_source_sha
runtime_entrypoint
runtime_app
runtime_service_account
policy_config_hash
secret_reference_versions_metadata_only
scheduler_job
scheduler_target_revision_or_image_digest
deployed_at
verified_at
age_ms
quality_state: PROVEN | DRIFT | STALE | ERROR | UNKNOWN
evidence_id
```

**Invariant:** source tag, UI badge, HTTP 200 or workflow configuration can never substitute for immutable digest + final serving revision + exact source compatibility proof.

### 5.6 `PaperLifecycleTruth`, `GateTruth`, `RiskPolicy`, `PreTradeRiskTruth`
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

### SOL-08 ordered implementation

1. Add `DeploymentTruth` schema and evidence writer.
2. Make WIF mandatory; remove `GCP_SA_KEY` fallback after one WIF-only proof.
3. Split deploy, web-runtime, Dhan-rotator, Scheduler-invoker and read-only-evidence service accounts.
4. Remove default Compute Engine SA fallback.
5. Build image with OCI labels for full git SHA, tree hash and build ID.
6. Resolve immutable Artifact Registry digest after build.
7. Consolidate image/env/secrets/scaling into one authoritative Cloud Run service mutation or collect truth only after the final mutation.
8. Verify 100% serving traffic and latest ready revision against the expected digest.
9. Pass source SHA/build ID into frontend build provenance; expose backend/runtime provenance read-only.
10. Compare frontend SHA == backend SHA == DEPLOY_GIT_SHA == evidence source SHA.
11. Record only secret reference metadata/version identifiers, never secret payloads.
12. Bind Scheduler/rotation job to explicit dedicated identities and expected image digest.
13. Emit sanitized exact-revision runtime evidence artifact and expose read-only subset in Observability.
14. Add repository-wide active production-path guard for Render instructions.
15. Add contract tests for one final serving revision, IAM least privilege, secret refs, live-off flags and provenance drift.

**SOL-08 PASS criteria:** exact application source SHA, frontend SHA, backend SHA, immutable image digest and final serving Cloud Run revision agree; traffic is on that revision; runtime/live-off/auth policy is read from that same revision; identities are explicit/least-privilege; Scheduler/rotator provenance is known; evidence is current; no active Render operational authority remains.

**Rollback/fail-safe:** on any identity/drift/evidence failure, service may stay available for analyzer viewing but `DeploymentTruth=UNKNOWN|DRIFT`, readiness stays blocked and mutation/live routing remains inhibited.

## 7. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `13/20` | OPEN |
| UI-002 | `3/20` | OPEN |
| UI-003 | `6/20` | OPEN |
| UI-005 | `11/20` | OPEN |
| UI-006 | `7/20` | OPEN |
| UI-007 | `7/20` | OPEN |
| UI-009 | `6/20` | OPEN |
| UI-011 | `3/20` | OPEN |
| UI-016 | `7/20` | OPEN — deployment truth separation added |
| UI-018 | `2/20` | OPEN — frontend build-marker vs exact deployment proof independently reproduced |
| CHAIN-001 | `1/20` | OPEN |
| CHAIN-002 | `5/20` | OPEN |
| CHAIN-003 | `1/20` | OPEN |
| CHAIN-004 | `2/20` | OPEN |
| CHAIN-005 | `2/20` | OPEN |
| CHAIN-006..014 | `1/20` each | OPEN |
| READY-001 | `4/20` | OPEN |
| READY-003 | `2/20` | OPEN |
| READY-008 | `2/20` | OPEN — GCP-only workflow guard does not retire Live Gate Render copy |
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
| GCP-001..011 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 8. Prioritized implementation order

### P0 Wave 1 — false-green/fail-open elimination
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline so later fixes can be tied to the serving revision.
4. SOL-05 parser null-safety + expiry-aware/provenance-aware chain cache.
5. SOL-11 StreamTruth, uncapped age and ordered REST/WS merge.
6. SOL-09 server-owned risk + mandatory pre-trade authority.
7. SOL-06 durable lifecycle/idempotency/reconciliation.
8. remove dead/unproven paper mutation control.
9. SOL-04 semantic readiness.
10. SOL-03 remaining zero/live/default-safe fallbacks.
11. SOL-10 legacy mutation UI quarantine.
12. SOL-07 rank-as-percent repair.

### P1 Wave 2 — runtime/account/paper economics
GCP IAM split + WIF-only auth, RuntimeEventEnvelope, full Dhan/account provenance, IV/Greeks model truth, costed fills/P&L, portfolio risk, true WebSocket proof.

### P2 Wave 3 — institutional operator quality
Responsive/mobile, accessibility/keyboard/focus, command palette/search, deep drilldowns, SLO/incidents, security/session settings and audit export.

## 9. Product information architecture target

1. Command Center — Overview + Decision Intel + truth strip.
2. Market / Scanner — watch, scanner, ranker, signals.
3. Options & Greeks — chain, explicit expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + calibration/evidence.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — transport/heartbeat/source/freshness/auth/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, alerts, runtime events, logs, schema/parse errors, latency, reconnects and revision-filtered evidence.
10. Security / Settings — sessions, IAM/policy versions, permissions, audit export, non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 10. Product UI visual evolution — V10

New concept: **Observability & Deployment Truth V10**.

Changes driven by this iteration:
- source SHA, immutable image digest and Cloud Run revision are separate first-class fields;
- frontend and backend build SHA compatibility is visible;
- entrypoint/runtime app identity is visible;
- WIF versus legacy-key state is visible without exposing secrets;
- runtime service account and Scheduler provenance are explicit;
- live/analyzer/auth states remain UNKNOWN until same-revision evidence exists;
- SLO/error panels carry source/evidence rather than generic green badges;
- deployment drift checks compare image/digest/SHA/frontend/backend/route/policy identities;
- incident timeline is revision-filtered and evidence-linked;
- Render-era authority is explicitly rejected;
- live router remains locked.

Visual artifact: `Genesis_System3_Observability_Deployment_Truth_Target_V10.png`.

## 11. Positive foundations to preserve

- Cloud Run is explicitly documented as runtime/scheduler authority in active workflow.
- Active workflow allow-list rejects Render runtime references, self-hosted runners, scheduled GitHub workflows and live-trading enable flags.
- Deployment forces analyzer/live-off flags and mounts dashboard/worker secrets using Secret Manager references.
- Build uses a unique SHA-derived image tag.
- Runtime launcher is explicit: `scripts/start_cloud_run.py` -> `dashboard.backend.app:app`, one Uvicorn worker.
- Runtime evidence collector already sanitizes/redacts logs and captures useful HTTP/latency/error categories.
- Docker image runs as a non-root `appuser` and has a healthcheck.
- Dhan option-chain traffic remains process-serialized and rate paced.
- WS reconnect has backoff+jitter foundation.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness or deployment proof.

## 12. Historical proof/open-gate interpretation

PR descriptions, workflow configuration, build strings and historical PASS artifacts remain scoped evidence only. They cannot prove current runtime truth unless tied to exact source SHA + immutable image digest + final serving Cloud Run revision.

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
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

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; expiry/cache/freshness/order/reconnect tests as applicable; restart/idempotency/reconciliation tests; immutable image digest + final Cloud Run revision/runtime proof where required; analyzer/live-off unchanged; and no contradictory independent evidence.

## 14. Next audit/solution slices

1. DB/state-store consistency: file/JSON/Firestore ownership, locking, atomicity, concurrency, duplicate authorities and restart truth.
2. AI/ML/prediction ledger: calibration, frozen cutoff, model/hash, drift and realized after-cost outcome.
3. Responsive/accessibility: desktop/tablet/mobile, keyboard/focus/live regions/dense tables.
4. Scanner/ranker contracts and performance/memory/concurrency under market-open load.
5. Security/session detail: cookie policy, CSRF, session revocation, command/settings permissions and audit export.

## 15. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser PASS, image tag, UI badge, workflow success description, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval or process-local simulator never substitutes for authoritative source+event time+freshness+schema+ordering+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.
