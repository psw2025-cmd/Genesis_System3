# Online Research Source Map and Gap Protocol

**Purpose:** Ensure agents do full online/source-based discovery instead of waiting for the user to point out small missing requirements.

**Applies to:** Claude, Cursor, Gemini, Codex, ChatGPT, and future System3 agents.

**Safety rule:** Online research can create requirements and proof tasks, but must not enable live trading.

---

# Core rule

For market/trading/dashboard/broker gaps, the agent must not rely only on local repo inspection or user examples.

Before claiming a gap family is complete, agent must search and compare against authoritative online sources:

```text
exchange sources
clearing sources
regulator sources
broker API docs
market data docs
professional broker/dashboard UX examples
options education/specification sources
global options infrastructure sources
current news/regulatory changes
```

The agent must record:

```text
source checked
what source proves
System3 gap found
required proof artifact
required dashboard field
required backend/ledger field
status
```

---

# Required source categories

## SRC1 — NSE equity derivatives official source checks

Agents must check NSE official sources for:

- contract specifications
- list of underlyings
- F&O stock introduction/exclusion tracker
- stock option strike scheme
- quantity freeze list
- permitted lot size list
- market timings and holidays
- price bands
- corporate action adjustments
- derivatives market reports
- circulars

System3 gaps to derive:

- contract master freshness
- F&O eligibility
- lot-size validation
- strike-step validation
- freeze quantity validation
- expiry/calendar validation
- corporate-action contract adjustment
- trading session/holiday validation

Required artifacts:

```text
reports/latest/online_source_validation/nse_contract_source_map.json
reports/latest/contract_master_freshness/summary.json
reports/latest/fno_eligibility/summary.json
reports/latest/contract_spec_validation/summary.json
```

Status: `REQUIRES_CONTINUOUS_ONLINE_CHECK`.

---

## SRC2 — NSE Clearing / risk / MWPL source checks

Agents must check official clearing/risk sources for:

- market-wide position limit
- margins
- SPAN/risk parameter files
- client margin reporting
- violations
- settlement schedule
- settlement price
- settlement mechanism
- securities transaction tax
- FII/MF position limits

System3 gaps to derive:

- F&O ban/MWPL gate
- margin gate
- settlement risk gate
- STT/charges gate
- position limit gate
- violation/surveillance gate

Required artifacts:

```text
reports/latest/online_source_validation/nse_clearing_source_map.json
reports/latest/fno_ban_mwpl_gate/summary.json
reports/latest/margin_and_settlement_gate/summary.json
reports/latest/fee_tax_rule_monitor/summary.json
```

Status: `REQUIRES_CONTINUOUS_ONLINE_CHECK`.

---

## SRC3 — SEBI regulator source checks

Agents must check SEBI official circulars, consultation papers, and studies for:

- equity derivatives framework changes
- weekly expiry limitations
- contract-size/lot-size rules
- upfront option premium requirements
- expiry-day risk control
- retail F&O loss studies
- algorithmic trading requirements
- broker compliance requirements
- investor risk disclosures
- market manipulation/surveillance updates

System3 gaps to derive:

- regulatory rule monitor
- expiry rule monitor
- lot size rule monitor
- retail-loss risk warning
- algo governance rules
- live enablement approval policy
- audit/compliance logs

Required artifacts:

```text
reports/latest/online_source_validation/sebi_source_map.json
reports/latest/regulatory_rule_monitor/summary.json
reports/latest/expiry_rule_monitor/summary.json
reports/latest/live_enablement_governance/summary.json
```

Status: `REQUIRES_CONTINUOUS_ONLINE_CHECK`.

---

## SRC4 — Broker API documentation source checks

Agents must check broker API docs, initially DhanHQ for current System3, and later any active broker.

Mandatory Dhan/API sections to compare:

- authentication
- orders
- orderbook
- tradebook
- holdings
- positions
- funds and margin
- market quote
- live market feed
- full market depth
- option chain
- instrument list
- rate limits
- postbacks/live order updates

System3 gaps to derive:

- broker-shape parity
- paper ledger shape parity
- real read-only portfolio view
- quote/depth/OI/volume mapping
- option chain mapping
- order/trade lifecycle mapping
- rate-limit and outage handling
- token watchdog

Required artifacts:

```text
reports/latest/online_source_validation/broker_api_source_map.json
reports/latest/portfolio_parity/broker_shape_parity.json
reports/latest/broker_quote_depth_mapping/summary.json
reports/latest/broker_order_tradebook_mapping/summary.json
```

Status: `REQUIRES_BROKER_DOC_SYNC`.

---

## SRC5 — Option-chain and options-pricing education/specification source checks

Agents must check credible sources for:

- option premium = intrinsic + extrinsic value
- call/put definitions
- strike price
- expiry
- settlement
- exercise style
- Greeks: delta, gamma, theta, vega
- implied volatility
- moneyness
- volume vs open interest
- bid/ask spread
- assignment/exercise risk
- margin risk

System3 gaps to derive:

- premium decomposition
- Greeks validation
- IV regime gate
- moneyness/break-even gate
- executable quote gate
- OI/volume interpretation
- settlement/exercise classification

Required artifacts:

```text
reports/latest/online_source_validation/options_pricing_source_map.json
reports/latest/option_premium_decomposition/summary.json
reports/latest/greeks_validation/summary.json
reports/latest/iv_regime/summary.json
```

