# System3 Windows Self-Hosted Full System Proof

Generated: `2026-07-14T23:10:24.920008Z`

Final status: **BLOCKED**

Safety: live trading OFF, analyzer mode ON, order routes not called.

Response bodies persisted: **false**.

## Status board

| Area | Status | Detail |
|---|---|---|
| C:\Python310\python.exe scripts/system3_gate_evaluator.py --sync-gates | PASS | rc=0 elapsed=2.45s |
| C:\Python310\python.exe tools/system3_auto_coordinator.py --full | PASS | rc=0 elapsed=166.19s |
| C:\Python310\python.exe tools/system3_github_render_failure_tracker.py | PASS | rc=0 elapsed=5.31s |
| C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs | BLOCKED | rc=1 elapsed=1.02s |
| C:\Python310\python.exe tools/system3_autopilot_proof_board.py | BLOCKED | rc=1 elapsed=0.19s |
| HTTP /api/health | PASS | 200 |
| HTTP /api/state | PASS | 200 |
| HTTP /api/status | PASS | 200 |
| HTTP /api/broker/status | PASS | 200 |
| HTTP /api/broker/dhan/status | PASS | 200 |
| HTTP /api/broker/funds | PASS | 200 |
| HTTP /api/broker/holdings | PASS | 200 |
| HTTP /api/broker/positions | BLOCKED | 404 |
| HTTP /api/scanner/top_contract_gainers | PASS | 200 |
| HTTP /api/simulation/live/state | BLOCKED | 404 |
| Report system3_auto_gates | UNKNOWN | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_auto_gates\summary.json |
| Report github_render_failure_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\github_render_failure_tracker\summary.json |
| Report dashboard_visible_issue_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\dashboard_visible_issue_tracker\summary.json |
| Report autopilot_proof_board | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_autopilot_proof_board\summary.json |
| Report safe_repair_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\safe_repair_runner\summary.json |
| Report market_session_proof_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\market_session_proof_runner\summary.json |

## Blockers

- Command blocked: C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs — DASHBOARD_VISIBLE_ISSUES_BLOCKED issues=0 screenshots_missing=0 unsettled_tabs=0 exceptions=0 auth_ok=false tabs=0/16

- Command blocked: C:\Python310\python.exe tools/system3_autopilot_proof_board.py — 1
- HTTP blocked: /api/broker/positions — 404
- HTTP blocked: /api/simulation/live/state — 404
- Report not PASS: system3_auto_gates — UNKNOWN
- Report not PASS: github_render_failure_tracker — BLOCKED
- Report not PASS: dashboard_visible_issue_tracker — BLOCKED
- Report not PASS: autopilot_proof_board — MISSING
- Report not PASS: safe_repair_runner — MISSING
- Report not PASS: market_session_proof_runner — MISSING