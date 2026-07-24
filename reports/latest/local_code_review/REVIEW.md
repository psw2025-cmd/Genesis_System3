# Local Code Review (Cursor Review alternative)

- Generated: `2026-07-24T03:42:11.379982Z`
- Verdict: **FAIL**
- Changed files: **36**

> Free local review — no Cursor AI credits required.

## Summary

| Check | Status |
|---|---|
| git_summary | PASS |
| architecture_gate | PASS |
| verify_cursor_agent_bugs | PASS |
| py_compile | PASS |
| ast_static_scan | PASS |
| flake8 | FAIL |
| bandit | SKIP |
| pytest | FAIL |
| blocker_finder | SKIP |

## Changed files

- `check_integrity.py`
- `config/human_approval_gate.json`
- `docs/project_control/SYSTEM3_MASTER_STATUS.md`
- `reports/latest/analyzer_paper_lifecycle_proof/README.md`
- `reports/latest/analyzer_paper_lifecycle_proof/summary.json`
- `reports/latest/auto_recovery_blockers/README.md`
- `reports/latest/auto_recovery_blockers/auto_recovery_blockers.json`
- `reports/latest/dashboard_truth_proof/README.md`
- `reports/latest/dashboard_truth_proof/summary.json`
- `reports/latest/deployment_and_endpoint_proof/README.md`
- `reports/latest/deployment_and_endpoint_proof/summary.json`
- `reports/latest/fresh_data_automation_proof/README.md`
- `reports/latest/fresh_data_automation_proof/summary.json`
- `reports/latest/friction_expectancy/summary.json`
- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`
- `reports/latest/model_accuracy_report.json`
- `reports/latest/model_accuracy_report.md`
- `reports/latest/model_training_load_proof/README.md`
- `reports/latest/model_training_load_proof/summary.json`
- `reports/latest/option_strike_visibility.json`
- `reports/latest/option_strike_visibility.md`
- `reports/latest/production_viability_bridge/latest.json`
- `reports/latest/production_viability_bridge/summary.md`
- `reports/latest/proof_status_matrix/proof_status_matrix.json`
- `reports/latest/recent_backtest_walkforward_proof/README.md`
- `reports/latest/recent_backtest_walkforward_proof/summary.json`
- `reports/latest/repo_authority_and_duplicate_control/README.md`
- `reports/latest/repo_authority_and_duplicate_control/summary.json`
- `reports/latest/safety_and_secrets/README.md`
- `reports/latest/safety_and_secrets/summary.json`
- `reports/latest/system3_auto_coordinator/summary.json`
- `reports/latest/system3_auto_coordinator/summary.md`
- `reports/latest/system3_auto_gates/summary.json`
- `reports/latest/system3_auto_gates/summary.md`
- `reports/latest/system3_master_control_plane/README.md`
- `reports/latest/system3_master_control_plane/system3_master_control_plane.json`

## Details

### git_summary — PASS

```
branch=main, changed_files=36
```

Findings: 1
- `{"branch": "main", "changed": ["check_integrity.py", "config/human_approval_gate.json", "docs/project_control/SYSTEM3_MASTER_STATUS.md", "reports/latest/analyzer_paper_lifecycle_proof/README.md", "reports/latest/analyzer_paper_lifecycle_proof/summary.json", "reports/latest/auto_recovery_blockers/README.md", "reports/latest/auto_recovery_blockers/auto_recovery_blockers.json", "reports/latest/dashboard_truth_proof/README.md", "reports/latest/dashboard_truth_proof/summary.json", "reports/latest/deployment_and_endpoint_proof/README.md", "reports/latest/deployment_and_endpoint_proof/summary.json", "reports/latest/fresh_data_automation_proof/README.md", "reports/latest/fresh_data_automation_proof/summary.json", "reports/latest/friction_expectancy/summary.json", "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json", "reports/latest/model_accuracy_report.json", "reports/latest/model_accuracy_report.md", "reports/latest/model_training_load_proof/README.md", "reports/latest/model_training_load_proof/summary.json", "reports/latest/option_strike_visibility.json", "reports/latest/option_strike_visibility.md", "reports/latest/production_viability_bridge/latest.json", "reports/latest/production_viability_bridge/summary.md", "reports/latest/proof_status_matrix/proof_status_matrix.json", "reports/latest/recent_backtest_walkforward_proof/README.md", "reports/latest/recent_backtest_walkforward_proof/summary.json", "reports/latest/repo_authority_and_duplicate_control/README.md", "reports/latest/repo_authority_and_duplicate_control/summary.json", "reports/latest/safety_and_secrets/README.md", "reports/latest/safety_and_secrets/summary.json", "reports/latest/system3_auto_coordinator/summary.json", "reports/latest/system3_auto_coordinator/summary.md", "reports/latest/system3_auto_gates/summary.json", "reports/latest/system3_auto_gates/summary.md", "reports/latest/system3_master_control_plane/README.md", "reports/latest/system3_master_control_plane/system3_master_control_plane.json"], "status_short": "M config/human_approval_gate.json\n M docs/project_control/SYSTEM3_MASTER_STATUS.md\n M reports/latest/analyzer_paper_lifecycle_proof/README.md\n M reports/latest/analyzer_paper_lifecycle_proof/summary.json\n M reports/latest/auto_recovery_blockers/README.md\n M reports/latest/auto_recovery_blockers/auto_recovery_blockers.json\n M reports/latest/dashboard_truth_proof/README.md\n M reports/latest/dashboard_truth_proof/summary.json\n M reports/latest/deployment_and_endpoint_proof/README.md\n M reports/latest/deployment_and_endpoint_proof/summary.json\n M reports/latest/fresh_data_automation_proof/README.md\n M reports/latest/fresh_data_automation_proof/summary.json\n M reports/latest/friction_expectancy/summary.json\n M reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json\n M reports/latest/model_accuracy_report.json\n M reports/latest/model_accuracy_report.md\n M reports/latest/model_training_load_proof/README.md\n M reports/latest/model_training_load_proof/summary.json\n M reports/latest/option_strike_visibility.json\n M reports/latest/option_strike_visibility.md\n M reports/latest/production_viability_bridge/latest.json\n M reports/latest/production_viability_bridge/summary.md\n M reports/latest/proof_status_matrix/proof_status_matrix.json\n M reports/latest/recent_backtest_walkforward_proof/README.md\n M reports/latest/recent_backtest_walkforward_proof/summary.json\n M reports/latest/repo_authority_and_duplicate_control/README.md\n M reports/latest/repo_authority_and_duplicate_control/summary.json\n M reports/latest/safety_and_secrets/README.md\n M reports/latest/safety_and_secrets/summary.json\n M reports/latest/system3_auto_coordinator/summary.json\n M reports/latest/system3_auto_coordinator/summary.md\n M reports/latest/system3_auto_gates/summary.json\n M reports/latest/system3_auto_gates/summary.md\n M reports/latest/system3_master_control_plane/README.md\n M reports/latest/system3_master_control_plane/system3_master_control_plane.json\n?? reports/latest/documentation_contradictions.md\n?? reports/latest/friction_expectancy/summary.md\n?? reports/latest/local_code_review/\n?? reports/latest/markdown_inventory.json\n?? reports/latest/markdown_inventory.md\n?? reports/latest/model_to_trade_gap/\n?? reports/latest/system3_blocker_report.json\n?? reports/latest/system3_blocker_report.md\n?? reports/latest/system3_control_plane_status.json\n?? reports/latest/system3_control_plane_status.md\n?? reports/latest/websocket_tick_health/"}`

### architecture_gate — PASS

```
{
  "generated_at_utc": "2026-07-24T03:42:09.064267+00:00",
  "policy": "Architecture and trading safety must be FULL PASS. Only ci.yml is the active workflow.",
  "blocking": true,
  "changed_files": [
    "check_integrity.py"
  ],
  "checks": [
    {
      "name": "required_files_and_dirs",
      "status": "PASS",
      "missing_files": [],
      "missing_dirs": []
    },
    {
      "name": "critical_python_compile",
      "status": "PASS",
      "files_checked": [
        "run_system3.py",
        ".github\\scripts\\root_architecture_gate.py"
      ],
      "failures": []
    },
    {
      "name": "protected_runtime_paths_not_changed",
      "status": "PASS",
      "changed_files": [
        "check_integrity.py"
      ],
      "violations": []
    },
    {
      "name": "no_env_db_model_artifacts_changed",
      "status": "PASS",
      "blocked_files": []
    },
    {
      "name": "no_secret_like_values_in_changed_files",
      "status": "PASS",
      "findings": []
    },
    {
      "name": "no_obvious_live_trading_enablement_in_changed_files",
      "status": "PASS",
      "findings": []
    }
  ],
  "status": "PASS",
  "failed_count": 0,
  "protected_scope": {
    "trading_logic_changed": false,
    "broker_config_changed": false,
    "env_changed": false,
    "database_changed": false,
    "model_artifacts_changed": false
  }
}
```

### verify_cursor_agent_bugs — PASS

```
=== verify_cursor_agent_bugs ===

[OK] Fake LIVE gating: live_allowed/live_blockers present; synthetic never LIVE
[OK] At least 2 explicit except Exception in app.py (bare count=28, fix remaining for full PASS)
[OK] No duplicate repo_root_path assignments found
[OK] Logger check done (no attribution symbol found or has logger)

Result: PASS
```

### py_compile — PASS

```
compiled 1 file(s)
```

### ast_static_scan — PASS

```
0 finding(s)
```

### flake8 — FAIL

```
C:\System3\Genesis_System3\venv\Scripts\python.exe: No module named flake8
```

Findings: 1
- `{"line": "C:\\System3\\Genesis_System3\\venv\\Scripts\\python.exe: No module named flake8"}`

### bandit — SKIP

```
bandit not installed (pip install bandit)
```

### pytest — FAIL

```
targets=['tests/']
C:\System3\Genesis_System3\venv\Scripts\python.exe: No module named pytest
```

### blocker_finder — SKIP

```
use --full to run
```

## How to run

```bat
python tools/local_code_review.py
python tools/local_code_review.py --full
```
