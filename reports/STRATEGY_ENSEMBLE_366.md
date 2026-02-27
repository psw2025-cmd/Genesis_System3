# STRATEGY ENSEMBLE EVALUATION - PHASE 366

**Generated:** 2025-12-10 07:51:56

## Executive Summary

This phase evaluates the performance of multiple internal trading strategies
(ML, DL, Momentum, Mean-Reversion) across the curated signal dataset.


## Results

**Total Signals Evaluated:** 297  
**Dominant Strategy:** Mean-Reversion

### Strategy Performance Metrics

| Strategy | Count | Avg Confidence | Avg Score | Win Rate | Recency | Weighted Score | Dominance % |
|----------|-------|---|---|---|---|---|---|
| Mean-Reversion | 13 | 0.6016 | 0.6016 | 0.0000 | 1.0000 | 0.1810 | 4.38% |
| Momentum | 253 | 0.2917 | 0.3132 | 0.0000 | 1.0000 | 0.0457 | 85.19% |
| Unknown | 31 | nan | nan | 0.0000 | nan | nan | 10.44% |

## Market Condition Analysis

### Time Windows
- **Short-term:** 1 day(s) with 0 signals
- **Long-term:** 7 day(s) with 100 signals

**Short-term Dominant:** Unknown  
**Long-term Dominant:** Momentum

## Interpretation

- **Weighted Score:** Combines confidence, score, win rate, and recency
- **Market Dominance %:** Percentage of total signals from each strategy
- **Recency Score:** Favors more recent signals (adjusts for staleness)
- **Win Rate:** Signals that align with positive forward returns

## Recommendations

1. Monitor dominant strategy for market regime alignment
2. Watch for strategy switching (indicates market condition changes)
3. Use weighted scores to calibrate confidence thresholds
4. Adjust position sizing based on strategy mix in short-term window

---

**Status:** [OK] Analysis Complete (DRY-RUN)  
**Safety Mode:** DRY-RUN (no orders, no broker calls)
