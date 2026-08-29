# Cursor Permanent UI-Closure Rule

Status: ACTIVE Cursor operating contract. Does not weaken `docs/RUHI_RULE_V2.md`, LIVE locks, or Issue #188 one-write-lane.
Locked: 2026-08-22T10:54Z by owner instruction.
Gmail/chat is fallback only. Durable updates go to this file, the RUHI ledger, and Issue #188.

## Read first every tick

1. `docs/handoffs/CURSOR_TO_CHATGPT_PATH_INDEX.md`
2. `reports/coordination/ruhi_task_ledger.csv`
3. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md`
4. GitHub Issue #188

Then continuously execute the highest-priority unowned or Cursor-owned unblocked task. Do not stop at planning.

## Completion law

Backend/API/CI PASS alone is never completion.

For every user-visible feature compare, in order:

1. GCP runtime truth (exact serving SHA/revision)
2. Same-session API JSON
3. Frontend store/state
4. Rendered production `/ui`

Identify missing, stale, zero, hardcoded, error, or mismatched fields. Fix the narrow root cause. Test. PR. Deploy. Capture exact-serving-SHA browser evidence.

Do not claim `DONE` because a page rendered. UI evidence must match authoritative APIs semantically.

## Required audit surface

Canonical tabs:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

Audit each tab and all major states: loading, empty, error, closed-market, live-market.

Must include:

- broker
- NIFTY / BANKNIFTY / FINNIFTY / MIDCPNIFTY chains
- scanner / signals
- prediction / accuracy
- positions / PnL / risk
- scheduler / automation
- system health

## Market-phase honesty

During Indian market-closed periods, distinguish legitimate closed-market or stale last-session values from defects. Never manufacture live values. Never paint green over a truthful CLOSED/STALE/ERROR state.

## After every proof

Update `reports/coordination/ruhi_task_ledger.csv` and Issue #188 with:

- exact SHA / revision
- URL / tab
- API predicate
- screenshot / browser artifact
- PASS / FAIL
- blocker
- next owner

Then immediately claim the next unblocked item. Do not duplicate a lane another agent already owns.

## Human boundary

Ask Pritam only for genuinely human-only access/approval or a specific visual screenshot that agents cannot obtain. Otherwise keep executing.

## Safety

- `LIVE=false`
- orders disabled
- `ANALYZE` / `PAPER` only
- no live Scheduler / token / IAM mutation from this rule

## Current sequencing (2026-08-22)

1. Finish Cursor PR #321 / RUHI-022. Scope frozen. Merge only when Global Safety + Security Audit + CodeQL are green on the exact head.
2. One normal Cloud Run deploy. Prove `GET /api/scheduler/health?refresh=true` `healthy=true`.
3. Only if that still fails, inspect leftover `30 * * * *` in `scripts/gcp_runtime_identity_safety.py` and change nothing else.
4. Then continue tab-by-tab UI closure on the exact serving SHA (RUHI-007 / 008 / 017 / 018 and remaining canonical tabs).
