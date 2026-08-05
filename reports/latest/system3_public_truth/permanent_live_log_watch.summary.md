# Permanent Live Log Watch

Generated: 2026-08-05T06:28:06.935Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **FAIL**
Truth control visible: **true**

## Runtime Log Sources Captured
- Browser console entries: 13
- Page errors: 0
- Request failures: 41
- Network responses: 35

## Dhan Chain Truth
- BLOCKED (required) /api/chain/NIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED (required) /api/chain/BANKNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- PASS (required) /api/chain/FINNIFTY source=dhan priority=dhan_p0_live status=MARKET_OPEN spot=26760.3 contracts=160 blocker=-
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
- PASS Truth Control size=158413
- PASS Genesis Brain size=67034
- PASS E2E Proof size=153551
- PASS Overview size=126310
- PASS Option Chain size=193860
- PASS Signals size=66557
- PASS Paper Trades size=73849
- PASS Positions size=93375
- PASS Broker size=113539
- PASS Performance size=83160
- PASS ML Model size=103150
- PASS Live Gate size=79794

## Infrastructure Blockers
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/market-data:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/market-data:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/market-data:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/health:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/chains:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/trades/today:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/health:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/dhan/status:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/scanner/top_contract_gainers?top_n=5:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/genesis-production-brief:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/autonomous-brain:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/hidden-secrets-lab:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/never-die-monitor:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/hunger-meter:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/data-truth-score:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/health:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/system_health:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/final-message:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/funds:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/holdings:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/positions/live:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/auto_gates:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/NIFTY:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/BANKNIFTY:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/market-data:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/FINNIFTY:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/MIDCPNIFTY:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/SENSEX:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/pnl:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/trades/today:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/paper:net::ERR_ABORTED
- REQUEST_FAILED:https://genesis-system3-web-doq2wplepa-el.a.run.app/api/batch/market-data:net::ERR_ABORTED

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## Optional Data Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2' from origin 'https://genesis-system3-web-doq2wplepa-el.a.run.app' has bee
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2' from origin 'https://genesis-system
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2' from origin 'https://genesis-syst
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2' from origin 'https://genesis-system3-web-doq2wplepa-el.a.run.app' has 
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxPcwhsk.woff2' from origin 'https://genesis-syst
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_BROWSER_NOISE:error Access to font at 'https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2' from origin 'https://genesis-system3-web-doq2wplepa-el.a.run.app' has 
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxDcwg.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPx7cwhsk.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1pL7SUc.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/jetbrainsmono/v24/tDbv2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKwBNntkaToggR7BYRbKPxPcwhsk.woff2:net::ERR_FAILED
- OPTIONAL_REQUEST_FAILED:https://fonts.gstatic.com/s/inter/v20/UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa25L7SUc.woff2:net::ERR_FAILED