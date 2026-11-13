import os, sys, json, openpyxl
from datetime import datetime, timezone
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

header_fill_navy = PatternFill(start_color='1F497D', end_color='1F497D', fill_type='solid')
header_fill_red = PatternFill(start_color='C00000', end_color='C00000', fill_type='solid')
header_fill_green = PatternFill(start_color='385723', end_color='385723', fill_type='solid')
header_fill_orange = PatternFill(start_color='C65911', end_color='C65911', fill_type='solid')
header_font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
data_font = Font(name='Segoe UI', size=9)
title_font = Font(name='Segoe UI', size=12, bold=True, color='1F497D')

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

def style_sheet(ws, title, header_fill=header_fill_navy):
    ws.views.sheetView[0].showGridLines = True
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[1].height = 28
    
    for row in ws.iter_rows(min_row=2):
        ws.row_dimensions[row[0].row].height = 20
        for cell in row:
            cell.font = data_font
            cell.border = thin_border
            if isinstance(cell.value, (int, float)):
                cell.alignment = Alignment(horizontal='right', vertical='center')
            else:
                val_str = str(cell.value or '')
                if val_str in ('PASS', 'GREEN', 'APPROVED', 'YES', 'SAFE_TO_DELETE'):
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
                    cell.font = Font(name='Segoe UI', size=9, bold=True, color='276A3C')
                elif val_str in ('FAIL', 'RED', 'BLOCKED', 'NO', 'HIGH', 'CRITICAL'):
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
                    cell.font = Font(name='Segoe UI', size=9, bold=True, color='C00000')
                elif val_str in ('YELLOW', 'MANUAL_REVIEW', 'NEEDS_REVIEW', 'PARTIAL', 'MEDIUM', 'PENDING'):
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                    cell.fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
                    cell.font = Font(name='Segoe UI', size=9, bold=True, color='B25900')
                else:
                    cell.alignment = Alignment(horizontal='left', vertical='center')
                    
    for col in ws.columns:
        col_letter = col[0].column_letter
        max_len = 0
        for cell in col:
            v = str(cell.value or '')
            if len(v) > max_len: max_len = len(v)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 65)

# ==========================================
# 1. PHASE2_MERGE_MAP.xlsx
# ==========================================
print('Generating PHASE2_MERGE_MAP.xlsx...')
wb_m = openpyxl.Workbook()
ws_m1 = wb_m.active
ws_m1.title = 'MERGE_SPECIFICATION'

headers_m1 = [
    'Merge ID', 'Priority', 'Feature Name', 'Source File', 
    'Source Exact Lines', 'Source Functions / Components', 
    'Destination File', 'Destination Target Area', 'Merged Capabilities', 
    'Dependencies', 'Risk Level', 'Anti-Regression Verification'
]
ws_m1.append(headers_m1)

merge_rows = [
    [
        'MRG-01', 'P0', 'Dhan Marketfeed Quotes & Rate Limiter',
        'content/app/verified_market.py', 'lines 1-135',
        'get_verified_quotes(), _session(), _ids(), _mutex, _cache',
        'dashboard/backend/routers/chain.py', 'mount_verified_marketfeed() & rate_limiter',
        'Dhan marketfeed quotes (https://api.dhan.co/v2/marketfeed/quote), 1.0s TTL rate limiting, market session validation (OPEN/CLOSED), verified market endpoint logic',
        'urllib.request, json, threading, datetime, zoneinfo',
        'Medium', 'Verify /api/verified-market returns HTTP 200 with exchange_quotes_verified=True during market hours and graceful error when closed/expired'
    ],
    [
        'MRG-02', 'P0', 'Dhan JWT Token Prober & Auth Diagnostics',
        'content/app/probe_dhan_credentials.py', 'lines 1-59',
        'readenv(), claims decoder, exp validator, req()',
        'dashboard/backend/broker/dhan_auth.py', 'decode_dhan_jwt_claims() & verify_dhan_auth_status()',
        'JWT expiry decoding (base64 urlsafe without secret), credential validation (presence of client ID + token), auth diagnostics (profile status code, DH-901 error detection), secret-safe reporting (redacted logging)',
        'base64, json, datetime, urllib.request, logging',
        'Medium', 'Verify probe accurately detects expired token (2026-11-10T08:38:50 UTC) and emits DH-901 classification without printing secrets'
    ],
    [
        'MRG-03', 'P0', 'Dhan Holdings Normalization & Response Unwrapping',
        'content/app/dhan_account_router.py', 'lines 1-76, 99-137',
        '_unwrap_dhan_data(), _normalize_holding(), get_dhan_holdings()',
        'dashboard/backend/routers/broker.py', '_unwrap_dhan_payload() & get_normalized_holdings()',
        'Holdings normalization (totalQty, avgCostPrice, lastTradedPrice, invested, current, pnl, pnl_pct), response normalization (unwrapping nested raw["data"]["data"]), zero-holding fail-safe',
        'core.brokers.dhan.dhan_readonly, typing, time',
        'Low', 'Verify GET /api/broker/holdings unwraps all 11 live Demat holdings accurately with calculated P&L'
    ],
    [
        'MRG-04', 'P0', 'Broker Profile Masking & Account Summary Helpers',
        'content/app/dhan_account_router.py', 'lines 77-98, 145-170',
        'get_dhan_profile(), get_dhan_summary(), get_dhan_funds()',
        'dashboard/backend/routers/broker.py', 'get_masked_profile() & get_account_summary()',
        'Profile masking (mask PAN, mobile, client ID for UI), account summary aggregation (combines available funds, holdings count, position count into single payload)',
        'core.brokers.dhan.dhan_readonly, fastapi.APIRouter',
        'Low', 'Verify GET /api/broker/summary returns aggregated funds and masked profile without leaking PII'
    ],
    [
        'MRG-05', 'P0', 'Safe Environment Enforcer Script',
        'content/app/configure_safe_env.py', 'lines 1-73',
        'configure_safe_env(), enforce_strict_safety()',
        'scripts/configure_safe_env.py', 'enforce_safe_environment()',
        'Enforces ANALYZE_MODE=1, PAPER_MODE=1, LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0, AUTO_EXECUTE_TRADES=0, LIVE_ORDER_AUTHORITY=0 across local and cloud environments',
        'os, sys, dotenv, pathlib',
        'High', 'Verify environment audit passes all 6 safety locks and blocks live order placement'
    ]
]

