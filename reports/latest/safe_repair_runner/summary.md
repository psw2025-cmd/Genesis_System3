# System3 Safe Repair Runner

Generated UTC: `2026-07-24T03:53:43.830281Z`
Status: **BLOCKED**
API base: `http://127.0.0.1:8000`

## Safety

- live_trading_enabled: `false`
- system_ready_for_live_trading: `false`
- order_routes_called: `false`
- secrets_printed: `false`

## Gate summary

- Gates: `3/7`
- Trade ready: `False`
- Analyzer ready: `False`
- Open blockers: `['PROFIT_BLOCKER', 'SYS3-BLK-003', 'SYS3-BLK-005', 'TICK_HEALTH_BLOCKER']`
- Technical gates still required: `['ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS', 'POSITIVE_NET_EXPECTANCY_AFTER_COSTS', 'WEBSOCKET_TICK_HEALTH_PROVEN']`

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
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/system3_gate_evaluator.py --sync-gates` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe tools/system3_auto_coordinator.py --full --api-base http://127.0.0.1:8000` | `False` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/system3_model_accuracy_tracker.py --api-base http://127.0.0.1:8000` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/system3_option_visibility_audit.py --api-base http://127.0.0.1:8000` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/system3_friction_expectancy_proof.py` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/websocket_tick_health_proof.py` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe scripts/system3_blocker_finder.py --api-base http://127.0.0.1:8000` | `True` |
| `C:\System3\Genesis_System3\venv\Scripts\python.exe tools/system3_github_render_failure_tracker.py` | `True` |
