# Genesis System3 — Autonomous Engineering Master Plan

Status: ACTIVE CONTROL PLAN. This file complements `AGENTS.md` and `state/FAILURE_REMEDIATION_CHECKLIST.md`. It does not override machine evidence. `SYSTEM_STATE.md` contains historical/stale material and must not be used as sole production authority until reconciled against current GCP/GitHub evidence.

## 0. Mission
Build a resumable, fail-closed engineering loop where every user-visible/runtime/security failure becomes evidence, a root-cause investigation, a regression, a smallest durable repair, an automated verification, production proof where applicable, and a recurrence guard. No agent may claim closure from a local/CI-only green result.

## 1. Authority ladder
1. Current GCP production runtime/revision/traffic evidence.
2. Exact deployed SHA/image provenance.
3. Current GitHub `main` SHA.
4. Exact PR head SHA under test.
5. Current workflow artifacts/logs bound to that SHA.
6. Repository source/tests.
7. Current control Markdown.
8. Historical Markdown/email/chat.

Any conflict creates `AUTHORITY_CONFLICT` and blocks mutation until explained.

## 2. Mandatory pre-work checklist
- [ ] Record UTC/IST time, repo, branch, main SHA, PR head SHA.
- [ ] Read `AGENTS.md`.
- [ ] Read this plan.
- [ ] Read `state/FAILURE_REMEDIATION_CHECKLIST.md`.
- [ ] Read active P0 issue(s), especially #188 when market-data/UI related.
- [ ] Read relevant current workflow/artifact evidence.
- [ ] Verify LIVE safety flags remain zero/off.
- [ ] For production claims identify Cloud Run URL/revision/image/traffic/`DEPLOY_GIT_SHA`.
- [ ] Create durable checkpoint with work ID before mutation.

## 3. Repository-wide forensic inventory checklist
For a full remediation campaign collect/classify:
- [ ] tracked-file count and language/module inventory;
- [ ] backend entrypoints/routes/services;
- [ ] frontend tabs/components/hooks/API clients/WebSocket paths;
- [ ] broker/Dhan adapters/token/rotator/scheduler/jobs;
- [ ] GCP deployment/runtime/evidence scripts;
- [ ] workflows and mandatory gates;
- [ ] tests and proof harnesses;
- [ ] storage/cache/Firestore/state authorities;
- [ ] hard-coded symbol/security-id/expiry/strike lists;
- [ ] TODO/FIXME/NotImplemented/placeholder/demo/mock/synthetic markers;
- [ ] stale Render/localhost assumptions;
- [ ] silent exceptions/fallbacks/timeouts/retries;
- [ ] secret/logging and order/mutation surfaces;
- [ ] duplicate/dead/historical implementations.
Each match is classified `ACTIVE|TEST|HISTORICAL|GENERATED|FALSE_POSITIVE|DEFECT|SECURITY|DEAD_CODE` before action.

## 4. Runtime dependency graph checklist
For every affected UI feature map:
`tab -> component -> state/hook -> HTTP/WS -> route -> service -> cache/storage -> broker/provider -> parser -> response -> renderer`.
For automated data paths also map:
`Scheduler -> Cloud Run Job -> service account -> Secret Manager metadata/version -> token rotator -> broker auth -> runtime refresh -> UI/API`.
No fix is accepted until the initiating cause and downstream blast radius are known.

## 5. UI proof architecture
### Layer A — LOCAL_NON_PRODUCTION
Purpose: build/mount/navigation/render regression only.
Required manifest fields:
- [ ] `proof_scope=LOCAL_NON_PRODUCTION`;
- [ ] `production_authority=false`;
- [ ] `broker_connectivity_proven=false`;
- [ ] `production_claim_allowed=false`;
- [ ] localhost/Vite preview source recorded;
- [ ] 22 current sidebar tabs exercised;
- [ ] zero credential prompt;
- [ ] zero trading mutation/order action.
A PASS here never proves Dhan, market data, GCP revision, production UI, or production readiness.

