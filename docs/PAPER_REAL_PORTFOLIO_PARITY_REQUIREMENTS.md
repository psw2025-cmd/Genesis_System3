# Paper and Real Trade Portfolio Parity Requirements

**Purpose:** Ensure System3 dashboard and upstream ledgers support both paper-trade portfolio and real/broker portfolio visibility, with strict safety separation.

**Important safety rule:** This document does not approve live trading. Real trade portfolio can be read-only/reconciled while live order placement remains disabled until proof and explicit user approval.

---

# Core requirement

System3 must support three portfolio views:

```text
1. PAPER PORTFOLIO
2. REAL BROKER PORTFOLIO READ-ONLY
3. COMBINED / SIDE-BY-SIDE PORTFOLIO COMPARISON
```

These must never be mixed silently.

Every row, card, chart, and P&L number must show source:

```text
source = PAPER_LEDGER / BROKER_LIVE_READONLY / RECONCILED / STALE / FALLBACK / NOT_PROVEN
```

---

# PRP6-01 — Paper portfolio view

Paper portfolio must show all simulated/analyzer positions created by System3 paper logic.

Required fields:

- mode: PAPER
- strategy/signal id
- symbol/trading symbol
- exchange segment
- underlying
- instrument token
- CE/PE for options
- strike
- expiry
- lot size
- lots
- quantity
- side: buy/sell
- product type: PAPER_INTRADAY / PAPER_OPTIONS / PAPER_CNC
- average entry price
- entry quote timestamp
- current executable mark price
- current quote timestamp
- current value
- premium/capital deployed
- realized P&L
- unrealized P&L
- today's P&L
- total net P&L after charges/slippage
- stop loss
- target
- trailing status
- time stop
- exit liquidity
- status: open/closed/exited/blocked

Required artifact:

```text
reports/latest/portfolio_parity/paper_portfolio_snapshot.json
```

Status: `NOT_PROVEN`.

---

# PRP6-02 — Real broker portfolio read-only view

Real broker portfolio must be read-only unless live trading is later explicitly enabled by user approval and proof gates.

Required fields:

- mode: REAL_READONLY
- broker name
- broker connection status
- broker account alias only, no sensitive account data
- holdings
- positions
- orderbook
- tradebook
- funds/margin summary if permitted
- symbol/trading symbol
- exchange segment
- instrument token
- quantity
- average price
- current broker quote/mark
- realized P&L
- unrealized P&L
- today's P&L if broker provides or can be reconciled
- product type
- expiry/strike/option type for F&O
- last broker fetch time
- fetch status
- stale flag

Required artifact:

```text
reports/latest/portfolio_parity/real_broker_portfolio_readonly.json
```

Status: `NEEDS_BROKER_RUNTIME`.

---

# PRP6-03 — Paper vs real portfolio separation

The dashboard must never combine paper and real positions without clear labels.

Required UI labels:

```text
PAPER POSITION
REAL BROKER POSITION — READ ONLY
RECONCILED MATCH
MISMATCH
STALE BROKER DATA
STALE PAPER DATA
```

Required blocker rule:

```text
If portfolio source is unclear, dashboard must show PORTFOLIO_SOURCE_NOT_PROVEN and must not calculate combined P&L.
```

Required artifact:

```text
reports/latest/portfolio_parity/source_separation_proof.json
```

Status: `BLOCKER`.

---

# PRP6-04 — Combined portfolio comparison view

System3 should show side-by-side comparison:

| Field | Paper | Real Broker | Reconciliation |
|---|---|---|---|
| Symbol | paper symbol | broker symbol | match/mismatch |
| Quantity | paper qty | broker qty | match/mismatch |
| Avg price | paper avg | broker avg | diff |
| Current price | paper mark | broker mark | diff |
| Current value | paper value | broker value | diff |
| Day P&L | paper day P&L | broker day P&L | diff |
| Total P&L | paper total P&L | broker total P&L | diff |
| Status | paper status | broker status | reconciled/unreconciled |

Required artifact:

```text
reports/latest/portfolio_parity/paper_vs_real_reconciliation.json
```

Status: `NOT_PROVEN`.

---

# PRP6-05 — Real trade P&L reconciliation

For real/broker portfolio read-only, P&L must be reconciled from broker-provided values and System3 computed values.

Required calculations:

```text
real_current_value = broker_quantity × broker_mark_price
real_day_pnl = broker_day_pnl if available else computed from previous close/current mark
real_total_pnl = broker_realized_pnl + broker_unrealized_pnl
real_net_pnl = real_total_pnl - known costs if not already included
```

