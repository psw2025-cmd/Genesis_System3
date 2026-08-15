# Genesis System3 — Universal Agent Operating Contract

> Mandatory for every human or automated agent operating from GitHub Actions, GCP/Cloud Run/Scheduler, a local laptop, browser automation, broker integration, IDE/CLI, or any future environment. Read `state/AUTONOMOUS_ENGINEERING_MASTER_PLAN.md`, `state/FAILURE_REMEDIATION_CHECKLIST.md`, `CHANGE_LOG.md`, active P0 issue(s), and then `SYSTEM_STATE.md` as historical/contextual input only until its claims are cross-verified against current machine evidence.

## A. Authority
- Work only in `psw2025-cmd/Genesis_System3` unless owner explicitly changes scope.
- GCP is production/deployment authority; Render is legacy/non-authoritative.
- `SYSTEM_STATE.md` is not allowed to override newer GitHub/GCP/runtime/UI evidence and currently contains stale June/Render-era material.
- Never infer production state from localhost, Vite preview, unit tests, CI screenshots, historical reports, email, or prose.
- Production claims require exact GCP service/revision/image/SHA/traffic plus current production API/UI evidence.

## B. DO-NOT-ACT safety list
Agents MUST NOT do these merely to make a check green:
- Enable LIVE trading or `LIVE_TRADING_ENABLED`, `SYSTEM3_LIVE_TRADING_ALLOWED`, `AUTO_EXECUTE_TRADES`.
- Place/modify/cancel real orders or call mutation/order endpoints for proof.
- Manually rotate/replace Dhan tokens/secrets without proven root cause and authorized rotation path.
- Expose token/PIN/TOTP/API key/private key/secret payload in logs/screenshots/issues/PRs/artifacts/Markdown/chat/email.
- Blindly restart/redeploy Cloud Run when cause is unknown.
- Disable/weaken security/safety/provenance/branch protection/semantic UI checks.
- Globally suppress findings or use retry-until-green.
- Run uncontrolled `npm audit fix --force`/major upgrades without compatibility proof.
- Close P0 from one API call, screenshot, workflow, broker response, or token rotation.
- Treat `LOCAL_NON_PRODUCTION` proof as production broker/data proof.
- Overwrite historical evidence; checkpoint/append and preserve provenance.

## C. Mandatory bootstrap before mutation
1. Resolve repo, branch, current `main` SHA, PR head SHA, UTC/IST time.
2. Read this file + current master plan + failure checklist + `CHANGE_LOG.md` + active P0; read `SYSTEM_STATE.md` only as contextual history until cross-verified.
3. Resolve mandatory workflows and exact artifacts.
4. For production work resolve Cloud Run service, serving revision, image, `DEPLOY_GIT_SHA`, traffic and HTTPS URL.
5. Confirm analyzer/LIVE safety flags before and after work.
6. Create a durable checkpoint before mutation.
If sources conflict: `AUTHORITY_CONFLICT`; stop mutation, preserve evidence, investigate.

## D. Full dependency-path rule
Before fixing user-visible defects map:
`UI tab -> component -> hook/service -> HTTP/WS -> API route -> service -> cache/storage -> broker/provider -> response -> renderer`.
Add scheduler/job/Secret Manager/revision dependencies where applicable.

## E. Recursive 10-step failure loop — EVERY failure
1. Freeze exact evidence: timestamp/SHA/revision/run/job/step/log/artifact/safety flags.
2. Classify NEW vs RECURRENCE; runtime/product vs CI/proof-runner vs dependency/security vs documentation.
3. Reproduce on exact SHA/revision with smallest failing input; reject stale evidence.
4. Map blast radius across files/functions/APIs/jobs/workflows/UI/security/safety.
5. Research root cause from source + machine evidence + authoritative upstream docs; compare alternatives where material.
6. Add/reproduce failing regression and negative/adversarial case where practical.
7. Implement smallest durable fix; preserve observability/provenance; no blind retry/suppression.
8. Run focused + adjacent integration + compile/build + security/safety + mandatory CI; inspect exact artifacts.
9. For production relevance require exact-main deployment + runtime/API/broker/scheduler + semantic production UI proof.
10. Checkpoint result/recurrence. Any failed step recursively creates another ten-step child loop.
No depth limit for convenience; stop only when causal chain is proven and mandatory gates pass.

