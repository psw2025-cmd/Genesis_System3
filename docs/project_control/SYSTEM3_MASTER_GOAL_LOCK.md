# System3 Master Goal Lock

Repository: `psw2025-cmd/Genesis_System3`
Locked date: 2026-06-18
Owner goal source: Pritam Warghade

## Master objective

Build Genesis System3 as a world-class AI-assisted automated trading intelligence system for the Indian option market, focused on NSE optionable symbols and index/stock option segments.

The system objective is to continuously discover, predict, validate, and improve high-probability CE/PE trading opportunities before market movement becomes obvious, then compare predictions with actual market results and continuously learn from outcomes.

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

## Current priority order

1. Ensure GitHub Actions full proof job runs and uploads `system3-proof-pack`.
2. Fix any CI failures without enabling live trading.
3. Build optionable-symbol filter so equity-only names do not become option trade candidates.
4. Build prediction-vs-actual benchmark using real market data.
5. Build CE/PE paper lifecycle and PnL reconciliation.
6. Make dashboard show only real, reconciled truth.
7. Run multiple days of analyzer/paper proof.
8. Only after repeated proof, design controlled live-trading gate.

## Final locked statement

Genesis System3 is intended to become a highly automated, self-learning, AI-assisted Indian options trading system that discovers high-probability opportunities, validates predictions against real market outcomes, improves continuously, and eventually supports controlled trade execution only after strict proof gates.

The current locked state is proof-first analyzer/paper mode. Live trading remains disabled until evidence proves readiness.
