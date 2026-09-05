# Genesis System3 — Permanent Multi-Agent Coordination Center

**Purpose:** one permanent place every agent must read before work so the user never has to repeat the operating rules.

**Repository:** `psw2025-cmd/Genesis_System3`

**Production:** GCP project `system3-openalgo-safe`, region `asia-south1`, Cloud Run service `genesis-system3-web`.

**Primary live P0:** GitHub Issue #188.

## Mandatory entry rule

Every Cursor / Claude / Codex / ChatGPT / Cloud Agent / unknown agent must:

1. Read `AGENTS.md`.
2. Read this file.
3. Read `docs/project_control/AGENT_TASK_LEDGER.md`.
4. Refresh `origin/main`, open PRs, current Issue #188 comments, relevant workflows, and current GCP serving state before changing anything.
5. Never use an old report, old screenshot, old email, old PR summary, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, or `reports/latest/` as current truth without fresh verification.
6. Claim a non-conflicting lane in the shared ledger / Issue #188 before editing.
7. Execute first; report after obtaining real results.

## One-center coordination rule

The shared center is:

- **Permanent rules:** `docs/project_control/AGENT_COORDINATION_CENTER.md`
- **Current schedule / ownership / pending / proof:** `docs/project_control/AGENT_TASK_LEDGER.md`
- **Append-only cross-agent runtime log and P0 evidence:** GitHub Issue #188

Do not create competing coordination files unless this center explicitly delegates one.

## Continuous operating loop

Every agent repeats:

`REFRESH CURRENT TRUTH → READ OWNERSHIP → CLAIM SAFE LANE → EXECUTE → ROOT CAUSE → IMPLEMENT → TEST → CI → DEPLOY → NEW API PROOF → NEW PRODUCTION UI PROOF → UPDATE LEDGER + ISSUE #188 → TAKE NEXT TASK`

Do not wait for another user prompt for routine engineering work.

## Frequency / refresh schedule

These are execution rules, not user-notification spam:

- **At agent start:** full refresh of repo, open PRs, Issue #188, relevant workflows, GCP serving SHA, broker/API, and task ledger.
- **Before every edit / merge / deploy / production claim:** refresh `origin/main`, ownership, exact-head CI, and current serving revision.
- **While another workflow/deploy is running:** mark that lane `WAITING` and immediately continue a different non-conflicting safe task.
- **During active incident / P0:** re-check dependencies frequently enough to avoid stale decisions; do not busy-poll if useful work exists elsewhere.
- **After any merge/deploy/recovery:** create fresh API and production-browser evidence; pre-change evidence becomes historical.
- **At end of every work batch:** update the task ledger and Issue #188 with current status, proof, blockers, and next actions.

## Tool-first rule

When a safe tool can answer the question, run it before writing a plan.

Preferred order:

1. repository-native scripts;
2. Git / GitHub current state;
3. GCP runtime metadata/logs;
4. fresh production APIs;
5. fresh Chrome/WebDriver production UI;
6. focused tests;
7. broader CI;
8. external research only when it materially improves the solution.

Always inspect available tools quickly at start (`git`, `gh`, `gcloud`, `python3`, `curl`, `jq`, `rg`, `npm`, `node`, browser/Playwright/Selenium). Do not install tools merely because they are new; install/upgrade only when current capability is insufficient.

## No-idle rule

Never stop merely because CI, deploy, another agent, or propagation is pending.

1. Set the dependency lane to `WAITING`.
2. Select the highest-value unclaimed safe task.
3. Continue working.
4. Return when the dependency result exists.

## Shared task statuses

Use only these progress states:

- `TODO`
- `IN_PROGRESS`
- `WAITING`
- `BLOCKED_EXTERNAL`
- `DONE_CODE`
- `DONE_TESTED`
- `DONE_DEPLOYED`
- `DONE_LIVE_PROVEN`

For engineering maturity also record level when useful:

- `L0 DISCOVERED`
- `L1 ROOT_CAUSE_PROVEN`
- `L2 FIX_IMPLEMENTED`
- `L3 LOCAL_TESTED`
- `L4 CI_GREEN`
- `L5 MERGED`
- `L6 EXACT_SHA_DEPLOYED`
- `L7 API_PROVEN`
- `L8 UI_PROVEN`
- `L9 STABILITY_PROVEN`

Never call a task simply DONE when it has only reached code or CI.

## Required task fields

Every active ledger row must contain:

`ID | PRIOR_COMMITMENT | OWNER | STATUS | LEVEL | DEPENDENCY | ACTION_TAKEN | PROOF | LIVE_UI_PROOF | BLOCKER | NEXT_ACTION | TARGET_PR`

## Multi-agent ownership

Before editing or merging:

- `git fetch origin --prune`
- inspect current `main`;
- inspect open PRs and current Issue #188 comments;
- determine which agent owns each active lane and which files are being touched;
- never silently overwrite newer work;
- use an independent lane when another agent already owns the same area;
- if agents disagree on production truth, generate new live evidence rather than debating historical artifacts.

## Defect closure rule

For every verified defect:

`fresh reproduce → first divergence → root cause → affected surfaces → compare safe fixes → smallest durable fix → regression/adversarial tests → focused tests → mandatory CI → merge per governance → exact serving SHA → fresh API proof → fresh production UI proof → stability proof if required`

Do not stop at “issue found”, “code fixed”, or “workflow green”.

## Production evidence hierarchy

For current runtime/UI claims use:

1. fresh production browser observation;
2. same-session production API evidence;
3. same-window production logs/runtime metadata;
4. current serving revision/SHA/config;
5. current source;
6. historical artifacts only for comparison.

## Canonical production UI

`https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`

For full UI lifecycle proof verify all 22 canonical tabs from `AGENTS.md`. `HTTP 200` or “tab rendered” is not semantic PASS. User-visible proof requires populated/correctly-labelled data, freshness/source truth, no unexplained placeholders, and API↔UI parity where applicable.

## Safety boundary

Always preserve:

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`

Never place/modify/cancel/square-off real orders, expose secrets, print raw broker tokens, or create/export service-account JSON keys. Dhan token rotation/recovery must use the dedicated governed authority only.

## User-action boundary

Routine repo/code/tests/CI/logs/deploy verification/browser proof/safe recovery should be handled without asking the user to do developer work. Ask the user only for genuine account-level or break-glass actions such as LIVE enablement, real orders, broker MFA, billing/org changes, or unavailable account permissions.

## User update rule

Do not send the user long repeated technical narratives by default.

Default user-facing update is only:

1. **SCHEDULED / RUNNING** — what is currently executing or waiting.
2. **NEXT** — next highest-priority actions.
3. **PENDING / BLOCKED** — only unresolved items requiring attention.
4. **USER ACTION** — normally `NONE`; show only genuine user-required action.

All detailed proof, exact commands, SHAs, workflow IDs, screenshots, blocker micro-details, and cross-agent handoffs belong in the shared ledger / Issue #188 unless the user asks for detail.