for r in merge_rows:
    ws_m1.append(r)
style_sheet(ws_m1, 'MERGE_SPECIFICATION')

ws_m2 = wb_m.create_sheet('DO_NOT_MERGE_CONSTRAINTS')
headers_m2 = ['Rule ID', 'Constraint Name', 'Prohibited Action', 'Enforcement Mechanism', 'Evidence Required']
ws_m2.append(headers_m2)
constraint_rows = [
    ['CST-01', 'No Duplicate Routes', 'Do not define identical FastAPI endpoint paths across multiple routers', 'FastAPI route collision check in tests/analyze_all_url_paths.py', 'Exact 653 route count parity audit'],
    ['CST-02', 'No Parallel Implementations', 'Do not keep content/app active after dashboard/backend consolidation', 'Retirement of content/app entry points post-verification', 'Single process binding on port 8008 / Cloud Run'],
    ['CST-03', 'No Feature Regressions', 'Do not drop working Demat holdings, option chain Greeks, or market session checks', 'Unit and integration test suites in tests/test_ui_p0_recovery_mission.py', 'Test execution logs with 0 regressions'],
    ['CST-04', 'Zero Real Orders Path', 'Never merge order execution or live broker trading pathways', 'LIVE_TRADING_ENABLED=0 hardlock & 403 Safety Gate block', 'Security test in tests/test_kill_switch.py PASS'],
    ['CST-05', 'No Secret Exposure', 'Never commit, log, or expose raw Dhan tokens or PAN details in code or responses', 'Regex secret scanners and probe masking functions', 'Sanitized audit logs in reports/latest/']
]
for r in constraint_rows:
    ws_m2.append(r)
style_sheet(ws_m2, 'DO_NOT_MERGE_CONSTRAINTS')
wb_m.save('PHASE2_MERGE_MAP.xlsx')
print('Saved PHASE2_MERGE_MAP.xlsx')

# ==========================================
# 2. PHASE3_TEST_RESULTS.xlsx
# ==========================================
print('Generating PHASE3_TEST_RESULTS.xlsx...')
wb_t = openpyxl.Workbook()
ws_t1 = wb_t.active
ws_t1.title = 'TEST_SUITE_EXECUTION'

headers_t1 = [
    'Test Suite ID', 'Category', 'Target File / Suite', 'Scope / Purpose',
    'Execution Command', 'Observed Result', 'Error / Exit Reason', 
    'Blocker Reference', 'Remediation'
]
ws_t1.append(headers_t1)

test_rows = [
    [
        'TST-01', 'Unit (Safety)', 'tests/test_kill_switch.py',
        'Verify kill switch safety gate, paper mode lock, zero live order authority',
        'pytest tests/test_kill_switch.py -v', 'PASS', 'None (1 passed in 0.42s)',
        'None', 'Preserve all safety locks in all environments'
    ],
    [
        'TST-02', 'Router / Local Server', 'tests/test_ui_p0_recovery_mission.py',
        'Verify 16 P0 UI recovery endpoints against running local server (port 8008)',
        'pytest tests/test_ui_p0_recovery_mission.py -v', 'FAIL',
        'ConnectionRefusedError: [WinError 10061] Target machine actively refused it (port 8008 offline)',
        'BLK-03 (Local server not running in current session)',
        'Start local server on port 8008 via scripts/start_backend_persistent.py before running suite'
    ],
    [
        'TST-03', 'Integration (6 Pillars)', 'tests/test_6_pillars_verification.py',
        'Verify 6-pillar command center audit against local server endpoints',
        'pytest tests/test_6_pillars_verification.py -v', 'FAIL',
        'ConnectionRefusedError: [WinError 10061] (port 8008 offline)',
        'BLK-03 (Local server offline)',
        'Start local server and execute integration tests'
    ],
    [
        'TST-04', 'Broker Authentication', 'content/app/probe_dhan_credentials.py',
        'Probe live Dhan API credentials, decode JWT expiry, verify profile status',
        'python content/app/probe_dhan_credentials.py', 'FAIL',
        'HTTP 401 Unauthorized (error code: DH-901; JWT expired 2026-11-10T08:38:50 UTC)',
        'BLK-01 (Dhan Access Token Expired)',
        'Owner must generate fresh daily Dhan Access Token and update .secrets/dhan.env'
    ],
    [
        'TST-05', 'Startup Validation', 'dashboard/backend/app.py',
        'Verify Python importability, route mounting, and syntax of primary architecture',
        'python -c "import dashboard.backend.app"', 'PASS', 'Module imported successfully with 0 syntax errors',
        'None', 'Clean startup validation'
    ],
    [
        'TST-06', 'Cloud Compatibility', 'dashboard/backend/Dockerfile',
        'Verify Dockerfile multi-stage build definition and dependency requirements',
        'dockerfile-lint / syntax review', 'PASS', 'Dockerfile cdca8f921d7b301b syntax verified for Cloud Run',
        'None', 'Production image specification ready'
    ],
    [
        'TST-07', 'Paper-Mode Verification', 'core/engine/anti_fake_guard.py',
        'Verify paper ledger determinism, zero live execution path, slippage modeling',
        'pytest tests/test_autonomous_watchdog.py -v', 'PASS', 'Paper trading locks verified active',
        'None', 'Permanent paper safety maintained'
    ]
]
for r in test_rows:
    ws_t1.append(r)
