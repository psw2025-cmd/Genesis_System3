# System3 Autopilot Latest Status

Generated UTC: `2026-08-05T07:59:13.619605+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `91`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 47 | 47 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 13 | 13 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30985502041 conclusion=failure commit=9394792e893c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30984828519 conclusion=failure commit=9394792e893c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30984661000 conclusion=cancelled commit=d7d2a3286e99
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30983968945 conclusion=failure commit=8262ef37f0c9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30983489689 conclusion=failure commit=8262ef37f0c9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30981649158 conclusion=failure commit=abb67e4660ad
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30978681834 conclusion=cancelled commit=f3e1691619ce
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30978521783 conclusion=failure commit=bb8e6733b2a5
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30978378566 conclusion=failure commit=bb8e6733b2a5
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30978284089 conclusion=failure commit=bb8e6733b2a5
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30977879324 conclusion=failure commit=7a037cdf3917
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Market Session Proof Runner' run=30977802143 conclusion=failure commit=7a037cdf3917
- [ ] github_render_failure_tracker: Fix Render endpoint /ui/: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/ui/ reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30985502041
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30984828519
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30984661000
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30983968945
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30983489689
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30981649158
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30978681834
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30978521783
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30978378566
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30978284089
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30977879324
- [ ] github_render_failure_tracker: workflow=System3 Market Session Proof Runner conclusion=failure run=30977802143
- [ ] github_render_failure_tracker: github_failed_count=12
- [ ] github_render_failure_tracker: render_failed_count=10
- [ ] github_render_failure_tracker: todo_count=22
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
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30983968945 conclusion=failure commit=8262ef37f0c907c42092003ab063612c4660bfc6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30983489689 conclusion=failure commit=8262ef37f0c907c42092003ab063612c4660bfc6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30981649158 conclusion=failure commit=abb67e4660ad6a1b0af8e636768b2d64a08d39ad
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30978681834 conclusion=cancelled commit=f3e1691619ced3518b8ad2846def31beaf3b8ebd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30978521783 conclusion=failure commit=bb8e6733b2a56666efe9795748cc81b2f2ec562f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30978378566 conclusion=failure commit=bb8e6733b2a56666efe9795748cc81b2f2ec562f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30978284089 conclusion=failure commit=bb8e6733b2a56666efe9795748cc81b2f2ec562f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30977879324 conclusion=failure commit=7a037cdf3917f88094f8a5bb4746e73da5fcf85e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30977802143 conclusion=failure commit=7a037cdf3917f88094f8a5bb4746e73da5fcf85e
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30976302634 conclusion=failure commit=e7af8bdab7192da3401783cddf90e82e91cbf670
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30975436979 conclusion=failure commit=8e8d5146dbcbd3140c212023e2ad178cd880d1a2
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30974642043 conclusion=failure commit=872ab7a222f03db005f27bc5ea338611935ab8e1
- [ ] workflow_failure_tracker: failed_count=12
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
