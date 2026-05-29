# Root Runtime Authority Inventory — Report Only

Generated: `2026-05-29T22:05:28.900922+00:00`

## Safety policy
- No files deleted.
- No files moved.
- No quarantine performed.
- This PR is discovery/report only.

## Root / Docker / Backend probe
| Probe | Result |
|---|---|
| `repo_root` | `/workspaces/Genesis_System3` |
| `backend_dir_exists` | `False` |
| `backend_dockerfile_exists` | `False` |
| `dockerignore_exists` | `False` |
| `deploy_backend_workflow_exists` | `False` |

## Summary
| Metric | Count |
|---|---:|
| `tracked_files_scanned` | 3564 |
| `duplicate_content_groups` | 8 |
| `duplicate_name_groups` | 24 |
| `unique_duplicate_files` | 203 |
| `batch1_quarantine_candidates` | 3 |
| `manual_review_required` | 18 |

## Duplicate content groups
### Group 1: `70430ab232fc8800...`
- Keep candidate: `core/broker/desktop.ini`
  - `core/broker/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `src/angel/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/angel_one/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_real_blended/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_ultra/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_ultra_staging/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `src/storage/live/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `tools/storage/live/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `.qodo/workflows/desktop.ini` — class=`config`, criticality=`critical_devops`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `dashboard/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/e2e/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-10/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-11/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-22/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/assets/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/components/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/hooks/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/utils/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.cursor/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.github/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.qodo/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.vscode/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `models/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `phases/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `reports/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `runtime_reports/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `scripts/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `state/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `system3_full_inspector/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tools/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.github/instructions/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.qodo/agents/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/diffs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/proof_packs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/state_snapshots/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/data/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/execution/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/geni/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/monitoring/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/tools/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/ultra/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/validation/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/assets/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `models/xgboost_v1/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `reports/forensic/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/analytics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/core/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/metrics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/ml/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/output/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/outputs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/selector/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/sim/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/trading/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/utils/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/validation/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tools/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/ai_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/backups/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/breakout_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/entry_exit_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/greeks_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/momentum_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/scoring_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/trend_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/volatility_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/xgboost/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/backups/BEFORE_PHASE311_330_20251206_0249/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/anti_corruption/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/changesets/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/integrity/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/history/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/metrics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/system_health/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/logs/research/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/system_health/fs_baseline/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/test_runs/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/auto/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/auto/system3_generated_tests/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `docs/desktop.ini` — class=`doc`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `docs/ultra_micro/desktop.ini` — class=`doc`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`

### Group 2: `0969728a6fdda097...`
- Keep candidate: `GENESIS_MAGIC_ENV_FIX.bat`
  - `GENESIS_MAGIC_ENV_FIX.bat` — class=`production`, criticality=`sensitive`, refs=4, action=`KEEP_OR_REVIEW_LATER`
  - `GENESIS_MAGIC_ENV_FIX.md` — class=`doc`, criticality=`sensitive`, refs=4, action=`KEEP_OR_REVIEW_LATER`

### Group 3: `5d0586abf24c1288...`
- Keep candidate: `dashboard/frontend/src/components/AppSelfTest.tsx`
  - `dashboard/frontend/src/components/AppSelfTest.tsx` — class=`production`, criticality=`sensitive`, refs=22, action=`KEEP_OR_REVIEW_LATER`
  - `app_self_test_component.tsx` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`

### Group 4: `e3b0c44298fc1c14...`
- Keep candidate: `core/brokers/__init__.py`
  - `core/brokers/__init__.py` — class=`production`, criticality=`critical_trading`, refs=79, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/angel_one/__init__.py` — class=`production`, criticality=`critical_trading`, refs=79, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `desktop_app/npm` — class=`production`, criticality=`normal`, refs=97, action=`KEEP_OR_REVIEW_LATER`
  - `config/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/data/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/system3_phase368_broker_latency_monitor.py` — class=`production`, criticality=`critical_trading`, refs=17, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/data/__init__ - Copy - Copy - Copy (3).py` — class=`production`, criticality=`normal`, refs=2, action=`REVIEW_BEFORE_QUARANTINE`
  - `desktop_app/system3-ultra-desktop@1.0.0` — class=`production`, criticality=`normal`, refs=0, action=`QUARANTINE_CANDIDATE_BATCH_1`
  - `reports/trader_test_20260210_075042.md` — class=`doc`, criticality=`critical_trading`, refs=1, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`

### Group 5: `d945482e91f065ec...`
- Keep candidate: `kill_switch.json`
  - `kill_switch.json` — class=`config`, criticality=`normal`, refs=64, action=`KEEP_OR_REVIEW_LATER`
  - `config/kill_switch.json` — class=`config`, criticality=`normal`, refs=64, action=`KEEP_OR_REVIEW_LATER`

### Group 6: `edd5ad41e3148535...`
- Keep candidate: `runtime_flags.json`
  - `runtime_flags.json` — class=`config`, criticality=`normal`, refs=7, action=`KEEP_OR_REVIEW_LATER`
  - `config/runtime_flags.json` — class=`config`, criticality=`normal`, refs=7, action=`KEEP_OR_REVIEW_LATER`

### Group 7: `278608c6efe99c86...`
- Keep candidate: `config/system3_config.json`
  - `config/system3_config.json` — class=`config`, criticality=`normal`, refs=33, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/config/system3_config.json` — class=`config`, criticality=`normal`, refs=33, action=`KEEP_OR_REVIEW_LATER`