style_sheet(ws_t1, 'TEST_SUITE_EXECUTION')

ws_t2 = wb_t.create_sheet('TEST_SUMMARY')
headers_t2 = ['Category', 'Total Tests', 'PASS', 'FAIL / BLOCKED', 'Pass Rate (%)', 'Status']
ws_t2.append(headers_t2)
summary_rows = [
    ['Safety & Kill Switch (Unit)', 1, 1, 0, 100.0, 'PASS'],
    ['Startup & Architecture (Unit)', 2, 2, 0, 100.0, 'PASS'],
    ['Paper Mode & Anti-Fake Guard', 1, 1, 0, 100.0, 'PASS'],
    ['Local Server Endpoint Verification', 16, 0, 16, 0.0, 'FAIL'],
    ['Broker Live Integration & Quote Probe', 1, 0, 1, 0.0, 'FAIL'],
    ['OVERALL TEST SCORECARD', 21, 4, 17, 19.0, 'RED']
]
for r in summary_rows:
    ws_t2.append(r)
style_sheet(ws_t2, 'TEST_SUMMARY')
wb_t.save('PHASE3_TEST_RESULTS.xlsx')
print('Saved PHASE3_TEST_RESULTS.xlsx')

# ==========================================
# 3. PHASE4_CLOUD_VERIFICATION.xlsx
# ==========================================
print('Generating PHASE4_CLOUD_VERIFICATION.xlsx...')
wb_c = openpyxl.Workbook()
ws_c1 = wb_c.active
ws_c1.title = 'CLOUD_VERIFICATION_MATRIX'

headers_c1 = [
    'Control ID', 'Verification Item', 'Target URL / Cloud Metric',
    'Expected Result', 'Observed Result', 'Evidence & Output',
    'Verdict', 'Blocker / Notes'
]
ws_c1.append(headers_c1)

cloud_rows = [
    [
        'CLD-01', 'Cloud Run Service Startup',
        'https://genesis-system3-web-doq2wplepa-el.a.run.app',
        'Service returns HTTP 200 / healthy container response',
        'Revision genesis-system3-web-00136-qub active and serving 100% traffic',
        'gcloud run services describe genesis-system3-web --region asia-south1 confirms 100% traffic on revision 136',
        'PASS', 'Revision 136 is deployed and responsive'
    ],
    [
        'CLD-02', 'Health Endpoint Verification',
        'https://genesis-system3-web-doq2wplepa-el.a.run.app/api/health',
        'HTTP 200 OK with runtime status and git sha',
        'HTTP 200 OK returned by Cloud Run container',
        'Probed /api/health; returns status: ok, mode: analyze/paper',
        'PASS', 'Health check passed'
    ],
    [
        'CLD-03', 'Broker Status Endpoint Verification',
        'https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/dhan/status',
        'HTTP 200 OK with broker telemetry payload',
        'HTTP 200 OK returned, but connected: false (upstream token expired)',
        'Response: {status: disconnected, error: UPSTREAM_DHAN_TOKEN_EXPIRED, latency_ms: null}',
        'PARTIAL', 'Endpoint functioning correctly; upstream Dhan token expired'
    ],
    [
        'CLD-04', 'Dhan Live Connectivity',
        'Dhan API https://api.dhan.co/v2/profile',
        'Authenticated response from DhanHQ v2 API',
        'HTTP 401 Unauthorized (error code: DH-901)',
        'content/app/probe_dhan_credentials.py confirms token expired 2026-11-10T08:38:50 UTC',
        'FAIL', 'BLK-01: Token expired; requires owner refresh'
    ],
    [
        'CLD-05', 'Permanent Paper Mode & Zero Live Orders',
        'LIVE_TRADING_ENABLED & SYSTEM3_LIVE_TRADING_ALLOWED',
        'Values must be 0 / false in Cloud Run environment',
        'Cloud Run revision 136 env vars confirm LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0',
        'gcloud run revisions describe confirms 0 live order authority; zero order execution path exists',
        'PASS', 'Constitutional paper safety verified'
    ],
    [
        'CLD-06', 'Cloud Run Logs Cleanliness',
        'GCP Cloud Logging logName: run.googleapis.com/stdout',
        'No uncaught 500 exceptions, clean structured logging',
        'Orderly fail-closed logging observed; no unhandled crashes',
        'Cloud Logging queries show clean error boundary containment',
        'PASS', 'Clean runtime logging verified'
    ],
    [
        'CLD-07', 'No Deployment Regressions',
        'Traffic allocation & container image digest',
        '100% traffic pinned to verified image sha256:4a14ad39a348',
        '100% traffic on revision 136; unverified candidate 141 has 0% traffic',
        'CLOUD_GITHUB_TRUTH.xlsx confirms traffic pin; no routing drift to candidate 141',
        'PASS', 'No deployment regressions detected'
    ],
    [
        'CLD-08', 'Cloud Run Mutation Consent',
        'docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md',
        'Separate explicit owner approval required before billable builds/deployments',
        'No approval granted for new deployment; DRY RUN mandate active',
        'AGENTS.md constitution enforces autonomous repairs only; deployment mutation blocked',
        'BLOCKED', 'BLK-02: Awaiting owner deployment approval'
    ]
]
for r in cloud_rows:
    ws_c1.append(r)
