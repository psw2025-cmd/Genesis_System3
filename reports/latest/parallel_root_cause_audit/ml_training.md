# Parallel Audit — ml_training

- Status: **BLOCKED**
- Blockers: `2`

## Findings
- CE/PE historical options training pipeline exists.
- CE/PE contract builder exists.

## Blockers
- Options ML training summary is missing/not published.
- Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.

## Required fixes
- Run options-ml-training-proof workflow with valid Dhan historical data or licensed CSV import.
- ML tab must show score fields from proof JSON, not hardcoded text.
