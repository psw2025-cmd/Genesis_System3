# CSV Additional Columns Recommendation

**Date**: 2026-01-30  
**Analysis**: Current CSV structure vs. recommended additions  
**Status**: ✅ **ANALYSIS COMPLETE**

---

## 📊 Current CSV Status

**File**: `storage/live/option_chain_ALL_INDICES.csv`
- **Rows**: 374 option contracts
- **Columns**: 37 columns
- **Data Quality**: Excellent (95%+ completeness for most fields)
- **Missing**: Greeks data (0% - expected, market was closed)

---

## ✅ Current Columns (37)

### Contract Info (14 columns)
- underlying, exchange, tradingSymbol, symbol, name, token
- expiry, expiry_date, strike, option_type
- instrumentType, lotSize, tickSize, spot_price, moneyness

### Price Data (9 columns)
- ltp, open, high, low, close, volume, oi, change, pChange

### Bid/Ask (4 columns)
- bidPrice, bidQty, offerPrice, offerQty

### Greeks (6 columns)
- delta, gamma, theta, vega, rho, iv

### Premium Fields (3 columns)
- pTime, pOI, pVolume

### Timestamp (1 column - missing in current fetch)
- Note: `fetch_timestamp` columns are added by hourly auto-fetch script

---

## 🎯 Recommended Additional Columns (14)

### 🔴 HIGH PRIORITY (3 columns)

#### 1. `intrinsic_value` (float)
**Description**: Intrinsic value of option  
**Calculation**:
- For CE: `max(0, spot_price - strike)`
- For PE: `max(0, strike - spot_price)`

**Use Case**: 
- Option valuation
- Moneyness analysis
- Determining ITM/OTM status

**Example**: If spot=25400, strike=25000, CE intrinsic = 400

---

#### 2. `extrinsic_value` (float)
**Description**: Extrinsic (time) value of option  
**Calculation**: `ltp - intrinsic_value`

**Use Case**:
- Time value analysis
- Theta decay tracking
- Premium composition

**Example**: If ltp=500, intrinsic=400, extrinsic = 100

---

#### 3. `bid_ask_spread` (float)
**Description**: Absolute bid-ask spread  
**Calculation**: `offerPrice - bidPrice`

**Use Case**:
- Liquidity analysis
- Execution cost estimation
- Market depth assessment

**Example**: If bid=125, ask=126, spread = 1

---

### 🟡 MEDIUM PRIORITY (7 columns)

#### 4. `intrinsic_pct` (float)
**Description**: Intrinsic value as % of premium  
**Calculation**: `(intrinsic_value / ltp) * 100`

**Use Case**: Option composition analysis

---

#### 5. `atm_distance` (float)
**Description**: Absolute distance from ATM strike in points  
**Calculation**: `abs(strike - spot_price)`

**Use Case**: Strike selection, moneyness analysis

---

#### 6. `atm_distance_pct` (float)
**Description**: Distance from ATM as % of spot  
**Calculation**: `(abs(strike - spot_price) / spot_price) * 100`

**Use Case**: Relative strike positioning

---

#### 7. `bid_ask_spread_pct` (float)
**Description**: Bid-ask spread as % of mid price  
**Calculation**: `(bid_ask_spread / mid_price) * 100`

**Use Case**: Relative liquidity measure

---

#### 8. `mid_price` (float)
**Description**: Mid price (average of bid and ask)  
**Calculation**: `(bidPrice + offerPrice) / 2`

**Use Case**: Fair value estimation

---

#### 9. `volume_oi_ratio` (float)
**Description**: Volume to OI ratio  
**Calculation**: `volume / oi` (if oi > 0)

**Use Case**: Trading activity vs open positions

---

#### 10. `put_call_spread` (float)
**Description**: Difference between CE and PE premium (for same strike)  
**Calculation**: `CE_ltp - PE_ltp` (requires merging CE/PE pairs)

**Use Case**: Put-call parity analysis, arbitrage detection

**Note**: Requires matching CE/PE pairs by strike

---

### 🟢 LOW PRIORITY (4 columns)

#### 11. `delta_gamma_ratio` (float)
**Description**: Delta to Gamma ratio  
**Calculation**: `delta / gamma` (if gamma > 0)

**Use Case**: Advanced Greeks analysis, hedging efficiency

---

#### 12. `theta_per_day` (float)
**Description**: Theta per day (normalized)  
**Calculation**: `theta / days_to_expiry`

**Use Case**: Time decay analysis

---

#### 13. `premium_pct_of_strike` (float)
**Description**: Premium as % of strike price  
**Calculation**: `(ltp / strike) * 100`

**Use Case**: Relative premium analysis

---

#### 14. `premium_pct_of_spot` (float)
**Description**: Premium as % of spot price  
**Calculation**: `(ltp / spot_price) * 100`

