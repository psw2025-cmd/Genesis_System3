# System3 Master Goal Lock

Repository: `psw2025-cmd/Genesis_System3`
Locked date: 2026-06-18
Owner goal source: Pritam Warghade

## Master objective

Build Genesis System3 as a world-class AI-assisted automated trading intelligence system for the Indian option market, focused on NSE optionable symbols and index/stock option segments.

The system objective is to continuously discover, predict, validate, and improve high-probability CE/PE trading opportunities before market movement becomes obvious, then compare predictions with actual market results and continuously learn from outcomes.

## Result-oriented execution rule

This project must be managed by result, not by vague activity.

Every phase, PR, script, workflow, agent run, and patch must define:

1. The exact goal.
2. The expected measurable result.
3. The files/scripts/workflows involved.
4. The command or CI job used to test it.
5. The proof artifact generated.
6. The PASS/PARTIAL/BLOCKED/FAIL status.
7. The remaining blocker.
8. The freeze condition before moving to the next phase.

No phase can be called complete only because code was written. A phase is complete only when its proof passes and its result is frozen in `reports/latest/` or a project-control document.

## Important realism rule

The system must aim for maximum practical prediction quality and profitability, but it must never claim guaranteed profit, guaranteed highest accuracy, or guaranteed market-beating performance without evidence.

Every claim must be backed by repeatable proof from logs, reports, market data, prediction-vs-actual comparison, paper lifecycle records, and PnL reconciliation.

## Current operating mode

Until full proof is achieved:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `ANALYZE_MODE=1`
- `SYSTEM3_MODE=analyze`
- Paper/analyzer mode only
- No real broker order placement
- No automatic live execution
- No hidden live trading path

## Phase freeze framework

Each phase must be frozen before the next phase starts.

A freeze means:

- scope is clear
- code path is known
- test command is known
- result is measured
- output artifact exists
- dashboard/report truth matches source data
- blockers are documented
- next action is explicit
- no live trading flag was changed

Freeze file format:

```text
PHASE: <phase name>
GOAL: <result expected>
STATUS: PASS / PARTIAL / BLOCKED / FAIL
PROOF_PATH: reports/latest/<phase>/...
COMMANDS_RUN: <exact commands>
FILES_CHANGED: <exact files>
BLOCKERS: <exact blocker list>
NEXT_PHASE_ALLOWED: YES/NO
LIVE_TRADING: DISABLED
TRADE_READY: NO
```

## Result-oriented phase map

### Phase 0 — Repository and goal authority

Goal:
Freeze the master project objective and stop future agent drift.

Expected result:
All agents know that System3 is an analyzer/paper-first Indian options AI automation system, not a deployment-only project and not a live-trading shortcut.

Required proof:
- This file exists.
- CI can read repo files.
- `reports/latest/` proof pack can be generated.

Freeze condition:
PASS only when the goal file, CI workflow, and proof artifact process exist.

### Phase 1 — CI and safety proof

Goal:
Make GitHub Actions prove safety and basic runtime import health.

Expected result:
CI runs with read-only permissions and all live trading flags disabled.

Required proof:
- `.github/workflows/ci.yml`
- job `workflow-policy-guard`
- job `architecture-trading-safety`
- job `python-compile-proof`
- job `full-proof-pack-validation`
- artifact `system3-proof-pack`

Freeze condition:
PASS only when GitHub Actions run completes and artifact exists.
If logs are unavailable, status is NOT VERIFIED.

### Phase 2 — Optionable universe filter

Goal:
Prevent equity-only symbols from becoming option trade candidates.

Expected result:
Only NSE optionable stocks and valid index option symbols can enter CE/PE trade planning.

Required proof:
- optionable universe source file or API result
- symbol eligibility report
- rejected equity-only list
- accepted optionable list
- expiry/strike availability check

Freeze condition:
PASS only when signals like equity-only names are rejected before trade planning.

### Phase 3 — Prediction-vs-actual benchmark

Goal:
Compare every prediction against actual market results.

