# System3 Global Control Plane Status

Generated UTC: `2026-07-24T03:39:09.317958+00:00`

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
| `reports/latest/markdown_inventory.json` | `True` | `492366` |
| `reports/latest/markdown_inventory.md` | `True` | `126958` |
| `reports/latest/documentation_contradictions.md` | `True` | `116055` |
| `reports/latest/option_strike_visibility.json` | `True` | `3110` |
| `reports/latest/option_strike_visibility.md` | `True` | `1606` |
| `reports/latest/model_accuracy_report.json` | `True` | `878` |
| `reports/latest/model_accuracy_report.md` | `True` | `851` |
| `reports/latest/system3_blocker_report.json` | `True` | `492` |
| `reports/latest/system3_blocker_report.md` | `True` | `724` |

## Summaries

### markdown_summary

- **generated_at_utc**: `2026-07-24T03:39:00.967173+00:00`
- **root**: `C:\System3\Genesis_System3`
- **total_markdown_files**: `795`
- **required_active_docs_present**: `10`
- **required_active_docs_total**: `10`
- **missing_required_active_docs**: `[]`
- **class_counts**: `{'HISTORICAL_REPORT': 537, 'UNKNOWN': 31, 'DUPLICATE_RISK': 199, 'REFERENCE': 18, 'ACTIVE_CONTROL': 10}`
- **risk_term_file_count**: `535`
- **strong_ready_file_count**: `61`
- **duplicate_risk_file_count**: `310`
- **contradiction_file_count**: `526`
- **open_blockers_detected**: `True`

### option_summary

- **generated_at_utc**: `2026-07-24T03:39:07.968997+00:00`
- **signal_source**: `api:http://127.0.0.1:8000/api/gain_rank`
- **option_master_source**: `security_id_list.csv`
- **rows**: `4`
- **paper_trade_allowed_count**: `0`
- **blocked_count**: `4`

### model_summary

- **generated_at_utc**: `2026-07-24T03:39:08.545002+00:00`
- **sources**: `[]`
- **rows**: `1`
- **proof_pass_count**: `0`
- **blocked_count**: `1`
- **direction_known_count**: `0`
- **direction_hit_rate**: `None`
- **option_profitable_known_count**: `0`

### blocker_summary

- **generated_at_utc**: `2026-07-24T03:39:08.974870+00:00`
- **root**: `C:\System3\Genesis_System3`
- **api_base**: `http://127.0.0.1:8000`
- **state_source**: `api:http://127.0.0.1:8000/api/state`
- **state_error**: `None`
- **broker_source**: `api:http://127.0.0.1:8000/api/broker/status`
- **broker_error**: `None`
- **total_blockers**: `0`
- **severity_counts**: `{}`
- **safety_status**: `PAPER_SAFETY_NOT_BLOCKED_BY_STATIC_SCAN`

## Safety Statement

This runner and its child scripts are intended to be read-only verification/reporting tools. They do not enable live trading, do not place orders, and do not touch credentials.

## Next Rule

Do not patch runtime logic until this status report, blocker report, option visibility report, and model accuracy report have been reviewed.
