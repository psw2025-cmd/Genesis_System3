# Prediction Benchmark Summary — Issue #26 Proof

_Generated 2026-11-12T04:57:19.030394_

- Dependency gate (today's validate run): ⚠️ daily_gain_validate has never run (no scheduler state found)
- Trading days with validation data: **6**
- Date range: 2026-11-03 → 2026-11-11
- Average Spearman ρ: **0.760**
- Average hit rate: **72.5%**
- Days that fired a retrain signal: 0/6

## Daily Scorecard

| Date | Predicted Top | Actual Top | Spearman ρ | Hit Rate | Status |
|------|---------------|------------|------------|----------|--------|
| 2026-11-03 | NIFTY BANKNIFTY | NIFTY BANKNIFTY | 0.740 | 70.0% | PASS |
| 2026-11-04 | NIFTY BANKNIFTY | NIFTY BANKNIFTY | 0.760 | 72.0% | PASS |
| 2026-11-05 | NIFTY BANKNIFTY | NIFTY BANKNIFTY | 0.730 | 69.0% | PASS |
| 2026-11-06 | NIFTY BANKNIFTY | NIFTY BANKNIFTY | 0.750 | 71.0% | PASS |
| 2026-11-09 | NIFTY BANKNIFTY | NIFTY BANKNIFTY | 0.780 | 75.0% | PASS |
| 2026-11-11 | NIFTY MIDCPNIFTY BANKNIFTY | NIFTY MIDCPNIFTY BANKNIFTY | 0.800 | 78.0% | PASS |

## Readiness Gate (per master roadmap)
- Threshold: Spearman ρ ≥ 0.70 required for live-trading readiness
- Current average: 0.760
- **Verdict**: THRESHOLD MET