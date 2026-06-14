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

No AI opinion, dashboard green color, or single PASS label is final. If anything is stale, synthetic, fallback, simulated, closed-market, unproven, missing-token, not liquid, not reconciled, or not costed, Claude must mark it `NOT_PROVEN / PASS_WITH_WARNINGS / BLOCKED` and must not mark it production-ready.

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
| 2026-06-14 23:25 | ChatGPT | external market research + repo baseline | option price microstructure batch 3 | Added why option-chain prices rise/fall and the missing System3 proof/gates required to model it | this file | DONE |

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
6. Broker proof: quote access, orderbook, tradebook, positions, token watchdog.
7. Ultra dashboard truth command center.
8. Risk-first execution.
9. Proof-first governance.
10. Self-learning loop.
11. Fail-closed production.

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

Option premium is not moved by one thing. It is the market price of a contract containing:

```text
option premium = intrinsic value + extrinsic/time value
```

Intrinsic value depends on spot/underlying vs strike. Extrinsic value depends on time remaining, implied volatility, supply/demand, event risk, liquidity, and rates/dividends where applicable.

## 1. Underlying price movement

| Situation | Call option | Put option | Required System3 check |
|---|---|---|---|
| Underlying rises | Usually rises | Usually falls | live spot/underlying tick + option tick correlation |
| Underlying falls | Usually falls | Usually rises | live spot/underlying tick + option tick correlation |
| Underlying flat | May fall due theta or IV crush | May fall due theta or IV crush | no-trade if premium decays without directional edge |

**Gap:** System3 must not infer option price direction from underlying alone. It must also check delta, gamma, IV, spread, time, and liquidity.

## 2. Delta — first-order directional sensitivity

Delta estimates how much option price changes for a change in underlying.

**System3 gap:** every trade candidate must record:

- delta
- delta source
- timestamp
- moneyness bucket: ITM/ATM/OTM
- expected premium move for underlying move

**Required artifact:** `reports/latest/greeks_validation/summary.json`.

## 3. Gamma — acceleration risk/reward

Gamma changes delta as the underlying moves. Gamma is usually highest near ATM and near expiry. This is why ATM/near-expiry options can explode or collapse quickly.

**System3 gap:** no candidate should be ranked high without gamma and expiry-risk classification.

**Required fields:** `gamma`, `gamma_bucket`, `near_expiry_gamma_risk`, `max_expected_premium_acceleration`.

## 4. Theta — time decay

Theta reduces extrinsic value as time passes. Near expiry, time decay can dominate direction if the underlying does not move fast enough.

**System3 gap:** option-buying signals must prove expected move speed is greater than theta decay plus spread and charges.

**Required computation:**

```text
expected_intraday_edge = expected_delta_gain + expected_gamma_gain + expected_vega_gain - theta_decay - spread_cost - charges - slippage
```

Reject if expected edge <= 0.

## 5. Vega and implied volatility

IV affects option premium. Calls and puts can rise even if spot movement is small when IV expands. They can fall despite correct direction when IV crushes after event/news.

**System3 gap:** current scanner must not use only price momentum; it must track IV change and IV rank.

**Required fields:**

- `iv_now`
- `iv_change_1m/5m/15m`
- `iv_rank`
- `iv_percentile`
- `vega`
- `event_iv_crush_risk`

## 6. Moneyness: ITM / ATM / OTM

| Bucket | Behavior | System3 gap |
|---|---|---|
| ITM | more intrinsic, higher delta, lower relative gamma | less explosive but more stable |
| ATM | high gamma, active liquidity, sensitive to direction/IV/time | often best for controlled high-gain scanner |
| OTM | cheap, high % move possible, high expiry risk | reject if no liquidity or unrealistic move required |

**Required gate:** System3 must compute distance-to-strike and required underlying move to break even before entry.

## 7. Bid/ask spread and market depth

An option can show high LTP but be untradeable if bid/ask spread is wide or quantity is thin.

**System3 gap:** LTP alone is not enough. Candidate must have:

- bid
- ask
- bid quantity
- ask quantity
- spread absolute
- spread percent
- depth/liquidity score

Reject if spread is too wide or bid is missing.

## 8. Volume, OI, and OI change

Volume shows current session activity. OI shows open contracts. OI change may suggest build-up/unwinding but must be interpreted with price movement.

**System3 gap:** System3 must classify OI + price behavior:

| Price | OI | Possible interpretation |
|---|---|---|
| Price up | OI up | long build-up / fresh buying interest |
| Price up | OI down | short covering / unwind |
| Price down | OI up | short build-up / writing pressure |
| Price down | OI down | long unwinding |

This interpretation must be proof-tagged, not assumed.

## 9. Event/news volatility

Events can increase IV before the event and crush IV after the event. Correct direction can still lose money if IV crush is larger than directional gain.

**System3 gap:** add event-risk gate:

- earnings/news/economic event
- result day
- RBI/Fed/global macro event
- index rebalancing
- corporate action
- large gap-open risk

## 10. Expiry-day microstructure

Near expiry, option premium becomes extremely sensitive to small underlying moves and time decay. OTM options can go to zero quickly.

**System3 gap:** add special expiry-day mode:

- tighter time stop
- tighter spread rule
- no deep OTM unless exceptional liquidity and momentum
- mandatory real bid/ask
- fast exit rule
- no carry of near-expiry lottery options without proof

## 11. Demand/supply and order book imbalance

Market makers and participants move bid/ask based on underlying, IV, inventory, hedging, and order flow. LTP can jump on a small trade but executable bid may not support exit.

**System3 gap:** add order-book microstructure fields:

- top 5 bid/ask depth where broker supports it
- imbalance ratio
- last trade size
- quote update frequency
- stale quote flag

## 12. Correlation and pair behavior

Index options depend on basket movement. Stock options depend on stock + sector + market. Global options may depend on futures, ETF, FX, rates, or volatility product dynamics.

**System3 gap:** candidate scoring must include market regime and correlation:

- index trend
- sector trend
- stock relative strength
- futures basis where applicable
- global cue risk

---

# Option Price Movement Gaps for System3

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
- net P&L after charges not positive
- no exit liquidity
- no broker reconciliation

---

# Current final statement

All currently known gaps are being collected in this living file. The latest expansion adds option-price microstructure: System3 must understand why option premiums rise/fall before it can safely chase highest controlled gain. The next repo batch must compare current code against OPM3-01 to OPM3-12 and create/patch proof artifacts for every missing capability before any production-ready claim.
