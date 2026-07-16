# System3 Autopilot Latest Status

Generated UTC: `2026-07-16T04:52:37.122574+00:00`
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
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 101 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29472171690 conclusion=failure commit=250d04c35578
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29472171689 conclusion=failure commit=250d04c35578
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29472171687 conclusion=failure commit=250d04c35578
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29472171672 conclusion=failure commit=250d04c35578
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29472171671 conclusion=failure commit=250d04c35578
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29472133200 conclusion=failure commit=b24525e8b81e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29472085537 conclusion=failure commit=b24525e8b81e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=29472080796 conclusion=failure commit=b24525e8b81e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Current' run=29471913231 conclusion=failure commit=b24525e8b81e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29471708281 conclusion=failure commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29471708261 conclusion=failure commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29471708217 conclusion=cancelled commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29471704467 conclusion=cancelled commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29471704458 conclusion=cancelled commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29471704452 conclusion=failure commit=6428646d48d6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29471689720 conclusion=cancelled commit=4bdd964d78ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29471689700 conclusion=failure commit=4bdd964d78ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29471689694 conclusion=failure commit=4bdd964d78ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29471682232 conclusion=failure commit=4bdd964d78ee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29471666717 conclusion=failure commit=e2b930b29ee7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29471666715 conclusion=failure commit=e2b930b29ee7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29471666703 conclusion=failure commit=e2b930b29ee7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29471665457 conclusion=failure commit=e2b930b29ee7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29471652340 conclusion=failure commit=798a2288cffb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29471652334 conclusion=failure commit=798a2288cffb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29471652295 conclusion=failure commit=798a2288cffb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=29471574505 conclusion=failure commit=b3ef1d9e8b12
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=29470935332 conclusion=failure commit=b33056dcb8ce
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29470583087 conclusion=failure commit=ff5f30a60070
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29470583086 conclusion=failure commit=ff5f30a60070
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29470559818 conclusion=failure commit=ce0546da2d71
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29470559506 conclusion=failure commit=ce0546da2d71
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29470559469 conclusion=failure commit=ce0546da2d71
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29470559454 conclusion=failure commit=ce0546da2d71
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29470543671 conclusion=failure commit=a12de1ffb04f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29470543660 conclusion=cancelled commit=a12de1ffb04f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29470543644 conclusion=failure commit=a12de1ffb04f
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /ui/: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/health: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 503 status=503
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/ reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/ui/ reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/health reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 503 status=503
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29472171690
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29472171689
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29472171687
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29472171672
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29472171671
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29472133200
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Full Proof conclusion=failure run=29472085537
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=29472080796
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Current conclusion=failure run=29471913231
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29471708281
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29471708261
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29471708217
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29471704467
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29471704458
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29471704452
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29471689720
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=29471689700
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29471689694
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29471682232
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29471666717
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29471666715
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29471666703
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29471665457
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29471652340
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29471652334
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29471652295
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=29471574505
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=29470935332
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29470583087
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29470583086
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29470559818
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29470559506
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29470559469
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29470559454
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29470543671
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29470543660
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29470543644
- [ ] github_render_failure_tracker: github_failed_count=37
- [ ] github_render_failure_tracker: render_failed_count=12
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 29471574505 conclusion=failure commit=b3ef1d9e8b12c24a0e9590c99be57133647026f5
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 29470935332 conclusion=failure commit=b33056dcb8ce1ddeef5b30505fc6fd29bc02928c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470583087 conclusion=failure commit=ff5f30a60070a9b6325e134ddd3310188072b8d1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29470583086 conclusion=failure commit=ff5f30a60070a9b6325e134ddd3310188072b8d1
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470559818 conclusion=failure commit=ce0546da2d717161af0165a0df04f56c92903a14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470559506 conclusion=failure commit=ce0546da2d717161af0165a0df04f56c92903a14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470559469 conclusion=failure commit=ce0546da2d717161af0165a0df04f56c92903a14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29470559454 conclusion=failure commit=ce0546da2d717161af0165a0df04f56c92903a14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470543671 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29470543660 conclusion=cancelled commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29470543644 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29470543637 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470543631 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29470543623 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29470543589 conclusion=failure commit=a12de1ffb04f87dbe4712b90ba8c132668901a84
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29470500402 conclusion=cancelled commit=39b2d6a12d12293b38bcba7ddc55e6772e314532
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 29470319644 conclusion=cancelled commit=39b2d6a12d12293b38bcba7ddc55e6772e314532
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29470256414 conclusion=failure commit=39b2d6a12d12293b38bcba7ddc55e6772e314532
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470064575 conclusion=failure commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29470064564 conclusion=failure commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29470064535 conclusion=failure commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29470062610 conclusion=cancelled commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470062585 conclusion=failure commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29470062568 conclusion=cancelled commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470044129 conclusion=failure commit=258fe16039545642ffb3e8290571052ad5ae237d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470037966 conclusion=failure commit=8615023044acd9f5430775fca805b6c18246dbb3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29470037357 conclusion=failure commit=8615023044acd9f5430775fca805b6c18246dbb3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470037343 conclusion=failure commit=8615023044acd9f5430775fca805b6c18246dbb3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470037288 conclusion=failure commit=8615023044acd9f5430775fca805b6c18246dbb3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470025510 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29470025475 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470025468 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29470022597 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29470022592 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29470022584 conclusion=failure commit=614b7ac75dd89e476c95cf5d60857286d9a75930
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 29470014606 conclusion=cancelled commit=f348836cce763ea4c86a7f9362bf5220ad3e7b23
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29470014574 conclusion=failure commit=f348836cce763ea4c86a7f9362bf5220ad3e7b23
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29469590111 conclusion=failure commit=49e775478023603a3c48a87bb6c13513a171aa65
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29469590070 conclusion=failure commit=49e775478023603a3c48a87bb6c13513a171aa65
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
