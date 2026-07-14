# Dashboard Visible Issue Tracker
Generated: 2026-07-14T01:22:03.141Z
Base: https://genesis-system3-backend.onrender.com
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `78`
Info line count: `107`
Screenshot missing count: `1`
Unsettled tab count: `16`
UI exception count: `1`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 20063ms markers=CHECKING...
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
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 20052ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: last scanner snapshot and staleness
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 20048ms markers=CHECKING...
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · API
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Dhan broker connection	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Dhan access token/session	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker funds/margin	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker holdings response	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real broker positions response	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	PASS	clean
- [ ] Fix visible UI blocker on E2E Proof: Paper/analyzer P&L endpoint	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Today paper lifecycle endpoint	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Gate/risk endpoint visible	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- [ ] Fix visible UI blocker on Overview: STALE
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: market-session proof pending
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- [ ] Fix visible UI blocker on Option Chain: DHAN DEGRADED
- [ ] Fix visible UI blocker on Option Chain: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- [ ] Fix visible UI blocker on Signals: DHAN DEGRADED
- [ ] Fix visible UI blocker on Signals: Error Loading Data
- [ ] Fix visible UI blocker on Signals: Error: Request failed with status code 502
- [ ] Fix visible UI blocker on Signals: Signal data unavailable
- [ ] Fix visible UI blocker on Signals: ❌ Error Loading Data Endpoint: /api/state HTTP Status: 502 Error: Request failed with status code 502 Retry
- [ ] Fix visible UI blocker on Signals: Endpoint: /api/state HTTP Status: 502 Error: Request failed with status code 502
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 20047ms
- [ ] Fix visible UI blocker on Trade: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 20041ms
- [ ] Fix visible UI blocker on Paper Trades: DHAN DEGRADED
- [ ] Fix visible UI blocker on Paper Trades: unavailable
- [ ] Fix visible UI blocker on Paper Trades: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- [ ] Fix visible UI blocker on Paper Trades: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- [ ] Fix visible UI blocker on Paper Trades: BLOCKED
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 20039ms
- [ ] Fix visible UI blocker on Positions: DHAN DEGRADED
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 20043ms
- [ ] Fix visible UI blocker on Performance: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 20040ms
- [ ] Fix visible UI blocker on ML Model: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- [ ] Fix visible UI blocker on Broker: DHAN DEGRADED
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- [ ] Fix visible UI blocker on Alerts: DHAN DEGRADED
- [ ] Fix visible UI blocker on Alerts: Alerts unavailable: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 20055ms
- [ ] Fix visible UI blocker on System: DHAN DEGRADED
- [ ] Fix visible UI blocker on System: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 20055ms
- [ ] Fix visible UI blocker on Live Gate: DHAN DEGRADED
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 20063 | 13 | 5 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 20052 | 4 | 7 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 20048 | 18 | 5 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 20053 | 4 | 14 | 0 | overview.txt |
| Sim Live | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 20053 | 3 | 5 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 20042 | 7 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 20047 | 3 | 5 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 20041 | 6 | 20 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 20039 | 2 | 7 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 20043 | 2 | 6 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 20040 | 5 | 5 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 20059 | 3 | 7 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 20053 | 3 | 5 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 20055 | 3 | 6 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 20055 | 2 | 5 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 20063ms markers=CHECKING...
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
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 20052ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: last scanner snapshot and staleness
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 20048ms markers=CHECKING...
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · API
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Dhan broker connection	BLOCKED	-
- **E2E Proof**: Dhan access token/session	BLOCKED	-
- **E2E Proof**: Real broker funds/margin	BLOCKED	-
- **E2E Proof**: Real broker holdings response	BLOCKED	-
- **E2E Proof**: Real broker positions response	BLOCKED	-
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	PASS	clean
- **E2E Proof**: Paper/analyzer P&L endpoint	BLOCKED	-
- **E2E Proof**: Today paper lifecycle endpoint	BLOCKED	-
- **E2E Proof**: Gate/risk endpoint visible	BLOCKED	-
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- **Overview**: STALE
- **Overview**: PEND
- **Overview**: market-session proof pending
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- **Option Chain**: DHAN DEGRADED
- **Option Chain**: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 20042ms
- **Signals**: DHAN DEGRADED
- **Signals**: Error Loading Data
- **Signals**: Error: Request failed with status code 502
- **Signals**: Signal data unavailable
- **Signals**: ❌ Error Loading Data Endpoint: /api/state HTTP Status: 502 Error: Request failed with status code 502 Retry
- **Signals**: Endpoint: /api/state HTTP Status: 502 Error: Request failed with status code 502
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 20047ms
- **Trade**: DHAN DEGRADED
- **Trade**: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 20041ms
- **Paper Trades**: DHAN DEGRADED
- **Paper Trades**: unavailable
- **Paper Trades**: System is in PAPER mode. All trades are simulated. No real money orders will be placed. Broker not ready - real data unavailable.
- **Paper Trades**: Reason: paper engine has no open position, market is closed, Dhan data is blocked, or paper gate rejected the setup. This is not a live-order failure.
- **Paper Trades**: BLOCKED
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 20039ms
- **Positions**: DHAN DEGRADED
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 20043ms
- **Performance**: DHAN DEGRADED
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 20040ms
- **ML Model**: DHAN DEGRADED
- **ML Model**: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- **Broker**: DHAN DEGRADED
- **Broker**: BLOCKED BY BACKEND FLAG
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 20053ms
- **Alerts**: DHAN DEGRADED
- **Alerts**: Alerts unavailable: RENDER_UNAVAILABLE
- **System**: ASYNC_CONTENT_NOT_SETTLED after 20055ms
- **System**: DHAN DEGRADED
- **System**: RENDER_UNAVAILABLE
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 20055ms
- **Live Gate**: DHAN DEGRADED
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
- **Genesis Brain**: Next: enforce position sizing in paper lifecycle
- **Genesis Brain**: "message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."
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
- **Overview**: Market closed: Before pre-market (opens at 09:15)
- **Overview**: Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Overview**: Paper Lifecycle
- **Overview**: Wire is_tradeable_fo_symbol() in ranking/paper trade path
- **Option Chain**: MARKET CLOSED / DATA POLLING
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: PAPER ONLY
- **Option Chain**: Paper Trades
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
- **Broker**: NONE - MARKET CLOSED IS OK
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
