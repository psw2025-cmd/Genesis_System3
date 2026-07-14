# System3 Autopilot Latest Status

Generated UTC: `2026-07-14T03:19:16.260632+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `183`

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
| workflow_failure_tracker | BLOCKED | BLOCKED | 43 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29303178591 conclusion=failure commit=c000deb3a438
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29303178575 conclusion=failure commit=c000deb3a438
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29303169416 conclusion=failure commit=6293a809c455
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29303169392 conclusion=failure commit=6293a809c455
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29303169391 conclusion=failure commit=6293a809c455
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29303169373 conclusion=failure commit=6293a809c455
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29303169370 conclusion=failure commit=6293a809c455
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302874366 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302874352 conclusion=cancelled commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29302874332 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29302874301 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29302874295 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29302874274 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29302874265 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29302786273 conclusion=failure commit=9c8a09e86dca
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302662908 conclusion=failure commit=f3fea6f64a00
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29302662865 conclusion=cancelled commit=f3fea6f64a00
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302662860 conclusion=cancelled commit=f3fea6f64a00
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302654192 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29302654186 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29302654185 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29302654184 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29302654182 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302654173 conclusion=cancelled commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=29302654171 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302651741 conclusion=failure commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29302651717 conclusion=cancelled commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302651690 conclusion=cancelled commit=901554fe21d1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302638827 conclusion=failure commit=58be8069b880
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29302638790 conclusion=cancelled commit=58be8069b880
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302638781 conclusion=cancelled commit=58be8069b880
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29302632945 conclusion=failure commit=58be8069b880
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29302618138 conclusion=cancelled commit=e56418d2c63d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302618134 conclusion=cancelled commit=e56418d2c63d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302618105 conclusion=failure commit=e56418d2c63d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29302611135 conclusion=failure commit=f1909e9ae4ae
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29302606837 conclusion=failure commit=f1909e9ae4ae
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29302606833 conclusion=failure commit=f1909e9ae4ae
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302606831 conclusion=failure commit=f1909e9ae4ae
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29302606492 conclusion=failure commit=f1909e9ae4ae
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29302606483 conclusion=cancelled commit=f1909e9ae4ae
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
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c000deb3a4387478b014f141edb24d9859ea9ad9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303178591", "run_id": 29303178591, "updated_at": "2026-07-14T03:18:00Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "c000deb3a4387478b014f141edb24d9859ea9ad9", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303178575", "run_id": 29303178575, "updated_at": "2026-07-14T03:18:09Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "6293a809c455fae79cacdbef67d9d4f144a5eabb", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303169416", "run_id": 29303169416, "updated_at": "2026-07-14T03:17:53Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "6293a809c455fae79cacdbef67d9d4f144a5eabb", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303169392", "run_id": 29303169392, "updated_at": "2026-07-14T03:17:46Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "6293a809c455fae79cacdbef67d9d4f144a5eabb", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303169391", "run_id": 29303169391, "updated_at": "2026-07-14T03:17:49Z", "workflow": "System3 1000 Point TODO Status Updater"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "6293a809c455fae79cacdbef67d9d4f144a5eabb", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303169373", "run_id": 29303169373, "updated_at": "2026-07-14T03:17:47Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "6293a809c455fae79cacdbef67d9d4f144a5eabb", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29303169370", "run_id": 29303169370, "updated_at": "2026-07-14T03:17:48Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874366", "run_id": 29302874366, "updated_at": "2026-07-14T03:10:45Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874352", "run_id": 29302874352, "updated_at": "2026-07-14T03:17:51Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874332", "run_id": 29302874332, "updated_at": "2026-07-14T03:10:49Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874301", "run_id": 29302874301, "updated_at": "2026-07-14T03:13:11Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874295", "run_id": 29302874295, "updated_at": "2026-07-14T03:10:45Z", "workflow": "System3 1000 Point TODO Status Updater"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874274", "run_id": 29302874274, "updated_at": "2026-07-14T03:10:42Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302874265", "run_id": 29302874265, "updated_at": "2026-07-14T03:10:43Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302786273", "run_id": 29302786273, "updated_at": "2026-07-14T03:17:34Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f3fea6f64a0037b7f213ac2c4cff9e3377126d75", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302662908", "run_id": 29302662908, "updated_at": "2026-07-14T03:05:43Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f3fea6f64a0037b7f213ac2c4cff9e3377126d75", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302662865", "run_id": 29302662865, "updated_at": "2026-07-14T03:08:28Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f3fea6f64a0037b7f213ac2c4cff9e3377126d75", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302662860", "run_id": 29302662860, "updated_at": "2026-07-14T03:10:49Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654192", "run_id": 29302654192, "updated_at": "2026-07-14T03:05:31Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654186", "run_id": 29302654186, "updated_at": "2026-07-14T03:05:32Z", "workflow": "Dashboard Visual Loading Postflight"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654185", "run_id": 29302654185, "updated_at": "2026-07-14T03:05:38Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654184", "run_id": 29302654184, "updated_at": "2026-07-14T03:06:09Z", "workflow": "Dashboard Shell Diagnostic"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654182", "run_id": 29302654182, "updated_at": "2026-07-14T03:05:29Z", "workflow": "Dashboard Visual Proof Strict Gate"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654173", "run_id": 29302654173, "updated_at": "2026-07-14T03:05:35Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302654171", "run_id": 29302654171, "updated_at": "2026-07-14T03:05:37Z", "workflow": "System3 1000 Point TODO Status Updater"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302651741", "run_id": 29302651741, "updated_at": "2026-07-14T03:05:28Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302651717", "run_id": 29302651717, "updated_at": "2026-07-14T03:05:33Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "901554fe21d12574ed4b701548dea393af04e1f1", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302651690", "run_id": 29302651690, "updated_at": "2026-07-14T03:05:24Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "58be8069b8804b1047d28d290352793832f0d280", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302638827", "run_id": 29302638827, "updated_at": "2026-07-14T03:05:14Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "58be8069b8804b1047d28d290352793832f0d280", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302638790", "run_id": 29302638790, "updated_at": "2026-07-14T03:05:18Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "58be8069b8804b1047d28d290352793832f0d280", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302638781", "run_id": 29302638781, "updated_at": "2026-07-14T03:05:18Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "58be8069b8804b1047d28d290352793832f0d280", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302632945", "run_id": 29302632945, "updated_at": "2026-07-14T03:05:59Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e56418d2c63d13b7e313433f05df5371b9954f4b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302618138", "run_id": 29302618138, "updated_at": "2026-07-14T03:05:02Z", "workflow": "Dashboard Visible Issue Tracker"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e56418d2c63d13b7e313433f05df5371b9954f4b", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302618134", "run_id": 29302618134, "updated_at": "2026-07-14T03:05:15Z", "workflow": "System3 Safe Repair Runner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "e56418d2c63d13b7e313433f05df5371b9954f4b", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302618105", "run_id": 29302618105, "updated_at": "2026-07-14T03:04:44Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302611135", "run_id": 29302611135, "updated_at": "2026-07-14T03:05:15Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302606837", "run_id": 29302606837, "updated_at": "2026-07-14T03:05:29Z", "workflow": "System3 Autopilot Proof Board"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302606833", "run_id": 29302606833, "updated_at": "2026-07-14T03:04:50Z", "workflow": "System3 Secure Install Credential Audit"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302606831", "run_id": 29302606831, "updated_at": "2026-07-14T03:04:27Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "failure", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302606492", "run_id": 29302606492, "updated_at": "2026-07-14T03:04:26Z", "workflow": "System3 Experimental Solution Planner"}
- [ ] github_render_failure_tracker: {"branch": "main", "commit": "f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f", "conclusion": "cancelled", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29302606483", "run_id": 29302606483, "updated_at": "2026-07-14T03:04:33Z", "workflow": "System3 Safe Repair Runner"}
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29303181076 conclusion=failure commit=c000deb3a4387478b014f141edb24d9859ea9ad9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29303178591 conclusion=failure commit=c000deb3a4387478b014f141edb24d9859ea9ad9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29303178575 conclusion=failure commit=c000deb3a4387478b014f141edb24d9859ea9ad9
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29303169416 conclusion=failure commit=6293a809c455fae79cacdbef67d9d4f144a5eabb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29303169392 conclusion=failure commit=6293a809c455fae79cacdbef67d9d4f144a5eabb
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29303169391 conclusion=failure commit=6293a809c455fae79cacdbef67d9d4f144a5eabb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29303169373 conclusion=failure commit=6293a809c455fae79cacdbef67d9d4f144a5eabb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29303169370 conclusion=failure commit=6293a809c455fae79cacdbef67d9d4f144a5eabb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302874366 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302874352 conclusion=cancelled commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29302874332 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29302874301 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29302874295 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29302874274 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29302874265 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29302786273 conclusion=failure commit=9c8a09e86dca2a17ac8b9c173bef8f8b7e8563ce
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302662908 conclusion=failure commit=f3fea6f64a0037b7f213ac2c4cff9e3377126d75
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29302662865 conclusion=cancelled commit=f3fea6f64a0037b7f213ac2c4cff9e3377126d75
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302662860 conclusion=cancelled commit=f3fea6f64a0037b7f213ac2c4cff9e3377126d75
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302654192 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29302654186 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29302654185 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29302654184 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29302654182 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302654173 conclusion=cancelled commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29302654171 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302651741 conclusion=failure commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29302651717 conclusion=cancelled commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302651690 conclusion=cancelled commit=901554fe21d12574ed4b701548dea393af04e1f1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302638827 conclusion=failure commit=58be8069b8804b1047d28d290352793832f0d280
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29302638790 conclusion=cancelled commit=58be8069b8804b1047d28d290352793832f0d280
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302638781 conclusion=cancelled commit=58be8069b8804b1047d28d290352793832f0d280
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29302632945 conclusion=failure commit=58be8069b8804b1047d28d290352793832f0d280
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29302618138 conclusion=cancelled commit=e56418d2c63d13b7e313433f05df5371b9954f4b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302618134 conclusion=cancelled commit=e56418d2c63d13b7e313433f05df5371b9954f4b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302618105 conclusion=failure commit=e56418d2c63d13b7e313433f05df5371b9954f4b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29302611135 conclusion=failure commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29302606837 conclusion=failure commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29302606833 conclusion=failure commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302606831 conclusion=failure commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29302606492 conclusion=failure commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29302606483 conclusion=cancelled commit=f1909e9ae4ae98dc8b016fc8e2b38ef92d053b4f
- [ ] workflow_failure_tracker: failed_count=42
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
