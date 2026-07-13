# System3 Windows Self-Hosted Full System Proof

Generated: `2026-07-13T13:53:55.707469Z`

Final status: **BLOCKED**

Safety: live trading OFF, analyzer mode ON, order routes not called.

Response bodies persisted: **false**.

## Status board

| Area | Status | Detail |
|---|---|---|
| C:\Python310\python.exe scripts/system3_gate_evaluator.py --sync-gates | PASS | rc=0 elapsed=3.33s |
| C:\Python310\python.exe tools/system3_auto_coordinator.py --full | BLOCKED | timeout after 240s |
| C:\Python310\python.exe tools/system3_github_render_failure_tracker.py | PASS | rc=0 elapsed=8.23s |
| C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs | BLOCKED | rc=1 elapsed=0.09s |
| C:\Python310\python.exe tools/system3_autopilot_proof_board.py | BLOCKED | rc=1 elapsed=0.28s |
| HTTP /api/health | PASS | 200 |
| HTTP /api/state | PASS | 200 |
| HTTP /api/status | PASS | 200 |
| HTTP /api/broker/status | PASS | 200 |
| HTTP /api/broker/dhan/status | PASS | 200 |
| HTTP /api/broker/funds | PASS | 200 |
| HTTP /api/broker/holdings | PASS | 200 |
| HTTP /api/broker/positions | BLOCKED | 404 |
| HTTP /api/scanner/top_contract_gainers | BLOCKED | request_timeout |
| HTTP /api/simulation/live/state | BLOCKED | 502 |
| Report system3_auto_gates | UNKNOWN | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_auto_gates\summary.json |
| Report github_render_failure_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\github_render_failure_tracker\summary.json |
| Report dashboard_visible_issue_tracker | BLOCKED | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\dashboard_visible_issue_tracker\summary.json |
| Report autopilot_proof_board | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\system3_autopilot_proof_board\summary.json |
| Report safe_repair_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\safe_repair_runner\summary.json |
| Report market_session_proof_runner | MISSING | C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\reports\latest\market_session_proof_runner\summary.json |

## Blockers

- Command blocked: C:\Python310\python.exe tools/system3_auto_coordinator.py --full — timeout after 240s
- Command blocked: C:\Python310\python.exe tools/dashboard_visible_issue_tracker.mjs — node:internal/modules/package_json_reader:316
  throw new ERR_MODULE_NOT_FOUND(packageName, fileURLToPath(base), null);
        ^

Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'playwright' imported from C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3\tools\dashboard_visible_issue_tracker.mjs
    at Object.getPackageJSONURL (node:internal/modules/package_json_reader:316:9)
    at packageResolve (node:internal/modules/esm/resolve:768:81)
    at moduleResolve (node:internal/modules/esm/resolve:858:18)
    at defaultResolve (node:internal/modules/esm/resolve:990:11)
    at #cachedDefaultResolve (node:internal/modules/esm/loader:712:20)
    at #resolveAndMaybeBlockOnLoaderThread (node:internal/modules/esm/loader:729:38)
    at ModuleLoader.resolveSync (node:internal/modules/esm/loader:758:52)
    at #resolve (node:internal/modules/esm/loader:694:17)
    at ModuleLoader.getOrCreateModuleJob (node:internal/modules/esm/loader:614:35)
    at ModuleJob.syncLink (node:internal/modules/esm/module_job:143:33) {
  code: 'ERR_MODULE_NOT_FOUND'
}

Node.js v25.2.1

- Command blocked: C:\Python310\python.exe tools/system3_autopilot_proof_board.py — 1
- HTTP blocked: /api/broker/positions — 404
- HTTP blocked: /api/scanner/top_contract_gainers — request_timeout
- HTTP blocked: /api/simulation/live/state — 502
- Report not PASS: system3_auto_gates — UNKNOWN
- Report not PASS: github_render_failure_tracker — BLOCKED
- Report not PASS: dashboard_visible_issue_tracker — BLOCKED
- Report not PASS: autopilot_proof_board — MISSING
- Report not PASS: safe_repair_runner — MISSING
- Report not PASS: market_session_proof_runner — MISSING