style_sheet(ws_c1, 'CLOUD_VERIFICATION_MATRIX')

ws_c2 = wb_c.create_sheet('LIVE_ORDER_SAFETY_AUDIT')
headers_c2 = ['Safety Parameter', 'Environment Key', 'Required Value', 'Observed Value in Cloud Run', 'Verdict', 'Proof Reference']
ws_c2.append(headers_c2)
safety_rows = [
    ['Analyze Mode Lock', 'ANALYZE_MODE', '1', '1', 'PASS', 'Revision 136 container env spec'],
    ['Paper Mode Lock', 'PAPER_MODE', '1', '1', 'PASS', 'Revision 136 container env spec'],
    ['System Mode', 'SYSTEM3_MODE', 'analyze', 'analyze', 'PASS', 'Revision 136 container env spec'],
    ['Live Trading Enabled', 'LIVE_TRADING_ENABLED', '0', '0', 'PASS', 'Revision 136 container env spec'],
    ['System3 Live Trading Allowed', 'SYSTEM3_LIVE_TRADING_ALLOWED', '0', '0', 'PASS', 'Revision 136 container env spec'],
    ['Auto Execute Trades', 'AUTO_EXECUTE_TRADES', '0', '0', 'PASS', 'Revision 136 container env spec'],
    ['Live Order Authority', 'LIVE_ORDER_AUTHORITY', '0', '0', 'PASS', 'Revision 136 container env spec'],
    ['Order Placement Allowed', 'ORDER_PLACEMENT_ALLOWED', 'false', 'false', 'PASS', 'Revision 136 container env spec']
]
for r in safety_rows:
    ws_c2.append(r)
style_sheet(ws_c2, 'LIVE_ORDER_SAFETY_AUDIT')
wb_c.save('PHASE4_CLOUD_VERIFICATION.xlsx')
print('Saved PHASE4_CLOUD_VERIFICATION.xlsx')

# ==========================================
# 4. PHASE5_RETIREMENT_REPORT.xlsx
# ==========================================
print('Generating PHASE5_RETIREMENT_REPORT.xlsx...')
wb_r = openpyxl.Workbook()
ws_r1 = wb_r.active
ws_r1.title = 'CONTENT_APP_CLASSIFICATION'

headers_r1 = [
    'File Path', 'Size (Bytes)', 'Classification', 
    'Phase Prerequisite', 'Superseding Target in dashboard/backend', 
    'Justification & Evidence', 'Risk of Deletion'
]
ws_r1.append(headers_r1)

content_files = [
    ('content/app/app.py', 484392, 'NEEDS_REVIEW', 'Phase 2-4 PASS', 'dashboard/backend/app.py', 'Contains 653 legacy routes, prototype UI endpoints, and telemetry handlers; needs staged retirement post-merge', 'High'),
    ('content/app/configure_safe_env.py', 3207, 'DO_NOT_DELETE', 'Phase 2 PASS', 'scripts/configure_safe_env.py', 'Source of safe environment configuration logic; retain until script consolidated', 'Medium'),
    ('content/app/dhan_account_router.py', 6383, 'DO_NOT_DELETE', 'Phase 2 PASS', 'dashboard/backend/routers/broker.py', 'Source of 11-holding unwrapping and summary aggregation logic; retain until merged', 'High'),
    ('content/app/probe_dhan_credentials.py', 3207, 'DO_NOT_DELETE', 'Phase 2 PASS', 'dashboard/backend/broker/dhan_auth.py', 'Source of secret-safe JWT decoding and DH-901 diagnosis; retain until merged', 'High'),
    ('content/app/verified_market.py', 13535, 'DO_NOT_DELETE', 'Phase 2 PASS', 'dashboard/backend/routers/chain.py', 'Source of verified Dhan marketfeed quotes and rate limiting; retain until merged', 'High'),
    ('content/app/templates/premium.html', 39120, 'NEEDS_REVIEW', 'Phase 2-4 PASS', 'dashboard/frontend/ (Next.js/React)', 'Single-page HTML interface with 22-tab layout and Chart.js; retain for visual fallback', 'Medium'),
    ('content/app/templates/premium.html.bak', 38156, 'SAFE_TO_DELETE', 'Phase 2-4 PASS', 'None (stale backup)', 'Redundant 38KB backup of HTML template; safe to delete post-consolidation', 'None'),
    ('content/app/uvicorn_detached.log', 10161, 'SAFE_TO_DELETE', 'Immediate', 'None (runtime artifact)', 'Obsolete process execution log left behind by detached worker; safe to delete', 'None'),
    ('content/app/truth_backups/20261102T162014Z/app.py', 47641, 'SAFE_TO_DELETE', 'Immediate', 'None (obsolete snapshot)', 'Legacy Nov 2 snapshot with outdated mock routes; safe to delete', 'None'),
    ('content/app/truth_backups/20261102T162014Z/premium.html', 30953, 'SAFE_TO_DELETE', 'Immediate', 'None (obsolete snapshot)', 'Legacy Nov 2 HTML template backup; safe to delete', 'None'),
    ('content/app/truth_backups/verified_gate_20261102T165613Z/app.py', 50847, 'SAFE_TO_DELETE', 'Immediate', 'None (temporary script artifact)', 'Backup snapshot generated during script execution; safe to delete', 'None'),
    ('content/app/truth_backups/verified_gate_20261102T165613Z/premium.html', 33576, 'SAFE_TO_DELETE', 'Immediate', 'None (temporary script artifact)', 'Backup snapshot generated during script execution; safe to delete', 'None'),
    ('content/app/verified_sources/dhan_instrument_master_detailed.csv', 18450120, 'NEEDS_REVIEW', 'Phase 2-4 PASS', 'core/brokers/dhan/security_master.csv', 'Authoritative instrument master (210,520 contracts) used for security ID lookup; preserve', 'High'),
    ('content/app/verified_sources/master_manifest.json', 1420, 'NEEDS_REVIEW', 'Phase 2-4 PASS', 'core/brokers/dhan/manifest.json', 'Security master hash manifest and update metadata; preserve', 'Medium')
]

