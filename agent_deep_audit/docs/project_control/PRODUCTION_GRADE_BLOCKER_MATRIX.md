# System3 Production-Grade Blocker Matrix

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
Current blocker procedure: `docs/SYSTEM3_CURRENT_BLOCKER_RUNBOOK.md`.

## Important status rule

This document defines **blocker categories and proof requirements**. It does not permanently assert which blockers are open/closed now.

Any row's current status must be recomputed from new authoritative evidence for the present investigation. Historical reports, `reports/latest/`, previous workflow results, or earlier screenshots may establish past state only.

## Production-grade categories

| Area | Current-state question | Required fresh/current proof |
|---|---|---|
| Deployment | What revision/SHA serves production now? | Fresh GCP service/revision/traffic metadata |
| Safety | Is LIVE/order authority still disabled? | Fresh runtime/config safety evidence |
| Broker | Is Dhan connected now? | Fresh `/api/broker/status`; token metadata alone is insufficient |
| Health | Is runtime ready/healthy now? | Fresh health/runtime observation |
| Market data | Is required data available/fresh now? | Fresh production API/source provenance + timestamps |
| Option Chain | Are required chains/contracts/strikes actually present now? | Fresh production data + visible production UI proof where UI-facing |
| UI | What does the user actually see now? | New request-scoped GCP production Chrome/WebDriver lifecycle |
| Signals/scanner | Are current candidates/data states truthful? | Fresh data-backed output + provenance; no fabricated candidates |
| Paper lifecycle | Is signal->entry->exit->PnL currently proven? | Current durable records/API/UI reconciliation |
| ML/prediction | What performance is actually proven? | Time-windowed prediction-vs-actual/backtest/walk-forward evidence |
| IAM | What principals can deploy/invoke/repair now? | Fresh GCP IAM/resource-policy query |
| Automation | Are schedulers/jobs/recovery paths currently configured? | Fresh Cloud Scheduler/Run Jobs metadata + bounded execution evidence when applicable |
| Security | Are exact-head security gates satisfied? | Exact relevant source SHA CI/security evidence |

## UI blocker contract

A full current UI audit requires all 22 canonical production tabs captured after the investigation/request starts using `scripts/gcp_live_ui_snapshot.py`.

`22/22 rendered` is only render proof. Semantic data-bearing checks still apply. Visible states such as `—`, `UNKNOWN`, `WAITING`, `LOADING`, `POLL`, `NO DATA`, `DISCONNECTED`, `ERROR`, or `DEGRADED` must be classified in market/session context.

## Evidence freshness contract

- Interactive `now/current/live`: new observation must begin after the current request/investigation starts.
- Scheduled current verdict: evidence must declare capture time and bounded max age.
- Missing/invalid timestamp: `NOT_PROVEN`.
- Stored artifact from an earlier request: `HISTORICAL_EVIDENCE` for current-state purposes.
- New fix/redeploy/recovery: previous evidence cannot prove the post-change state.

Use `scripts/system3_temporal_truth_guard.py` for machine validation.

## Safety rule

System3 remains Analyzer/PAPER by default:

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- no real order mutation
- no secret payload exposure

## Closure law

A category can be called PASS only for the scope and observation time actually proven. A historical PASS is not automatically a current PASS.

For UI-facing fixes, closure requires fresh post-fix production-browser proof plus correlated backend/API truth.