Required flags:

- broker_value_used
- system_computed_value_used
- discrepancy_amount
- discrepancy_percent
- reconciliation_status

Required artifact:

```text
reports/latest/portfolio_parity/real_pnl_reconciliation.json
```

Status: `NOT_PROVEN`.

---

# PRP6-06 — Paper trade P&L reconciliation

Paper P&L must be calculated from actual paper fills and current executable mark price.

Required calculations:

```text
paper_investment = sum(entry_fill_price × quantity) + costs
paper_current_value = current_executable_mark_price × quantity
paper_unrealized_pnl = paper_current_value - paper_investment - exit_estimated_costs
paper_realized_pnl = closed_trade_exit_value - entry_value - costs
paper_day_pnl = today's realized + today's mark-to-market change
paper_total_pnl = realized + unrealized
```

Required artifact:

```text
reports/latest/portfolio_parity/paper_pnl_reconciliation.json
```

Status: `NOT_PROVEN`.

---

# PRP6-07 — Portfolio cards required on dashboard

Dashboard must include these separate cards:

## Paper Portfolio Card

```text
Mode: PAPER
Paper Capital
Paper Investment Deployed
Paper Current Value
Paper Today P&L
Paper Overall P&L
Open Paper Positions
Closed Paper Trades
Paper Net P&L after costs
Paper Data Freshness
```

## Real Broker Portfolio Card

```text
Mode: REAL READ-ONLY
Broker Connected
Broker Last Fetch
Real Holdings Count
Real Positions Count
Real Current Value
Real Today P&L
Real Overall P&L
Broker Data Freshness
Live Trading: DISABLED
```

## Reconciliation Card

```text
Paper vs Real Source Separation: PASS/FAIL
Broker Position Reconciled: YES/NO
P&L Reconciled: YES/NO
Mismatch Count
Stale Source Count
Exact Blockers
```

Required artifact:

```text
reports/latest/portfolio_parity/dashboard_card_coverage.json
```

Status: `FEATURE_GAP`.

---

# PRP6-08 — Real portfolio action safety

Real portfolio rows may show action buttons only with strict safety labels.

Allowed while live disabled:

```text
View only
Refresh broker data
Compare with paper
Export proof
```

Not allowed while live disabled:

```text
Real Buy
Real Sell
Real Modify
Real Cancel
```

If action buttons exist, they must be disabled and show exact reason:

```text
LIVE_TRADING_DISABLED
USER_APPROVAL_MISSING
TRADE_READY_FALSE
BROKER_RECONCILIATION_NOT_PROVEN
RISK_GATE_NOT_PROVEN
```

Required artifact:

```text
reports/latest/portfolio_parity/real_action_safety.json
```

Status: `BLOCKER`.

---

# PRP6-09 — Paper and real orderbook/tradebook tabs

Dashboard must show four separate tabs:

```text
Paper Orders
Paper Trades
Real Broker Orderbook Read-Only
Real Broker Tradebook Read-Only
```

Every order/trade row must include:

- source
- symbol
- side
- quantity
- price
- order status
- timestamp
- exchange order id for broker real orders if available
- paper order id for paper orders
- strategy/signal id for System3 paper orders
- charges/costs
- P&L impact

Required artifact:

```text
reports/latest/portfolio_parity/order_tradebook_coverage.json
```

Status: `FEATURE_GAP`.

---

# PRP6-10 — Data freshness and connection state for both portfolios

Dashboard must show freshness separately:

| Source | Freshness required |
|---|---|
| Paper ledger | last write time and last mark time |
| Real broker portfolio | last successful broker fetch time |
| Quote | last quote timestamp and quote age |
| Option chain | last option-chain fetch time |
| P&L | last recalculation time |

If any source is stale, show:

```text
PAPER_PORTFOLIO_STALE
REAL_PORTFOLIO_STALE
QUOTE_STALE
OPTION_CHAIN_STALE
PNL_STALE
```

Required artifact:

```text
reports/latest/portfolio_parity/freshness_matrix.json
```

Status: `BLOCKER`.

---

# Final portfolio parity rule

System3 dashboard is incomplete until it can answer separately:

```text
What is my paper portfolio?
What is my real broker portfolio?
What is the difference between them?
Which values are live, stale, or fallback?
What is paper P&L?
What is real P&L?
What is reconciled and what is not?
Why is live action disabled?
```

Until then:

```text
PAPER_REAL_PORTFOLIO_PARITY: NOT_PROVEN
LIVE_TRADING: DISABLED
```