for cf in content_files:
    ws_r1.append([cf[0], cf[1], cf[2], cf[3], cf[4], cf[5], cf[6]])
style_sheet(ws_r1, 'CONTENT_APP_CLASSIFICATION')

ws_r2 = wb_r.create_sheet('RETIREMENT_SUMMARY')
headers_r2 = ['Classification Category', 'File Count', 'Total Size (Bytes)', 'Action in Dry Run', 'Prerequisite for Deletion']
ws_r2.append(headers_r2)
ws_r2.append(['SAFE_TO_DELETE', 6, 218494, 'DO NOT DELETE (Dry Run Only)', 'Phase 2 PASS + Phase 3 PASS + Phase 4 PASS'])
ws_r2.append(['DO_NOT_DELETE (Merge Source)', 4, 26332, 'PRESERVE (Source of truth for Phase 2)', 'Must be merged and verified in dashboard/backend before retirement'])
ws_r2.append(['NEEDS_REVIEW (Data / Template / Core)', 4, 18975093, 'PRESERVE (Under review)', 'Requires comprehensive UI and instrument master audit'])
ws_r2.append(['TOTAL CONTENT/APP FILES REVIEWED', 14, 19219919, 'NO FILES MODIFIED OR DELETED', 'Strict Dry Run Mandate Preserved'])
style_sheet(ws_r2, 'RETIREMENT_SUMMARY')
wb_r.save('PHASE5_RETIREMENT_REPORT.xlsx')
print('Saved PHASE5_RETIREMENT_REPORT.xlsx')

# ==========================================
# 5. DEPLOYMENT_SIGNOFF.xlsx
# ==========================================
print('Generating DEPLOYMENT_SIGNOFF.xlsx...')
wb_s = openpyxl.Workbook()
ws_s1 = wb_s.active
ws_s1.title = 'SIGNOFF_CHECKLIST'

headers_s1 = [
    'Section', 'Checklist Item', 'Acceptance Criterion',
    'Current State (Dry Run)', 'Signoff Status', 'Owner Action Required', 'Evidence Reference'
]
ws_s1.append(headers_s1)

signoff_items = [
    ['SOURCE CONTROL', 'GitHub main clean', 'Working tree clean, no untracked clutter', '9 commits behind origin/main; local untracked scripts', 'PENDING', 'Fast-forward git pull origin main after review', 'git status'],
    ['SOURCE CONTROL', 'No merge conflicts', 'Branch clean and mergeable with origin/main', 'Fast-forward possible with 0 merge conflicts', 'PASS', 'None', 'git log origin/main..HEAD'],
    ['ARCHITECTURE', 'dashboard/backend primary runtime', 'Single runtime handling all API routes', 'Mapped in Phase 2; content/app currently co-exists', 'PENDING', 'Approve execution of Phase 2 merge plan', 'FINAL_CONSOLIDATION_PLAN.xlsx'],
    ['ARCHITECTURE', 'No duplicate active implementation', 'Single implementation per feature', 'Duplicate route & broker logic identified in Phase 0 scan', 'BLOCKED', 'Approve retirement of duplicate content/app files', 'REPOSITORY_FILE_SCAN.xlsx'],
    ['DHAN', 'Authentication verified', 'Valid JWT token returns HTTP 200 on /profile', 'JWT token expired on 2026-11-10T08:38:50 UTC (HTTP 401 DH-901)', 'FAIL', 'Generate fresh Dhan Access Token in Dhan web portal', 'content/app/probe_dhan_credentials.py'],
    ['DHAN', 'Real market data verified', 'Live quote endpoint returns valid exchange feed', 'Blocked by expired Dhan access token (HTTP 401)', 'BLOCKED', 'Rotate token in .secrets/dhan.env and GCP Secret Manager', 'QUOTE_HTTP 401'],
    ['DHAN', 'Holdings, Funds, Positions verified', 'Read-only Demat holdings unwrapped correctly', 'Blocked by expired Dhan token', 'BLOCKED', 'Rotate token to restore live account telemetry', 'PROFILE_HTTP 401'],
    ['SAFETY', 'LIVE_TRADING_ENABLED=0', 'Strict lock on live order placement', 'Hardlocked to 0 in all configurations and Cloud Run', 'APPROVED', 'None (Keep permanent lock)', 'agent_policy.yaml & Cloud Run env'],
    ['SAFETY', 'SYSTEM3_LIVE_TRADING_ALLOWED=0', 'Strict secondary lock on trading engine', 'Hardlocked to 0 across runtime and containers', 'APPROVED', 'None (Keep permanent lock)', 'AGENTS.md constitution'],
    ['SAFETY', 'Real order execution blocked', 'Zero real broker orders path', '100% blocked by safety gate; HTTP 403 on POST /placeorder', 'APPROVED', 'None (Permanent paper lock)', 'tests/test_kill_switch.py PASS'],
    ['TESTING', 'Unit tests PASS', 'Isolated safety and component tests pass', 'Safety unit tests PASS (test_kill_switch.py)', 'PARTIAL', 'None', 'pytest tests/test_kill_switch.py'],
    ['TESTING', 'Integration tests PASS', 'All API routes and server contracts pass', 'Server offline on port 8008; Dhan token expired', 'BLOCKED', 'Start local server and rotate token', 'test_ui_p0_recovery_mission.py'],
    ['TESTING', 'Startup tests PASS', 'Clean module imports and syntax validation', 'dashboard.backend.app imports with 0 errors', 'PASS', 'None', 'python -c import dashboard.backend.app'],
    ['CLOUD', 'Build PASS', 'Cloud Build container image builds cleanly', 'Cloud Build c0049f2f built image sha256:4a14ad39 cleanly', 'PASS', 'None', 'CLOUD_GITHUB_TRUTH.xlsx'],
    ['CLOUD', 'Deploy PASS', 'Service deployed to Cloud Run in asia-south1', 'Deploy mutation blocked per Directive 20261018', 'BLOCKED', 'Provide explicit owner approval for deployment', 'CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md'],
    ['CLOUD', 'Health PASS', 'Cloud Run /api/health returns HTTP 200', 'Cloud Run revision 136 returns HTTP 200', 'PASS', 'None', 'Cloud Run health probe PASS'],
    ['CLOUD', 'Broker PASS', 'Broker endpoint responds with structured payload', 'HTTP 200 returned, but reporting disconnected status', 'PARTIAL', 'Rotate token in Cloud Run secrets', 'GET /api/broker/dhan/status'],
    ['CLOUD', 'Dhan PASS', 'Dhan connectivity verified in cloud runtime', 'Upstream token expired; Cloud Run reports DH-901', 'BLOCKED', 'Update GCP Secret Manager secret dhan_access_token', 'Cloud Logging HTTP 401']
]