### Group 8: `7109bf4fb4db4edd...`
- Keep candidate: `docs/system3_phases_101_130_final_test_results - Copy.md`
  - `docs/system3_phases_101_130_final_test_results - Copy.md` — class=`doc`, criticality=`normal`, refs=2, action=`REVIEW_BEFORE_QUARANTINE`
  - `docs/system3_phases_101_130_final_test_results.md` — class=`doc`, criticality=`normal`, refs=5, action=`KEEP_OR_REVIEW_LATER`

## Duplicate filename groups
### `desktop.ini`
- Keep candidate: `core/broker/desktop.ini`
  - `core/broker/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `src/angel/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/angel_one/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_real_blended/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_ultra/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/models/angel_one_ultra_staging/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `src/storage/live/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `tools/storage/live/desktop.ini` — class=`config`, criticality=`critical_trading`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `.qodo/workflows/desktop.ini` — class=`config`, criticality=`critical_devops`, refs=107, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `dashboard/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/e2e/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-10/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-11/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/logs/2026-02-22/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/assets/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/components/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/hooks/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/src/utils/desktop.ini` — class=`config`, criticality=`sensitive`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.cursor/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.github/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.qodo/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.vscode/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `models/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `phases/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `reports/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `runtime_reports/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `scripts/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `state/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `system3_full_inspector/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tools/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.github/instructions/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `.qodo/agents/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/diffs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/proof_packs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/state_snapshots/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/data/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/execution/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/geni/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/monitoring/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/tools/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/ultra/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/validation/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/assets/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `models/xgboost_v1/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `reports/forensic/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/analytics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/core/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/metrics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/ml/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/output/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/outputs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/selector/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/sim/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/trading/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/utils/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `src/validation/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tools/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/ai_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/backups/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/breakout_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/config/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/entry_exit_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/greeks_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/momentum_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/scoring_engine/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/trend_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/volatility_model/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/xgboost/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/logs/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/backups/BEFORE_PHASE311_330_20251206_0249/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/anti_corruption/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/changesets/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/logs/integrity/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/history/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/metrics/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/system_health/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/logs/research/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/storage/system_health/fs_baseline/desktop.ini` — class=`config`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/test_runs/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/auto/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `tests/auto/system3_generated_tests/desktop.ini` — class=`test`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `docs/desktop.ini` — class=`doc`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`
  - `docs/ultra_micro/desktop.ini` — class=`doc`, criticality=`normal`, refs=107, action=`KEEP_OR_REVIEW_LATER`

### `settings.json`
- Keep candidate: `.cursor/settings.json`
  - `.cursor/settings.json` — class=`config`, criticality=`normal`, refs=47, action=`KEEP_OR_REVIEW_LATER`
  - `.vscode/settings.json` — class=`config`, criticality=`normal`, refs=47, action=`KEEP_OR_REVIEW_LATER`

### `.env`
- Keep candidate: `.env`
  - `.env` — class=`production`, criticality=`sensitive`, refs=85, action=`KEEP_OR_REVIEW_LATER`
  - `config/.env` — class=`production`, criticality=`sensitive`, refs=85, action=`KEEP_OR_REVIEW_LATER`

### `tasks.json`
- Keep candidate: `.vscode/tasks.json`
  - `.vscode/tasks.json` — class=`config`, criticality=`normal`, refs=108, action=`KEEP_OR_REVIEW_LATER`
  - `agent_memory/tasks.json` — class=`config`, criticality=`normal`, refs=108, action=`KEEP_OR_REVIEW_LATER`

