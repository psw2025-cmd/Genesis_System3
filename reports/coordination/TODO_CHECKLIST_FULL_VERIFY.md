# TODO_CHECKLIST_FULL_VERIFY

**Updated UTC:** `2026-08-26T19:35:00Z`
**Evidence:** `reports/latest/full_cross_verify_20260826_193000/`
**main:** `0d6955987115f88b710aca0f0f0dec68d23fa6bc` · **serving:** `fb4772f9d52b67a31b55ee85aab8604e525bbad6` · **class:** DOCS/TEST/CI_ONLY_LAG

| ID | Pri | Rating | Status | Owner | Title | Proof |
|---|---|---|---|---|---|---|
| TV-001 | P0 | 1 | **DONE** | AGENT | Truth gate: origin/main vs live deploy_info vs laptop | `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` |
| TV-002 | P0 | 1 | **DONE** | AGENT | Live API dump (deploy/broker/health/state/scheduler/auto_gates) | `reports/latest/full_cross_verify_20260826_193000/` |
| TV-003 | P0 | 1 | **DONE** | AGENT | ACCESS_PROBE capability | `reports/latest/access_capability/ACCESS_PROBE_RESULT.md` |
| TV-004 | P0 | 1 | **DONE** | AGENT | Gmail System3 thread intake (14d) | `reports/latest/full_cross_verify_20260826_193000/gmail_system3_threads.json` |
| TV-005 | P0 | 1 | **DONE** | AGENT | Restore ruleset 21581518 6th check: BLOCKING - priority workflows only | `reports/latest/full_cross_verify_20260826_193000/ruleset_21581518.json` |
| TV-006 | P0 | 2 | **DONE** | AGENT | Refresh coordination CSVs/runbook/RUHI/COMMAND_CENTER/TRACKING | `reports/coordination/` |
| TV-007 | P0 | 1 | **PENDING** | AGENT | Post #188 SYSTEM3_COORDINATION_V1 + FULL_VERIFY_REPORT | `reports/latest/full_cross_verify_20260826_193000/FULL_VERIFY_REPORT.md` |
| TV-008 | P0 | 1 | **PENDING** | AGENT | RHUI V2.2 overall acceptance | `reports/coordination/RHUI_V2.2_GATE_BOARD.csv` |
| TV-009 | P0 | 2 | **PENDING** | AGENT | Scheduler HEALTHY + business artifact dates (rank/forecast/signals) | `reports/latest/full_cross_verify_20260826_193000/scheduler_health.json` |
| TV-010 | P0 | 2 | **DONE** | AGENT | Bhavcopy / signals lane hardening observe (#367 on serving) | `signals-daily last_attempt 2026-08-26T13:15Z; prior 92lf5 SUCCEEDED` |
| TV-011 | P0 | 2 | **PENDING** | AGENT | Forecast / rank business artifacts current-date | `reports/latest/full_cross_verify_20260826_193000/scheduler_health.json` |
| TV-012 | P0 | 1 | **PENDING** | AGENT | 22-tab semantic API↔UI proof on exact serving SHA | `reports/latest/live_proof_center/LATEST/` |
| TV-013 | P0 | 1 | **PENDING** | AGENT | #188 Broker/UI parity (chain columns LTP%/Buildup/OI%/Greeks/ATM) | `Issue #188 OPEN; local OptionChain dirty not on serving` |
| TV-014 | P0 | 2 | **PENDING** | AGENT | Auto gates 7/7 trade_ready | `reports/latest/full_cross_verify_20260826_193000/auto_gates.json` |
| TV-015 | P0 | 3 | **BLOCKED** | AGENT | Workflow Priority Guard FORENSIC rate-limit failures on main | `https://github.com/psw2025-cmd/Genesis_System3/actions/runs/33005422907` |
| TV-016 | P1 | 3 | **DONE** | AGENT | Open P0 issues board (#179,#187,#228,#166,#168,#44…) | `gh issue list P0 + open issues JSON in session` |
| TV-017 | P1 | 4 | **DONE** | AGENT | Do not blind-redeploy for docs tip | `reports/latest/repo_path_audit/cloud_github_vs_laptop.json` |
| TV-018 | P1 | 3 | **PENDING** | AGENT | API 404 honesty: charts/predictions/multibagger/paper/trades | `live HTTP 404 snapshot this session` |
| TV-019 | P2 | 4 | **PENDING** | HUMAN | Stale open docs PRs backlog (#353 governance pack, #335 semantic, …) | `gh pr list open` |
| TV-020 | P1 | 3 | **PENDING** | HUMAN | HUMAN optional: Cursor GitHub App / agent PAT re-auth | `reports/coordination/AGENT_ACCESS_REQUESTS.md (if present)` |

**Counts:** DONE=9 PENDING=10 BLOCKED=1

## Notes

- Rating 1=critical for HUMAN attention … 5=nice.
- Mark DONE only with proof paths/URLs.
- RHUI ACCEPTED forbidden until gate board green.

### TV-001 — Truth gate: origin/main vs live deploy_info vs laptop
- status/owner: **DONE** / AGENT
- notes: main=0d6955987115 serving=fb4772f9d52b class=DOCS_TEST_CI_ONLY_LAG primary_clone_ok

### TV-002 — Live API dump (deploy/broker/health/state/scheduler/auto_gates)
- status/owner: **DONE** / AGENT
- notes: All HTTP 200; broker AUTH_OK; LIVE=false; gates 2/7

### TV-003 — ACCESS_PROBE capability
- status/owner: **DONE** / AGENT
- notes: HAVE gmail_api/gh/gcloud/live; MISSING none

### TV-004 — Gmail System3 thread intake (14d)
- status/owner: **DONE** / AGENT
- notes: 25 msgs; ChatGPT+human: Priority Guard ruleset missing; Actions fail mails

### TV-005 — Restore ruleset 21581518 6th check: BLOCKING - priority workflows only
- status/owner: **DONE** / AGENT
- notes: PUT succeeded 2026-08-27T01:08 IST; was HUMAN_ACTION from Gmail/#188

### TV-006 — Refresh coordination CSVs/runbook/RUHI/COMMAND_CENTER/TRACKING
- status/owner: **DONE** / AGENT
- notes: This PR; land on main via docs PR

### TV-007 — Post #188 SYSTEM3_COORDINATION_V1 + FULL_VERIFY_REPORT
- status/owner: **PENDING** / AGENT
- notes: After PR push; then comment #188

### TV-008 — RHUI V2.2 overall acceptance
- status/owner: **PENDING** / AGENT
- notes: NOT_ACCEPTED: semantic UI + ML gates + business artifact dates

### TV-009 — Scheduler HEALTHY + business artifact dates (rank/forecast/signals)
- status/owner: **PENDING** / AGENT
- notes: transport HEALTHY; business_readiness=PARTIAL wrong-date artifacts

### TV-010 — Bhavcopy / signals lane hardening observe (#367 on serving)
- status/owner: **DONE** / AGENT
- notes: Code on serving; next weekday runs continue; no redeploy needed

### TV-011 — Forecast / rank business artifacts current-date
- status/owner: **PENDING** / AGENT
- notes: forecast-daily last 04:00Z; rank 03:45Z; wrong-date flags

### TV-012 — 22-tab semantic API↔UI proof on exact serving SHA
- status/owner: **PENDING** / AGENT
- notes: HTTP mounts ≠ semantic PASS; market closed now

### TV-013 — #188 Broker/UI parity (chain columns LTP%/Buildup/OI%/Greeks/ATM)
- status/owner: **PENDING** / AGENT
- notes: DONE only after runtime merge + serving re-snap

### TV-014 — Auto gates 7/7 trade_ready
- status/owner: **PENDING** / AGENT
- notes: 2/7 pass (MODEL_ACCURACY + EQUITY_FO); LIVE stays OFF

### TV-015 — Workflow Priority Guard FORENSIC rate-limit failures on main
- status/owner: **BLOCKED** / AGENT
- notes: GitHub Actions installation API 403 rate limit — not code; cool-down

### TV-016 — Open P0 issues board (#179,#187,#228,#166,#168,#44…)
- status/owner: **DONE** / AGENT
- notes: #179 Render hardened via #365; #188 primary active; #44 legacy Render

### TV-017 — Do not blind-redeploy for docs tip
- status/owner: **DONE** / AGENT
- notes: Explicitly skipped Auto Deploy; serving stays #367

### TV-018 — API 404 honesty: charts/predictions/multibagger/paper/trades
- status/owner: **PENDING** / AGENT
- notes: holdings/funds 200; charts/predictions/multibagger/paper/trades 404

### TV-019 — Stale open docs PRs backlog (#353 governance pack, #335 semantic, …)
- status/owner: **PENDING** / HUMAN
- notes: #353 CI mostly green but CodeQL check fail name; triage separately

### TV-020 — HUMAN optional: Cursor GitHub App / agent PAT re-auth
- status/owner: **PENDING** / HUMAN
- notes: Not blocking this loop; Priority Guard ruleset fixed by agent

