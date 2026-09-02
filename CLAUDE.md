# Genesis System3 Claude Instructions

Genesis System3 is an Indian equity/options paper-trading dashboard. It runs on the local laptop from GitHub source. GCP is out of scope.

## Non-negotiable safety rules

- Live trading is disabled. Never set `LIVE_TRADING_ENABLED`, `SYSTEM3_LIVE_TRADING_ALLOWED`, or `AUTO_EXECUTE_TRADES` to anything but `"0"`. Never add code that places a broker order.
- Never invent numbers. No hardcoded prices, P&L, win rates, Sharpe ratios, sample trades, fundamentals, or catalysts are allowed anywhere in `dashboard/backend/`. If real data is unavailable, the endpoint must return an explicit empty state: `{"status": "NO_DATA", "reason": "<specific>"}`. A fabricated metric in a trading dashboard is the most severe defect class in this repository; this exact pattern was already found and removed once.
- `SYSTEM3_REAL_ONLY=1` is the default. Synthetic data may be served only on a path labelled `SIMULATION_ONLY` in the payload and visibly labelled in the UI.
- Never commit `dashboard/frontend/dist`.
- Fail closed, never fail open. `except: pass` is banned. Every handler must log with a code and set an explicit degraded status. If market state cannot be determined, return `MARKET_STATE_UNKNOWN`; never fall through to synthetic data.
- Before claiming any task complete, run the verification command specified by the task and paste its real output. Never report success from reasoning alone.
