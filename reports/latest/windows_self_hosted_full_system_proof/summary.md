# System3 Windows Self-Hosted Full System Proof

Generated: `2026-07-26T05:02:01.068904Z`

Final status: **BLOCKED**

Safety: live trading OFF, analyzer mode ON, order routes not called.

Response bodies persisted: **false**.

## Status board

| Area | Status | Detail |
|---|---|---|
| C:\Python310\python.exe scripts/system3_gate_evaluator.py --sync-gates | PASS | rc=0 elapsed=7.17s |
| C:\Python310\python.exe tools/system3_auto_coordinator.py --full | BLOCKED | timeout after 240s |
| C:\Python310\python.exe tools/system3_github_render_failure_tracker.py | PASS | rc=0 elapsed=28.93s |
| C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs | BLOCKED | rc=1 elapsed=2.25s |
| C:\Python310\python.exe tools/system3_autopilot_proof_board.py | BLOCKED | rc=1 elapsed=0.35s |
| HTTP /api/health | BLOCKED | network_error |
| HTTP /api/state | BLOCKED | network_error |
| HTTP /api/status | BLOCKED | network_error |
| HTTP /api/broker/status | BLOCKED | network_error |
| HTTP /api/broker/dhan/status | BLOCKED | network_error |
| HTTP /api/broker/funds | BLOCKED | network_error |
| HTTP /api/broker/holdings | BLOCKED | network_error |
| HTTP /api/broker/positions | BLOCKED | network_error |
| HTTP /api/scanner/top_contract_gainers | BLOCKED | network_error |
| HTTP /api/simulation/live/state | BLOCKED | network_error |
| Report system3_auto_gates | UNKNOWN | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_auto_gates\summary.json |
| Report github_render_failure_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\github_render_failure_tracker\summary.json |
| Report dashboard_visible_issue_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\dashboard_visible_issue_tracker\summary.json |
| Report autopilot_proof_board | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_autopilot_proof_board\summary.json |
| Report safe_repair_runner | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\safe_repair_runner\summary.json |
| Report market_session_proof_runner | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\market_session_proof_runner\summary.json |

## Blockers

- Command blocked: C:\Python310\python.exe tools/system3_auto_coordinator.py --full — timeout after 240s
- Command blocked: C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs — DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=0 screenshots_missing=0 unsettled_tabs=0 exceptions=0 auth_ok=false tabs=0/16

- Command blocked: C:\Python310\python.exe tools/system3_autopilot_proof_board.py — 1
- HTTP blocked: /api/health — network_error
- HTTP blocked: /api/state — network_error
- HTTP blocked: /api/status — network_error
- HTTP blocked: /api/broker/status — network_error
- HTTP blocked: /api/broker/dhan/status — network_error
- HTTP blocked: /api/broker/funds — network_error
- HTTP blocked: /api/broker/holdings — network_error
- HTTP blocked: /api/broker/positions — network_error
- HTTP blocked: /api/scanner/top_contract_gainers — network_error
- HTTP blocked: /api/simulation/live/state — network_error
- Report not PASS: system3_auto_gates — UNKNOWN
- Report not PASS: github_render_failure_tracker — BLOCKED
- Report not PASS: dashboard_visible_issue_tracker — BLOCKED
- Report not PASS: autopilot_proof_board — MISSING
- Report not PASS: safe_repair_runner — BLOCKED
- Report not PASS: market_session_proof_runner — BLOCKED