Expected result:
For each predicted symbol/direction, the system records actual movement, rank, gain/loss, CE/PE correctness, and miss reason.

Required proof:
- `prediction_vs_actual.csv`
- `top_mover_match.csv`
- `missed_opportunities.md`
- calibration/hit-rate summary

Freeze condition:
PASS only when real market rows exist and no fake metrics are used.

### Phase 4 — CE/PE decision and paper trade lifecycle

Goal:
Convert qualified predictions into paper option trade plans and track full lifecycle.

Expected result:
Every paper trade has signal, CE/PE, strike, expiry, entry, SL, target, trailing rule, exit, and PnL.

Required proof:
- signal-order-trade join
- paper fills
- open/closed positions
- PnL reconciliation
- mismatch report

Freeze condition:
PASS only when dashboard, DB, logs, and report show matching lifecycle truth.

### Phase 5 — Continuous learning loop

Goal:
Make the system learn from real prediction outcomes and paper-trade results.

Expected result:
The system updates analysis, thresholds, ranking, and model candidates based on proof-backed outcome data.

Required proof:
- learning input dataset
- model/threshold candidate report
- before/after benchmark
- rollback plan
- promotion gate result

Freeze condition:
PASS only when improvement is measured on out-of-sample or walk-forward data and no auto-promotion bypass exists.

### Phase 6 — Dashboard truth and operator control

Goal:
Dashboard must show real reconciled system truth.

Expected result:
UI/API state must match backend source files, DB, reports, and alerts.

Required proof:
- browser/API smoke proof
- `/api/state`
- `/api/broker/status`
- `/api/health`
- dashboard screenshot or API JSON
- mode truth proof

Freeze condition:
PASS only when dashboard cannot show LIVE while broker/data is not ready.

### Phase 7 — Multi-day analyzer/paper proof

Goal:
Prove the system works practically across multiple market days.

Expected result:
The system runs pre-market, market-open, intraday, and post-market flows repeatedly with consistent proof.

Required proof:
- daily proof packs
- daily prediction-vs-actual
- daily lifecycle/PnL reconciliation
- daily dashboard truth
- daily blocker summary

Freeze condition:
PASS only after repeated market-day evidence, not one static run.

### Phase 8 — Controlled live-readiness gate

Goal:
Design live execution only after all analyzer/paper proof gates pass.

Expected result:
Live mode remains disabled until explicit approval and hard risk controls exist.

Required proof:
- kill switch
- max loss rule
- max trade count
- slippage/spread guard
- broker order dry-run proof
- manual approval record

Freeze condition:
PASS only when live readiness is proven. Until then `TRADE_READY=NO`.

## Long-term target capability

System3 should eventually support the following capabilities after proof gates pass:

1. Market universe discovery
   - Identify only tradable and optionable Indian market symbols.
   - Separate equity-only symbols from option-tradable symbols.
   - Detect index options and stock options correctly.
   - Avoid signals on symbols where no valid option trade exists.

2. Prediction engine
   - Predict high-gain symbols before movement.
   - Predict CE/PE direction with confidence.
   - Rank opportunities by expected value, probability, liquidity, risk/reward, and option tradability.
   - Compare every prediction against actual market outcome.
   - Track hit rate, rank quality, calibration, missed opportunities, false positives, and false negatives.

3. Continuous learning
   - Store every prediction, decision, paper trade, exit, PnL, and market result.
   - Learn from prediction-vs-actual mismatch.
   - Improve model thresholds only through governed proof.
   - Block auto-promotion unless objective metrics pass.
   - Maintain model version history and rollback ability.

4. Paper/analyzer lifecycle
   - Convert qualified signals into paper option trade plans.
   - Include CE/PE, strike, expiry, entry, stop loss, target, trailing rule, confidence, reason, and risk.
   - Reconcile signal -> order plan -> paper fill -> exit -> PnL.
   - Dashboard, DB, reports, and alerts must match.

