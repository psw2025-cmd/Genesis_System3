# System3 Experimental Solution Plan

Generated UTC: `2026-07-12T12:03:45.769058+00:00`
Status: **BLOCKED**
Issues: `74`
Fix lanes: `10`

## Rule

Use this plan to fix root causes by lane. Do not claim resolved until proof reports are PASS and live dashboard visual issues are zero.

## Report status

| Report | Status |
|---|---|
| `reports/latest/render_100_agent_swarm/summary.json` | `MISSING` |
| `reports/latest/autopilot_proof_board/summary.json` | `MISSING` |
| `reports/latest/dashboard_visible_issue_tracker/summary.json` | `MISSING` |
| `reports/latest/secure_install_credential_audit/summary.json` | `BLOCKED` |
| `reports/latest/parallel_root_cause_audit/summary.json` | `BLOCKED` |
| `reports/latest/workflow_failure_tracker/summary.json` | `BLOCKED` |
| `reports/latest/todo_status_update/summary.json` | `BLOCKED` |
| `reports/latest/system3_public_truth/index.json` | `FAIL` |

## Fix lanes

### WORKFLOW_CI — 34 issues

Recommended fixes:
- Read workflow_failure_tracker TODO.
- Fix failing workflow logs one by one.
- Keep failed workflows in TODO until later successful run proves fixed.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: missing_report:reports/latest/render_100_agent_swarm/summary.json
- `reports/latest/autopilot_proof_board/summary.json`: missing_report:reports/latest/autopilot_proof_board/summary.json
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: missing_report:reports/latest/dashboard_visible_issue_tracker/summary.json
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29188296601 conclusion=failure commit=325d0b6568aeb4a465cc982265955eb976d915e0
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Cloud Runtime Check' run 29188285899 conclusion=cancelled commit=2b94621fdf90608a12d4a92248da53365c600f17
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29188285890 conclusion=cancelled commit=2b94621fdf90608a12d4a92248da53365c600f17
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29187706168 conclusion=failure commit=4baec3db8f17c88b9652d53c87b2cb6d8ecb34f9
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29187345770 conclusion=cancelled commit=dcc19a7f2572e7a15523516f4ba8fb77b9d9914e
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29187338089 conclusion=cancelled commit=bfb108b2cbe59a5a73dfdefbecf5326e226afe1f
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29187277532 conclusion=cancelled commit=3e29bdf057391ea319019622c5dbb08c2c2a1671
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Genesis System3 Global Safety CI' run 29187099940 conclusion=cancelled commit=5991b1d981b1112a29af436fa677540053159f9d
- `reports/latest/workflow_failure_tracker/summary.json`: {"branch": "main", "commit": "325d0b6568aeb4a465cc982265955eb976d915e0", "conclusion": "failure", "created_at": "2026-07-12T09:56:17Z", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29188296601", "run_id": 29188296601, "updated_at": "2026-07-12T09:56:56Z", "workflow": "Genesis System3 Global Safety CI"}
- `reports/latest/workflow_failure_tracker/summary.json`: {"branch": "main", "commit": "325d0b6568aeb4a465cc982265955eb976d915e0", "conclusion": "failure", "created_at": "2026-07-12T09:56:16Z", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29188296590", "run_id": 29188296590, "updated_at": "2026-07-12T09:56:49Z", "workflow": "Permanent Repo Render Safety"}
- `reports/latest/workflow_failure_tracker/summary.json`: {"branch": "main", "commit": "325d0b6568aeb4a465cc982265955eb976d915e0", "conclusion": "failure", "created_at": "2026-07-12T09:56:16Z", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29188296364", "run_id": 29188296364, "updated_at": "2026-07-12T09:56:16Z", "workflow": ".github/workflows/options-ml-training-proof.yml"}
- `reports/latest/workflow_failure_tracker/summary.json`: {"branch": "main", "commit": "2b94621fdf90608a12d4a92248da53365c600f17", "conclusion": "cancelled", "created_at": "2026-07-12T09:55:51Z", "html_url": "https://github.com/psw2025-cmd/Genesis_System3/actions/runs/29188285899", "run_id": 29188285899, "updated_at": "2026-07-12T09:56:32Z", "workflow": "Cloud Runtime Check"}

### UI_RED_VISUAL — 12 issues

Recommended fixes:
- Use dashboard_visible_issue_tracker output as source of truth.
- Fix root cause for each visible red/blocked/pending line; do not hide text.
- Re-run tracker until visible_issue_count=0.

Top issues:
- `reports/latest/secure_install_credential_audit/summary.json`: Required secret missing from workflow env: DASHBOARD_API_KEY
- `reports/latest/secure_install_credential_audit/summary.json`: Required secret missing from workflow env: DHAN_CLIENT_ID
- `reports/latest/secure_install_credential_audit/summary.json`: Required secret missing from workflow env: DHAN_ACCESS_TOKEN
- `reports/latest/secure_install_credential_audit/summary.json`: Add/verify required secret in secure store: DASHBOARD_API_KEY
- `reports/latest/secure_install_credential_audit/summary.json`: Add/verify required secret in secure store: DHAN_CLIENT_ID
- `reports/latest/secure_install_credential_audit/summary.json`: Add/verify required secret in secure store: DHAN_ACCESS_TOKEN
- `reports/latest/secure_install_credential_audit/summary.json`: status=BLOCKED
- `reports/latest/parallel_root_cause_audit/summary.json`: Need fresh screenshot after latest commits; older screenshots do not prove current UI.
- `reports/latest/parallel_root_cause_audit/summary.json`: status=BLOCKED
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Dashboard Live UI Proof' run 29187099924 conclusion=failure commit=5991b1d981b1112a29af436fa677540053159f9d
- `reports/latest/workflow_failure_tracker/summary.json`: status=BLOCKED
- `reports/latest/todo_status_update/summary.json`: status=BLOCKED

### RENDER_DEPLOY — 11 issues

Recommended fixes:
- Verify /api/deploy/info exposes latest commit.
- Force Render redeploy if commit mismatch or missing.
- Run live dashboard screenshot proof after deploy.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Public truth final verdict is FAIL.
- `reports/latest/parallel_root_cause_audit/summary.json`: Need compare public truth commit with latest repository head and Render deploy info; static repo audit cannot prove Render freshness.
- `reports/latest/parallel_root_cause_audit/summary.json`: Final public truth is FAIL.
- `reports/latest/parallel_root_cause_audit/summary.json`: Final truth must aggregate latest Render, integration, visual, broker, chain, scanner, paper, ML proof.
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29188296590 conclusion=failure commit=325d0b6568aeb4a465cc982265955eb976d915e0
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29188285896 conclusion=failure commit=2b94621fdf90608a12d4a92248da53365c600f17
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29187706180 conclusion=failure commit=4baec3db8f17c88b9652d53c87b2cb6d8ecb34f9
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29187345805 conclusion=failure commit=dcc19a7f2572e7a15523516f4ba8fb77b9d9914e
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29187338101 conclusion=failure commit=bfb108b2cbe59a5a73dfdefbecf5326e226afe1f
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29187277521 conclusion=failure commit=3e29bdf057391ea319019622c5dbb08c2c2a1671
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'Permanent Repo Render Safety' run 29187099915 conclusion=failure commit=5991b1d981b1112a29af436fa677540053159f9d

### ML_TRAINING — 8 issues

Recommended fixes:
- Build real CE/PE dataset proof.
- Train/test split and accuracy/AUC/Spearman proof.
- Dashboard must show score and blocked reason if unavailable.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Options ML training summary is missing/not published.
- `reports/latest/parallel_root_cause_audit/summary.json`: Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29188296364 conclusion=failure commit=325d0b6568aeb4a465cc982265955eb976d915e0
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29188285638 conclusion=failure commit=2b94621fdf90608a12d4a92248da53365c600f17
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29187705858 conclusion=failure commit=4baec3db8f17c88b9652d53c87b2cb6d8ecb34f9
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29187345533 conclusion=failure commit=dcc19a7f2572e7a15523516f4ba8fb77b9d9914e
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29187337809 conclusion=failure commit=bfb108b2cbe59a5a73dfdefbecf5326e226afe1f
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow '.github/workflows/options-ml-training-proof.yml' run 29187277310 conclusion=failure commit=3e29bdf057391ea319019622c5dbb08c2c2a1671

### UNKNOWN — 2 issues

Recommended fixes:
- Inspect source report, classify manually, add rule to planner.

Top issues:
- `reports/latest/secure_install_credential_audit/summary.json`: blocker_count=3
- `reports/latest/parallel_root_cause_audit/summary.json`: blocker_count=14

### ROUTE_CODE — 2 issues

Recommended fixes:
- Patch active dashboard/backend/app.py route if routers are disabled.
- Remove duplicate route ambiguity or prove active endpoint response.
- Add tests/proofs for active route behavior.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- `reports/latest/parallel_root_cause_audit/summary.json`: Trading router may be inactive if app.py duplicate routes are authoritative.

### BROKER_DHAN — 2 issues

Recommended fixes:
- Check broker diagnose/funds/holdings/positions read-only endpoints.
- Treat token/auth/funds failure as connected=false.
- Do not enable live orders.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.
- `reports/latest/parallel_root_cause_audit/summary.json`: Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.

### FAKE_STALE_DATA — 1 issues

Recommended fixes:
- Remove fake/mock/synthetic/Yahoo/bhavcopy from displayed live truth path.
- Allow only explicit blocked status when real data missing.
- Add proof that no fake rows are used in paper/signals/ML dashboard.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.

### OPTION_CHAIN — 1 issues

Recommended fixes:
- Prove Dhan chain rows for enabled universe.
- Show strike/expiry/CE/PE visibility in dashboard.
- Block scanner until chain rows are real.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.

### PAPER_LIFECYCLE — 1 issues

Recommended fixes:
- Require paper entry, exit, PnL, source/provenance.
- Reject fake/fixture/mock rows.
- Show order endpoints not called.

Top issues:
- `reports/latest/parallel_root_cause_audit/summary.json`: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.

