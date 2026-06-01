# System3 Brutal Gap Analysis

## Verdict

System3 has useful safety and proof foundations, but it is not yet an institutional autonomous ML trading system. It currently lacks a complete data-to-model-to-runtime control loop.

## Gap matrix

| Pillar | Current state | Institutional requirement | Gap severity |
|---|---|---|---|
| Data ingestion | Not proven as complete nightly full-market pipeline | Scheduled full-day ingestion with validation and lineage | Critical |
| Options chain history | Not proven as complete, clean, partitioned data lake | Full option chain, expiry, strike, IV, OI, liquidity, and lifecycle data | Critical |
| Feature store | Not proven as authoritative | Versioned offline and online feature definitions | Critical |
| Backtesting | Fragmented and not proven as nightly replay engine | Automated daily replay with slippage, fees, and lifecycle truth | Critical |
| Model registry | Not proven | MLflow registry with active and candidate model stages | Critical |
| Model promotion | Not proven | Gated promotion based on walk-forward and paper proof | Critical |
| Hyperparameter tuning | Not proven | Optuna/Ray Tune weekend optimization with anti-overfit gates | High |
| Regime detection | Not proven as authoritative runtime router | Real-time regime classifier and strategy router | High |
| Execution latency | Not proven as low-latency architecture | Async WebSocket pipeline and queue-based execution | High |
| Database writes | Blocking behavior not globally proven safe | Non-blocking persistence queue | High |
| Dashboard truth | Shell and proof dashboards exist | Live truth dashboard with data provenance and latency metrics | High |
| Deployment | GCP proof path added | Runtime-proven backend and controlled cloud deployment | Medium |
| Duplicate files | Inventory exists but cleanup incomplete | Authority map, quarantine, and deletion only after proof | High |

## Current strengths

- Blocking architecture and trading safety gate exists.
- GCP Cloud Run manual proof path exists.
- Backend Docker path proof exists.
- Stale risky PRs were closed.
- Analyzer/paper safety is established as policy.

## Critical failures to fix first

1. No authoritative autonomous ML control plane.
2. No single data lineage contract from raw data to model decision.
3. No model registry and promotion governance.
4. No nightly drift and backtest loop.
5. No proven feature store boundary.
6. No non-blocking event and persistence architecture proof.
7. No complete regime-aware strategy router.
8. No production-grade runtime truth dashboard.

## Non-negotiable standards

System3 must not claim autonomous learning until all are true:

- data has immutable lineage
- backtest is reproducible
- model candidate is versioned
- promotion is gated
- runtime is paper/analyzer safe
- execution path is non-blocking
- dashboard shows real state, not static claims
- stale duplicate files are quarantined before deletion

## Immediate structural recommendation

Build the autonomous ML control plane first. Without it, adding more models, dashboards, or deployment targets increases chaos instead of improving trading intelligence.
