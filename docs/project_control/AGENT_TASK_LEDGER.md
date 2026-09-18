# Genesis System3 — Shared Agent Task Ledger

**Authority:** dynamic coordination file. Every active agent must read before work and update after each work batch. Detailed runtime evidence should also be appended to GitHub Issue #188.

**Do not treat this file as live truth by itself.** Every production claim must still be freshly revalidated per `AGENTS.md` and `docs/project_control/AGENT_COORDINATION_CENTER.md`.

## Current execution schedule

| Priority | Task | Owner | Status | Level | Dependency | Proof target | Next action |
|---|---|---|---|---|---|---|---|
| P0 | Refresh current `origin/main`, open PR ownership, Issue #188, mandatory CI and GCP serving SHA before any production action | NEXT AVAILABLE AGENT | TODO | L0 | None | Fresh preflight snapshot + exact SHAs | Run `scripts/system3_preflight_control_plane.py` and independently verify critical claims |
| P0 | Verify current production broker truth only against exact deployed Cloud Run revision | NEXT AVAILABLE AGENT | TODO | L0 | Fresh preflight | Exact serving SHA + fresh broker/API evidence | Recheck PR #313/current replacement and production state; do not assume old PR status |
| P0 | Fresh 22-tab production semantic UI proof with API↔UI parity | NEXT AVAILABLE NON-CONFLICTING AGENT | TODO | L0 | Exact deployed SHA known | New browser evidence from production URL | Use `scripts/gcp_live_ui_snapshot.py`; capture source/freshness/population/defects |
| P0 | Continue Issue #188 supported-universe coverage closure: NSE/BSE cash, indices, derivatives, option chains, discovery, quotes, candles, WS | NEXT AVAILABLE DATA LANE AGENT | TODO | L0 | Current broker/API state | Expected/backend/UI counts + missing set + source/freshness | Pick highest-impact missing category and trace first divergence end-to-end |
| P0 | Cross-agent ownership check before edits so no duplicate/conflicting work | EVERY AGENT | TODO | L0 | None | Current PR/Issue ownership map | Claim lane in this ledger / Issue #188 before editing |
| P1 | Recheck Cloud Agent environment PR #314/current replacement and avoid duplicate environment work | NEXT AVAILABLE AGENT | TODO | L0 | Current PR state | Current PR status/checks | Reuse existing environment if healthy; do not rebuild unnecessarily |
| P1 | Recheck scheduler-health diagnostic PR #286/current replacement | NEXT AVAILABLE AGENT | TODO | L0 | Current PR state | Current exact-head CI + changed-line review | Continue only if still active and unowned |
| P1 | Recheck Actions storage forensic PR #291/current replacement | NEXT AVAILABLE AGENT | TODO | L0 | Current PR state | Current exact-head CI | Continue only if non-conflicting with P0 work |
| P1 | Recheck Codex/RUHI guide PR #304/current replacement | NEXT AVAILABLE AGENT | TODO | L0 | Current PR state | Current merge/state evidence | Do not duplicate if already merged/superseded |

## Active ownership / claims

Agents must add or update one row before editing.

| Lane | Agent | Branch / PR | Files / surface | Claimed at UTC | Status | Handoff |
|---|---|---|---|---|---|---|
| NONE YET | — | — | — | — | TODO | First active agent refreshes current state and claims a lane |

## Completed this batch

| Task | Owner | Result | Level reached | Exact proof | Live UI proof | Timestamp UTC |
|---|---|---|---|---|---|---|
| Shared coordination center created | ChatGPT | Permanent coordination rules and shared ledger prepared on coordination branch | L2 | Branch `docs/central-agent-coordination-20260822` | N/A | 2026-08-22 |

## Waiting

| Task | Waiting on | Safe parallel work to continue | Owner | Recheck trigger |
|---|---|---|---|---|
| None recorded yet | — | — | — | — |

## Blocked external / user action

| Blocker | Why agent cannot resolve | Required user action | Owner | Evidence |
|---|---|---|---|---|
| None | — | NONE | — | — |

## Next queue

Maintain the next highest-value concrete actions here, ordered P0→P1→P2. Do not add vague items.

1. Refresh current main / PR / Issue #188 / workflow / GCP state.
2. Establish exact production serving SHA vs current `origin/main`.
3. Verify broker/API truth from current production revision.
4. Create new semantic production UI proof from a browser session started after the current investigation begins.
5. Compare backend/API vs UI for the highest-impact Issue #188 category.
6. Trace the first verified divergence to root cause.
7. Claim a non-conflicting implementation lane.
8. Implement the smallest durable fix where authorized.
9. Add focused regression/adversarial tests.
10. Run focused tests before broad CI.
11. Run required exact-head CI.
12. Merge per repository governance when gates are green.
13. Verify exact SHA deployment.
14. Capture fresh same-session API evidence.
15. Capture fresh production UI evidence.
16. Update Issue #188 with exact proof and blocker micro-details.
17. Update this ledger with achieved level/status.
18. If waiting on CI/deploy, immediately take the next non-conflicting task.
19. Continue supported-universe coverage closure.
20. Keep LIVE/order safety locks unchanged.

## Mandatory row format for every active task

`ID | PRIOR_COMMITMENT | OWNER | STATUS | LEVEL | DEPENDENCY | ACTION_TAKEN | PROOF | LIVE_UI_PROOF | BLOCKER | NEXT_ACTION | TARGET_PR`

## Default user-facing summary format

Agents should keep detailed evidence here / Issue #188 and send the user only:

### SCHEDULED / RUNNING
- ...

### NEXT
- ...

### PENDING / BLOCKED
- ...

### USER ACTION
- `NONE` unless genuine user-only action exists.
