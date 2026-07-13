# System3 Experimental Solution Plan

Generated UTC: `2026-07-13T19:37:41.789878+00:00`
Status: **BLOCKED**
Issues: `408`
Fix lanes: `13`

## Rule

Use this plan to fix root causes by lane. Do not claim resolved until proof reports are PASS and live dashboard visual issues are zero.

## Report status

| Report | Status |
|---|---|
| `reports/latest/render_100_agent_swarm/summary.json` | `BLOCKED` |
| `reports/latest/github_render_failure_tracker/summary.json` | `BLOCKED` |
| `reports/latest/autopilot_proof_board/summary.json` | `MISSING` |
| `reports/latest/dashboard_visible_issue_tracker/summary.json` | `BLOCKED` |
| `reports/latest/secure_install_credential_audit/summary.json` | `BLOCKED` |
| `reports/latest/parallel_root_cause_audit/summary.json` | `BLOCKED` |
| `reports/latest/workflow_failure_tracker/summary.json` | `BLOCKED` |
| `reports/latest/todo_status_update/summary.json` | `BLOCKED` |
| `reports/latest/system3_public_truth/index.json` | `FAIL` |

## Fix lanes

### GITHUB_RENDER_FAILURE — 128 issues

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
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'System3 Safe Repair Runner' run=29278567434 conclusion=failure commit=40f8ebfef038
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'System3 Windows Self-Hosted Full Proof' run=29278392362 conclusion=failure commit=47be4f808bf9
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'System3 Experimental Solution Planner' run=29278427458 conclusion=failure commit=47be4f808bf9
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'Permanent Repo Render Safety' run=29278393020 conclusion=failure commit=47be4f808bf9
- `reports/latest/github_render_failure_tracker/summary.json`: Fix latest GitHub workflow 'System3 Autopilot Proof Board' run=29278392633 conclusion=failure commit=47be4f808bf9

### UI_RED_VISUAL — 110 issues

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

### BROKER_DHAN — 32 issues

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

### OPTION_CHAIN — 23 issues

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

### UNKNOWN — 23 issues

Recommended fixes:
- Inspect source report, classify manually, add rule to planner.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_014:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_034:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_054:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_074:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: agent_094:root_cause_matrix: Parallel root-cause blockers remain: 14
- `reports/latest/render_100_agent_swarm/summary.json`: issue_count=143
- `reports/latest/github_render_failure_tracker/summary.json`: todo_count=16
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "ASYNC_CONTENT_NOT_SETTLED after 20045ms markers=CHECKING..."}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Genesis Brain", "text": "ASYNC_CONTENT_NOT_SETTLED after 20042ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "E2E Proof", "text": "ASYNC_CONTENT_NOT_SETTLED after 20045ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Overview", "text": "ASYNC_CONTENT_NOT_SETTLED after 20045ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Overview", "text": "PEND"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Trade", "text": "ASYNC_CONTENT_NOT_SETTLED after 20061ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Positions", "text": "ASYNC_CONTENT_NOT_SETTLED after 20039ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Performance", "text": "ASYNC_CONTENT_NOT_SETTLED after 20035ms"}

### ML_TRAINING — 16 issues

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
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: Fix visible UI blocker on ML Model: Training proof missing.
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "ASYNC_CONTENT_NOT_SETTLED after 20037ms"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "No matured ML training/performance artifact is available. This means model is not proven trained/ready yet."}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "BLOCKED"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "ML Model", "text": "Training proof missing."}
- `reports/latest/parallel_root_cause_audit/summary.json`: Options ML training summary is missing/not published.

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
- `reports/latest/autopilot_proof_board/summary.json`: missing_report:reports/latest/autopilot_proof_board/summary.json
- `reports/latest/workflow_failure_tracker/summary.json`: failed_count=47

### PAPER_LIFECYCLE — 8 issues

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
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "Paper/analyzer lifecycle\tBLOCKED\tNO\ttoday_trade_rows=0, endpoint=0"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Paper Trades", "text": "ASYNC_CONTENT_NOT_SETTLED after 20040ms"}
- `reports/latest/parallel_root_cause_audit/summary.json`: Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.

### ROUTE_CODE — 7 issues

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
- `reports/latest/parallel_root_cause_audit/summary.json`: Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.
- `reports/latest/parallel_root_cause_audit/summary.json`: Trading router may be inactive if app.py duplicate routes are authoritative.

### FAKE_STALE_DATA — 6 issues

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
- `reports/latest/parallel_root_cause_audit/summary.json`: Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.

### SCANNER_SIGNAL — 5 issues

Recommended fixes:
- Verify top_contract_gainers returns real rows.
- Require CE/PE side, strike, expiry, score, reason.
- If market closed, report exact blocked reason, not fake signal.

Top issues:
- `reports/latest/render_100_agent_swarm/summary.json`: agent_047:scanner_signals: Scanner/signals endpoint server error: /api/scanner/top_contract_gainers
- `reports/latest/render_100_agent_swarm/summary.json`: agent_087:scanner_signals: Scanner/signals endpoint server error: /api/state
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "Universe / ranking candidates\tBLOCKED\tYES\tcandidate_rows=0, gain=0, scanner=0"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Truth Control", "text": "CE / PE decision evidence\tBLOCKED\tYES\tNo CE/PE side found in model/ranker/scanner payload"}
- `reports/latest/dashboard_visible_issue_tracker/summary.json`: {"tab": "Signals", "text": "ASYNC_CONTENT_NOT_SETTLED after 20048ms"}

### INSTALL_CREDENTIAL — 5 issues

Recommended fixes:
- Fix dependency/import/compile errors from secure audit.
- Verify credentials via redacted secure env checks only.
- Never print or commit credential values.

Top issues:
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29278974477 conclusion=failure commit=c393ae652cbf1ff58756f1b5938df7e9086cc0ef
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29278935782 conclusion=failure commit=f339f8482680d51738a6a0ebdfc4264db6edb0ec
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29278934474 conclusion=failure commit=f339f8482680d51738a6a0ebdfc4264db6edb0ec
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29278917958 conclusion=failure commit=3ec64a33a1888d0a6d18ec2917042fb7a191f99c
- `reports/latest/workflow_failure_tracker/summary.json`: Fix workflow 'System3 Secure Install Credential Audit' run 29278897399 conclusion=failure commit=6644368d9d5b69e6c3e275b032a32a9d00e42465