## F. Agent/tool failure handling
Preserve partial evidence and last successful atomic unit; record `AGENT_EXECUTION_FAILED`; classify infrastructure/permission/rate-limit/data/code/unknown; retry only failed unit after stating hypothesis/expected result; use independent verification when possible; resume from checkpoint, never memory.

## G. Two-layer UI truth
**Layer A local CI:** must declare `proof_scope=LOCAL_NON_PRODUCTION`, `production_authority=false`, `broker_connectivity_proven=false`, `production_claim_allowed=false`. It proves build/mount/navigation/22-tab rendering only.

**Layer B deployed GCP:** HTTPS Cloud Run URL + expected exact SHA/revision. In one proof window Overview + Broker + System must agree on Dhan; correlate `/api/health` + `/api/broker/status`; prove WebSocket + visible non-placeholder market data; sanitized provenance only.

Production broker-connected claims are forbidden unless Layer B passes. Layer A never substitutes.

## H. Market-data/UI completeness
Production closure requires visible broker-supported NSE/BSE equities/indices, index/equity derivatives, CE/PE, multiple index/equity option chains, available expiries/contracts/strikes, ALL STRIKES, freshness/source/error truth and API↔UI parity. Zero/missing counts fail unless independently proven legitimate. All current Sidebar tabs must be semantically exercised; tab changes must update browser contract in the same change.

## I. Broker/Dhan reliability
Broker health and token-rotation reliability are separate. Track attempts/successes/failures/auth/timeouts/concurrency/crashes/latency/connected duration. Never call Dhan fixed from one response. Prove Scheduler -> Job -> Secret Manager -> runtime -> broker as one chain. Secrets stay redacted.

## J. Deployment/provenance
`PR head -> mandatory gates -> merge -> current main -> deploy exact SHA -> Cloud Run revision/image -> intended traffic -> DEPLOY_GIT_SHA == main -> health -> broker -> scheduler/jobs -> production UI -> recurrence window -> documentation`.
Any broken arrow means OPEN/FAILED/BLOCKED.

## K. Anti-false-green
Fail closed for missing tab coverage, blank/loading/placeholder UI, credential prompt, required API failure, missing universe/equity options/expiries/contracts/strikes, UI/API mismatch, stale evidence, SHA mismatch, unavailable broker proof, secret exposure, live-order authority, or production proof sourced from localhost.

## L. Security
CodeQL, dependency audit, Bandit/static security, secret scanning and architecture safety are fail-closed. Declassification requires exact-code-shape review + regression tests; raw findings remain visible. Never globally suppress a detector to get green.

## M. Checkpoint/documentation
`state/AUTONOMOUS_ENGINEERING_MASTER_PLAN.md` is the current execution/checklist contract; `SYSTEM_STATE.md` becomes current factual state only after machine cross-verification; `CHANGE_LOG.md` is chronology; `state/FAILURE_REMEDIATION_CHECKLIST.md` is recursive work ledger. Checkpoint after inventory, dependency map, each defect, implementation, test group, workflow result, deployment and production verification. Minimum: `timestamp | SHA | branch | work_id | status | evidence | finding | next_action`.

## N. User-action escalation
Default autonomous read-only investigation and safe repo/test remediation. Ask owner only for genuinely non-automatable account-owner action such as interactive broker consent, owner-only permission or billing/account verification. State exact action/reason. Never ask owner to restart/rotate/redeploy as diagnostic shortcut.

## O. Definition of done
`CODE -> TEST -> SECURITY -> MERGE -> EXACT-MAIN DEPLOY -> RUNTIME -> BROKER -> DATA -> 22-TAB SEMANTIC UI -> OBSERVATION -> CROSS-VERIFY -> DOCUMENT`.
Only then: `CLOSED — PROVEN`.
