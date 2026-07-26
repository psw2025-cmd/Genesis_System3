# Options Big-Data Research

## Current status

- Status: **PARTIAL_WITH_REAL_DATA_SMOKE_PASS**
- Repository tracked files inventoried by the existing control plane: `2,358`
- Existing repository bhavcopy days proven: `5`
- Deterministic planning underlyings: `146` (`140` stock + `6` index)
- Deterministic five-year Dhan request plan: `409,920`
- PR files added: `18`
- Research CLI/analysis scripts: `5`
- Research package modules: `4`
- Focused tests: `11/11 PASS`
- Python compilation: `9/9 PASS`
- Synthetic pipeline smoke: `12,800` input rows → `12,640` feature rows → `3` test days → `6` selected trades
- Synthetic smoke accepted as market-performance proof: `false`

## Real NSE F&O archive proof — 24 July 2026

| Metric | Number |
|---|---:|
| Files downloaded | `1` |
| Total rows | `38,800` |
| File bytes | `1,447,636` |
| Option rows | `38,160` |
| Stock-option rows | `33,020` |
| Index-option rows | `5,140` |
| Futures rows | `640` |
| Option underlyings | `215` |
| Distinct expiries | `18` |
| Distinct strikes | `1,805` |
| CE rows | `18,978` |
| PE rows | `19,182` |
| Positive-volume rows | `20,352` |
| Positive-OI rows | `26,179` |
| Unclassified option rows | `0` |
| Missing files | `0` |
| Hash mismatches | `0` |
| Duplicate rows | `0` |
| Invalid OHLC rows | `0` |
| Negative volume/OI rows | `0` |

File SHA-256:

```text
92646b1e9aebf2de81da1e779709c564762958613caff7706159a5f8777768c6
```

## Still not completed

- Full multi-year market files downloaded: `0`
- Full multi-year market rows downloaded: `0`
- Models trained on the new real dataset: `0`
- Costed backtests run on the new real dataset: `0`
- Live trading: `OFF`
- Order placement: `BLOCKED`
- Model promotion: `BLOCKED`

## Repository-wide inherited CI blocker

- Workflow files scanned: `44`
- Existing policy findings: `70`
- Findings caused by the new options workflow: `0`

The inherited findings are existing write permissions, `git push` operations, and deployment strings in unrelated workflows. They cause the repository's global safety guard to fail before architecture/testing.

## Blockers

1. `DHAN_ACCESS_TOKEN_NOT_AVAILABLE_TO_THIS_EXECUTION_CONTEXT`
2. `CURRENT_DHAN_DETAILED_INSTRUMENT_MASTER_NOT_CAPTURED`
3. `PERSISTENT_MULTI_YEAR_BIG_DATA_TRANSFER_NOT_EXECUTED`
4. `FULL_MULTI_YEAR_DATASET_NOT_PRESENT`
5. `REAL_DATA_MODEL_TRAINING_NOT_EXECUTED`
6. `REAL_DATA_COSTED_BACKTEST_NOT_EXECUTED`
7. `GLOBAL_SAFETY_CI_PREEXISTING_70_WORKFLOW_POLICY_FINDINGS`
