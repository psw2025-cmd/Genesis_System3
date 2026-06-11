# ROOT_CAUSE_ANALYSIS.md

## Current State (From Latest Run)

```
QC_PASSED: False
TRADE_SIGNALS: 0
NO_TRADE_REASONS: {'LOW_CONFIDENCE': 4, 'QC_FAILED': 1}

ACTION: NO_TRADE
CONFIDENCE: 0.6950659042985966
REASON: LOW_CONFIDENCE
CANDIDATE_STRATEGY: IRON_CONDOR
```

## Root Causes Identified

### Issue #1: QC Validation Too Strict
**File**: `src/validation/qc_validator.py`
**Function**: `validate_snapshot(df, underlying)`
**Condition**: Multiple checks failing
**Impact**: Blocks ALL strategy execution for QC-failed underlyings
**Fix Required**: 
- Lower `min_contracts` thresholds OR
- Implement QC override for PAPER_SANITY mode (allow >= 70% pass rate)

**Current Thresholds**:
- SENSEX: 30 contracts
- MIDCPNIFTY: 40 contracts
- FINNIFTY: 45 contracts
- NIFTY: 50 contracts
- BANKNIFTY: 50 contracts
- Data completeness: 70%
- ATM strikes: >= 10 (or >= 5 in sim_mode)

### Issue #2: Strategy Engine Thresholds Too Strict
**File**: `src/selector/strategy_engine.py`
**Function**: `recommend_strategy()`
**Condition**: 
```python
if confidence < self.min_confidence or liquidity_score < self.min_liquidity_score:
    return NO_TRADE
```
**Current Thresholds**:
- `min_confidence`: 0.5
- `min_liquidity_score`: 40.0

**Additional Blocking Conditions**:
```python
# Line 227-257: Strategy selection requires:
- BULLISH: bullish_score > 60
- BEARISH: bearish_score > 60
- NEUTRAL: liquidity_score > 70
```

**Impact**: Even with confidence 0.695, if liquidity_score < 40 OR sentiment scores < 60, returns NO_TRADE
**Fix Required**: Lower thresholds OR implement PAPER_SANITY override

### Issue #3: Confidence Filter Converting TRADE to NO_TRADE
**File**: `option_chain_automation_master.py`
**Function**: `generate_signals()`
**Line**: 922-936
**Condition**: 
```python
elif s.get('confidence', 0) >= self.config.min_confidence:
    filtered_signals.append(s)
else:
    # Low confidence - convert to NO_TRADE
    no_trade['action'] = 'NO_TRADE'
    no_trade['reason'] = 'LOW_CONFIDENCE'
```
**Impact**: Even if strategy returns TRADE, if confidence < 0.5, converts to NO_TRADE
**Fix Required**: This is correct behavior, but min_confidence may be too high OR strategy is returning low confidence

### Issue #4: Liquidity Score Calculation May Be Low
**File**: `option_chain_automation_master.py`
**Function**: `generate_signals()`
**Line**: 792-796
**Condition**:
```python
liquidity_score = min(100.0, (avg_volume * 0.4 + avg_oi * 0.6) / 100)
```
**Issue**: Division by 100 may make score too low if volume/OI are already in small units
**Impact**: liquidity_score < 40 even with good data
**Fix Required**: Verify calculation OR adjust threshold

### Issue #5: Sentiment Scores May Be Low
**File**: `src/selector/strategy_engine.py`
**Function**: `analyze_sentiment()`
**Line**: 56-110
**Condition**: Requires bullish_score > 60 OR bearish_score > 60 for BULLISH/BEARISH strategies
**Impact**: NEUTRAL sentiment with liquidity_score < 70 also blocks trades
**Fix Required**: Lower sentiment thresholds OR allow NEUTRAL with lower liquidity

### Issue #6: LIVE Safety Lock (Not Applicable for Paper)
**File**: `option_chain_automation_master.py`
**Function**: `run_cycle()`
**Line**: 1475-1478
**Condition**: 
```python
if not self.sim_mode and not self.live_trade_enabled:
    trade_signals = []
```
**Impact**: In LIVE mode without `--live-trade-enable`, all trades blocked
**Fix Required**: This is SAFETY - correct behavior. Paper trading should use `--sim` mode OR enable live_trade_enabled

## Summary Table

| Issue | File | Function | Condition | Fix Required |
|-------|------|----------|-----------|--------------|
| QC Too Strict | `qc_validator.py` | `validate_snapshot()` | Multiple checks failing | Lower thresholds OR PAPER_SANITY override |
| Strategy Thresholds | `strategy_engine.py` | `recommend_strategy()` | `liquidity_score < 40` OR `sentiment scores < 60` | Lower thresholds OR PAPER_SANITY override |
| Confidence Filter | `option_chain_automation_master.py` | `generate_signals()` | `confidence < 0.5` | Verify why confidence is low OR lower threshold |
| Liquidity Calculation | `option_chain_automation_master.py` | `generate_signals()` | `liquidity_score = (avg_volume * 0.4 + avg_oi * 0.6) / 100` | Verify calculation |
| Sentiment Thresholds | `strategy_engine.py` | `analyze_sentiment()` | `bullish_score <= 60` AND `bearish_score <= 60` | Lower thresholds |
| LIVE Safety Lock | `option_chain_automation_master.py` | `run_cycle()` | `not sim_mode and not live_trade_enabled` | Use `--sim` for paper OR enable flag |

## Primary Blockers (In Order of Impact)

1. **QC_FAILED** (1 underlying) → Blocks strategy entirely
2. **LOW_CONFIDENCE** (4 underlyings) → Strategy returns TRADE but confidence filter converts to NO_TRADE
3. **Liquidity Score < 40** → Strategy returns NO_TRADE before confidence check
4. **Sentiment Scores < 60** → Strategy returns NO_TRADE for BULLISH/BEARISH

## Recommended Fixes

1. **Implement PAPER_SANITY mode**:
   - If QC passes >= 70% of underlyings, allow trades
   - If confidence >= 0.60, force at least 1 trade per cycle
   - Override strategy thresholds temporarily

2. **Lower QC thresholds** for paper trading:
   - Reduce `min_contracts` by 20-30%
   - Reduce `min_data_completeness` to 60%

3. **Lower strategy thresholds**:
   - `min_liquidity_score`: 40 → 30
   - `min_confidence`: 0.5 → 0.45
   - Sentiment scores: 60 → 50
   - NEUTRAL liquidity: 70 → 50

4. **Fix liquidity score calculation**:
   - Verify if division by 100 is correct
   - May need to remove division if volume/OI are already normalized
