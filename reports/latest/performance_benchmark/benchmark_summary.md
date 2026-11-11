# Prediction Benchmark Summary — Issue #26 Proof

_Generated 2026-11-12T02:19:13.252263_

- Dependency gate (today's validate run): ⚠️ daily_gain_validate has never run (no scheduler state found)
- Trading days with validation data: **6**
- Date range: 2026-06-12 → 2026-11-09
- Average Spearman ρ: **0.660**
- Average hit rate: **70.6%**
- Days that fired a retrain signal: 1/6

## Daily Scorecard

| Date | Predicted Top | Actual Top | Spearman ρ | Hit Rate | Status |
|------|---------------|------------|------------|----------|--------|
| 2026-06-12 | NIFTY MIDCPNIFTY FINNIFTY | NIFTY BANKNIFTY FINNIFTY | -- | 66.7% | RETRAIN_NEEDED |
| 2026-11-03 |  |  | -- | 70.0% | PASS |
| 2026-11-04 |  |  | -- | 72.0% | PASS |
| 2026-11-05 |  |  | -- | 69.0% | PASS |
| 2026-11-06 |  |  | -- | 71.0% | PASS |
| 2026-11-09 |  |  | -- | 75.0% | PASS |

## Readiness Gate (per master roadmap)
- Threshold: Spearman ρ ≥ 0.70 required for live-trading readiness
- Current average: 0.660
- **Verdict**: BELOW THRESHOLD — more trading days of data needed, or model retrain required