# System3 Autopilot Latest Status

Generated UTC: `2026-08-03T05:05:25.891383+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `130`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 73 | 73 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 28 | 28 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30785078018 conclusion=failure commit=f660e3fc0791
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30784185467 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30783983185 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30783856816 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30783740900 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30783663403 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30781982921 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30781893382 conclusion=failure commit=d3ea26dc2fad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30781728600 conclusion=failure commit=f20fa4e83fdf
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30781721848 conclusion=cancelled commit=f20fa4e83fdf
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30781681375 conclusion=failure commit=f20fa4e83fdf
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30778324545 conclusion=failure commit=1a968cc6d713
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30778239397 conclusion=failure commit=1a968cc6d713
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30778074581 conclusion=failure commit=0ee654eaca0d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30778069238 conclusion=cancelled commit=0ee654eaca0d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30778027784 conclusion=failure commit=0ee654eaca0d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30777241590 conclusion=cancelled commit=49b90c4e1bf8
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30775716717 conclusion=failure commit=7bebcf17c0be
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30775709161 conclusion=failure commit=7bebcf17c0be
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30775676213 conclusion=cancelled commit=faa411f70c73
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30775676202 conclusion=failure commit=faa411f70c73
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30775653691 conclusion=failure commit=456b35882814
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30775640519 conclusion=failure commit=456b35882814
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
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=30785078018
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30784185467
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30783983185
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30783856816
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30783740900
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30783663403
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30781982921
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30781893382
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30781728600
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30781721848
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30781681375
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30778324545
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30778239397
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30778074581
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30778069238
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30778027784
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30777241590
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30775716717
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30775709161
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30775676213
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30775676202
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30775653691
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30775640519
- [ ] github_render_failure_tracker: github_failed_count=23
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=35
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30785078018 conclusion=failure commit=f660e3fc0791b468360445968dab52e9042466e5
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30784185467 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30783983185 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30783856816 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30783740900 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30783663403 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30781982921 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30781893382 conclusion=failure commit=d3ea26dc2fad2bddf7c3a6237aff959eaf544a5b
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30781728600 conclusion=failure commit=f20fa4e83fdf0ae83b3cfdc3694ac0aa839834f6
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30781721848 conclusion=cancelled commit=f20fa4e83fdf0ae83b3cfdc3694ac0aa839834f6
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30781681375 conclusion=failure commit=f20fa4e83fdf0ae83b3cfdc3694ac0aa839834f6
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30780833429 conclusion=failure commit=1a968cc6d7139e66d55bc6fbabbaf8a70a77b711
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30778324545 conclusion=failure commit=1a968cc6d7139e66d55bc6fbabbaf8a70a77b711
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30778239397 conclusion=failure commit=1a968cc6d7139e66d55bc6fbabbaf8a70a77b711
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30778074581 conclusion=failure commit=0ee654eaca0de5bc7ba85bf9caf2c999ee79c0d7
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30778069238 conclusion=cancelled commit=0ee654eaca0de5bc7ba85bf9caf2c999ee79c0d7
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30778027784 conclusion=failure commit=0ee654eaca0de5bc7ba85bf9caf2c999ee79c0d7
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30777241590 conclusion=cancelled commit=49b90c4e1bf8e8e962b3501205e99b04b07fa65d
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30777227385 conclusion=failure commit=7bebcf17c0bedbc875ddfe8c10b344e5d09bdde6
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30775716717 conclusion=failure commit=7bebcf17c0bedbc875ddfe8c10b344e5d09bdde6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30775709161 conclusion=failure commit=7bebcf17c0bedbc875ddfe8c10b344e5d09bdde6
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30775676213 conclusion=cancelled commit=faa411f70c7386660d5a6734d6787d8df164cec0
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30775676202 conclusion=failure commit=faa411f70c7386660d5a6734d6787d8df164cec0
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30775653691 conclusion=failure commit=456b3588281420a9a9edd66642e34fbd5144b857
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30775640519 conclusion=failure commit=456b3588281420a9a9edd66642e34fbd5144b857
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30774713128 conclusion=failure commit=0d4dddc4d3572d3eb2f199f87e53c08d501b11b0
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30772741755 conclusion=failure commit=f331fae7aa690382e593ff346985857af2f9abb2
- [ ] workflow_failure_tracker: failed_count=27
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
