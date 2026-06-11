# System3 Master Control Plane

Generated UTC: 2026-06-11T17:10:55.739879+00:00

- Verdict: `TRADE_READY_BLOCKED`
- Trade ready: `False`
- Live trading enabled: `False`
- Mode: `Analyzer/Paper only`

## Gate Matrix

| Gate | Status | Pass | Blockers | Warnings |
|---|---|---:|---:|---:|
| `safety_and_secrets` | `FAIL` | `False` | `2` | `0` |
| `repo_authority_and_duplicate_control` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `deployment_and_endpoint_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `fresh_data_automation_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `2` |
| `model_training_load_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `2` |
| `recent_backtest_walkforward_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `analyzer_paper_lifecycle_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `dashboard_truth_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |

## Active blockers

- `safety_and_secrets:forbidden_secret_style_files_tracked`
- `safety_and_secrets:possible_secret_like_content_in_tracked_text`

## Manual-only items

- broker OTP/manual login/session renewal when required
- secure GitHub/runner/Render secret creation
- real live trading enablement
- unknown real broker position resolution
- model promotion approval when metrics are weak or unproven
