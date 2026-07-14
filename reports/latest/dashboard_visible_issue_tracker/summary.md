# Dashboard Visible Issue Tracker
Generated: 2026-07-14T04:32:00.587Z
Base: https://genesis-system3-backend.onrender.com
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `87`
Info line count: `94`
Screenshot missing count: `1`
Unsettled tab count: `16`
UI exception count: `1`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- [ ] Fix visible UI blocker on Truth Control: BLOCKED
- [ ] Fix visible UI blocker on Truth Control: MONEY_READY_BLOCKED
- [ ] Fix visible UI blocker on Truth Control: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- [ ] Fix visible UI blocker on Truth Control: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- [ ] Fix visible UI blocker on Truth Control: Dhan option-chain availability	PARTIAL	YES	enabled_ready=0/4, enabled_safe_no_trade=4/4, optional_ready=0/1, optional_safe_no_trade=1/1
- [ ] Fix visible UI blocker on Truth Control: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- [ ] Fix visible UI blocker on Truth Control: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 20058ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 20058ms
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
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- [ ] Fix visible UI blocker on Overview: ERROR
- [ ] Fix visible UI blocker on Overview: Client ID or user generated access token is invalid or expired.
- [ ] Fix visible UI blocker on Overview: STALE
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: market-session proof pending
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 20045ms
- [ ] Fix visible UI blocker on Option Chain: Source: dhan / blocked_until_real_dhan_stream
- [ ] Fix visible UI blocker on Option Chain: OPTION CHAIN - NIFTY Live option-chain rows are not available for this selected symbol. Status: NO_DHAN_DATA Source: dhan / blocked_until_real_dhan_stream Backend: NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 20044ms
- [ ] Fix visible UI blocker on Signals: What Blocked Trading?
- [ ] Fix visible UI blocker on Signals: 0/4
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? No Underlying Low Confidence
- [ ] Fix visible UI blocker on Signals: What Blocked Trading? Scanner Segments 0/4
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 20049ms
- [ ] Fix visible UI blocker on Trade: Source: dhan / blocked_until_real_dhan_stream
- [ ] Fix visible UI blocker on Trade: OPTION CHAIN - NIFTY Live option-chain rows are not available for this selected symbol. Status: NO_DHAN_DATA Source: dhan / blocked_until_real_dhan_stream Backend: NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 20044ms
- [ ] Fix visible UI blocker on Paper Trades: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- [ ] Fix visible UI blocker on Paper Trades: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- [ ] Fix visible UI blocker on Paper Trades: BLOCKED
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 20050ms
- [ ] Fix visible UI blocker on ML Model: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- [ ] Fix visible UI blocker on Broker: BLOCKED / TOKEN ERROR
- [ ] Fix visible UI blocker on Broker: BROKER AUTH BLOCKED - NOT READY
- [ ] Fix visible UI blocker on Broker: ERROR / INVALID OR EXPIRED
- [ ] Fix visible UI blocker on Broker: ERROR/BLOCKED
- [ ] Fix visible UI blocker on Broker: DH-901 - Invalid_Authentication - Client ID or user generated access token is invalid or expired.
- [ ] Fix visible UI blocker on Broker: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Broker: Failed to load funds: DH-901 - Invalid_Authentication - Client ID or user generated access token is invalid or expired.
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- [ ] Fix visible UI blocker on Alerts: Alerts unavailable: NO_DHAN_DATA
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 20041ms
- [ ] Fix visible UI blocker on System: Broker not connected - real data unavailable
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 20059 | 8 | 5 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 20058 | 3 | 6 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 20058 | 33 | 4 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 20053 | 6 | 11 | 0 | overview.txt |
| Sim Live | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 20045 | 3 | 4 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 20044 | 5 | 6 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 20049 | 3 | 4 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 20044 | 4 | 20 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 20048 | 1 | 6 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 20042 | 1 | 5 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 20050 | 4 | 4 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 20048 | 9 | 4 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 20042 | 2 | 4 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 20041 | 2 | 5 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 20048 | 3 | 6 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- **Truth Control**: BLOCKED
- **Truth Control**: MONEY_READY_BLOCKED
- **Truth Control**: At least one required enabled-universe layer is missing proof. Live broker order execution must remain disabled.
- **Truth Control**: Broker read-only connection	BLOCKED	YES	connected=false, broker=dhan, order_allowed=false
- **Truth Control**: Dhan option-chain availability	PARTIAL	YES	enabled_ready=0/4, enabled_safe_no_trade=4/4, optional_ready=0/1, optional_safe_no_trade=1/1
- **Truth Control**: Universe / ranking candidates	BLOCKED	YES	candidate_rows=0, gain=0, scanner=0
- **Truth Control**: CE / PE decision evidence	BLOCKED	YES	No CE/PE side found in model/ranker/scanner payload
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 20058ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 20058ms
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
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- **Overview**: ERROR
- **Overview**: Client ID or user generated access token is invalid or expired.
- **Overview**: STALE
- **Overview**: PEND
- **Overview**: market-session proof pending
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 20045ms
- **Option Chain**: Source: dhan / blocked_until_real_dhan_stream
- **Option Chain**: OPTION CHAIN - NIFTY Live option-chain rows are not available for this selected symbol. Status: NO_DHAN_DATA Source: dhan / blocked_until_real_dhan_stream Backend: NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 20044ms
- **Signals**: What Blocked Trading?
- **Signals**: 0/4
- **Signals**: What Blocked Trading? No Underlying Low Confidence
- **Signals**: What Blocked Trading? Scanner Segments 0/4
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 20049ms
- **Trade**: Source: dhan / blocked_until_real_dhan_stream
- **Trade**: OPTION CHAIN - NIFTY Live option-chain rows are not available for this selected symbol. Status: NO_DHAN_DATA Source: dhan / blocked_until_real_dhan_stream Backend: NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 20044ms
- **Paper Trades**: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- **Paper Trades**: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- **Paper Trades**: BLOCKED
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 20050ms
- **ML Model**: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- **Broker**: BLOCKED / TOKEN ERROR
- **Broker**: BROKER AUTH BLOCKED - NOT READY
- **Broker**: ERROR / INVALID OR EXPIRED
- **Broker**: ERROR/BLOCKED
- **Broker**: DH-901 - Invalid_Authentication - Client ID or user generated access token is invalid or expired.
- **Broker**: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- **Broker**: BLOCKED BY BACKEND FLAG
- **Broker**: Failed to load funds: DH-901 - Invalid_Authentication - Client ID or user generated access token is invalid or expired.
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- **Alerts**: Alerts unavailable: NO_DHAN_DATA
- **System**: ASYNC_CONTENT_NOT_SETTLED after 20041ms
- **System**: Broker not connected - real data unavailable
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 20048ms
- **Live Gate**: LIVE_TRADING_BLOCKED
- **Live Gate**: Live trading blocked — see failed gates above
## Informational lines
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: PAPER ONLY
- **Truth Control**: Paper Trades
- **Truth Control**: Paper/analyzer lifecycle	PARTIAL	NO	today_trade_rows=0, endpoint=200
- **Genesis Brain**: PAPER
- **Genesis Brain**: LIVE OFF
- **Genesis Brain**: PAPER ONLY
- **Genesis Brain**: Paper Trades
- **Genesis Brain**: Next: enforce position sizing in paper lifecycle
- **Genesis Brain**: "message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."
- **E2E Proof**: PAPER
- **E2E Proof**: LIVE OFF
- **E2E Proof**: PAPER ONLY
- **E2E Proof**: Paper Trades
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: PAPER ONLY
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Paper Lifecycle
- **Overview**: Wire is_tradeable_fo_symbol() in ranking/paper trade path
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: PAPER ONLY
- **Option Chain**: Paper Trades
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: PAPER ONLY
- **Signals**: Paper Trades
- **Signals**: NO TRADE
- **Signals**: No signal generated
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: PAPER ONLY
- **Trade**: Paper Trades
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
- **Paper Trades**: Mode: PAPER | Data Source: NOT_READY | Broker: Disconnected
- **Paper Trades**: Open Paper Positions (0)
- **Paper Trades**: No open paper positions
- **Paper Trades**: Today Paper Trade Proof
- **Paper Trades**: Total Paper Exposure
- **Paper Trades**: Paper UI does not call broker/order close endpoints.
- **Positions**: PAPER
- **Positions**: LIVE OFF
- **Positions**: PAPER ONLY
- **Positions**: Paper Trades
- **Positions**: PAPER ONLY — NO REAL MONEY
- **Positions**: Paper engine generates positions during market hours
- **Performance**: PAPER
- **Performance**: LIVE OFF
- **Performance**: PAPER ONLY
- **Performance**: Paper Trades
- **Performance**: No performance data yet — paper engine has not closed any trades.
- **ML Model**: PAPER
- **ML Model**: LIVE OFF
- **ML Model**: PAPER ONLY
- **ML Model**: Paper Trades
- **Broker**: PAPER
- **Broker**: LIVE OFF
- **Broker**: PAPER ONLY
- **Broker**: Paper Trades
- **Alerts**: PAPER
- **Alerts**: LIVE OFF
- **Alerts**: PAPER ONLY
- **Alerts**: Paper Trades
- **System**: PAPER
- **System**: LIVE OFF
- **System**: PAPER ONLY
- **System**: Paper Trades
- **System**: Paper Mode
- **Live Gate**: PAPER
- **Live Gate**: LIVE OFF
- **Live Gate**: PAPER ONLY
- **Live Gate**: Paper Trades
- **Live Gate**: LIVE_TRADING_ENABLED=0 (must be 0 for paper, 1 for live)
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
