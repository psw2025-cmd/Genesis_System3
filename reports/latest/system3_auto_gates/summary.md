# System3 Auto Gates

Generated: `2026-09-05T20:10:34.151180Z`
Gates passing: **5/7**
Trade ready: **False**
Analyzer ready: **True**

## Gates

| Gate | Pass | Blocker |
|---|---|---|
| `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` | `True` | `-` |
| `POSITIVE_NET_EXPECTANCY_AFTER_COSTS` | `False` | `PROFIT_BLOCKER` |
| `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` | `False` | `SYS3-BLK-008` |
| `WEBSOCKET_TICK_HEALTH_PROVEN` | `True` | `-` |
| `MODEL_ACCURACY_REPORT_PRESENT` | `True` | `-` |
| `OPTION_STRIKE_VISIBILITY_PROVEN` | `True` | `-` |
| `EQUITY_FO_ELIGIBILITY_PROVEN` | `True` | `-` |

## Open blockers

- `PROFIT_BLOCKER`
- `SYS3-BLK-008`

## Auto actions

- Run scripts/system3_friction_expectancy_proof.py after paper trades accumulate
- Run scripts/paper_lifecycle_proof.py during market hours with broker connected
