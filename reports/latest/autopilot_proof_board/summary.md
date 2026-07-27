# System3 Autopilot Latest Status

Generated UTC: `2026-07-27T08:15:32.760210+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `171`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 115 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 42 | 42 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30248625357 conclusion=failure commit=bc2fd873c06c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30248148411 conclusion=failure commit=7777a1e2bb2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30248127611 conclusion=failure commit=7777a1e2bb2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=30248006230 conclusion=failure commit=7777a1e2bb2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=30248002956 conclusion=failure commit=7777a1e2bb2d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Current' run=30247503154 conclusion=failure commit=be5e387a0d82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30247424289 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247424282 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30247424272 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30247424249 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247424202 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30247424191 conclusion=failure commit=dbcb6f9b595b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247382287 conclusion=failure commit=93804c0a7d42
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247382261 conclusion=cancelled commit=93804c0a7d42
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30247382228 conclusion=failure commit=93804c0a7d42
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30247378073 conclusion=failure commit=8a49e8684836
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247378069 conclusion=cancelled commit=8a49e8684836
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247378044 conclusion=failure commit=8a49e8684836
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247367202 conclusion=cancelled commit=0f6fa9f5cee4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30247367189 conclusion=cancelled commit=0f6fa9f5cee4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247367182 conclusion=failure commit=0f6fa9f5cee4
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30247339123 conclusion=failure commit=cc187d4b0358
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30247320093 conclusion=failure commit=917ff64b7d3e
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30247312258 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247311694 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30247311692 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30247306265 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30247306253 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30247306245 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247306229 conclusion=cancelled commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30247306221 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247306194 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247304615 conclusion=cancelled commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30247304543 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247304537 conclusion=failure commit=d633b905dcff
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30247300923 conclusion=failure commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30247300922 conclusion=failure commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30247300908 conclusion=cancelled commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30247300886 conclusion=cancelled commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30247300883 conclusion=failure commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30247300851 conclusion=cancelled commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30247300837 conclusion=failure commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30247300830 conclusion=failure commit=0fbe2a49ae8f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30247297607 conclusion=failure commit=0fbe2a49ae8f
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
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=30248625357
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Auth-Resilient Proof conclusion=failure run=30248148411
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30248127611
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Full Proof conclusion=failure run=30248006230
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=30248002956
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Current conclusion=failure run=30247503154
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=30247424289
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=30247424282
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30247424272
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=30247424249
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247424202
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30247424191
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247382287
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30247382261
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=30247382228
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=30247378073
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30247378069
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247378044
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30247367202
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=30247367189
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247367182
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30247339123
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30247320093
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30247312258
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247311694
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30247311692
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30247306265
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=30247306253
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30247306245
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30247306229
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=30247306221
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30247306194
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
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30246482009 conclusion=failure commit=29e253442037d8eca1fc3187ea48dce8612094d8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Backend Live Simulation Proof' run 30246350310 conclusion=failure commit=29e253442037d8eca1fc3187ea48dce8612094d8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246235472 conclusion=failure commit=1bcd2762045dd815c644294a035bf3ac327b2433
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30246235295 conclusion=failure commit=1bcd2762045dd815c644294a035bf3ac327b2433
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30246226291 conclusion=failure commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30246226057 conclusion=cancelled commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246225594 conclusion=failure commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30246224049 conclusion=failure commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246223459 conclusion=failure commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30246223389 conclusion=cancelled commit=ee42fa8883ff2b8c02f1021cc8115b6204fc076f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246211517 conclusion=failure commit=3f4c3cb60ba55ee5a3e42e77b44434f249ea49e3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246211514 conclusion=failure commit=3f4c3cb60ba55ee5a3e42e77b44434f249ea49e3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30246211475 conclusion=failure commit=3f4c3cb60ba55ee5a3e42e77b44434f249ea49e3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246210318 conclusion=failure commit=3f4c3cb60ba55ee5a3e42e77b44434f249ea49e3
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246188107 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246187936 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Loading Postflight' run 30246186968 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30246186771 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246186703 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246186689 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Proof Strict Gate' run 30246186453 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246186397 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Shell Diagnostic' run 30246186386 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246186359 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30246186319 conclusion=cancelled commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30246186296 conclusion=failure commit=d607232c99986dd079ec661f6f96a5bf5b728544
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246168018 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246167804 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30246167802 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 30246162503 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30246162266 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 Autopilot Proof Board' run 30246162215 conclusion=failure commit=68f682fcb2c7169fe192c0c65581c753c63a4048
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 30246147881 conclusion=cancelled commit=2b0817cbb62a51fb2295ffe02710646b161cd002
- [ ] workflow_failure_tracker: Fix workflow 'System3 Workflow Failure Tracker' run 30246147857 conclusion=failure commit=2b0817cbb62a51fb2295ffe02710646b161cd002
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Issue Tracker' run 30246147822 conclusion=failure commit=2b0817cbb62a51fb2295ffe02710646b161cd002
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Deploy Provenance Gate' run 30246123798 conclusion=failure commit=bb452a3b833cef2ddaddda199412b09ab9e914c5
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 30246093164 conclusion=failure commit=bb452a3b833cef2ddaddda199412b09ab9e914c5
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30246035508 conclusion=failure commit=9805607926359ec597ab5b4c033f8fa00c8632bf
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30245324410 conclusion=failure commit=fbc35c153f7e73179aae3ea1a624c420a6d78ae8
- [ ] workflow_failure_tracker: Fix workflow 'System3 Experimental Solution Planner' run 30245228580 conclusion=failure commit=7c922eb3d011a1a6a412e3818412e89f6d755836
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30245228564 conclusion=failure commit=7c922eb3d011a1a6a412e3818412e89f6d755836
- [ ] workflow_failure_tracker: failed_count=41
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