for s in signoff_items:
    ws_s1.append(s)
style_sheet(ws_s1, 'SIGNOFF_CHECKLIST')

ws_s2 = wb_s.create_sheet('FINAL_VERDICT')
headers_s2 = ['Metric', 'Value', 'Status', 'Mandatory Rule Impact']
ws_s2.append(headers_s2)
ws_s2.append(['Total Checklist Items', 18, 'INFO', 'Full deployment checklist coverage'])
ws_s2.append(['Approved / Passing Items', 7, 'GREEN', 'Safety locks, container startup, and build pass'])
ws_s2.append(['Pending Items', 3, 'YELLOW', 'Git pull and merge approval pending'])
ws_s2.append(['Blocked / Failing Items', 8, 'RED', 'Dhan token expired & Cloud deploy consent pending'])
ws_s2.append(['FINAL DEPLOYMENT VERDICT', 'RED = BLOCKER EXISTS', 'RED', 'Mandate STOP: Do not deploy, do not modify files'])
style_sheet(ws_s2, 'FINAL_VERDICT')
wb_s.save('DEPLOYMENT_SIGNOFF.xlsx')
print('Saved DEPLOYMENT_SIGNOFF.xlsx')

# ==========================================
# 6. GENESIS_FINAL_IMPLEMENTATION_REPORT.xlsx
# ==========================================
print('Generating GENESIS_FINAL_IMPLEMENTATION_REPORT.xlsx...')
wb_f = openpyxl.Workbook()
ws_f1 = wb_f.active
ws_f1.title = 'EXECUTIVE_SUMMARY'

headers_f1 = ['Report Section', 'Key Finding / Metric', 'Status', 'Details & Evidence']
ws_f1.append(headers_f1)
exec_rows = [
    ['Mission Objective', 'Controlled Consolidation of Genesis System3 into dashboard/backend', 'DRY_RUN_COMPLETE', 'Planned consolidation preserving real Dhan data, paper trading, and zero broker orders'],
    ['Repository Scan (Phase 0)', '2,819 files scanned across 9 core directory patterns', 'PASS', 'Produced REPOSITORY_FILE_SCAN.xlsx and REPOSITORY_FILE_SCAN.json; detected 4 duplicate features, 12 delete candidates'],
    ['Primary Architecture (Phase 1)', 'dashboard/backend established as single canonical runtime', 'TARGET_CONFIRMED', 'GitHub origin/main as code authority; Google Cloud Run asia-south1 as target runtime'],
    ['Feature Merge Map (Phase 2)', '4 proven features mapped from content/app into dashboard/backend', 'MAPPED_DRY_RUN', 'PHASE2_MERGE_MAP.xlsx maps marketfeed quotes, JWT probe, holdings unwrapping, and summary helpers'],
    ['Test Verification (Phase 3)', 'Safety & startup tests pass; local server & broker tests fail', 'RED (FAIL)', 'PHASE3_TEST_RESULTS.xlsx: Kill switch PASS; local server offline & Dhan token expired'],
    ['Cloud Verification (Phase 4)', 'Cloud Run revision 136 healthy; deploy mutation blocked', 'RED (BLOCKED)', 'PHASE4_CLOUD_VERIFICATION.xlsx: Health PASS; Dhan token expired; Cloud mutation requires owner approval'],
    ['Retirement Review (Phase 5)', 'Content/app classified into SAFE_TO_DELETE (6), DO_NOT_DELETE (4), NEEDS_REVIEW (4)', 'BLOCKED_BY_PREREQ', 'PHASE5_RETIREMENT_REPORT.xlsx: Retirement gated until Phases 2-4 achieve live PASS'],
    ['Acceptance Criteria Evaluation', 'Architecture: YELLOW | Dhan: RED | Safety: GREEN | Testing: RED | Cloud: RED', 'RED (BLOCKER)', 'Mandatory STOP triggered: 2 critical external blockers prevent green readiness'],
    ['Deployment Signoff Verdict', 'DEPLOYMENT_SIGNOFF.xlsx: 7 Approved, 3 Pending, 8 Blocked', 'RED = BLOCKER EXISTS', 'Do not deploy. Maintain dry-run posture until blockers remediated by owner']
]
for r in exec_rows:
    ws_f1.append(r)
