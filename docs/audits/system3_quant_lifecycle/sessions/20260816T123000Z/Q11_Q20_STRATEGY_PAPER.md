# Q11–Q20 — Strategy, Backtest, Paper, Promotion

## Q11 Strategy inventory — **PARTIAL**
Dominant runtime behavior: **analyzer / gain-rank / paper surfaces**, not uncontrolled live order strategies.
Classify broadly:
| Family | Class |
|--------|-------|
| Gain-rank selection | ACTIVE_RUNTIME (analyzer) |
| Paper trade UI/flows | PAPER_ONLY / PARTIAL |
| Ultra/phase strategy menus | EXPERIMENTAL / BACKTEST_ONLY / DEAD_CODE mix |
| Live auto-execute | **DISABLED** (`LIVE_TRADING_ENABLED=false`, orders false) |

Duplicate strategy names under phases: known risk — treat as UNKNOWN until file-level dedupe pass.

## Q12 Best-strategy search — **NOT_PROVEN**
No evidence-based tournament selecting “best” with OOS expectancy + regime robustness as SSOT.

## Q13 Backtest — **PARTIAL / NOT_PROVEN**
Mechanics/tooling exist; institutional requirements (full costs, no future OC knowledge, realistic fills, leakage gate) historically **`walk_forward_cost_slippage_proven: false`**.
Options contract existence checks: incomplete for full universe.

## Q14 Walk-forward / robustness — **MISSING / NOT_PROVEN** as production gate.

## Q15 Prediction vs actual — **PARTIAL**
Validator writes history; `/api/accuracy_trend` exposes rolling summary.
Durable `prediction_id` ledger with model_version/strategy_version on every prod prediction: **INCOMPLETE**.

## Q16 Self-learning (safe definition) — **PARTIAL**
Retrain signal → `auto_retrain.py` is controlled; does **not** allow uncontrolled self-mod.
Champion overwrite on single failure: blocked by design intent.

## Q17 Champion/challenger — **MISSING**
No MLflow-style registry with hash, rollback, independent promotion record.

## Q18 Self-correction taxonomy — **PARTIAL / NOT_PROVEN**
Error class routing (DATA/FEATURE/MODEL/REGIME/…) not fully operationalized in UI/API.

## Q19 Paper/simulation — **PARTIAL**
Paper tabs/APIs exist; continuous market-day lifecycle proof still a known gap (`REAL_PAPER_LIFECYCLE_NOT_PROVEN` historically).

## Q20 Promotion gate — **FAIL (correctly blocked)**
LIVE off. Cannot promote to real money. Missing: DATA/FEATURE/LEAKAGE/OOS/BACKTEST/COST/RISK/PAPER/UI truth all green simultaneously.

**Safety:** Do not flip LIVE flags.
