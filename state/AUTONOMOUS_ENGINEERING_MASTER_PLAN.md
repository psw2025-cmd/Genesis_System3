# Genesis System3 — Autonomous Engineering Master Plan

Status: ACTIVE CONTROL PLAN. This file complements `AGENTS.md` and `state/FAILURE_REMEDIATION_CHECKLIST.md`. It does not override machine evidence. `SYSTEM_STATE.md` contains historical/stale material and must not be used as sole production authority until reconciled against current GCP/GitHub evidence.

## 0. Mission
Build a resumable, fail-closed engineering loop where every user-visible/runtime/security failure becomes evidence, root-cause investigation, regression, smallest durable repair, automated verification, production proof where applicable, and recurrence guard. No agent may claim closure from a local/CI-only green result.

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
- [ ] Read `AGENTS.md`, this plan, failure checklist and active P0 issue(s).
- [ ] Read current workflow/artifact evidence.
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
No fix is accepted until initiating cause and downstream blast radius are known.

## 5. UI proof architecture
### Layer A — LOCAL_NON_PRODUCTION
Required: explicit non-production scope/authority fields, localhost/Vite origin, all 22 current tabs, zero credential prompt and zero order/mutation action. PASS never proves Dhan, GCP revision, production data or readiness.

### Layer B — GCP_DEPLOYED_SEMANTIC
Required before production broker/data claim: HTTPS Cloud Run URL; exact expected/deployed SHA and revision; traffic; health/broker status; sanitized token provenance; Overview+Broker+System agreement; WebSocket correlation; visible non-placeholder data; repeated refresh/second session; screenshot+semantic manifest; zero mutations/orders.

## 6. Issue #188 market-data completeness checklist
- [ ] NSE/BSE cash equities where broker-supported.
- [ ] NSE/BSE supported indices.
- [ ] Equity and index derivatives.
- [ ] Instrument/security-ID discovery.
- [ ] Multiple index option chains.
- [ ] Multiple equity option chains.
- [ ] All broker-returned expiries.
- [ ] CE/PE coverage.
- [ ] All returned strikes / ALL STRIKES.
- [ ] LTP/bid/ask/volume/OI/change-OI/IV/Greeks when genuinely supplied/derived and source-labelled.
- [ ] Freshness/stale reason.
- [ ] API↔UI count/value parity.
- [ ] Broker-outage degraded state.
- [ ] Rate-limit/backoff/circuit breaker.
- [ ] WebSocket disconnect/reconnect/resubscribe.

## 7. Dhan reliability checklist
Broker connectivity and rotator reliability remain separate. Track attempts/successes/failures/auth/timeouts/concurrency/crashes/latency/connected duration; prove Scheduler→Job→identity→Secret Manager metadata/version→rotator→runtime→read-only broker→UI; multiple consecutive rotations and connected-duration proof are required.

## 8. Security checklist
- [ ] root/backend pip audit;
- [ ] npm audit;
- [ ] CodeQL Python/JS-TS;
- [ ] Bandit/static security;
- [ ] secret scan;
- [ ] dependency compatibility/lock determinism;
- [ ] architecture/order safety;
- [ ] raw findings retained when exact reviewed shape is declassified;
- [ ] no global suppression/forced major upgrade;
- [ ] declassification tied to scanner finding location, not neighboring context.

Known open security child loops:
- `SEC-001.1`: npm audit 4 vulnerabilities (3 HIGH, 1 MODERATE) on the last inspected completed security artifact; Vite/PostCSS/esbuild/nanoid compatible-lock remediation pending.
- `SEC-001.2`: mixed-snippet Bandit false-green risk found by independent PR review; source and adversarial tests repaired, current exact-head verification pending.

## 9. Automation design checklist
- [ ] reuse authoritative workflows; avoid sprawl;
- [ ] least-privilege/read-only safety CI;
- [ ] deterministic exact-SHA checkout/provenance;
- [ ] bounded retry only for classified transient infrastructure failure;
- [ ] repeated semantic failure = RECURRENCE;
- [ ] safe artifacts uploaded on failure;
- [ ] exact failing step preserved;
- [ ] local/production provenance separated;
- [ ] stale artifact rejected;
- [ ] final enforcement consumes all sub-results;
- [ ] machine-readable PASS/FAIL/BLOCKED + blockers;
- [ ] adversarial tests for the checker itself.

