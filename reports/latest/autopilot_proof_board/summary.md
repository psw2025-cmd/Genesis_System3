# System3 Autopilot Latest Status

Generated UTC: `2026-07-15T01:42:15.033297+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `171`

## Non-negotiable rules

- Manual screenshots from user are not required for proof.
- Backend, frontend, live dashboard UI, GitHub/Render health, workflow health, TODO status, and final truth must be proven by automation.
- Secrets are never printed or committed.
- Live trading remains OFF; no live order routes are called.
- Production-grade claim is allowed only when this board is PASS.

## Core gates

| Gate | Status |
|---|---:|
| render_visual | BLOCKED |
| github_render_health | BLOCKED |
| backend_frontend_install | BLOCKED |
| workflow_health | BLOCKED |
| root_cause_zero | BLOCKED |
| todo_zero | BLOCKED |
| public_truth_pass | BLOCKED |

## Source reports

| Report | Raw status | Gate status | Blockers |
|---|---|---|---:|
| secure_install_credential_audit | BLOCKED | BLOCKED | 6 |
| dashboard_visible_issue_tracker | BLOCKED | BLOCKED | 1 |
| github_render_failure_tracker | BLOCKED | BLOCKED | 103 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 37 |
| todo_status_update | BLOCKED | BLOCKED | 0 |
| dashboard_visual_production_proof | UNKNOWN | BLOCKED | 0 |
| system3_public_truth | FAIL | BLOCKED | 0 |

## Blockers

- [ ] secure_install_credential_audit: Required secret missing from workflow env: DASHBOARD_API_KEY
- [ ] secure_install_credential_audit: Required secret missing from workflow env: DHAN_CLIENT_ID
- [ ] secure_install_credential_audit: Required secret missing from workflow env: DHAN_ACCESS_TOKEN
- [ ] secure_install_credential_audit: Add/verify required secret in secure store: DASHBOARD_API_KEY
- [ ] secure_install_credential_audit: Add/verify required secret in secure store: DHAN_CLIENT_ID
- [ ] secure_install_credential_audit: Add/verify required secret in secure store: DHAN_ACCESS_TOKEN
- [ ] dashboard_visible_issue_tracker: Playwright/browser launch failed: Error: browserType.launch: Executable doesn't exist at /home/runner/.cache/ms-playwright/chromium_headless_shell-1148/chrome-linux/headless_shell
╔═════════════════════════════════════════════════════════════════════════╗
║ Looks like Playwright Test or Playwright w
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29382218286 conclusion=failure commit=9f30cf6b8050
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382218258 conclusion=failure commit=9f30cf6b8050
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29382214811 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29382214743 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29382214701 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382214700 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382212768 conclusion=cancelled commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382212760 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29382212519 conclusion=cancelled commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382212510 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382212507 conclusion=cancelled commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29382208434 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382208433 conclusion=failure commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29382208352 conclusion=cancelled commit=a15adeeec524
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382187118 conclusion=failure commit=ad2704fa44d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29382187107 conclusion=cancelled commit=ad2704fa44d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382187080 conclusion=cancelled commit=ad2704fa44d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29382174502 conclusion=failure commit=ad2704fa44d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382163090 conclusion=failure commit=81faa109d79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382163063 conclusion=cancelled commit=81faa109d79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29382162881 conclusion=failure commit=81faa109d79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29382158983 conclusion=failure commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29382158957 conclusion=failure commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382158954 conclusion=failure commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382156726 conclusion=cancelled commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29382156714 conclusion=cancelled commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382156713 conclusion=failure commit=30c96f18de3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29382146546 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29382146536 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382146519 conclusion=cancelled commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29382146515 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29382146514 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29382146512 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382146503 conclusion=failure commit=3548b373f9e6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29382144025 conclusion=failure commit=c7363d086cd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29382144015 conclusion=cancelled commit=c7363d086cd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29382143998 conclusion=cancelled commit=c7363d086cd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29382139978 conclusion=failure commit=c7363d086cd7
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/health: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 502 status=502
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/", "error_type": "TimeoutError", "reason": "HTTP status 0", "status_code": 0, "url": "https://genesis-system3-backend.onrender.com/"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/ui/", "error_type": "TimeoutError", "reason": "HTTP status 0", "status_code": 0, "url": "https://genesis-system3-backend.onrender.com/ui/"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/health", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/health"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/state", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/state"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/deploy/info", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/deploy/info"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/broker/diagnose", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/broker/diagnose"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/broker/funds", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/broker/funds"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/broker/holdings", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/broker/holdings"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/broker/positions/live", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/broker/positions
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/scanner/top_contract_gainers", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/scanner/t
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/paper", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/paper"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/api/ml/performance", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/api/ml/performance"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9f30cf6b8050db38650f9c55a54ecf5ee1c27c89", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382218286", "run_id": 29382218286, "updated_at": "2026-07-15T01:40:54Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9f30cf6b8050db38650f9c55a54ecf5ee1c27c89", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382218258", "run_id": 29382218258, "updated_at": "2026-07-15T01:40:45Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382214811", "run_id": 29382214811, "updated_at": "2026-07-15T01:41:02Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382214743", "run_id": 29382214743, "updated_at": "2026-07-15T01:40:39Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382214701", "run_id": 29382214701, "updated_at": "2026-07-15T01:40:39Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382214700", "run_id": 29382214700, "updated_at": "2026-07-15T01:40:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382212768", "run_id": 29382212768, "updated_at": "2026-07-15T01:40:32Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382212760", "run_id": 29382212760, "updated_at": "2026-07-15T01:40:40Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382212519", "run_id": 29382212519, "updated_at": "2026-07-15T01:40:30Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382212510", "run_id": 29382212510, "updated_at": "2026-07-15T01:40:37Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382212507", "run_id": 29382212507, "updated_at": "2026-07-15T01:40:30Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382208434", "run_id": 29382208434, "updated_at": "2026-07-15T01:40:42Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382208433", "run_id": 29382208433, "updated_at": "2026-07-15T01:40:36Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a15adeeec524948ee2dd8c17ed80737e93f9ee42", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382208352", "run_id": 29382208352, "updated_at": "2026-07-15T01:40:34Z", "workflow": "System3 1000 Point TODO Status Updater"
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "ad2704fa44d487e462f0e310c2289d21b9ba58a1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382187118", "run_id": 29382187118, "updated_at": "2026-07-15T01:40:01Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "ad2704fa44d487e462f0e310c2289d21b9ba58a1", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382187107", "run_id": 29382187107, "updated_at": "2026-07-15T01:40:29Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "ad2704fa44d487e462f0e310c2289d21b9ba58a1", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382187080", "run_id": 29382187080, "updated_at": "2026-07-15T01:40:44Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "ad2704fa44d487e462f0e310c2289d21b9ba58a1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382174502", "run_id": 29382174502, "updated_at": "2026-07-15T01:40:39Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "81faa109d79fb98d35203719d0119f04b82adb91", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382163090", "run_id": 29382163090, "updated_at": "2026-07-15T01:39:27Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "81faa109d79fb98d35203719d0119f04b82adb91", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382163063", "run_id": 29382163063, "updated_at": "2026-07-15T01:40:07Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "81faa109d79fb98d35203719d0119f04b82adb91", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382162881", "run_id": 29382162881, "updated_at": "2026-07-15T01:40:27Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382158983", "run_id": 29382158983, "updated_at": "2026-07-15T01:40:26Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382158957", "run_id": 29382158957, "updated_at": "2026-07-15T01:39:31Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382158954", "run_id": 29382158954, "updated_at": "2026-07-15T01:39:22Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382156726", "run_id": 29382156726, "updated_at": "2026-07-15T01:39:20Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382156714", "run_id": 29382156714, "updated_at": "2026-07-15T01:39:52Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "30c96f18de3d8acb850aa9556f58f4442f497bd2", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382156713", "run_id": 29382156713, "updated_at": "2026-07-15T01:39:18Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146546", "run_id": 29382146546, "updated_at": "2026-07-15T01:40:30Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146536", "run_id": 29382146536, "updated_at": "2026-07-15T01:39:02Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146519", "run_id": 29382146519, "updated_at": "2026-07-15T01:39:11Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146515", "run_id": 29382146515, "updated_at": "2026-07-15T01:39:49Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146514", "run_id": 29382146514, "updated_at": "2026-07-15T01:39:02Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146512", "run_id": 29382146512, "updated_at": "2026-07-15T01:39:15Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "3548b373f9e65c309b3b59e9dee736c94f265b40", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382146503", "run_id": 29382146503, "updated_at": "2026-07-15T01:39:07Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c7363d086cd7da0881e0f84a3d0222d601b2e3f3", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382144025", "run_id": 29382144025, "updated_at": "2026-07-15T01:39:03Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c7363d086cd7da0881e0f84a3d0222d601b2e3f3", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382144015", "run_id": 29382144015, "updated_at": "2026-07-15T01:38:55Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c7363d086cd7da0881e0f84a3d0222d601b2e3f3", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382143998", "run_id": 29382143998, "updated_at": "2026-07-15T01:39:09Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c7363d086cd7da0881e0f84a3d0222d601b2e3f3", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29382139978", "run_id": 29382139978, "updated_at": "2026-07-15T01:39:42Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: github_failed_count=38
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=50
- [ ] parallel_root_cause_audit: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- [ ] parallel_root_cause_audit: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.
- [ ] parallel_root_cause_audit: Public truth final verdict is FAIL.
- [ ] parallel_root_cause_audit: Need compare public truth commit with latest repository head and Render deploy info; static repo audit cannot prove Render freshness.
- [ ] parallel_root_cause_audit: Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.
- [ ] parallel_root_cause_audit: Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.
- [ ] parallel_root_cause_audit: Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.
- [ ] parallel_root_cause_audit: Trading router may be inactive if app.py duplicate routes are authoritative.
- [ ] parallel_root_cause_audit: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.
- [ ] parallel_root_cause_audit: Options ML training summary is missing/not published.
- [ ] parallel_root_cause_audit: Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.
- [ ] parallel_root_cause_audit: Need fresh screenshot after latest commits; older screenshots do not prove current UI.
- [ ] parallel_root_cause_audit: Final public truth is FAIL.
- [ ] parallel_root_cause_audit: Final truth must aggregate latest Render, integration, visual, broker, chain, scanner, paper, ML proof.
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29382224117 conclusion=failure commit=5db0ff6c16321446e506019de37640a48d449a92
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382218286 conclusion=failure commit=9f30cf6b8050db38650f9c55a54ecf5ee1c27c89
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382218258 conclusion=failure commit=9f30cf6b8050db38650f9c55a54ecf5ee1c27c89
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382214811 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29382214743 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29382214701 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382214700 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382212768 conclusion=cancelled commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382212760 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29382212519 conclusion=cancelled commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382212510 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382212507 conclusion=cancelled commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382208434 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382208433 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29382208352 conclusion=cancelled commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382187118 conclusion=failure commit=ad2704fa44d487e462f0e310c2289d21b9ba58a1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29382187107 conclusion=cancelled commit=ad2704fa44d487e462f0e310c2289d21b9ba58a1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382187080 conclusion=cancelled commit=ad2704fa44d487e462f0e310c2289d21b9ba58a1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29382174502 conclusion=failure commit=ad2704fa44d487e462f0e310c2289d21b9ba58a1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382163090 conclusion=failure commit=81faa109d79fb98d35203719d0119f04b82adb91
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382163063 conclusion=cancelled commit=81faa109d79fb98d35203719d0119f04b82adb91
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29382162881 conclusion=failure commit=81faa109d79fb98d35203719d0119f04b82adb91
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29382158983 conclusion=failure commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382158957 conclusion=failure commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382158954 conclusion=failure commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382156726 conclusion=cancelled commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29382156714 conclusion=cancelled commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382156713 conclusion=failure commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29382146546 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29382146536 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29382146519 conclusion=cancelled commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29382146515 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29382146514 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382146512 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382146503 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29382144025 conclusion=failure commit=c7363d086cd7da0881e0f84a3d0222d601b2e3f3
- [ ] workflow_failure_tracker: failed_count=36
- [ ] todo_status_update: status=BLOCKED
- [ ] dashboard_visual_production_proof: status=UNKNOWN
- [ ] system3_public_truth: status=FAIL
- [ ] core_gate_blocked:render_visual
- [ ] core_gate_blocked:github_render_health
- [ ] core_gate_blocked:backend_frontend_install
- [ ] core_gate_blocked:workflow_health
- [ ] core_gate_blocked:root_cause_zero
- [ ] core_gate_blocked:todo_zero
- [ ] core_gate_blocked:public_truth_pass
