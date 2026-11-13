# System3 Signal-to-Trade Control

## Purpose

This file defines the minimum professional control chain before any signal is treated as a paper-trade candidate.

System3 must not treat a symbol as trade-ready only because it has a high signal score. A valid option paper trade requires tradability, contract mapping, quote proof, liquidity proof, and risk proof.

## Required Chain

```text
market scan
  -> candidate symbol
  -> classify index/equity/cash-only
  -> prove option/F&O eligibility
  -> select expiry
  -> select CE/PE side
  -> select strike
  -> map instrument token/security id
  -> fetch quote/LTP/bid/ask/spread
  -> check liquidity and spread
  -> check risk/capital/position limits
  -> create paper order only
  -> reconcile paper order/trade/position/PnL
```

## Gate Table

| Gate | Required proof | If missing |
|---|---|---|
| Symbol classification | Index / equity / cash-only | Block trade readiness |
| F&O/option eligibility | Symbol exists in valid option universe | Mark `OBSERVE_ONLY_CASH_OR_UNKNOWN` |
| Expiry selection | Valid, current, not stale | Block paper trade |
| CE/PE decision | Direction mapped to call/put intent | Block paper trade |
| Strike selection | Strike selected by defined rule | Block paper trade |
| Token/security ID | Broker/NSE contract token found | Block paper trade |
| Quote | LTP available and timestamped | Block paper trade |
| Bid/ask/spread | Spread acceptable or explicitly unavailable with safe fallback | Block or mark simulated |
| Liquidity | Volume/OI/spread threshold pass | Block or observe |
| Risk | Size/SL/TP/trailing/limits pass | Block paper trade |
| Ledger | Order/trade/position/PnL reconcile | Block proof claim |

## Required Report

`reports/latest/option_strike_visibility.md/json` must include one row per latest signal.

Required fields:

| Field | Meaning |
|---|---|
| `signal_ts_ist` | When signal was produced |
| `underlying` | Signal underlying |
| `symbol_type` | INDEX / EQUITY / CASH_ONLY / UNKNOWN |
| `option_eligible` | true/false |
| `eligibility_source` | Dhan/NSE/F&O master/static cache/etc. |
| `signal_side` | BUY/SELL/LONG/SHORT |
| `option_side` | CE/PE/NONE |
| `expiry` | Selected expiry |
| `strike` | Selected strike |
| `instrument_token` | Broker/NSE token/security id |
| `ltp` | Contract LTP |
| `bid` | Bid if available |
| `ask` | Ask if available |
| `spread_pct` | Spread percent if available |
| `liquidity_status` | PASS/WARN/FAIL/UNKNOWN |
| `paper_trade_allowed` | true/false |
| `blocker_reason` | Exact reason if not allowed |

## Current Known Concern

User observed that dashboard may show index-level signal while equity option PE/CE strike visibility is not clear. This must be treated as a critical open blocker until the option visibility report exists.

## Missed Opportunity Classification

Every missed opportunity must be classified as one of:

| Class | Meaning |
|---|---|
| VALID_OPTION_MISS | Option-tradable, token/strike/liquidity valid, but System3 missed it |
| CASH_ONLY_MOVER | Strong equity/cash mover but not valid for options paper trade |
| COLLECTED_NOT_SELECTED | Valid candidate collected but rank/risk/cap rejected it |
| SELECTED_BLOCKED | Selected but blocked by expiry/strike/token/quote/liquidity/risk |
| UNKNOWN_NEEDS_PROOF | Data not enough to classify |

## Non-Negotiable Rule

No signal can become paper-trade-ready unless this exact statement can be proven:

```text
The selected instrument is option-tradable now, with valid expiry, strike, token/security id, quote, and acceptable execution assumptions.
```
