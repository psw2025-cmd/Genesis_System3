# Genesis System3 — Agent Constitution

**Canonical checkout:** `C:\Genesis_System3_Clean`  
**Upstream code:** GitHub `psw2025-cmd/Genesis_System3` (`origin/main`)  
**Runtime and acceptance:** local Windows laptop at `http://127.0.0.1:8000` (discover the bound port; do not assume a document).  
**Machine policy:** `agent_policy.yaml` (schema v6)  
**Temporal marker:** `SYSTEM3_TEMPORAL_TRUTH_V1` — `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`  
**Broker:** Dhan. Angel and Render hosting are retired and non-authoritative.

This file is the short universal constitution. Domain rules live under `.cursor/rules/00`–`60`. Do not duplicate them here.

## Instruction precedence

1. Latest explicit user instruction.
2. Permanent trading, secret, and destructive-operation safety.
3. This `AGENTS.md`.
4. Applicable scoped `.cursor/rules/*.mdc` files.
5. Current control-plane documents under `docs/control_plane/`.
6. Current source, tests, and fresh local runtime evidence.
7. Historical reports, snapshots, Issue #188, Cloud Run URLs, and old agent output as context only.

If two instructions conflict, stop only the conflicting action. Continue other safe work.

`docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md` supersedes active GCP/Cloud Run/Claude-only/Issue-#188-bus/GitOps-deploy clauses.

## Safety (non-negotiable)

```
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
AUTO_EXECUTE_TRADES=0
SYSTEM3_MODE=analyze
```

PAPER/ANALYZER only. Never enable LIVE, never place/modify/cancel/square-off a real Dhan order, never print secrets, never weaken gates to manufacture PASS. Prove `place_order_calls=0` via blocked adapters and mocks. Do not send order-shaped traffic to a real broker order endpoint.

## Mutation boundaries

- Do not `git reset --hard`, `git clean`, `git restore .`, stash, rebase --autostash, or force-push.
- Dirty-worktree files in the canonical checkout are protected. Task work happens on a dedicated branch/worktree from `origin/main`.
- No single named AI is sole controller. Concurrent agents must not overwrite unrelated work.
- Issue #188 is historical coordination context, not a mandatory bus.
- GCP/Cloud Run/Render are retired as runtime, token, storage, scheduler, monitoring, and acceptance authority. Do not run `gcloud`, deploy Cloud Run, or mint tokens through GCP.
- GitHub `main` is the upstream code baseline. It is not local-runtime truth.

## Evidence

Current claims (`now` / `live` / `UI now`) require a new observation after a recorded UTC start: local browser + same-session local API. `reports/latest/` is historical. HTTP 200 and a screenshot are not semantic PASS. `connected=true` is not market-data PASS.

Statuses: `PASS` `FAIL` `BLOCKED` `UNKNOWN` `PARTIAL` `NOT_PROVEN` `NOT_APPLICABLE` `HISTORICAL_ONLY`.

## Product lock (one copy)

Local-laptop, evidence-driven, AI-assisted Indian-market intelligence: authentic data, instrument identity, options intelligence (six indices + dynamic equity CE/PE), PAPER only, prediction-to-outcome lineage, multibagger equity research with uncertainty, local scheduling, dashboard proof, tests. No guaranteed profit. No fabricated readiness. Detail: `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`.

## Completion

Do not stop at analysis, a plan, a commit, a PR, or CI green. Completion requires local API/browser/data/safety proof for the claimed scope, plus an honest residual list.

Every material update states: `STATUS`, `IN_PROGRESS`, `CURRENT_STEP`, `NEXT_ACTION`, `MANDATORY_USER_ACTION`, `OPTIONAL_ACCELERATION_ACTION`.
