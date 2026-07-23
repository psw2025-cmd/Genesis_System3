# System3 Autopilot Latest Status

Generated UTC: `2026-07-23T04:59:37.649653+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `169`

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

| Report | Raw status | Gate status | Current blockers | Raw entries |
|---|---|---|---:|---:|
| secure_install_credential_audit | BLOCKED | BLOCKED | 6 | 6 |
| dashboard_visible_issue_tracker | BLOCKED | BLOCKED | 1 | 1 |
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 105 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 40 | 40 |
| todo_status_update | BLOCKED | BLOCKED | 0 | 0 |
| dashboard_visual_production_proof | UNKNOWN | BLOCKED | 0 | 0 |
| system3_public_truth | BLOCKED_NOT_TRADE_READY | BLOCKED | 0 | 0 |

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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29980781842 conclusion=failure commit=86c32b9eb492
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=29980634288 conclusion=failure commit=08e3e524fcd3
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29980570735 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29980570709 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980570707 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29980570705 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980570685 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29980570679 conclusion=failure commit=1998dcf28358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Current' run=29980245199 conclusion=failure commit=14451caf4848
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29980135866 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980135840 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29980135815 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29980135807 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980135790 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29980135773 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980133167 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980133165 conclusion=cancelled commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980133122 conclusion=failure commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29980133120 conclusion=cancelled commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980133112 conclusion=cancelled commit=131c1c3bce3d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29980117700 conclusion=cancelled commit=e20a5896a492
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980117695 conclusion=failure commit=e20a5896a492
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980117673 conclusion=cancelled commit=e20a5896a492
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29980107054 conclusion=failure commit=e20a5896a492
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29980094376 conclusion=failure commit=d28b3db4c75f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29980094316 conclusion=failure commit=d28b3db4c75f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980094314 conclusion=failure commit=d28b3db4c75f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29980091269 conclusion=failure commit=24380c7e8c88
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980077440 conclusion=cancelled commit=0a7c83fe9a72
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29980077429 conclusion=cancelled commit=0a7c83fe9a72
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980077428 conclusion=failure commit=0a7c83fe9a72
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29980073180 conclusion=failure commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29980073151 conclusion=cancelled commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29980073141 conclusion=cancelled commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29980073138 conclusion=failure commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29980073119 conclusion=failure commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29980073116 conclusion=failure commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29980073106 conclusion=failure commit=b9c4fffa3e43
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29980070983 conclusion=cancelled commit=b9c4fffa3e43
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
- [ ] github_render_failure_tracker: endpoint=/ reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/ui/ reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/health reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 502 status=502
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29980781842
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=29980634288
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29980570735
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29980570709
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980570707
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29980570705
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29980570685
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29980570679
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Current conclusion=failure run=29980245199
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29980135866
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29980135840
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29980135815
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29980135807
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980135790
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29980135773
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980133167
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29980133165
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980133122
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29980133120
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29980133112
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29980117700
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980117695
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29980117673
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29980107054
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29980094376
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29980094316
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980094314
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29980091269
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29980077440
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29980077429
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980077428
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29980073180
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=cancelled run=29980073151
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29980073141
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29980073138
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29980073119
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29980073116
- [ ] parallel_root_cause_audit: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- [ ] parallel_root_cause_audit: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.
- [ ] parallel_root_cause_audit: Need compare public truth commit with latest repository head and Render deploy info; static repo audit cannot prove Render freshness.
- [ ] parallel_root_cause_audit: Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.
- [ ] parallel_root_cause_audit: Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.
- [ ] parallel_root_cause_audit: Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.
- [ ] parallel_root_cause_audit: Trading router may be inactive if app.py duplicate routes are authoritative.
- [ ] parallel_root_cause_audit: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.
- [ ] parallel_root_cause_audit: Options ML training summary is missing/not published.
- [ ] parallel_root_cause_audit: Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.
- [ ] parallel_root_cause_audit: Need fresh screenshot after latest commits; older screenshots do not prove current UI.
- [ ] parallel_root_cause_audit: Final truth must aggregate latest Render, integration, visual, broker, chain, scanner, paper, ML proof.
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 29979957023 conclusion=failure commit=ce886ba5b0ffd07ea8a4498039f09da66e329725
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 29979144438 conclusion=failure commit=2569162f2d02ed5c3b78b932994819acb5657cd1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29978726080 conclusion=failure commit=2569162f2d02ed5c3b78b932994819acb5657cd1
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 29978616972 conclusion=cancelled commit=6f9eb8f415ab41cf8cd6b7be53d27b0689ce3eab
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 29978527371 conclusion=cancelled commit=6f9eb8f415ab41cf8cd6b7be53d27b0689ce3eab
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29978466404 conclusion=failure commit=6f9eb8f415ab41cf8cd6b7be53d27b0689ce3eab
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29978400975 conclusion=cancelled commit=f1f06a7c46e13732eb42ab068476d95ba4c3d549
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29978400972 conclusion=failure commit=f1f06a7c46e13732eb42ab068476d95ba4c3d549
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978400966 conclusion=failure commit=f1f06a7c46e13732eb42ab068476d95ba4c3d549
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29978248212 conclusion=cancelled commit=219fadb1b7f750e83406063bdbe75ee7b283d5dc
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978248195 conclusion=failure commit=219fadb1b7f750e83406063bdbe75ee7b283d5dc
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978221340 conclusion=failure commit=0a9f403fffb23a751e5a6a1f8e0880f518cf20e1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978221331 conclusion=failure commit=0a9f403fffb23a751e5a6a1f8e0880f518cf20e1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29978221298 conclusion=failure commit=0a9f403fffb23a751e5a6a1f8e0880f518cf20e1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978217706 conclusion=failure commit=22d727b605ea30c7e272c20e4f452100187bfa3d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978202959 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29978202928 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29978202925 conclusion=cancelled commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29978202924 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29978202922 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29978202921 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978202920 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29978200948 conclusion=cancelled commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978200936 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29978200923 conclusion=failure commit=6c64ff9db17aa4dbe4880b8d759ac18ced243656
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978175608 conclusion=failure commit=e89b8af0084772040e2d4ab277f241429785c872
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29978175591 conclusion=failure commit=e89b8af0084772040e2d4ab277f241429785c872
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978175545 conclusion=failure commit=e89b8af0084772040e2d4ab277f241429785c872
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978172199 conclusion=failure commit=fbd37794ab0d4228429866fd1d926ef3967f3162
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978171749 conclusion=failure commit=fbd37794ab0d4228429866fd1d926ef3967f3162
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978158101 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29978158052 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978158049 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29978154718 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29978154716 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29978154683 conclusion=failure commit=eb46e17c65a9835a544d44ccc6815da87310c034
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29978146935 conclusion=cancelled commit=27ac05a2568ababad5215563e003773fc967f299
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29978146909 conclusion=cancelled commit=27ac05a2568ababad5215563e003773fc967f299
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29977695593 conclusion=failure commit=d3751851551f8261bb072b6f997f6faa88328d0b
- [ ] workflow_failure_tracker: failed_count=39
- [ ] todo_status_update: status=BLOCKED
- [ ] dashboard_visual_production_proof: status=UNKNOWN
- [ ] system3_public_truth: status=BLOCKED_NOT_TRADE_READY
- [ ] core_gate_blocked:render_visual
- [ ] core_gate_blocked:github_render_health
- [ ] core_gate_blocked:backend_frontend_install
- [ ] core_gate_blocked:workflow_health
- [ ] core_gate_blocked:root_cause_zero
- [ ] core_gate_blocked:todo_zero
- [ ] core_gate_blocked:public_truth_pass
