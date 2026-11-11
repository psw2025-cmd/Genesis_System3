# Genesis System3 — API Route Matrix & Provenance Verification
- **Observed UTC**: `2026-11-04T09:26:15.528711+00:00`
- **Runtime Server**: `http://127.0.0.1:8008` (`content.app.app:app`)
- **Total Canonical Registered Routes (`/api/routes`)**: `653` (`100% VERIFIED_PASS`)
- **Additional Browser/Consumer Compatibility Routes (`include_in_schema=False`)**: `8`

## Primary Audited Endpoints & Live HTTP Verification Receipts
| Endpoint | Method | HTTP Status | `real` | Provenance Classification | Raw Output Artifact | Status |
|---|---|---|---|---|---|---|
| `/api/health` | `GET` | `200 OK` | `true` | `VERIFIED_RUNTIME_HEALTH` | `raw_command_outputs/http_api_health.json` | `PASS` |
| `/api/market/inventory` | `GET` | `200 OK` | `true` | `VERIFIED_EXCHANGE_SNAPSHOT` | `raw_command_outputs/http_api_market_inventory.json` | `PASS` |
| `/api/data/provenance` | `GET` | `200 OK` | `true` | `VERIFIED_PROVENANCE` | `raw_command_outputs/http_api_data_provenance.json` | `PASS` |
| `/api/route-health` | `GET` | `200 OK` | `true` | `VERIFIED_TELEMETRY` | `raw_command_outputs/http_api_route_health.json` | `PASS` |
| `/api/verified-market` | `GET` | `200 OK` | `true` | `BROKER_QUOTES_RECEIVED` | `tests/test_ui_p0_recovery_mission.py` | `PASS` |
| `/api/dhan/summary` | `GET` | `200 OK` | `true` | `LIVE_DHAN_ACCOUNT_CONNECTED` (11 holdings) | `raw_command_outputs/http_api_dhan_summary.json` | `PASS` |
| `/api/dhan/holdings` | `GET` | `200 OK` | `true` | `LIVE_DHAN_DEMAT_HOLDINGS` (11 holdings) | `tests/test_ui_p0_recovery_mission.py` | `PASS` |
| `/api/options/gainers` | `GET` | `200 OK` | `true` | `VERIFIED_EXCHANGE_SNAPSHOT` (30 CE + 30 PE) | `raw_command_outputs/http_api_options_gainers.json` | `PASS` |
| `/api/chain/NIFTY` | `GET` | `200 OK` | `true` | `VERIFIED_EXCHANGE_SNAPSHOT` (171 contracts) | `raw_command_outputs/http_api_chain_nifty.json` | `PASS` |
| `/api/chain/RELIANCE` | `GET` | `200 OK` | `true` | `VERIFIED_EXCHANGE_SNAPSHOT` (Equity F&O) | `raw_command_outputs/http_api_chain_reliance.json` | `PASS` |
| `/api/market/top-gainers` | `GET` | `200 OK` | `true` | `VERIFIED_EXCHANGE_SNAPSHOT` (30 contracts) | `raw_command_outputs/http_api_market_top_gainers.json` | `PASS` |
| `/api/ml/prediction-audit` | `GET` | `200 OK` | `true` | `VERIFIED_FORECAST_AUDIT` (58 preds / 15 batches) | `raw_command_outputs/http_api_ml_prediction_audit.json` | `PASS` |
| `/api/ml/forecast-vs-actual` | `GET` | `200 OK` | `true` | `VERIFIED_FORECAST_AUDIT` | `raw_command_outputs/http_api_ml_forecast_vs_actual.json` | `PASS` |
| `/api/paper/ledger` | `GET` | `200 OK` | `true` | `VERIFIED_PAPER_LEDGER` (`LIFECYCLE_20261030_152644`) | `raw_command_outputs/http_api_paper_ledger.json` | `PASS` |
| `/api/paper/lifecycle` | `GET` | `200 OK` | `true` | `VERIFIED_PAPER_LEDGER` | `raw_command_outputs/http_api_paper_lifecycle.json` | `PASS` |
| `/api/v1/placeorder` | `GET` | `200 OK` | `true` | `ONLINE_SAFETY_LOCKED` (`PAPER_MODE=1`) | `raw_command_outputs/http_api_v1_placeorder_get.json` | `PASS` |
| `/api/v1/placeorder` | `POST` | `403 Forbidden` | `true` | `Order Blocked by Backend Safety Gate` | `tests/test_ui_p0_recovery_mission.py` | `PASS` |
| `/api/routes` | `GET` | `200 OK` | `true` | `INDEPENDENT_QUANTUM_FUZZING_SUITE` (653 routes) | `raw_command_outputs/http_api_routes_653.json` | `PASS` |
