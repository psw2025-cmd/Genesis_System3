# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 19:27 IST`

> This revision supersedes older status text in this file. Historical evidence is retained below only where it remains relevant. `PATCHED` never means `CLOSED`.

## 0. Scope, source revision and safety lock

- Repository authority: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Current application/source HEAD after this run: `1d7e06a0f661a873528d96bcc685dc7b0af87f58` (merge of PR #102).
- Prior application milestones in this cascade:
  - PR #100 browser reusable-key removal -> merge `e655330559a6d85b42c5cc951308827f6718f41f`.
  - PR #101 server SessionTruth authority -> merge `5ea9b12e3358876ae900fc07c584b349ef8c2254`.
  - PR #102 Mutation CapabilityManifest -> merge `1d7e06a0f661a873528d96bcc685dc7b0af87f58`.
- Google Cloud is the only accepted deployment target. Render-era runtime instructions/tools are non-authoritative migration debt.
- Runtime posture: ANALYZER/PAPER. LIVE remains OFF/LOCKED. No live order was enabled, placed, modified, cancelled or routed in this run.
- Exact merge-commit deployment/runtime proof is still NOT PROVEN. PR-head CI is evidence for the tested PR head only.

## 1. Smart-cascade step position

Current 1-18 flow state:

`1 VERIFY -> 2 SELECT -> 3 ROOT CAUSE -> 4 DESIGN -> 5 PATCH -> 6 TEST -> 7 PR -> 8 CI -> 9 FIX/RETEST -> 10 MERGE -> 11 POST-MERGE VERIFY -> 12 PREP/CONTINUE -> 13 USER GCP ONLY IF REQUIRED -> 14 DEPLOY VERIFY -> 15 RUNTIME TEST -> 16 USER DHAN AUTH ONLY IF REQUIRED -> 17 FULL EVIDENCE -> 18 CLOSED`

This run completed a full source/CI/merge loop for P0-1 SessionTruth and then immediately completed a source/CI/merge loop for the first P0-2 CapabilityManifest slice. The cascade now continues inside **P0-2 runtime enforcement**; user action is **NOT REQUIRED**.

## 2. Executive verdict

| Area | Current verdict | Implementation state |
|---|---|---|
| SessionTruth/Auth | **PARTIAL VERIFIED / RUNTIME UNPROVEN** | PR #100 + #101 merged; browser secret replay removed; opaque expiring/revocable server sessions added |
| MutationPolicy | **PARTIAL PATCH / CI VERIFIED** | PR #102 merged; every current write route classified with zero UNKNOWN in CI; runtime capability enforcement still required |
| SafetyTruth / execution eligibility | **FAIL / P0** | READY TO PATCH after P0-2 enforcement |
| PreTradeRiskService | **FAIL / P0** | READY TO PATCH |
| AccountTruth | **FAIL / P0-P1** | READY TO PATCH |
| PaperLedger/Reconciliation | **PARTIAL PATCH / FAIL P0** | PR #99 fixed one dual-authority defect; durable event ledger/reconciliation still required |
| StateTruth / Firestore | **FAIL / P0-P1** | READY TO PATCH |
| DeploymentTruth / GCP | **FAIL / NOT PROVEN** | READY TO PATCH |
| WorkCoordinator/idempotency | **FAIL / P0-P1** | READY TO PATCH |
| OptionChainTruth | **FAIL / P0-P1** | READY TO PATCH |
| StreamTruth | **FAIL / P0-P1** | READY TO PATCH |
| ScannerTruth | **FAIL / P0-P1** | READY TO PATCH |
| PredictionTruth/ML | **MISSING / P0-P1** | READY TO PATCH/DESIGN |
| Institutional UI/A11Y | **FAIL / P1** | READY TO PATCH |
| Real-money readiness | **NO** | LIVE stays OFF/LOCKED |

## 3. P0-1 SessionTruth/Auth — current authoritative status

### Resolved source defects

**AUTH browser reusable-secret exposure — PATCHED/CI VERIFIED.** PR #100 removed `sessionStorage` persistence of the reusable dashboard API key and removed global `X-API-Key` replay interceptors. Browser login now exchanges the key once for a cookie session.

**AUTH deterministic cookie / browser-only expiry / no server revocation — PATCHED/CI VERIFIED at source level.** PR #101 added `dashboard/backend/session_truth.py` and `dashboard/backend/secure_app.py` and changed the GCP launcher to `dashboard.backend.secure_app:app`.

World-class behavior now implemented in source:
- cryptographically random opaque session token via `secrets.token_urlsafe(32)`;
- only SHA-256 token hash stored server-side;
- authoritative server `issued_at`, `expires_at`, `revoked_at`;
- revoked session tombstone retained until natural expiry;
- server-side logout revocation;
- HttpOnly/SameSite cookie; Secure derives from Cloud Run forwarded HTTPS scheme;
- login throttling: 10 failures/5 min per client;
- logout Origin validation when a cookie is present;
- process restart invalidates sessions fail-closed;
- trusted `X-API-Key` compatibility retained for CI/API probes, not browser persistence.

Exact PR #101 final head: `05099d1122853e26332c84dcac6cd623a7cf1f3a`.
CI evidence on that exact head:
- `Genesis System3 Global Safety CI` run `31498213627`: **SUCCESS**; all 5 blocking jobs SUCCESS, including backend pytest/proof pack, frontend build, Python compile, workflow/trading-safety guard and architecture/trading-safety gate.
- `GCP Stage 2 Safety Checks` run `31498213658`: **SUCCESS**.
- `GCP Dhan Token Fix CI` run `31498213607`: **SUCCESS**.
- Merge: PR #101 -> `5ea9b12e3358876ae900fc07c584b349ef8c2254`.

### Remaining SessionTruth closure gap

**RUNTIME UNPROVEN.** Exact deployed Cloud Run cookie attributes, login/expiry/revocation behavior and serving revision have not yet been proven against the merge revision. The SessionTruth store is intentionally process-local and therefore requires the intended single-instance/single-worker Cloud Run constraint until shared state exists. Multi-instance deployment before shared session authority is prohibited.

**Closure tests still required:** HTTPS Set-Cookie attributes; invalid-key throttling; successful login; expiry; logout/revocation; replay after logout rejected; process restart invalidation; cross-origin logout rejected; exact serving revision/digest proof. Until those pass: status is `PATCHED / PR-CI VERIFIED / RUNTIME UNPROVEN`, not CLOSED.

## 4. P0-2 MutationPolicy + CapabilityManifest

### CapabilityManifest slice — PATCHED/CI VERIFIED

PR #102 introduced `dashboard/backend/mutation_policy.py` with canonical capabilities:
`SESSION_CREATE`, `SESSION_REVOKE_SELF`, `WORKER_INGEST`, `PAPER_MUTATION`, `RISK_POLICY_WRITE`, `SAFETY_CONTROL`, `SCHEDULER_CONTROL`, `PREFERENCE_WRITE`, `ANALYZER_COMMAND`, `LIVE_APPROVAL`, `LIVE_MUTATION`, `UNKNOWN`.

The manifest is generated from the actual FastAPI route table, not a manually counted list. CI requires:
1. every POST/PUT/PATCH/DELETE route has a non-UNKNOWN capability;
2. duplicate `(method,path)` write owners = 0;
3. live order paths classify only as `LIVE_MUTATION`;
4. paper close remains `PAPER_MUTATION`, never live mutation.

Exact PR #102 head: `c9c20fecd5b9ebfa92af33eaa017f53191c63944`.
CI evidence on that head:
- `Genesis System3 Global Safety CI` run `31498678214`: **SUCCESS**, all 5 blocking jobs SUCCESS including backend pytest/proof pack.
- `GCP Stage 2 Safety Checks` run `31498678244`: **SUCCESS**.
- `GCP Dhan Token Fix CI` run `31498678234`: **SUCCESS**.
- Merge: PR #102 -> `1d7e06a0f661a873528d96bcc685dc7b0af87f58`.

### Remaining P0-2 root cause

Classification is not yet the complete runtime authority. The next patch must install capability-aware middleware/enforcement in the secure app so:
- `UNKNOWN` is denied at runtime and CI;
- `LIVE_MUTATION` remains independently hard denied in analyzer/paper regardless of UI labels;
- `LIVE_APPROVAL` cannot silently become router authority;
- `PAPER_MUTATION` receives explicit authentication, CSRF and idempotency policy;
- `WORKER_INGEST` remains bound to worker identity/token and replay evidence;
- risk/safety/scheduler/preference/analyzer writes each receive exact auth/replay/audit requirements;
- response/audit evidence records capability + request/evidence ID without secrets.

**Status:** `PARTIAL PATCH / CI VERIFIED / READY TO PATCH RUNTIME ENFORCEMENT`.

## 5. P0-3 SafetyTruth + P0-4 PreTradeRiskService

**Severity/status:** P0 / FIX-REQUIRED.

Root cause: kill-switch/mode/risk truth remains split; current transaction paths are not yet proven to require one immutable fail-closed `ExecutionDecision` derived from current safety, account and market truth.

Target chain:
`Intent -> MutationPolicy -> SafetyTruth -> DeploymentTruth -> StateTruth -> Stream/OptionChain/AccountTruth -> PreTradeRiskService -> ExecutionDecision -> serialized PaperMutationWorker`.

`ExecutionDecision {decision_id,intent_id,state:PASS|FAIL|UNKNOWN|ERROR,safety_revision,risk_policy_revision,account_snapshot_id,market_snapshot_ids,expires_at,evidence_ids[]}`.

PASS requires UNKNOWN/STALE/ERROR to inhibit; UI can never override; scheduler cannot bypass; every paper/live-adjacent mutation needs a current decision. LIVE router remains independently locked.

## 6. P0-5 AccountTruth

`ACCOUNT-001..008` remain FIX-REQUIRED.

Retained root causes:
- Dhan positions/holdings can conflate transport success with semantic broker success;
- malformed/missing account numbers can normalize to zero;
- empty/zero can be certified too easily after upstream semantic loss;
- profile connectivity is visually too close to account correctness;
- funds/holdings/positions lack one generation, source event time, receive time, TTL and evidence ID;
- browser can reconstruct financial zeros/P&L;
- duplicate disabled broker router contains weaker zero/empty-on-error behavior;
- AccountTruth not yet mandatory in PreTradeRiskService.

Canonical solution: `BrokerReadResult<T>` + `AccountSnapshotCoordinator` + `AccountTruth`, with `PASS|EMPTY_PROVEN|STALE|AUTH_ERROR|RATE_LIMITED|ERROR|UNKNOWN`. Error/unknown can never become zero exposure. `account_snapshot_id` becomes mandatory risk evidence.

## 7. P0-6 Paper lifecycle / reconciliation

PR #99 merge `6a8f728d58d00cc91381306f8535225b2819777a` remains a partial bridge:
- PAPER-017 direct route-level `positions_live.json` mutation: PATCHED/static verified/runtime unproven.
- PAPER-018 manual-close vs same-engine authority/race: PATCHED/PARTIAL/static verified/runtime unproven.
- PERF-004: engine lock reduces simultaneous mutation but duplicate `/api/paper/tick` requests can still execute sequentially without command idempotency.

Still OPEN: persistence failure semantics, destructive day rollover/repeatable IDs, explicit order/fill lifecycle, versioned cost/P&L provenance, quantity/instrument provenance and authoritative reconciliation identity.

Target: append-only `PaperCommand -> PaperOrderEvent -> PaperFill -> PositionEvent -> CostBreakdown -> ReconciliationTruth`, global immutable IDs/correlation IDs, one serialized/idempotent mutation worker, projections rebuilt from ledger, DRIFT/ERROR never PASS.

## 8. P0-7 StateTruth / P0-8 DeploymentTruth / P0-9 WorkCoordinator

### StateTruth
Shared GCP state must become authority with domain revisions/CAS, writer/runtime/event IDs and fail-closed degradation. Local JSON/files are projections only.

### DeploymentTruth
Retained GCP blockers:
- GCP-012: image tag is not immutable digest proof;
- GCP-013: web runtime/rotator/scheduler identity separation insufficient;
- GCP-014: long-lived `GCP_SA_KEY` fallback remains migration debt;
- GCP-015: desired Cloud Run spec is split across conflicting deployment mutations;
- GCP-016: ordinary app deployment mutates IAM/scheduler topology;
- GCP-017: ordinary app deployment can execute Dhan token rotation;
- GCP-018: traffic ownership of exact serving revision not fully proven;
- GCP-019: executable Render-era operational tooling remains.

Target chain:
`source SHA -> Cloud Build ID -> Artifact Registry sha256 digest -> Cloud Run revision -> traffic allocation -> runtime SHA -> IAM/safety evidence -> immutable evidence ID`.

### WorkCoordinator
Bounded domain workers, keyed singleflight, completion-driven polling, queue/event-loop observability, serialized/idempotent paper mutation and rejection of late/stale results remain required.

## 9. P1 data, AI and product UI

- `CHAIN-001..014`: OptionChainTruth; null never becomes zero; expiry/security keyed cache; source/event/receive/age/TTL/evidence; full Greeks provenance.
- `WS-001..011`: StreamTruth; transport-open != fresh market stream; sequence/heartbeat/schema/event time; reject replay/out-of-order.
- `SCAN-001..010`: ScannerTruth; latest observation replaces old high watermark; stale rows evict; rank != eligibility.
- `ML-001..014`: PredictionTruth + ModelArtifactManifest; immutable model/data/features hashes, temporal leakage proof, calibration, outcome linkage to reconciled after-cost paper events.
- `UI-001` remains `LOCKED-20X / FIX-REQUIRED`: no default-green/zero-safe UI. All Tier-0 status badges must consume typed truth contracts. Browser/mobile/keyboard/axe/console proof still required.

## 10. Closure discipline and counters

- `UI-001`: LOCKED-20X / FIX-REQUIRED; repeated reproduction does not mean fixed.
- `PAPER-017`: historical reproduction `1/20`; fix static evidence exists, runtime closure pending.
- `PAPER-018`: historical reproduction `1/20`; partial fix static evidence exists, runtime closure pending.
- `PERF-004`: historical reproduction `2/20`; exactly-once runtime verification remains 0.
- `ACCOUNT-001..008`: remain at prior `1/20` each.
- `GCP-012..019`: remain at prior `1/20` each.
- `PAPER-010 route-absence`: CLOSED/CORRECTED only for the historical false claim that the route did not exist.
- PR #100/#101/#102 green CI does not establish deployment, broker truth, trade-readiness or profitability.

Definitions:
- `OPEN/FIX-REQUIRED`: defect still reproduces/current design incomplete.
- `READY TO PATCH`: root cause/design/tests sufficiently specified.
- `PATCHED`: source changed.
- `PARTIAL`: one failure mode removed; canonical solution incomplete.
- `VERIFIED`: exact-revision required tests/evidence pass.
- `CLOSED`: all finding-specific PASS criteria independently satisfied, including runtime/deployment where applicable.

## 11. Prioritized remediation roadmap

### P0 strict order
1. SessionTruth/Auth — **source PATCHED + PR CI VERIFIED; runtime proof deferred to deployment stage**.
2. MutationPolicy + CapabilityManifest — **manifest PATCHED + CI VERIFIED; runtime enforcement NEXT**.
3. SafetyTruth + ExecutionEligibility.
4. Mandatory PreTradeRiskService.
5. AccountTruth + AccountSnapshotCoordinator.
6. Durable PaperLedger + ReconciliationService.
7. StateTruth + domain CAS.
8. DeploymentTruth V2 / GCP identity and digest chain.
9. WorkCoordinator/idempotency.

### P1
OptionChainTruth -> StreamTruth -> ScannerTruth -> PredictionTruth -> institutional UI/accessibility/observability.

## 12. Product-design track

Current target remains an institutional `Readiness / Proof` + `Security / Settings` experience:
- command header: source SHA, deployment digest/revision, market/session, analyzer/paper state, LIVE LOCKED;
- security panel: session mode, issued/expires state, server revocation evidence, browser secret storage = NO, auth throttling state, CSRF/origin state;
- mutation capability panel: route capability, auth requirement, idempotency requirement, last decision/evidence ID, live mutations visibly HARD DENIED;
- account/market/paper/risk states remain separate typed truths with age/provenance;
- no unproven metric, readiness score, broker state or profitability claim may be shown as PASS.

## 13. Next immediate cascade slice

Continue P0-2 by installing runtime capability enforcement on top of the merged manifest. Prove UNKNOWN and LIVE_MUTATION fail closed, preserve worker-ingest separation, define per-capability authentication/CSRF/idempotency requirements, run exact-head CI, merge only after all blocking jobs pass, then immediately begin P0-3 SafetyTruth.

**USER ACTION REQUIRED: NO.**
