# System3 Autopilot Latest Status

Generated UTC: `2026-07-15T10:41:45.584889+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `163`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 95 | 95 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 39 | 39 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29408755341 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29408755283 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29408755252 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29408755248 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408755230 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408752396 conclusion=failure commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408752378 conclusion=cancelled commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29408752371 conclusion=cancelled commit=1eb0a1ba6efc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408738417 conclusion=failure commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408738397 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29408738284 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408737872 conclusion=failure commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408737851 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29408737828 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408736053 conclusion=failure commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29408736042 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408736040 conclusion=cancelled commit=6e8df1c1e5d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408724951 conclusion=failure commit=28087b96b24c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408724912 conclusion=cancelled commit=28087b96b24c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408705147 conclusion=failure commit=28087b96b24c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408682654 conclusion=failure commit=6c4a823f0cc2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408682612 conclusion=failure commit=6c4a823f0cc2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29408682606 conclusion=failure commit=6c4a823f0cc2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408679477 conclusion=failure commit=6c4a823f0cc2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408660668 conclusion=failure commit=e210fe289af6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408660633 conclusion=cancelled commit=e210fe289af6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408656682 conclusion=failure commit=e269718aa79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408653102 conclusion=failure commit=e269718aa79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408653084 conclusion=failure commit=e269718aa79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29408653023 conclusion=failure commit=e269718aa79f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29408631897 conclusion=failure commit=2d8d97914e27
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29408631863 conclusion=failure commit=2d8d97914e27
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29408631826 conclusion=failure commit=2d8d97914e27
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29408419121 conclusion=cancelled commit=2ce8b7705ea2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Genesis System3 Global Safety CI' run=29408065117 conclusion=failure commit=2ce8b7705ea2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=29408065094 conclusion=failure commit=2ce8b7705ea2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=29408065089 conclusion=failure commit=2ce8b7705ea2
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29408755341
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29408755283
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29408755252
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29408755248
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408755230
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408752396
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408752378
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29408752371
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408738417
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408738397
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29408738284
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408737872
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408737851
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29408737828
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408736053
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29408736042
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408736040
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408724951
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408724912
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408705147
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408682654
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408682612
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29408682606
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408679477
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408660668
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408660633
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408656682
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408653102
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408653084
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29408653023
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29408631897
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29408631863
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29408631826
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29408419121
- [ ] github_render_failure_tracker: workflow=Genesis System3 Global Safety CI conclusion=failure run=29408065117
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=29408065094
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=29408065089
- [ ] github_render_failure_tracker: github_failed_count=37
- [ ] github_render_failure_tracker: render_failed_count=9
- [ ] github_render_failure_tracker: todo_count=46
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
- [ ] workflow_failure_tracker: Fix workflow 'Genesis System3 Global Safety CI' run 29408065117 conclusion=failure commit=2ce8b7705ea2d1c7d35c55a554c6e7425108df22
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29408065094 conclusion=failure commit=2ce8b7705ea2d1c7d35c55a554c6e7425108df22
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Settle Proof' run 29408065089 conclusion=failure commit=2ce8b7705ea2d1c7d35c55a554c6e7425108df22
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29408064425 conclusion=failure commit=2ce8b7705ea2d1c7d35c55a554c6e7425108df22
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29408007963 conclusion=failure commit=c433851c3d8dfc329caa306798d64d41140fd980
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Full Proof' run 29407864202 conclusion=failure commit=c433851c3d8dfc329caa306798d64d41140fd980
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 29407668735 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Current' run 29407543126 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 29407391345 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 29407321559 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 29407273623 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29407208658 conclusion=failure commit=53625fb0b37c6a570222a00c0345ae582e3a999d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 29406680942 conclusion=failure commit=c88165bbf3d3f09cc5606371fe89efbda1fa2dff
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406615123 conclusion=failure commit=cc32def802a27e2ed410035c106ff0d9261fa826
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29406615063 conclusion=failure commit=cc32def802a27e2ed410035c106ff0d9261fa826
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29406582513 conclusion=failure commit=4b15dce458fb74a03bb104836f1ef21fa8dd3216
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406582390 conclusion=failure commit=4b15dce458fb74a03bb104836f1ef21fa8dd3216
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406582331 conclusion=failure commit=4b15dce458fb74a03bb104836f1ef21fa8dd3216
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406578933 conclusion=failure commit=4b15dce458fb74a03bb104836f1ef21fa8dd3216
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 29406567947 conclusion=failure commit=59a6311cc681d408b8a97bf4af018cc6385755d2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406552644 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29406552255 conclusion=cancelled commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29406552188 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29406552131 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406552123 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29406552082 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29406552063 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406549267 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29406549214 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29406549210 conclusion=cancelled commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29406548817 conclusion=cancelled commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29406548782 conclusion=cancelled commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406548753 conclusion=failure commit=39ae0190e86b0de4e6c6e0771626bbc5ef852861
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406513727 conclusion=failure commit=39785331ea0db8906c01e184ed64bb9bfce56338
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406511878 conclusion=failure commit=39785331ea0db8906c01e184ed64bb9bfce56338
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29406510719 conclusion=failure commit=39785331ea0db8906c01e184ed64bb9bfce56338
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29406510674 conclusion=failure commit=39785331ea0db8906c01e184ed64bb9bfce56338
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29406510660 conclusion=failure commit=39785331ea0db8906c01e184ed64bb9bfce56338
- [ ] workflow_failure_tracker: failed_count=38
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
