# Agent Proactive Micro Discovery Protocol

**Purpose:** Stop user-driven discovery. The user should not have to point out every missing dashboard, option-chain, broker, risk, or market gap. Agents must proactively search and document gaps before patching.

**Applies to:** Claude, Cursor, Gemini, Codex, ChatGPT, and any future repo agent.

---

# Core rule

When the user gives a goal, the agent must not wait for the user to list all missing details.

The agent must perform independent micro-level forensic discovery across:

```text
repo code
runtime reports
proof artifacts
broker API shape
exchange/market rules
option-chain mechanics
market-impact drivers
dashboard UX parity
risk and execution rules
governance and safety rules
```

The agent must then update the audit files with every gap found.

---

# User expectation

The user's expectation is:

```text
User gives only goal.
Agent discovers all dependencies, gaps, risks, upstream requirements, dashboard fields, proof artifacts, and blocker conditions.
Agent does not rely on user to teach missing pieces.
Agent self-verifies before any action.
```

---

# Required agent behavior before any patch

Before code/design/dashboard/proof work, agent must run this thinking workflow:

```text
1. What is the user goal?
2. What must be true for this goal to be achievable?
3. Which data is needed?
4. Which upstream services/files/APIs are needed?
5. Which market rules affect it?
6. Which broker fields affect it?
7. Which dashboard fields must show it?
8. Which risk gates must block it?
9. Which proof artifacts prove it?
10. What is missing now?
11. What must be added to audit file?
12. What is the safest next patch or test?
```

No patch should happen until steps 1-11 are documented.

---

# Exhaustive micro-gap discovery checklist

## A. Data discovery

Agent must check:

- live quote source
- quote timestamp
- quote age
- stale/fallback/synthetic state
- spot/index quote
- option quote
- bid/ask
- depth
- LTP
- OHLC
- volume
- OI
- IV
- Greeks
- data entitlement/API limitation
- retry/failure path
- rate limits
- data mismatch between endpoints

Required output:

```text
DATA_GAPS_FOUND
DATA_PROOF_REQUIRED
DATA_BLOCKERS
```

---

## B. Option-chain discovery

Agent must check:

- underlying
- exchange
- segment
- instrument token
- option type CE/PE
- expiry
- strike
- strike step
- lot size
- tick size
- freeze quantity
- bid
- ask
- spread
- bid quantity
- ask quantity
- LTP
- OI
- OI change
- volume
- IV
- delta/gamma/theta/vega
- moneyness
- break-even
- theta survival
- expiry-day risk
- event IV crush risk

Required output:

```text
OPTION_CHAIN_GAPS_FOUND
OPTION_CHAIN_PROOF_REQUIRED
OPTION_CHAIN_BLOCKERS
```

---

## C. India market-impact discovery

Agent must check:

- RBI/MPC calendar
- Fed/global macro calendar
- CPI/WPI/IIP/GDP/Budget/election events
- USD/INR
- crude
- gold/risk-off proxy
- US indices
- Asian markets
- GIFT Nifty
- FII/DII flow
- India VIX
- sector rotation
- earnings/results
- corporate actions
- index rebalancing
- F&O ban/MWPL
- circuit/halt/surveillance
- holidays
- expiry rule changes
- lot-size rule changes
- regulatory/SEBI/exchange circulars
- news shock
- market crowding/anomaly

Required output:

```text
MARKET_IMPACT_GAPS_FOUND
MARKET_IMPACT_PROOF_REQUIRED
MARKET_IMPACT_BLOCKERS
```

---

## D. Broker parity discovery

Agent must check broker API shape and System3 paper shape for parity:

- holdings
- positions
- orderbook
- tradebook
- market quote
- option chain
- funds/margin if available
- product type
- average price
- buy quantity
- sell quantity
- net quantity
- realized P&L
- unrealized P&L
- expiry
- strike
- option type
- exchange segment
- token
- quote depth
- OI/volume

Required output:

```text
BROKER_PARITY_GAPS_FOUND
BROKER_PARITY_PROOF_REQUIRED
BROKER_PARITY_BLOCKERS
```

---

## E. Dashboard discovery

Agent must compare System3 dashboard against real broker/professional dashboard expectations:

- production ready YES/NO
- paper ready YES/NO
- broker connected
- live trading disabled
- data source
- last quote time
- quote age
- poor connection/stale/fallback warning
- investment/deployed capital
- current value
- overall P&L
- today P&L
- realized P&L
- unrealized P&L
- net P&L after costs
- holdings/positions summary
- average buy price
- lots/quantity
- option position card
- bid/ask/spread/OI/volume/IV/Greeks
- stop/target/trailing/time exit
- orderbook/tradebook
- event/news/macro tab
- age/tax/charges tab
- exact blocker if action disabled

Required output:

```text
DASHBOARD_GAPS_FOUND
DASHBOARD_PROOF_REQUIRED
DASHBOARD_BLOCKERS
```

---

## F. Risk discovery

Agent must check:

- max loss per trade
- max daily loss
- position size
- lot size
- premium exposure
- margin
- slippage
- spread
- liquidity
- theta decay
- gamma risk
- event IV crush
- gap risk
- expiry risk
- no-exit risk
- kill switch
- max consecutive losses
- capital protection
- live disablement

Required output:

```text
RISK_GAPS_FOUND
RISK_PROOF_REQUIRED
RISK_BLOCKERS
```

---

## G. Execution discovery

Agent must check:

- signal-to-order path
- paper order creation
- fill model
- mark-to-market
- modify/cancel
- exit logic
- stop loss
- target
- trailing
- time stop
- order status refresh
- broker orderbook reconciliation
- tradebook reconciliation
- position reconciliation
- charges/slippage
- net P&L
- audit event IDs

Required output:

```text
EXECUTION_GAPS_FOUND
EXECUTION_PROOF_REQUIRED
EXECUTION_BLOCKERS
```

---

## H. Proof/governance discovery

Agent must check:

- proof matrix
- full pipeline readiness
- lifecycle proof
- dashboard proof
- browser/DOM proof
- API-vs-report reconciliation
- report-vs-DB reconciliation
- real market vs weekend/closed proof
- fallback/synthetic detection
- model promotion policy
- live enablement policy
- rollback
- user approval
- audit trail

Required output:

```text
PROOF_GAPS_FOUND
GOVERNANCE_GAPS_FOUND
FINAL_BLOCKERS
```

---

# Mandatory audit update behavior

After every discovery batch, agent must update one of these files:

```text
docs/AI_PRODUCTION_READINESS_FINDINGS.md
docs/DASHBOARD_PORTFOLIO_PARITY_GAP_MATRIX.md
docs/AGENT_PROACTIVE_MICRO_DISCOVERY_PROTOCOL.md
```

If the gap is new, create a specific gap ID.

Gap ID format:

```text
DATA#
OPT#
MKT#
OPM#
DASH#
BROKER#
RISK#
EXEC#
PROOF#
GOV#
```

Each gap must include:

```text
Gap ID
Description
Why it matters
Current evidence
Current status
Required proof artifact
Required patch/test
```

---

# Stop condition

Agent may stop only after creating a clear next-batch plan. It must not claim all gaps are found permanently. Market structure, broker APIs, exchange rules, and dashboard expectations can change.

Use this wording:

```text
Current batch complete. More gaps may exist. Next batch should inspect <specific area>.
```

---

# Final instruction

Do not make the user spoon-feed missing requirements.

The system must behave like a forensic engineer:

```text
Goal received → discover missing layers → prove current state → record gaps → then patch.
```