### `COMPLETE_VALIDATION_REPORT.md`
- Keep candidate: `COMPLETE_VALIDATION_REPORT.md`
  - `COMPLETE_VALIDATION_REPORT.md` — class=`doc`, criticality=`normal`, refs=2, action=`REVIEW_BEFORE_QUARANTINE`
  - `docs/COMPLETE_VALIDATION_REPORT.md` — class=`doc`, criticality=`normal`, refs=2, action=`REVIEW_BEFORE_QUARANTINE`

### `README.md`
- Keep candidate: `dashboard/README.md`
  - `dashboard/README.md` — class=`doc`, criticality=`sensitive`, refs=40, action=`KEEP_OR_REVIEW_LATER`
  - `README.md` — class=`doc`, criticality=`normal`, refs=40, action=`KEEP_OR_REVIEW_LATER`
  - `docs/ultra_micro/README.md` — class=`doc`, criticality=`normal`, refs=40, action=`KEEP_OR_REVIEW_LATER`
  - `reports/ci_truth/README.md` — class=`doc`, criticality=`normal`, refs=40, action=`KEEP_OR_REVIEW_LATER`

### `__init__.py`
- Keep candidate: `core/broker/__init__.py`
  - `core/broker/__init__.py` — class=`production`, criticality=`critical_trading`, refs=79, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/__init__.py` — class=`production`, criticality=`critical_trading`, refs=79, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/angel_one/__init__.py` — class=`production`, criticality=`critical_trading`, refs=79, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `config/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/data/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/execution/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/geni/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/models/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/monitoring/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/tools/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/ultra/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/utils/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/validation/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/ai_model/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/breakout_model/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/entry_exit_engine/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/greeks_engine/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/momentum_model/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/scoring_engine/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/trend_model/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/volatility_model/__init__.py` — class=`production`, criticality=`normal`, refs=79, action=`KEEP_OR_REVIEW_LATER`

### `kill_switch.json`
- Keep candidate: `kill_switch.json`
  - `kill_switch.json` — class=`config`, criticality=`normal`, refs=64, action=`KEEP_OR_REVIEW_LATER`
  - `config/kill_switch.json` — class=`config`, criticality=`normal`, refs=64, action=`KEEP_OR_REVIEW_LATER`

### `runtime_flags.json`
- Keep candidate: `runtime_flags.json`
  - `runtime_flags.json` — class=`config`, criticality=`normal`, refs=7, action=`KEEP_OR_REVIEW_LATER`
  - `config/runtime_flags.json` — class=`config`, criticality=`normal`, refs=7, action=`KEEP_OR_REVIEW_LATER`

### `system3_config.json`
- Keep candidate: `config/system3_config.json`
  - `config/system3_config.json` — class=`config`, criticality=`normal`, refs=33, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/config/system3_config.json` — class=`config`, criticality=`normal`, refs=33, action=`KEEP_OR_REVIEW_LATER`

### `__init__.cpython-310.pyc`
- Keep candidate: `core/brokers/__pycache__/__init__.cpython-310.pyc`
  - `core/brokers/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`critical_trading`, refs=1, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/brokers/angel_one/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`critical_trading`, refs=1, action=`DO_NOT_QUARANTINE_WITHOUT_MANUAL_REVIEW`
  - `core/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/data/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/monitoring/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/ultra/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/utils/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/validation/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/ai_model/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/breakout_model/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/entry_exit_engine/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/greeks_engine/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/momentum_model/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/scoring_engine/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/trend_model/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`
  - `core/engine/volatility_model/__pycache__/__init__.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=1, action=`REVIEW_BEFORE_QUARANTINE`

### `ensemble_predictor.cpython-310.pyc`
- Keep candidate: `core/engine/__pycache__/ensemble_predictor.cpython-310.pyc`
  - `core/engine/__pycache__/ensemble_predictor.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=0, action=`QUARANTINE_CANDIDATE_BATCH_1`
  - `src/ml/__pycache__/ensemble_predictor.cpython-310.pyc` — class=`production`, criticality=`normal`, refs=0, action=`QUARANTINE_CANDIDATE_BATCH_1`

### `ensemble_predictor.py`
- Keep candidate: `core/engine/ensemble_predictor.py`
  - `core/engine/ensemble_predictor.py` — class=`production`, criticality=`normal`, refs=52, action=`KEEP_OR_REVIEW_LATER`
  - `src/ml/ensemble_predictor.py` — class=`production`, criticality=`normal`, refs=47, action=`KEEP_OR_REVIEW_LATER`

