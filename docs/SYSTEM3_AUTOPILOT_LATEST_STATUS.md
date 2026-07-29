# System3 Autopilot Latest Status

Generated UTC: `2026-07-29T08:00:11.595650+00:00`
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30433707601 conclusion=failure commit=506c561f061c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30432291205 conclusion=failure commit=8268c18b8b55
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30431087391 conclusion=failure commit=c427dcdb223a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30431004435 conclusion=failure commit=c427dcdb223a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30430792027 conclusion=failure commit=705dfc2b1f90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30430780878 conclusion=cancelled commit=705dfc2b1f90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30430727483 conclusion=failure commit=705dfc2b1f90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30430264048 conclusion=failure commit=705dfc2b1f90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30429941372 conclusion=failure commit=705dfc2b1f90
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30429619719 conclusion=failure commit=e4358af40c1d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30429429276 conclusion=failure commit=e4358af40c1d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30428734659 conclusion=failure commit=e47e51cec233
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30425688291 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30425495353 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30425453462 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30425421611 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30425397734 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30425225556 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30425167133 conclusion=failure commit=90922c9a581c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30425022292 conclusion=failure commit=adc441ea55d3
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30424989935 conclusion=failure commit=c5d22f4c93b2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30424988995 conclusion=cancelled commit=c5d22f4c93b2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30424945631 conclusion=failure commit=30681c9fb89e
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
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30433707601
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30432291205
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30431087391
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30431004435
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30430792027
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30430780878
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30430727483
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30430264048
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30429941372
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30429619719
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30429429276
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30428734659
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30425688291
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30425495353
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30425453462
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30425421611
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30425397734
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30425225556
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30425167133
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30425022292
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30424989935
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30424988995
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30424945631
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
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30431087391 conclusion=failure commit=c427dcdb223a2641262e15258c56c00a5afeddd2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30431004435 conclusion=failure commit=c427dcdb223a2641262e15258c56c00a5afeddd2
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30430792027 conclusion=failure commit=705dfc2b1f90dc8f1c57968e88f98a70b084bf38
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30430780878 conclusion=cancelled commit=705dfc2b1f90dc8f1c57968e88f98a70b084bf38
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30430727483 conclusion=failure commit=705dfc2b1f90dc8f1c57968e88f98a70b084bf38
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30429941372 conclusion=failure commit=705dfc2b1f90dc8f1c57968e88f98a70b084bf38
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30429769566 conclusion=failure commit=e4358af40c1dc3db50022a98e50460858b5c3681
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30429619719 conclusion=failure commit=e4358af40c1dc3db50022a98e50460858b5c3681
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30429429276 conclusion=failure commit=e4358af40c1dc3db50022a98e50460858b5c3681
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30428734659 conclusion=failure commit=e47e51cec2338fe39fa06ebd8f60aa278889f367
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30425688291 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30425495353 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30425453462 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30425421611 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30425397734 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30425225556 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30425167133 conclusion=failure commit=90922c9a581ca9af199116684ddc43b496fa725c
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30425022292 conclusion=failure commit=adc441ea55d3d15411b1a1393bf39d1567d2459d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30424989935 conclusion=failure commit=c5d22f4c93b2188f035d21010e4b7e2d9150f150
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30424988995 conclusion=cancelled commit=c5d22f4c93b2188f035d21010e4b7e2d9150f150
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30424945631 conclusion=failure commit=30681c9fb89e52b57ed63f99d2fb5654dca0a6bf
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30424847319 conclusion=failure commit=30681c9fb89e52b57ed63f99d2fb5654dca0a6bf
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30424019162 conclusion=failure commit=9f36abcc881d981add8c3429a571952ab4b3eaec
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30423486776 conclusion=failure commit=ad3909bc1ce3dec894b2b1c8968f37ebf193c0db
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30422641994 conclusion=failure commit=21176045c6951a2947bc74e5f2a7026e25e47e5a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30421813510 conclusion=failure commit=a99b1938a8ccf8c57df8075cb5749eebe2c1d091
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30421367925 conclusion=failure commit=85a3b7d3f77fcbbfc47c5240ffd3d95eb6b3b595
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
