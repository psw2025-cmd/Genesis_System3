# System3 Autopilot Latest Status

Generated UTC: `2026-07-15T08:25:18.101481+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `165`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 99 | 99 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 37 | 37 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29400671370 conclusion=failure commit=79144d6e1e88
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=29400216343 conclusion=failure commit=ba0a5636cac9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=29400057695 conclusion=failure commit=ba0a5636cac9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29399442075 conclusion=failure commit=d0bc4782bd34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399442031 conclusion=failure commit=d0bc4782bd34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399404152 conclusion=failure commit=b2f86db76f23
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399404140 conclusion=failure commit=b2f86db76f23
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29399404116 conclusion=failure commit=b2f86db76f23
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399402949 conclusion=failure commit=b2f86db76f23
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=29399384327 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=29399384283 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=29399384211 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29399384209 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399384194 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29399384190 conclusion=cancelled commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399384159 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=29399370739 conclusion=failure commit=4d1c4ba7a99c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29399328525 conclusion=cancelled commit=df81aa620b10
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399328504 conclusion=failure commit=df81aa620b10
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29399328497 conclusion=failure commit=df81aa620b10
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399318029 conclusion=failure commit=61bb26cae746
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=29399317915 conclusion=cancelled commit=61bb26cae746
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29399317898 conclusion=cancelled commit=61bb26cae746
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399277573 conclusion=failure commit=9b2530154223
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399269804 conclusion=failure commit=9b2530154223
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399269752 conclusion=failure commit=9b2530154223
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29399269714 conclusion=failure commit=9b2530154223
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399260301 conclusion=failure commit=cff507b60ec6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=29399256025 conclusion=failure commit=9bb418a45a90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399247486 conclusion=failure commit=9bb418a45a90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29399247453 conclusion=failure commit=9bb418a45a90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399247421 conclusion=failure commit=9bb418a45a90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=29399239706 conclusion=failure commit=236159d3b390
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=29399239389 conclusion=failure commit=236159d3b390
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=29399239366 conclusion=failure commit=236159d3b390
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=29399221086 conclusion=failure commit=4683b1d1973a
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
- [ ] github_render_failure_tracker: workflow=.github/workflows/options-ml-training-proof.yml conclusion=failure run=29400671370
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=29400216343
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=29400057695
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=29399442075
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399442031
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399404152
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399404140
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29399404116
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399402949
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=29399384327
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=29399384283
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=29399384211
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29399384209
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399384194
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29399384190
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399384159
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=29399370739
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29399328525
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399328504
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=29399328497
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399318029
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=29399317915
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=29399317898
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399277573
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399269804
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399269752
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29399269714
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399260301
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=29399256025
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399247486
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29399247453
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399247421
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=29399239706
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=29399239389
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=29399239366
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=29399221086
- [ ] github_render_failure_tracker: github_failed_count=36
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=48
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
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29400671370 conclusion=failure commit=79144d6e1e88c7f868be981b6745b9817701e517
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 29400216343 conclusion=failure commit=ba0a5636cac9b68de5de67762a9ca481e3b53a3b
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 29400057695 conclusion=failure commit=ba0a5636cac9b68de5de67762a9ca481e3b53a3b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29399442075 conclusion=failure commit=d0bc4782bd343a5002cde9e3d99bbacaad550cb4
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399442031 conclusion=failure commit=d0bc4782bd343a5002cde9e3d99bbacaad550cb4
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399404152 conclusion=failure commit=b2f86db76f2354f4b9c8334d0563a7ab25f0cd37
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399404140 conclusion=failure commit=b2f86db76f2354f4b9c8334d0563a7ab25f0cd37
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29399404116 conclusion=failure commit=b2f86db76f2354f4b9c8334d0563a7ab25f0cd37
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399402949 conclusion=failure commit=b2f86db76f2354f4b9c8334d0563a7ab25f0cd37
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 29399384327 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 29399384283 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 29399384211 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29399384209 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399384194 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29399384190 conclusion=cancelled commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399384159 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 29399370739 conclusion=failure commit=4d1c4ba7a99c272625a7c8f0b780a79aa3fccffb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29399328525 conclusion=cancelled commit=df81aa620b106721b60dd38b26ce32371019dc6c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399328504 conclusion=failure commit=df81aa620b106721b60dd38b26ce32371019dc6c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29399328497 conclusion=failure commit=df81aa620b106721b60dd38b26ce32371019dc6c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399318029 conclusion=failure commit=61bb26cae7467f1b1a15c0aef72a75acc7216bca
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 29399317915 conclusion=cancelled commit=61bb26cae7467f1b1a15c0aef72a75acc7216bca
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29399317898 conclusion=cancelled commit=61bb26cae7467f1b1a15c0aef72a75acc7216bca
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399277573 conclusion=failure commit=9b253015422349187db0f9b5e307d2ae007bbbd6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399269804 conclusion=failure commit=9b253015422349187db0f9b5e307d2ae007bbbd6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399269752 conclusion=failure commit=9b253015422349187db0f9b5e307d2ae007bbbd6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29399269714 conclusion=failure commit=9b253015422349187db0f9b5e307d2ae007bbbd6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399260301 conclusion=failure commit=cff507b60ec6d2873550f71de027af1c97be3932
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 29399256025 conclusion=failure commit=9bb418a45a90b5b2e046638a8e829f3eb758fa32
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399247486 conclusion=failure commit=9bb418a45a90b5b2e046638a8e829f3eb758fa32
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29399247453 conclusion=failure commit=9bb418a45a90b5b2e046638a8e829f3eb758fa32
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399247421 conclusion=failure commit=9bb418a45a90b5b2e046638a8e829f3eb758fa32
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 29399239706 conclusion=failure commit=236159d3b3908f021d3b553c308645bd4e689a1c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 29399239389 conclusion=failure commit=236159d3b3908f021d3b553c308645bd4e689a1c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29399239366 conclusion=failure commit=236159d3b3908f021d3b553c308645bd4e689a1c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 29399221086 conclusion=failure commit=4683b1d1973af20864bb22abf2fb65a284eaa468
- [ ] workflow_failure_tracker: failed_count=36
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
