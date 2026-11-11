# System3 Model Accuracy Register

## Purpose

This file defines how System3 proves model/ranker accuracy. A score, dashboard badge, or one-day result is not enough.

System3 must prove that each prediction happened before the move and must compare predictions against actual market outcomes.

## Required Prediction Record

Every prediction must have:

| Field | Required |
|---|---|
| Prediction timestamp IST | Yes |
| Symbol / underlying | Yes |
| Symbol type | INDEX / EQUITY / UNKNOWN |
| Direction | UP/DOWN/CE/PE/LONG/SHORT |
| Confidence / score | Yes |
| Feature snapshot reference | Yes |
| Data source and freshness | Yes |
| Option eligibility status | Yes |
| Selected expiry/strike/token if trade candidate | Yes |
| Market price at prediction | Yes |
| Outcome window 5m | Yes when data available |
| Outcome window 15m | Yes when data available |
| Outcome window 30m | Yes when data available |
| Outcome EOD | Yes when data available |
| Max favorable move | Yes |
| Max adverse move | Yes |
| Direction correct | Yes |
| Option contract profitable | Yes when mapped |
| Rejection/blocker reason | Yes if not traded |

## Required Daily Metrics

| Metric | Meaning |
|---|---|
| Prediction count | Number of pre-move predictions |
| Valid option candidate count | Predictions that passed option tradability |
| Direction hit rate | Percent correct direction |
| Option profitability hit rate | Percent where mapped option would be profitable |
| Spearman rank correlation | Rank score vs actual market gain |
| False positive count | High-confidence signal that failed |
| False negative count | Valid move missed by system |
| Missed valid option opportunities | Strong valid option moves not selected |
| Cash-only movers | Strong movers excluded correctly |
| Selection regret | Better valid option candidate existed but not selected |
| Timing error | Signal too early/late |
| Data blocker count | Missing data prevented proof |

## Required Reports

| Output | Purpose |
|---|---|
| `reports/latest/model_accuracy_report.md` | Human summary |
| `reports/latest/model_accuracy_report.json` | Machine-readable summary |
| `reports/history/model_accuracy_YYYYMMDD.json` | Daily historical proof |

## Pass Criteria

System3 model/ranker can only be marked `PROVEN_PAPER_READY` when all are true:

1. At least 5 market days of daily prediction-vs-actual reports exist.
2. Predictions are timestamped before the measured move.
3. Valid option candidates are separated from cash-only movers.
4. Ranker selections are compared against rejected valid candidates.
5. Option contract profitability is evaluated, not only underlying direction.
6. Data and execution blockers are separately counted.
7. No unresolved CRITICAL blocker remains in `SYSTEM3_BLOCKER_REGISTER.md`.

## Current Status

| Area | Current status |
|---|---|
| Multi-day accuracy proof | OPEN |
| Prediction-before-move ledger | OPEN |
| Option-mapped profitability proof | OPEN |
| Rejected candidate comparison | OPEN |
| Cash-only vs option-valid classification | OPEN |
| Dashboard accuracy proof | OPEN |

## False Pass Prevention

Do not call the model accurate because:

- one prediction was correct,
- dashboard shows a green badge,
- confidence score is high,
- underlying moved in expected direction after signal without pre-move timestamp proof,
- cash-only mover is counted as an option miss,
- strike/token mapping is missing.

## Close Condition

The model accuracy blocker can close only after:

```text
5+ trading days of reports + option-mapped outcome proof + no unresolved data/tradability blockers.
```
