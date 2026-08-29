# System3 Autopilot Latest Status

**HISTORICAL / NON-AUTHORITATIVE.** Captured `2026-08-06`. Render.com hosting rows below are retired. Production is GCP Cloud Run only.

Generated UTC: `2026-08-06T04:53:20.235085+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `107`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 59 | 59 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 14 | 14 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 17 | 17 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31072227900 conclusion=cancelled commit=745d23645f4f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31072136466 conclusion=cancelled commit=f93ba7008145
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Isolated' run=31072110264 conclusion=failure commit=b6b6971ddc74
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=31072110263 conclusion=failure commit=b6b6971ddc74
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Warmed' run=31072110219 conclusion=failure commit=b6b6971ddc74
- [ ] github_render_failure_tracker: Fix GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31072109743 conclusion=failure commit=b6b6971ddc74
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Windows Self-Hosted Workflow Migration' run=31071564183 conclusion=failure commit=7383995be877
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Broker Chain Semantic Gate' run=31070786177 conclusion=failure commit=9b2e1cb3f646
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Full Auto Truth' run=31070258869 conclusion=failure commit=9b2e1cb3f646
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31070192402 conclusion=cancelled commit=7fbd63bc5d82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Live UI Proof' run=31070157864 conclusion=failure commit=7fbd63bc5d82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31070075697 conclusion=cancelled commit=2dca37b2adf7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31070069295 conclusion=cancelled commit=6537ead6601c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Latest Truth Publish' run=31070069043 conclusion=failure commit=6537ead6601c
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=31070054493 conclusion=cancelled commit=c988960a5bb3
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Cloud Runtime Check' run=31070022696 conclusion=cancelled commit=089ac5aa2476
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Production Proof' run=31070022635 conclusion=failure commit=089ac5aa2476
- [ ] github_render_failure_tracker: Fix GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=31070022062 conclusion=failure commit=089ac5aa2476
- [ ] github_render_failure_tracker: Fix Render endpoint /: HTTP status 0 status=0
- [ ] github_render_failure_tracker: Fix Render endpoint /api/state: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/deploy/info: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/diagnose: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/funds: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/holdings: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/broker/positions/live: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/scanner/top_contract_gainers: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/paper: HTTP status 401 status=401
- [ ] github_render_failure_tracker: Fix Render endpoint /api/ml/performance: HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/ reason=HTTP status 0 status=0
- [ ] github_render_failure_tracker: endpoint=/api/state reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/deploy/info reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/diagnose reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/funds reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/holdings reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/broker/positions/live reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/scanner/top_contract_gainers reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/paper reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: endpoint=/api/ml/performance reason=HTTP status 401 status=401
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31072227900
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31072136466
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Isolated conclusion=failure run=31072110264
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=31072110263
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Warmed conclusion=failure run=31072110219
- [ ] github_render_failure_tracker: workflow=.github/workflows/options-ml-training-proof.yml conclusion=failure run=31072109743
- [ ] github_render_failure_tracker: workflow=System3 Windows Self-Hosted Workflow Migration conclusion=failure run=31071564183
- [ ] github_render_failure_tracker: workflow=System3 Broker Chain Semantic Gate conclusion=failure run=31070786177
- [ ] github_render_failure_tracker: workflow=System3 Full Auto Truth conclusion=failure run=31070258869
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31070192402
- [ ] github_render_failure_tracker: workflow=Dashboard Live UI Proof conclusion=failure run=31070157864
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31070075697
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31070069295
- [ ] github_render_failure_tracker: workflow=System3 Latest Truth Publish conclusion=failure run=31070069043
- [ ] github_render_failure_tracker: workflow=System3 1000 Point TODO Status Updater conclusion=cancelled run=31070054493
- [ ] github_render_failure_tracker: workflow=Cloud Runtime Check conclusion=cancelled run=31070022696
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Production Proof conclusion=failure run=31070022635
- [ ] github_render_failure_tracker: workflow=.github/workflows/options-ml-training-proof.yml conclusion=failure run=31070022062
- [ ] github_render_failure_tracker: github_failed_count=18
- [ ] github_render_failure_tracker: render_failed_count=10
- [ ] github_render_failure_tracker: todo_count=28
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 31072136466 conclusion=cancelled commit=f93ba7008145347a1c48a2820b2f825515b98ee6
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Isolated' run 31072110264 conclusion=failure commit=b6b6971ddc74324f38dee39dbb35899fbff47c31
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 31072110263 conclusion=failure commit=b6b6971ddc74324f38dee39dbb35899fbff47c31
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 31072109743 conclusion=failure commit=b6b6971ddc74324f38dee39dbb35899fbff47c31
- [ ] workflow_failure_tracker: Fix workflow 'System3 Windows Self-Hosted Workflow Migration' run 31071564183 conclusion=failure commit=7383995be8778621321ffb6f225ca86dfe5af069
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 31070786177 conclusion=failure commit=9b2e1cb3f646988c080754fc61b9659a377235fb
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Auto Truth' run 31070258869 conclusion=failure commit=9b2e1cb3f646988c080754fc61b9659a377235fb
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 31070192402 conclusion=cancelled commit=7fbd63bc5d8291b4fa418fb4eaec298e2be5eb69
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 31070157864 conclusion=failure commit=7fbd63bc5d8291b4fa418fb4eaec298e2be5eb69
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 31070075697 conclusion=cancelled commit=2dca37b2adf7c1bf9172953d8944d9cff10b3947
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 31070069295 conclusion=cancelled commit=6537ead6601cb9ba6bfa08924133795fcf91442b
- [ ] workflow_failure_tracker: Fix workflow 'System3 Latest Truth Publish' run 31070069043 conclusion=failure commit=6537ead6601cb9ba6bfa08924133795fcf91442b
- [ ] workflow_failure_tracker: Fix workflow 'System3 1000 Point TODO Status Updater' run 31070054493 conclusion=cancelled commit=c988960a5bb30d64143c156ec7d4efa2d79dd510
- [ ] workflow_failure_tracker: Fix workflow 'Cloud Runtime Check' run 31070022696 conclusion=cancelled commit=089ac5aa247637d7d6b7a14a256d50d6e0c7dc7a
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visual Production Proof' run 31070022635 conclusion=failure commit=089ac5aa247637d7d6b7a14a256d50d6e0c7dc7a
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 31070022062 conclusion=failure commit=089ac5aa247637d7d6b7a14a256d50d6e0c7dc7a
- [ ] workflow_failure_tracker: failed_count=16
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
