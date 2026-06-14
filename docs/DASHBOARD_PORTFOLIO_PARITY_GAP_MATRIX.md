# Dashboard Portfolio Parity Gap Matrix

**Purpose:** Convert real broker portfolio-screen expectations into System3 paper/analyzer dashboard requirements.

**Source example:** User-provided real portfolio screenshot showing Bajaj Hindusthan Sugar holding screen.

**Important safety rule:** This is a dashboard/proof requirement only. It must not enable live trading.

---

## Why this file exists

The current System3 dashboard is still closer to a system-monitoring/proof dashboard. A real broker/portfolio view shows practical account-level information that a user expects immediately:

- instrument name and latest quote
- exchange and quote timestamp
- market open/closed state
- investment amount
- current value
- overall profit/loss
- today's profit/loss
- XIRR/CAGR or equivalent return metrics
- shares/quantity held
- average buy price
- MTF/collateral/rental/borrowed flags where relevant
- buy/sell action buttons
- trade history
- news/trades/age-tax/portfolio tabs
- connectivity warning if data is weak

For System3 paper trading, the same type of truth must be visible for every paper position and every paper holding.

---

# Screenshot-derived dashboard gaps

## DP5-01 — Investment Performance card missing/incomplete

The real broker screen shows:

```text
Investment
Current Value
Overall Profit
Today's Profit
XIRR
CAGR
```

System3 paper dashboard must show equivalent values:

| Broker-style field | Paper System3 equivalent | Required source/proof |
|---|---|---|
| Investment | total paper capital deployed / premium paid | paper orders + fill ledger |
| Current Value | current mark-to-market value | live quote / paper mark price |
| Overall Profit | realized + unrealized net P&L | paper ledger + charges model |
| Today's Profit | day P&L since market open | intraday paper ledger |
| XIRR | optional for multi-day investment simulation | cashflow ledger |
| CAGR | optional for long-duration paper/investment mode | historical ledger |

**Current gap:** dashboard does not yet show full broker-style investment performance for paper trades.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/investment_performance.json`.

**Status:** BLOCKER for user trust/dashboard completeness.

---

## DP5-02 — Holding Summary missing/incomplete

The real broker screen shows:

```text
Shares in Holding
Avg Buy Price
Bought on MTF
On Rental
Borrowed
```

System3 must show for every paper position/holding:

| Broker-style field | Paper/Analyzer equivalent |
|---|---|
| Shares in Holding | paper quantity / lots / netQty |
| Avg Buy Price | weighted average paper fill price |
| Bought on MTF | product type: PAPER_CNC / PAPER_INTRADAY / PAPER_OPTIONS; MTF=N/A unless modeled |
| On Rental | N/A or 0 for paper unless lending model exists |
| Borrowed | N/A or 0 unless short/borrow model exists |

For options, it must show:

- underlying
- option symbol
- CE/PE
- strike
- expiry
- lot size
- lots
- quantity
- average premium
- premium investment
- current option LTP/bid/ask
- current mark value
- unrealized P&L
- realized P&L
- net P&L after costs

**Current gap:** System3 dashboard does not yet provide full broker-like holding summary for each paper position.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/holding_summary.json`.

**Status:** BLOCKER.

---

## DP5-03 — Current Value and mark-to-market proof missing

The screenshot has a Current Value column. For System3 paper trading, current value must be computed as:

```text
current_value = quantity × current_executable_mark_price
```

For options, mark price must not blindly use LTP. It should prefer:

```text
mark_price = mid(bid, ask) when bid/ask valid
else conservative executable bid for long positions
else LTP only with warning
```

**Current gap:** paper dashboard may show P&L without proving executable mark price.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/mark_to_market_proof.json`.

**Status:** BLOCKER.

---

## DP5-04 — Quote timestamp and data quality warning missing/incomplete

The screenshot shows exchange and last quote time, and also a poor internet warning.

System3 dashboard must show:

- exchange
- quote source
- quote timestamp
- quote age seconds
- market open/closed
- data source: live/bhavcopy/synthetic/fallback/not-ready
- poor connection / stale quote / broker error warning
- last successful quote fetch
- last broker heartbeat

**Current gap:** dashboard truth is incomplete if it shows values without quote freshness and connectivity warnings.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/data_quality_badges.json`.

**Status:** BLOCKER.

---

## DP5-05 — Today’s P&L and overall P&L separation missing/incomplete

Broker-style screen separates:

```text
Overall Profit
Today's Profit
```

System3 must separate:

| Metric | Meaning |
|---|---|
| realized_pnl_today | closed trades today after charges |
| unrealized_pnl_today | MTM change in open paper positions today |
| total_day_pnl | realized + unrealized today |
| overall_realized_pnl | all closed paper trades |
| overall_unrealized_pnl | current open MTM |
| total_pnl | overall realized + unrealized |
| net_pnl_after_costs | total after brokerage/taxes/slippage |

**Current gap:** dashboard must not mix total, daily, realized, and unrealized values.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/pnl_reconciliation.json`.

**Status:** BLOCKER.

---

## DP5-06 — Buy/Sell action states must be safe and explicit

The real broker screen has Buy and Sell buttons. For System3 Analyzer/Paper mode, dashboard may show action buttons but must label them clearly:

| Button/state | Allowed behavior |
|---|---|
| Buy | Paper order only when paper mode active and proof passes |
| Sell | Paper exit only for paper position |
| Live Buy/Sell | hidden/disabled until explicit user approval and live flags enabled |
| Disabled reason | must show exact blocker |

**Required blocker labels:**

- live trading disabled
- paper not ready
- market closed
- quote stale
- no valid contract token
- risk gate failed
- broker disconnected
- no exit liquidity

**Current gap:** dashboard lacks broker-style action area with safe paper/live separation and blocker reasons.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/action_state_proof.json`.

