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
→ option-price microstructure gaps
→ India/global market-impact gaps
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

No AI opinion, dashboard green color, or single PASS label is final. If anything is stale, synthetic, fallback, simulated, closed-market, unproven, missing-token, not liquid, not reconciled, not costed, or not market-context validated, Claude must mark it `NOT_PROVEN / PASS_WITH_WARNINGS / BLOCKED` and must not mark it production-ready.

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
| 2026-06-14 22:25 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | forensic gap framework | Added goal-to-core decomposition | this file | DONE |
| 2026-06-14 22:35 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | original vision gap matrix | Added original System3 design vision vs current implementation gap matrix | this file | DONE |
| 2026-06-14 22:45 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | multi-validation batch 1 | Added backend runtime truth, SSOT, dashboard hardcoded proof, CORS/security, and position reconciliation findings | this file | DONE |
| 2026-06-14 22:55 | ChatGPT | `86d7717b7b7dbab626162cfa6f8e56f8dbad6d01` | Claude start-here protocol | Added explicit intent, unchanged goal, non-confusion levels, and self-verification protocol | this file | DONE |
| 2026-06-14 23:10 | ChatGPT | external market research + repo baseline | market intelligence batch 2 | Added India + global options market gap matrix and System3 requirement impacts | this file | DONE |
| 2026-06-14 23:25 | ChatGPT | external market research + repo baseline | option price microstructure batch 3 | Added why option-chain prices rise/fall and missing System3 proof/gates | this file | DONE |
| 2026-06-14 23:40 | ChatGPT | external market research + repo baseline | India market impact batch 4 | Added India market-impact gap matrix: macro, FII/DII, RBI/Fed, USDINR, crude, VIX, expiry, holiday, sector, news, and F&O-ban effects | this file | DONE |

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
5. Option-price microstructure: know why premium rises/falls before selecting strike.
6. India/global market-impact intelligence: know what can move underlying, IV, liquidity, and expiry behavior.
7. Broker proof: quote access, orderbook, tradebook, positions, token watchdog.
8. Ultra dashboard truth command center.
9. Risk-first execution.
10. Proof-first governance.
11. Self-learning loop.
12. Fail-closed production.

---

# Market Intelligence Batch 2 — India + Global Options Market Gap Matrix

The options market is a live microstructure problem involving contract specs, liquidity, spreads, IV, Greeks, margin, expiry, settlement, broker support, regulation, and execution quality.

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
| Liquidity fragmentation | Multiple exchanges may quote same option | NBBO/best-bid-offer abstraction where applicable |
| Trading halts/outages | Global venues can halt/disrupt trading | Halt/outage detection and kill switch |

---

# Option Price Microstructure Batch 3 — Why option-chain prices rise/fall

## Core formula

```text
option premium = intrinsic value + extrinsic/time value
```

Intrinsic value depends on spot/underlying vs strike. Extrinsic value depends on time remaining, implied volatility, supply/demand, event risk, liquidity, and rates/dividends where applicable.

## Micro price drivers

1. **Underlying price move** — calls usually rise when underlying rises; puts usually rise when underlying falls, but this is not sufficient alone.
2. **Delta** — first-order sensitivity to underlying.
3. **Gamma** — acceleration in delta; high near ATM/expiry.
4. **Theta** — time decay; can destroy option buying if expected move is slow.
5. **Vega/IV** — premium can rise due to IV expansion and fall due to IV crush.
6. **Moneyness** — ITM/ATM/OTM have different delta/gamma/liquidity/risk.
7. **Bid/ask/depth** — LTP is not executable truth.
8. **Volume/OI/OI change** — must be interpreted with price, not alone.
9. **Event/news volatility** — IV can expand before event and crush after event.
10. **Expiry-day microstructure** — gamma/theta extreme; OTM can go to zero quickly.
11. **Order book imbalance** — quote depth and market-maker behavior affect entry/exit.
12. **Correlation/regime** — index, sector, futures, global cues matter.

## Option Price Movement Gaps for System3

