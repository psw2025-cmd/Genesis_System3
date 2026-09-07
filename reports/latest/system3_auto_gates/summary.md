# System3 Auto Gates

Generated: `2026-09-07T18:14:53.437258Z`
Gates passing: **5/7**
Trade ready: **False**
Analyzer ready: **True**

## Gates

| Gate | Pass | Blocker |
|---|---|---|
| `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` | `False` | `SYS3-BLK-005` |
| `POSITIVE_NET_EXPECTANCY_AFTER_COSTS` | `False` | `PROFIT_BLOCKER` |
| `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` | `True` | `-` |
| `WEBSOCKET_TICK_HEALTH_PROVEN` | `True` | `-` |
| `MODEL_ACCURACY_REPORT_PRESENT` | `True` | `-` |
| `OPTION_STRIKE_VISIBILITY_PROVEN` | `True` | `-` |
| `EQUITY_FO_ELIGIBILITY_PROVEN` | `True` | `-` |

## Open blockers

- `PROFIT_BLOCKER`
- `SYS3-BLK-005`

## Auto actions

- Run daily_gain_validate at 15:35 IST weekdays; auto_retrain if rho<0.40 x3 days
- Run scripts/system3_friction_expectancy_proof.py after paper trades accumulate
