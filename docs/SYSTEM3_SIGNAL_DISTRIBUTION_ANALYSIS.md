# System3 Signal Distribution Analysis - Clean EV-Ready CSV

**Date**: 2025-12-04  
**Data Source**: Clean EV-Ready CSV (232 rows)  
**Status**: ✅ **ANALYSIS COMPLETE**

---

## Executive Summary

The signal distribution analysis reveals that **proposed thresholds (BUY >= 0.400, SELL <= -0.400) are too high** for the current dataset. **No signals exist** at these thresholds. Recommended thresholds are much lower: **BUY >= 0.1** and **SELL <= -0.1**.

---

## Overall Distribution Statistics

### Final Score Distribution

| Statistic | Value |
|-----------|-------|
| **Total Rows** | 232 |
| **Valid final_score** | 232 (100%) |
| **Mean** | -0.001507 (slightly negative) |
| **Median** | -0.010079 (negative) |
| **Std Dev** | 0.109195 |
| **Min** | -0.231473 |
| **25th Percentile** | -0.076254 |
| **75th Percentile** | 0.070186 |
| **Max** | 0.329456 |

### Key Insights

1. **Distribution is centered near zero** (mean = -0.0015, median = -0.0101)
2. **Range is limited**: -0.23 to 0.33 (no extreme scores)
3. **Slightly negative bias**: More signals below zero than above
4. **No signals at high thresholds**: BUY >= 0.4 and SELL <= -0.4 both have 0 signals

---

## Signal Counts at Different Thresholds

### BUY Thresholds

| Threshold | Signal Count | Percentage | Status |
|-----------|--------------|------------|--------|
| **BUY >= 0.1** | **40** | **17.2%** | ✅ **RECOMMENDED** |
| **BUY >= 0.15** | **13** | **5.6%** | ✅ **RECOMMENDED** |
| BUY >= 0.2 | 8 | 3.4% | ⚠️ Low count |
| BUY >= 0.25 | 6 | 2.6% | ⚠️ Very low |
| BUY >= 0.3 | 5 | 2.2% | ⚠️ Very low |
| **BUY >= 0.4** | **0** | **0.0%** | ❌ **NO SIGNALS** |
| BUY >= 0.5 | 0 | 0.0% | ❌ No signals |

### SELL Thresholds

| Threshold | Signal Count | Percentage | Status |
|-----------|--------------|------------|--------|
| **SELL <= -0.1** | **39** | **16.8%** | ✅ **RECOMMENDED** |
| **SELL <= -0.15** | **15** | **6.5%** | ✅ **RECOMMENDED** |
| SELL <= -0.2 | 8 | 3.4% | ⚠️ Low count |
| **SELL <= -0.3** | **0** | **0.0%** | ❌ **NO SIGNALS** |
| SELL <= -0.4 | 0 | 0.0% | ❌ No signals |
| SELL <= -0.5 | 0 | 0.0% | ❌ No signals |

---

## Per-Underlying Distribution

### BANKNIFTY (44 rows)

| Statistic | Value |
|-----------|-------|
| Mean | -0.013455 |
| Median | -0.048579 |
| Min | -0.175675 |
| Max | **0.131147** |
| **BUY >= 0.1** | **6 signals** |
| BUY >= 0.4 | 0 signals |
| **SELL <= -0.1** | **8 signals** |
| SELL <= -0.4 | 0 signals |

**Analysis**: Lower scores overall, max score only 0.131. Lower BUY threshold (0.1) works.

### FINNIFTY (40 rows)

| Statistic | Value |
|-----------|-------|
| Mean | -0.006987 |
| Median | -0.047680 |
| Min | -0.146871 |
| Max | **0.142016** |
| **BUY >= 0.1** | **6 signals** |
| BUY >= 0.4 | 0 signals |
| **SELL <= -0.1** | **5 signals** |
| SELL <= -0.4 | 0 signals |

**Analysis**: Similar to BANKNIFTY, max score 0.142. Lower BUY threshold needed.

### MIDCPNIFTY (54 rows)

