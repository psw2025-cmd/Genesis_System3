# Dashboard Visible Issue Tracker
Generated: 2026-07-13T22:48:53.135Z
Base: https://genesis-system3-backend.onrender.com
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `77`
Info line count: `97`
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
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 20054ms markers=CHECKING...
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
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 20058ms
- [ ] Fix visible UI blocker on Overview: STALE
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: market-session proof pending
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 20060ms
- [ ] Fix visible UI blocker on Option Chain: DHAN DEGRADED
- [ ] Fix visible UI blocker on Option Chain: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 20047ms
- [ ] Fix visible UI blocker on Signals: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 20057ms
- [ ] Fix visible UI blocker on Trade: DHAN DEGRADED
- [ ] Fix visible UI blocker on Trade: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 20054ms
- [ ] Fix visible UI blocker on Paper Trades: DHAN DEGRADED
- [ ] Fix visible UI blocker on Paper Trades: Error Loading Data
- [ ] Fix visible UI blocker on Paper Trades: Error: Request failed with status code 502
- [ ] Fix visible UI blocker on Paper Trades: ❌ Error Loading Data Endpoint: /api/state Error: Request failed with status code 502 Retry
- [ ] Fix visible UI blocker on Paper Trades: Endpoint: /api/state Error: Request failed with status code 502
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 20065ms
- [ ] Fix visible UI blocker on Positions: DHAN DEGRADED
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- [ ] Fix visible UI blocker on Performance: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 20050ms
- [ ] Fix visible UI blocker on ML Model: DHAN DEGRADED
- [ ] Fix visible UI blocker on ML Model: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: Training proof missing.
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- [ ] Fix visible UI blocker on Broker: DHAN DEGRADED
- [ ] Fix visible UI blocker on Broker: BROKER PROOF NOT READY
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 20056ms
- [ ] Fix visible UI blocker on Alerts: DHAN DEGRADED
- [ ] Fix visible UI blocker on Alerts: Alerts unavailable: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 20060ms
- [ ] Fix visible UI blocker on System: DHAN DEGRADED
- [ ] Fix visible UI blocker on System: RENDER_UNAVAILABLE
- [ ] Fix visible UI blocker on System: Broker not connected - real data unavailable
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 20046ms
- [ ] Fix visible UI blocker on Live Gate: DHAN DEGRADED
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 20063 | 13 | 5 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 20052 | 4 | 7 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 20054 | 18 | 5 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 20058 | 4 | 14 | 0 | overview.txt |
| Sim Live | BLOCKED | MISSING | NO | 0 | 0 | 0 | 1 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 20060 | 3 | 5 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 20047 | 2 | 5 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 20057 | 3 | 6 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 20054 | 6 | 6 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 20065 | 2 | 7 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 20059 | 2 | 6 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 20050 | 5 | 5 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 20059 | 4 | 7 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 20056 | 3 | 6 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 20060 | 4 | 6 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 20046 | 4 | 7 | 0 | gates.txt |
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
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 20054ms markers=CHECKING...
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
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 20058ms
- **Overview**: STALE
- **Overview**: PEND
- **Overview**: market-session proof pending
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 20060ms
- **Option Chain**: DHAN DEGRADED
- **Option Chain**: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 20047ms
- **Signals**: DHAN DEGRADED
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 20057ms
- **Trade**: DHAN DEGRADED
- **Trade**: STALE / FALLBACK DATA - NIFTY source=dhan priority=dhan_last_verified_snapshot fetched=2026-07-13T09:51:38.030367+00:00 - Market closed — showing last verified Dhan option-chain snapshot, not live ticks.
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 20054ms
- **Paper Trades**: DHAN DEGRADED
- **Paper Trades**: Error Loading Data
- **Paper Trades**: Error: Request failed with status code 502
- **Paper Trades**: ❌ Error Loading Data Endpoint: /api/state Error: Request failed with status code 502 Retry
- **Paper Trades**: Endpoint: /api/state Error: Request failed with status code 502
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 20065ms
- **Positions**: DHAN DEGRADED
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- **Performance**: DHAN DEGRADED
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 20050ms
- **ML Model**: DHAN DEGRADED
- **ML Model**: No matured ML training/performance artifact is available. This means model is not proven trained/ready yet.
- **ML Model**: BLOCKED
- **ML Model**: Training proof missing.
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 20059ms
- **Broker**: DHAN DEGRADED
- **Broker**: BROKER PROOF NOT READY
- **Broker**: BLOCKED BY BACKEND FLAG
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 20056ms
- **Alerts**: DHAN DEGRADED
- **Alerts**: Alerts unavailable: RENDER_UNAVAILABLE
- **System**: ASYNC_CONTENT_NOT_SETTLED after 20060ms
- **System**: DHAN DEGRADED
- **System**: RENDER_UNAVAILABLE
- **System**: Broker not connected - real data unavailable
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 20046ms
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
- **Trade**: Render/backend returned 502 for /api/paper. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
- **Paper Trades**: MARKET CLOSED / DATA POLLING
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: PAPER ONLY
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
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
- **Alerts**: Render/backend returned 502 for /api/paper. Keeping last good data where available. Retrying slowly; last good truth remains visible where available.
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
