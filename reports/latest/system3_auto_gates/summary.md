# System3 Auto Gates

Generated: `2026-10-31T08:31:10.488994Z`
Gates passing: **6/7**
Trade ready: **False**
Analyzer ready: **True**

## Gates

| Gate | Pass | Blocker |
|---|---|---|
| `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` | `True` | `-` |
| `POSITIVE_NET_EXPECTANCY_AFTER_COSTS` | `True` | `-` |
| `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` | `True` | `-` |
| `WEBSOCKET_TICK_HEALTH_PROVEN` | `False` | `TICK_HEALTH_BLOCKER` |
| `MODEL_ACCURACY_REPORT_PRESENT` | `True` | `-` |
| `OPTION_STRIKE_VISIBILITY_PROVEN` | `True` | `-` |
| `EQUITY_FO_ELIGIBILITY_PROVEN` | `True` | `-` |

## Open blockers

- `TICK_HEALTH_BLOCKER`

## Auto actions

- REST poll â‰¤10s counts for analyzer; WebSocket stream for live execution
