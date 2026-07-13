# Dashboard Visible Issue Tracker
Generated: 2026-07-13T16:12:01.539Z
Base: https://genesis-system3-backend.onrender.com
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `83`
Info line count: `107`
Screenshot missing count: `1`
UI exception count: `1`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Backend/API route health	BLOCKED	YES	health=0, state=0
- [ ] Fix visible UI blocker on Truth Control: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- [ ] Fix visible UI blocker on Truth Control: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- [ ] Fix visible UI blocker on Truth Control: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- [ ] Fix visible UI blocker on Truth Control: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- [ ] Fix visible UI blocker on Truth Control: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- [ ] Fix visible UI blocker on Truth Control: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- [ ] Fix visible UI blocker on Truth Control: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=0
- [ ] Fix visible UI blocker on Truth Control: Risk gates and automation status	BLOCKED	YES	auto_gates_http=0, status=-
- [ ] Fix visible UI blocker on Genesis Brain: DHAN DEGRADED
- [ ] Fix visible UI blocker on Genesis Brain: Request failed with status code 502
- [ ] Fix visible UI blocker on E2E Proof: DHAN DEGRADED
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · API
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Dhan broker connection	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Dhan access token/session	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker funds/margin	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Real broker holdings response	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Real broker positions response	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	PASS	clean
- [ ] Fix visible UI blocker on E2E Proof: Paper/analyzer P&L endpoint	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Today paper lifecycle endpoint	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Gate/risk endpoint visible	BLOCKED	502
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on E2E Proof: NIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: BANKNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: FINNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: MIDCPNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: SENSEX	BLOCKED	-	-	502	-	-	UNKNOWN
- [ ] Fix visible UI blocker on E2E Proof: /api/health	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/state	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/dhan/status	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/funds	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/holdings	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/broker/positions/live	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/gain_rank	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/pnl	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/trades/today	502	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: /api/auto_gates	502	BLOCKED	-
- [ ] Fix visible UI blocker on Overview: DHAN DEGRADED
- [ ] Fix visible UI blocker on Overview: API status: RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
- [ ] Fix visible UI blocker on Overview: ERROR
- [ ] Fix visible UI blocker on Overview: STALE
- [ ] Fix visible UI blocker on Overview: FAIL
- [ ] Fix visible UI blocker on Overview: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on Option Chain: DHAN DEGRADED
- [ ] Fix visible UI blocker on Signals: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: DHAN DEGRADED
- [ ] Fix visible UI blocker on Paper Trades: DHAN DEGRADED
- [ ] Fix visible UI blocker on Paper Trades: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- [ ] Fix visible UI blocker on Paper Trades: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- [ ] Fix visible UI blocker on Paper Trades: BLOCKED
- [ ] Fix visible UI blocker on Positions: DHAN DEGRADED
- [ ] Fix visible UI blocker on Performance: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: DHAN DEGRADED
- [ ] Fix visible UI blocker on Broker: BLOCKED / TOKEN ERROR
- [ ] Fix visible UI blocker on Broker: BROKER AUTH BLOCKED - NOT READY
- [ ] Fix visible UI blocker on Broker: ERROR / INVALID OR EXPIRED
- [ ] Fix visible UI blocker on Broker: ERROR/BLOCKED
- [ ] Fix visible UI blocker on Broker: 502 - RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available.
- [ ] Fix visible UI blocker on Broker: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Broker: Failed to load funds: 502 - RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available.
- [ ] Fix visible UI blocker on Broker: Failed to load positions: Positions: Render/backend returned 502 for /api/broker/positions/live. Keeping last good data where available.
- [ ] Fix visible UI blocker on Alerts: DHAN DEGRADED
- [ ] Fix visible UI blocker on Alerts: Alerts unavailable: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on System: DHAN DEGRADED
- [ ] Fix visible UI blocker on System: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on Live Gate: DHAN DEGRADED
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | 12 | 5 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | 2 | 5 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | 33 | 5 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | 6 | 12 | 0 | overview.txt |
| Sim Live | BLOCKED | MISSING | 0 | 0 | 1 | sim_live.txt |
| Option Chain | BLOCKED | OK | 1 | 6 | 0 | chain.txt |
| Signals | BLOCKED | OK | 1 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | 1 | 6 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | 4 | 21 | 0 | paper.txt |
| Positions | BLOCKED | OK | 1 | 7 | 0 | positions.txt |
| Performance | BLOCKED | OK | 1 | 6 | 0 | performance.txt |
| ML Model | BLOCKED | OK | 4 | 5 | 0 | ml.txt |
| Broker | BLOCKED | OK | 10 | 6 | 0 | broker.txt |
| Alerts | BLOCKED | OK | 2 | 5 | 0 | alerts.txt |
| System | BLOCKED | OK | 2 | 6 | 0 | system.txt |
| Live Gate | BLOCKED | OK | 3 | 7 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Backend/API route health	BLOCKED	YES	health=0, state=0
- **Truth Control**: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- **Truth Control**: Funds / margin truth	BLOCKED	YES	available=-, used=-, source=-
- **Truth Control**: Holdings and live positions read path	BLOCKED	YES	holdings=0, positions=0
- **Truth Control**: Dhan option-chain availability	BLOCKED	YES	enabled_ready=0/4, enabled_safe_no_trade=0/4, optional_ready=0/1, optional_safe_no_trade=0/1
- **Truth Control**: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- **Truth Control**: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- **Truth Control**: Paper/analyzer lifecycle	BLOCKED	NO	today_trade_rows=0, endpoint=0
- **Truth Control**: Risk gates and automation status	BLOCKED	YES	auto_gates_http=0, status=-
- **Genesis Brain**: DHAN DEGRADED
- **Genesis Brain**: Request failed with status code 502
- **E2E Proof**: DHAN DEGRADED
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · API
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Dhan broker connection	BLOCKED	502
- **E2E Proof**: Dhan access token/session	BLOCKED	-
- **E2E Proof**: Real broker funds/margin	BLOCKED	502
- **E2E Proof**: Real broker holdings response	BLOCKED	502
- **E2E Proof**: Real broker positions response	BLOCKED	502
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	PASS	clean
- **E2E Proof**: Paper/analyzer P&L endpoint	BLOCKED	502
- **E2E Proof**: Today paper lifecycle endpoint	BLOCKED	502
- **E2E Proof**: Gate/risk endpoint visible	BLOCKED	502
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **E2E Proof**: NIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- **E2E Proof**: BANKNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- **E2E Proof**: FINNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- **E2E Proof**: MIDCPNIFTY	BLOCKED	-	-	502	-	-	UNKNOWN
- **E2E Proof**: SENSEX	BLOCKED	-	-	502	-	-	UNKNOWN
- **E2E Proof**: /api/health	502	BLOCKED	-
- **E2E Proof**: /api/state	502	BLOCKED	-
- **E2E Proof**: /api/broker/dhan/status	502	BLOCKED	-
- **E2E Proof**: /api/broker/funds	502	BLOCKED	-
- **E2E Proof**: /api/broker/holdings	502	BLOCKED	-
- **E2E Proof**: /api/broker/positions/live	502	BLOCKED	-
- **E2E Proof**: /api/gain_rank	502	BLOCKED	-
- **E2E Proof**: /api/pnl	502	BLOCKED	-
- **E2E Proof**: /api/trades/today	502	BLOCKED	-
- **E2E Proof**: /api/auto_gates	502	BLOCKED	-
- **Overview**: DHAN DEGRADED
- **Overview**: API status: RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
- **Overview**: ERROR
- **Overview**: STALE
- **Overview**: FAIL
- **Overview**: RENDER_UNAVAILABLE
- **Option Chain**: DHAN DEGRADED
- **Signals**: DHAN DEGRADED
- **Trade**: DHAN DEGRADED
- **Paper Trades**: DHAN DEGRADED
- **Paper Trades**: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- **Paper Trades**: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- **Paper Trades**: BLOCKED
- **Positions**: DHAN DEGRADED
- **Performance**: DHAN DEGRADED
- **ML Model**: DHAN DEGRADED
- **ML Model**: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: DHAN DEGRADED
- **Broker**: BLOCKED / TOKEN ERROR
- **Broker**: BROKER AUTH BLOCKED - NOT READY
- **Broker**: ERROR / INVALID OR EXPIRED
- **Broker**: ERROR/BLOCKED
- **Broker**: 502 - RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available.
- **Broker**: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- **Broker**: BLOCKED BY BACKEND FLAG
- **Broker**: Failed to load funds: 502 - RENDER_UNAVAILABLE - Render/backend returned 502 for /api/broker/funds. Keeping last good data where available.
- **Broker**: Failed to load positions: Positions: Render/backend returned 502 for /api/broker/positions/live. Keeping last good data where available.
- **Alerts**: DHAN DEGRADED
- **Alerts**: Alerts unavailable: RENDER_UNAVAILABLE
- **System**: DHAN DEGRADED
- **System**: RENDER_UNAVAILABLE
- **Live Gate**: DHAN DEGRADED
- **Live Gate**: LIVE_TRADING_BLOCKED
- **Live Gate**: Live trading blocked — see failed gates above
## Informational lines
- **Truth Control**: MARKET CLOSED / DATA POLLING
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: PAPER ONLY
- **Truth Control**: Paper Trades
- **Genesis Brain**: MARKET CLOSED / DATA POLLING
- **Genesis Brain**: PAPER
- **Genesis Brain**: LIVE OFF
- **Genesis Brain**: PAPER ONLY
- **Genesis Brain**: Paper Trades
- **E2E Proof**: MARKET CLOSED / DATA POLLING
- **E2E Proof**: PAPER
- **E2E Proof**: LIVE OFF
- **E2E Proof**: PAPER ONLY
- **E2E Proof**: Paper Trades
- **Overview**: MARKET CLOSED / DATA POLLING
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: PAPER ONLY
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Market closed: After hours (closed at 15:30)
- **Overview**: Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Option Chain**: MARKET CLOSED / DATA POLLING
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: PAPER ONLY
- **Option Chain**: Paper Trades
- **Option Chain**: NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Signals**: MARKET CLOSED / DATA POLLING
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: PAPER ONLY
- **Signals**: Paper Trades
- **Trade**: MARKET CLOSED / DATA POLLING
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: PAPER ONLY
- **Trade**: Paper Trades
- **Trade**: NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Paper Trades**: MARKET CLOSED / DATA POLLING
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: PAPER ONLY
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
- **Paper Trades**: Recheck Paper Proof
- **Paper Trades**: PAPER / ANALYZER SAFE
- **Paper Trades**: Today Paper Entries
- **Paper Trades**: Today Paper Exits
- **Paper Trades**: Closed paper/analyzer records
- **Paper Trades**: Paper Truth Provenance
- **Paper Trades**: NO_PAPER_SOURCE
- **Paper Trades**: Visual gate requirement: paper rows must show analyzer-only provenance. Fake/mock/fixture/synthetic/fallback rows must be rejected before display.
- **Paper Trades**: PAPER TRADING MODE (NO REAL ORDERS)
- **Paper Trades**: Mode: PAPER | Data Source: NOT_READY | Broker: Connected
- **Paper Trades**: Open Paper Positions (0)
- **Paper Trades**: No open paper positions
- **Paper Trades**: Today Paper Trade Proof
- **Paper Trades**: Total Paper Exposure
- **Paper Trades**: Paper UI does not call broker/order close endpoints.
- **Positions**: MARKET CLOSED / DATA POLLING
- **Positions**: PAPER
- **Positions**: LIVE OFF
- **Positions**: PAPER ONLY
- **Positions**: Paper Trades
- **Positions**: PAPER ONLY — NO REAL MONEY
- **Positions**: Paper engine generates positions during market hours
- **Performance**: MARKET CLOSED / DATA POLLING
- **Performance**: PAPER
- **Performance**: LIVE OFF
- **Performance**: PAPER ONLY
- **Performance**: Paper Trades
- **Performance**: No performance data yet — paper engine has not closed any trades.
- **ML Model**: MARKET CLOSED / DATA POLLING
- **ML Model**: PAPER
- **ML Model**: LIVE OFF
- **ML Model**: PAPER ONLY
- **ML Model**: Paper Trades
- **Broker**: MARKET CLOSED / DATA POLLING
- **Broker**: PAPER
- **Broker**: LIVE OFF
- **Broker**: PAPER ONLY
- **Broker**: Paper Trades
- **Broker**: MARKET CLOSED / READ-ONLY OK
- **Alerts**: MARKET CLOSED / DATA POLLING
- **Alerts**: PAPER
- **Alerts**: LIVE OFF
- **Alerts**: PAPER ONLY
- **Alerts**: Paper Trades
- **System**: MARKET CLOSED / DATA POLLING
- **System**: PAPER
- **System**: LIVE OFF
- **System**: PAPER ONLY
- **System**: Paper Trades
- **System**: Paper Mode
- **Live Gate**: MARKET CLOSED / DATA POLLING
- **Live Gate**: PAPER
- **Live Gate**: LIVE OFF
- **Live Gate**: PAPER ONLY
- **Live Gate**: Paper Trades
- **Live Gate**: LIVE_TRADING_ENABLED=0 (must be 0 for paper, 1 for live)
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