### Layer B — GCP_DEPLOYED_SEMANTIC
Required before any production UI/broker claim:
- [ ] HTTPS Cloud Run URL derived from GCP;
- [ ] expected SHA recorded;
- [ ] serving revision/image/traffic recorded;
- [ ] `DEPLOY_GIT_SHA == expected current main`;
- [ ] `/api/health` current and lightweight;
- [ ] `/api/broker/status` current, sanitized and latency recorded;
- [ ] Overview, Broker and System tabs agree on Dhan state in same proof window;
- [ ] WebSocket state visible/correlated;
- [ ] visible non-placeholder market rows;
- [ ] second refresh/session repeats the result;
- [ ] screenshots + semantic JSON manifest;
- [ ] zero credentials/mutations/order calls.

## 6. Issue #188 market-data completeness checklist
For broker-supported legal/API universe prove expected/backend/UI/missing counts plus source/freshness/latency:
- [ ] NSE cash equities;
- [ ] BSE cash equities;
- [ ] NSE indices;
- [ ] BSE indices where supported;
- [ ] equity derivatives;
- [ ] index derivatives;
- [ ] instrument/security-ID discovery;
- [ ] multiple index option chains;
- [ ] multiple equity option chains;
- [ ] all broker-returned expiries;
- [ ] CE and PE coverage;
- [ ] all returned strikes / ALL STRIKES default;
- [ ] bid/ask/LTP/volume/OI/change-OI/IV/Greeks when genuinely provided/derived and source-labelled;
- [ ] quote freshness and stale reason;
- [ ] candle/chart continuity where supported;
- [ ] API↔UI count/value parity;
- [ ] broker outage degraded state, no blank/hang;
- [ ] rate-limit/backoff/circuit breaker;
- [ ] WebSocket disconnect/reconnect/resubscribe expected coverage.

## 7. Dhan reliability checklist
Treat broker connectivity and rotator reliability separately.
- [ ] recent rotation attempts count;
- [ ] success/failure ratio;
- [ ] auth error count;
- [ ] timeout count;
- [ ] concurrency/version-conflict count;
- [ ] crash/exit-code count;
- [ ] scheduler enabled/timezone/identity;
- [ ] job execution identity;
- [ ] Secret Manager version metadata only, never payload;
- [ ] expected-version/concurrency protection;
- [ ] runtime observes winning/latest valid version;
- [ ] broker read-only call succeeds;
- [ ] connected duration measured;
- [ ] repeated consecutive rotations succeed;
- [ ] UI and API remain connected through rotations.
One success never closes reliability.

## 8. Security checklist
- [ ] pip root audit;
- [ ] pip backend audit;
- [ ] npm audit;
- [ ] CodeQL Python/JS-TS;
- [ ] Bandit/static security;
- [ ] secret scan;
- [ ] dependency compatibility/lock determinism;
- [ ] architecture/order safety;
- [ ] raw findings retained even when exact reviewed shape is declassified;
- [ ] no global suppression;
- [ ] no forced incompatible dependency upgrade.
Current known child loop: npm audit remains 4 vulnerabilities (3 HIGH, 1 MODERATE) on run #53; direct/transitive Vite/PostCSS/esbuild/nanoid path remains open until lock-compatible patched versions are proven.

## 9. Automation design checklist
Automation must itself be tested.
- [ ] authoritative existing workflows reused; avoid workflow sprawl;
- [ ] read-only permissions for CI gates;
- [ ] GitHub-hosted runners for global safety;
- [ ] deterministic exact-SHA checkout/provenance;
- [ ] bounded retry only for classified transient infrastructure failure;
- [ ] second identical failure becomes RECURRENCE;
- [ ] artifacts uploaded even on fail when safe;
- [ ] failure reason/step preserved;
- [ ] local proof labeled non-production;
- [ ] production proof waits for exact serving SHA;
- [ ] security and safety remain fail-closed;
- [ ] no auto-live/order authority;
- [ ] no secret payload access;
- [ ] no stale artifact accepted as current;
- [ ] automation produces machine-readable PASS/FAIL/BLOCKED plus blocker list;
- [ ] automation contract has adversarial regression tests.

