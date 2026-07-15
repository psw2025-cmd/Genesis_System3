# System3 Auto Gates

Generated: `2026-07-15T01:42:07.118271Z`
Gates passing: **1/7**
Trade ready: **False**
Analyzer ready: **False**

## Gates

| Gate | Pass | Blocker |
|---|---|---|
| `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` | `False` | `SYS3-BLK-005` |
| `POSITIVE_NET_EXPECTANCY_AFTER_COSTS` | `False` | `PROFIT_BLOCKER` |
| `REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF` | `False` | `SYS3-BLK-008` |
| `WEBSOCKET_TICK_HEALTH_PROVEN` | `False` | `TICK_HEALTH_BLOCKER` |
| `MODEL_ACCURACY_REPORT_PRESENT` | `True` | `-` |
| `OPTION_STRIKE_VISIBILITY_PROVEN` | `False` | `SYS3-BLK-003` |
| `EQUITY_FO_ELIGIBILITY_PROVEN` | `False` | `SYS3-BLK-004` |

## Open blockers

- `PROFIT_BLOCKER`
- `SYS3-BLK-003`
- `SYS3-BLK-004`
- `SYS3-BLK-005`
- `SYS3-BLK-008`
- `TICK_HEALTH_BLOCKER`

## Auto actions

- Run daily_gain_validate at 15:35 IST weekdays; auto_retrain if rho<0.40 x3 days
- Run scripts/system3_friction_expectancy_proof.py after paper trades accumulate
- Run scripts/paper_lifecycle_proof.py during market hours with broker connected
- REST poll ≤10s counts for analyzer; WebSocket stream for live execution
- Run scripts/system3_option_visibility_audit.py
- Verify security_id_list.csv OPTSTK universe loads
