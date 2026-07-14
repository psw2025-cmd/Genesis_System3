# Permanent Live Log Watch

Generated: 2026-07-14T08:19:41.727Z
Base: https://genesis-system3-backend.onrender.com
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **FAIL**
Truth control visible: **true**

## Runtime Log Sources Captured
- Browser console entries: 11
- Page errors: 0
- Request failures: 5
- Network responses: 82

## Dhan Chain Truth
- BLOCKED (required) /api/chain/NIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED (required) /api/chain/BANKNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED (required) /api/chain/FINNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED (required) /api/chain/MIDCPNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
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
- PASS Truth Control size=199272
- PASS Genesis Brain size=282771
- PASS E2E Proof size=190600
- PASS Overview size=155665
- PASS Option Chain size=114380
- PASS Signals size=123890
- PASS Paper Trades size=169489
- PASS Positions size=107914
- PASS Broker size=151530
- PASS Performance size=107780
- PASS ML Model size=134184
- PASS Live Gate size=134477

## Infrastructure Blockers
- UI:Paper Trades:FORBIDDEN:/synthetic/i
- UI:Paper Trades:FORBIDDEN:/fake/i
- UI:Paper Trades:FORBIDDEN:/mock/i

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## Optional Data Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2' from origin 'https://genesis-system
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been block
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2' from origin 'https://genesis-syst
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been bl
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2' from origin 'https://genesis-system3-backend.onrender.com' has been bl
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2:net::ERR_FAILED