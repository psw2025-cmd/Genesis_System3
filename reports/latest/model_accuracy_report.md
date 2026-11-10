# System3 Model Accuracy Report

Generated UTC: `2026-10-29T10:19:23.666606+00:00`

## Summary

- **Sources**: `api:/api/gain_rank`
- **Rows**: `4`
- **Proof pass count**: `0`
- **Blocked count**: `4`
- **Direction known count**: `0`
- **Direction hit rate**: `None`

## Accuracy Rows

| Symbol | Type | Direction | CE/PE | Confidence | Strike | 5m | 15m | 30m | EOD | Direction Correct | Option Profitable | Proof | Blocker |
|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|
| `NIFTY` | `INDEX` | `DOWN` | `PE` | `61.09` | `` | `None` | `None` | `None` | `None` | `None` | `None` | `BLOCKED` | `STRIKE_NOT_LINKED;ACTUAL_OUTCOME_WINDOW_MISSING` |
| `FINNIFTY` | `INDEX` | `DOWN` | `PE` | `59.89` | `` | `None` | `None` | `None` | `None` | `None` | `None` | `BLOCKED` | `STRIKE_NOT_LINKED;ACTUAL_OUTCOME_WINDOW_MISSING` |
| `MIDCPNIFTY` | `INDEX` | `DOWN` | `PE` | `35.32` | `` | `None` | `None` | `None` | `None` | `None` | `None` | `BLOCKED` | `STRIKE_NOT_LINKED;ACTUAL_OUTCOME_WINDOW_MISSING` |
| `BANKNIFTY` | `INDEX` | `DOWN` | `PE` | `31.71` | `` | `None` | `None` | `None` | `None` | `None` | `None` | `BLOCKED` | `STRIKE_NOT_LINKED;ACTUAL_OUTCOME_WINDOW_MISSING` |

## Pass Rule

Model accuracy is not proven until 5+ market days include prediction-before-move timestamps, option-mapped strike/token proof, and actual 5m/15m/30m/EOD outcomes.