Status: `REQUIRES_MODEL_AND_UI_MAPPING`.

---

## SRC6 — India market-impact source checks

Agents must check online/current sources for:

- RBI/MPC calendar
- Fed/FOMC calendar
- Indian CPI/WPI/IIP/GDP/Budget/election events
- USD/INR
- crude oil
- gold/risk-off proxy
- US indices
- Asian markets
- GIFT Nifty
- FII/DII flows
- India VIX
- sector indices
- corporate results/earnings
- corporate actions
- index rebalancing
- news shocks
- exchange holidays
- trading-hour/session changes

System3 gaps to derive:

- macro event calendar
- pre-market global cue score
- FII/DII flow engine
- India VIX regime
- sector regime
- news shock gate
- holiday/session gate

Required artifacts:

```text
reports/latest/online_source_validation/india_market_impact_source_map.json
reports/latest/macro_event_calendar/summary.json
reports/latest/global_cue_score/summary.json
reports/latest/india_vix_regime/summary.json
reports/latest/fii_dii_flow/summary.json
```

Status: `REQUIRES_DAILY_ONLINE_REFRESH`.

---

## SRC7 — Professional dashboard UX source checks

Agents must compare System3 dashboard with broker/professional trading dashboard patterns:

- portfolio screen
- holdings screen
- positions screen
- orderbook
- tradebook
- quote panel
- option-chain panel
- P&L card
- today vs total P&L
- current value
- avg buy price
- quantity/lots
- data freshness
- connectivity warning
- action buttons
- disabled reason
- news tab
- tax/charges tab

System3 gaps to derive:

- dashboard portfolio parity
- paper/real portfolio separation
- option contract visibility
- broker-style position cards
- action blocker reasons
- stale data warning

Required artifacts:

```text
reports/latest/online_source_validation/dashboard_ux_source_map.json
reports/latest/dashboard_portfolio_parity/tab_coverage.json
reports/latest/options_dashboard_contract_visibility/top_summary_status.json
reports/latest/portfolio_parity/dashboard_card_coverage.json
```

Status: `REQUIRES_UI_PARITY_AUDIT`.

---

## SRC8 — Global options infrastructure source checks

If System3 ever expands beyond India, agents must research:

- OCC clearing rules for US listed options
- Cboe option product specifications
- CME futures options specifications
- exchange calendars and holidays
- settlement/exercise style
- assignment risk
- multipliers and contract specs
- currency and FX conversion
- data entitlement requirements
- broker permissions/margin

System3 gaps to derive:

- global market adapter layer
- product taxonomy
- settlement/exercise engine
- assignment risk engine
- FX and currency gate
- data entitlement gate

Required artifacts:

```text
reports/latest/online_source_validation/global_options_source_map.json
reports/latest/global_market_adapter/summary.json
reports/latest/settlement_exercise_risk/summary.json
reports/latest/data_entitlement_gate/summary.json
```

Status: `NOT_IMPLEMENTED_FOR_GLOBAL_OPTIONS`.

---

# Online research batch output format

Every online research batch must produce a table:

| Source category | Source URL/domain | What was checked | Gap found | System3 requirement | Artifact needed | Status |
|---|---|---|---|---|---|---|

Every finding must be classified:

```text
NEW_GAP
CONFIRMED_EXISTING_GAP
CHANGED_RULE
STALE_ASSUMPTION
NEEDS_OFFICIAL_CONFIRMATION
NO_ACTION
```

---

# Mandatory recurring refresh rules

Some sources must be checked regularly:

| Source type | Refresh frequency |
|---|---|
| broker token/connectivity | every runtime start and heartbeat |
| quote/option-chain data | live/intraday |
| F&O ban/MWPL | every market day before signal selection |
| contract master / instrument list | every market day before market open |
| holidays/session changes | weekly + before expiry |
| SEBI/NSE circulars | daily/weekly depending on automation capability |
| expiry/lot-size rules | daily until stable, then weekly plus circular watcher |
| macro/event calendar | daily before market open |
| broker API docs | on version change and monthly review |

---

# Fail-closed rule for online source gaps

If online source data is missing or stale, System3 must not assume.

Use status:

```text
ONLINE_SOURCE_NOT_CHECKED
OFFICIAL_SOURCE_NOT_PROVEN
SOURCE_STALE
RULE_CHANGE_UNVERIFIED
```

and block production readiness.

---

# Current known authoritative source examples

These are examples of source classes agents must verify and keep fresh, not a permanent complete list:

- NSE equity derivatives contract information and downloadable CSVs for permitted lot size, quantity freeze, stock option strike scheme, and underlyings.
- NSE Clearing/risk pages for margins, settlement, STT, position limits, MWPL.
- SEBI circulars/studies for equity derivative rule changes and individual F&O risk.
- DhanHQ API docs for holdings, positions, orderbook, tradebook, market quote, option chain, instrument list, and rate limits.
- Current financial news only as supplementary evidence for regulatory/market changes; official source must be preferred where available.

---

# Final instruction

Agents must not wait for the user to say:

```text
show CE/PE
show strike
show current value
show paper vs real portfolio
show quote stale warning
show F&O ban
show expiry change
```

Those must be discovered from online sources, broker docs, exchange specs, and dashboard parity checks automatically.

Current batch complete. More gaps may exist. Next batch should inspect current repo implementation against this online source map and create missing source-validation proof scripts.
