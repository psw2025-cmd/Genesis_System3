# Dashboard Live UI Proof

Generated: 2026-07-10T12:48:05.698Z
Base: https://genesis-system3-backend.onrender.com
Required symbols: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY
Optional symbols: SENSEX
Final verdict: **FAIL**
Trader readiness panel visible: **false**
Truth control visible: **false**

## Chain Truth
- FAIL (required) /api/chain/NIFTY source=null priority=null status=success spot=0 contracts=0 blocker=success
- FAIL (required) /api/chain/BANKNIFTY source=null priority=null status=success spot=0 contracts=0 blocker=success
- FAIL (required) /api/chain/FINNIFTY source=null priority=null status=success spot=0 contracts=0 blocker=success
- FAIL (required) /api/chain/MIDCPNIFTY source=null priority=null status=success spot=0 contracts=0 blocker=success
- FAIL (optional) /api/chain/SENSEX source=null priority=null status=success spot=0 contracts=0 blocker=success

## API
- FAIL 429  /api/auth/status
- FAIL 429  /api/deploy/info
- PASS 200  /api/health
- FAIL 429  /api/state
- FAIL 429  /api/broker/dhan/status
- FAIL 429  /api/broker/funds
- FAIL 401  /api/broker/holdings
- FAIL 429  /api/broker/positions/live
- FAIL 429  /api/chain/NIFTY
- FAIL 429  /api/chain/BANKNIFTY
- FAIL 429  /api/chain/FINNIFTY
- FAIL 429  /api/chain/MIDCPNIFTY
- FAIL 429 (optional) /api/chain/SENSEX
- FAIL 429  /api/gain_rank
- FAIL 401  /api/scanner/top_contract_gainers?top_n=5
- FAIL 429  /api/pnl
- FAIL 429  /api/trades/today
- FAIL 429  /api/auto_gates

## UI Screenshots
- FAIL Truth Control - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- FAIL Genesis Brain - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- FAIL E2E Proof - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- FAIL Overview - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- FAIL Option Chain - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- FAIL Signals - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- FAIL Paper Trades - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- FAIL Positions - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- FAIL Broker - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- FAIL Performance - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- FAIL ML Model - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- FAIL Live Gate - TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()


## Infrastructure Blockers
- AUTH_FAIL:429
- API_FAIL:/api/auth/status:429
- API_FAIL:/api/deploy/info:429
- API_FAIL:/api/state:429
- API_FAIL:/api/broker/dhan/status:429
- API_FAIL:/api/broker/funds:429
- API_FAIL:/api/broker/holdings:401
- API_FAIL:/api/broker/positions/live:429
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:success
- API_FAIL:/api/chain/NIFTY:429
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:success
- API_FAIL:/api/chain/BANKNIFTY:429
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:success
- API_FAIL:/api/chain/FINNIFTY:429
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:success
- API_FAIL:/api/chain/MIDCPNIFTY:429
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:success
- API_FAIL:/api/chain/SENSEX:429
- API_FAIL:/api/gain_rank:429
- API_FAIL:/api/scanner/top_contract_gainers?top_n=5:401
- API_FAIL:/api/pnl:429
- API_FAIL:/api/trades/today:429
- API_FAIL:/api/auto_gates:429
- UI_EXCEPTION:Truth Control:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Truth Control"]').first()

- UI_EXCEPTION:Genesis Brain:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Genesis Brain"]').first()

- UI_EXCEPTION:E2E Proof:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="E2E Proof"]').first()

- UI_EXCEPTION:Overview:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Overview"]').first()

- UI_EXCEPTION:Option Chain:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Option Chain"]').first()

- UI_EXCEPTION:Signals:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Signals"]').first()

- UI_EXCEPTION:Paper Trades:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Paper Trades"]').first()

- UI_EXCEPTION:Positions:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Positions"]').first()

- UI_EXCEPTION:Broker:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Broker"]').first()

- UI_EXCEPTION:Performance:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Performance"]').first()

- UI_EXCEPTION:ML Model:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="ML Model"]').first()

- UI_EXCEPTION:Live Gate:TimeoutError: locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for locator('button[title="Live Gate"]').first()

- TRADER_READINESS_PANEL_NOT_VISIBLE
- TRUTH_CONTROL_NOT_VISIBLE

## Trading Readiness Blockers
- none

## Optional Data Blockers
- none