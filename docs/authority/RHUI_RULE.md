# RHUI Rule — Practical Multi-Agent Progress Contract

**Marker:** `RHUI_RULE_V2`

This policy extends the repository's autonomous-operations and temporal-truth policies. It defines how ChatGPT, Claude, Cursor, and future agents coordinate, prove work, and expose practical progress.

## Canonical coordination surfaces

- GitHub Issue #188 is the shared technical coordination bus.
- Gmail is the asynchronous Claude ↔ ChatGPT coordination bus.
- Cursor and future repo agents must not depend on Gmail access; accepted cross-agent findings must be mirrored into Issue #188.
- The user is not a routine technical relay.

## User-visible outcome

The authoritative GCP `/ui` dashboard is the final user acceptance surface. GitHub, Gmail, APIs, logs, tests, workflow artifacts, and reports are investigation/evidence sources only.

Do not call a production-affecting task complete until the applicable chain reaches:

`DISCOVERED -> ROOT_CAUSE_PROVEN -> PATCHED -> TESTED -> EXACT_HEAD_GATED -> MERGED -> DEPLOYED -> UI_PROVEN -> STABILITY_PROVEN -> COMPLETE`

A green PR/CI/deploy or 22/22 route render alone is not semantic production completion.

## Required report/mail structure

Every meaningful agent report must contain:

- `RHUI_REPORT_V2`
- `AGENT`, `ROLE`, `CAPTURE_UTC`, `CAPTURE_IST`
- `CURRENT_MAIN_SHA`, `SERVING_SHA`, `SERVING_REVISION`
- `PREVIOUS_COMMITMENTS[]`
- `COMPLETED_THIS_REPORT[]` with proof URL/path/run/PR/SHA/UI capture
- `NOT_COMPLETED[]` with exact reason, owner, and next attempt
- `CURRENT_IN_PROGRESS[]` with observable evidence
- `NEXT_TARGET_BATCH[]` — bounded, independently verifiable tasks; default up to 20, never filler
- `BLOCKERS[]` with `HUMAN_ACTION_REQUIRED=YES/NO`
- `ALTERNATIVE_SOLUTIONS[]` for confirmed blockers: minimum fix / structural fix / defense-in-depth
- `RECOMMENDED_SOLUTION`
- `NEXT_OWNER`, `NEXT_ACTION`

Every later report must explicitly reconcile the previous report's commitments. Unfinished tasks cannot disappear.

## Parallelism and ownership

- Multiple agents may independently investigate the same symptom.
- Exactly one implementation owner may write a functional root-cause/file lane at a time.
- Before any mutation, re-read current `main`, open PRs, changed files, current Issue #188 ownership markers, and current mandatory checks.
- Waiting on CI, deployment, another agent, market hours, or an external dependency must not freeze unrelated work. Continue safe non-overlapping tasks.
- Never create competing patches for the same root cause.

### Default specialist lanes

- **ChatGPT:** consolidation, GitHub landing, exact-head CI/review/merge coordination, exact-main deployment/proof coordination, cross-agent contradiction resolution.
- **Claude:** independent read-only live/GCP/UI/API forensics, deployment-risk verification, semantic/UI parity checks, token-liveness and stability evidence.
- **Cursor/local-capable agent:** repo/editor implementation, local-laptop historical forensics, frontend/browser implementation, focused regression tests.

If an agent lacks required access, it must produce a micro-handoff containing exact file/function/run/error/evidence/requested action so another capable owner can continue without the user debugging manually.

## Practical progress board

Maintain a machine-readable progress tracker (CSV or JSON is acceptable) and expose a user-visible **RHUI Progress** panel inside an existing `/ui` operator surface such as **System** or **Truth Control**. Do not add a new canonical tab merely for coordination unless the UI contract is intentionally updated.

Minimum fields:

`task_id | priority | area | owner | stage | proof | last_action | next_action | blocker | human_action | updated_ist`

Until this panel is deployed and exact-serving UI-proven, Issue #188 plus RHUI Gmail reports are the temporary control board.

## Full-System MRI scope

Reusable read-only proof should cover, as applicable:

- exact serving SHA/revision/traffic;
- market-session truth;
- broker status and token metadata without secret values;
- NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY chain source/freshness/contracts/spot;
- all 22 canonical tabs and semantic content;
- NSE/BSE universe and index/equity derivatives;
- index and equity option chains across supported symbols/expiries/strikes;
- charts and WebSocket/reconnect behavior;
- Signals, Trade, Paper lifecycle, Positions, P&L, Performance;
- ML/model registry/training/prediction/calibration/drift/retraining;
- Risk & Scenarios;
- scheduler/jobs/alerts/System/Live Gate;
- same-session API ↔ UI parity;
- sustained market-session stability.

## Local-history forensic lane

Genesis System3 existed on a local laptop before GCP. A local-capable agent must separately inventory historical databases, paper logs, reports, schedulers, processes, sample/demo rows, and runtime paths to determine why durable paper-trade lifecycle proof did not become visible.

Local evidence is historical diagnosis only; it does not override current GCP production authority. Findings must be converted into bounded repo/GCP remediation tasks.

## Human escalation

Set `HUMAN_ACTION_REQUIRED=YES` only for genuine human-only external actions such as billing/subscription/funding, identity/consent, an unavailable permission that no safe existing authority can solve, or explicit LIVE-trading approval. State alternatives already attempted and the exact minimum user action.

## Safety and authority

- GCP is authoritative production runtime.
- GitHub is authoritative code/configuration source.
- ANALYZE/PAPER only.
- `LIVE=false`, order placement disabled.
- No secret payload exposure.
- No blind broker token mint/rotation.
- No IAM/WIF weakening.
- No gate dilution or retry-until-green.
- No production PASS from source, docs, CI, API health, or `connected=true` alone.

For current task ownership and live state, always read the newest RHUI markers in Issue #188; this document defines the standing contract, not the current runtime snapshot.
