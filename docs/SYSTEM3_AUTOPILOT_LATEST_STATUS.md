# System3 Autopilot Latest Status

Generated UTC: `2026-07-28T10:56:44.095271+00:00`
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30352644970 conclusion=failure commit=b91ca22358bc
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30351155034 conclusion=failure commit=65d96ec930d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30350494050 conclusion=failure commit=65d96ec930d4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30350112599 conclusion=failure commit=34ed26faecc0
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30349924422 conclusion=failure commit=34ed26faecc0
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30349914009 conclusion=failure commit=34ed26faecc0
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30349743287 conclusion=cancelled commit=d2120afef885
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30349679482 conclusion=failure commit=d47bd2d3e66f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30349655071 conclusion=failure commit=d47bd2d3e66f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30348832285 conclusion=failure commit=d47bd2d3e66f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30348396129 conclusion=failure commit=bb084700c53c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30347061917 conclusion=failure commit=1aff2bc4f33a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=30346571764 conclusion=failure commit=1aff2bc4f33a
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Permanent Repo Render Safety' run=30346314287 conclusion=failure commit=8a7d80ac57d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=30345927039 conclusion=failure commit=8a7d80ac57d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Backend Live Simulation Proof' run=30345829820 conclusion=failure commit=8a7d80ac57d9
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Workflow Failure Tracker' run=30345661324 conclusion=failure commit=8e5586894cee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30345657943 conclusion=cancelled commit=8e5586894cee
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Deploy Provenance Gate' run=30345617351 conclusion=failure commit=d93e1c32d1f1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=30345573759 conclusion=failure commit=d93e1c32d1f1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=30344652684 conclusion=failure commit=d93e1c32d1f1
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=30344311581 conclusion=failure commit=f194e3c4401d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=30342803984 conclusion=failure commit=c2d535f39146
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
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30352644970
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30351155034
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30350494050
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30350112599
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30349924422
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30349914009
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30349743287
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30349679482
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30349655071
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30348832285
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30348396129
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30347061917
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=30346571764
- [ ] github_render_failure_tracker: workflow=Permanent Repo Render Safety conclusion=failure run=30346314287
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=30345927039
- [ ] github_render_failure_tracker: workflow=System3 Backend Live Simulation Proof conclusion=failure run=30345829820
- [ ] github_render_failure_tracker: workflow=System3 Workflow Failure Tracker conclusion=failure run=30345661324
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=30345657943
- [ ] github_render_failure_tracker: workflow=Dashboard Deploy Provenance Gate conclusion=failure run=30345617351
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=30345573759
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=30344652684
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=30344311581
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=30342803984
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30349924422 conclusion=failure commit=34ed26faecc0df75c421201984f2183b7b9fe626
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30349914009 conclusion=failure commit=34ed26faecc0df75c421201984f2183b7b9fe626
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30349743287 conclusion=cancelled commit=d2120afef885d0b64d9221e3e91f75a8d9a2b05e
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30349679482 conclusion=failure commit=d47bd2d3e66f8297b46bd9dd7079c988a99aac10
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30349655071 conclusion=failure commit=d47bd2d3e66f8297b46bd9dd7079c988a99aac10
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30348832285 conclusion=failure commit=d47bd2d3e66f8297b46bd9dd7079c988a99aac10
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30348625193 conclusion=failure commit=bb084700c53ce4a4bd6e278a4c9e80c6ec27814d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30348396129 conclusion=failure commit=bb084700c53ce4a4bd6e278a4c9e80c6ec27814d
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30347061917 conclusion=failure commit=1aff2bc4f33a5909edd13402dbaca0a6acf8809f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30346571764 conclusion=failure commit=1aff2bc4f33a5909edd13402dbaca0a6acf8809f
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30346314287 conclusion=failure commit=8a7d80ac57d9f8f9bb47c2cc253783c6e32fb339
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30345927039 conclusion=failure commit=8a7d80ac57d9f8f9bb47c2cc253783c6e32fb339
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30345829820 conclusion=failure commit=8a7d80ac57d9f8f9bb47c2cc253783c6e32fb339
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30345661324 conclusion=failure commit=8e5586894cee5a86e4c387220f65abe543dd4a54
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30345657943 conclusion=cancelled commit=8e5586894cee5a86e4c387220f65abe543dd4a54
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30345617351 conclusion=failure commit=d93e1c32d1f111c2264627c9767a70f54c14a2b9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30345573759 conclusion=failure commit=d93e1c32d1f111c2264627c9767a70f54c14a2b9
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30344652684 conclusion=failure commit=d93e1c32d1f111c2264627c9767a70f54c14a2b9
- [ ] workflow_failure_tracker: Fix workflow 'System3 GitHub Render Failure Tracker' run 30344436830 conclusion=failure commit=f194e3c4401de2e061fe0d7462a8830ed84e4889
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 30344311581 conclusion=failure commit=f194e3c4401de2e061fe0d7462a8830ed84e4889
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30342803984 conclusion=failure commit=c2d535f391466de185e052610c6943af749bea96
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 30341969887 conclusion=failure commit=c2d535f391466de185e052610c6943af749bea96
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30341683957 conclusion=failure commit=e7bf134542d7461790c4ac5a129ff6e3ebd353dd
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30341098833 conclusion=failure commit=e7bf134542d7461790c4ac5a129ff6e3ebd353dd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30341096530 conclusion=failure commit=e7bf134542d7461790c4ac5a129ff6e3ebd353dd
- [ ] workflow_failure_tracker: Fix workflow 'System3 Render Worker Preflight' run 30340974341 conclusion=failure commit=cfd53dd2ba2fe17d478ea15cb653ca488e164b99
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30340924942 conclusion=cancelled commit=5badd8cb26156482e1ed00ea9a870ced55aa9782
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
