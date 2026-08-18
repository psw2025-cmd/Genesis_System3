# Cursor live status — W1 broker reliability + 906 core

WAVE=CURSOR-W1-BROKER-RELIABILITY-PLUS-906-CORE
OWNER=CURSOR
CURRENT_MAIN_AT_START=6fdcb398a67c1cdf57fc231db778be2f62897018
SERVING_SHA_AT_START=06103b4abf1ebcb530a43369cff9b8dafc9f5f30
UPDATED_UTC=2026-08-18T10:15:00Z
STATE=GATES_PENDING

## Live recurrence evidence

PROBE_UTC=2026-08-18T10:02:39Z
connected=false
error=DHAN_REQUEST_REJECTED_906
auth_classification=null
secret_version=269
expired=false
hours_remaining=23.28
attempts:
- docs-access-token-only HTTP 400 code 906
- sdk-dhanClientId HTTP 400 code 906

## Core issue

DH-906 is a non-auth request rejection. The probe treated it as a header-contract
fallback and issued a second Profile GET. Token rotation on 906 did not prevent
recurrence. Official Profile GET is access-token only.

## Files owned this wave

- core/brokers/dhan/cloud_status_probe.py
- tests/test_dhan_profile_header_reconcile.py
- dashboard/frontend/src/lib/healthTruth.ts
- dashboard/frontend/src/components/TopBar.tsx
- dashboard/frontend/src/components/BrokerPanel.tsx
- dashboard/frontend/src/components/SystemProgressPanel.tsx
- tests/test_live_ui_truth_remediation_contract.py
- docs/BROKER_RECURRENCE_FORENSIC_CHECKLIST.md
- reports/latest/broker_recovery_20260818_live/README.md
- CHANGE_LOG.md

## Safety

LIVE=false ORDERS=false TOKEN_MUTATION=false IAM_MUTATION=false
CLAUDE_OVERLAP=none
