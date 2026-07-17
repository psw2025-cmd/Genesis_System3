# System3 Autopilot Latest Status

Generated UTC: `2026-07-17T04:52:59.951724+00:00`
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

| Report | Raw status | Gate status | Current blockers | Raw entries |
|---|---|---|---:|---:|
| secure_install_credential_audit | BLOCKED | BLOCKED | 6 | 6 |
| dashboard_visible_issue_tracker | BLOCKED | BLOCKED | 1 | 1 |
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 103 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 42 | 42 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29555714353 conclusion=failure commit=9211f0714a8e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555681958 conclusion=failure commit=29b43b8b02ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29555681939 conclusion=failure commit=29b43b8b02ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29555681918 conclusion=failure commit=29b43b8b02ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29555681910 conclusion=failure commit=29b43b8b02ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29555681901 conclusion=failure commit=29b43b8b02ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=29555672347 conclusion=failure commit=10406ef9e65a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555294636 conclusion=failure commit=0311faa1e82c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555294612 conclusion=failure commit=0311faa1e82c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29555283195 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29555283180 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29555283175 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555283172 conclusion=cancelled commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555283162 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29555283152 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555281264 conclusion=cancelled commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555281254 conclusion=failure commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29555281251 conclusion=cancelled commit=6f0747c5eefd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555267395 conclusion=failure commit=c443b8555b34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555267375 conclusion=cancelled commit=c443b8555b34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29555267369 conclusion=cancelled commit=c443b8555b34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29555255385 conclusion=failure commit=c443b8555b34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29555242470 conclusion=failure commit=a68a7ee7dedc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29555242468 conclusion=failure commit=a68a7ee7dedc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555242458 conclusion=failure commit=a68a7ee7dedc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29555239069 conclusion=failure commit=9ad94f2724ab
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Settle Normalizer' run=29555226565 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29555226552 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29555226541 conclusion=cancelled commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29555226539 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29555226523 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555226520 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555226512 conclusion=cancelled commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29555226506 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29555224573 conclusion=cancelled commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29555224513 conclusion=failure commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29555224497 conclusion=cancelled commit=19d9ae856e5d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29555223899 conclusion=cancelled commit=19d9ae856e5d
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
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29555714353
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555681958
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29555681939
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29555681918
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29555681910
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29555681901
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=29555672347
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555294636
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29555294612
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29555283195
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29555283180
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29555283175
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29555283172
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555283162
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29555283152
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29555281264
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555281254
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29555281251
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555267395
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29555267375
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29555267369
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29555255385
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29555242470
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29555242468
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555242458
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29555239069
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Settle Normalizer conclusion=failure run=29555226565
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29555226552
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=cancelled run=29555226541
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29555226539
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29555226523
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555226520
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29555226512
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29555226506
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29555224573
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29555224513
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29555224497
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29555223899
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 29555085410 conclusion=failure commit=b4cf29a7d8e6a658d3c31793fa5e2f3dc296fd7f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 29554399546 conclusion=failure commit=af1ae290180e485a863a46044e15933649b75cad
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29553937164 conclusion=failure commit=9455c14e80f8ab0c484725111fadab7c50a1dfcd
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 29553860204 conclusion=cancelled commit=9455c14e80f8ab0c484725111fadab7c50a1dfcd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 29553778030 conclusion=cancelled commit=9455c14e80f8ab0c484725111fadab7c50a1dfcd
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29553720084 conclusion=failure commit=9455c14e80f8ab0c484725111fadab7c50a1dfcd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29553564740 conclusion=failure commit=088736d5a5dee0c9c4777e97b3183ab952b7f194
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553564694 conclusion=failure commit=088736d5a5dee0c9c4777e97b3183ab952b7f194
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553542394 conclusion=failure commit=ab68a0a9c73a5a3b1c07cbcc1e3fc031f95de84f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553542313 conclusion=failure commit=ab68a0a9c73a5a3b1c07cbcc1e3fc031f95de84f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553542298 conclusion=failure commit=ab68a0a9c73a5a3b1c07cbcc1e3fc031f95de84f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553542288 conclusion=failure commit=ab68a0a9c73a5a3b1c07cbcc1e3fc031f95de84f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29553534485 conclusion=cancelled commit=dcdaff4ae0feddae46e15b02f3051d58e5d30aff
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29553534416 conclusion=failure commit=dcdaff4ae0feddae46e15b02f3051d58e5d30aff
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553534382 conclusion=failure commit=dcdaff4ae0feddae46e15b02f3051d58e5d30aff
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29553526074 conclusion=cancelled commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553526060 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29553526058 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553526053 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553526051 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29553526050 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29553526028 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29553523630 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553523607 conclusion=failure commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29553523597 conclusion=cancelled commit=7357818202f8ca929f0a33a4fa782387738e06eb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553506549 conclusion=failure commit=ad25e73a324bc4f948888a4267b0a7196aa12684
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553502659 conclusion=failure commit=ad25e73a324bc4f948888a4267b0a7196aa12684
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553502654 conclusion=failure commit=ad25e73a324bc4f948888a4267b0a7196aa12684
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553502653 conclusion=failure commit=ad25e73a324bc4f948888a4267b0a7196aa12684
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553502013 conclusion=failure commit=ad25e73a324bc4f948888a4267b0a7196aa12684
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553491113 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553491112 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553491090 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29553487386 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553487366 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553487362 conclusion=failure commit=329ad7b772ef0d97d09ef9af2795628420002eba
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29553478374 conclusion=cancelled commit=5c811b8d658a34c9dcca35bf08e18faf56fdbb7a
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29553478352 conclusion=cancelled commit=5c811b8d658a34c9dcca35bf08e18faf56fdbb7a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29553034655 conclusion=failure commit=d365c5e06a6029d05e8a6d867e56895f3baa14cf
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29553034629 conclusion=failure commit=d365c5e06a6029d05e8a6d867e56895f3baa14cf
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29553034560 conclusion=failure commit=d365c5e06a6029d05e8a6d867e56895f3baa14cf
- [ ] workflow_failure_tracker: failed_count=41
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
