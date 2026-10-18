# Genesis System3 — agent constitution

**Active owner directive:** `docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md` (`SYSTEM3_CLOUD_ONLY_OWNER_DIRECTIVE_20261018`).
**Code authority:** `psw2025-cmd/Genesis_System3` exact approved `main` SHA.
**Target production authority (not a readiness claim):** GCP `system3-openalgo-safe` / `asia-south1`.
**Machine policy:** `agent_policy.yaml` (v6).
**Temporal marker:** `SYSTEM3_TEMPORAL_TRUTH_V1` — `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
**Broker:** Dhan. Retired Render and Angel-era deployments/instructions are historical and non-authoritative for System3.

## Priority and conflicts
1. Latest explicit owner instruction, including the active cloud-only directive and its scoped consent.
2. Permanent trading, secret, cost/approval and destructive-operation safety.
3. This constitution and the active machine policy.
4. Applicable scoped rules, runbook, current source and fresh evidence.
5. Prior local-laptop/RUHI/GCP-exit material and historical reports as history only.

The 2026-09-07 local-laptop directive and conflicting older prose are superseded. The laptop/Cloud Shell is only an optional control client. Never require a local System3 server, checkout, Windows scheduler or laptop uptime for routine operation.

## Owner-approved actions as of 2026-10-18
Autonomous GitHub repairs, testing, CI and read-only GCP verification ONLY. Separate explicit owner approval is required before any new billable cloud build/deployment or cloud configuration mutation (including GCP IAM, Scheduler, Cloud Run, secrets, artifact pushes, billing/budgets). A PR merge is not implicit permission to deploy. Do not enable automatic production deployment through a normal GitHub push.

## Permanent PAPER/analyzer safety
```text
ANALYZE_MODE=1
PAPER_MODE=1
SYSTEM3_MODE=analyze
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
LIVE_ORDER_AUTHORITY=0
ORDER_PLACEMENT_ALLOWED=false
```
No real order placement/modification/cancellation/square-off, no order-shaped real-broker test traffic, no broker secret payload in code/chat/logs/evidence, no service-account JSON keys, no bypass of safety gates. Prove real broker order counts independently before claiming zero.

## GitHub and evidence discipline
Dedicated non-destructive branch/PR from fresh main; inspect parallel PR ownership and workflow side effects before writing. Do not force-push or overwrite unrelated work. Only current independently observed cloud runtime and same-session authenticated API/browser/broker receipts can establish production truth. CI green, `reports/latest/`, historical GCP image digests and HTTP 200 alone cannot. Evidence statuses: `PASS/FAIL/BLOCKED/UNKNOWN/PARTIAL/NOT_PROVEN/HISTORICAL_ONLY`. Include UTC time, project, command, exit, exact SHA/digest and proof hash. Read-only project inventory must use explicit `--project` and region.

## Delivery
Carry out safe connected-tool work autonomously; ask the owner only at genuine owner-only approval/consent/MFA boundaries. Keep blocked and unknown facts explicit. Follow `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md` for exact pre-merge and acceptance re-reads. Full PAPER/ANALYZE PASS requires verified deployed cloud runtime, single worker lease, fresh data, 22-tab semantic UI/API parity, durable paper ledger, provenance and independent LIVE/order safety checks.
