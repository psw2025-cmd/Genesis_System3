# System3 Master Control Plane

Generated UTC: 2026-06-14T14:02:21.248313+00:00

- Verdict: `ANALYZER_READY_PROOF_INCOMPLETE`
- Trade ready: `False`
- Live trading enabled: `False`
- Mode: `Analyzer/Paper only`

## Gate Matrix

| Gate | Status | Pass | Blockers | Warnings |
|---|---|---:|---:|---:|
| `safety_and_secrets` | `PASS` | `True` | `0` | `0` |
| `repo_authority_and_duplicate_control` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `deployment_and_endpoint_proof` | `PASS` | `True` | `0` | `0` |
| `fresh_data_automation_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `3` |
| `model_training_load_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `2` |
| `recent_backtest_walkforward_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `analyzer_paper_lifecycle_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `1` |
| `dashboard_truth_proof` | `PASS_WITH_WARNINGS` | `True` | `0` | `2` |

## Active blockers

- None

## Manual-only items

- broker OTP/manual login/session renewal when required
- secure GitHub/runner/Render secret creation
- real live trading enablement
- unknown real broker position resolution
- model promotion approval when metrics are weak or unproven