5. Automation
   - Run daily without manual babysitting after safe configuration.
   - Perform pre-market checks, market-open scans, intraday monitoring, post-market learning, and end-of-day reports.
   - Detect holidays, market hours, data freshness, broker read-only status, and token health.
   - Send clear alerts/reports without placing real trades until live approval gates pass.

6. Risk and safety
   - Never place live orders unless all readiness gates pass and explicit live approval exists.
   - Enforce max trades per day, max loss, max symbol exposure, max option spread/slippage, and kill switch.
   - Paper mode must remain default.
   - Live mode must require explicit environment flags, broker validation, and final governance proof.

7. Dashboard and proof
   - Dashboard must show real system truth, not fake/synthetic success.
   - UI mode must never display LIVE when broker is disconnected or data is synthetic/not ready.
   - Every readiness claim must have proof artifacts under `reports/latest/`.
   - GitHub Actions must upload proof artifacts such as `system3-proof-pack`.

## Required proof gates before live trading

Trade readiness is `NO` until all of these are proven:

1. Repo authority proof: PASS
2. CI safety workflow: PASS
3. Secrets scan: PASS
4. Live trading disabled by default: PASS
5. Broker read-only/analyzer connection proof: PASS
6. Fresh market data proof: PASS
7. Optionable universe filter proof: PASS
8. Prediction-vs-actual benchmark: PASS with real market rows
9. Top gainer/top loser comparison: PASS with actual market data
10. CE/PE decision validation: PASS
11. Paper trade lifecycle: PASS
12. PnL reconciliation: PASS
13. Dashboard truth proof: PASS
14. Alert/report consistency: PASS
15. Risk-control and kill-switch proof: PASS
16. Multi-day repeated analyzer/paper proof: PASS
17. Manual approval for live mode: PASS

Until then:

- `TRADE_READY=NO`
- `LIVE_TRADING=DISABLED`
- `ANALYZER_OR_PAPER_ONLY=YES`

## Agent instructions

Any future AI agent, Copilot, Cursor, Claude Code, Codex, Gemini, or automation must follow this lock file.

Agents must:

- Read this file before modifying trading logic.
- Preserve analyzer/paper mode by default.
- Produce proof before claims.
- Work result-first: every patch must have target result, test command, proof path, and freeze status.
- Freeze each phase before starting the next phase.
- Avoid fake PASS statements.
- Avoid deleting source without repo authority proof.
- Avoid changing broker, DB, model, or live execution paths without explicit safety plan.
- Prioritize optionable universe filtering, prediction-vs-actual validation, lifecycle reconciliation, and dashboard truth.

Agents must not:

- Enable live trading.
- Commit secrets.
- Place real broker orders.
- Claim guaranteed profit.
- Claim world-best accuracy without evidence.
- Hide blockers.
- Confuse equity signals with option-tradable signals.
- Skip phase-freeze evidence.

## Current priority order

1. Ensure GitHub Actions full proof job runs and uploads `system3-proof-pack`.
2. Fix any CI failures without enabling live trading.
3. Build optionable-symbol filter so equity-only names do not become option trade candidates.
4. Build prediction-vs-actual benchmark using real market data.
5. Build CE/PE paper lifecycle and PnL reconciliation.
6. Make dashboard show only real, reconciled truth.
7. Run multiple days of analyzer/paper proof.
8. Only after repeated proof, design controlled live-trading gate.

## Result freeze commandment

No work is complete until the result is proven.

A future agent must answer every task with:

- What result was targeted?
- What changed?
- What command/test proved it?
- What artifact proves it?
- What phase is frozen?
- What remains blocked?
- Is live trading still disabled?
- Is trade readiness still NO?

## Final locked statement

Genesis System3 is intended to become a highly automated, self-learning, AI-assisted Indian options trading system that discovers high-probability opportunities, validates predictions against real market outcomes, improves continuously, and eventually supports controlled trade execution only after strict proof gates.

The current locked state is proof-first analyzer/paper mode. Live trading remains disabled until evidence proves readiness.

Each phase must be result-oriented and frozen only after proof. Activity without measurable result is not completion.
