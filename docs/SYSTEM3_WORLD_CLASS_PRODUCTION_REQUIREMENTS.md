# System3 World-Class Production Readiness Requirements

## Current verdict

System3 must remain in **ANALYZER / PAPER ONLY** until the requirements below are proven with live market-session evidence.

Live trading must remain disabled.

## Why this document exists

Recent paper results and dashboard screenshots show that basic API connectivity is not enough. A production-grade options trading system must prove positive expectancy **after** brokerage, taxes, fees, slippage, bid-ask spread, latency, data staleness, and execution quality.

A model can show a theoretical hit rate and still lose money if execution friction is too high.

## Non-negotiable production gates

### 1. Friction and expectancy gate

Required proof fields per trading day:

- gross P&L
- brokerage
- STT
- exchange transaction charge
- GST
- SEBI charge
- stamp duty
- slippage
- bid-ask spread cost
- net P&L
- win rate
- average win
- average loss
- profit factor
- expectancy per trade
- expectancy after all costs
- max drawdown
- risk of ruin estimate

Production rule:

```text
Do not allow live trading unless net expectancy after all costs is positive for at least 5 consecutive market sessions and minimum sample size is met.
```

### 2. WebSocket / tick-health gate

REST polling alone is not sufficient for intraday options execution.

Required dashboard/proof fields:

- websocket connected true/false
- last tick timestamp
- tick age milliseconds
- tick drop count
- reconnect count
- order-book/depth available true/false
- REST fallback active true/false
- REST fallback reason
- quote-to-signal latency
- signal-to-order latency
- order-to-fill latency
- total decision latency

Production rule:

```text
If websocket tick health is not proven, no live order execution is allowed.
```

### 3. Option-chain integrity gate

Required checks:

- underlying spot timestamp
- option-chain timestamp
- Greeks timestamp
- spot/chain/Greeks synchronization age
- ATM strike correctness
- bid/ask spread percentage
- depth / volume / OI sufficiency
- stale chain detection
- crossed or invalid bid-ask detection
- IV/Delta sanity range
- spot-price mismatch detection

Production rule:

```text
If spot price and option-chain/Greeks are not synchronized, stop signal generation for options.
```

### 4. Execution-quality gate

Required fields per paper/live-like trade:

- signal id
- candidate id
- quote timestamp
- selected option contract
- bid at signal
- ask at signal
- LTP at signal
- intended entry
- simulated fill
- actual/paper fill
- slippage rupees
- slippage percentage
- spread paid
- entry delay milliseconds
- exit delay milliseconds
- exit reason
- gross P&L
- net P&L
- proof status

Production rule:

```text
Live trading remains blocked if slippage and spread cost are not measured and inside approved limits.
```

### 5. No-trade matrix gate

A no-trade decision must explain exact blocked condition.

Required gate rows:

- market session
- broker connectivity
- websocket tick freshness
- REST fallback status
- data source truth
- option-chain freshness
- spread gate
- liquidity gate
- OI gate
- IV/Delta sanity gate
- risk gate
- daily loss gate
- model confidence gate
- correlation / regime gate
- paper lifecycle gate

### 6. Model-to-trade gap gate

A prediction model is not production-ready unless forecast accuracy translates into executed trade profitability.

Required proof:

- prediction hit rate
- paper trade win rate
- net expectancy
- false positives
- false negatives
- missed opportunities
- average adverse excursion
- average favorable excursion
- calibration drift
- regime-wise performance
- symbol-wise performance

Production rule:

```text
A high prediction hit rate cannot override negative trade expectancy.
```

### 7. Strategy quarantine rule

The system must auto-quarantine any strategy when:

- net expectancy <= 0 after costs
- win rate below minimum threshold and reward/risk insufficient
- slippage exceeds allowed limit
- spread exceeds allowed limit
- websocket/tick health is missing
- proof data is dry-run or simulated
- sample size is too small

### 8. Render/cloud readiness gate

Required proof:

- backend startup binds to host 0.0.0.0 and the dynamic PORT
- `/api/health` responds quickly without waiting for heavy model loading
- worker logs prove scheduler/token-daemon/watchdog started
- API uptime and latency are recorded
- cold-start delay is measured
- errors are captured in proof logs

### 9. Safety gate

Live trading must remain impossible unless all of the following are true:

- human approval true
- live toggle true
- broker live order wrapper implemented and audited
- all proof gates pass
- kill switch false
- daily risk limit configured
- max order size configured
- max loss and max drawdown gates configured

Default state must remain:

```text
PAPER / ANALYZER ONLY
LIVE DISABLED
ORDER PLACEMENT BLOCKED
```

## Minimum production-ready dashboard cards

The dashboard must show:

1. Broker truth
2. WebSocket tick health
3. Data source truth
4. Chain freshness
5. Spread/liquidity gate
6. Strategy expectancy after costs
7. Paper lifecycle proof
8. Execution latency
9. Slippage and charges
10. Model-to-trade gap
11. No-trade reason matrix
12. Proof gate matrix
13. Safety / kill switch
14. Daily risk and drawdown

## Required next implementation package

Create or extend proof reports:

- `reports/latest/system3_truth_bridge/latest.json`
- `reports/latest/execution_quality/summary.json`
- `reports/latest/friction_expectancy/summary.json`
- `reports/latest/websocket_tick_health/summary.json`
- `reports/latest/option_chain_integrity/summary.json`
- `reports/latest/no_trade_matrix/summary.json`
- `reports/latest/model_to_trade_gap/summary.json`

## Production verdict format

Every run must output:

```json
{
  "analyzer_ready": true,
  "paper_ready": true,
  "live_ready": false,
  "trade_ready": false,
  "reason": "Real market paper lifecycle and positive net expectancy not proven"
}
```

## Final rule

A system that loses money after costs in paper mode is not a broker problem, dashboard problem, or model-loader problem. It is a production strategy failure until proven otherwise with costed, latency-aware, live-session paper evidence.
