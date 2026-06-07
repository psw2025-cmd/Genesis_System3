# Production Grade Readiness Gate

Generated UTC: 2026-06-07T19:42:58.845983+00:00

Verdict: `NOT_PRODUCTION_GRADE_READY`
Production-grade ready: `False`
Trade ready: `False`

Checks passed: `9/26`
Critical blockers: `12`
Medium blockers: `5`

## Blockers

| Area | Check | Severity | Fix |
|---|---|---|---|
| `repo` | `old/backup/copy files classified` | `medium` | classify 12 review candidates with runtime map before delete/archive |
| `data` | `Yahoo fallback data proof published` | `medium` | run external Yahoo data proof |
| `data` | `Yahoo fallback symbols OK` | `medium` | fix external public data fallback |
| `data` | `broker/analyzer market data proven` | `critical` | connect broker in analyzer mode and prove paper lifecycle |
| `model` | `fresh model training proven` | `critical` | run authoritative training/load proof |
| `model` | `fresh training accuracy metric proven` | `critical` | publish accuracy metrics with dataset/date |
| `backtest` | `recent backtest proven` | `critical` | run recent backtest |
| `backtest` | `walk-forward cost/slippage proven` | `critical` | run walk-forward with costs/slippage |
| `backtest` | `safe dry-run validation execution proof published` | `medium` | run safe dry-run validation workflow |
| `backtest` | `safe dry-run commands passed` | `medium` | fix dry-run failures |
| `paper_lifecycle` | `live-market analyzer paper trade today proven` | `critical` | prove BUY/SELL/fill/exit/PnL lifecycle in analyzer mode |
| `dashboard` | `full dashboard proof published` | `critical` | run ultra dashboard readiness proof |
| `dashboard` | `dashboard endpoint coverage published` | `critical` | run dashboard endpoint coverage proof |
| `dashboard` | `full dashboard ready proven` | `critical` | fix frontend build/UI/API wiring and browser proof |
| `dashboard` | `backend endpoint coverage core ok` | `critical` | fix failing read-only endpoint coverage |
| `dashboard` | `browser visual proof completed` | `critical` | run browser/UI screenshot smoke proof |
| `production` | `overall trading pipeline trade_ready` | `critical` | clear all pipeline blockers first |

## Next fix queue

1. connect broker in analyzer mode and prove paper lifecycle
2. run authoritative training/load proof
3. publish accuracy metrics with dataset/date
4. run recent backtest
5. run walk-forward with costs/slippage
6. prove BUY/SELL/fill/exit/PnL lifecycle in analyzer mode
7. run ultra dashboard readiness proof
8. run dashboard endpoint coverage proof
9. fix frontend build/UI/API wiring and browser proof
10. fix failing read-only endpoint coverage
11. run browser/UI screenshot smoke proof
12. clear all pipeline blockers first
13. classify 12 review candidates with runtime map before delete/archive
14. run external Yahoo data proof
15. fix external public data fallback
16. run safe dry-run validation workflow
17. fix dry-run failures

Analyzer/Paper only. Live trading disabled.
