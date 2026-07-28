# System3 Autopilot Latest Status

Generated UTC: `2026-07-28T07:56:56.559893+00:00`
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
| github_render_failure_tracker | BLOCKED | BLOCKED | 77 | 77 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30340277618 conclusion=failure commit=584d0d1f6f52
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30338874821 conclusion=failure commit=5f1d7a7c89b1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30338163800 conclusion=failure commit=5f1d7a7c89b1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30337748883 conclusion=failure commit=5f1d7a7c89b1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30337647288 conclusion=failure commit=5f1d7a7c89b1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30337466788 conclusion=failure commit=f0b5560047a9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30337434767 conclusion=failure commit=9c02af797bdc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30337431220 conclusion=cancelled commit=9c02af797bdc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30337363755 conclusion=failure commit=9c02af797bdc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30336836891 conclusion=failure commit=95d387aa6d03
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30336515381 conclusion=failure commit=95d387aa6d03
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30336199126 conclusion=failure commit=017394f9223e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30335073887 conclusion=failure commit=d930f909985f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30334255541 conclusion=failure commit=d930f909985f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30332044864 conclusion=failure commit=c46f9f8b0c6e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30331922368 conclusion=failure commit=c46f9f8b0c6e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30331874465 conclusion=failure commit=c46f9f8b0c6e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30331835497 conclusion=failure commit=c46f9f8b0c6e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30331555641 conclusion=failure commit=c46f9f8b0c6e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30331513723 conclusion=failure commit=c95abab3c363
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30331497114 conclusion=cancelled commit=4ea276f53f55
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Render Worker Preflight' run=30331460244 conclusion=failure commit=9bbbc6754d7d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30331446555 conclusion=failure commit=9bbbc6754d7d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30331430006 conclusion=failure commit=9bbbc6754d7d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Market Session Proof Runner' run=30331346641 conclusion=failure commit=9bbbc6754d7d
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
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30340277618
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30338874821
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30338163800
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30337748883
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30337647288
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30337466788
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30337434767
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30337431220
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30337363755
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30336836891
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30336515381
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30336199126
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30335073887
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30334255541
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30332044864
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30331922368
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30331874465
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30331835497
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30331555641
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30331513723
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30331497114
- [ ] github_render_failure_tracker: workflow=System3 Render Worker Preflight conclusion=failure run=30331460244
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30331446555
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30331430006
- [ ] github_render_failure_tracker: workflow=System3 Market Session Proof Runner conclusion=failure run=30331346641
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
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30337363755 conclusion=failure commit=9c02af797bdcebf390a1d06a89a0b6f8699a8fb3
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30336515381 conclusion=failure commit=95d387aa6d031ed7546acdad9522fd9c3d637dae
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30336344871 conclusion=failure commit=017394f9223e585c97e0aee3941f3d59b512f86a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30336199126 conclusion=failure commit=017394f9223e585c97e0aee3941f3d59b512f86a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30335073887 conclusion=failure commit=d930f909985fee793898e9a4619aeb6edf5d61f0
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30334255541 conclusion=failure commit=d930f909985fee793898e9a4619aeb6edf5d61f0
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30332044864 conclusion=failure commit=c46f9f8b0c6ed9f83301e8b99c658fc862aa117f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30331922368 conclusion=failure commit=c46f9f8b0c6ed9f83301e8b99c658fc862aa117f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30331874465 conclusion=failure commit=c46f9f8b0c6ed9f83301e8b99c658fc862aa117f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30331835497 conclusion=failure commit=c46f9f8b0c6ed9f83301e8b99c658fc862aa117f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30331555641 conclusion=failure commit=c46f9f8b0c6ed9f83301e8b99c658fc862aa117f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30331513723 conclusion=failure commit=c95abab3c363349c366ae8b2959d174a53897d9a
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30331497114 conclusion=cancelled commit=4ea276f53f55c512b91413707fc7fbf5c7211924
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30331460244 conclusion=failure commit=9bbbc6754d7df5694b295628206383711b8538c7
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30331446555 conclusion=failure commit=9bbbc6754d7df5694b295628206383711b8538c7
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30331430006 conclusion=failure commit=9bbbc6754d7df5694b295628206383711b8538c7
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30331346641 conclusion=failure commit=9bbbc6754d7df5694b295628206383711b8538c7
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30330827813 conclusion=failure commit=9bbbc6754d7df5694b295628206383711b8538c7
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30330486148 conclusion=failure commit=60d677749f1dc6fb13c2d3869063845d21ed4ecc
- [ ] workflow_failure_tracker: Fix workflow 'System3 Market Session Proof Runner' run 30329865959 conclusion=failure commit=5864f3041098109e8c2a366a134127f771f7a7c0
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 30329029225 conclusion=failure commit=8cb5155b40be5725e8f35628aec72c8186b807a6
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30328269745 conclusion=failure commit=a95b3cc0282b6e0077520c5d80d57fff503f8046
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30327750520 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30327626674 conclusion=failure commit=ec440ea6a6b7c5a8498749ffa8eb0132483a1f2d
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