style_sheet(ws_f1, 'EXECUTIVE_SUMMARY')

ws_f2 = wb_f.create_sheet('BLOCKER_REGISTER')
headers_f2 = ['Blocker ID', 'Blocker Title', 'Severity', 'Root Cause', 'Evidence', 'Remediation Step', 'Owner Action Required']
ws_f2.append(headers_f2)
blocker_rows = [
    [
        'BLK-01', 'Dhan Access Token Expired (HTTP 401 DH-901)', 'CRITICAL',
        'Daily Dhan JWT token expired on 2026-11-10T08:38:50 UTC. Read-only live quote and account endpoints fail with HTTP 401.',
        'content/app/probe_dhan_credentials.py output: JWT_EXPIRY_UTC 2026-11-10T08:38:50+00:00 ALREADY_EXPIRED True; PROFILE_HTTP 401; PROFILE_ERROR_CODE DH-901',
        'Generate a fresh 24-hour Dhan Access Token from Dhan web portal and update .secrets/dhan.env and GCP Secret Manager.',
        'YES: Owner must log into Dhan portal, generate new Access Token, and paste it into .secrets/dhan.env'
    ],
    [
        'BLK-02', 'Cloud Run Deployment & Mutation Restricted Without Explicit Approval', 'CRITICAL',
        'Constitutional AGENTS.md and CLOUD_ONLY_OWNER_DIRECTIVE_20261018 strictly prohibit new billable cloud builds, container deployments, or IAM mutations without separate explicit owner consent.',
        'Directive 20261018: Separate explicit owner approval is required before any new billable cloud build/deployment or cloud configuration mutation.',
        'Present complete consolidation dry-run evidence package and request explicit owner sign-off for Cloud Run deployment.',
        'YES: Owner must provide explicit approval string (e.g. APPROVE CLOUD RUN DEPLOYMENT)'
    ],
    [
        'BLK-03', 'Local Port 8008 Server Inactive in Current Session', 'MEDIUM',
        'Local uvicorn server on port 8008 is not currently running; pytest endpoint suites fail with ConnectionRefusedError.',
        'pytest tests/test_ui_p0_recovery_mission.py exited with WinError 10061 (No connection could be made)',
        'Launch server via scripts/start_backend_persistent.py or scheduled task before executing endpoint suites.',
        'NO: Autonomous agent action (can be launched when ready)'
    ]
]
for r in blocker_rows:
    ws_f2.append(r)
style_sheet(ws_f2, 'BLOCKER_REGISTER')
wb_f.save('GENESIS_FINAL_IMPLEMENTATION_REPORT.xlsx')
print('Saved GENESIS_FINAL_IMPLEMENTATION_REPORT.xlsx')

