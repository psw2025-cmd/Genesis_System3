# System3 Experimental Solution Plan

Generated UTC: `2026-07-15T04:30:15.523529+00:00`
Status: **BLOCKED**
Issues: `554`
Fix lanes: `13`

## Rule

Use this plan to fix root causes by lane. Do not claim resolved until proof reports are PASS and live dashboard visual issues are zero.

## Report status

| Report | Status |
|---|---|
| `reports/latest/render_100_agent_swarm/summary.json` | `BLOCKED` |
| `reports/latest/github_render_failure_tracker/summary.json` | `BLOCKED` |
| `reports/latest/autopilot_proof_board/summary.json` | `BLOCKED` |
| `reports/latest/dashboard_visible_issue_tracker/summary.json` | `BLOCKED` |
| `reports/latest/secure_install_credential_audit/summary.json` | `BLOCKED` |
| `reports/latest/parallel_root_cause_audit/summary.json` | `BLOCKED` |
| `reports/latest/workflow_failure_tracker/summary.json` | `BLOCKED` |
| `reports/latest/todo_status_update/summary.json` | `BLOCKED` |
| `reports/latest/system3_public_truth/index.json` | `BLOCKED_NOT_TRADE_READY` |

## Fix lanes

### GITHUB_RENDER_FAILURE — 216 issues

Recommended fixes:
- Open docs/SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md first.
- Fix failed GitHub workflows from latest run/job evidence.
- Fix failing Render endpoints or deploy freshness issues.
- Keep item open until a later GitHub + Render failure tracker run is PASS.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_011:workflow_failures: Workflow failures present: failed_count=22
- `reports/latest/render_100_agent_swarm/summary.json`: agent_011:workflow_failures: Workflow failure tracker status=BLOCKED
- `reports/latest/render_100_agent_swarm/summary.json`: agent_031:workflow_failures: Workflow failures present: failed_count=22
- `reports/latest/render_100_agent_swarm/summary.json`: agent_031:workflow_failures: Workflow failure tracker status=BLOCKED
- `reports/latest/render_100_agent_swarm/summary.json`: agent_051:workflow_failures: Workflow failures present: failed_count=22
- `reports/latest/render_100_agent_swarm/summary.json`: agent_051:workflow_failures: Workflow failure tracker status=BLOCKED
- `reports/latest/render_100_agent_swarm/summary.json`: agent_071:workflow_failures: Workflow failures present: failed_count=22
- `reports/latest/render_100_agent_swarm/summary.json`: agent_071:workflow_failures: Workflow failure tracker status=BLOCKED
- `reports/latest/render_100_agent_swarm/summary.json`: agent_091:workflow_failures: Workflow failures present: failed_count=22
- `reports/latest/render_100_agent_swarm/summary.json`: agent_091:workflow_failures: Workflow failure tracker status=BLOCKED
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'Genesis System3 Global Safety CI' run=29384061148 conclusion=failure commit=af2c809fc57c
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'Permanent Repo Render Safety' run=29384061100 conclusion=failure commit=af2c809fc57c
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'Dashboard Deploy Provenance Gate' run=29384061145 conclusion=failure commit=af2c809fc57c
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow '.github/workflows/options-ml-training-proof.yml' run=29384060705 conclusion=failure commit=af2c809fc57c
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'Dashboard Visible Issue Tracker' run=29383293610 conclusion=failure commit=7285ab99b389

### UI_RED_VISUAL — 132 issues

Recommended fixes:
- Use dashboard_visible_issue_tracker output as source of truth.
- Fix root cause for each visible red/blocked/pending line; do not hide text.
- Re-run tracker until visible_issue_count=0.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_003:frontend_ui_load: UI route failed to load.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_012:visible_ui_issues: Dashboard visible issue tracker summary missing.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_013:todo_status: TODO status is not complete: BLOCKED counts={'BLOCKED': 1, 'DONE': 0, 'PARTIAL': 0, 'PENDING': 0}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_015:install_dependencies: Install/credential audit blocked: 3 blockers
- `reports/latest/render_100_agent_swarm/summary.json`: agent_019:proof_files: Required proof files missing: ['reports/latest/autopilot_proof_board/summary.json', 'reports/latest/dashboard_visible_issue_tracker/summary.json']
- `reports/latest/render_100_agent_swarm/summary.json`: agent_023:frontend_ui_load: UI route failed to load.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_032:visible_ui_issues: Dashboard visible issue tracker summary missing.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_033:todo_status: TODO status is not complete: BLOCKED counts={'BLOCKED': 1, 'DONE': 0, 'PARTIAL': 0, 'PENDING': 0}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_035:install_dependencies: Install/credential audit blocked: 3 blockers
- `reports/latest/render_100_agent_swarm/summary.json`: agent_039:proof_files: Required proof files missing: ['reports/latest/autopilot_proof_board/summary.json', 'reports/latest/dashboard_visible_issue_tracker/summary.json']
- `reports/latest/render_100_agent_swarm/summary.json`: agent_043:frontend_ui_load: UI route failed to load.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_052:visible_ui_issues: Dashboard visible issue tracker summary missing.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_053:todo_status: TODO status is not complete: BLOCKED counts={'BLOCKED': 1, 'DONE': 0, 'PARTIAL': 0, 'PENDING': 0}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_055:install_dependencies: Install/credential audit blocked: 3 blockers
- `reports/latest/render_100_agent_swarm/summary.json`: agent_059:proof_files: Required proof files missing: ['reports/latest/autopilot_proof_board/summary.json', 'reports/latest/dashboard_visible_issue_tracker/summary.json']

