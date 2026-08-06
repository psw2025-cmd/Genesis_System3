# Dashboard Visible Issue Tracker
Generated: 2026-08-06T09:36:33.661Z
Base: https://genesis-system3-web-doq2wplepa-el.a.run.app
Status: **BLOCKED**
Expected tab count: `16`
Scanned tab count: `16`
Visible blocker count: `78`
Info line count: `73`
Screenshot missing count: `0`
Unsettled tab count: `16`
UI exception count: `0`
Auth OK: `true`
Production-grade claim allowed: `false`
## Rule
Every live sidebar tab must be scanned and its asynchronous content must settle before PASS. A timed-out tab is still captured but is recorded as ASYNC_CONTENT_NOT_SETTLED. Visible UI blockers remain TODO until automated UI proof shows they are gone. Informational NO TRADE / MARKET CLOSED / LIVE OFF lines are recorded separately and do not count as blocker unless paired with ERROR/FAIL/PENDING/MISSING/STALE/AUTH/0/4.
## TODO
- [ ] Fix visible UI blocker on Truth Control: ASYNC_CONTENT_NOT_SETTLED after 5022ms markers=CHECKING...
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
- [ ] Fix visible UI blocker on Truth Control: Dashboard operator truth	BLOCKED	YES	health_ok=false, broker_ok=false, gates_ok=false, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- [ ] Fix visible UI blocker on Genesis Brain: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- [ ] Fix visible UI blocker on Genesis Brain: BLOCKED
- [ ] Fix visible UI blocker on Genesis Brain: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- [ ] Fix visible UI blocker on E2E Proof: ASYNC_CONTENT_NOT_SETTLED after 5019ms
- [ ] Fix visible UI blocker on E2E Proof: Real broker/data truth only. Live money remains blocked until every row below passes.
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · FULL E2E
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · API
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · DHAN CHAIN
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · NO BAD SOURCE
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback
- [ ] Fix visible UI blocker on E2E Proof: BLOCKED · TRADER READY
- [ ] Fix visible UI blocker on E2E Proof: Dhan broker connection	BLOCKED	200
- [ ] Fix visible UI blocker on E2E Proof: Dhan access token/session	BLOCKED	-
- [ ] Fix visible UI blocker on E2E Proof: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- [ ] Fix visible UI blocker on E2E Proof: No non-Dhan/stale/fallback markers in chain	BLOCKED	blocked marker found
- [ ] Fix visible UI blocker on E2E Proof: Live-money switch blocked until separate proof	PASS	blocked
- [ ] Fix visible UI blocker on E2E Proof: NIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: BANKNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: FINNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: MIDCPNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: SENSEX	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- [ ] Fix visible UI blocker on E2E Proof: /api/gain_rank	0	BLOCKED	READ_ONLY_PROBE_TIMEOUT_3500MS
- [ ] Fix visible UI blocker on Overview: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- [ ] Fix visible UI blocker on Overview: ERROR
- [ ] Fix visible UI blocker on Overview: STALE
- [ ] Fix visible UI blocker on Overview: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Overview: PEND
- [ ] Fix visible UI blocker on Overview: market-session proof pending
- [ ] Fix visible UI blocker on Sim Live: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on Option Chain: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Option Chain: Market: OPEN · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Option Chain: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Signals: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- [ ] Fix visible UI blocker on Trade: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- [ ] Fix visible UI blocker on Trade: Market: OPEN · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Trade: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- [ ] Fix visible UI blocker on Paper Trades: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Positions: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on Performance: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- [ ] Fix visible UI blocker on ML Model: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- [ ] Fix visible UI blocker on ML Model: MODEL_PROOF_LOADED_BUT_BLOCKED
- [ ] Fix visible UI blocker on ML Model: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- [ ] Fix visible UI blocker on ML Model: 0 proven / 1 blocked
- [ ] Fix visible UI blocker on ML Model: BLOCKED
- [ ] Fix visible UI blocker on ML Model: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- [ ] Fix visible UI blocker on ML Model: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-07-24T03:53:31.406031+00:00
- [ ] Fix visible UI blocker on Broker: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- [ ] Fix visible UI blocker on Broker: BLOCKED / TOKEN ERROR
- [ ] Fix visible UI blocker on Broker: BROKER AUTH BLOCKED - NOT READY
- [ ] Fix visible UI blocker on Broker: ERROR / INVALID OR EXPIRED
- [ ] Fix visible UI blocker on Broker: ERROR/BLOCKED
- [ ] Fix visible UI blocker on Broker: BROKER API AUTH ERROR
- [ ] Fix visible UI blocker on Broker: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- [ ] Fix visible UI blocker on Broker: BLOCKED BY BACKEND FLAG
- [ ] Fix visible UI blocker on Broker: Failed to load funds: unknown error
- [ ] Fix visible UI blocker on Broker: Failed to load holdings: unknown error
- [ ] Fix visible UI blocker on Broker: Failed to load positions: unknown error
- [ ] Fix visible UI blocker on Alerts: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on System: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- [ ] Fix visible UI blocker on System: ERROR
- [ ] Fix visible UI blocker on System: Broker not connected - real data unavailable
- [ ] Fix visible UI blocker on Live Gate: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- [ ] Fix visible UI blocker on Live Gate: LIVE_TRADING_BLOCKED
- [ ] Fix visible UI blocker on Live Gate: Live trading blocked — see failed gates above
## Tab results
| Tab | Status | Screenshot | Settled | Settle ms | Blockers | Info | Exceptions | Text file |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Truth Control | BLOCKED | OK | NO | 5022 | 14 | 3 | 0 | truth.txt |
| Genesis Brain | BLOCKED | OK | NO | 5016 | 3 | 5 | 0 | genesis.txt |
| E2E Proof | BLOCKED | OK | NO | 5019 | 19 | 6 | 0 | e2e_proof.txt |
| Overview | BLOCKED | OK | NO | 5016 | 6 | 10 | 0 | overview.txt |
| Sim Live | BLOCKED | OK | NO | 5015 | 1 | 6 | 0 | sim_live.txt |
| Option Chain | BLOCKED | OK | NO | 5014 | 3 | 3 | 0 | chain.txt |
| Signals | BLOCKED | OK | NO | 5014 | 1 | 3 | 0 | signals.txt |
| Trade | BLOCKED | OK | NO | 5015 | 3 | 4 | 0 | trade.txt |
| Paper Trades | BLOCKED | OK | NO | 5012 | 1 | 5 | 0 | paper.txt |
| Positions | BLOCKED | OK | NO | 5011 | 1 | 5 | 0 | positions.txt |
| Performance | BLOCKED | OK | NO | 5011 | 1 | 5 | 0 | performance.txt |
| ML Model | BLOCKED | OK | NO | 5013 | 7 | 3 | 0 | ml.txt |
| Broker | BLOCKED | OK | NO | 5012 | 11 | 3 | 0 | broker.txt |
| Alerts | BLOCKED | OK | NO | 5010 | 1 | 3 | 0 | alerts.txt |
| System | BLOCKED | OK | NO | 5009 | 3 | 4 | 0 | system.txt |
| Live Gate | BLOCKED | OK | NO | 5010 | 3 | 5 | 0 | gates.txt |
## Visible blockers
- **Truth Control**: ASYNC_CONTENT_NOT_SETTLED after 5022ms markers=CHECKING...
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
- **Truth Control**: Dashboard operator truth	BLOCKED	YES	health_ok=false, broker_ok=false, gates_ok=false, enabled_chains_ready=0/4 (runtime API probes; not hard-coded)
- **Genesis Brain**: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- **Genesis Brain**: BLOCKED
- **Genesis Brain**: Visible metrics must include Spearman rho, Top-N hit rate, prediction confidence, gain-rank staleness, and prediction-vs-actual proof. This UI now exposes the control panel; next data step is filling multi-day rows from market validation reports.
- **E2E Proof**: ASYNC_CONTENT_NOT_SETTLED after 5019ms
- **E2E Proof**: Real broker/data truth only. Live money remains blocked until every row below passes.
- **E2E Proof**: BLOCKED · FULL E2E
- **E2E Proof**: BLOCKED · API
- **E2E Proof**: BLOCKED · DHAN CHAIN
- **E2E Proof**: BLOCKED · NO BAD SOURCE
- **E2E Proof**: No non-Dhan/stale/fallback
- **E2E Proof**: BLOCKED · TRADER READY
- **E2E Proof**: Dhan broker connection	BLOCKED	200
- **E2E Proof**: Dhan access token/session	BLOCKED	-
- **E2E Proof**: Real Dhan option chain for all watched symbols	BLOCKED	0/5
- **E2E Proof**: No non-Dhan/stale/fallback markers in chain	BLOCKED	blocked marker found
- **E2E Proof**: Live-money switch blocked until separate proof	PASS	blocked
- **E2E Proof**: NIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: BANKNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: FINNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: MIDCPNIFTY	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: SENSEX	BLOCKED	dhan	dhan_only_no_rows	NO_DHAN_DATA	0	0	NO_CURRENT_OR_VERIFIED_DHAN_OPTION_CHAIN_ROWS
- **E2E Proof**: /api/gain_rank	0	BLOCKED	READ_ONLY_PROBE_TIMEOUT_3500MS
- **Overview**: ASYNC_CONTENT_NOT_SETTLED after 5016ms
- **Overview**: ERROR
- **Overview**: STALE
- **Overview**: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Overview**: PEND
- **Overview**: market-session proof pending
- **Sim Live**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **Option Chain**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Option Chain**: Market: OPEN · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Option Chain**: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Signals**: ASYNC_CONTENT_NOT_SETTLED after 5014ms
- **Trade**: ASYNC_CONTENT_NOT_SETTLED after 5015ms
- **Trade**: Market: OPEN · No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Trade**: Backend: No current or verified Dhan option-chain rows are available. Non-Dhan or old local market data is blocked by the Dhan-only truth guard.
- **Paper Trades**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Positions**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **Performance**: ASYNC_CONTENT_NOT_SETTLED after 5011ms
- **ML Model**: ASYNC_CONTENT_NOT_SETTLED after 5013ms
- **ML Model**: MODEL_PROOF_LOADED_BUT_BLOCKED
- **ML Model**: Loaded 1 blocked accuracy artifact(s). Model not proven — missing matured prediction history / post-market validation. Blocker: model_accuracy_report:NO_PREDICTION_SOURCE_FOUND
- **ML Model**: 0 proven / 1 blocked
- **ML Model**: BLOCKED
- **ML Model**: MODEL	STATUS	PREDICTIONS	AVG ACCURACY	PROOF PASS / BLOCKED	BLOCKER	GENERATED
- **ML Model**: model_accuracy_report	BLOCKED	0	N/A	0 / 1	NO_PREDICTION_SOURCE_FOUND	2026-07-24T03:53:31.406031+00:00
- **Broker**: ASYNC_CONTENT_NOT_SETTLED after 5012ms
- **Broker**: BLOCKED / TOKEN ERROR
- **Broker**: BROKER AUTH BLOCKED - NOT READY
- **Broker**: ERROR / INVALID OR EXPIRED
- **Broker**: ERROR/BLOCKED
- **Broker**: BROKER API AUTH ERROR
- **Broker**: BLOCKED UNTIL DHAN TOKEN / CLIENT AUTH IS VALID
- **Broker**: BLOCKED BY BACKEND FLAG
- **Broker**: Failed to load funds: unknown error
- **Broker**: Failed to load holdings: unknown error
- **Broker**: Failed to load positions: unknown error
- **Alerts**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **System**: ASYNC_CONTENT_NOT_SETTLED after 5009ms
- **System**: ERROR
- **System**: Broker not connected - real data unavailable
- **Live Gate**: ASYNC_CONTENT_NOT_SETTLED after 5010ms
- **Live Gate**: LIVE_TRADING_BLOCKED
- **Live Gate**: Live trading blocked — see failed gates above
## Informational lines
- **Truth Control**: PAPER
- **Truth Control**: LIVE OFF
- **Truth Control**: Paper Trades
- **Genesis Brain**: PAPER
- **Genesis Brain**: LIVE OFF
- **Genesis Brain**: Paper Trades
- **Genesis Brain**: Next: enforce position sizing in paper lifecycle
- **Genesis Brain**: "message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."
- **E2E Proof**: PAPER
- **E2E Proof**: LIVE OFF
- **E2E Proof**: Paper Trades
- **E2E Proof**: Paper/analyzer P&L endpoint	PASS	200
- **E2E Proof**: Today paper lifecycle endpoint	PASS	count=0
- **E2E Proof**: /api/state	200	PASS	PAPER
- **Overview**: PAPER
- **Overview**: LIVE OFF
- **Overview**: Paper Trades
- **Overview**: ANALYZER / PAPER COMMAND CENTER
- **Overview**: Market closed does not hide read-only broker, paper, scanner, gate, alert, or health/state data.
- **Overview**: PAPER P&L
- **Overview**: Paper only
- **Overview**: market closed must not hide read-only data
- **Overview**: Paper Lifecycle
- **Overview**: Wire is_tradeable_fo_symbol() in ranking/paper trade path
- **Sim Live**: PAPER
- **Sim Live**: LIVE OFF
- **Sim Live**: Paper Trades
- **Sim Live**: ✓ LIVE OFF
- **Sim Live**: Backend virtual paper order tape
- **Sim Live**: REAL PAPER LIFECYCLE MARKET DAY PROOF
- **Option Chain**: PAPER
- **Option Chain**: LIVE OFF
- **Option Chain**: Paper Trades
- **Signals**: PAPER
- **Signals**: LIVE OFF
- **Signals**: Paper Trades
- **Trade**: PAPER
- **Trade**: LIVE OFF
- **Trade**: Paper Trades
- **Trade**: Loading… · 0 rows · Dhan live · trading truth for paper MTM
- **Paper Trades**: PAPER
- **Paper Trades**: LIVE OFF
- **Paper Trades**: Paper Trades
- **Paper Trades**: Paper Trading Console
- **Paper Trades**: Loading paper positions + Dhan mark-to-market…
- **Positions**: PAPER
- **Positions**: LIVE OFF
- **Positions**: Paper Trades
- **Positions**: PAPER ONLY — NO REAL MONEY
- **Positions**: Paper engine generates positions during market hours
- **Performance**: PAPER
- **Performance**: LIVE OFF
- **Performance**: Paper Trades
- **Performance**: OPEN PAPER
- **Performance**: Cloud paper engine
- **ML Model**: PAPER
- **ML Model**: LIVE OFF
- **ML Model**: Paper Trades
- **Broker**: PAPER
- **Broker**: LIVE OFF
- **Broker**: Paper Trades
- **Alerts**: PAPER
- **Alerts**: LIVE OFF
- **Alerts**: Paper Trades
- **System**: PAPER
- **System**: LIVE OFF
- **System**: Paper Trades
- **System**: Paper Mode
- **Live Gate**: PAPER
- **Live Gate**: LIVE OFF
- **Live Gate**: Paper Trades
- **Live Gate**: LIVE_TRADING_ENABLED=0 (must be 0 for paper, 1 for live)
- **Live Gate**: All technical gates must pass before the approval section appears. Continue running in PAPER mode to accumulate proof data.