# ==========================================
# 7. GENESIS_FINAL_IMPLEMENTATION_REPORT.json
# ==========================================
print('Generating GENESIS_FINAL_IMPLEMENTATION_REPORT.json...')
final_json = {
  "repository_scan": {
    "files_scanned": 2819,
    "duplicates_found": 4,
    "orphan_files": 2
  },
  "architecture": {
    "status": "MERGE_CANDIDATES_MAPPED_DRY_RUN",
    "primary_runtime": "dashboard/backend"
  },
  "dhan": {
    "authentication": "FAILED_TOKEN_EXPIRED (HTTP 401 / DH-901; Expired 2026-11-10T08:38:50 UTC)",
    "market_data": "BLOCKED_UPSTREAM_TOKEN_EXPIRED",
    "paper_mode": "ACTIVE_VERIFIED (LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0)"
  },
  "merge_candidates": [
    {
      "source": "content/app/verified_market.py",
      "destination": "dashboard/backend/routers/chain.py",
      "features": ["Dhan marketfeed quotes", "Rate limiting", "Market session validation", "Verified market endpoint logic"]
    },
    {
      "source": "content/app/probe_dhan_credentials.py",
      "destination": "dashboard/backend/broker/dhan_auth.py",
      "features": ["JWT expiry decoding", "Credential validation", "Auth diagnostics", "Secret-safe reporting"]
    },
    {
      "source": "content/app/dhan_account_router.py",
      "destination": "dashboard/backend/routers/broker.py",
      "features": ["Holdings normalization", "Response normalization", "Profile masking", "Account summary helpers"]
    },
    {
      "source": "content/app/configure_safe_env.py",
      "destination": "scripts/configure_safe_env.py",
      "features": ["Strict environment safety lock enforcement"]
    }
  ],
  "delete_candidates": [
    "content/app/templates/premium.html.bak",
    "content/app/truth_backups/20261102T162014Z/app.py",
    "content/app/truth_backups/20261102T162014Z/premium.html",
    "content/app/truth_backups/verified_gate_20261102T165613Z/app.py",
    "content/app/truth_backups/verified_gate_20261102T165613Z/premium.html",
    "content/app/uvicorn_detached.log",
    "dashboard/backend/app.py.bak",
    "dashboard/backend/app.py.bak_20261101_065834",
    "dashboard/backend/app.py.bak_market_top_route",
    "dashboard/backend/app.py.bak_perma_del_20261101_074025",
    "dashboard/backend/app.py.bak_perma_del_20261101_074148",
    "dashboard/backend/test_temp.txt"
  ],
  "blockers": [
    {
      "id": "BLK-01",
      "title": "Dhan Access Token Expired (HTTP 401 DH-901)",
      "root_cause": "Daily Dhan JWT expired on 2026-11-10T08:38:50 UTC. Read-only live quote and account endpoints return HTTP 401.",
      "remediation": "Owner must generate a fresh 24-hour Dhan Access Token via Dhan web portal and update .secrets/dhan.env and GCP Secret Manager."
    },
    {
      "id": "BLK-02",
      "title": "Cloud Run Deployment & Mutation Restricted Without Explicit Owner Approval",
      "root_cause": "Constitutional AGENTS.md and CLOUD_ONLY_OWNER_DIRECTIVE_20261018 strictly prohibit new billable cloud builds, container deployments, or IAM mutations without separate explicit owner consent.",
      "remediation": "Present tested consolidation artifacts to owner for review and request explicit deployment authorization."
    },
    {
      "id": "BLK-03",
      "title": "Dual Parallel Architectures (content/app vs dashboard/backend)",
      "root_cause": "Historical rapid prototyping led to duplicate route and broker logic across content/app and dashboard/backend.",
      "remediation": "Execute Phase 2 controlled merge of verified_market.py, probe_dhan_credentials.py, and dhan_account_router.py into dashboard/backend."
    }
  ],
  "risks": [
    {
      "risk": "Accidental Live Order Execution",
      "severity": "CRITICAL",
      "mitigation": "Hardlocked by LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0, ANALYZE_MODE=1, PAPER_MODE=1, and zero-order safety gate."
    },
    {
      "risk": "Market Data Degradation During Consolidation",
      "severity": "HIGH",
      "mitigation": "Preserve verified Dhan marketfeed rate limiter and security master resolution in dashboard/backend/routers/chain.py."
    },
    {
      "risk": "Cloud Run Environment Drift",
      "severity": "MEDIUM",
      "mitigation": "Require exact Git SHA build provenance and verify Cloud Run revision image digest matches GitHub origin/main."
    }
  ],
  "acceptance_criteria": [
    {
      "criterion": "ARCHITECTURE: dashboard/backend is primary runtime; single canonical implementation; no active duplicates",
      "verdict": "YELLOW (Mapped in dry run; pending merge execution)"
    },
    {
      "criterion": "DHAN: Dhan authentication works; real Dhan data available; holdings/funds/positions work; no synthetic/mock production path",
      "verdict": "RED (FAIL: Dhan JWT expired 2026-11-10T08:38:50 UTC; HTTP 401 DH-901)"
    },
    {
      "criterion": "SAFETY: LIVE_TRADING_ENABLED=0; SYSTEM3_LIVE_TRADING_ALLOWED=0; zero real order execution path; paper trading functional",
      "verdict": "GREEN (PASS: Constitutional safety locks fully intact and verified)"
    },
    {
      "criterion": "TESTING: Unit tests pass; integration tests pass; startup validation passes; no runtime failures",
      "verdict": "RED (FAIL: Unit safety & startup tests PASS; endpoint integration tests blocked by offline server and expired token)"
    },
    {
      "criterion": "CLOUD: Cloud Run deployment succeeds; health endpoints pass; broker status passes; Dhan verified; no deployment regressions",
      "verdict": "RED (BLOCKED: Revision 136 healthy, but deploy mutation requires explicit owner approval; Dhan token expired)"
    }
  ],
  "deployment_signoff": [
    {"section": "SOURCE CONTROL", "item": "GitHub main clean & no merge conflicts", "status": "PENDING (9 commits behind origin/main)"},
    {"section": "ARCHITECTURE", "item": "dashboard/backend primary runtime & no duplicates", "status": "BLOCKED (Requires merge execution)"},
    {"section": "DHAN", "item": "Authentication, market data, holdings verified", "status": "BLOCKED (JWT token expired)"},
    {"section": "SAFETY", "item": "LIVE_TRADING_ENABLED=0 & real orders blocked", "status": "APPROVED (PASS)"},
    {"section": "TESTING", "item": "Unit, integration, and startup tests pass", "status": "BLOCKED (Token expired & server offline)"},
    {"section": "CLOUD", "item": "Cloud Run build, deploy, and health verified", "status": "BLOCKED (Owner approval required)"}
  ],
  "final_status": "RED",
  "recommended_next_action": "STOP per mandate. Document Blocker BLK-01 (Dhan JWT expired) and BLK-02 (Cloud Run deployment approval required). Request owner token refresh and deployment approval before proceeding to live execution."
}

with open('GENESIS_FINAL_IMPLEMENTATION_REPORT.json', 'w', encoding='utf-8') as f:
    json.dump(final_json, f, indent=2)

print('Saved GENESIS_FINAL_IMPLEMENTATION_REPORT.json')
