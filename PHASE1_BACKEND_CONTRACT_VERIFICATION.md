# PHASE 1: Backend Contract Verification

## Endpoint Contract (From production_grade_zero_errors_validation.py)

### Required Endpoints (MUST return HTTP 200)

| Endpoint | Path | Expected Status | Required JSON Keys |
|----------|------|----------------|-------------------|
| Health | `/api/health` | 200 | `status`, `mode`, `broker_status`, `market_status` |
| State | `/api/state` | 200 | `mode`, `broker`, `market`, `data_source`, `cycle_count` |
| Learning Insights | `/api/learning/insights` | 200 | `status`, `win_rate`, `total_trades`, `updated_at` |
| Learning Status | `/api/learning/status` | 200 | `status`, `last_update`, `total_cycles`, `updated_at` |
| Forensic Report | `/api/forensic/report` | 200 | `status`, `timestamp`, `signal_accuracy`, `data_integrity`, `performance_metrics` |
| Validation Status | `/api/validation/status` | 200 | `status`, `results`, `updated_at` |
| Chain NIFTY | `/api/chain/NIFTY` | 200 | `underlying`, `spot`, `contracts`, `total_contracts`, `data_source` |
| Chain BANKNIFTY | `/api/chain/BANKNIFTY` | 200 | Same as NIFTY |
| Chain FINNIFTY | `/api/chain/FINNIFTY` | 200 | Same as NIFTY |
| Signal Top | `/api/signal/top` | 200 | `action`, `underlying`, `reason`, `data_source` |
| Positions | `/api/positions` | 200 | `positions`, `open_count` |
| PnL | `/api/pnl` | 200 | `total_pnl`, `daily_pnl`, `summary` |
| QC | `/api/qc` | 200 | `status`, `failures` |
| Performance | `/api/perf` | 200 | `history`, `summary` |

## Contract Rules

1. **ALL endpoints MUST return HTTP 200** (never 404, never 500)
2. **ALL responses MUST be valid JSON**
3. **If no data exists → return empty-but-valid schema**
4. **If error occurs → return HTTP 200 with `"status": "error"` in JSON**

## Status

✅ All 14 endpoints implemented and verified
✅ All return HTTP 200
✅ All have proper error handling
✅ All return valid JSON even when empty
