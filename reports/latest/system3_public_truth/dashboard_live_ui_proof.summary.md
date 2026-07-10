# Dashboard Live UI Proof

Generated: 2026-07-10T09:08:22.380Z
Base: https://genesis-system3-backend.onrender.com
Final verdict: **FAIL**
Trader readiness panel visible: **false**
Truth control visible: **false**

## Chain Truth
- FAIL /api/chain/NIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/BANKNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/FINNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/MIDCPNIFTY source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN
- FAIL /api/chain/SENSEX source=null priority=null status=null spot=0 contracts=0 blocker=NOT_REAL_DHAN_CHAIN

## API
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
- FAIL 502 /api/trades/today
- FAIL 502 /api/auto_gates

## UI Screenshots
- FAIL Truth Control - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- FAIL Genesis Brain - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- FAIL E2E Proof - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- FAIL Overview - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- FAIL Option Chain - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- FAIL Signals - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- FAIL Paper Trades - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- FAIL Positions - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- FAIL Broker - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- FAIL Performance - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- FAIL ML Model - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- FAIL Live Gate - TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()


## Infrastructure Blockers
- AUTH_FAIL:502
- API_FAIL:/api/auth/status:502
- API_FAIL:/api/deploy/info:502
- API_FAIL:/api/health:502
- API_FAIL:/api/state:502
- API_FAIL:/api/broker/dhan/status:502
- API_FAIL:/api/broker/funds:502
- API_FAIL:/api/broker/holdings:502
- API_FAIL:/api/broker/positions/live:502
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/NIFTY:502
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/BANKNIFTY:502
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/FINNIFTY:502
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/MIDCPNIFTY:502
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NOT_REAL_DHAN_CHAIN
- API_FAIL:/api/chain/SENSEX:502
- API_FAIL:/api/gain_rank:502
- API_FAIL:/api/pnl:502
- API_FAIL:/api/trades/today:502
- API_FAIL:/api/auto_gates:502
- UI_EXCEPTION:Truth Control:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- UI_EXCEPTION:Genesis Brain:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- UI_EXCEPTION:E2E Proof:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- UI_EXCEPTION:Overview:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- UI_EXCEPTION:Option Chain:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- UI_EXCEPTION:Signals:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- UI_EXCEPTION:Paper Trades:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- UI_EXCEPTION:Positions:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- UI_EXCEPTION:Broker:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- UI_EXCEPTION:Performance:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- UI_EXCEPTION:ML Model:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- UI_EXCEPTION:Live Gate:TimeoutError: locator.click: Timeout 10000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()

- TRADER_READINESS_PANEL_NOT_VISIBLE
- TRUTH_CONTROL_NOT_VISIBLE

## Trading Readiness Blockers
- none