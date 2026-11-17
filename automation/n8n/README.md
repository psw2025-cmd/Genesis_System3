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
