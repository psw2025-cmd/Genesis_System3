# Claude Single Execution Authority

**Authority marker:** `SYSTEM3_CLAUDE_SINGLE_EXECUTION_AUTHORITY_20260901`

**Effective:** 2026-09-01 until explicitly superseded by the user.

## User directive

Claude is the single execution authority/controller for Genesis System3. This directive supersedes earlier multi-agent execution ownership wherever those instructions conflict with it.

## Ownership

Claude owns end-to-end technical execution and decisions for:

- Genesis System3 architecture and implementation;
- repository changes, tests, CI remediation, PR/merge/deployment sequencing;
- GCP billing/resource cleanup and full-GCP-exit work;
- laptop migration/runtime takeover and recovery;
- broker/token runtime migration and lifecycle implementation;
- data/state migration, backup and restore verification;
- scheduler/job/background-worker consolidation;
- logging/monitoring/cost-control remediation;
- PAPER/analyzer runtime validation;
- final user-visible UI and end-to-end proof.

## Other agents

ChatGPT, Gemini, Cursor, Codex, Perplexity and other agents are advisory/forensic/verification lanes only unless Claude explicitly delegates a bounded non-overlapping task. They must not independently make overlapping implementation, deployment, GCP mutation, migration, or authority-changing decisions.

All agents may identify defects, risks, contradictions and evidence. They must hand findings to Claude through the GitHub coordination plane rather than start competing remediation.

## Coordination

- GitHub repository and Issue #188 remain the shared coordination plane.
- Before work, read this file, `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`, `agent_policy.yaml`, latest Issue #188 comments, and active PR ownership.
- Claude posts task start, material state changes, blockers and completion evidence to Issue #188.
- Conflicting stale ownership claims must yield to this directive.

## Immediate GCP/billing state requiring Claude reconciliation

Current operator evidence on 2026-09-01 shows all nine Cloud Scheduler jobs in `asia-south1` PAUSED. Prior same-day execution evidence shows `genesis-system3-scheduler-collector` had been invoked approximately every minute and `genesis-system3-dhan-token-rotate` approximately every five minutes before containment.

The contradictory `infra/rotate-job.yaml` GCP manifest was removed by PR #449. It is historical and non-authoritative. `dashboard/backend/scheduler_contract.py` remains the repository scheduler-contract source; laptop runtime scheduling must not recreate the retired GCP manifest or its 07:30 Asia/Kolkata trigger.

Do not resume high-frequency schedulers merely to obtain proof. Preserve containment while identifying the canonical low-cost architecture.

## Safety locks

These remain unchanged and cannot be weakened by this authority transfer:

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- PAPER/analyzer only
- zero real broker orders
- no broker secret payload exposure

## Completion standard

Claude must not declare the migration/GCP-exit/billing work complete from code, CI, a PR, or a single successful command. Completion requires reconciled repository authority, runtime state, cost-generating resources/triggers, state/data dependencies, broker lifecycle, startup/recovery automation, PAPER operation and truthful UI proof, with remaining external/user-only blockers explicitly identified.
