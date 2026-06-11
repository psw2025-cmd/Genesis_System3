# OptionChain Master - Complete Guide

## 🎯 Overview

The OptionChain Master Excel file provides comprehensive option chain analysis with all calculations, metrics, and data for production trading.

**File Location:** `outputs/OptionChain_Master_v3_AI_FINAL.xlsx`

---

## 📊 What's Included

### Excel Sheets (10 Total)

1. **OptionChain_Data** - Main comprehensive data (358 rows, 58 columns)
2. **CHAIN_CALC** - All calculated columns only
3. **Summary** - Underlying-wise summary metrics
4. **OI_BUILDUP** - Open Interest buildup analysis
5. **GREEKS** - All Greeks data (Delta, Gamma, Theta, Vega, Rho, IV)
6. **GAMMA_THETA_MAP** - Gamma/Theta exposure mapping
7. **BANKNIFTY_Chain** - BANKNIFTY specific data
8. **FINNIFTY_Chain** - FINNIFTY specific data
9. **MIDCPNIFTY_Chain** - MIDCPNIFTY specific data
10. **NIFTY_Chain** - NIFTY specific data

### Data Columns (58 Total)

#### Contract Information
- underlying, exchange, token, symbol, strike, option_type, expiry

#### Price Data
- ltp, spot_price, bidPrice, offerPrice, mid_price, open, high, low, close

#### Volume & OI
- volume, oi, dVolume, dOI

#### Greeks
- delta, gamma, theta, vega, rho, iv

#### Calculated Metrics (19 columns)
- intrinsic_value, extrinsic_value
- bid_ask_spread, bid_ask_spread_pct
- atm_distance, atm_distance_pct
- expected_move
- gamma_exposure, theta_exposure, vega_exposure
- liquidity_score
- iv_rank, iv_percentile
- breakeven_price
- theoretical_price, price_vs_theoretical
- max_profit, max_loss, risk_reward_ratio
- moneyness
- time_decay_rate

---

## 🚀 Quick Start

### Option 1: Update Excel File (Recommended)

**Double-click:** `UPDATE_OPTIONCHAIN_MASTER.bat`

This will:
1. ✅ Fetch fresh option chain data
2. ✅ Rebuild Excel with all calculations
3. ✅ Verify data quality
4. ✅ Show performance report

**Time:** ~90 seconds (first time), ~10 seconds (if CSV is fresh)

### Option 2: Monitor Performance

**Double-click:** `MONITOR_OPTIONCHAIN.bat`

This shows:
- File status and age
- Data completeness
- Underlying coverage
- Recommendations

### Option 3: Manual Update (Command Line)

```bash
cd C:\Genesis_System3
UPDATE_OPTIONCHAIN_MASTER.bat
```

**Force fresh fetch:**
```bash
UPDATE_OPTIONCHAIN_MASTER.bat --force-fetch
```

---

## ⚙️ Automated Scheduling

### Windows Task Scheduler Setup

1. **Open Task Scheduler** (search "Task Scheduler" in Windows)

2. **Create Basic Task:**
   - Name: `Update OptionChain Master`
   - Trigger: Daily at 9:00 AM (before market opens)
   - Action: Start a program
   - Program: `C:\Genesis_System3\UPDATE_OPTIONCHAIN_MASTER.bat`
   - Start in: `C:\Genesis_System3`

3. **Additional Triggers:**
   - Add trigger: Every 1 hour during market hours (9:15 AM - 3:30 PM)
   - Add trigger: At 3:45 PM (after market close)

4. **Settings:**
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
   - ✅ Configure for: Windows 10

---

## 📈 Performance Metrics

### Current Status
- **Rows:** 358 option contracts
- **Columns:** 58 (including 19 calculated)
- **Data Completeness:** 79.9%
- **Contract Info:** 100% complete
- **Price Data:** 100% complete
- **Greeks:** 100% complete
- **Calculated:** 92.9% complete

### Update Performance
- **Fetch Time:** ~78 seconds (with fresh API calls)
- **Build Time:** ~10 seconds
- **Verify Time:** ~2 seconds
- **Total Time:** ~90 seconds

---

## 🔍 Data Sources

### Primary Source
- **CSV:** `outputs/chain_raw_live.csv`
  - Updated by live system every 5 seconds
  - Contains all raw option chain data

### Secondary Source
- **Storage:** `storage/live/option_chain_ALL_INDICES.csv`
  - Backup/archive location
  - Used if live CSV is unavailable

---

## ✅ Verification Checklist

After each update, verify:

- [ ] Excel file exists and opens correctly
- [ ] All 10 sheets are present
- [ ] Main sheet has 58 columns
- [ ] Data completeness > 75%
- [ ] All critical columns present (underlying, strike, option_type, ltp, spot_price)
- [ ] Calculated columns are populated
- [ ] No errors in performance report

---

## 🛠️ Troubleshooting

### Issue: Excel file not updating

**Solution:**
1. Check if CSV source exists: `outputs/chain_raw_live.csv`
2. Run with force fetch: `UPDATE_OPTIONCHAIN_MASTER.bat --force-fetch`
3. Check live system status

### Issue: Low data completeness

**Solution:**
1. Verify market is open (9:15 AM - 3:30 PM IST)
2. Check API connectivity
3. Run monitor: `MONITOR_OPTIONCHAIN.bat`

### Issue: Missing calculated columns

**Solution:**
1. Ensure all dependencies installed: `pip install openpyxl xlsxwriter`
2. Rebuild: `UPDATE_OPTIONCHAIN_MASTER.bat --force-fetch`

---

## 📝 Best Practices

1. **Update Frequency:**
   - Before market open: 9:00 AM
   - During market: Every hour
   - After market close: 3:45 PM

2. **Data Quality:**
   - Always verify completeness > 75%
   - Check all critical columns present
   - Review performance report

3. **Backup:**
   - Excel file has auto-backup: `.xlsx.backup`
   - Keep CSV source files for recovery

---

## 📞 Support

For issues or questions:
1. Run `MONITOR_OPTIONCHAIN.bat` for diagnostics
2. Check logs in `logs/` directory
3. Review verification output

---

## 🎯 Next Steps

1. ✅ **Set up scheduled updates** (Task Scheduler)
2. ✅ **Review Excel file** - Open and explore all sheets
3. ✅ **Monitor performance** - Run monitor script regularly
4. ✅ **Integrate with trading** - Use data for decision making

---

**Last Updated:** 2026-01-31  
**Status:** Production Ready ✅
