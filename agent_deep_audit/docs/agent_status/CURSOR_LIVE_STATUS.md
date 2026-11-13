# Cursor live status — W4 LIVE_GATE alert leak

WAVE=CURSOR-W4-LIVE-GATE-ALERT-LEAK
OWNER=CURSOR
CURRENT_MAIN_AT_START=9d9f53613ff5f286290bd352a3eb61ea0cb2a20c
SERVING_SHA_AT_START=9d9f53613ff5f286290bd352a3eb61ea0cb2a20c
UPDATED_UTC=2026-08-18T12:15:00Z
STATE=IMPLEMENTING

## Defect reproduced

Production Alerts tab showed `1 ACTIVE` with:

`human_approved=NOT APPROVED — owner must set live_trading_approved=true in kill_switch.json`

The right rail already said Live Readiness = BLOCKED BY DESIGN. `/api/alerts/recent`
synth used `type=system_alert` and `id=OPS_LIVE_GATE`. AlertsTab only hid
`type===LIVE_GATE`, so the kill-switch instruction leaked into Active.

## Files owned this wave

- dashboard/frontend/src/lib/alertTruth.ts
- dashboard/frontend/src/components/AlertsTab.tsx
- dashboard/backend/app.py
- tests/test_paper_alert_truth_contract.py
- tests/evals/test_eval_live_gate_alert_leak.py
- tests/test_live_ui_truth_remediation_contract.py

## Safety

LIVE=false ORDERS=false TOKEN_MUTATION=false IAM_MUTATION=false
CLAUDE_OVERLAP=none
USER_ACTION_REQUIRED=false
