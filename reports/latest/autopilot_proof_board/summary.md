# System3 Autopilot Latest Status

Generated UTC: `2026-07-30T04:52:03.373931+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `127`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 71 | 71 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 27 | 27 |
| todo_status_update | BLOCKED | BLOCKED | 0 | 0 |
| dashboard_visual_production_proof | UNKNOWN | BLOCKED | 0 | 0 |
| system3_public_truth | FAIL | BLOCKED | 0 | 0 |

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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30514055102 conclusion=failure commit=275458e986fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30513321843 conclusion=failure commit=d8d35a9d714c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30512872244 conclusion=failure commit=a4adb00e180d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30512769141 conclusion=failure commit=a4adb00e180d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30512607209 conclusion=failure commit=a4adb00e180d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30511140349 conclusion=failure commit=a4adb00e180d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30511069341 conclusion=failure commit=a4adb00e180d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30510957314 conclusion=failure commit=4974b7501b04
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30510931068 conclusion=failure commit=886f84dfa52d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30510930474 conclusion=cancelled commit=886f84dfa52d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30510893726 conclusion=failure commit=886f84dfa52d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30507332080 conclusion=failure commit=e6f88310b3cb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30507224027 conclusion=failure commit=e6f88310b3cb
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30507033764 conclusion=cancelled commit=14aaab61b93a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30507033729 conclusion=failure commit=14aaab61b93a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30506985361 conclusion=failure commit=14aaab61b93a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30506022662 conclusion=failure commit=58f3ee62ac34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30503931686 conclusion=failure commit=66bc34580252
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30503916703 conclusion=failure commit=3cd6e15e5aa8
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30503875656 conclusion=cancelled commit=f492423bfa30
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30503849555 conclusion=failure commit=e31bd13f0be6
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30503836653 conclusion=failure commit=e31bd13f0be6
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/health: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/ reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/ui/ reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/health reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=30514055102
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30513321843
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30512872244
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30512769141
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30512607209
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30511140349
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30511069341
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30510957314
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30510931068
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30510930474
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30510893726
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30507332080
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30507224027
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30507033764
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30507033729
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30506985361
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30506022662
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30503931686
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30503916703
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30503875656
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30503849555
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30503836653
- [ ] github_render_failure_tracker: github_failed_count=22
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=34
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30514055102 conclusion=failure commit=275458e986fa580b4dee0c4174233aaedf959bcc
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30513321843 conclusion=failure commit=d8d35a9d714c0b5593725455e6a6b1d7bf6fd5a6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30512872244 conclusion=failure commit=a4adb00e180df16d8207b591594bc71820b14e0e
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30512769141 conclusion=failure commit=a4adb00e180df16d8207b591594bc71820b14e0e
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30512607209 conclusion=failure commit=a4adb00e180df16d8207b591594bc71820b14e0e
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30511140349 conclusion=failure commit=a4adb00e180df16d8207b591594bc71820b14e0e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30511069341 conclusion=failure commit=a4adb00e180df16d8207b591594bc71820b14e0e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30510957314 conclusion=failure commit=4974b7501b049871a5ae7bdda2ce213a3ca00618
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30510931068 conclusion=failure commit=886f84dfa52d5556ead1e0633bc59e994a23a6e5
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30510930474 conclusion=cancelled commit=886f84dfa52d5556ead1e0633bc59e994a23a6e5
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30510893726 conclusion=failure commit=886f84dfa52d5556ead1e0633bc59e994a23a6e5
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30510116844 conclusion=failure commit=e6f88310b3cb7fbc1d712fd4af520da324bd58c7
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30507332080 conclusion=failure commit=e6f88310b3cb7fbc1d712fd4af520da324bd58c7
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30507224027 conclusion=failure commit=e6f88310b3cb7fbc1d712fd4af520da324bd58c7
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30507033764 conclusion=cancelled commit=14aaab61b93aafb848de72554bbf4c904047ac60
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30507033729 conclusion=failure commit=14aaab61b93aafb848de72554bbf4c904047ac60
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30506985361 conclusion=failure commit=14aaab61b93aafb848de72554bbf4c904047ac60
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30506022662 conclusion=failure commit=58f3ee62ac34560f1e849104f87e901794f07978
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30505995353 conclusion=failure commit=66bc34580252d452bea23ccd5b51abb3e53de458
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30503931686 conclusion=failure commit=66bc34580252d452bea23ccd5b51abb3e53de458
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30503916703 conclusion=failure commit=3cd6e15e5aa8f329746ce53aaf6be2024e226412
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30503875656 conclusion=cancelled commit=f492423bfa3019085aa064f73667172e9d43661a
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30503849555 conclusion=failure commit=e31bd13f0be60e79a52d700dfc94a6f9416a746d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30503836653 conclusion=failure commit=e31bd13f0be60e79a52d700dfc94a6f9416a746d
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30502797959 conclusion=failure commit=514610eb50e9cd0ca5e61270b14cbec7fdcf3556
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30500260663 conclusion=failure commit=d3309942a40374637b5ba2cad0e05ff60d68b667
- [ ] workflow_failure_tracker: failed_count=26
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
