# Genesis System3 — Executed Command Index (`Section 5` & `Section 7`)
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`
- **Git HEAD**: `d5ad4d0c7a9dc3c26ad13666fb791bb9e2a13a82`

| Command ID | Command Executed | Exit Code | Raw Output Artifact |
|---|---|---:|---|
| `CMD-001` | `git rev-parse HEAD` | `0` | `raw_command_outputs/git_identity.stdout.txt` |
| `CMD-002` | `git branch --show-current` | `0` | `raw_command_outputs/git_branch.stdout.txt` |
| `CMD-003` | `git status --short` | `0` | `raw_command_outputs/git_status_short.stdout.txt` |
| `CMD-004` | `.venv\Scripts\python.exe -m pytest -q tests/test_order_zero_calls.py tests/test_dhan_*.py ...` | `0` | `raw_command_outputs/pytest_dhan_and_safety.stdout.txt` |
| `CMD-005` | `.venv\Scripts\python.exe tests/test_ui_p0_recovery_mission.py` (15 tests) | `0` | `raw_command_outputs/unittest_ui_p0_recovery_15_tests.stderr.txt` |
| `CMD-006` | `.venv\Scripts\python.exe tests/test_ui_production_e2e.py` (Playwright Chromium E2E) | `0` | `.agy-proof/receipt.json` |
| `CMD-007` | `GET http://127.0.0.1:8008/api/health` | `0` | `raw_command_outputs/http_api_health.json` |
| `CMD-008` | `GET http://127.0.0.1:8008/api/market/inventory` | `0` | `raw_command_outputs/http_api_market_inventory.json` |
| `CMD-009` | `GET http://127.0.0.1:8008/api/data/provenance` | `0` | `raw_command_outputs/http_api_data_provenance.json` |
| `CMD-010` | `GET http://127.0.0.1:8008/api/ml/prediction-audit` | `0` | `raw_command_outputs/http_api_ml_prediction_audit.json` |
| `CMD-011` | `GET http://127.0.0.1:8008/api/paper/ledger` | `0` | `raw_command_outputs/http_api_paper_ledger.json` |
| `CMD-012` | `GET http://127.0.0.1:8008/api/chain/NIFTY` | `0` | `raw_command_outputs/http_api_chain_nifty.json` |
| `CMD-013` | `GET http://127.0.0.1:8008/api/market/top-gainers` | `0` | `raw_command_outputs/http_api_market_top_gainers.json` |
| `CMD-014` | `GET http://127.0.0.1:8008/api/dhan/summary` | `0` | `raw_command_outputs/http_api_dhan_summary.json` |
