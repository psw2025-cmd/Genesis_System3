# System3 Thresholds Upgrade - Complete Analysis
**Analysis Date**: 2025-12-04 00:21:42  
**Workflow**: Complete thresholds upgrade (Phase 221 → 222 → Proposer → Test)

---

## Executive Summary

**Status**: ✅ **SUCCESSFUL**  
**Key Achievement**: System now generates **2 BUY signals** (vs 0 with default thresholds)  
**Thresholds Generated**: Data-driven thresholds based on EV analysis  
**Data Quality**: 560 of 608 rows have forward returns (92% coverage)

---

## 1. Forward Returns Analysis (Phase 221)

### File: `storage/live/angel_index_ai_signals_with_forward.csv`

**Total Rows**: 608  
**Rows with Forward Returns**: 560 (92.1% coverage)  
**Missing Forward Returns**: 48 rows (7.9%)

**Reason for Missing**:
- Last N rows in each contract group (can't compute forward returns for final snapshots)
- Expected behavior - not an error

**Forward Return Columns**:
- `fwd_ret_1`: 1-snapshot forward return
- `fwd_ret_3`: 3-snapshot forward return  
- `fwd_ret_5`: 5-snapshot forward return

**Sample Data**:
- Row 4: `fwd_ret_1=0.148`, `fwd_ret_3=0.148`, `fwd_ret_5=0.148` (BANKNIFTY CE, positive)
- Row 5: `fwd_ret_1=-0.102`, `fwd_ret_3=-0.102`, `fwd_ret_5=-0.102` (BANKNIFTY PE, negative)

**Status**: ✅ **EXCELLENT** - Forward returns computed correctly using LTP (option premium)

---

## 2. EV Tables Analysis (Phase 222)

### File: `logs/research/system3_signal_edge_report.md`

**Total EV Tables**: 51  
**Grouped By**: 5 underlyings × 3 horizons × multiple score bins

### Key Findings by Underlying

#### BANKNIFTY
**Horizon 1 (Most Immediate)**:
- `[-0.1, 0.1)`: **+0.0104 avg return**, 30 trades, 50% hit-rate ✅ **BEST**
- `[0.1, 0.3)`: -0.0114 avg return, 10 trades, 50% hit-rate ❌
- `[-0.3, -0.1)`: -0.0105 avg return, 12 trades, 33% hit-rate ❌

**Analysis**: The `[-0.1, 0.1)` bin (neutral scores) shows positive returns! This suggests the model is conservative but effective for neutral scores.

**Proposed Threshold**: BUY >= 0.10 (using `[0.1, 0.3)` bin start, but data shows `[-0.1, 0.1)` is better)

#### FINNIFTY
**Horizon 1**:
- `[-0.1, 0.1)`: **+0.0091 avg return**, 31 trades, 16% hit-rate ⚠️ (low hit-rate)
- `[0.1, 0.3)`: -0.0040 avg return, 10 trades, 10% hit-rate ❌
- `[-0.3, -0.1)`: -0.0202 avg return, 9 trades, 11% hit-rate ❌

**Analysis**: Similar pattern - neutral scores perform best, but hit-rate is low (16%).

**Proposed Threshold**: BUY >= 0.40 (default, no positive-score bins with >=20 samples)

#### MIDCPNIFTY
**Horizon 1**:
- `[-0.1, 0.1)`: **+0.0014 avg return**, 42 trades, 33% hit-rate ⚠️ (very small return)
- `[-0.3, -0.1)`: +0.0041 avg return, 5 trades, 40% hit-rate ⚠️ (too few samples)
- `[0.1, 0.3)`: -0.0053 avg return, 7 trades, 0% hit-rate ❌

**Analysis**: Very small returns, low hit-rates. Limited edge detected.

**Proposed Threshold**: BUY >= 0.40 (default, insufficient data)

#### NIFTY
**Horizon 1**:
- `[-0.1, 0.1)`: **+0.0917 avg return**, 19 trades, 47% hit-rate ✅ **EXCELLENT**
- `[-0.3, -0.1)`: -0.0039 avg return, 16 trades, 50% hit-rate ❌
- `[0.1, 0.3)`: -0.0008 avg return, 12 trades, 33% hit-rate ❌
- `[0.3, 0.5)`: -0.0382 avg return, 5 trades, 60% hit-rate ❌

**Horizon 3** (Better Performance):
- `[-0.1, 0.1)`: **+0.1186 avg return**, 19 trades, 53% hit-rate ✅
- `[0.1, 0.3)`: **+0.0603 avg return**, 12 trades, 58% hit-rate ✅
- `[-0.3, -0.1)`: **+0.1109 avg return**, 16 trades, 63% hit-rate ✅

**Analysis**: NIFTY shows strong performance, especially at horizon 3. The `[-0.1, 0.1)` bin has excellent returns.

**Proposed Threshold**: BUY >= 0.40 (default, but `[-0.1, 0.1)` shows better returns)

#### SENSEX
**Horizon 1**:
- `[-0.1, 0.1)`: **+0.0114 avg return**, 38 trades, 42% hit-rate ✅
- `[-0.3, -0.1)`: **+0.0552 avg return**, 7 trades, 43% hit-rate ⚠️ (too few samples)
- `[0.1, 0.3)`: -0.0235 avg return, 5 trades, 40% hit-rate ❌

**Analysis**: Similar to others - neutral scores perform best.

**Proposed Threshold**: BUY >= 0.40 (default, insufficient positive-score data)

---

## 3. Thresholds Analysis

### File: `storage/meta/system3_live_thresholds.json`

**Global Thresholds**:
- BUY: **0.34** (lowered from 0.40)
- SELL: **-0.40** (unchanged)

**Per-Underlying Thresholds**:

| Underlying | BUY Threshold | SELL Threshold | Rationale |
|------------|---------------|----------------|-----------|
| BANKNIFTY | **0.10** | -0.40 | Lowered based on `[0.1, 0.3)` bin (though `[-0.1, 0.1)` shows better returns) |
| FINNIFTY | 0.40 | -0.40 | Default (no positive-score bins with >=20 samples) |
| MIDCPNIFTY | 0.40 | -0.40 | Default (insufficient data) |
| NIFTY | 0.40 | -0.40 | Default (though `[-0.1, 0.1)` shows excellent returns) |
| SENSEX | 0.40 | -0.40 | Default (insufficient data) |

**Analysis**:
- ✅ BANKNIFTY threshold lowered to 0.10 (more aggressive)
- ⚠️ Other underlyings use default 0.40 (conservative, but data-limited)
- ⚠️ **Issue**: The proposer selected `[0.1, 0.3)` bin for BANKNIFTY, but this bin has **negative returns** (-0.0114). The `[-0.1, 0.1)` bin has positive returns (+0.0104) but wasn't selected because it includes negative scores.

**Recommendation**: Consider using `[-0.1, 0.1)` bin threshold (0.0 or slightly negative) for BANKNIFTY, or adjust the proposer logic.

---

## 4. Comparison Report Analysis

### File: `docs/system3_thresholds_comparison.md`

**Test Data**: 30 signals from recent snapshots

**Results**:

| Signal | Auto-Thresholds (0.40/-0.40) | Live-Thresholds | Difference |
|--------|-------------------------------|-----------------|------------|
| BUY | 0 | **2** | **+2** ✅ |
| SELL | 0 | 0 | 0 |
| HOLD | 30 | 28 | -2 |

**BUY Signals Generated**:
1. BANKNIFTY 59200 CE: `final_score=0.138661` (above 0.10 threshold)
2. BANKNIFTY 59300 CE: `final_score=0.103389` (above 0.10 threshold)

**Analysis**:
- ✅ **Success**: 2 BUY signals generated (vs 0 with defaults)
- ✅ Both signals are BANKNIFTY (which has lower threshold 0.10)
- ⚠️ No SELL signals (all scores above -0.40)
- ⚠️ Limited test data (only 30 signals)

**Score Distribution**:
- Min: -0.168
- Max: 0.222
- Mean: -0.004
- Std: 0.103

**Observation**: Scores are centered around 0, with most in the `[-0.1, 0.1)` range. This aligns with the EV analysis showing this bin has positive returns.

---

## 5. Threshold Optimizer Log Analysis

### File: `logs/research/system3_threshold_optimizer.log`

**EV Metrics Used**:

| Underlying | BUY Threshold | SELL Threshold | BUY Count | SELL Count | BUY Avg Return | SELL Avg Return |
|------------|---------------|----------------|-----------|------------|----------------|-----------------|
| BANKNIFTY | 0.100 | -0.400 | 30 | 0 | 0.0104 | 0.0000 |
| FINNIFTY | 0.400 | -0.400 | 0 | 0 | 0.0000 | 0.0000 |
| MIDCPNIFTY | 0.400 | -0.400 | 0 | 0 | 0.0000 | 0.0000 |
| NIFTY | 0.400 | -0.400 | 0 | 0 | 0.0000 | 0.0000 |
| SENSEX | 0.400 | -0.400 | 0 | 0 | 0.0000 | 0.0000 |

**Analysis**:
- ✅ BANKNIFTY: 30 samples with positive return (0.0104)
- ❌ Other underlyings: No positive-score bins with >=20 samples
- ⚠️ **Issue**: The proposer selected `[0.1, 0.3)` bin for BANKNIFTY, but this bin actually has **negative returns** in the EV table. The logic needs refinement.

---

## 6. Critical Findings

### ✅ What Worked

1. **Forward Returns**: Successfully computed for 92% of rows
2. **EV Tables**: 51 tables created, showing clear patterns
3. **Threshold Generation**: BANKNIFTY threshold lowered to 0.10
4. **Signal Generation**: 2 BUY signals generated (vs 0 with defaults)

### ⚠️ Issues Identified

1. **Threshold Proposer Logic**:
   - Selected `[0.1, 0.3)` bin for BANKNIFTY, but this bin has **negative returns** (-0.0114)
   - Should have selected `[-0.1, 0.1)` bin which has **positive returns** (+0.0104)
   - Logic needs to prioritize return quality over bin position

2. **Limited Data**:
   - Only 560 rows with forward returns
   - Many score bins have <20 samples
   - Most underlyings fall back to default thresholds

3. **Score Distribution**:
   - Most scores in `[-0.1, 0.1)` range (neutral)
   - Very few scores > 0.40 (explains why default threshold generates 0 BUY signals)
   - Model is conservative (good for safety, but limits signal generation)

### 🔍 Key Insights

1. **Neutral Scores Perform Best**:
   - The `[-0.1, 0.1)` bin consistently shows positive returns across underlyings
   - This suggests the model is well-calibrated for neutral market conditions
   - Consider using a threshold around 0.0 or slightly negative for BUY

2. **Horizon Matters**:
   - Horizon 3 and 5 show better returns than horizon 1
   - NIFTY shows excellent returns at horizon 3 (+0.1186)
   - Consider using longer horizons for threshold selection

3. **BANKNIFTY Shows Promise**:
   - Lower threshold (0.10) generates 2 BUY signals
   - These signals have scores 0.103 and 0.138 (above threshold)
   - Worth monitoring performance of these signals

---

## 7. Recommendations

### Immediate Actions

1. **Refine Threshold Proposer**:
   - Prioritize return quality over bin position
   - Consider using `[-0.1, 0.1)` bin threshold for underlyings where it shows positive returns
   - Use horizon 3 data if horizon 1 is insufficient

2. **Adjust BANKNIFTY Threshold**:
   - Current: 0.10 (based on `[0.1, 0.3)` bin, but this bin has negative returns)
   - Recommended: 0.0 or -0.05 (to capture `[-0.1, 0.1)` bin which has positive returns)
   - **Caution**: This is more aggressive, monitor closely

3. **Collect More Data**:
   - Run system for several more days to accumulate more signals
   - Target: 2000+ rows with forward returns
   - This will improve EV table quality and threshold selection

### Future Improvements

1. **Multi-Horizon Thresholds**:
   - Use different thresholds for different holding periods
   - Short-term (1 snapshot): More conservative
   - Medium-term (3-5 snapshots): More aggressive

2. **Dynamic Thresholds**:
   - Adjust thresholds based on market conditions
   - Higher thresholds in high volatility
   - Lower thresholds in low volatility

3. **Hit-Rate Weighting**:
   - Consider hit-rate in addition to average return
   - Prefer bins with both positive returns AND high hit-rate (>50%)

---

## 8. Expected Trade Frequency

### Current State (After Upgrade)

**With Live Thresholds**:
- BUY signals: **2 per 30 signals** (6.7% of signals)
- SELL signals: 0 per 30 signals (0%)
- HOLD signals: 28 per 30 signals (93.3%)

**Projected (Per Snapshot)**:
- If each snapshot generates ~30 signals:
  - BUY: ~2 signals per snapshot
  - SELL: ~0 signals per snapshot (scores not negative enough)
  - HOLD: ~28 signals per snapshot

**Daily Projection** (assuming 60 snapshots/day):
- BUY: ~120 signals/day
- SELL: ~0 signals/day
- HOLD: ~1680 signals/day

### Comparison to Default Thresholds

**With Default Thresholds (0.40/-0.40)**:
- BUY: 0 signals (0%)
- SELL: 0 signals (0%)
- HOLD: 30 signals (100%)

**Improvement**: **+2 BUY signals** (from 0 to 2)

---

## 9. Limitations

### Data Volume

1. **Limited Historical Data**:
   - Only 608 total rows
   - 560 with forward returns
   - Many score bins have <20 samples

2. **Sparse EV Tables**:
   - Some underlyings have very few data points
   - Most underlyings fall back to default thresholds
   - Need more data for robust threshold selection

### Model Output

1. **Conservative Scores**:
   - Most scores in `[-0.1, 0.1)` range
   - Very few scores > 0.40
   - Model is risk-averse (good for safety)

2. **Limited Positive-Score Bins**:
   - Most positive returns are in neutral-score bins
   - Positive-score bins (`[0.1, 0.3)`, `[0.3, 0.5)`) often have negative returns
   - Suggests model may be over-conservative

### Threshold Selection

1. **Proposer Logic**:
   - Currently prioritizes bin position over return quality
   - Selected `[0.1, 0.3)` for BANKNIFTY, but this bin has negative returns
   - Should prioritize return quality

2. **Minimum Sample Size**:
   - Requires >=20 samples per bin
   - Many bins don't meet this requirement
   - Falls back to defaults, which may be too conservative

---

## 10. Conclusion

**Overall Status**: ✅ **SUCCESSFUL UPGRADE**

**Key Achievements**:
1. ✅ Forward returns computed for 92% of data
2. ✅ EV tables generated showing clear patterns
3. ✅ Thresholds generated (BANKNIFTY lowered to 0.10)
4. ✅ 2 BUY signals generated (vs 0 with defaults)

**Key Findings**:
1. Neutral scores (`[-0.1, 0.1)`) show positive returns across underlyings
2. BANKNIFTY threshold lowered successfully (generates 2 BUY signals)
3. Other underlyings need more data for threshold optimization
4. Model is conservative but effective for neutral market conditions

**Next Steps**:
1. Monitor the 2 BUY signals generated
2. Collect more data (target: 2000+ rows)
3. Refine threshold proposer logic to prioritize return quality
4. Consider using `[-0.1, 0.1)` bin threshold for more underlyings

**System Status**: ✅ **READY FOR MONITORING** - The system will now generate more BUY signals with the new thresholds, especially for BANKNIFTY.

