# Root Runtime Authority Inventory — Compact Report Only

Generated: `2026-05-30T08:29:55.950200+00:00`

## Safety
- No files deleted.
- No files moved.
- No quarantine performed.
- Noise excluded: `desktop.ini`, logs, cache, dist, previous authority reports.

## Root / Docker / Backend Probe
| Probe | Result |
|---|---|
| `repo_root` | `/workspaces/Genesis_System3` |
| `backend_dir_exists` | `False` |
| `backend_dockerfile_exists` | `False` |
| `dockerignore_exists` | `False` |
| `deploy_backend_workflow_exists` | `False` |
| `dashboard_backend_dir_exists` | `True` |
| `dashboard_backend_dockerfile_exists` | `False` |

## Summary
| Metric | Count |
|---|---:|
| `tracked_files_scanned_after_noise_filter` | `3025` |
| `excluded_noise_rule` | `desktop.ini/log/cache/dist/report-authority paths excluded` |
| `duplicate_content_groups` | `7` |
| `duplicate_name_groups` | `20` |
| `unique_duplicate_files_limited_index` | `77` |
| `batch1_candidates` | `0` |
| `manual_review_required` | `19` |

## Top duplicate content groups
### Group 1
- Keep candidate: `GENESIS_MAGIC_ENV_FIX.bat`
  - `GENESIS_MAGIC_ENV_FIX.bat` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `GENESIS_MAGIC_ENV_FIX.md` — refs=9, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
### Group 2
- Keep candidate: `dashboard/frontend/src/components/AppSelfTest.tsx`
  - `dashboard/frontend/src/components/AppSelfTest.tsx` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `app_self_test_component.tsx` — refs=9, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### Group 3
- Keep candidate: `core/brokers/__init__.py`
  - `core/brokers/__init__.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `core/engine/system3_phase368_broker_latency_monitor.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `core/brokers/angel_one/__init__.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `reports/trader_test_20260210_075042.md` — refs=4, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `config/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `desktop_app/npm` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/data/__init__ - Copy - Copy - Copy (3).py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/data/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/engine/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### Group 4
- Keep candidate: `kill_switch.json`
  - `kill_switch.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `config/kill_switch.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### Group 5
- Keep candidate: `runtime_flags.json`
  - `runtime_flags.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `config/runtime_flags.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### Group 6
- Keep candidate: `config/system3_config.json`
  - `config/system3_config.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/engine/config/system3_config.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### Group 7
- Keep candidate: `docs/system3_phases_101_130_final_test_results - Copy.md`
  - `docs/system3_phases_101_130_final_test_results - Copy.md` — refs=16, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `docs/system3_phases_101_130_final_test_results.md` — refs=13, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER

## Top duplicate filename groups
### `settings.json`
- Keep candidate: `.cursor/settings.json`
  - `.cursor/settings.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `.vscode/settings.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `.env`
- Keep candidate: `.env`
  - `.env` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `config/.env` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
### `tasks.json`
- Keep candidate: `.vscode/tasks.json`
  - `.vscode/tasks.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `agent_memory/tasks.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `COMPLETE_VALIDATION_REPORT.md`
- Keep candidate: `COMPLETE_VALIDATION_REPORT.md`
  - `COMPLETE_VALIDATION_REPORT.md` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `docs/COMPLETE_VALIDATION_REPORT.md` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `README.md`
- Keep candidate: `dashboard/README.md`
  - `dashboard/README.md` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `README.md` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `docs/ultra_micro/README.md` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `reports/ci_truth/README.md` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `__init__.py`
- Keep candidate: `core/broker/__init__.py`
  - `core/broker/__init__.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `core/brokers/__init__.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `core/brokers/angel_one/__init__.py` — refs=20, criticality=critical_trading, recommendation=MANUAL_REVIEW_REQUIRED
  - `config/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/data/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/engine/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/execution/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/geni/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/models/__init__.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `kill_switch.json`
- Keep candidate: `kill_switch.json`
  - `kill_switch.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `config/kill_switch.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `runtime_flags.json`
- Keep candidate: `runtime_flags.json`
  - `runtime_flags.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `config/runtime_flags.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `system3_config.json`
- Keep candidate: `config/system3_config.json`
  - `config/system3_config.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/engine/config/system3_config.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `ensemble_predictor.py`
- Keep candidate: `core/engine/ensemble_predictor.py`
  - `core/engine/ensemble_predictor.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `src/ml/ensemble_predictor.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `greeks_calculator.py`
- Keep candidate: `dashboard/backend/greeks_calculator.py`
  - `dashboard/backend/greeks_calculator.py` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `core/engine/greeks_engine/greeks_calculator.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `system3_phase331_signal_integrity.py`
- Keep candidate: `system3_phase331_signal_integrity.py`
  - `system3_phase331_signal_integrity.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `core/engine/system3_phase331_signal_integrity.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `app.py`
- Keep candidate: `dashboard/app.py`
  - `dashboard/app.py` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `dashboard/backend/app.py` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
### `index.html`
- Keep candidate: `dashboard/index.html`
  - `dashboard/index.html` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `dashboard/frontend/index.html` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `reports/model_benchmark_dashboard/index.html` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
### `package-lock.json`
- Keep candidate: `dashboard/frontend/package-lock.json`
  - `dashboard/frontend/package-lock.json` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `package-lock.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `desktop_app/package-lock.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `package.json`
- Keep candidate: `dashboard/frontend/package.json`
  - `dashboard/frontend/package.json` — refs=20, criticality=sensitive, recommendation=MANUAL_REVIEW_REQUIRED
  - `package.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `desktop_app/package.json` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `performance_metrics.py`
- Keep candidate: `scripts/performance_metrics.py`
  - `scripts/performance_metrics.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `src/analytics/performance_metrics.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `start_backend.bat`
- Keep candidate: `start_backend.bat`
  - `start_backend.bat` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `scripts/start_backend.bat` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `start_backend.bat.bak_20260225_005921`
- Keep candidate: `start_backend.bat.bak_20260225_005921`
  - `start_backend.bat.bak_20260225_005921` — refs=12, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `scripts/start_backend.bat.bak_20260225_005921` — refs=12, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
### `test_phases_261_300.py`
- Keep candidate: `test_phases_261_300.py`
  - `test_phases_261_300.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER
  - `tests/auto/system3_generated_tests/test_phases_261_300.py` — refs=20, criticality=normal, recommendation=KEEP_OR_REVIEW_LATER