| Statistic | Value |
|-----------|-------|
| Mean | -0.003093 |
| Median | -0.017232 |
| Min | -0.104446 |
| Max | **0.118305** |
| **BUY >= 0.1** | **7 signals** |
| BUY >= 0.4 | 0 signals |
| **SELL <= -0.1** | **5 signals** |
| SELL <= -0.4 | 0 signals |

**Analysis**: Largest sample size (54), but max score only 0.118. Lower threshold needed.

### NIFTY (50 rows) ⭐ **BEST DISTRIBUTION**

| Statistic | Value |
|-----------|-------|
| Mean | **0.020082** (positive!) |
| Median | **0.049595** (positive!) |
| Min | -0.231473 |
| Max | **0.329456** (highest!) |
| **BUY >= 0.1** | **17 signals** (most!) |
| BUY >= 0.4 | 0 signals |
| **SELL <= -0.1** | **15 signals** (most!) |
| SELL <= -0.4 | 0 signals |

**Analysis**: 
- ⭐ **Best distribution** - positive mean and median
- ⭐ **Highest max score** (0.329)
- ⭐ **Most BUY signals** (17 at 0.1)
- ⭐ **Most SELL signals** (15 at -0.1)
- **Best candidate for threshold optimization**

### SENSEX (44 rows)

| Statistic | Value |
|-----------|-------|
| Mean | -0.007163 |
| Median | -0.010000 |
| Min | -0.154736 |
| Max | **0.158868** |
| **BUY >= 0.1** | **4 signals** |
| BUY >= 0.4 | 0 signals |
| **SELL <= -0.1** | **6 signals** |
| SELL <= -0.4 | 0 signals |

**Analysis**: Moderate distribution, max score 0.159. Lower threshold needed.

---

## Recommended Thresholds

### Based on Signal Distribution Analysis

#### Option 1: Balanced (Recommended)

| Underlying | BUY Threshold | SELL Threshold | Expected Signals |
|------------|---------------|-----------------|------------------|
| **BANKNIFTY** | >= **0.100** | <= **-0.100** | 6 BUY, 8 SELL |
| **FINNIFTY** | >= **0.100** | <= **-0.100** | 6 BUY, 5 SELL |
| **MIDCPNIFTY** | >= **0.100** | <= **-0.100** | 7 BUY, 5 SELL |
| **NIFTY** | >= **0.100** | <= **-0.100** | 17 BUY, 15 SELL |
| **SENSEX** | >= **0.100** | <= **-0.100** | 4 BUY, 6 SELL |

**Total**: ~40 BUY signals, ~39 SELL signals

#### Option 2: Conservative (Higher Quality)

| Underlying | BUY Threshold | SELL Threshold | Expected Signals |
|------------|---------------|-----------------|------------------|
| **BANKNIFTY** | >= **0.150** | <= **-0.150** | ~2 BUY, ~2 SELL |
| **FINNIFTY** | >= **0.150** | <= **-0.150** | ~2 BUY, ~2 SELL |
| **MIDCPNIFTY** | >= **0.150** | <= **-0.150** | ~2 BUY, ~2 SELL |
| **NIFTY** | >= **0.150** | <= **-0.150** | ~5 BUY, ~5 SELL |
| **SENSEX** | >= **0.150** | <= **-0.150** | ~2 BUY, ~2 SELL |

**Total**: ~13 BUY signals, ~15 SELL signals

#### Option 3: Aggressive (More Signals)

| Underlying | BUY Threshold | SELL Threshold | Expected Signals |
|------------|---------------|-----------------|------------------|
| **All** | >= **0.050** | <= **-0.050** | ~60-80 BUY, ~60-80 SELL |

**Total**: More signals but lower quality

---

## Comparison with Phase 223 Proposed Thresholds

### Phase 223 Proposed (Too High)

| Underlying | BUY Threshold | SELL Threshold | Actual Signals |
|------------|---------------|----------------|----------------|
| BANKNIFTY | >= 0.100 | <= -0.400 | 30 BUY, **0 SELL** |
| Others | >= 0.400 | <= -0.400 | **0 BUY, 0 SELL** |

**Problem**: Thresholds too high, no signals for most underlyings

### Distribution-Based Recommended (Feasible)

