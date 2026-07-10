# Dashboard Live UI Proof

Generated: 2026-07-10T11:48:24.820Z
Base: https://genesis-system3-backend.onrender.com
Final verdict: **BLOCKED_NOT_TRADE_READY**
Trader readiness panel visible: **true**
Truth control visible: **true**

## Chain Truth
- PASS /api/chain/NIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=24212.8 contracts=160 blocker=-
- PASS /api/chain/BANKNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=58082.7 contracts=160 blocker=-
- PASS /api/chain/FINNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=26824.1 contracts=160 blocker=-
- PASS /api/chain/MIDCPNIFTY source=dhan priority=dhan_last_verified_snapshot status=MARKET_CLOSED_DHAN_SNAPSHOT spot=14796 contracts=160 blocker=-
- BLOCKED /api/chain/SENSEX source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS

## API
- PASS 200 /api/auth/status
- PASS 200 /api/deploy/info
- PASS 200 /api/health
- PASS 200 /api/state
- PASS 200 /api/broker/dhan/status
- PASS 200 /api/broker/funds
- PASS 200 /api/broker/holdings
- PASS 200 /api/broker/positions/live
- PASS 200 /api/chain/NIFTY
- PASS 200 /api/chain/BANKNIFTY
- PASS 200 /api/chain/FINNIFTY
- PASS 200 /api/chain/MIDCPNIFTY
- PASS 200 /api/chain/SENSEX
- PASS 200 /api/gain_rank
- PASS 200 /api/pnl
- PASS 200 /api/trades/today
- PASS 200 /api/auto_gates

## UI Screenshots
- PASS Truth Control
- PASS Genesis Brain
- PASS E2E Proof
- PASS Overview
- PASS Option Chain
- PASS Signals
- PASS Paper Trades
- PASS Positions
- PASS Broker
- PASS Performance
- PASS ML Model
- PASS Live Gate

## Infrastructure Blockers
- none

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS