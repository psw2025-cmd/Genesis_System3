# System3 Autopilot Latest Status

Generated UTC: `2026-07-14T14:47:48.991493+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `182`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 109 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 42 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29342344317 conclusion=failure commit=b1a805188991
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29342344294 conclusion=failure commit=b1a805188991
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29342323985 conclusion=failure commit=2c9c362d89ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29342323165 conclusion=failure commit=2c9c362d89ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29342322396 conclusion=failure commit=2c9c362d89ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29342322324 conclusion=failure commit=2c9c362d89ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29342321899 conclusion=failure commit=2c9c362d89ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341777886 conclusion=failure commit=2b4f436be987
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341729493 conclusion=cancelled commit=601121812dd9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341729168 conclusion=cancelled commit=601121812dd9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341727786 conclusion=failure commit=601121812dd9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341694079 conclusion=cancelled commit=96f470803f75
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341693729 conclusion=cancelled commit=96f470803f75
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341693622 conclusion=failure commit=96f470803f75
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341688417 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29341687410 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29341686864 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341686783 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29341686662 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29341686463 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29341686416 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29341686387 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29341686331 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29341686271 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29341686261 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341686110 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341685973 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29341685785 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341682224 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341682175 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341680818 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341679527 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341679065 conclusion=cancelled commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341678723 conclusion=failure commit=324666714baa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29341657549 conclusion=failure commit=0d0ff11739f8
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29341654232 conclusion=failure commit=75e727d313df
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341654119 conclusion=cancelled commit=75e727d313df
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29341653977 conclusion=cancelled commit=75e727d313df
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29341634831 conclusion=failure commit=75e727d313df
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29341634188 conclusion=failure commit=75e727d313df
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29341634074 conclusion=cancelled commit=75e727d313df
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 0 status=0
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
- [ ] github_render_failure_tracker: {"classification": {"mentions_auth_error": false, "mentions_commit_or_sha": false, "mentions_server_error": false}, "endpoint": "/", "error_type": "TimeoutError", "reason": "HTTP status 0", "status_code": 0, "url": "https://genesis-system3-backend.onrender.com/"}
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
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "b1a805188991ebb65313770511f34a9080fdde37", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342344317", "run_id": 29342344317, "updated_at": "2026-07-14T14:46:38Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "b1a805188991ebb65313770511f34a9080fdde37", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342344294", "run_id": 29342344294, "updated_at": "2026-07-14T14:46:27Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342323985", "run_id": 29342323985, "updated_at": "2026-07-14T14:46:23Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342323165", "run_id": 29342323165, "updated_at": "2026-07-14T14:46:10Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342322396", "run_id": 29342322396, "updated_at": "2026-07-14T14:46:08Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342322324", "run_id": 29342322324, "updated_at": "2026-07-14T14:46:10Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29342321899", "run_id": 29342321899, "updated_at": "2026-07-14T14:46:14Z", "workflow": "System3 1000 Point TODO Status Updater"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "2b4f436be987d1109ebc5c415712b500f2d91c64", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341777886", "run_id": 29341777886, "updated_at": "2026-07-14T14:45:55Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "601121812dd9fe4823d6f2ee3dbdb8e6dd759468", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341729493", "run_id": 29341729493, "updated_at": "2026-07-14T14:38:49Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "601121812dd9fe4823d6f2ee3dbdb8e6dd759468", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341729168", "run_id": 29341729168, "updated_at": "2026-07-14T14:46:32Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "601121812dd9fe4823d6f2ee3dbdb8e6dd759468", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341727786", "run_id": 29341727786, "updated_at": "2026-07-14T14:38:20Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "96f470803f75b5cf71868abe2efaa27c4c0826c8", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341694079", "run_id": 29341694079, "updated_at": "2026-07-14T14:38:09Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "96f470803f75b5cf71868abe2efaa27c4c0826c8", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341693729", "run_id": 29341693729, "updated_at": "2026-07-14T14:38:26Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "96f470803f75b5cf71868abe2efaa27c4c0826c8", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341693622", "run_id": 29341693622, "updated_at": "2026-07-14T14:37:52Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341688417", "run_id": 29341688417, "updated_at": "2026-07-14T14:37:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341687410", "run_id": 29341687410, "updated_at": "2026-07-14T14:39:43Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686864", "run_id": 29341686864, "updated_at": "2026-07-14T14:37:55Z", "workflow": "System3 1000 Point TODO Status Updater"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686783", "run_id": 29341686783, "updated_at": "2026-07-14T14:37:40Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686662", "run_id": 29341686662, "updated_at": "2026-07-14T14:37:45Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686463", "run_id": 29341686463, "updated_at": "2026-07-14T14:37:35Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686416", "run_id": 29341686416, "updated_at": "2026-07-14T14:37:36Z", "workflow": "System3 1000 Point TODO Status Updater"
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686387", "run_id": 29341686387, "updated_at": "2026-07-14T14:37:47Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686331", "run_id": 29341686331, "updated_at": "2026-07-14T14:37:46Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686271", "run_id": 29341686271, "updated_at": "2026-07-14T14:37:54Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686261", "run_id": 29341686261, "updated_at": "2026-07-14T14:37:47Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341686110", "run_id": 29341686110, "updated_at": "2026-07-14T14:37:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341685973", "run_id": 29341685973, "updated_at": "2026-07-14T14:37:35Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341685785", "run_id": 29341685785, "updated_at": "2026-07-14T14:37:51Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341682224", "run_id": 29341682224, "updated_at": "2026-07-14T14:37:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341682175", "run_id": 29341682175, "updated_at": "2026-07-14T14:37:34Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341680818", "run_id": 29341680818, "updated_at": "2026-07-14T14:37:40Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341679527", "run_id": 29341679527, "updated_at": "2026-07-14T14:37:31Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341679065", "run_id": 29341679065, "updated_at": "2026-07-14T14:37:30Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "324666714baaddf75d46caece8c884e18d6b8bd9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341678723", "run_id": 29341678723, "updated_at": "2026-07-14T14:37:40Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "0d0ff11739f8bc6a4d34c606f5ff203f4dc8b643", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341657549", "run_id": 29341657549, "updated_at": "2026-07-14T14:38:12Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341654232", "run_id": 29341654232, "updated_at": "2026-07-14T14:37:16Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341654119", "run_id": 29341654119, "updated_at": "2026-07-14T14:37:44Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341653977", "run_id": 29341653977, "updated_at": "2026-07-14T14:37:29Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341634831", "run_id": 29341634831, "updated_at": "2026-07-14T14:37:02Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341634188", "run_id": 29341634188, "updated_at": "2026-07-14T14:37:00Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "75e727d313df2c76712d9b40f65a924175fc6d8b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29341634074", "run_id": 29341634074, "updated_at": "2026-07-14T14:37:12Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: github_failed_count=41
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=53
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29342344317 conclusion=failure commit=b1a805188991ebb65313770511f34a9080fdde37
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29342344294 conclusion=failure commit=b1a805188991ebb65313770511f34a9080fdde37
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29342323985 conclusion=failure commit=2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29342323165 conclusion=failure commit=2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29342322396 conclusion=failure commit=2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29342322324 conclusion=failure commit=2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29342321899 conclusion=failure commit=2c9c362d89ad46e5e8d4aaf39ed79a69c6903cc9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341777886 conclusion=failure commit=2b4f436be987d1109ebc5c415712b500f2d91c64
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341729493 conclusion=cancelled commit=601121812dd9fe4823d6f2ee3dbdb8e6dd759468
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341729168 conclusion=cancelled commit=601121812dd9fe4823d6f2ee3dbdb8e6dd759468
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341727786 conclusion=failure commit=601121812dd9fe4823d6f2ee3dbdb8e6dd759468
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341694079 conclusion=cancelled commit=96f470803f75b5cf71868abe2efaa27c4c0826c8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341693729 conclusion=cancelled commit=96f470803f75b5cf71868abe2efaa27c4c0826c8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341693622 conclusion=failure commit=96f470803f75b5cf71868abe2efaa27c4c0826c8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341688417 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29341687410 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29341686864 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341686783 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29341686662 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29341686463 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29341686416 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29341686387 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29341686331 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29341686271 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29341686261 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341686110 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341685973 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29341685785 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341682224 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341682175 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341680818 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341679527 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341679065 conclusion=cancelled commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341678723 conclusion=failure commit=324666714baaddf75d46caece8c884e18d6b8bd9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29341657549 conclusion=failure commit=0d0ff11739f8bc6a4d34c606f5ff203f4dc8b643
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29341654232 conclusion=failure commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341654119 conclusion=cancelled commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29341653977 conclusion=cancelled commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29341634831 conclusion=failure commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29341634188 conclusion=failure commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29341634074 conclusion=cancelled commit=75e727d313df2c76712d9b40f65a924175fc6d8b
- [ ] workflow_failure_tracker: failed_count=41
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
