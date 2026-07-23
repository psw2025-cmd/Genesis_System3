# System3 Autopilot Latest Status

Generated UTC: `2026-07-23T08:35:08.640443+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `150`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 89 | 89 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 32 | 32 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29991547827 conclusion=failure commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29991547819 conclusion=failure commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29991547808 conclusion=failure commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29991547791 conclusion=failure commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29991545243 conclusion=cancelled commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29991545241 conclusion=failure commit=cd2c0431977e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29991504765 conclusion=failure commit=66792620558b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29991504756 conclusion=failure commit=66792620558b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29991483223 conclusion=failure commit=66792620558b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29991466247 conclusion=failure commit=14450477b3b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29991466238 conclusion=failure commit=14450477b3b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29991466072 conclusion=failure commit=14450477b3b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29991452478 conclusion=cancelled commit=54b55802753e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29991424699 conclusion=failure commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29991424694 conclusion=cancelled commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29991424677 conclusion=failure commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29991424663 conclusion=failure commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29991424655 conclusion=cancelled commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29991424629 conclusion=failure commit=2fc3e8b7d810
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29991404045 conclusion=failure commit=e8d0b6c24c38
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29990866807 conclusion=failure commit=fa2cf9d76b2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29990856921 conclusion=cancelled commit=fa2cf9d76b2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29990843166 conclusion=cancelled commit=9bc3da40032c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29990843069 conclusion=failure commit=9bc3da40032c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29990843066 conclusion=cancelled commit=9bc3da40032c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29990828682 conclusion=cancelled commit=8138fbe13494
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29990828651 conclusion=failure commit=8138fbe13494
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29990828621 conclusion=failure commit=8138fbe13494
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29990821265 conclusion=failure commit=8138fbe13494
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29990821233 conclusion=failure commit=8138fbe13494
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29990821222 conclusion=failure commit=8138fbe13494
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
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29991547827
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29991547819
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29991547808
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29991547791
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29991545243
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29991545241
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29991504765
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29991504756
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29991483223
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29991466247
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29991466238
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29991466072
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29991452478
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29991424699
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29991424694
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29991424677
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29991424663
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=cancelled run=29991424655
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29991424629
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29991404045
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29990866807
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29990856921
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29990843166
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29990843069
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29990843066
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29990828682
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=29990828651
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29990828621
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29990821265
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29990821233
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29990821222
- [ ] github_render_failure_tracker: github_failed_count=31
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=43
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29991547827 conclusion=failure commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29991547819 conclusion=failure commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29991547808 conclusion=failure commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29991547791 conclusion=failure commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29991545243 conclusion=cancelled commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29991545241 conclusion=failure commit=cd2c0431977ed46b789bc1659f471e375f6e7273
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29991504765 conclusion=failure commit=66792620558bd5b1931efd8a7f92199eed574616
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29991504756 conclusion=failure commit=66792620558bd5b1931efd8a7f92199eed574616
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29991483223 conclusion=failure commit=66792620558bd5b1931efd8a7f92199eed574616
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29991466247 conclusion=failure commit=14450477b3b7ab61cb87cabd6bdb471634e4fc3c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29991466238 conclusion=failure commit=14450477b3b7ab61cb87cabd6bdb471634e4fc3c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29991466072 conclusion=failure commit=14450477b3b7ab61cb87cabd6bdb471634e4fc3c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29991452478 conclusion=cancelled commit=54b55802753ef1770024554f3c46b2bbb33c88d0
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29991424699 conclusion=failure commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29991424694 conclusion=cancelled commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29991424677 conclusion=failure commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29991424663 conclusion=failure commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29991424655 conclusion=cancelled commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29991424629 conclusion=failure commit=2fc3e8b7d810e6d6dc6d1bb67434328fcda97f9f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29991404045 conclusion=failure commit=e8d0b6c24c3854cca66754f7b6a638f3b1be189a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29990866807 conclusion=failure commit=fa2cf9d76b2d9f8f921aabf8cae8d725cab522fe
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29990856921 conclusion=cancelled commit=fa2cf9d76b2d9f8f921aabf8cae8d725cab522fe
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29990843166 conclusion=cancelled commit=9bc3da40032cab8cf32b3dac718e7d5f3cda98c6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29990843069 conclusion=failure commit=9bc3da40032cab8cf32b3dac718e7d5f3cda98c6
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29990843066 conclusion=cancelled commit=9bc3da40032cab8cf32b3dac718e7d5f3cda98c6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29990828682 conclusion=cancelled commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29990828651 conclusion=failure commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29990828621 conclusion=failure commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29990821265 conclusion=failure commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29990821233 conclusion=failure commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29990821222 conclusion=failure commit=8138fbe1349481294957f76fe8648dd99ea921cd
- [ ] workflow_failure_tracker: failed_count=31
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
