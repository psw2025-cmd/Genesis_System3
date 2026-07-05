# System3 Current Runtime Truth

## Purpose

This file records current runtime truth. It overrides old reports that say `FINAL`, `COMPLETE`, `READY`, or `PASS` unless those reports are backed by current runtime proof.

## Latest Known Runtime Truth

Source: user-provided `/api/state` JSON on 2026-06-15 around 12:53 IST.

| Field | Latest value | Status |
|---|---|---|
| `mode` | `PAPER` | SAFE |
| `data_source` | `BROKER` | WATCH |
| `market.is_open` | `true` | INFO |
| `broker.broker` | `dhan` | INFO |
| `broker.mode` | `ANALYZER` | SAFE |
| `broker.connected` | `true` | PASS |
| `broker.live_trading_enabled` | `false` | SAFE |
| `broker.order_placement_allowed` | `false` | SAFE |
| `broker.credentials_present` | `true` | INFO |
| `broker.latency_ms` | about `253` in latest proof | PASS |
| `broker.error` | `null` | PASS |
| `positions` | `[]` | SAFE |
| `pnl.total` | `0.0` | SAFE |
| `signals.status` | `NO_TRADE` | INFO |
| `reconciliation.status` | `OK` | PASS |

## Active Runtime Contradiction

| Contradiction | Evidence | Status |
|---|---|---|
| Broker connected but disconnect alerts keep appearing | `broker.connected=true` and latest `BROKER_DISCONNECTED` alert timestamp matches current state timestamp | OPEN |

This is not acceptable for live-readiness. It may be safe in PAPER mode, but it breaks dashboard trust and readiness proof.

## Runtime Truth Rules

1. `/api/broker/status` is the canonical broker connectivity check unless explicitly superseded by a better broker-status service.
2. `/api/state` must not contain fresh disconnect alerts when canonical broker status is connected.
3. Missing broker update data must not be interpreted as disconnected.
4. Alert generation must use threshold, dedupe, and recovery logic.
5. Dashboard UI status must be derived from backend state/proof, not hard-coded pass values.

## Required Runtime Proof Files

| Required output | Purpose | Status |
|---|---|---|
| `reports/latest/system3_blocker_report.md` | Human-readable blocker summary | MISSING |
| `reports/latest/system3_blocker_report.json` | Machine-readable blocker summary | MISSING |
| `reports/latest/option_strike_visibility.md` | PE/CE strike/token proof | MISSING |
| `reports/latest/option_strike_visibility.json` | Machine-readable strike/token proof | MISSING |
| `reports/latest/model_accuracy_report.md` | Prediction-vs-actual proof | MISSING |
| `reports/latest/model_accuracy_report.json` | Machine-readable model accuracy proof | MISSING |
| `reports/latest/markdown_inventory.md` | Documentation inventory and classification | MISSING |
| `reports/latest/documentation_contradictions.md` | Docs claiming pass/final against current blockers | MISSING |

## Safe Runtime Position

Current system can be used only for:

- dashboard observation,
- PAPER/analyzer monitoring,
- blocker finding,
- data/option/model validation.

Current system must not be called:

- live-ready,
- trade-ready,
- fully validated,
- model-proven,
- execution-proven.

## Required Next Runtime Checks

1. Check `/api/state` after alert fix.
2. Check `/api/broker/status` after alert fix.
3. Confirm false `BROKER_DISCONNECTED` alerts stop while connected.
4. Confirm PAPER and order blockers remain unchanged.
5. Confirm signals map to PE/CE expiry/strike/token before paper trade readiness.
