# System3 Autopilot Latest Status

Generated UTC: `2026-07-31T05:04:52.088486+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `123`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 69 | 69 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 25 | 25 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30604659882 conclusion=failure commit=4474010bb446
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30603803078 conclusion=failure commit=53cc2bd42da5
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30603549277 conclusion=failure commit=82efd511f721
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30603411777 conclusion=failure commit=82efd511f721
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30603270038 conclusion=failure commit=82efd511f721
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30601762879 conclusion=failure commit=82efd511f721
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30601666131 conclusion=failure commit=82efd511f721
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30601496951 conclusion=failure commit=b8662e40dc34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30601494544 conclusion=cancelled commit=b8662e40dc34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30601445239 conclusion=failure commit=b8662e40dc34
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30597951375 conclusion=failure commit=e58ad205a463
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30597865913 conclusion=failure commit=e58ad205a463
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30597677188 conclusion=failure commit=28d44fa0c637
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30597664449 conclusion=failure commit=18e43363ef25
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30597627729 conclusion=failure commit=18e43363ef25
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30596745314 conclusion=failure commit=6f607a3149b3
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30595036148 conclusion=failure commit=0492b686a172
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30595010478 conclusion=failure commit=0492b686a172
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30594952313 conclusion=failure commit=63d9ce6f63f2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30594948809 conclusion=failure commit=63d9ce6f63f2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30594911453 conclusion=failure commit=63d9ce6f63f2
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
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=30604659882
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30603803078
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30603549277
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30603411777
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30603270038
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30601762879
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30601666131
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30601496951
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30601494544
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30601445239
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30597951375
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30597865913
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30597677188
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30597664449
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30597627729
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30596745314
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30595036148
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30595010478
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30594952313
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30594948809
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30594911453
- [ ] github_render_failure_tracker: github_failed_count=21
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=33
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30603803078 conclusion=failure commit=53cc2bd42da55ff01fe623ad94d3e41235330ee6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30603549277 conclusion=failure commit=82efd511f721846e3af570dede5753f5fc5cca52
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30603411777 conclusion=failure commit=82efd511f721846e3af570dede5753f5fc5cca52
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30603270038 conclusion=failure commit=82efd511f721846e3af570dede5753f5fc5cca52
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30601762879 conclusion=failure commit=82efd511f721846e3af570dede5753f5fc5cca52
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30601666131 conclusion=failure commit=82efd511f721846e3af570dede5753f5fc5cca52
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30601496951 conclusion=failure commit=b8662e40dc347dafda12f1dc8b989735e88d211b
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30601494544 conclusion=cancelled commit=b8662e40dc347dafda12f1dc8b989735e88d211b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30601445239 conclusion=failure commit=b8662e40dc347dafda12f1dc8b989735e88d211b
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30600609220 conclusion=failure commit=e58ad205a4636e65320d12ac0e49d35cb9bff63f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30597951375 conclusion=failure commit=e58ad205a4636e65320d12ac0e49d35cb9bff63f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30597865913 conclusion=failure commit=e58ad205a4636e65320d12ac0e49d35cb9bff63f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30597677188 conclusion=failure commit=28d44fa0c637004e345b19dd7a16cd938f5e628a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30597664449 conclusion=failure commit=18e43363ef2525df4975e7dc68b32be9286fcb47
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30597627729 conclusion=failure commit=18e43363ef2525df4975e7dc68b32be9286fcb47
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30596745314 conclusion=failure commit=6f607a3149b3fc6c75f039d2d159348f9f6ca5b6
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30596715602 conclusion=failure commit=0492b686a17232b469797879bf1a697b2dfb0aa3
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30595036148 conclusion=failure commit=0492b686a17232b469797879bf1a697b2dfb0aa3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30595010478 conclusion=failure commit=0492b686a17232b469797879bf1a697b2dfb0aa3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30594952313 conclusion=failure commit=63d9ce6f63f27491b0ccb16c8f53cc4faaf1ce62
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30594948809 conclusion=failure commit=63d9ce6f63f27491b0ccb16c8f53cc4faaf1ce62
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30594911453 conclusion=failure commit=63d9ce6f63f27491b0ccb16c8f53cc4faaf1ce62
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30593829010 conclusion=failure commit=356582edcef94b94daf7503e023188b6ad6d6303
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30591222482 conclusion=failure commit=07602d71bbd75874c1fd3249f98da848b123eb14
- [ ] workflow_failure_tracker: failed_count=24
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
