# System3 Autopilot Latest Status

Generated UTC: `2026-07-27T05:06:58.984877+00:00`
Owner/operator: **PRITAM S. WARGHADE**
Status: **BLOCKED**
Blockers: `151`

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
| github_render_failure_tracker | BLOCKED | BLOCKED | 100 | 113 |
| parallel_root_cause_audit | BLOCKED | BLOCKED | 12 | 12 |
| workflow_failure_tracker | BLOCKED | BLOCKED | 22 | 22 |
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
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Auth-Resilient Proof' run=30238546733 conclusion=failure commit=1ffb29c8bbd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30238522024 conclusion=failure commit=1ffb29c8bbd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Settle Proof' run=30238403541 conclusion=failure commit=1ffb29c8bbd7
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Proof Current' run=30238121582 conclusion=failure commit=44d0b3a61397
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30238066717 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30238066712 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30238066707 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30238066698 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238066693 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30238066675 conclusion=failure commit=a4dc5cb21c82
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30238042109 conclusion=cancelled commit=99be7a440e7b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30238042104 conclusion=failure commit=99be7a440e7b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238042067 conclusion=failure commit=99be7a440e7b
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30238040728 conclusion=cancelled commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30238040696 conclusion=cancelled commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238040679 conclusion=failure commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238036036 conclusion=failure commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30238036024 conclusion=cancelled commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30238036003 conclusion=failure commit=3c098952254d
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30238018867 conclusion=failure commit=92587b267f9f
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30238005141 conclusion=failure commit=bdf17395dde2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238005136 conclusion=failure commit=bdf17395dde2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30238005099 conclusion=failure commit=bdf17395dde2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30238003928 conclusion=failure commit=bdf17395dde2
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30238001756 conclusion=failure commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30238001735 conclusion=failure commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30238001732 conclusion=cancelled commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30238001729 conclusion=cancelled commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30238001727 conclusion=failure commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30238001718 conclusion=failure commit=589febcf8c02
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30237989232 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30237989189 conclusion=cancelled commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30237989181 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Proof Strict Gate' run=30237989074 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Shell Diagnostic' run=30237989066 conclusion=cancelled commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30237989065 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visual Loading Postflight' run=30237989060 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 1000 Point TODO Status Updater' run=30237989052 conclusion=cancelled commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Safe Repair Runner' run=30237989051 conclusion=cancelled commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Autopilot Proof Board' run=30237989045 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Secure Install Credential Audit' run=30237989037 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'System3 Experimental Solution Planner' run=30237986897 conclusion=failure commit=03908d5c8016
- [ ] github_render_failure_tracker: Fix GitHub workflow 'Dashboard Visible Issue Tracker' run=30237986882 conclusion=cancelled commit=03908d5c8016
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
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Auth-Resilient Proof conclusion=failure run=30238546733
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30238522024
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Settle Proof conclusion=failure run=30238403541
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Proof Current conclusion=failure run=30238121582
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=failure run=30238066717
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=30238066712
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=failure run=30238066707
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30238066698
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238066693
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30238066675
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30238042109
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=30238042104
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238042067
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30238040728
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=cancelled run=30238040696
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238040679
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238036036
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30238036024
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=30238036003
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30238018867
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30238005141
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238005136
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30238005099
- [ ] github_render_failure_tracker: workflow=System3 Autopilot Proof Board conclusion=failure run=30238003928
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Proof Strict Gate conclusion=failure run=30238001756
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30238001735
- [ ] github_render_failure_tracker: workflow=Dashboard Shell Diagnostic conclusion=cancelled run=30238001732
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30238001729
- [ ] github_render_failure_tracker: workflow=System3 Secure Install Credential Audit conclusion=failure run=30238001727
- [ ] github_render_failure_tracker: workflow=Dashboard Visual Loading Postflight conclusion=failure run=30238001718
- [ ] github_render_failure_tracker: workflow=System3 Experimental Solution Planner conclusion=failure run=30237989232
- [ ] github_render_failure_tracker: workflow=System3 Safe Repair Runner conclusion=cancelled run=30237989189
- [ ] github_render_failure_tracker: workflow=Dashboard Visible Issue Tracker conclusion=failure run=30237989181
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
- [ ] workflow_failure_tracker: Fix workflow 'System3 Broker Chain Semantic Gate' run 30237070837 conclusion=failure commit=f3a35d239a9fe5b884b980c2f685069dc3a2512f
- [ ] workflow_failure_tracker: Fix workflow 'System3 Safe Repair Runner' run 30236855888 conclusion=failure commit=75329a8eb8869dd5d584c7db5f7c231b04b84721
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Live UI Proof' run 30236697793 conclusion=failure commit=75329a8eb8869dd5d584c7db5f7c231b04b84721
- [ ] workflow_failure_tracker: Fix workflow 'Permanent Repo Render Safety' run 30236510557 conclusion=failure commit=75329a8eb8869dd5d584c7db5f7c231b04b84721
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Full History' run 30234951537 conclusion=failure commit=d5ea122c9bc1cf6c955ebf329549ac912e4b9b9e
- [ ] workflow_failure_tracker: Fix workflow 'Genesis System3 Global Safety CI' run 30234951531 conclusion=failure commit=d5ea122c9bc1cf6c955ebf329549ac912e4b9b9e
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 30234948894 conclusion=failure commit=d5ea122c9bc1cf6c955ebf329549ac912e4b9b9e
- [ ] workflow_failure_tracker: Fix workflow 'Options Corrected Framework Phase1' run 30234783325 conclusion=failure commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Self-Hosted Model' run 30234783302 conclusion=cancelled commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Artifact Model' run 30234783289 conclusion=cancelled commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Full History' run 30234783277 conclusion=cancelled commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow 'Genesis System3 Global Safety CI' run 30234783276 conclusion=cancelled commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 30234781566 conclusion=failure commit=cd11807b15762fad09c4780c0bc359abdde5495a
- [ ] workflow_failure_tracker: Fix workflow 'Dashboard Visible Proof Warmed' run 30234781527 conclusion=failure commit=75329a8eb8869dd5d584c7db5f7c231b04b84721
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Artifact Model' run 30234761354 conclusion=cancelled commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Self-Hosted Model' run 30234761316 conclusion=cancelled commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow 'Genesis System3 Global Safety CI' run 30234761296 conclusion=cancelled commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow 'System3 Full Non-Live Proof' run 30234761283 conclusion=cancelled commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Full History' run 30234761262 conclusion=cancelled commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 30234759553 conclusion=failure commit=d506687cd01de6adfd5e19745a0b4cc184c05d3a
- [ ] workflow_failure_tracker: Fix workflow 'Options Big-Data Artifact Model' run 30234737765 conclusion=cancelled commit=2f54c0d3cfa8c2b4ff2456579927014eb097a763
- [ ] workflow_failure_tracker: failed_count=21
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
