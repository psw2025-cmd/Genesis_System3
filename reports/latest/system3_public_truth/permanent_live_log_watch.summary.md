# Permanent Live Log Watch

Generated: 2026-07-10T10:33:50.385Z
Base: https://genesis-system3-backend.onrender.com
Final verdict: **FAIL**
Truth control visible: **false**

## Runtime Log Sources Captured
- Browser console entries: 19
- Page errors: 0
- Request failures: 0
- Network responses: 19

## Dhan Chain Truth
- FAIL /api/chain/NIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/BANKNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/FINNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/MIDCPNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/SENSEX source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN

## API Endpoints
- FAIL 502 /api/auth/status
- FAIL 502 /api/deploy/info
- FAIL 502 /api/health
- FAIL 502 /api/state
- FAIL 502 /api/broker/dhan/status
- FAIL 502 /api/broker/funds
- FAIL 502 /api/broker/holdings
- FAIL 502 /api/broker/positions/live
- FAIL 502 /api/chain/NIFTY
- FAIL 502 /api/chain/BANKNIFTY
- FAIL 502 /api/chain/FINNIFTY
- FAIL 502 /api/chain/MIDCPNIFTY
- FAIL 502 /api/chain/SENSEX
- FAIL 502 /api/gain_rank
- FAIL 502 /api/pnl
- FAIL 502 /api/auto_gates

## Screenshots
- FAIL Truth Control size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- FAIL Genesis Brain size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- FAIL E2E Proof size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- FAIL Overview size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- FAIL Option Chain size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- FAIL Signals size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- FAIL Paper Trades size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- FAIL Positions size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- FAIL Broker size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- FAIL Performance size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- FAIL ML Model size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- FAIL Live Gate size=0 TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()


## Infrastructure Blockers
- AUTH_FAIL:502
- API_FAIL:/api/auth/status:502
- API:/api/auth/status:FORBIDDEN:/mock/i
- API_FAIL:/api/deploy/info:502
- API:/api/deploy/info:FORBIDDEN:/mock/i
- API_FAIL:/api/health:502
- API:/api/health:FORBIDDEN:/mock/i
- API_FAIL:/api/state:502
- API:/api/state:FORBIDDEN:/mock/i
- API_FAIL:/api/broker/dhan/status:502
- API:/api/broker/dhan/status:FORBIDDEN:/mock/i
- API_FAIL:/api/broker/funds:502
- API:/api/broker/funds:FORBIDDEN:/mock/i
- API_FAIL:/api/broker/holdings:502
- API:/api/broker/holdings:FORBIDDEN:/mock/i
- API_FAIL:/api/broker/positions/live:502
- API:/api/broker/positions/live:FORBIDDEN:/mock/i
- API_FAIL:/api/chain/NIFTY:502
- API:/api/chain/NIFTY:FORBIDDEN:/mock/i
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/BANKNIFTY:502
- API:/api/chain/BANKNIFTY:FORBIDDEN:/mock/i
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/FINNIFTY:502
- API:/api/chain/FINNIFTY:FORBIDDEN:/mock/i
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/MIDCPNIFTY:502
- API:/api/chain/MIDCPNIFTY:FORBIDDEN:/mock/i
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/SENSEX:502
- API:/api/chain/SENSEX:FORBIDDEN:/mock/i
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/gain_rank:502
- API:/api/gain_rank:FORBIDDEN:/mock/i
- API_FAIL:/api/pnl:502
- API:/api/pnl:FORBIDDEN:/mock/i
- API_FAIL:/api/auto_gates:502
- API:/api/auto_gates:FORBIDDEN:/mock/i
- UI_TAB_EXCEPTION:Truth Control:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- UI_TAB_EXCEPTION:Genesis Brain:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- UI_TAB_EXCEPTION:E2E Proof:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- UI_TAB_EXCEPTION:Overview:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- UI_TAB_EXCEPTION:Option Chain:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- UI_TAB_EXCEPTION:Signals:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- UI_TAB_EXCEPTION:Paper Trades:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- UI_TAB_EXCEPTION:Positions:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- UI_TAB_EXCEPTION:Broker:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- UI_TAB_EXCEPTION:Performance:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- UI_TAB_EXCEPTION:ML Model:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- UI_TAB_EXCEPTION:Live Gate:TimeoutError: locator.click: Timeout 12000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()

- TRUTH_CONTROL_NOT_VISIBLE
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()
- BROWSER_CONSOLE:error Failed to load resource: the server responded with a status of 502 ()

## Trading Readiness Blockers
- none