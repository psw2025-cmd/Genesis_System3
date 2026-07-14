# Permanent Live Log Watch

Generated: 2026-07-14T04:03:15.558Z
Base: https://genesis-system3-backend.onrender.com
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **FAIL**
Truth control visible: **false**

## Runtime Log Sources Captured
- Browser console entries: 4
- Page errors: 0
- Request failures: 0
- Network responses: 22

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
- FAIL Truth Control size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- FAIL Genesis Brain size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- FAIL E2E Proof size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- FAIL Overview size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- FAIL Option Chain size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- FAIL Signals size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- FAIL Paper Trades size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- FAIL Positions size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- FAIL Broker size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- FAIL Performance size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- FAIL ML Model size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- FAIL Live Gate size=0 TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()


## Infrastructure Blockers
- UI_TAB_EXCEPTION:Truth Control:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- UI_TAB_EXCEPTION:Genesis Brain:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- UI_TAB_EXCEPTION:E2E Proof:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- UI_TAB_EXCEPTION:Overview:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- UI_TAB_EXCEPTION:Option Chain:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- UI_TAB_EXCEPTION:Signals:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- UI_TAB_EXCEPTION:Paper Trades:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- UI_TAB_EXCEPTION:Positions:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- UI_TAB_EXCEPTION:Broker:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- UI_TAB_EXCEPTION:Performance:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- UI_TAB_EXCEPTION:ML Model:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- UI_TAB_EXCEPTION:Live Gate:TimeoutError: locator.click: Timeout 25000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()

- TRUTH_CONTROL_NOT_VISIBLE

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## Optional Data Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: the server responded with a status of 502 ()
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: the server responded with a status of 502 ()
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: the server responded with a status of 502 ()
- TRANSIENT_BROWSER_NOISE_AFTER_API_PASS:error Failed to load resource: the server responded with a status of 502 ()