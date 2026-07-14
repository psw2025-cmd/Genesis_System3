# System3 Production Viability Bridge

Generated UTC: `2026-07-14T21:11:19.941301+00:00`

## Summary

| Field | Value |
|---|---|
| `production_live_ready` | `False` |
| `paper_analyzer_allowed` | `True` |
| `strategy_quarantined_for_live` | `True` |
| `highest_severity` | `CRITICAL` |
| `blocker_count` | `10` |
| `warning_count` | `3` |
| `severity_counts` | `{'CRITICAL': 3, 'HIGH': 7, 'MEDIUM': 3}` |

## Blockers

| Severity | Code | Message | Action |
|---|---|---|---|
| CRITICAL | `TRADE_READY_FALSE` | Full pipeline readiness is false. | Keep live disabled; clear pipeline blockers. |
| CRITICAL | `REAL_MARKET_PAPER_LIFECYCLE_MISSING` | Real market paper lifecycle is not proven. | Run market-session analyzer paper lifecycle proof. |
| CRITICAL | `RAW_LIFECYCLE_DRY_RUN` | Raw lifecycle proof is simulation/dry-run. | Do not mark production ready from dry-run proof. |
| HIGH | `FRESH_BROKER_DATA_NOT_PROVEN` | Fresh broker live data proof is missing. | Run secure runtime broker freshness proof. |
| HIGH | `MODEL_PROMOTION_BLOCKED` | Model promotion is blocked. | Require policy + validation proof before promotion. |
| HIGH | `WEBSOCKET_TICK_HEALTH_NOT_PROVEN` | WebSocket tick health is not proven. | Implement/prove tick stream, last tick age, reconnect count and REST fallback state. |
| HIGH | `FRICTION_EXPECTANCY_NOT_PROVEN_POSITIVE` | Positive expectancy after brokerage, charges, spread and slippage is not proven. | Generate costed expectancy report from paper/live-like trade ledger. |
| HIGH | `EXECUTION_QUALITY_NOT_PROVEN` | Execution quality/slippage/spread proof is missing. | Generate entry/exit delay, spread paid and slippage proof. |
| HIGH | `OPTION_CHAIN_INTEGRITY_NOT_PROVEN` | Spot/chain/Greeks synchronization proof is missing. | Prove spot, option chain and Greeks timestamps are synchronized before signals. |
| HIGH | `MODEL_TO_TRADE_GAP_NOT_PROVEN` | Prediction hit rate is not proven to translate into net trade profitability. | Compare forecast hit rate vs trade win rate and net expectancy. |

## Warnings

| Severity | Code | Message | Action |
|---|---|---|---|
| MEDIUM | `BROWSER_TRUTH_NOT_PROVEN` | Browser screenshot truth is not proven. | Run browser screenshot proof. |
| MEDIUM | `API_DB_REPORT_RECON_NOT_PROVEN` | API/DB/report reconciliation is not proven. | Run dashboard truth reconciliation. |
| MEDIUM | `REFRESH_INTERVAL_UNKNOWN` | Refresh interval is not visible in live proof. | Expose refresh/tick latency in truth bridge. |