### `greeks_calculator.py`
- Keep candidate: `dashboard/backend/greeks_calculator.py`
  - `dashboard/backend/greeks_calculator.py` — class=`production`, criticality=`sensitive`, refs=24, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/greeks_engine/greeks_calculator.py` — class=`production`, criticality=`normal`, refs=24, action=`KEEP_OR_REVIEW_LATER`

### `system3_phase331_signal_integrity.py`
- Keep candidate: `system3_phase331_signal_integrity.py`
  - `system3_phase331_signal_integrity.py` — class=`production`, criticality=`normal`, refs=22, action=`KEEP_OR_REVIEW_LATER`
  - `core/engine/system3_phase331_signal_integrity.py` — class=`production`, criticality=`normal`, refs=22, action=`KEEP_OR_REVIEW_LATER`

### `app.py`
- Keep candidate: `dashboard/app.py`
  - `dashboard/app.py` — class=`production`, criticality=`sensitive`, refs=154, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/backend/app.py` — class=`production`, criticality=`sensitive`, refs=154, action=`KEEP_OR_REVIEW_LATER`

### `index.css`
- Keep candidate: `dashboard/frontend/src/index.css`
  - `dashboard/frontend/src/index.css` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/assets/index.css` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`

### `index.html`
- Keep candidate: `dashboard/index.html`
  - `dashboard/index.html` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/index.html` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`
  - `reports/model_benchmark_dashboard/index.html` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`
  - `dashboard/frontend/dist/index.html` — class=`production`, criticality=`sensitive`, refs=130, action=`KEEP_OR_REVIEW_LATER`

### `package-lock.json`
- Keep candidate: `dashboard/frontend/package-lock.json`
  - `dashboard/frontend/package-lock.json` — class=`config`, criticality=`sensitive`, refs=5, action=`KEEP_OR_REVIEW_LATER`
  - `package-lock.json` — class=`config`, criticality=`normal`, refs=5, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/package-lock.json` — class=`config`, criticality=`normal`, refs=5, action=`KEEP_OR_REVIEW_LATER`

### `package.json`
- Keep candidate: `dashboard/frontend/package.json`
  - `dashboard/frontend/package.json` — class=`config`, criticality=`sensitive`, refs=128, action=`KEEP_OR_REVIEW_LATER`
  - `package.json` — class=`config`, criticality=`normal`, refs=128, action=`KEEP_OR_REVIEW_LATER`
  - `desktop_app/package.json` — class=`config`, criticality=`normal`, refs=128, action=`KEEP_OR_REVIEW_LATER`

### `performance_metrics.py`
- Keep candidate: `scripts/performance_metrics.py`
  - `scripts/performance_metrics.py` — class=`production`, criticality=`normal`, refs=62, action=`KEEP_OR_REVIEW_LATER`
  - `src/analytics/performance_metrics.py` — class=`production`, criticality=`normal`, refs=62, action=`KEEP_OR_REVIEW_LATER`

### `start_backend.bat`
- Keep candidate: `start_backend.bat`
  - `start_backend.bat` — class=`production`, criticality=`normal`, refs=45, action=`KEEP_OR_REVIEW_LATER`
  - `scripts/start_backend.bat` — class=`production`, criticality=`normal`, refs=45, action=`KEEP_OR_REVIEW_LATER`

### `start_backend.bat.bak_20260225_005921`
- Keep candidate: `start_backend.bat.bak_20260225_005921`
  - `start_backend.bat.bak_20260225_005921` — class=`production`, criticality=`normal`, refs=6, action=`KEEP_OR_REVIEW_LATER`
  - `scripts/start_backend.bat.bak_20260225_005921` — class=`production`, criticality=`normal`, refs=6, action=`KEEP_OR_REVIEW_LATER`

### `test_phases_261_300.py`
- Keep candidate: `test_phases_261_300.py`
  - `test_phases_261_300.py` — class=`test`, criticality=`normal`, refs=12, action=`KEEP_OR_REVIEW_LATER`
  - `tests/auto/system3_generated_tests/test_phases_261_300.py` — class=`test`, criticality=`normal`, refs=12, action=`KEEP_OR_REVIEW_LATER`

## Next safe action after this PR
Create a separate quarantine PR only for `QUARANTINE_CANDIDATE_BATCH_1` files after human review.
