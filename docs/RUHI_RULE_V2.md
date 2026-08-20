# RUHI_RULE_V2 — Genesis System3 Multi-Agent Execution Contract

Status: ACTIVE when merged. Supersedes informal/local-only coordination rules.

## 1. Single source of truth

All agents (ChatGPT, Cursor, Claude and any future agent) must reconstruct current state from:

1. GitHub current `main` SHA.
2. GitHub Issue #188 for live P0/UI parity status.
3. `reports/coordination/ruhi_task_ledger.csv` for task ownership, dependencies, progress and proof.
4. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md` for current coordination snapshot.
5. Gmail RUHI messages only as transport/notification; durable state must be reflected back into GitHub.

Local laptop notes, local Cursor rules, unpushed Claude patches, stale emails and old workflow results are not authoritative until mirrored into the shared ledger/handoff or landed in GitHub.

## 2. No invisible work

Every agent status email/update MUST contain these sections in this order:

- `RULE_VERSION`
- `BATCH_ID`
- `CURRENT_MAIN_SHA`
- `SERVING_SHA` (if production relevant)
- `MARKET_PHASE`
- `PREVIOUS_BATCH_COMMITMENT`
- `PREVIOUS_BATCH_RESULT`
- `COMPLETED_WITH_PROOF`
- `NOT_COMPLETED`
- `BLOCKERS_OR_CONFUSION`
- `HANDOFF_REQUIRED`
- `NEXT_BATCH_COMMITMENT`
- `USER_ACTION_REQUIRED`

A task is not complete because code exists, CI is green, a PR merged or an API returned 200. Completion requires the proof class defined in the ledger.

## 3. Twenty-task rolling batch rule

Default batch size is 20 highest-priority executable tasks.

Each new RUHI status message must reconcile the previous batch task-by-task before creating the next batch:

- `DONE`: acceptance criteria met and proof recorded.
- `PARTIAL`: some acceptance criteria met; remaining work explicit.
- `BLOCKED`: exact blocker and owner/access dependency recorded.
- `SUPERSEDED`: newer task/fix invalidated it; link replacement.
- `NOT_STARTED`: must explain why it was skipped.

The next mail must never silently replace or forget unfinished commitments from the previous mail.

If fewer than 20 executable tasks exist, publish the real smaller number. Never invent tasks to satisfy the count.

## 4. Proof hierarchy

For user-visible dashboard behavior, proof priority is:

1. Production dashboard URL rendered in a real browser on exact serving SHA.
2. Screenshot/video/browser artifact tied to URL + timestamp + serving SHA.
3. UI semantic assertion/result tied to exact serving SHA.
4. Backend/API correlation.
5. CI/unit tests.
6. Source/docs only.

For UI tasks, levels 4–6 alone cannot yield `DONE`.

Required dashboard proof should include visible source/freshness/error state where relevant. A blank/WAITING/placeholder tab is a failure even if the route renders.

## 5. Specialist ownership

- Cursor: laptop-local history, local repo archaeology, browser/UI capture, GCP/browser surfaces available to Cursor, practical reproduction, local patches and UI-facing implementation when fastest.
- Claude: independent forensic/adversarial review, root-cause hypotheses, patch preparation when it lacks push access, independent cross-check of claims.
- ChatGPT: controller/consolidator, Gmail/GitHub coordination, task ledger authority, acceptance criteria, PR review/merge decisions, contradiction resolution and final user-facing status.
- Other agents: claim a bounded lane in the ledger before modifying overlapping files.

Specialists own tasks in their strongest domain. Avoid duplicate implementations.

## 6. Access-gap handoff rule

If an agent lacks access, it must not stop at `cannot access`. It must provide a micro-handoff containing:

- exact task ID;
- exact command/UI path/API endpoint;
- expected evidence;
- current observed evidence;
- suspected files/functions/resources;
- safety constraints;
- success/failure acceptance criteria;
- recommended next owner.

The receiving agent records the result in the same ledger row.

## 7. Local-laptop origin forensic is mandatory

Genesis System3 existed locally before GCP deployment. Long-lived defects (especially paper-trade absence, missing UI data, stale hard-coded/demo paths and migration gaps) must be investigated against local history, not only current cloud code.

Cursor must inventory, without exposing secrets:

- historical local repo roots/checkouts;
- branches/commits not present on remote;
- old databases/logs/reports proving whether paper trades ever existed;
- old scheduler/task configuration;
- old environment/config names (names only, no secret values);
- old UI/backend implementations and dead code;
- files/features lost or changed during local → GitHub → GCP migration;
- duplicate/obsolete Render-era logic;
- discrepancies between laptop behavior and current GCP serving behavior.

Findings must be converted into ledger tasks with evidence and remediation owner.

## 8. Paper-trade acceptance rule

Do not mark paper trading complete until a real market-session production proof demonstrates end-to-end:

market data → scanner/ranker → signal decision → paper/analyzer order path → persisted paper record → dashboard paper-trade row → P&L/position update.

Zero live-order safety must remain proven: `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0` unless the user explicitly authorizes a separate live-trading change.

## 9. Dashboard is the user acceptance surface

The user should not need to interpret logs, JSON or CI to know whether a feature works. Downstream work is accepted only when the relevant result is visible and truthful on the production dashboard URL wherever the task is user-facing.

All dashboard tabs/features must eventually have a ledger row and latest proof timestamp.

## 10. Progress measurement

Each status mail must publish:

- total known tasks;
- DONE count;
- PARTIAL count;
- BLOCKED count;
- OPEN executable count;
- previous batch completion percentage;
- number of tasks with fresh production-UI proof;
- number of regressions reopened since prior mail.

Progress percentage must be calculated from task states, not estimated subjectively.

## 11. No stale-claim rule

Before starting or reporting a task, verify current main/serving SHA and recent ledger state. A claim based on an old SHA, old revision or old email must be labeled STALE and cannot drive acceptance.

## 12. Failure and regression rule

Any recurrence after a claimed fix reopens the task or creates a linked regression task. Do not preserve a green historical status when current production disproves it.

## 13. Email convention

Subjects:

- `RUHI CLAIM — <agent> — <batch/task>`
- `RUHI STATUS — <agent> — <batch> — <result>`
- `RUHI FINDING — <agent> — <task>`
- `RUHI HANDOFF — <from> → <to> — <task>`
- `RUHI HUMAN-ACTION — <task>`

Every mail must include the ledger path and task IDs changed.

## 14. Safety

Do not weaken IAM/WIF, expose secret values, mint/rotate tokens unnecessarily, enable live trading or place/modify/cancel live orders merely to make a proof pass. Live-order-capable changes require explicit proof of analyzer-only isolation or explicit user authorization.

## 15. Definition of a useful agent cycle

A cycle is useful only if it produces at least one of:

- a newly completed ledger task with required proof;
- a materially narrowed root cause with evidence;
- a tested code/config remediation ready for the owning agent;
- a resolved blocker/access handoff;
- a regression caught and converted into an owned remediation task.

Pure restatement of old status does not count as progress.
