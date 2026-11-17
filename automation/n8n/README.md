# n8n Evidence Loop — Legacy Genesis System3

## Scope and deployment state
This is an **inactive, importable n8n workflow template**, not an installed or running n8n instance. It is scoped exclusively to the legacy `psw2025-cmd/Genesis_System3` repository. It must not interact with Genesis System3 LIVE NEW.

## Activation runbook
1. Provision or connect a trusted n8n instance (not yet verified) and import `genesis-legacy-ci-evidence-loop.json`.
2. Attach a GitHub API credential to **Read GitHub Actions runs** with minimum read-only Actions access. Never embed a token in the JSON, URL, code node, or execution output. If the repository is private, anonymous requests will fail.
3. Manually execute once and verify the HTTP node returns a `workflow_runs` array, then inspect the Code node's `status`, `next_action`, `checks`, `failures`, `stalled` and `pending`. Confirm the response matches GitHub's run URLs.
4. Add a durable ledger sink (e.g., protected GitHub branch or database) and an authorized execution worker before enabling remediation. The supplied workflow **only reads and classifies CI**; it cannot correct code, dispatch trusted council runs, notify other agents, or establish artifact readback. Do not misrepresent it as autonomous repair.
5. Keep this workflow inactive until an owner chooses whether n8n or the existing ChatGPT Genesis Master Orchestrator owns the hourly trigger; otherwise two schedulers will duplicate work. Once chosen, activate and inspect first scheduled execution history and readback.
6. Extend only through reviewed PRs: (a) bounded backoff and idempotency keyed by `run_id`/`head_sha`, (b) job/log retrieval, (c) explicit evidence artifact verification, (d) task queue with leases and retry budgets, (e) safe PR-only repair, (f) CI and branch-protection verification, (g) latency SLO tracking and upgrades based on previous delays. Preserve complete audit history.
7. To evaluate past delays, compare timestamped run creation/start/end with prior cycle; measure queue latency, execution latency, repeat failures, stale runs, and missing verification. Never claim an improvement until before/after measurements on comparable work exist.

## Classification rules
- `FAIL` if a latest workflow run fails or remains incomplete more than 45 minutes after creation.
- `RUNNING` when latest runs are still in progress.
- `NOT_VERIFIED` when CI has no observed failure but authenticated three-provider council execution, artifact readback, UI/runtime proof and current deployed SHA are still unverified.
- `verified_workflow_count` counts observed successful latest workflow runs; **not** completed tasks or verified production capability.
- The GitHub Actions endpoint is paginated to 100 recent runs; a repository with more workflows may have incomplete coverage. For full coverage, add pagination and workflow-specific queries before calling it comprehensive.

## Safety
No live broker orders, deployments, secrets exposure, arbitrary shell execution, or untrusted PR code with provider credentials. Keep PAPER_MODE=1, LIVE_ORDER_AUTHORITY=0, REAL_BROKER_ORDERS=0, LIVE_TRADING_ENABLED=0 and ORDER_PLACEMENT_ALLOWED=false. The template does not alter runtime safety settings.

## Verified regression discovered 2026-11-17
The CI run for n8n PR #652, head `6bdb4aa6788e7a1f0cfd1dfb720edf910f110dee`, revealed **actual failures**, not a scheduler-only delay:
- Global Safety CI: https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881870 — frontend browser runtime job failed, other inspected jobs including policy guard passed.
- Frontend Browser Runtime Smoke: https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881899 — `genesis:lazy_content_still_loading` and `mobile_genesis:render_not_proven`. The other 22 canonical tabs were reported PASS in the inspected run; this is not production proof.
- UI artifact ID `14291453346`: https://github.com/psw2025-cmd/Genesis_System3/actions/runs/43999881899/artifacts/14291453346. Artifact existence and upload SHA in logs do **not** establish independent downloaded readback.

### Exact next repair sequence
1. Fetch the current `main` frontend Genesis tab lazy-import/component source and browser harness; reproduce the tab-specific unresolved fallback in a deterministic local Chrome CI run.
2. Trace import error, missing provider context, API await or render deadlock; distinguish component failure from a test-only timeout. Fix the underlying frontend or harness race without suppressing assertions.
3. Execute production build, TypeScript check, browser smoke on desktop and mobile, then verify all 23 tab PASS lines and no loading fallback.
4. Verify the exact new PR SHA and rerun Global Safety CI and Frontend Browser Runtime Smoke; both must conclude success. Only then mark this incident PASS.
5. Update durable task ledger and delay metrics; never convert FAIL to PASS by raising timeouts alone.

### Classifier hardening
The n8n code now checks the GitHub API schema, selects the newest run by timestamp rather than relying on API array order, treats absent runs as NOT VERIFIED, distinguishes RUNNING and FAIL, and explicitly labels provider review, runtime and artifact readback as unverified. A 100-run response still requires pagination before claiming complete workflow coverage.
