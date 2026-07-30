# System3 Autopilot Latest Status

Generated UTC: `2026-07-30T10:50:33.659345+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `120`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 67 | 67 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 24 | 24 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30534954095 conclusion=failure commit=bb14f331336d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30534239093 conclusion=failure commit=dace81cc85fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30534130703 conclusion=failure commit=dace81cc85fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30533957332 conclusion=failure commit=dace81cc85fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30533379625 conclusion=failure commit=dace81cc85fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30533358190 conclusion=failure commit=dace81cc85fa
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30533222669 conclusion=cancelled commit=9e85cf389172
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30533172853 conclusion=failure commit=ae505c0096d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30533167224 conclusion=failure commit=ae505c0096d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30531048203 conclusion=failure commit=caa546145b36
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30530441382 conclusion=failure commit=a95d6dabedbc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30530338958 conclusion=failure commit=a95d6dabedbc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30530252605 conclusion=failure commit=a95d6dabedbc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30529957961 conclusion=failure commit=a95d6dabedbc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30529883433 conclusion=failure commit=a95d6dabedbc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30529714649 conclusion=failure commit=b67ccebd6f31
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30529706045 conclusion=failure commit=b67ccebd6f31
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30529703356 conclusion=cancelled commit=b67ccebd6f31
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30529644761 conclusion=failure commit=b67ccebd6f31
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30527034181 conclusion=failure commit=c65da5f414e0
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
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30534954095
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30534239093
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30534130703
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30533957332
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30533379625
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30533358190
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30533222669
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30533172853
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30533167224
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30531048203
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30530441382
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30530338958
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30530252605
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30529957961
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30529883433
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30529714649
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30529706045
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30529703356
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30529644761
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30527034181
- [ ] github_render_failure_tracker: github_failed_count=20
- [ ] github_render_failure_tracker: render_failed_count=12
- [ ] github_render_failure_tracker: todo_count=32
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30535770566 conclusion=failure commit=dada07591a96628e978d2dbf709ccc4a322a0614
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30534954095 conclusion=failure commit=bb14f331336dfc98de8918711b9789b752f018de
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30534130703 conclusion=failure commit=dace81cc85fae324f1686947e44189c18966bca5
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30533957332 conclusion=failure commit=dace81cc85fae324f1686947e44189c18966bca5
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30533379625 conclusion=failure commit=dace81cc85fae324f1686947e44189c18966bca5
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30533358190 conclusion=failure commit=dace81cc85fae324f1686947e44189c18966bca5
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30533222669 conclusion=cancelled commit=9e85cf38917286e8f3c99c5fabe7bffd5e665ace
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30533172853 conclusion=failure commit=ae505c0096d4a385a5e9a14aa94a028c4229473a
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30533167224 conclusion=failure commit=ae505c0096d4a385a5e9a14aa94a028c4229473a
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30532380667 conclusion=failure commit=55ed684ccee28a4f99b868dcb59d9cdc4f94b6a2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30531048203 conclusion=failure commit=caa546145b36548ed8c154fba03800434edcea6a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30530441382 conclusion=failure commit=a95d6dabedbc5b93a45963b5489266ccc0870b69
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30530338958 conclusion=failure commit=a95d6dabedbc5b93a45963b5489266ccc0870b69
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30530252605 conclusion=failure commit=a95d6dabedbc5b93a45963b5489266ccc0870b69
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30529957961 conclusion=failure commit=a95d6dabedbc5b93a45963b5489266ccc0870b69
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30529883433 conclusion=failure commit=a95d6dabedbc5b93a45963b5489266ccc0870b69
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30529714649 conclusion=failure commit=b67ccebd6f311c27bfccbe2dc4d09ea86004a7aa
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30529706045 conclusion=failure commit=b67ccebd6f311c27bfccbe2dc4d09ea86004a7aa
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30529703356 conclusion=cancelled commit=b67ccebd6f311c27bfccbe2dc4d09ea86004a7aa
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30529644761 conclusion=failure commit=b67ccebd6f311c27bfccbe2dc4d09ea86004a7aa
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30528604162 conclusion=failure commit=658ba250df777ce1bcc2053b3f9e3a02cb4f4fbe
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30527034181 conclusion=failure commit=c65da5f414e0b00a1845877cb2a6fbb35bfe8557
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30526243449 conclusion=failure commit=fb8c1d5af900f9ee517d91a11f1b24e5c0647af5
- [ ] workflow_failure_tracker: failed_count=23
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