### BROKER_DHAN — 51 issues

Recommended fixes:
- Check broker diagnose/funds/holdings/positions read-only endpoints.
- Treat token/auth/funds failure as connected=false.
- Do not enable live orders.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_004:backend_api_smoke: Backend API smoke failed /api/broker/diagnose: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_004:backend_api_smoke: Backend API smoke failed /api/broker/funds: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_005:broker_truth: Broker/auth issue visible at /api/broker/diagnose: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_005:broker_truth: Broker/auth issue visible at /api/broker/funds: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_005:broker_truth: Broker/auth issue visible at /api/broker/holdings: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_005:broker_truth: Broker/auth issue visible at /api/broker/positions/live: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_025:broker_truth: Broker/auth issue visible at /api/broker/diagnose: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_025:broker_truth: Broker/auth issue visible at /api/broker/funds: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_025:broker_truth: Broker/auth issue visible at /api/broker/holdings: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_025:broker_truth: Broker endpoint server error: /api/broker/positions/live
- `reports/latest/render_100_agent_swarm/summary.json`: agent_044:backend_api_smoke: Backend API smoke failed /api/broker/diagnose: status=0
- `reports/latest/render_100_agent_swarm/summary.json`: agent_044:backend_api_smoke: Backend API smoke failed /api/broker/funds: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_045:broker_truth: Broker/auth issue visible at /api/broker/diagnose: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_045:broker_truth: Broker/auth issue visible at /api/broker/funds: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_045:broker_truth: Broker endpoint server error: /api/broker/holdings

### RENDER_DEPLOY — 36 issues

