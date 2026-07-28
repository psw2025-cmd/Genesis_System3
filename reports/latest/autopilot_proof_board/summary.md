# System3 Autopilot Latest Status

Generated UTC: `2026-07-28T04:52:37.601502+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `131`

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
| workflow_failure_tracker | BLOCKED | BLOCKED | 29 | 29 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=30329029225 conclusion=failure commit=8cb5155b40be
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30328269745 conclusion=failure commit=a95b3cc0282b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30327750520 conclusion=failure commit=ec440ea6a6b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30327626674 conclusion=failure commit=ec440ea6a6b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30327469216 conclusion=failure commit=ec440ea6a6b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30325999368 conclusion=failure commit=ec440ea6a6b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30325945634 conclusion=failure commit=ec440ea6a6b7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30325802159 conclusion=failure commit=80004f38ff70
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30325792890 conclusion=cancelled commit=80004f38ff70
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30325750819 conclusion=failure commit=80004f38ff70
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30321988573 conclusion=failure commit=614a25e0ecd1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30321867673 conclusion=failure commit=614a25e0ecd1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30321717896 conclusion=failure commit=8864657cd537
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30321687040 conclusion=failure commit=3c61af99e787
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30321686104 conclusion=cancelled commit=3c61af99e787
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30321635530 conclusion=failure commit=3c61af99e787
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30318608038 conclusion=failure commit=30a2096bc44e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30318606627 conclusion=failure commit=30a2096bc44e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30318554341 conclusion=cancelled commit=96db1ef7813c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30318549692 conclusion=failure commit=7d73a6c33498
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30318546881 conclusion=failure commit=7d73a6c33498
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30318511226 conclusion=failure commit=7d73a6c33498
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30316443824 conclusion=failure commit=dcd6da9169a4
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
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=30329029225
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30328269745
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30327750520
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30327626674
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30327469216
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30325999368
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30325945634
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30325802159
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30325792890
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30325750819
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30321988573
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30321867673
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30321717896
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30321687040
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30321686104
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30321635530
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30318608038
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30318606627
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30318554341
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30318549692
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30318546881
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30318511226
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Auth-Resilient Proof conclusion=failure run=30316443824
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30329029225 conclusion=failure commit=8cb5155b40be5725e8f35628aec72c8186b807a6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30328269745 conclusion=failure commit=a95b3cc0282b6e0077520c5d80d57fff503f8046
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30327750520 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30327626674 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30327469216 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30325999368 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30325945634 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30325802159 conclusion=failure commit=80004f38ff7021ff9dd000a404c78f3ba9691715
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30325792890 conclusion=cancelled commit=80004f38ff7021ff9dd000a404c78f3ba9691715
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30325750819 conclusion=failure commit=80004f38ff7021ff9dd000a404c78f3ba9691715
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30324838537 conclusion=failure commit=614a25e0ecd194cacc547d479694bc06acde57d4
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30321988573 conclusion=failure commit=614a25e0ecd194cacc547d479694bc06acde57d4
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30321867673 conclusion=failure commit=614a25e0ecd194cacc547d479694bc06acde57d4
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30321717896 conclusion=failure commit=8864657cd5371156d7deafef2d9a5d4a47b5c623
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30321687040 conclusion=failure commit=3c61af99e78731a81e763826dcf37b823718590f
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30321686104 conclusion=cancelled commit=3c61af99e78731a81e763826dcf37b823718590f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30321635530 conclusion=failure commit=3c61af99e78731a81e763826dcf37b823718590f
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30320581095 conclusion=failure commit=30a2096bc44e94619353339a571e6d6247df8b28
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30318608038 conclusion=failure commit=30a2096bc44e94619353339a571e6d6247df8b28
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30318606627 conclusion=failure commit=30a2096bc44e94619353339a571e6d6247df8b28
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30318554341 conclusion=cancelled commit=96db1ef7813c4ef274babc3094e80d1642d70e81
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30318549692 conclusion=failure commit=7d73a6c3349858ee20fddc97f9566f61b1f54cfc
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30318546881 conclusion=failure commit=7d73a6c3349858ee20fddc97f9566f61b1f54cfc
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30318511226 conclusion=failure commit=7d73a6c3349858ee20fddc97f9566f61b1f54cfc
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30317486181 conclusion=failure commit=d804ab9f6814e303da6f6df8ee98979040e3d9f8
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Auth-Resilient Proof' run 30316443824 conclusion=failure commit=dcd6da9169a4db15b05d513d078e444f4b40f27c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 30316428933 conclusion=failure commit=dcd6da9169a4db15b05d513d078e444f4b40f27c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Full Proof' run 30316318294 conclusion=failure commit=dcd6da9169a4db15b05d513d078e444f4b40f27c
- [ ] workflow_failure_tracker: failed_count=28
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
