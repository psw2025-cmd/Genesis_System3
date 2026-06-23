# System3 Truth Bridge Guide

## Purpose

This is the single GitHub-readable proof bridge for System3 dashboard truth.

It exists because some tools may not directly open the Render dashboard/API, but they can read GitHub files. The bridge fetches live public API endpoints, combines them with committed proof files, and writes one report.

## Files

- Script: `scripts/system3_truth_bridge.py`
- GitHub Action: `.github/workflows/system3-truth-bridge.yml`
- JSON report: `reports/latest/system3_truth_bridge/latest.json`
- Human report: `reports/latest/system3_truth_bridge/summary.md`

## What it reads

Live public endpoints:

- `/api/state`
- `/api/health`
- `/api/broker/status`
- `/api/debug/state_source`
- `/api/underlyings`
- `/api/qc`
- `/api/chain/NIFTY`
- `/api/chain/BANKNIFTY`
- `/api/chain/FINNIFTY`
- `/api/chain/MIDCPNIFTY`

Committed proof files:

- `reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json`
- `reports/latest/proof_status_matrix/proof_status_matrix.json`
- `reports/latest/dashboard_truth_proof/summary.json`
- `reports/latest/fresh_data_automation_proof/summary.json`
- `reports/latest/analyzer_paper_lifecycle_proof/summary.json`
- `reports/latest/analyzer_paper_lifecycle_proof/LIFECYCLE_20260614_142129.json`
- `reports/latest/model_training_load_proof/summary.json`
- `reports/latest/live_current_issue_check/issues.json`

## Important issue codes

| Code | Meaning |
|---|---|
| `LIVE_ENDPOINT_FAILED` | One public API endpoint failed to fetch. |
| `BROKER_STATE_HEALTH_MISMATCH` | `/api/state` and `/api/health` disagree about broker status. |
| `BROKER_DIRECT_STATE_MISMATCH` | `/api/broker/status` and `/api/state` disagree. |
| `FALSE_BROKER_DISCONNECTED` | Broker connected but disconnect alert is active. |
| `BAD_CLOSED_MARKET_DATA_SOURCE` | Market closed + broker connected is labelled synthetic. |
| `DATA_SOURCE_MISMATCH` | `/api/state` and `/api/health` data source labels disagree. |
| `LIVE_SAFETY_BREACH` | Live mode/order placement appears enabled. Critical. |
| `CHAIN_NOT_READY_WITH_BROKER` | Option chain says NOT_READY while broker is connected. |
| `ZERO_CHAIN_CONTRACTS_MARKET_OPEN` | Market open but option chain has zero contracts. |
| `TRADE_READY_FALSE` | Full trading pipeline is not trade-ready. |
| `PROOF_MATRIX_INCOMPLETE` | Proof matrix still says readiness incomplete. |
| `FRESH_BROKER_DATA_NOT_PROVEN` | Broker live-data freshness proof missing. |
| `REAL_PAPER_LIFECYCLE_NOT_PROVEN` | Real market paper lifecycle proof missing. |
| `RAW_LIFECYCLE_IS_DRY_RUN` | Raw lifecycle file is a dry-run/simulation. |
| `MODEL_PROMOTION_BLOCKED` | Model promotion blocked by policy/proof. |

## How to run manually in GitHub

1. Open GitHub repo.
2. Go to **Actions**.
3. Select **System3 Truth Bridge**.
4. Click **Run workflow**.
5. Wait until it completes.
6. Open `reports/latest/system3_truth_bridge/summary.md`.
7. Open `reports/latest/system3_truth_bridge/latest.json` for full machine proof.

## Safety

This bridge is read-only. It does not use broker secrets, does not place orders, and does not enable live trading.

Live trading must remain disabled until all proof gates pass and human approval is explicitly given.
