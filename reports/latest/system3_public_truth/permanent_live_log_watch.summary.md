# Permanent Live Log Watch

Generated: 2026-07-10T16:35:12.695Z
Base: https://genesis-system3-backend.onrender.com
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **FAIL**
Truth control visible: **true**

## Runtime Log Sources Captured
- Browser console entries: 11
- Page errors: 0
- Request failures: 5
- Network responses: 110

## Dhan Chain Truth
- PASS (required) /api/chain/NIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=24212.8 contracts=160 blocker=-
- PASS (required) /api/chain/BANKNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=58082.7 contracts=160 blocker=-
- PASS (required) /api/chain/FINNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=26824.1 contracts=160 blocker=-
- PASS (required) /api/chain/MIDCPNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=14796 contracts=160 blocker=-
- BLOCKED (optional) /api/chain/SENSEX source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## API Endpoints
- PASS 200  /api/auth/status
- PASS 200  /api/deploy/info
- PASS 200  /api/health
- PASS 200  /api/state
- PASS 200  /api/broker/dhan/status
- PASS 200  /api/broker/funds
- PASS 200  /api/broker/holdings
- PASS 200  /api/broker/positions/live
- PASS 200  /api/chain/NIFTY
- PASS 200  /api/chain/BANKNIFTY
- PASS 200  /api/chain/FINNIFTY
- PASS 200  /api/chain/MIDCPNIFTY
- PASS 200 (optional) /api/chain/SENSEX
- PASS 200  /api/gain_rank
- PASS 200  /api/scanner/top_contract_gainers?top_n=5
- PASS 200  /api/pnl
- PASS 200  /api/auto_gates

## Screenshots
- PASS Truth Control size=171355
- PASS Genesis Brain size=242931
- PASS E2E Proof size=144479
- PASS Overview size=118670
- PASS Option Chain size=192153
- PASS Signals size=80934
- PASS Paper Trades size=120792
- PASS Positions size=61745
- PASS Broker size=108630
- PASS Performance size=61769
- PASS ML Model size=72486
- PASS Live Gate size=102311

## Infrastructure Blockers
- BROWSER_CONSOLE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been block
- BROWSER_CONSOLE:error Failed to load resource: net::ERR_FAILED
- BROWSER_CONSOLE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2' from origin 'https://genesis-system
- BROWSER_CONSOLE:error Failed to load resource: net::ERR_FAILED
- BROWSER_CONSOLE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2' from origin 'https://genesis-syst
- BROWSER_CONSOLE:error Failed to load resource: net::ERR_FAILED
- BROWSER_CONSOLE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been bl
- BROWSER_CONSOLE:error Failed to load resource: net::ERR_FAILED
- BROWSER_CONSOLE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been bl
- BROWSER_CONSOLE:error Failed to load resource: net::ERR_FAILED
- REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2:net::ERR_FAILED
- REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2:net::ERR_FAILED
- REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2:net::ERR_FAILED
- REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2:net::ERR_FAILED
- REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2:net::ERR_FAILED

## Trading Readiness Blockers
- none

## Optional Data Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS