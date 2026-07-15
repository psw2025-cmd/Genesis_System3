# System3 Safe Repair Runner

Generated UTC: `2026-07-15T10:43:17.279487Z`
Status: **BLOCKED**
API base: `https://genesis-system3-backend.onrender.com`

## Safety

- live_trading_enabled: `false`
- system_ready_for_live_trading: `false`
- order_routes_called: `false`
- secrets_printed: `false`

## Gate summary

- Gates: `1/7`
- Trade ready: `False`
- Analyzer ready: `False`
- Open blockers: `['PROFIT_BLOCKER', 'SYS3-BLK-003', 'SYS3-BLK-004', 'SYS3-BLK-005', 'SYS3-BLK-008', 'TICK_HEALTH_BLOCKER']`
- Technical gates still required: `['ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS', 'POSITIVE_NET_EXPECTANCY_AFTER_COSTS', 'REAL_PAPER_LIFECYCLE_MARKET_DAY_PROOF', 'WEBSOCKET_TICK_HEALTH_PROVEN']`

## Proof summary

- Visible UI status: `BLOCKED`
- Visible issue count: `0`
- GitHub/Render status: `BLOCKED`
- Autopilot status: `BLOCKED`

## Blocked reasons

- [ ] technical trade_ready gates are not all PASS
- [ ] automated dashboard visual proof is not PASS
- [ ] GitHub plus Render failure tracker is not PASS
- [ ] autopilot proof board is not PASS

## Endpoints after run

| Endpoint | OK | Status |
|---|---:|---:|
| `/api/health` | `True` | `200` |
| `/api/state` | `True` | `200` |
| `/api/status` | `True` | `200` |
| `/api/broker/status` | `True` | `200` |
| `/api/broker/dhan/status` | `True` | `200` |
| `/api/broker/funds` | `True` | `200` |
| `/api/broker/holdings` | `True` | `200` |
| `/api/broker/positions/live` | `True` | `200` |
| `/api/approval/status` | `True` | `200` |
| `/api/kill-switch/status` | `True` | `200` |

## Commands

| Command | PASS |
|---|---:|
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/system3_gate_evaluator.py --sync-gates` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python tools/system3_auto_coordinator.py --full --api-base https://genesis-system3-backend.onrender.com` | `False` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/system3_model_accuracy_tracker.py --api-base https://genesis-system3-backend.onrender.com` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/system3_option_visibility_audit.py --api-base https://genesis-system3-backend.onrender.com` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/system3_friction_expectancy_proof.py` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/websocket_tick_health_proof.py` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python scripts/system3_blocker_finder.py --api-base https://genesis-system3-backend.onrender.com` | `True` |
| `/opt/hostedtoolcache/Python/3.11.15/x64/bin/python tools/system3_github_render_failure_tracker.py` | `True` |