**Use Case**: Cost of option relative to underlying

---

## ⚠️ Missing Base Column

**`fetch_date`** - Required for `days_to_expiry` calculation

**Current Status**: 
- `fetch_timestamp` columns are added by `auto_fetch_option_chain_hourly.py`
- `fetch_all_indices_option_chain.py` does NOT add timestamps

**Recommendation**: 
- Add `fetch_date` to `fetch_all_indices_option_chain.py` OR
- Calculate `days_to_expiry` using `expiry_date` and current date

---

## 📋 Implementation Priority

### Phase 1: Essential Calculations (HIGH Priority)
1. ✅ `intrinsic_value`
2. ✅ `extrinsic_value`
3. ✅ `bid_ask_spread`

**Impact**: Core option valuation and liquidity analysis

---

### Phase 2: Enhanced Analysis (MEDIUM Priority)
4. ✅ `atm_distance` / `atm_distance_pct`
5. ✅ `mid_price`
6. ✅ `volume_oi_ratio`
7. ✅ `intrinsic_pct`

**Impact**: Better strike selection and market analysis

---

### Phase 3: Advanced Metrics (LOW Priority)
8. ✅ Greeks-based ratios
9. ✅ Premium percentages
10. ✅ Put-call parity metrics

**Impact**: Advanced trading strategies and analysis

---

## 💡 Implementation Notes

### Where to Add Calculations

**Option 1**: Add to `broker.py` - `get_option_chain_by_underlying()`
- Pros: Calculated at fetch time, always available
- Cons: Adds computation overhead during fetch

**Option 2**: Add as post-processing step
- Pros: Flexible, can recalculate without re-fetching
- Cons: Requires separate processing step

**Option 3**: Add to CSV export/append logic
- Pros: Calculated once when saving
- Cons: Need to handle existing data

**Recommended**: **Option 2** - Post-processing function that can be applied to any DataFrame

---

## 🔧 Sample Implementation

```python
def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add calculated columns to option chain DataFrame"""
    df = df.copy()
    
    # Intrinsic value
    def calc_intrinsic(row):
        if row['option_type'] == 'CE':
            return max(0, row['spot_price'] - row['strike'])
        else:  # PE
            return max(0, row['strike'] - row['spot_price'])
    
    df['intrinsic_value'] = df.apply(calc_intrinsic, axis=1)
    df['extrinsic_value'] = df['ltp'] - df['intrinsic_value']
    df['intrinsic_pct'] = (df['intrinsic_value'] / df['ltp'] * 100).fillna(0)
    
    # ATM distance
    df['atm_distance'] = abs(df['strike'] - df['spot_price'])
    df['atm_distance_pct'] = (df['atm_distance'] / df['spot_price'] * 100).fillna(0)
    
    # Bid-ask spread
    df['bid_ask_spread'] = df['offerPrice'] - df['bidPrice']
    df['mid_price'] = (df['bidPrice'] + df['offerPrice']) / 2
    df['bid_ask_spread_pct'] = (df['bid_ask_spread'] / df['mid_price'] * 100).fillna(0)
    
    # Volume/OI ratio
    df['volume_oi_ratio'] = (df['volume'] / df['oi']).fillna(0)
    
    # Days to expiry (if fetch_date available)
    if 'fetch_date' in df.columns:
        df['fetch_date'] = pd.to_datetime(df['fetch_date'])
        df['expiry_date'] = pd.to_datetime(df['expiry_date'])
        df['days_to_expiry'] = (df['expiry_date'] - df['fetch_date']).dt.days
        df['time_to_expiry'] = df['days_to_expiry'] / 365.0
    
    return df
```

---

## 📊 Expected Benefits

### For Trading
- ✅ Better strike selection (ATM distance)
- ✅ Liquidity assessment (bid-ask spread)
- ✅ Option valuation (intrinsic/extrinsic)

### For Analysis
- ✅ Time decay tracking (days to expiry)
- ✅ Market activity (volume/OI ratio)
- ✅ Put-call parity (spread analysis)

### For Strategy
- ✅ Risk assessment (Greeks ratios)
- ✅ Cost analysis (premium percentages)
- ✅ Arbitrage detection (put-call spread)

---

## ✅ Conclusion

**Current CSV**: ✅ **Well-structured, comprehensive base data**

**Recommended Additions**: **14 calculated columns**
- **3 HIGH priority** (essential for trading)
- **7 MEDIUM priority** (enhanced analysis)
- **4 LOW priority** (advanced metrics)

**Next Steps**:
1. Implement HIGH priority columns first
2. Add `fetch_date` to fetch scripts for time calculations
3. Create post-processing function for calculated columns
4. Test with sample data before full deployment

---

**Analysis Completed**: 2026-01-30  
**Status**: ✅ **READY FOR IMPLEMENTATION**
