# Options Dashboard Contract Visibility Requirements

**Purpose:** Ensure System3 dashboard clearly shows equity/stock option and index option contract details: CE/PE, strike, expiry, option symbol, token, lot size, bid/ask, spread, OI, volume, IV, Greeks, and contract validity.

**Safety rule:** This is dashboard/proof visibility only. It does not enable live trading.

---

# Core issue

The user reported that dashboard does not clearly show:

```text
equity option strike
CE / PE
selected option contract
```

This is a serious dashboard and upstream data gap.

If System3 predicts or paper-trades options, user must see exactly which option contract is involved.

---

# OPTD7-01 — Option contract identity must be visible

Every option signal, candidate, paper trade, and position must show:

- underlying symbol
- underlying type: INDEX / EQUITY_STOCK / ETF / FUTURE_UNDERLYING if global later
- exchange
- segment
- F&O eligible: YES/NO
- contract trading symbol
- instrument token
- CE/PE
- strike
- expiry
- lot size
- quantity
- lots
- tick size
- freeze quantity where available
- source of contract master
- contract master timestamp

Required dashboard columns:

```text
Underlying | Type | CE/PE | Strike | Expiry | Lot | Qty | Token | Contract Symbol | Valid?
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/contract_identity.json
```

Status: `BLOCKER` until visible.

---

# OPTD7-02 — Equity stock options must be separated from cash equity

A cash equity symbol must not be displayed as if it is option-tradable.

Dashboard must classify every symbol as:

```text
CASH_ONLY
FNO_EQUITY_OPTION_ELIGIBLE
INDEX_OPTION_ELIGIBLE
UNKNOWN_NEEDS_PROOF
```

If a stock is not in F&O universe, dashboard must show:

```text
NO OPTION CONTRACT — CASH ONLY / REJECTED FOR OPTION TRADE
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/fno_eligibility_classification.json
```

Status: `BLOCKER`.

---

# OPTD7-03 — Selected strike must be shown with reason

For each option candidate, dashboard must show why this strike was selected:

- ATM / ITM / OTM bucket
- distance from spot
- strike step validation
- expected move required
- break-even
- liquidity score
- spread score
- OI/volume score
- delta/gamma opportunity
- theta survival score
- expiry risk score
- risk/reward

Required card:

```text
Selected Strike Explanation
```

Required fields:

```text
spot_price
selected_strike
strike_distance
moneyness
break_even
required_underlying_move
selection_reason
reject_reason_if_not_selected
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/strike_selection_explanation.json
```

Status: `NOT_PROVEN`.

---

# OPTD7-04 — CE/PE direction and trade side must be explicit

Dashboard must not only show signal type; it must show:

```text
Direction: BULLISH / BEARISH / NEUTRAL
Option Side: CE / PE
Action: BUY / SELL / OBSERVE_ONLY / REJECTED
Paper/Real: PAPER / REAL_READONLY / LIVE_DISABLED
```

Examples:

```text
BULLISH → CE BUY candidate
BEARISH → PE BUY candidate
NEUTRAL → NO_TRADE / OBSERVE_ONLY
```

If the system is not allowed to trade, dashboard must show:

```text
Action: OBSERVE_ONLY
Reason: PAPER_NOT_READY / CONTRACT_NOT_VALID / LIVE_DISABLED / RISK_GATE_FAILED
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/ce_pe_direction_action.json
```

Status: `BLOCKER`.

---

# OPTD7-05 — Option quote panel required

For selected contract, dashboard must show live quote quality:

- LTP
- bid
- ask
- bid quantity
- ask quantity
- spread absolute
- spread percent
- volume
- OI
- OI change
- IV
- delta
- gamma
- theta
- vega
- quote timestamp
- quote age seconds
- quote source
- stale/fallback flag

Required dashboard card:

```text
Option Contract Quote Quality
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/option_quote_quality.json
```

Status: `BLOCKER`.

---

# OPTD7-06 — Option-chain table must be visible for selected underlying

Dashboard must include option-chain table for selected underlying/expiry:

| CE Bid | CE Ask | CE LTP | CE OI | CE Vol | Strike | PE Bid | PE Ask | PE LTP | PE OI | PE Vol |
|---|---|---|---|---|---|---|---|---|---|---|

Additional optional columns:

- IV
- delta/gamma/theta/vega
- spread percent
- liquidity score
- selected row marker
- rejected row reason

Required features:

```text
expiry selector
ATM marker
selected strike highlight
invalid strike warning
liquidity/spread color warnings
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/option_chain_table_coverage.json
```

Status: `FEATURE_GAP / BLOCKER FOR OPTIONS TRUST`.

---

# OPTD7-07 — Paper trade card must show contract details

Any paper order/trade/position must show:

```text
PAPER OPTION POSITION
Underlying
CE/PE
Strike
Expiry
Lot size
Lots
Quantity
Avg premium
Entry quote time
Current bid/ask/LTP
Executable mark price
Current value
Day P&L
Total P&L
SL/Target/Trail
Exit liquidity
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/paper_option_position_card.json
```

Status: `BLOCKER`.

---

# OPTD7-08 — Real broker option position card must show contract details read-only

For real broker read-only positions/holdings, dashboard must show:

```text
REAL BROKER OPTION POSITION — READ ONLY
Underlying
Trading symbol
Token
CE/PE
Strike
Expiry
Product type
Quantity
Avg price
Broker LTP/mark
Realized P&L
Unrealized P&L
Last broker fetch time
Stale flag
Live trading disabled
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/real_option_position_card_readonly.json
```

Status: `NEEDS_BROKER_RUNTIME`.

---

# OPTD7-09 — Option candidate rejection reasons must be visible

When System3 rejects a candidate, dashboard must show exact reason:

- equity is cash-only
- no F&O contract
- no expiry found
- no strike found
- no token
- bid/ask missing
- spread too wide
- OI/volume too low
- quote stale
- Greeks missing
- IV risk too high
- theta risk too high
- expiry risk too high
- risk gate failed
- broker disconnected
- paper disabled
- live disabled

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/rejection_reasons.json
```

Status: `BLOCKER`.

---

# OPTD7-10 — Dashboard top summary must include option visibility status

Dashboard top bar or proof panel must show:

```text
Option Contract Selected: YES/NO
F&O Eligible: YES/NO
CE/PE Visible: YES/NO
Strike Visible: YES/NO
Expiry Visible: YES/NO
Token Proven: YES/NO
Bid/Ask Proven: YES/NO
Liquidity Proven: YES/NO
Paper Option Position Visible: YES/NO
Real Option Position Read-Only Visible: YES/NO
```

Required artifact:

```text
reports/latest/options_dashboard_contract_visibility/top_summary_status.json
```

Status: `BLOCKER`.

---

# Final rule

For any option-related signal/trade, dashboard is incomplete unless user can answer:

```text
Is this equity cash-only or option-tradable?
Is this an index option or equity stock option?
Is it CE or PE?
What strike?
What expiry?
What lot size?
What token?
What bid/ask/LTP?
Why this strike?
Can it be entered/exited?
Why was it rejected if not traded?
```

Until this is visible:

```text
OPTIONS_CONTRACT_VISIBILITY: NOT_PROVEN
DASHBOARD_OPTIONS_TRUST: BLOCKED
```
