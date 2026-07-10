# Dashboard Live UI Proof

Generated: 2026-07-10T09:05:00.199Z
Base: https://genesis-system3-backend.onrender.com
Final verdict: **FAIL**
Trader readiness panel visible: **true**
Truth control visible: **true**

## Chain Truth
- BLOCKED /api/chain/NIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/BANKNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/FINNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- BLOCKED /api/chain/MIDCPNIFTY source=dhan priority=dhan_only_no_rows status=NO_DHAN_DATA spot=0 contracts=0 blocker=NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
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
- FAIL Signals
- FAIL Paper Trades
- PASS Positions
- PASS Broker
- PASS Performance
- PASS ML Model
- PASS Live Gate

## Infrastructure Blockers
- UI_FAIL:Signals
- UI_FAIL:Paper Trades

## Trading Readiness Blockers
- CHAIN_NOT_TRADE_READY:/api/chain/NIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/BANKNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/FINNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/MIDCPNIFTY:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- CHAIN_NOT_TRADE_READY:/api/chain/SENSEX:NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS