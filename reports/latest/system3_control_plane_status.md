# System3 Global Control Plane Status

Generated UTC: `2026-07-14T21:11:08.216273+00:00`

## Overall Verdict

`FAIL_FORBIDDEN_REPORT_PATH`

## Script Runs

| Script | Status | Return Code |
|---|---:|---:|
| `scripts/system3_markdown_inventory.py` | `FAIL` | `2` |
| `scripts/system3_option_visibility_audit.py` | `PASS` | `0` |
| `scripts/system3_model_accuracy_tracker.py` | `PASS` | `0` |
| `scripts/system3_blocker_finder.py` | `PASS` | `0` |

## Expected Reports

| Report | Exists | Size Bytes |
|---|---:|---:|
| `reports/latest/markdown_inventory.json` | `True` | `463769` |
| `reports/latest/markdown_inventory.md` | `True` | `120518` |
| `reports/latest/documentation_contradictions.md` | `True` | `113609` |
| `reports/latest/option_strike_visibility.json` | `True` | `891` |
| `reports/latest/option_strike_visibility.md` | `True` | `796` |
| `reports/latest/model_accuracy_report.json` | `True` | `878` |
| `reports/latest/model_accuracy_report.md` | `True` | `851` |
| `reports/latest/system3_blocker_report.json` | `True` | `1029` |
| `reports/latest/system3_blocker_report.md` | `True` | `790` |

## Summaries

### markdown_summary

- **generated_at_utc**: `2026-07-14T21:10:53.441405+00:00`
- **root**: `C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3`
- **total_markdown_files**: `743`
- **required_active_docs_present**: `10`
- **required_active_docs_total**: `10`
- **missing_required_active_docs**: `[]`
- **class_counts**: `{'HISTORICAL_REPORT': 518, 'UNKNOWN': 1, 'DUPLICATE_RISK': 196, 'REFERENCE': 18, 'ACTIVE_CONTROL': 10}`
- **risk_term_file_count**: `528`
- **strong_ready_file_count**: `53`
- **duplicate_risk_file_count**: `306`
- **contradiction_file_count**: `519`
- **open_blockers_detected**: `True`

### option_summary

- **generated_at_utc**: `2026-07-14T21:11:03.259136+00:00`
- **signal_source**: `no-signal-source-found`
- **option_master_source**: `security_id_list.csv`
- **rows**: `1`
- **paper_trade_allowed_count**: `0`
- **blocked_count**: `1`

### model_summary

- **generated_at_utc**: `2026-07-14T21:11:06.932544+00:00`
- **sources**: `[]`
- **rows**: `1`
- **proof_pass_count**: `0`
- **blocked_count**: `1`
- **direction_known_count**: `0`
- **direction_hit_rate**: `None`
- **option_profitable_known_count**: `0`

### blocker_summary

- **generated_at_utc**: `2026-07-14T21:11:08.048697+00:00`
- **root**: `C:\actions-runner-genesis\_work\Genesis_System3\Genesis_System3`
- **api_base**: `https://genesis-system3-backend.onrender.com`
- **state_source**: `api:https://genesis-system3-backend.onrender.com/api/state`
- **state_error**: `HTTP_ERROR_401: Unauthorized`
- **broker_source**: `api:https://genesis-system3-backend.onrender.com/api/broker/status`
- **broker_error**: `HTTP_ERROR_401: Unauthorized`
- **total_blockers**: `1`
- **severity_counts**: `{'MEDIUM': 1}`
- **safety_status**: `PAPER_SAFETY_NOT_BLOCKED_BY_STATIC_SCAN`

## Safety Statement

This runner and its child scripts are intended to be read-only verification/reporting tools. They do not enable live trading, do not place orders, and do not touch credentials.

## Next Rule

Do not patch runtime logic until this status report, blocker report, option visibility report, and model accuracy report have been reviewed.
