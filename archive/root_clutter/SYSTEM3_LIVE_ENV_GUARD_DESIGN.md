# System3 Live Trading Environment Guard

**Status:** Implemented (DRY-RUN enforced). Live trading remains blocked until an explicit env variable is enabled and configs are flipped.

## Guard Behavior
- Environment variable `SYSTEM3_LIVE_TRADING_ALLOWED` controls permission to place real orders.
- If the variable is **missing**, empty, "0", "false", or "False": live trading is **blocked** even if config flags are flipped.
- When set to a truthy value (e.g., "1", "true"), live trading can proceed **only if** existing safety flags (`LIVE_TRADING_ENABLED`, `USE_LIVE_EXECUTION_ENGINE`, automation `auto_execute_trades`) are also enabled. This keeps a dual-key requirement.

## Integration Points
- Core live order paths (broker invocation) must check the env guard before any live order placement.
- DRY-RUN, paper trading, and virtual PnL flows are **not** affected.

## How to Safely Enable Live Trading (future)
1) Set environment variable: `SYSTEM3_LIVE_TRADING_ALLOWED=1` (or `true`).
2) Flip config flags to True: `LIVE_TRADING_ENABLED`, `USE_LIVE_EXECUTION_ENGINE`, and automation `auto_execute_trades` as required.
3) Run preflight and watchdog; verify guard logs show "LIVE TRADING ALLOWED".
4) Proceed only after manual review and approvals.

## Proof Artifacts
- Guard code added in live trading path (see broker execution guard).
- DRY-RUN remains enforced; no change to safety defaults.