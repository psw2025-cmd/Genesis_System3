# Genesis System3

Genesis System3 is a local-laptop-authoritative, proof-first market-analysis and PAPER trading system. It is not authorized for real orders.

## Authority

- Code/configuration authority: GitHub `psw2025-cmd/Genesis_System3` current `main`.
- Execution/runtime authority: authorized Windows laptop checkout `C:\Genesis_System3_Clean`.
- Dashboard: `http://127.0.0.1:8000/ui` using the port defined by current-main configuration.
- Coordination/status bus: GitHub Issue #188.
- Broker authority: Dhan through the current-main approved local secure-secret lifecycle.

## Agent start here

Every agent must start fresh from current remote `main`, Issue #188, active PR ownership, and fresh evidence from the currently running authorized laptop instance. Stored reports are historical context until revalidated.

## Acceptance rule

Current health/readiness requires exact-main laptop provenance plus fresh same-session backend/UI, broker metadata without secret values, NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY source/freshness/contracts, scheduler/background-worker state, local DB/state consistency, logs/alerts, and semantic verification of all 22 canonical UI tabs.

## Local startup

```powershell
.\.venv\Scripts\python.exe -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
```

## Safety defaults

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- No real order placement, modification, cancellation, or square-off
- No secret/token/PIN/TOTP/private-key exposure