| Gap ID | Missing capability | Why it matters | Required artifact/status |
|---|---|---|---|
| OPM3-01 | premium decomposition: intrinsic + extrinsic | Need know whether price move is real direction or just IV/time | `reports/latest/option_premium_decomposition/summary.json` |
| OPM3-02 | live delta/gamma/theta/vega per candidate | Premium can rise/fall for Greeks, not only spot move | `reports/latest/greeks_validation/summary.json` |
| OPM3-03 | moneyness and break-even calculation | Avoid impossible OTM lottery strikes | `reports/latest/moneyness_breakeven/summary.json` |
| OPM3-04 | IV change and IV crush risk | Correct direction can still lose after IV crush | `reports/latest/iv_regime/summary.json` |
| OPM3-05 | spread/depth executable price validation | LTP can be fake/unexecutable | `reports/latest/executable_quote_quality/summary.json` |
| OPM3-06 | OI/volume/OI-change interpretation | OI alone can mislead signal | `reports/latest/oi_volume_interpretation/summary.json` |
| OPM3-07 | expiry-day special risk mode | Gamma/theta extreme near expiry | `reports/latest/expiry_day_risk/summary.json` |
| OPM3-08 | event/news IV risk gate | IV expansion/crush changes premium | `reports/latest/event_iv_risk/summary.json` |
| OPM3-09 | order-book imbalance and quote update frequency | Need know whether premium can be entered/exited | `reports/latest/orderbook_microstructure/summary.json` |
| OPM3-10 | expected edge after theta/spread/charges/slippage | Highest gain must be net profitable, not gross premium movement | `reports/latest/expected_option_edge/summary.json` |
| OPM3-11 | live spot-option tick correlation | Need prove option reacts correctly to underlying | `reports/latest/spot_option_correlation/summary.json` |
| OPM3-12 | regime-aware scoring | Option behavior changes in trend/range/high IV/news/expiry | `reports/latest/market_regime_option_behavior/summary.json` |

---

# India Market Impact Batch 4 — What moves Indian option chain and market

## Why this section exists

Option-chain price movement is downstream of market-impact drivers. System3 must understand what can move the underlying index/stock, implied volatility, liquidity, spreads, OI, volume, and expiry-day behavior.

## Public market findings used

- SEBI/Reuters reported very high individual F&O loss rates and large net losses in FY25, reinforcing fail-closed risk rules.
- SEBI has changed/standardized derivatives expiry rules, and NSE/BSE expiry days can change under regulatory/exchange decisions.
- NSE derivatives activity and equity options remain central to Indian market volume/revenue, so liquidity and crowding risk matter.
- Indian exchanges publish holiday calendars that affect expiry, time decay, liquidity, and pre/post-holiday gaps.
- Options volume and open interest are different liquidity/participation measures and both must be tracked.

## India market-impact gap matrix

| Impact driver | How it can affect market/options | Present System3 gap | Required gate/artifact |
|---|---|---|---|
| RBI policy / MPC | Moves Bank Nifty, INR, yields, rate-sensitive sectors, IV | No formal RBI event calendar gate | `reports/latest/macro_event_calendar/summary.json` |
| US Fed / global rates | Moves global risk appetite, FII flow, USD/INR, gap opens | No global macro calendar integration | `reports/latest/global_macro_impact/summary.json` |
| USD/INR | Impacts IT, pharma, importers, FIIs, inflation sentiment | No FX regime input | `reports/latest/fx_regime/summary.json` |
| Crude oil | Impacts inflation, OMCs, aviation, paint, INR, broad market | No crude/regime input | `reports/latest/commodity_impact/summary.json` |
| US indices / Nasdaq / S&P / Dow | Impacts Indian gap-open and IT/global risk | No pre-market global cue score | `reports/latest/global_cue_score/summary.json` |
| GIFT Nifty | Early cue for Nifty gap/open sentiment | Not proven as live data source | `reports/latest/gift_nifty_cue/summary.json` |
| FII/DII cash flows | Drives index trend, sector rotation, liquidity | No daily flow integration | `reports/latest/fii_dii_flow/summary.json` |
| India VIX / volatility regime | Drives option premium expansion/crush | IV/VIX regime not formalized | `reports/latest/india_vix_regime/summary.json` |
| Earnings/results | Stock options IV expansion/crush, gaps | No earnings calendar gate | `reports/latest/earnings_event_risk/summary.json` |
| Corporate actions | Strike/lot adjustments, price gaps | No corporate-action adjustment proof | `reports/latest/corporate_action_contract_adjustment/summary.json` |
| Index rebalancing | Basket demand/supply, sector/index moves | No index event gate | `reports/latest/index_rebalance_event/summary.json` |
| Sector rotation | Index moves may hide sector winners/losers | No sector-relative strength gate | `reports/latest/sector_regime/summary.json` |
| News/geopolitics | Sudden IV, gaps, liquidity changes | No news shock classifier | `reports/latest/news_shock_gate/summary.json` |
| F&O ban / MWPL | Stock option/future trading can be restricted | No MWPL/F&O-ban gate proven | `reports/latest/fno_ban_mwpl_gate/summary.json` |
| Exchange holidays | Time decay, gap risk, expiry shifts, liquidity | Calendar not proven as hard gate | `reports/latest/exchange_calendar_gate/summary.json` |
| Expiry day rule changes | Changes theta/gamma/liquidity behavior | Expiry assumptions unsafe | `reports/latest/expiry_rule_monitor/summary.json` |
| Lot size changes | Affects position sizing and risk | Lot-size freshness not proven | `reports/latest/lot_size_change_monitor/summary.json` |
| Pre-open/session changes | Price discovery/gaps may change | No session microstructure model | `reports/latest/session_structure_gate/summary.json` |
| Circuit/halt/surveillance | Orders may fail or liquidity vanish | No halt/circuit gate | `reports/latest/circuit_halt_gate/summary.json` |
| Broker/API outages | Data/order proof fails | Broker watchdog exists but incomplete | `reports/latest/broker_outage_watchdog/summary.json` |
| Tax/charges/regulatory changes | Net P&L changes | Static cost assumptions unsafe | `reports/latest/fee_tax_rule_monitor/summary.json` |
| Market manipulation/crowding risk | Index options can be distorted on expiry | No crowding/anomaly detector | `reports/latest/options_crowding_anomaly/summary.json` |