**Status:** BLOCKER.

---

## DP5-07 — Tabs and drill-down sections missing/incomplete

The screenshot has:

```text
Market
Portfolio
Age & Tax
News
Trades
```

System3 dashboard should have equivalent paper/analyzer tabs:

| Broker tab | System3 paper/analyzer equivalent |
|---|---|
| Market | quote, chart, option-chain, market regime |
| Portfolio | holdings/positions/P&L summary |
| Age & Tax | holding age, charges, tax/STT estimate, cost model |
| News | event/news/macro risk feed |
| Trades | paper orderbook, tradebook, fill/exits, audit |

**Current gap:** System3 dashboard currently focuses more on proof/system health than full trade/portfolio drill-down.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/tab_coverage.json`.

**Status:** FEATURE_GAP.

---

## DP5-08 — Portfolio/position upstream data model missing

A real portfolio screen requires a clean upstream model. System3 needs these tables/ledgers:

```text
paper_orders
paper_fills
paper_trades
paper_positions
paper_holdings
paper_cashflows
paper_charges
paper_mark_to_market_snapshots
paper_pnl_daily
paper_corporate_actions
paper_contract_specs
paper_audit_events
```

Each row must include:

- symbol / trading symbol
- exchange segment
- instrument token
- product type
- buy/sell side
- quantity/lots
- average price
- fill price
- order time
- fill time
- quote time
- source
- charges
- realized/unrealized P&L
- strategy/signal id
- risk decision id
- proof id

**Current gap:** without this upstream ledger, dashboard cannot be trusted.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/upstream_ledger_schema.json`.

**Status:** HARD_BLOCKER for portfolio truth.

---

## DP5-09 — Broker API parity requirement

A real dashboard can be modeled from broker APIs. For Dhan, official API documentation exposes portfolio/positions endpoints with holdings and positions including fields such as total quantity, average cost price, product type, buy/sell quantities, net quantity, realized profit, unrealized profit, expiry date, option type, and strike price. Dhan also exposes market quote fields such as LTP, OHLC, depth, buy/sell quantity, volume, and OI.

System3 paper dashboard should mirror that structure even in Analyzer/Paper mode:

```text
paper_holding ≈ broker_holding shape
paper_position ≈ broker_position shape
paper_quote ≈ broker_market_quote shape
paper_tradebook ≈ broker_tradebook shape
paper_orderbook ≈ broker_orderbook shape
```

**Current gap:** paper state is not yet broker-shape compatible.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/broker_shape_parity.json`.

**Status:** BLOCKER.

---

## DP5-10 — Options portfolio parity

For paper options, the broker-style dashboard must show:

- underlying
- option symbol
- strike
- expiry
- CE/PE
- lot size
- lots
- net quantity
- avg buy premium
- current bid/ask/LTP
- executable mark price
- premium investment
- current value
- theta decay estimate
- IV change
- delta/gamma/vega
- stop loss
- target
- trailing status
- time stop
- exit liquidity
- current net P&L after charges

**Current gap:** current dashboard does not expose this broker-style option portfolio panel.

**Required artifact:** `reports/latest/dashboard_portfolio_parity/options_position_card.json`.

**Status:** BLOCKER.

---

# Dashboard portfolio parity required top cards

System3 dashboard must add these cards:

## Portfolio Summary

```text
Mode: ANALYZER / PAPER / LIVE_DISABLED
Production Ready: NO
Paper Ready: YES/NO
Broker Connected: YES/NO
Data Source: LIVE / NOT_READY / SYNTHETIC / FALLBACK
Last Quote Time
Quote Age
```

## Investment Performance

```text
Capital Allocated
Premium/Investment Deployed
Current Value
Overall P&L
Today's P&L
Realized P&L
Unrealized P&L
Net P&L after charges
Return %
Max Drawdown
```

## Position/Holding Summary

```text
Symbol
Exchange
Quantity/Lots
Avg Buy Price
Current Executable Price
Current Value
Day P&L
Total P&L
Product Type
Signal ID
Risk Status
Exit Status
```

## Options Position Card

```text
Underlying
CE/PE
Strike
Expiry
Lot Size
Lots
Premium Paid
Current Bid/Ask/LTP
Spread %
OI
Volume
IV
Greeks
Theta Risk
Expiry Risk
Stop/Target/Trail
Exit Liquidity
```

## Data Quality Card

```text
Connection status
Broker heartbeat
Quote timestamp
Staleness
Fallback used?
Synthetic used?
Last successful refresh
API error
Poor internet / poor data warning
```

---

# Final requirement

A paper-trade dashboard is incomplete unless the user can answer:

```text
What did System3 buy/sell?
At what price?
Why?
How much capital/premium is deployed?
What is current value?
What is today’s P&L?
What is total P&L?
Is this value based on live quote, stale quote, or fallback?
Can I exit?
What is the exact blocker if I cannot exit?
```

Until these are visible and reconciled, dashboard status must remain:

```text
DASHBOARD_PORTFOLIO_PARITY: NOT_PROVEN
```
