# RHUI_RULE_V2.2 — Genesis System3 Cloud-Only Multi-Agent Execution Contract

Status: ACTIVE when merged. Supersedes prior RUHI/RHUI rules that allowed local-laptop execution or local forensic authority.

## 0. Current acceptance lock (material change — 2026-08-27 full cross-verify)

**Overall RHUI V2.2 = NOT_ACCEPTED** until the gate board in `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` is all green for acceptance criteria. Do **not** falsely claim ACCEPTED after a docs/test-only merge.

Pinned **runtime** serving (do not blind-redeploy): SHA `fb4772f9d52b67a31b55ee85aab8604e525bbad6` · revision `genesis-system3-web-00617-vif` @ 100%.

GitHub `main` tip `0d6955987115f88b710aca0f0f0dec68d23fa6bc` (#371 docs; includes #370/#369) vs serving is **DOCS/TEST/CI_ONLY_LAG** — not a failed Cloud Run promotion. Do not redeploy solely to equalize.

Live proof snapshot (2026-08-27 ~01:05 IST / evidence `reports/latest/full_cross_verify_20260826_193000/`): broker `AUTH_OK` / LIVE OFF / orders OFF; scheduler transport **HEALTHY**; business readiness **PARTIAL** (wrong-date rank/forecast/signals); auto_gates **2/7**. Ruleset `21581518` now has **six** required contexts including `BLOCKING - priority workflows only` (restored this cycle after Gmail/#188 correction). HUMAN_ACTION_REQUIRED=**NO** for ruleset (agent fixed). Continuous 5-min Gmail/scheduler MRI control plan is **owned by sibling agent** → `docs/handoffs/MRI_GMAIL_SCHEDULER_5MIN_CONTROL_PLAN.md` (do not invent a competing plan here).

Mandatory multi-verify artifacts:

- `docs/handoffs/RHUI_V2.2_MATERIAL_CHANGE.md`
- `reports/coordination/RHUI_V2.2_Verification_Checklist.json`
- `reports/coordination/TODO_CHECKLIST_FULL_VERIFY.md`
- `reports/latest/full_cross_verify_20260826_193000/` (+ prior `post369_live_proof_20260827_000506/`)
- `reports/latest/repo_path_audit/cloud_github_vs_laptop.json`
- Issue #188 `SYSTEM3_COORDINATION_V1` comments

Fail-closed distinctions agents must keep:

1. Cloud Run deploy PASS ≠ scheduler-health PASS ≠ RHUI ACCEPTED.
2. 22/22 visual tab mounts ≠ semantic API↔UI acceptance.
3. Pre-market 4/4 NOT READY ≠ broker/token failure (recheck after open).
4. Docs/test-only `main` tip ahead of serving ≠ failed deploy (check Auto Deploy path filters before workflow_dispatch).
5. #369/#371 merge ≠ runtime change (test/docs-only).
6. Claiming `HUMAN_ACTION_REQUIRED=NO` while a required provider context is still omitted from ruleset `21581518` is a governance false-green — re-verify contexts before asserting no human action.

## 1. Single source of truth

All agents (ChatGPT, Cursor, Claude, Codex and any future agent) must reconstruct current state from:

1. GitHub current `main` SHA in `psw2025-cmd/Genesis_System3` — **only code authority**.
2. GitHub Issue #188 — canonical shared technical/progress bus.
3. `reports/coordination/ruhi_task_ledger.csv` — task ownership, dependencies, progress and proof.
4. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md` — coordination snapshot.
5. Authoritative GCP `system3-openalgo-safe` — **only runtime/deployment authority**.
6. **Live Proof Center** — `reports/latest/live_proof_center/LATEST/` (+ `reports/coordination/LIVE_PROOF_CENTER_POINTER.md`, branch `live-proof-center`, workflow `live-proof-center.yml`) — sanitized continuous MRI for agents without laptop/gcloud access.
7. Gmail only as transport/notification; durable state must be reflected back into GitHub.

Before claiming “no GCP / laptop / access”, agents MUST read the Live Proof Center pointer and INDEX. Local laptop repos, local branches, local databases, local Cursor state/history, local token files, local schedulers, local reports and local historical artifacts are **NON-AUTHORITATIVE**. They must not be used for execution, deployment, broker/token recovery, proof or acceptance.

## 2. Cloud-only execution lock

All implementation must start from a fresh remote GitHub `main` in a clean cloud-capable lane.

Forbidden:

- deploying from a laptop checkout;
- minting/rotating broker tokens from a laptop;
- using local `.env`, token files, databases or scheduled tasks as current truth;
- copying a local file/branch into current main because it existed historically;
- using local screenshots/logs as production acceptance;
- allowing a local Cursor/IDE agent to become runtime authority.

Any useful historical idea must be re-derived from current GitHub main, independently reviewed, and implemented through the normal GitHub PR → CI → merge → GCP deploy → exact-serving proof flow.

## 3. No invisible work

Every meaningful agent status must reconcile:

- `RULE_VERSION`
- `BATCH_ID`
- `CURRENT_MAIN_SHA`
- `SERVING_SHA`
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

## 4. Rolling batch rule

Default next batch is the highest-priority executable work, normally up to 20 real tasks.

Every new RHUI status must reconcile the previous batch task-by-task:

- `DONE`: acceptance criteria met and proof recorded.
- `PARTIAL`: some criteria met; remaining work explicit.
- `BLOCKED`: exact blocker and owner/access dependency recorded.
- `SUPERSEDED`: newer task/fix invalidated it; link replacement.
- `NOT_STARTED`: explain why skipped.

Unfinished commitments may not silently disappear.

## 5. Proof hierarchy

For user-visible dashboard behavior, proof priority is:

1. Production dashboard URL rendered in a real browser on exact serving SHA.
2. Screenshot/video/browser artifact tied to URL + timestamp + serving SHA.
3. UI semantic assertion/result tied to exact serving SHA.
4. Same-session backend/API correlation.
5. CI/unit tests.
6. Source/docs only.

For UI tasks, levels 4–6 alone cannot yield `DONE`.

A route-render PASS is not a semantic/data-readiness PASS. Blank/WAITING/placeholder/false-green state fails unless it is explicitly truthful for the current state.

## 6. Specialist ownership

- **ChatGPT**: controller/consolidator, task ownership, acceptance criteria, GitHub/GCP coordination, contradiction resolution, PR/merge/deploy/proof decisions.
- **Claude**: independent cloud/GCP/UI/API forensic verifier and adversarial cross-checker.
- **Cursor/Codex/other coding agents**: implementation only from current GitHub main in cloud/remote lanes; no local-laptop authority.
- **Other agents**: claim a bounded lane in Issue #188/ledger before modifying overlapping files.

Multiple agents may investigate independently; only one implementation writer owns a functional root-cause/file lane.

## 7. Broker/token authority

Broker/token operations are cloud-only.

Canonical authority:

- GCP Secret Manager;
- isolated Cloud Run job `genesis-system3-dhan-token-rotate`;
- approved Cloud Scheduler authority;
- guarded GitHub manual-recovery workflow only when preconditions prove it is required.

The web runtime and local machines must never mint/rotate tokens.

Never blind-mint or retry-until-green. Recovery requires current evidence, single-flight/cooldown protection and metadata-only proof. Do not expose token/PIN/TOTP values.

Broker acceptance requires, on exact current serving revision:

- `/ui` visibly shows broker connected;
- same-session `/api/broker/status` confirms usable broker state;
- token source is canonical dynamic GCP authority, with metadata only;
- NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY have positive contracts/strikes and truthful source/freshness;
- no contradictory WAITING/CLOSED/stale-success state;
- `LIVE=false` and `orders=false`.

`connected=true` alone is not full acceptance.

## 8. Paper-trade acceptance

Do not mark paper trading complete until a real market-session production proof demonstrates:

market data → scanner/ranker → signal decision → paper/analyzer path → persisted paper record → dashboard row → P&L/position update.

Zero live-order safety remains mandatory:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`

unless a separate explicit live-trading authorization is given later.

## 9. Dashboard truth contract

The user should be able to judge progress from the authoritative production URL, not from logs or agent narrative.

All 22 current canonical tabs must be audited region-by-region. Each visible card/badge/table/chart/status/empty-state should be classified as one of:

- `PASS_TRUTHFUL`
- `PASS_DERIVED_TRANSPARENT`
- `STALE_EXPLICIT`
- `DEGRADED_EXPLICIT`
- `UNKNOWN_EXPLICIT`
- `PLACEHOLDER`
- `HARDCODED`
- `DEMO_OR_MOCK`
- `FALSE_GREEN`
- `MISLEADING`
- `MISSING`
- `BROKEN`
- `NOT_APPLICABLE`

User-visible DONE requires exact-current-main Cloud Run revision at 100% traffic and fresh browser proof.

## 10. Stages and progress measurement

Use:

`DISCOVERED -> ROOT_CAUSE_PROVEN -> PATCHED -> TESTED -> EXACT_HEAD_GATED -> MERGED -> DEPLOYED -> UI_PROVEN -> STABILITY_PROVEN -> COMPLETE`

Each meaningful report must publish task counts and reconcile:

`PREVIOUS_TARGET -> ACTUAL_RESULT -> PROOF -> DELTA -> NEXT_TARGET_BATCH`.

Progress percentages must come from task states, not estimates.

## 11. No stale-claim rule

Before starting or reporting a task, verify current remote main, current serving SHA/revision and latest shared RHUI state. Old SHA/revision/email/artifact proof is historical and cannot drive current acceptance.

## 12. Failure and regression rule

Any recurrence after a claimed fix reopens the task or creates a linked regression. Current production truth overrides historical green status.

### 12.1 Immediate interruption and lost-proof disclosure

Every agent must notify the user immediately when a material task, browser
capture, video, screenshot run, test, deployment, API probe, upload, or evidence
write stalls, fails, is interrupted, times out, loses output, or can no longer
finish its promised acceptance proof. The agent must not wait for the user to
ask what happened and must not hide the event inside later status prose.

The immediate update must state: `WHAT_FAILED`, `WHEN`, `USER_VISIBLE_IMPACT`,
`WORK_PRESERVED`, `WORK_LOST_OR_UNPROVEN`, `RECOVERY_ACTION_NOW`,
`USER_ACTION_NEEDED`, and `SAFETY_STATE`. Partial files are never promoted to
valid evidence until integrity and completeness are verified. The agent must
freeze useful diagnostics, stop or clean orphan processes, resume through the
fastest safe path, and report the first recovered proof as a new observation.
Silence after a known material interruption is a RUHI violation.

## 13. Human escalation boundary

The user is not a routine coordination relay.

Human action is allowed only for genuine external owner-only boundaries such as:

- billing/subscription/funding;
- identity/consent;
- official broker account/MFA/credential reset;
- unavailable external permission with no safe cloud bridge;
- destructive action requiring explicit approval;
- explicit LIVE trading approval.

Routine repo, CI, deploy, broker-status, scheduler, UI and proof work remains agent-owned.

## 14. Safety

Do not weaken IAM/WIF, expose secret values, mint/rotate tokens unnecessarily, enable live trading, place/modify/cancel live orders, dilute gates or accept retry-until-green behavior merely to make proof pass.

## 15. Definition of a useful agent cycle

A useful cycle produces at least one of:

- a newly completed task with required proof;
- a materially narrowed root cause with evidence;
- a tested bounded remediation;
- a resolved access/coordination blocker;
- a regression converted into an owned task;
- a new exact-serving browser/API truth observation.

Pure restatement of old status does not count as progress.

## 16. Action-over-narrative and controller accountability (2026-08-30)

This rule is mandatory for ChatGPT/controller and every current or future agent. It exists because prolonged analysis, status reporting, email/Issue commentary, repeated diagnosis, or coordination without converting known gaps into implementation is a System3 failure mode.

1. **The controller must act, not merely observe.** When a material defect is found and the connected execution lane can safely modify the repository, tests, workflow, tracker, or documentation, the controller must create the bounded implementation change in the same working cycle or explicitly record the exact technical blocker that makes execution impossible. A response that only describes what another agent should do is non-compliant when the controller has the capability to do it.
2. **No repeated rediscovery.** Once a defect/root cause is known, future cycles must start from that state and advance it through `PATCHED -> TESTED -> EXACT_HEAD_GATED -> MERGED -> DEPLOYED -> UI_PROVEN`, rather than repeatedly rescanning and rewriting the same explanation.
3. **Multi-agent work does not reduce controller responsibility.** ChatGPT remains accountable for continuously checking whether specialist work actually closes the end-to-end requirement. A specialist producing major progress in one day that exposes long-standing controller omissions must trigger immediate reconciliation: identify what the controller failed to implement/check, add those omissions to the ledger, and execute all safe controller-owned remediation without waiting for the user.
4. **New-agent discoveries are mandatory learning inputs.** Any materially better architecture, tool, proof mechanism, dashboard capability, forensic technique, or implementation produced by another agent must be compared against the current authoritative system. Missing superior capability becomes an owned upgrade task; it may not be ignored because an older controller/script already exists.
5. **Command Center must never be stale authority.** `scripts/system3_command_center_refresh.py` and its outputs are not accepted as authoritative merely because they are named Command Center. They must be cross-verified against current GitHub main, current GCP serving revision/traffic, Live Proof Center/Ultra-MRI, browser reconciliation, current Issue #188 state, and India market-session authority. A stale committed snapshot must be explicitly labelled `STALE/NOT_AUTHORITY`.
6. **Controller scripts must evolve with the system.** When newer proof machinery supersedes a narrower controller path, the established central controller must integrate the newer machinery instead of leaving parallel disconnected truth systems. Specifically, the Command Center should orchestrate canonical Live Proof Center, Ultra-MRI, serving-SHA/browser reconciliation, current GitHub issue/workflow evidence, market-session classification, and lifecycle dependency generation rather than relying on a fixed PEND catalog alone.
7. **Dynamic discovery over hard-coded comfort.** Hard-coded issue catalogs/dependency maps may seed checks but cannot be the sole source for current defects. Current P0/P1 GitHub issues, exact-main workflow failures, production API/browser failures, GCP runtime/scheduler/job failures, stale/false-green UI states, broker/data gaps, prediction/paper lifecycle failures, and cleanup/resource hygiene findings must be dynamically reconciled.
8. **Every material chat cycle needs an execution delta.** Unless genuinely blocked by an owner-only boundary, a material System3 cycle must produce at least one concrete delta such as a commit/PR, test, workflow run, live proof refresh, issue/ledger state transition, safe configuration repair, or implemented controller improvement. Chat/email/Issue text alone is not sufficient when an executable remediation is available.
9. **No credit for activity without closure.** Number of messages, emails, comments, scans, reports, years spent, agents involved, or tests run is not progress by itself. Progress is measured only by verified lifecycle state advancement and truthful production proof.
10. **Controller self-audit after material specialist progress.** After any specialist lands a material batch, the controller must ask: `What did this expose that the controller should already have detected, implemented, integrated, or verified?` The answer becomes immediate actionable work, not narrative commentary.
11. **User is not the enforcement mechanism.** The user must not need to repeatedly remind agents to implement rather than discuss. Violation of this section is itself a governance defect that must be surfaced in Issue #188/ledger and corrected.
12. **Safety remains unchanged.** Action-over-narrative never authorizes LIVE trading, secret exposure, destructive cleanup, gate dilution, blind token rotation, or unsafe IAM changes. Safe PAPER/analyzer implementation and proof should proceed autonomously; genuine irreversible/owner-only boundaries still require explicit authorization.