---

# MKT4 required architecture additions

## MKT4-01 — Market impact calendar engine

Create a calendar engine for:

- RBI policy
- Fed policy
- CPI/WPI/IIP/GDP
- Budget/election/major policy events
- earnings/results
- holidays
- expiry days
- corporate actions
- index rebalancing

Status: `NOT_IMPLEMENTED`.

## MKT4-02 — Pre-market global cue engine

Before market open, System3 must score:

- GIFT Nifty
- US indices
- Asian markets
- USD/INR
- crude
- gold/risk-off proxy
- global volatility

Status: `NOT_PROVEN`.

## MKT4-03 — India VIX and IV regime engine

System3 must classify:

- low IV / high IV
- IV expansion
- IV crush risk
- expiry IV abnormality
- event IV risk

Status: `NOT_PROVEN`.

## MKT4-04 — FII/DII and sector flow engine

System3 must track FII/DII flows and sector rotation because options signals should not ignore institutional flow direction.

Status: `NOT_IMPLEMENTED`.

## MKT4-05 — F&O ban / MWPL gate

Stock options/futures candidates must be rejected or downgraded if ban/MWPL/surveillance risk is present.

Status: `NOT_PROVEN`.

## MKT4-06 — News shock / event risk gate

High-impact news must trigger observe-only or reduced-risk mode until spread/liquidity normalizes.

Status: `NOT_IMPLEMENTED`.

## MKT4-07 — Expiry/holiday/session rule monitor

System3 must not hardcode expiry/holiday assumptions. It must monitor exchange calendars and regulatory/exchange circular changes.

Status: `BLOCKER` until current proof artifact exists.

## MKT4-08 — Market crowding/anomaly detector

Because index options can become extremely crowded around expiry, System3 needs anomaly detection for abnormal OI, volume, IV, spread, and spot-option dislocation.

Status: `NOT_IMPLEMENTED`.

---

# Updated highest-controlled-gain option scanner rule

System3 must not rank candidates only by raw option premium % move.

Required score:

```text
controlled_gain_score =
    signal_strength
  × tradability_quality
  × executable_quote_quality
  × liquidity_depth
  × delta_gamma_opportunity
  × iv_regime_score
  × theta_survival_score
  × expiry_risk_score
  × market_impact_score
  × event_risk_score
  × net_edge_after_costs
  × exit_probability
```

Immediate rejection if:

- no valid broker token
- no fresh spot quote
- no fresh option quote
- no bid or no ask
- spread too wide
- OI/volume too low
- IV/Greeks missing without explicit fallback classification
- theta decay greater than expected edge
- expiry risk too high
- event IV crush risk high
- macro/event risk not classified
- F&O ban/MWPL/circuit risk unverified
- holiday/expiry rule stale
- net P&L after charges not positive
- no exit liquidity
- no broker reconciliation

---

# Current final statement

All currently known gaps are being collected in this living file. The latest expansion adds India market-impact intelligence: System3 must account for RBI/Fed/global cues, USD/INR, crude, FII/DII, India VIX, GIFT Nifty, earnings, corporate actions, F&O ban/MWPL, holidays, expiry-rule changes, sector rotation, news shocks, circuit/halt risk, and crowding/anomaly behavior. Highest controlled option gain cannot be pursued safely until market-impact, option-chain, microstructure, broker, risk, proof, and dashboard gaps are all proven in Analyzer/Paper mode.
