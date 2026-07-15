# System3 Windows Self-Hosted Full System Proof

Generated: `2026-07-15T00:07:12.490519Z`

Final status: **BLOCKED**

Safety: live trading OFF, analyzer mode ON, order routes not called.

Response bodies persisted: **false**.

## Status board

| Area | Status | Detail |
|---|---|---|
| C:\Python310\python.exe scripts/system3_gate_evaluator.py --sync-gates | PASS | rc=0 elapsed=2.13s |
| C:\Python310\python.exe tools/system3_auto_coordinator.py --full | PASS | rc=0 elapsed=160.56s |
| C:\Python310\python.exe tools/system3_github_render_failure_tracker.py | PASS | rc=0 elapsed=7.1s |
| C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs | BLOCKED | rc=1 elapsed=1.0s |
| C:\Python310\python.exe tools/system3_autopilot_proof_board.py | BLOCKED | rc=1 elapsed=0.21s |
| HTTP /api/health | BLOCKED | 502 |
| HTTP /api/state | BLOCKED | 502 |
| HTTP /api/status | BLOCKED | 502 |
| HTTP /api/broker/status | BLOCKED | 502 |
| HTTP /api/broker/dhan/status | BLOCKED | 502 |
| HTTP /api/broker/funds | BLOCKED | 502 |
| HTTP /api/broker/holdings | BLOCKED | 502 |
| HTTP /api/broker/positions | BLOCKED | 502 |
| HTTP /api/scanner/top_contract_gainers | BLOCKED | 502 |
| HTTP /api/simulation/live/state | BLOCKED | 502 |
| Report system3_auto_gates | UNKNOWN | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_auto_gates\summary.json |
| Report github_render_failure_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\github_render_failure_tracker\summary.json |
| Report dashboard_visible_issue_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\dashboard_visible_issue_tracker\summary.json |
| Report autopilot_proof_board | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_autopilot_proof_board\summary.json |
| Report safe_repair_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\safe_repair_runner\summary.json |
| Report market_session_proof_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\market_session_proof_runner\summary.json |

## Blockers

- Command blocked: C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs — DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=0 screenshots_missing=0 unsettled_tabs=0 exceptions=0 auth_ok=false tabs=0/16

- Command blocked: C:\Python310\python.exe tools/system3_autopilot_proof_board.py — 1
- HTTP blocked: /api/health — 502
- HTTP blocked: /api/state — 502
- HTTP blocked: /api/status — 502
- HTTP blocked: /api/broker/status — 502
- HTTP blocked: /api/broker/dhan/status — 502
- HTTP blocked: /api/broker/funds — 502
- HTTP blocked: /api/broker/holdings — 502
- HTTP blocked: /api/broker/positions — 502
- HTTP blocked: /api/scanner/top_contract_gainers — 502
- HTTP blocked: /api/simulation/live/state — 502
- Report not PASS: system3_auto_gates — UNKNOWN
- Report not PASS: github_render_failure_tracker — BLOCKED
- Report not PASS: dashboard_visible_issue_tracker — BLOCKED
- Report not PASS: autopilot_proof_board — MISSING
- Report not PASS: safe_repair_runner — MISSING
- Report not PASS: market_session_proof_runner — MISSING