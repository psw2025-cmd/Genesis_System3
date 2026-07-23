# System3 Autopilot Latest Status

Generated UTC: `2026-07-23T17:34:21.817906+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `172`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 109 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 43 | 43 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30029893891 conclusion=failure commit=259031e41f2a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30029890958 conclusion=failure commit=259031e41f2a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30029867992 conclusion=failure commit=6bc8b7c641e7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30029762863 conclusion=failure commit=b1683ffba457
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30029762829 conclusion=cancelled commit=b1683ffba457
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30029523268 conclusion=cancelled commit=f3684c9f38d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30029034315 conclusion=failure commit=546802581ff0
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30029034219 conclusion=cancelled commit=546802581ff0
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30028923046 conclusion=cancelled commit=44404960fa66
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30028922882 conclusion=cancelled commit=44404960fa66
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028922788 conclusion=failure commit=44404960fa66
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028888572 conclusion=failure commit=29bc67726000
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30028888558 conclusion=cancelled commit=29bc67726000
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028868755 conclusion=failure commit=6225074fbc03
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30028868706 conclusion=failure commit=6225074fbc03
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028868704 conclusion=failure commit=6225074fbc03
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30028847525 conclusion=failure commit=82c682d6fceb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028847213 conclusion=failure commit=82c682d6fceb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028847212 conclusion=failure commit=82c682d6fceb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028846398 conclusion=failure commit=82c682d6fceb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028824309 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30028824003 conclusion=cancelled commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028823846 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30028823826 conclusion=cancelled commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30028823685 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30028823579 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30028823546 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30028823521 conclusion=cancelled commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028823499 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30028823439 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30028819274 conclusion=cancelled commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30028819268 conclusion=cancelled commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028819203 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028791859 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028780074 conclusion=failure commit=2c70a6a57058
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028758717 conclusion=failure commit=d40df75a916b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30028758324 conclusion=failure commit=d40df75a916b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028757978 conclusion=failure commit=d40df75a916b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30028752023 conclusion=failure commit=d40df75a916b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30028752004 conclusion=failure commit=d40df75a916b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30028751254 conclusion=failure commit=d40df75a916b
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
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30029893891
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30029890958
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30029867992
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30029762863
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30029762829
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30029523268
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30029034315
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30029034219
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=30028923046
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30028922882
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028922788
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028888572
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30028888558
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028868755
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30028868706
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028868704
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30028847525
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028847213
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028847212
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028846398
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028824309
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=30028824003
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028823846
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30028823826
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=30028823685
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=30028823579
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30028823546
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30028823521
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028823499
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30028823439
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=30028819274
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30028819268
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30028819203
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028791859
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30028780074
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30029893891 conclusion=failure commit=259031e41f2a47e405a1fe232f127f57a8ab7b60
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30029890958 conclusion=failure commit=259031e41f2a47e405a1fe232f127f57a8ab7b60
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30029867992 conclusion=failure commit=6bc8b7c641e70f44f2b6a2d1b640cb8d58eb42da
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30029762863 conclusion=failure commit=b1683ffba4570e47a47e788dca4cc863f6f9d21c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30029762829 conclusion=cancelled commit=b1683ffba4570e47a47e788dca4cc863f6f9d21c
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30029736193 conclusion=failure commit=f3684c9f38d98d9b7c7d72edf743aac2c9505c4b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30029523268 conclusion=cancelled commit=f3684c9f38d98d9b7c7d72edf743aac2c9505c4b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30029034315 conclusion=failure commit=546802581ff0d348579933e9864950aee5999a6d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30029034219 conclusion=cancelled commit=546802581ff0d348579933e9864950aee5999a6d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30028923046 conclusion=cancelled commit=44404960fa66f973fe6ff85ed25d2544a92b702b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30028922882 conclusion=cancelled commit=44404960fa66f973fe6ff85ed25d2544a92b702b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028922788 conclusion=failure commit=44404960fa66f973fe6ff85ed25d2544a92b702b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028888572 conclusion=failure commit=29bc67726000d540afc39fd78855c271855890ed
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30028888558 conclusion=cancelled commit=29bc67726000d540afc39fd78855c271855890ed
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028868755 conclusion=failure commit=6225074fbc032a8f7a393341a6f45d52cce3fcef
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30028868706 conclusion=failure commit=6225074fbc032a8f7a393341a6f45d52cce3fcef
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028868704 conclusion=failure commit=6225074fbc032a8f7a393341a6f45d52cce3fcef
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30028847525 conclusion=failure commit=82c682d6fceb5bdcc7ceaf9d763b5b66e2479aee
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028847213 conclusion=failure commit=82c682d6fceb5bdcc7ceaf9d763b5b66e2479aee
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028847212 conclusion=failure commit=82c682d6fceb5bdcc7ceaf9d763b5b66e2479aee
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028846398 conclusion=failure commit=82c682d6fceb5bdcc7ceaf9d763b5b66e2479aee
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028824309 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30028824003 conclusion=cancelled commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028823846 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30028823826 conclusion=cancelled commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 30028823685 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 30028823579 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 30028823546 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30028823521 conclusion=cancelled commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028823499 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30028823439 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30028819274 conclusion=cancelled commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30028819268 conclusion=cancelled commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028819203 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028791859 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028780074 conclusion=failure commit=2c70a6a5705827402eaa9288a6ce3f32b9082b03
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028758717 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30028758324 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028757978 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30028752023 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30028752004 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30028751254 conclusion=failure commit=d40df75a916bcee79f859e2559d463ce7ee1823d
- [ ] workflow_failure_tracker: failed_count=42
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
