# Genesis System3 Autonomous End-to-End Runbook

**Authority marker:** `SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1`

**Current authority:** `docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md` and `AGENTS.md`. The 2026-09-01 Claude-only override is HISTORICAL_NON_AUTHORITY (`docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md`).

**Role:** Persistent self-instruction and completion ledger for every agent in this repository.

## Mandatory re-read boundary

Re-read this runbook and `AGENTS.md` from the current checked-out commit immediately before:

1. every merge decision;
2. every deployment or production mutation;
3. every production acceptance or rollback decision;
4. every issue/blocker closure;
5. every final response that claims completion, current state, or user action.

Chat memory, an earlier read, a prior agent summary, and `reports/latest/` do not
satisfy this boundary. Record the runbook path, marker, current Git SHA, and
re-read UTC time in the active completion ledger.

## Authority order

1. Latest explicit user instruction
2. Trading/secret/destructive safety
3. `AGENTS.md`
4. `docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md`
5. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
6. `agent_policy.yaml`
7. Scoped `.cursor/rules`

GCP Cloud Run, Claude-only ownership, and Issue #188 as a live bus do not
outrank the local-laptop directive.

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

## Local runtime cycle

Verify the symptom on `C:\Genesis_System3_Clean` and `http://127.0.0.1:8000`
(discover the bound port). Implement on a dedicated branch/worktree from
`origin/main`. Test. Prove local API/browser/safety. Do not deploy to Cloud Run
or run `gcloud`.

A completion claim requires fresh evidence from the local runtime. Code, PR, CI,
HTTP 200, rendered tabs, or historical screenshots alone are insufficient.