## 10. Automation self-check matrix
Every change affecting automation must verify:
- [ ] trigger coverage appropriate for changed paths;
- [ ] concurrency/cancel behavior cannot hide required final proof;
- [ ] permissions least-privilege;
- [ ] environment safety flags explicit;
- [ ] timeouts bounded;
- [ ] retry count bounded and visible;
- [ ] exact SHA included in artifact/report;
- [ ] artifact retention adequate;
- [ ] failure step cannot be skipped by `continue-on-error` without final enforcement;
- [ ] final enforcement consumes all sub-results;
- [ ] stale evidence rejected;
- [ ] local-vs-production provenance distinct;
- [ ] downstream workflow only starts after valid upstream condition;
- [ ] manual dispatch cannot bypass required invariants;
- [ ] no write-back/deploy in read-only safety workflow.

## 11. Universal recursive failure micro-loop
For EVERY failed checklist item:
1. Freeze evidence.
2. Assign atomic ID and classify NEW/RECURRENCE.
3. Reproduce exact smallest failure.
4. Trace every upstream/downstream dependency.
5. Research source, machine logs/artifacts, and authoritative upstream docs when tool/dependency-related.
6. Form at least two plausible remediation paths when material and falsify the weaker one.
7. Create failing regression plus adversarial/negative case.
8. Implement smallest durable repair with rollback boundary.
9. Run focused -> adjacent -> full smoke/security/safety -> exact artifact review -> production proof when relevant.
10. Checkpoint. Any failed item creates a new child 10-step loop before another retry.

## 12. Smoke-test ladder
A change cannot jump directly to production closure.
- [ ] syntax/compile/import;
- [ ] unit regression;
- [ ] adversarial regression;
- [ ] adjacent integration;
- [ ] backend/API contract;
- [ ] frontend strict/build;
- [ ] local 22-tab browser smoke;
- [ ] security/safety gates;
- [ ] exact-head mandatory workflow set;
- [ ] merge eligibility;
- [ ] exact-main deploy;
- [ ] Cloud Run provenance/health;
- [ ] Dhan scheduler/rotator/read-only broker proof;
- [ ] deployed 22-tab semantic UI;
- [ ] equity/index/options completeness;
- [ ] reconnect/degraded/rate-limit tests;
- [ ] recurrence-free market-session observation.

## 13. Documentation update checklist
Before marking any checkbox complete in current-state docs:
- [ ] source evidence checked;
- [ ] workflow/artifact evidence checked;
- [ ] GCP runtime checked if production-related;
- [ ] production UI checked if user-visible;
- [ ] SHA/revision/timestamp recorded;
- [ ] stale/contradictory historical statement explicitly marked stale rather than silently reused;
- [ ] result status is one of `PROVEN|FAILED|BLOCKED|IN_PROGRESS|STALE|UNKNOWN`.

## 14. Current cross-verification snapshot — 2026-08-15
- [x] PR #219 local browser proof expanded to 22 tabs.
- [x] Local browser proof explicitly separated from production authority.
- [x] Global Safety #1613 PASS on head `d9c38ec...`.
- [x] Frontend Browser Runtime Smoke #166 PASS on head `d9c38ec...`.
- [x] CodeQL #53 PASS on head `d9c38ec...`.
- [x] SonarQube Audit #53 workflow SUCCESS on head `d9c38ec...` (workflow success is not a substitute for external Sonar configuration/quality proof if scans are skipped/blocked).
- [ ] Security Audit Evidence #53 FAIL: exact hard blocker `npm_audit`; 4 vulnerabilities = 3 HIGH + 1 MODERATE. Artifact `security-audit-53`, ID `9243029535`, digest `sha256:df12d214bb7442dcf3762735d0b61858476789fd949903fdc8f592f17521d6b0`.
- [ ] Production Dhan connected from deployed GCP UI NOT YET PROVEN by a current exact-main Layer-B proof.
- [ ] Issue #188 remains OPEN.
- [ ] `SYSTEM_STATE.md` is stale and contains June/Render/manual-token instructions; do not use it as sole current authority.

## 15. Closure
Only `CODE -> TEST -> SECURITY -> MERGE -> EXACT MAIN DEPLOY -> RUNTIME -> BROKER -> DATA -> 22-TAB PRODUCTION UI -> STABILITY -> CROSS-VERIFY -> DOCUMENT` may become `CLOSED — PROVEN`.
