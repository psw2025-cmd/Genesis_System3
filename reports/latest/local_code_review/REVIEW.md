# Local Code Review (Cursor Review alternative)

- Generated: `2026-07-14T21:11:23.608897Z`
- Verdict: **PASS**
- Changed files: **10**

> Free local review — no Cursor AI credits required.

## Summary

| Check | Status |
|---|---|
| git_summary | PASS |
| architecture_gate | PASS |
| verify_cursor_agent_bugs | PASS |
| py_compile | SKIP |
| ast_static_scan | SKIP |
| flake8 | SKIP |
| bandit | SKIP |
| pytest | SKIP |
| blocker_finder | SKIP |

## Changed files

- `config/human_approval_gate.json`
- `reports/latest/friction_expectancy/summary.json`
- `reports/latest/model_accuracy_report.json`
- `reports/latest/model_accuracy_report.md`
- `reports/latest/option_strike_visibility.json`
- `reports/latest/option_strike_visibility.md`
- `reports/latest/production_viability_bridge/latest.json`
- `reports/latest/production_viability_bridge/summary.md`
- `reports/latest/system3_auto_gates/summary.json`
- `reports/latest/system3_auto_gates/summary.md`

## Details

### git_summary — PASS

```
branch=main, changed_files=10
```

Findings: 1
- `{"branch": "main", "changed": ["config/human_approval_gate.json", "reports/latest/friction_expectancy/summary.json", "reports/latest/model_accuracy_report.json", "reports/latest/model_accuracy_report.md", "reports/latest/option_strike_visibility.json", "reports/latest/option_strike_visibility.md", "reports/latest/production_viability_bridge/latest.json", "reports/latest/production_viability_bridge/summary.md", "reports/latest/system3_auto_gates/summary.json", "reports/latest/system3_auto_gates/summary.md"], "status_short": "M config/human_approval_gate.json\n M reports/latest/friction_expectancy/summary.json\n M reports/latest/model_accuracy_report.json\n M reports/latest/model_accuracy_report.md\n M reports/latest/option_strike_visibility.json\n M reports/latest/option_strike_visibility.md\n M reports/latest/production_viability_bridge/latest.json\n M reports/latest/production_viability_bridge/summary.md\n M reports/latest/system3_auto_gates/summary.json\n M reports/latest/system3_auto_gates/summary.md\n?? reports/latest/documentation_contradictions.md\n?? reports/latest/friction_expectancy/summary.md\n?? reports/latest/markdown_inventory.json\n?? reports/latest/markdown_inventory.md\n?? reports/latest/model_to_trade_gap/\n?? reports/latest/system3_blocker_report.json\n?? reports/latest/system3_blocker_report.md\n?? reports/latest/system3_control_plane_status.json\n?? reports/latest/system3_control_plane_status.md\n?? reports/latest/websocket_tick_health/"}`

### architecture_gate — PASS

```
{
  "generated_at_utc": "2026-07-14T21:11:21.534467+00:00",
  "policy": "Architecture and trading safety must be FULL PASS. Only ci.yml is the active workflow.",
  "blocking": true,
  "changed_files": [],
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
      "changed_files": [],
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

### py_compile — SKIP

```
no changed Python files
```

### ast_static_scan — SKIP

```
no changed Python files
```

### flake8 — SKIP

```
no changed Python files
```

### bandit — SKIP

```
no changed Python files
```

### pytest — SKIP

```
no mapped tests for changed files
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
