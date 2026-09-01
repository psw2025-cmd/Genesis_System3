# Genesis System3 Autonomous End-to-End Runbook

**Authority marker:** `SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1`

**2026-09-01 authority override:** `docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md` is the current user-directed execution-ownership authority. Claude is the sole controller/executor. Other agents are advisory/forensic/verification only unless Claude delegates a bounded non-overlapping task. This override changes ownership, not the PAPER/zero-order safety locks below.

**Role:** Persistent self-instruction and completion ledger contract for Codex,
ChatGPT, Cursor, Gemini, Claude, and every generic/unknown agent operating in
this repository.

## Mandatory re-read boundary

Re-read this runbook and `docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md` from the current checked-out commit immediately before:

1. every merge decision;
2. every deployment or production mutation;
3. every production acceptance or rollback decision;
4. every issue/blocker closure;
5. every final response that claims completion, current state, or user action.

Chat memory, an earlier read, a prior agent summary, and `reports/latest/` do not
satisfy this boundary. Record the runbook path, marker, current Git SHA, and
re-read UTC time in the active completion ledger.

## Authority order

For execution ownership, `docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md` takes precedence. Safety and evidence requirements remain governed by the narrower applicable authorities below:

1. `docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md`
2. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
3. `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`
4. `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`
5. `docs/END_TO_END_ISSUES_SOLUTIONS_AGENT_POLICY.md`
6. `agent_policy.yaml`
7. `docs/CONTINUOUS_CLOSURE_SYSTEM.md`
8. `docs/PREFLIGHT_CONTROL_PLANE.md`
9. `docs/architecture/INFINITE_GITOPS_AGENT_PROMPT.md`

When two sources appear to disagree, fail closed, preserve safety, and route execution-ownership conflicts to Claude. Stale multi-agent ownership must not create parallel mutations.

## Permanent safety state

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- PAPER/analyzer only
- no real order placement, modification, cancellation, or square-off
- no broker secret payload exposure
- no service-account JSON keys
- Dhan is the broker authority; Render and Angel instructions are historical

Only an explicit human break-glass process may authorize LIVE trading or real
orders. Routine autonomy never broadens that authority.

## Claude-controlled execution cycle

Claude owns implementation, debugging, tests, CI remediation, migration, GCP cleanup, deployment sequencing and final acceptance. Every other agent must restrict itself to evidence gathering, independent verification, review or a task explicitly delegated by Claude. Findings go to Issue #188; they do not create competing implementation lanes.

For each issue or goal Claude must: verify the authoritative symptom; identify root cause and downstream dependencies; implement the smallest durable solution from current main; test it; reconcile concurrent upstream work; prove runtime/serving state; and continue until the user-visible end goal is proven or a genuine external/user-only blocker is demonstrated.

## GCP-exit and billing-control requirement

The 2026-09-01 evidence establishes a contained but unresolved configuration conflict: all nine asia-south1 Cloud Scheduler jobs were observed PAUSED, while prior same-day executions show the scheduler collector firing approximately every minute and Dhan token rotation approximately every five minutes. Repository scheduler authority also conflicts: the scheduler contract encodes high-frequency behavior while the rotation infrastructure documentation describes a 07:30 Asia/Kolkata trigger.

Claude must keep the high-frequency schedules contained while reconciling repository SSOT, GCP runtime, laptop runtime, broker token lifecycle, state/data dependencies, backup/restore, background workers, logging/monitoring, deployment triggers and cost-generating resources. A pause alone is not completion if repository automation can recreate the cost source.

## Production and UI proof

A completion claim requires fresh evidence from the actual selected authoritative runtime. Code, PR, CI, HTTP 200, rendered tabs, or historical screenshots alone are insufficient. Preserve exact source SHA/runtime provenance, broker/source/freshness truth, browser/API semantic parity and zero-real-order evidence.

## Coordination

GitHub Issue #188 remains the live coordination/status bus. Claude posts task start, material state change, blockers and completion evidence. Other agents may post independent evidence but may not claim execution ownership or start overlapping mutations.