## 10. Automation self-check matrix
Every automation change verifies trigger coverage, cancel/concurrency behavior, permissions, safety flags, timeouts, retry visibility, exact SHA in evidence, artifact retention, no hidden `continue-on-error` green, final enforcement, stale-evidence rejection, proof provenance, downstream dependency ordering, manual-dispatch invariants and no write-back/deploy from read-only safety workflow.

## 11. Universal recursive failure micro-loop
1. Freeze evidence.
2. Assign atomic ID; classify NEW/RECURRENCE.
3. Reproduce exact smallest failure.
4. Trace upstream/downstream dependencies.
5. Research source + machine evidence + authoritative upstream docs where relevant.
6. Compare/falsify remediation alternatives.
7. Add failing + adversarial regression.
8. Implement smallest durable repair.
9. Run focused→adjacent→full smoke/security/safety→artifact review→production proof where relevant.
10. Checkpoint. Any failed item creates another child 10-step loop.

## 12. Smoke-test ladder
- [ ] syntax/compile/import;
- [ ] unit regression;
- [ ] adversarial regression;
- [ ] adjacent integration;
- [ ] backend/API contract;
- [ ] frontend build;
- [ ] local 22-tab browser smoke;
- [ ] security/safety gates;
- [ ] exact-head mandatory workflows;
- [ ] merge eligibility;
- [ ] exact-main deploy;
- [ ] Cloud Run provenance/health;
- [ ] Dhan scheduler/rotator/read-only broker proof;
- [ ] deployed 22-tab semantic UI;
- [ ] equity/index/options completeness;
- [ ] reconnect/degraded/rate-limit tests;
- [ ] recurrence-free market-session observation.

## 13. Documentation update checklist
Before marking current state complete: source checked; exact workflow/artifact checked; GCP checked for production; UI checked for user-visible claims; SHA/revision/timestamp recorded; stale historical claims marked; status only `PROVEN|FAILED|BLOCKED|IN_PROGRESS|STALE|UNKNOWN`.

## 14. Current cross-verification snapshot — 2026-08-15
- [x] PR #219 remains OPEN and mergeable; base remains `bcce7fb149eba5860989df56b7c98b50b5ff54be` at the last metadata check.
- [x] PR changed-file scope is 10 files: governance, proof harnesses, security summarizer/tests, and Playwright truth gate; no order/trading runtime file is in the changed-file list.
- [x] All three independent PR review threads are now resolved after fixes: Option Chain discovery race, governance marker mismatch, and Bandit neighboring-snippet false-green risk.
- [x] Governance architecture gate previously failed on its own detector mismatch and then passed after correction, proving the child-loop/self-check behavior.
- [x] Latest completed local Frontend Browser Runtime Smoke before this documentation checkpoint passed all canonical tab rendering and artifact upload; by contract it remains non-production.
- [x] SonarQube workflow passed on the latest inspected generation before this documentation checkpoint.
- [x] Bandit declassifier now maps the exact scanner `line_number` and requires equality to the reviewed static command; mixed safe+unsafe B602/B605 and ambiguous multiline adversarial tests are present.
- [ ] Current exact-head workflow set after the latest QC/documentation commits must complete; documentation commits themselves are not exempt from re-verification.
- [ ] npm audit remains the known genuine security blocker until a fresh exact-head artifact proves otherwise.
- [ ] Production Dhan connected from deployed GCP UI is NOT PROVEN by a current exact-main Layer-B proof.
- [ ] Issue #188 remains OPEN.
- [ ] `SYSTEM_STATE.md` remains STALE for current production authority and still contains June/Render/manual-token material.

## 15. Closure
Only `CODE -> TEST -> SECURITY -> MERGE -> EXACT MAIN DEPLOY -> RUNTIME -> BROKER -> DATA -> 22-TAB PRODUCTION UI -> STABILITY -> CROSS-VERIFY -> DOCUMENT` may become `CLOSED — PROVEN`.