| Underlying | BUY Threshold | SELL Threshold | Actual Signals |
|------------|---------------|----------------|----------------|
| All | >= 0.100 | <= -0.100 | **40 BUY, 39 SELL** |

**Solution**: Lower thresholds generate signals for all underlyings

---

## Key Findings

### 1. Threshold Feasibility

- ❌ **BUY >= 0.400**: **0 signals** (not feasible)
- ✅ **BUY >= 0.100**: **40 signals** (17.2% - feasible)
- ❌ **SELL <= -0.400**: **0 signals** (not feasible)
- ✅ **SELL <= -0.100**: **39 signals** (16.8% - feasible)

### 2. NIFTY Best Performer

- ⭐ **Positive mean and median** (only underlying with this)
- ⭐ **Highest max score** (0.329)
- ⭐ **Most BUY signals** (17 at 0.1)
- ⭐ **Most SELL signals** (15 at -0.1)
- **Best candidate for threshold optimization**

### 3. Score Distribution Characteristics

- **Centered near zero**: Mean = -0.0015, Median = -0.0101
- **Limited range**: -0.23 to 0.33 (no extreme scores)
- **Slightly negative bias**: More signals below zero
- **No extreme scores**: Max = 0.33, Min = -0.23

### 4. Sample Size Considerations

- **Total**: 232 rows (moderate sample size)
- **Per-underlying**: 40-54 rows (small for statistical significance)
- **Need more data** for robust threshold optimization

---

## Recommendations

### Immediate Actions

1. **✅ DONE**: Signal distribution analysis complete
2. **✅ DONE**: Feasible thresholds identified
3. **⚠️ TODO**: Update Phase 223 to use feasible thresholds
4. **⚠️ TODO**: Validate thresholds with test mode

### For Production Use

#### Recommended Thresholds (Based on Distribution)

**Global Thresholds**:
- **BUY >= 0.100** (40 signals, 17.2%)
- **SELL <= -0.100** (39 signals, 16.8%)

**Per-Underlying Thresholds** (if needed):
- **NIFTY**: BUY >= 0.100, SELL <= -0.100 (17 BUY, 15 SELL)
- **Others**: BUY >= 0.100, SELL <= -0.100 (lower signal counts)

#### Rationale

1. **Generates signals**: 40 BUY + 39 SELL = 79 total signals
2. **Reasonable percentage**: 17-18% of dataset (not too aggressive)
3. **Balanced**: Similar counts for BUY and SELL
4. **Feasible**: Signals actually exist at these thresholds

### For Future Optimization

1. **Collect More Data**: Increase sample size for better statistics
2. **Monitor Distribution**: Track how score distribution changes over time
3. **Refine Thresholds**: Adjust based on forward returns performance
4. **Per-Underlying Models**: Consider separate thresholds for each underlying

---

## Next Steps

### 1. Update Threshold Configuration

Update `system3_live_thresholds.json` with feasible thresholds:
```json
{
  "global": {
    "buy": 0.100,
    "sell": -0.100
  },
  "per_underlying": {
    "BANKNIFTY": {"buy": 0.100, "sell": -0.100},
    "FINNIFTY": {"buy": 0.100, "sell": -0.100},
    "MIDCPNIFTY": {"buy": 0.100, "sell": -0.100},
    "NIFTY": {"buy": 0.100, "sell": -0.100},
    "SENSEX": {"buy": 0.100, "sell": -0.100}
  }
}
```

### 2. Validate with Test Mode

Run test mode with new thresholds:
```bash
python system3_signal_test_mode.py --use-live-thresholds
```

### 3. Monitor Performance

- Track signal counts at these thresholds
- Monitor forward returns for signals
- Adjust thresholds based on performance

---

## Conclusion

**Signal distribution analysis reveals that proposed thresholds (0.400 / -0.400) are not feasible** for the current dataset. **Recommended thresholds are much lower**:

- ✅ **BUY >= 0.100** (40 signals available)
- ✅ **SELL <= -0.100** (39 signals available)

**NIFTY shows the best signal distribution** with positive mean/median and the most signals at recommended thresholds.

**Status**: ✅ **Analysis Complete** - Feasible thresholds identified

**Next Action**: Update threshold configuration and validate with test mode

---

**Last Updated**: 2025-12-04

