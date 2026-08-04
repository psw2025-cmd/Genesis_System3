# System3 Autopilot Latest Status

Generated UTC: `2026-08-04T07:57:30.731329+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `96`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 49 | 49 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 16 | 16 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30888283706 conclusion=failure commit=b5e3df14d061
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30887450550 conclusion=cancelled commit=07d37edda9fd
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30886713340 conclusion=failure commit=1ef3f1062dd2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30886118168 conclusion=failure commit=ed029e39a626
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30885769366 conclusion=failure commit=ed029e39a626
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30885429205 conclusion=failure commit=a6cdb4bf8a12
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30884273294 conclusion=failure commit=033bc303c6ec
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30881139797 conclusion=failure commit=764bc2f04682
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30880990985 conclusion=failure commit=764bc2f04682
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30880937571 conclusion=failure commit=764bc2f04682
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30880900088 conclusion=failure commit=764bc2f04682
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30880821045 conclusion=cancelled commit=e8b6af05cf3c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30880454597 conclusion=failure commit=e205e884b932
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Market Session Proof Runner' run=30880379233 conclusion=failure commit=e205e884b932
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30888283706
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30887450550
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30886713340
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30886118168
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30885769366
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30885429205
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30884273294
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30881139797
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30880990985
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30880937571
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30880900088
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30880821045
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30880454597
- [ ] github_render_failure_tracker: workflow=System3 Market Session Proof Runner conclusion=failure run=30880379233
- [ ] github_render_failure_tracker: github_failed_count=14
- [ ] github_render_failure_tracker: render_failed_count=9
- [ ] github_render_failure_tracker: todo_count=23
- [ ] parallel_root_cause_audit: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- [ ] parallel_root_cause_audit: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.
- [ ] parallel_root_cause_audit: Public truth final verdict is FAIL.
- [ ] parallel_root_cause_audit: Need compare public truth commit with latest repository head and Render deploy info; static repo audit cannot prove Render freshness.
- [ ] parallel_root_cause_audit: Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.
- [ ] parallel_root_cause_audit: Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.
- [ ] parallel_root_cause_audit: Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.
- [ ] parallel_root_cause_audit: Trading router may be inactive if app.py duplicate routes are authoritative.
- [ ] parallel_root_cause_audit: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.
- [ ] parallel_root_cause_audit: Options ML training summary is missing/not published.
- [ ] parallel_root_cause_audit: Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.
- [ ] parallel_root_cause_audit: Need fresh screenshot after latest commits; older screenshots do not prove current UI.
- [ ] parallel_root_cause_audit: Final public truth is FAIL.
- [ ] parallel_root_cause_audit: Final truth must aggregate latest Render, integration, visual, broker, chain, scanner, paper, ML proof.
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30886713340 conclusion=failure commit=1ef3f1062dd27742654d8ec9a86695eda5777a63
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30886118168 conclusion=failure commit=ed029e39a6263841759bf16bee737091907e4f36
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30885769366 conclusion=failure commit=ed029e39a6263841759bf16bee737091907e4f36
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30885429205 conclusion=failure commit=a6cdb4bf8a127b698f52b8c8c5005c3785008bfe
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30884273294 conclusion=failure commit=033bc303c6ec0e6bbe7d50fa3626b11e4429095d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30881139797 conclusion=failure commit=764bc2f04682b76b0b67b13b7163f5ace58ffe1d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30880990985 conclusion=failure commit=764bc2f04682b76b0b67b13b7163f5ace58ffe1d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30880937571 conclusion=failure commit=764bc2f04682b76b0b67b13b7163f5ace58ffe1d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30880900088 conclusion=failure commit=764bc2f04682b76b0b67b13b7163f5ace58ffe1d
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30880821045 conclusion=cancelled commit=e8b6af05cf3c6c5e41d9a6dd4ea12f686a8e679f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30880454597 conclusion=failure commit=e205e884b932c96cb272f0979431d425a5358d14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30880379233 conclusion=failure commit=e205e884b932c96cb272f0979431d425a5358d14
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30878847972 conclusion=failure commit=44a0832b4b8c394ce7215eaf48b8f34e3ffc59d3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30878032560 conclusion=failure commit=1c1e167acbabaff304cde38aefdf7fdf291fbbfb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30877188043 conclusion=failure commit=6b4b1e5674f7b902043bda8a37455e588cf291f8
- [ ] workflow_failure_tracker: failed_count=15
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