Recommended fixes:
- Verify /api/deploy/info exposes latest commit.
- Force Render redeploy if commit mismatch or missing.
- Run live dashboard screenshot proof after deploy.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_001:render_health: Render health failed /ui/: status=0 error=TimeoutError: The read operation timed out
- `reports/latest/render_100_agent_swarm/summary.json`: agent_001:render_health: Render health failed /api/health: status=502 error=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  font-weight: 500;
  font-style: normal;
  font-stretch: normal;
  src: url("data:font/woff2;base64,d09GMk9UVE8AAKewAAwAAAABa6QAAKdfAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYKmehqCHhuC4UocpRQGYACLBgE2AiQDkygEBgWFRwcg
- `reports/latest/render_100_agent_swarm/summary.json`: agent_002:deploy_freshness: Deploy info endpoint missing/failing; cannot prove Render deployed latest commit.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_010:public_truth: Public truth final verdict is FAIL.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_021:render_health: Render health failed /: status=0 error=TimeoutError: The read operation timed out
- `reports/latest/render_100_agent_swarm/summary.json`: agent_021:render_health: Render health failed /ui/: status=502 error=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  font-weight: 500;
  font-style: normal;
  font-stretch: normal;
  src: url("data:font/woff2;base64,d09GMk9UVE8AAKewAAwAAAABa6QAAKdfAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYKmehqCHhuC4UocpRQGYACLBgE2AiQDkygEBgWFRwcgW8pqkQK
- `reports/latest/render_100_agent_swarm/summary.json`: agent_022:deploy_freshness: Deploy info endpoint missing/failing; cannot prove Render deployed latest commit.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_030:public_truth: Public truth final verdict is FAIL.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_041:render_health: Render health failed /ui/: status=0 error=TimeoutError: The read operation timed out
- `reports/latest/render_100_agent_swarm/summary.json`: agent_041:render_health: Render health failed /api/health: status=0 error=TimeoutError: The read operation timed out
- `reports/latest/render_100_agent_swarm/summary.json`: agent_042:deploy_freshness: Deploy info endpoint missing/failing; cannot prove Render deployed latest commit.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_050:public_truth: Public truth final verdict is FAIL.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_061:render_health: Render health failed /: status=502 error=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  font-weight: 500;
  font-style: normal;
  font-stretch: normal;
  src: url("data:font/woff2;base64,d09GMk9UVE8AAKewAAwAAAABa6QAAKdfAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYKmehqCHhuC4UocpRQGYACLBgE2AiQDkygEBgWFRwcgW8pqkQKZcr
- `reports/latest/render_100_agent_swarm/summary.json`: agent_061:render_health: Render health failed /ui/: status=502 error=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  font-weight: 500;
  font-style: normal;
  font-stretch: normal;
  src: url("data:font/woff2;base64,d09GMk9UVE8AAKewAAwAAAABa6QAAKdfAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYKmehqCHhuC4UocpRQGYACLBgE2AiQDkygEBgWFRwcgW8pqkQK
- `reports/latest/render_100_agent_swarm/summary.json`: agent_061:render_health: Render health failed /api/health: status=502 error=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  font-weight: 500;
  font-style: normal;
  font-stretch: normal;
  src: url("data:font/woff2;base64,d09GMk9UVE8AAKewAAwAAAABa6QAAKdfAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAADYKmehqCHhuC4UocpRQGYACLBgE2AiQDkygEBgWFRwcg

### OPTION_CHAIN — 32 issues

Recommended fixes:
- Prove Dhan chain rows for enabled universe.
- Show strike/expiry/CE/PE visibility in dashboard.
- Block scanner until chain rows are real.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_006:option_chain: Option-chain proof blocked for NIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_006:option_chain: Option-chain proof blocked for BANKNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_006:option_chain: Option-chain proof blocked for FINNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_006:option_chain: Option-chain proof blocked for MIDCPNIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_026:option_chain: Option-chain proof blocked for NIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_026:option_chain: Option-chain proof blocked for BANKNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_026:option_chain: Option-chain proof blocked for FINNIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_026:option_chain: Option-chain proof blocked for MIDCPNIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_046:option_chain: Option-chain proof blocked for NIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_046:option_chain: Option-chain proof blocked for BANKNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_046:option_chain: Option-chain proof blocked for FINNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_046:option_chain: Option-chain proof blocked for MIDCPNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_066:option_chain: Option-chain proof blocked for NIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_066:option_chain: Option-chain proof blocked for BANKNIFTY: status=502 sample=<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>502</title>
    <style>@font-face {
  font-family: "Roobert";
  fon
- `reports/latest/render_100_agent_swarm/summary.json`: agent_066:option_chain: Option-chain proof blocked for FINNIFTY: status=401 sample={"detail":"Missing or invalid dashboard API session"}

### ML_TRAINING — 17 issues

Recommended fixes:
- Build real CE/PE dataset proof.
- Train/test split and accuracy/AUC/Spearman proof.
- Dashboard must show score and blocked reason if unavailable.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_009:ml_training: ML proof issue at /api/ml/performance: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_009:ml_training: ML proof issue at /api/ml/status: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_029:ml_training: ML proof issue at /api/ml/performance: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_029:ml_training: ML proof issue at /api/ml/status: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_049:ml_training: ML proof issue at /api/ml/status: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_069:ml_training: ML proof issue at /api/ml/performance: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_069:ml_training: ML proof issue at /api/ml/status: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_089:ml_training: ML proof issue at /api/ml/performance: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_089:ml_training: ML proof issue at /api/ml/status: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Options ML training summary is missing/not published.
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: Fix visible UI blocker on ML Model: Training proof missing.
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "ASYNC_CONTENT_NOT_SETTLED after 5011ms markers=CHECKING MODEL ARTIFACTS..."}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "BLOCKED"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "Training proof missing."}

### UNKNOWN — 17 issues

Recommended fixes:
- Inspect source report, classify manually, add rule to planner.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_014:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_034:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_054:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_074:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_094:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: issue_count=143
- `reports/latest/github_render_failure_tracker/summary.json`: todo_count=15
- `reports/latest/autopilot_proof_board/summary.json`: dashboard_visual_production_proof: status=UNKNOWN
- `reports/latest/autopilot_proof_board/summary.json`: system3_public_truth: status=FAIL
- `reports/latest/autopilot_proof_board/summary.json`: blocker_count=171
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Overview", "text": "ERROR"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Overview", "text": "PEND"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: expected_tab_count=16
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: info_line_count=78
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: unsettled_tab_count=2

### INSTALL_CREDENTIAL — 13 issues

Recommended fixes:
- Fix dependency/import/compile errors from secure audit.
- Verify credentials via redacted secure env checks only.
- Never print or commit credential values.

Top issues:
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Required secret missing from workflow env: DASHBOARD_API_KEY
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Required secret missing from workflow env: DHAN_CLIENT_ID
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Required secret missing from workflow env: DHAN_ACCESS_TOKEN
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Add/verify required secret in secure store: DASHBOARD_API_KEY
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Add/verify required secret in secure store: DHAN_CLIENT_ID
- `reports/latest/autopilot_proof_board/summary.json`: secure_install_credential_audit: Add/verify required secret in secure store: DHAN_ACCESS_TOKEN
- `reports/latest/autopilot_proof_board/summary.json`: workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382218286 conclusion=failure commit=9f30cf6b8050db38650f9c55a54ecf5ee1c27c89
- `reports/latest/autopilot_proof_board/summary.json`: workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382214811 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- `reports/latest/autopilot_proof_board/summary.json`: workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382208434 conclusion=failure commit=a15adeeec524948ee2dd8c17ed80737e93f9ee42
- `reports/latest/autopilot_proof_board/summary.json`: workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382158957 conclusion=failure commit=30c96f18de3d8acb850aa9556f58f4442f497bd2
- `reports/latest/autopilot_proof_board/summary.json`: workflow_failure_tracker: Fix workflow 'System3 Secure Install Credential Audit' run 29382146512 conclusion=failure commit=3548b373f9e65c309b3b59e9dee736c94f265b40
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29388866974 conclusion=failure commit=bc904e016d9714499b88d9fe8e39bb453ed25527
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29386597803 conclusion=failure commit=b1a18414c2789056c9bfc524d7ef1624adb384b4

### PAPER_LIFECYCLE — 11 issues

Recommended fixes:
- Require paper entry, exit, PnL, source/provenance.
- Reject fake/fixture/mock rows.
- Show order endpoints not called.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_008:paper_lifecycle: Paper lifecycle/provenance issue visible: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_028:paper_lifecycle: Paper lifecycle/provenance issue visible: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_048:paper_lifecycle: Paper lifecycle/provenance issue visible: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_068:paper_lifecycle: Paper lifecycle/provenance issue visible: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/render_100_agent_swarm/summary.json`: agent_088:paper_lifecycle: Paper lifecycle/provenance issue visible: {"detail":"Missing or invalid dashboard API session"}
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Paper Trades", "text": "Error Loading Data"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Paper Trades", "text": "Error: Request failed with status code 502"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Paper Trades", "text": "❌ Error Loading Data Endpoint: /api/state Error: Request failed with status code 502 Retry"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Paper Trades", "text": "Endpoint: /api/state Error: Request failed with status code 502"}
- `reports/latest/parallel_root_cause_audit/summary.json`: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.

### WORKFLOW_CI — 9 issues

Recommended fixes:
- Read workflow_failure_tracker TODO.
- Fix failing workflow logs one by one.
- Keep failed workflows in TODO until later successful run proves fixed.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_004:backend_api_smoke: Backend API smoke failed /api/health: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_004:backend_api_smoke: Backend API smoke failed /api/state: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_024:backend_api_smoke: Backend API smoke failed /api/health: status=0
- `reports/latest/render_100_agent_swarm/summary.json`: agent_024:backend_api_smoke: Backend API smoke failed /api/state: status=502
- `reports/latest/render_100_agent_swarm/summary.json`: agent_064:backend_api_smoke: Backend API smoke failed /api/health: status=0
- `reports/latest/render_100_agent_swarm/summary.json`: agent_084:backend_api_smoke: Backend API smoke failed /api/health: status=0
- `reports/latest/render_100_agent_swarm/summary.json`: agent_084:backend_api_smoke: Backend API smoke failed /api/state: status=502
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Performance", "text": "Failed to load performance data: 502"}
- `reports/latest/workflow_failure_tracker/summary.json`: failed_count=22

### ROUTE_CODE — 9 issues

Recommended fixes:
- Patch active dashboard/backend/app.py route if routers are disabled.
- Remove duplicate route ambiguity or prove active endpoint response.
- Add tests/proofs for active route behavior.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_018:route_conflicts: Modular broker router disabled; patches in router may not affect active app route.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_038:route_conflicts: Modular broker router disabled; patches in router may not affect active app route.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_058:route_conflicts: Modular broker router disabled; patches in router may not affect active app route.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_078:route_conflicts: Modular broker router disabled; patches in router may not affect active app route.
- `reports/latest/render_100_agent_swarm/summary.json`: agent_098:route_conflicts: Modular broker router disabled; patches in router may not affect active app route.
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Trading router may be inactive if app.py duplicate routes are authoritative.
- `reports/latest/parallel_root_cause_audit/summary.json`: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- `reports/latest/parallel_root_cause_audit/summary.json`: Trading router may be inactive if app.py duplicate routes are authoritative.

### FAKE_STALE_DATA — 7 issues

Recommended fixes:
- Remove fake/mock/synthetic/Yahoo/bhavcopy from displayed live truth path.
- Allow only explicit blocked status when real data missing.
- Add proof that no fake rows are used in paper/signals/ML dashboard.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_017:stale_fake_synthetic: Fake/stale/source-risk words found: [{'file': 'dashboard/backend/app.py', 'word': 'synthetic'}, {'file': 'dashboard/backend/app.py', 'word': 'fake'}, {'file': 'dashboard/backend/app.py', 'word': 'fixture'}, {'file': 'dashboard/backend/app.py', 'word': 'yahoo'}, {'file': 'dashboard/backend/app.py', 'word': 'bhavcopy'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 'word': 'synthetic'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 
- `reports/latest/render_100_agent_swarm/summary.json`: agent_037:stale_fake_synthetic: Fake/stale/source-risk words found: [{'file': 'dashboard/backend/app.py', 'word': 'synthetic'}, {'file': 'dashboard/backend/app.py', 'word': 'fake'}, {'file': 'dashboard/backend/app.py', 'word': 'fixture'}, {'file': 'dashboard/backend/app.py', 'word': 'yahoo'}, {'file': 'dashboard/backend/app.py', 'word': 'bhavcopy'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 'word': 'synthetic'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 
- `reports/latest/render_100_agent_swarm/summary.json`: agent_057:stale_fake_synthetic: Fake/stale/source-risk words found: [{'file': 'dashboard/backend/app.py', 'word': 'synthetic'}, {'file': 'dashboard/backend/app.py', 'word': 'fake'}, {'file': 'dashboard/backend/app.py', 'word': 'fixture'}, {'file': 'dashboard/backend/app.py', 'word': 'yahoo'}, {'file': 'dashboard/backend/app.py', 'word': 'bhavcopy'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 'word': 'synthetic'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 
- `reports/latest/render_100_agent_swarm/summary.json`: agent_077:stale_fake_synthetic: Fake/stale/source-risk words found: [{'file': 'dashboard/backend/app.py', 'word': 'synthetic'}, {'file': 'dashboard/backend/app.py', 'word': 'fake'}, {'file': 'dashboard/backend/app.py', 'word': 'fixture'}, {'file': 'dashboard/backend/app.py', 'word': 'yahoo'}, {'file': 'dashboard/backend/app.py', 'word': 'bhavcopy'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 'word': 'synthetic'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 
- `reports/latest/render_100_agent_swarm/summary.json`: agent_097:stale_fake_synthetic: Fake/stale/source-risk words found: [{'file': 'dashboard/backend/app.py', 'word': 'synthetic'}, {'file': 'dashboard/backend/app.py', 'word': 'fake'}, {'file': 'dashboard/backend/app.py', 'word': 'fixture'}, {'file': 'dashboard/backend/app.py', 'word': 'yahoo'}, {'file': 'dashboard/backend/app.py', 'word': 'bhavcopy'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 'word': 'synthetic'}, {'file': 'dashboard/frontend/src/components/PaperTrading.tsx', 
- `reports/latest/autopilot_proof_board/summary.json`: parallel_root_cause_audit: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.
- `reports/latest/parallel_root_cause_audit/summary.json`: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.

### SCANNER_SIGNAL — 4 issues

Recommended fixes:
- Verify top_contract_gainers returns real rows.
- Require CE/PE side, strike, expiry, score, reason.
- If market closed, report exact blocked reason, not fake signal.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_047:scanner_signals: Scanner/signals endpoint server error: /api/scanner/top_contract_gainers
- `reports/latest/render_100_agent_swarm/summary.json`: agent_087:scanner_signals: Scanner/signals endpoint server error: /api/state
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "Universe / ranking candidates\tBLOCKED\tYES\tcandidate_rows=0, gain=0, scanner=0"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "CE / PE decision evidence\tBLOCKED\tYES\tNo CE/PE side found in model/ranker/scanner payload"}

