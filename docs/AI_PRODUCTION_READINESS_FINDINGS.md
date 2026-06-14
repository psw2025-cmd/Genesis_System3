# AI Production Readiness Findings

## CLAUDE START HERE — INTENT, GOAL, AND SELF-VERIFICATION PROTOCOL

**Read this section first before any code change, proof run, dashboard change, or readiness claim.**

### User's unchanged goal

```text
Build System3 into a proof-first, option-tradability-aware, broker-reconciled, risk-controlled, self-learning AI trading control system that can eventually seek highest controlled asymmetric gain from the options segment, but only after Analyzer/Paper proof is complete.
```

### What the user expects from Claude/agent

The user may provide only the high-level goal. The agent must perform full forensic discovery and self-check every dependency gap before action:

```text
Goal
→ data gaps
→ signal gaps
→ tradability gaps
→ option-chain gaps
→ broker gaps
→ proof gaps
→ dashboard gaps
→ risk gaps
→ execution gaps
→ governance gaps
→ validated action plan
→ proof artifacts
→ only then patch/action
```

### Non-confusion rule

| Level | Meaning | Can it approve real trading? |
|---|---|---|
| `BROKER_CONNECTED` | Dhan read-only connection appears healthy | No |
| `ANALYZER_READY` | Dashboard/API can observe safely | No |
| `PAPER_READY` | Real market paper lifecycle can run | No live trading |
| `TRADE_READY` | All production proof gates pass | Still needs user approval |
| `LIVE_ENABLED` | Real order placement explicitly allowed | Only after user approval |

No AI opinion, dashboard green color, or single PASS label is final.

If any item is stale, synthetic, fallback, simulated, closed-market, unproven, missing-token, not liquid, or not reconciled, Claude must mark it `NOT_PROVEN / PASS_WITH_WARNINGS / BLOCKED` and must not mark it production-ready.

---

## Communication rule for every chat/update

Every assistant/agent response about this project must include:

```text
Mini summary:
- What I analysed
- What I found
- What I wrote/updated
- What proof supports it
- What I will check next
```

---

## Update log

| Time IST | Agent | Commit/ref checked | Area | Finding/action | Proof path | Status |
|---|---|---|---|---|---|---|
| 2026-06-14 21:58 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | initial audit | Created living production readiness audit file | `docs/AI_PRODUCTION_READINESS_FINDINGS.md` | DONE |
| 2026-06-14 22:25 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | forensic gap framework | Added goal-to-core decomposition: data, signal, tradability, option-chain, broker, proof, dashboard, risk, execution, governance | this file | DONE |
| 2026-06-14 22:35 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | original vision gap matrix | Added original System3 design vision vs current implementation gap matrix | this file | DONE |
| 2026-06-14 22:45 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | multi-validation batch 1 | Added backend runtime truth, SSOT, dashboard hardcoded proof, CORS/security, and position reconciliation findings | this file | DONE |
| 2026-06-14 22:55 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | Claude start-here protocol | Added explicit intent, unchanged goal, non-confusion levels, and self-verification protocol | this file | DONE |
| 2026-06-14 23:10 | ChatGPT | external market research + repo baseline | market intelligence batch 2 | Added India + global options market gap matrix and System3 requirement impacts | this file | DONE |

---

# Current baseline truth

- **Repo:** `psw2025-cmd/Genesis_System3`
- **Baseline main commit inspected:** `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01`
- **Mode:** Analyzer/Paper.
- **Live trading:** Disabled.
- **Order placement:** Blocked.
- **Broker:** Dhan appears connected in latest endpoint coverage proof.
- **Official readiness:** Not trade-ready.
- **Production-grade real trading:** Not ready.

---

# Original System3 design vision

System3 was intended as a complete **AI trading control system**, not only a dashboard or prediction script:

1. Analyzer/Paper before Live.
2. Real data truth.
3. Full signal lifecycle: data → scanner → signal → rank → tradability → paper order → exit → net P&L → learning.
4. Options-first tradability: valid underlying, expiry, strike, token, spread, liquidity.
5. Broker proof: quote access, orderbook, tradebook, positions, token watchdog.
6. Ultra dashboard truth command center.
7. Risk-first execution.
8. Proof-first governance.
9. Self-learning loop.
10. Fail-closed production.

---

# Market Intelligence Batch 2 — India + Global Options Market Gap Matrix

## External market facts checked

The options market is not just an option-chain table. It is a live microstructure problem involving contract specs, liquidity, spreads, IV, Greeks, margin, expiry, settlement, broker support, regulation, and execution quality.

Key public-market findings used for this batch:

1. SEBI/Reuters reported that Indian individual equity-derivative trader losses widened in FY25, with about 91% of individual F&O traders losing money and net losses around ₹1.06 trillion. This proves System3 must be risk-first and fail-closed, not highest-gain-chasing.
2. India is a very large equity derivatives market globally, and index options volume/expiry dynamics can be extreme. This means System3 must handle expiry-day, liquidity, manipulation/surveillance, and volatility risks.
3. SEBI/NSE rules around expiries and lot sizes can change. Any hardcoded expiry day, lot size, strike step, or contract quantity is unsafe.
4. Option-chain analysis requires expiry, strike, call/put side, bid, ask, LTP, volume, open interest, IV, and Greeks. Volume and open interest are not the same; both are required for liquidity and participation validation.
5. Global listed options differ by product type: equity options, index options, ETF options, futures options, cash-settled vs physically settled, American vs European exercise, and different clearing/settlement rules.
6. U.S. listed options are centrally cleared through OCC and global futures/options markets include CME-style futures options; this shows System3 must not assume Indian NSE index-option rules apply globally.

---

## India options market gaps for System3

| Market requirement | Why it matters | System3 current gap | Required proof/gate |
|---|---|---|---|
| NSE/BSE F&O eligibility | Cash stock movers may not be option-tradable | Equity symbols can appear before option tradability is proven | F&O universe file + broker token proof |
| Contract master | Tokens, lot size, expiry, strike, tick size change | Contract metadata not proven as authoritative/fresh | Daily broker/NSE instrument master snapshot |
| Expiry rules | Expiry days and weekly/monthly availability can change | Hardcoded expiry assumptions are unsafe | Exchange calendar + expiry validation artifact |
| Lot size changes | Position size/risk/charges depend on lot size | Lot-size freshness not proven | Contract spec timestamp + lot-size source proof |
| Quantity freeze limits | Large orders can be rejected | Freeze quantity not shown in trade gate | Freeze limit validation before order |
| Strike ladder | Wrong strike step creates invalid orders | Strike validity not proven | Broker option-chain strike validation |
| Bid/ask spread | Wide spread destroys option-buying edge | Spread gate not proven | Bid, ask, spread %, depth snapshot |
| LTP freshness | Stale quote causes fake entry/exit | Quote age not proven everywhere | `quote_ts`, `age_seconds`, stale reject |
| OI + volume | Liquidity and participation require both | OI/volume gating not fully proven | Min OI, min volume, OI-change rules |
| IV and IV rank | High IV can make buying options poor | IV/IV-rank not proven as decision gate | IV source + IV rank/historical IV proof |
| Greeks | Delta/gamma/theta/vega drive option behavior | Greeks not proven for every trade candidate | Greeks snapshot and model/source label |
| Expiry-day theta/gamma | Highest gains/losses often occur near expiry | Expiry-day special risk not formalized | Expiry-day rule set and time stop |
| STT/charges/slippage | Net P&L can reverse after costs | Cost model exists but must be per-contract live | Charges + slippage + net P&L proof |
| Market-wide ban/circuit/news | Stock options can become unsafe | Event/banned/surveillance checks not proven | Ban/circuit/news gate before stock option trade |
| Broker rate limits | Scanner can fail under API limits | Rate-limit backoff proof incomplete | Broker API latency/rate-limit report |

---

## Global options market gaps for System3

| Global requirement | Why India-only logic fails | Required architecture gap closure |
|---|---|---|
| Exchange differences | NSE, BSE, Cboe, CME, OCC-cleared options use different rules | Market adapter layer per exchange |
| Product type | Index, equity, ETF, futures options behave differently | Product taxonomy and contract schema |
| Exercise style | American vs European affects early exercise/assignment | Exercise-style field and risk rules |
| Settlement | Cash-settled vs physical settlement affects expiry risk | Settlement-type gate |
| Currency | Global contracts settle in different currencies | Currency conversion + FX risk gate |
| Time zone | Global markets trade across sessions | Market-calendar/timezone service |
| Clearing/assignment | OCC/CME style clearing differs from Indian index options | Clearing/assignment risk module |
| Margin | Option selling/futures options require margin models | Broker margin simulation/proof |
| Data vendors | Global option chains may need paid entitlements | Data entitlement and fallback detection |
| Corporate actions | Equity options can adjust strikes/multipliers | Corporate-action adjusted contract master |
| Futures options | Underlying is a futures contract, not cash/index spot | Futures-underlying mapping |
| Volatility products | VIX/futures options need separate logic | Product-specific model rules |
| Liquidity fragmentation | Multiple exchanges may quote same option | NBBO/best-bid-offer style abstraction where applicable |
| Trading halts/outages | Global venues can halt/disrupt trading | Halt/outage detection and kill switch |

---

# System3 Market Gap Additions

## MKT2-01 — Contract master freshness is mandatory

System3 must not trade or paper-trade an option unless it has a fresh contract master record proving:

- exchange
- segment
- underlying
- option symbol/trading symbol
- instrument token
- expiry
- strike
- CE/PE
- lot size
- tick size
- freeze quantity
- settlement type
- exercise style where applicable
- source timestamp

**Current status:** NOT_PROVEN for production.

**Required artifact:** `reports/latest/contract_master_freshness/summary.json`.

---

## MKT2-02 — Option-chain quality gate is mandatory

Before any signal becomes trade candidate, option-chain snapshot must prove:

- bid > 0
- ask > 0
- spread <= configured threshold
- LTP fresh
- OI above threshold
- volume above threshold
- IV present or explicitly unavailable
- Greeks present or explicitly unavailable
- quote timestamp not stale

**Current status:** NOT_PROVEN.

**Required artifact:** `reports/latest/option_chain_quality/summary.json`.

---

## MKT2-03 — Expiry and lot-size must not be hardcoded

India expiry and lot-size rules can change. System3 must reject any contract where expiry/lot size is assumed rather than validated from current exchange/broker metadata.

**Current status:** BLOCKER if any hardcoded lot/expiry path exists.

**Required artifact:** `reports/latest/contract_spec_validation/summary.json`.

---

## MKT2-04 — Highest-gain scanner must be risk-adjusted, not raw percentage chasing

A raw highest-gain options scanner will select lottery strikes, illiquid contracts, or late moved premiums. System3 must rank by controlled asymmetric edge:

```text
score = signal_strength
      × tradability_quality
      × liquidity_quality
      × quote_freshness
      × risk_reward
      × execution_probability
      × cost_adjusted_expected_value
```

Reject if any of these fail:

- no valid token
- no bid/ask
- stale quote
- spread too wide
- OI/volume too low
- expiry risk too high
- no stop/exit path
- no net P&L after charges

**Current status:** DESIGN_REQUIRED.

---

## MKT2-05 — Global mode requires market adapter abstraction

System3 must separate Indian options from global options. Global expansion requires adapters for:

- market calendar
- exchange code
- contract schema
- option-chain source
- broker API
- settlement/exercise style
- currency
- fees/taxes
- margin
- clearing/assignment

**Current status:** NOT_IMPLEMENTED for global options.

---

## MKT2-06 — Charges/tax/slippage must be contract-specific

For Indian option buying, net P&L must include premium, brokerage, STT, transaction charges, GST, stamp duty, SEBI/exchange fees where applicable, and slippage. Global markets require different fee/tax models.

**Current status:** PARTIAL; costed backtest exists but live contract-specific cost proof is not complete.

**Required artifact:** `reports/latest/contract_cost_model/summary.json`.

---

## MKT2-07 — Liquidity and spread must be live, not EOD-only

Bhavcopy/EOD can support research, but it cannot prove live intraday tradability. Live trading/paper trading requires intraday quote depth or at least fresh bid/ask/LTP.

**Current status:** BLOCKER for production.

---

## MKT2-08 — Assignment/settlement/exercise risk must be classified

For global options and some stock options, exercise/assignment/physical settlement can matter. Indian index options are generally cash-settled, but global/equity/futures options can differ.

**Current status:** NOT_IMPLEMENTED.

---

# Updated mandatory forensic gap framework

1. **Data gaps** — include market data entitlements, source freshness, intraday quote depth, fallback/synthetic detection.
2. **Signal gaps** — include live signal timestamp, market regime, volatility regime, trend confirmation, no-trade explanation.
3. **Tradability gaps** — include F&O eligibility, token, expiry, strike, lot, freeze quantity, ban/circuit checks.
4. **Option-chain gaps** — include bid/ask/LTP, spread, OI, volume, IV, Greeks, quote age, strike ladder.
5. **Broker gaps** — include quote, orderbook, tradebook, position, margin, API limits, token watchdog.
6. **Proof gaps** — include proof matrix, lifecycle, contract master, option-chain quality, cost model, dashboard reconciliation.
7. **Dashboard gaps** — include production-ready banner, trade-ready truth, data-source blocker, valid-contract status, broker reconciliation.
8. **Risk gaps** — include max loss, daily loss, expiry risk, slippage, spread, liquidity, theta/gamma, margin.
9. **Execution gaps** — include order wrapper, fill model, cancel/modify, exit logic, live quote-based fill, net P&L.
10. **Governance gaps** — include user approval, live enablement policy, model promotion, audit log, fallback rules.

---

# Current final statement

The current System3 is a useful Analyzer/Paper foundation, but India and global options-market analysis expands the gap list: production readiness now also requires contract-master freshness, option-chain quality, live bid/ask/spread/OI/volume/IV/Greeks checks, dynamic expiry/lot-size validation, contract-specific cost/slippage, broker margin/reconciliation, and global market adapter separation. Highest controlled option gain cannot be pursued safely until these gaps are proven in Analyzer/Paper mode.
