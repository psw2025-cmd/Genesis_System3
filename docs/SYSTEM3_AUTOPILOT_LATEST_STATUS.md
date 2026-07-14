# System3 Autopilot Latest Status

Generated UTC: `2026-07-14T23:58:53.635949+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `176`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 105 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 40 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377646003 conclusion=failure commit=a44656523b33
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377645981 conclusion=failure commit=a44656523b33
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29377632307 conclusion=failure commit=bc835427da46
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377632295 conclusion=failure commit=bc835427da46
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377632270 conclusion=failure commit=bc835427da46
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29377632267 conclusion=failure commit=bc835427da46
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29377265203 conclusion=failure commit=2fee5353c98e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Settle Normalizer' run=29377250073 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29377250045 conclusion=cancelled commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377250037 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29377250029 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29377250025 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29377250011 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377250010 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29377249696 conclusion=cancelled commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377249658 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29377249652 conclusion=cancelled commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377247320 conclusion=failure commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29377247304 conclusion=cancelled commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29377247275 conclusion=cancelled commit=e1f2b117660f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377241900 conclusion=failure commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29377241885 conclusion=cancelled commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29377241880 conclusion=cancelled commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29377236094 conclusion=cancelled commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377236082 conclusion=failure commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377222386 conclusion=failure commit=e22770d15f3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377207452 conclusion=failure commit=1a455bb16de2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377206142 conclusion=failure commit=1a455bb16de2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377206113 conclusion=failure commit=1a455bb16de2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377206109 conclusion=failure commit=1a455bb16de2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377186822 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377186771 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377186751 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377184936 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29377184930 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29377184915 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377184568 conclusion=failure commit=01af35726339
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=29377175640 conclusion=failure commit=a0d6ecc5282b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29377164376 conclusion=failure commit=0588be4d3bd6
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 502 status=502
- [ ] github_render_failure_tracker: Fix Render endpoint /ui/: HTTP status 502 status=502
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
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/"}
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/ui/", "error_type": null, "reason": "HTTP status 502", "status_code": 502, "url": "https://genesis-system3-backend.onrender.com/ui/"}
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
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a44656523b338f4dd1e6a0cd908efeb351377021", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377646003", "run_id": 29377646003, "updated_at": "2026-07-14T23:57:56Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a44656523b338f4dd1e6a0cd908efeb351377021", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377645981", "run_id": 29377645981, "updated_at": "2026-07-14T23:57:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "bc835427da46bef132085d2792cecac888f41880", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377632307", "run_id": 29377632307, "updated_at": "2026-07-14T23:57:25Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "bc835427da46bef132085d2792cecac888f41880", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377632295", "run_id": 29377632295, "updated_at": "2026-07-14T23:57:37Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "bc835427da46bef132085d2792cecac888f41880", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377632270", "run_id": 29377632270, "updated_at": "2026-07-14T23:57:27Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "bc835427da46bef132085d2792cecac888f41880", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377632267", "run_id": 29377632267, "updated_at": "2026-07-14T23:57:25Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2fee5353c98e68b83ee505edf42bd96a26acbb0e", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377265203", "run_id": 29377265203, "updated_at": "2026-07-14T23:57:14Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250073", "run_id": 29377250073, "updated_at": "2026-07-14T23:49:25Z", "workflow": "Dashboard Visual Settle Normalizer"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250045", "run_id": 29377250045, "updated_at": "2026-07-14T23:57:50Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250037", "run_id": 29377250037, "updated_at": "2026-07-14T23:49:29Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250029", "run_id": 29377250029, "updated_at": "2026-07-14T23:49:17Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250025", "run_id": 29377250025, "updated_at": "2026-07-14T23:52:29Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250011", "run_id": 29377250011, "updated_at": "2026-07-14T23:49:16Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377250010", "run_id": 29377250010, "updated_at": "2026-07-14T23:49:18Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377249696", "run_id": 29377249696, "updated_at": "2026-07-14T23:49:25Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377249658", "run_id": 29377249658, "updated_at": "2026-07-14T23:49:15Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377249652", "run_id": 29377249652, "updated_at": "2026-07-14T23:49:07Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377247320", "run_id": 29377247320, "updated_at": "2026-07-14T23:49:14Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377247304", "run_id": 29377247304, "updated_at": "2026-07-14T23:49:07Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e1f2b117660fadb1e6c3718f16323a7960d9855b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377247275", "run_id": 29377247275, "updated_at": "2026-07-14T23:49:07Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377241900", "run_id": 29377241900, "updated_at": "2026-07-14T23:49:10Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377241885", "run_id": 29377241885, "updated_at": "2026-07-14T23:49:04Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377241880", "run_id": 29377241880, "updated_at": "2026-07-14T23:49:04Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377236094", "run_id": 29377236094, "updated_at": "2026-07-14T23:48:57Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377236082", "run_id": 29377236082, "updated_at": "2026-07-14T23:49:02Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e22770d15f3df1b3eaf23993791ba87f1e4afb7e", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377222386", "run_id": 29377222386, "updated_at": "2026-07-14T23:49:25Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "1a455bb16de20916dcd90e79eb3b5854e7b41e98", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377207452", "run_id": 29377207452, "updated_at": "2026-07-14T23:49:04Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "1a455bb16de20916dcd90e79eb3b5854e7b41e98", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377206142", "run_id": 29377206142, "updated_at": "2026-07-14T23:48:28Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "1a455bb16de20916dcd90e79eb3b5854e7b41e98", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377206113", "run_id": 29377206113, "updated_at": "2026-07-14T23:49:01Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "1a455bb16de20916dcd90e79eb3b5854e7b41e98", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377206109", "run_id": 29377206109, "updated_at": "2026-07-14T23:48:17Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377186822", "run_id": 29377186822, "updated_at": "2026-07-14T23:47:56Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377186771", "run_id": 29377186771, "updated_at": "2026-07-14T23:48:08Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377186751", "run_id": 29377186751, "updated_at": "2026-07-14T23:48:54Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377184936", "run_id": 29377184936, "updated_at": "2026-07-14T23:48:56Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377184930", "run_id": 29377184930, "updated_at": "2026-07-14T23:48:07Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377184915", "run_id": 29377184915, "updated_at": "2026-07-14T23:47:55Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "01af357263396abaf4909d33127a500c12361237", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377184568", "run_id": 29377184568, "updated_at": "2026-07-14T23:49:03Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "a0d6ecc5282b49d075ac9f8162350420c39026da", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377175640", "run_id": 29377175640, "updated_at": "2026-07-14T23:47:45Z", "workflow": "System3 Workflow Failure Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "0588be4d3bd60e333a9ebc8e0b6128dad4b288ab", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29377164376", "run_id": 29377164376, "updated_at": "2026-07-14T23:48:47Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: github_failed_count=39
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=51
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377646003 conclusion=failure commit=a44656523b338f4dd1e6a0cd908efeb351377021
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377645981 conclusion=failure commit=a44656523b338f4dd1e6a0cd908efeb351377021
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29377632307 conclusion=failure commit=bc835427da46bef132085d2792cecac888f41880
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377632295 conclusion=failure commit=bc835427da46bef132085d2792cecac888f41880
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377632270 conclusion=failure commit=bc835427da46bef132085d2792cecac888f41880
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29377632267 conclusion=failure commit=bc835427da46bef132085d2792cecac888f41880
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29377265203 conclusion=failure commit=2fee5353c98e68b83ee505edf42bd96a26acbb0e
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Settle Normalizer' run 29377250073 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29377250045 conclusion=cancelled commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377250037 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29377250029 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29377250025 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29377250011 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377250010 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29377249696 conclusion=cancelled commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377249658 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29377249652 conclusion=cancelled commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377247320 conclusion=failure commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29377247304 conclusion=cancelled commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29377247275 conclusion=cancelled commit=e1f2b117660fadb1e6c3718f16323a7960d9855b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377241900 conclusion=failure commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29377241885 conclusion=cancelled commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29377241880 conclusion=cancelled commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29377236094 conclusion=cancelled commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377236082 conclusion=failure commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377222386 conclusion=failure commit=e22770d15f3df1b3eaf23993791ba87f1e4afb7e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377207452 conclusion=failure commit=1a455bb16de20916dcd90e79eb3b5854e7b41e98
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377206142 conclusion=failure commit=1a455bb16de20916dcd90e79eb3b5854e7b41e98
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377206113 conclusion=failure commit=1a455bb16de20916dcd90e79eb3b5854e7b41e98
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377206109 conclusion=failure commit=1a455bb16de20916dcd90e79eb3b5854e7b41e98
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377186822 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377186771 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377186751 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377184936 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29377184930 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29377184915 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377184568 conclusion=failure commit=01af357263396abaf4909d33127a500c12361237
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 29377175640 conclusion=failure commit=a0d6ecc5282b49d075ac9f8162350420c39026da
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29377164376 conclusion=failure commit=0588be4d3bd60e333a9ebc8e0b6128dad4b288ab
- [ ] workflow_failure_tracker: failed_count=39
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
