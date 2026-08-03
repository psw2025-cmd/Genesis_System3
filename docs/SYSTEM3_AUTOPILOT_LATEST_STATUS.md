# System3 Autopilot Latest Status

Generated UTC: `2026-08-03T11:15:20.571666+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `135`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 77 | 77 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30805561530 conclusion=failure commit=879be299f3ed
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30805353778 conclusion=failure commit=879be299f3ed
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30805130748 conclusion=failure commit=879be299f3ed
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30804939935 conclusion=failure commit=879be299f3ed
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30804774505 conclusion=failure commit=879be299f3ed
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30803550952 conclusion=cancelled commit=3ae0a30631de
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30803540436 conclusion=cancelled commit=3ae0a30631de
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30803525525 conclusion=cancelled commit=3f5ebe842c79
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30803525061 conclusion=failure commit=3f5ebe842c79
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Cloud Runtime Check' run=30803488350 conclusion=cancelled commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30803488042 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30803488007 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30803487994 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30803487978 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30803487794 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30803487735 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Isolated' run=30803487489 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Parallel Root-Cause Audit' run=30803487416 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=30803485872 conclusion=failure commit=c789ce37a997
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30802012543 conclusion=cancelled commit=120176facf20
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Parallel Root-Cause Audit' run=30801958172 conclusion=failure commit=051ed7b7d458
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30801958107 conclusion=failure commit=051ed7b7d458
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30801958056 conclusion=failure commit=051ed7b7d458
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30801958011 conclusion=failure commit=051ed7b7d458
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dhan Only Data Truth Proof' run=30801957996 conclusion=failure commit=051ed7b7d458
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
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30805561530
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30805353778
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30805130748
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30804939935
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30804774505
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30803550952
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30803540436
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30803525525
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30803525061
- [ ] github_render_failure_tracker: workflow=Cloud Runtime Check conclusion=cancelled run=30803488350
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30803488042
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30803488007
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30803487994
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30803487978
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30803487794
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30803487735
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Isolated conclusion=failure run=30803487489
- [ ] github_render_failure_tracker: workflow=System3 Parallel Root-Cause Audit conclusion=failure run=30803487416
- [ ] github_render_failure_tracker: workflow=.github/workflows/options-ml-training-proof.yml conclusion=failure run=30803485872
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30802012543
- [ ] github_render_failure_tracker: workflow=System3 Parallel Root-Cause Audit conclusion=failure run=30801958172
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30801958107
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30801958056
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30801958011
- [ ] github_render_failure_tracker: workflow=Dhan Only Data Truth Proof conclusion=failure run=30801957996
- [ ] github_render_failure_tracker: github_failed_count=25
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=37
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30805561530 conclusion=failure commit=879be299f3ed25b22bbcf5edb980115db2d56598
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30805130748 conclusion=failure commit=879be299f3ed25b22bbcf5edb980115db2d56598
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30804939935 conclusion=failure commit=879be299f3ed25b22bbcf5edb980115db2d56598
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30804774505 conclusion=failure commit=879be299f3ed25b22bbcf5edb980115db2d56598
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30803550952 conclusion=cancelled commit=3ae0a30631de491802c13f6090b5296218531f8c
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30803540436 conclusion=cancelled commit=3ae0a30631de491802c13f6090b5296218531f8c
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30803525525 conclusion=cancelled commit=3f5ebe842c7945c55429940bf8e199426321ce3d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30803525061 conclusion=failure commit=3f5ebe842c7945c55429940bf8e199426321ce3d
- [ ] workflow_failure_tracker: Fix workflow 'Cloud Runtime Check' run 30803488350 conclusion=cancelled commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30803488042 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30803488007 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30803487994 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30803487978 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30803487794 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30803487735 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Isolated' run 30803487489 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'System3 Parallel Root-Cause Audit' run 30803487416 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 30803485872 conclusion=failure commit=c789ce37a9977ea861814f244d43298bb25e4422
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30802012543 conclusion=cancelled commit=120176facf203d8ac57ce1ff322457fa19ca21ae
- [ ] workflow_failure_tracker: Fix workflow 'System3 Parallel Root-Cause Audit' run 30801958172 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30801958107 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30801958056 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30801958011 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dhan Only Data Truth Proof' run 30801957996 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30801957956 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30801957898 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Isolated' run 30801957877 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30801957834 conclusion=failure commit=051ed7b7d458cf9f35dc18bc2ad6b7fb3a7b299f
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
