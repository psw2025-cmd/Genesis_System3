# System3 Core Trading Goal and Architecture Rules

## Permanent Core Goal

System3 exists to become a proof-first paper-trading system that can:

1. Identify option-tradable Indian market opportunities before the main move happens.
2. Predict the direction, timing, trade type, strike/expiry eligibility, and expected opportunity quality before entry.
3. Take only safe paper trades first, never live trades unless explicitly promoted after long evidence.
4. Compare every prediction and every paper trade against actual market results every day.
5. Improve the selector/ranker/risk/execution logic from evidence, not assumptions.

The target is not only deployment or dashboard availability. Deployment is useful only if it helps the above trading-performance goal.

## Non-Negotiable Trading Mode

- Default mode: Analyzer/Paper only.
- Live trading must stay disabled unless there is explicit future approval and hard proof gates are passed.
- Any code path that can place, modify, or cancel live broker orders must have analyzer-only protection and audit logs.

## Dynamic Layers That Must Be Managed

### 1. Market Universe and Tradability Layer

The system must separate:

- NSE/BSE cash-only movers.
- F&O symbols.
- Option-tradable symbols with valid expiry, strike, token, liquidity, and spread.
- Broker-supported symbols.

A trade candidate is not valid until it passes tradability checks.

Required proof:

- Symbol exists in the broker/NSE option universe.
- Expiry is valid and not stale.
- Strike is available and mapped to correct instrument token.
- Bid/ask/liquidity/spread is acceptable.
- Cash-only movers are logged separately and not treated as missed option trades.

### 2. Prediction-Before-Move Layer

The system must prove that prediction happened before the move, not after.

Required proof for each prediction:

- Timestamp in IST.
- Symbol, direction, CE/PE intent, option eligibility status.
- Signal source and feature snapshot.
- Score before entry.
- Market price before prediction.
- Later market result after fixed windows such as 5 min, 15 min, 30 min, 60 min, and end of day.

### 3. Ranking and Selection Layer

The system must select the best opportunities from all valid candidates, not just any mover.

Required checks:

- Why this symbol was selected.
- Why stronger movers were rejected.
- Whether rejected symbols were option-tradable.
- Whether daily cap, per-symbol cap, open-position cap, risk gate, or liquidity gate blocked them.
- Whether ranker score matched realized market gain.

### 4. Paper Execution and Risk Layer

Paper trades must behave like realistic broker trades.

Required checks:

- Entry price must use realistic option quotes/spread logic.
- Stop loss, target, trailing stop, and exit logic must be recorded.
- Slippage and liquidity assumptions must be visible.
- Every paper order must reconcile with paper tradebook and position ledger.
- No fake profit should be counted without executable market evidence.

### 5. Daily Result Reconciliation Layer

Every trading day must produce a result file that compares:

- Predicted candidates vs actual market movement.
- Selected paper trades vs rejected opportunities.
- Highest-gain valid option opportunities vs System3 selected opportunities.
- Missed valid trades vs cash-only movers.
- P&L, drawdown, win rate, false positives, false negatives, and timing error.

Daily verdict must be one of:

- PASS: System predicted and selected valid high-gain option opportunities with realistic paper execution.
- PARTIAL: Some predictions were valid but selection/execution/risk/proof had gaps.
- FAIL: Prediction, eligibility, execution, or reconciliation did not prove market-matching performance.
- BLOCKED: Required data/feed/broker/universe/proof was missing.

## Global Architecture Comparison Rule

Every audit, implementation, or agent prompt must compare the current repo against stronger global trading-system architecture patterns:

- Universe management and instrument master integrity.
- Real-time data quality and timestamp correctness.
- Feature generation without lookahead bias.
- Model/ranker validation against out-of-sample market results.
- Risk engine and capital protection.
- Paper/live separation.
- Order/execution realism.
- Observability, logs, ledger, replay, and reproducibility.
- Daily proof ZIP/report generation.

The audit must output:

1. What exists now.
2. What is missing.
3. What is wrong or unsafe.
4. What must be corrected first.
5. What can improve prediction quality.
6. What can improve paper-trade profitability proof.
7. What should remain blocked until evidence exists.

## Required Pass/Fail Gates

### Gate A: Analyzer/Paper Safety

Pass only if live broker execution is disabled by default and protected at all order routes.

### Gate B: Market Data and Universe Integrity

Pass only if the system can prove valid option tradability before ranking or paper entry.

### Gate C: Prediction Ledger Integrity

Pass only if every prediction has timestamped pre-move evidence and later result comparison.

### Gate D: Ranker Quality

Pass only if selected candidates are compared against rejected valid candidates and actual market gain.

### Gate E: Paper Execution Realism

Pass only if paper fills, exits, P&L, and positions reconcile with realistic quotes and slippage assumptions.

### Gate F: Daily Market Result Proof

Pass only if a daily report proves predicted vs actual market result, highest-gain comparison, and missed-trade classification.

### Gate G: Profitability Evidence

Pass only after multiple trading days show stable positive expectancy with controlled drawdown and no proof gaps.

## Agent Operating Rule

No agent should focus only on deployment, UI, or code cleanup unless it directly supports the core trading-performance goal.

Before any change, an agent must state:

- Which gate it improves.
- Which proof file will show pass/fail.
- Whether it affects live trading risk.
- Whether it improves prediction quality, paper execution, or daily reconciliation.

## User Requirement Lock

The user's permanent requirement is:

System3 must become capable of finding the best daily market opportunity before it rises, safely paper-trading it, and proving prediction accuracy and paper profitability against real market results every day.
