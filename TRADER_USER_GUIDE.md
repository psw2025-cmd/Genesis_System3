# System3 Ultra Dashboard - Trader User Guide

**Version**: Production 1.0  
**Last Updated**: 2026-02-05

---

## 🚀 Quick Start

### Starting the System

**Option 1: One-Click Start (Recommended)**
```powershell
.\START_FULL_SYSTEM_WITH_DASHBOARD.ps1
```

This will automatically:
- ✅ Start trading system
- ✅ Start dashboard backend API
- ✅ Start dashboard frontend
- ✅ Start data monitoring
- ✅ Open dashboard in Chrome

**Option 2: Manual Start**
```powershell
# Terminal 1: Trading System
python option_chain_automation_master.py --sim --cycles 10

# Terminal 2: Dashboard Backend
cd dashboard\backend
..\..\venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000

# Terminal 3: Dashboard Frontend
cd dashboard\frontend
npm run dev
```

---

## 📊 Dashboard Access

### URLs
- **Main Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Browser Compatibility
- ✅ Google Chrome (Recommended)
- ✅ Microsoft Edge
- ✅ Firefox
- ⚠️ Safari (Limited support)

---

## 🎯 Dashboard Features

### 1. Overview Tab
**Real-time System Status**
- Mode (LIVE/SIM)
- Broker connection status
- Market status (Open/Closed)
- Cycle count and refresh interval
- QC status with failure reasons
- Trades executed and open positions
- Total PnL and daily PnL
- Performance SLA metrics

**Key Metrics**:
- **Cycle Duration**: Should be <60 seconds (SLA)
- **Fetch Duration**: Data fetch time
- **Strategy Duration**: Signal generation time
- **QC Pass Rate**: Data quality percentage

### 2. Chain Analytics Tab
**Option Chain Data**
- Multi-underlying support:
  - NIFTY
  - BANKNIFTY
  - FINNIFTY
  - MIDCPNIFTY
  - SENSEX

**Features**:
- Spot price (real-time)
- Put-Call Ratio (PCR)
- Total contracts count
- Live chain table with:
  - Strike prices
  - LTP (Last Traded Price)
  - Volume and OI
  - Greeks (Delta, Gamma, Theta, Vega)
  - IV (Implied Volatility)
  - Liquidity scores

**Filters**:
- Strike range (min/max)
- Near ATM only (within 5% of spot)
- Liquidity threshold
- Show invalid rows

### 3. Signals Tab
**Trading Signals & Recommendations**
- Top trade signal display
- Explainability panel:
  - Reasons for signal
  - Confidence score
  - Strategy details
- QC gating status
- "What blocked trading?" panel
- Strategy details:
  - Legs (single/multi-leg)
  - Strikes
  - Entry price
  - Stop loss
  - Target price
- Export signal snapshot as JSON

### 4. Paper Trading Tab
**Open Positions**
- Position table with:
  - Symbol
  - Quantity
  - Entry price
  - Current price
  - Unrealized PnL
  - Status

**PnL Charts**:
- Equity curve (total PnL over time)
- Daily PnL breakdown
- Win rate visualization
- Max profit/drawdown

**PnL Summary**:
- Total trades
- Winning trades
- Losing trades
- Win rate percentage
- Total realized PnL
- Total unrealized PnL
- Open positions count

### 5. Model Behavior Tab
**ML Model Performance**
- Model predictions
- Accuracy metrics
- Confidence scores
- Model selection logic

### 6. Control Plane Tab
**System Controls**
- Manual position closure
- System status controls
- Configuration settings

---

## 🔍 Data Validation

### Automatic Validation
The system automatically validates data every 5 minutes:
- ✅ Compares spot prices with live market data
- ✅ Validates option chain data accuracy
- ✅ Checks for data inconsistencies
- ✅ Auto-fixes critical issues

### Manual Validation
Run validation manually:
```powershell
.\venv\Scripts\python.exe .\scripts\dashboard_data_validator.py
```

### Validation Reports
Location: `outputs/validation/`
- `dashboard_validation_*.json` - Data validation results
- `multi_user_test_*.json` - Multi-user test results

---

## ⚠️ Troubleshooting

### Dashboard Not Loading
1. Check if backend is running:
   ```powershell
   curl http://localhost:8000/api/health
   ```
2. Check if frontend is running:
   ```powershell
   curl http://localhost:3000
   ```
3. Restart services:
   ```powershell
   .\START_FULL_SYSTEM_WITH_DASHBOARD.ps1
   ```

### Data Not Updating
1. Check if trading system is running
2. Verify data files exist:
   - `outputs/chain_raw_live.csv`
   - `outputs/health.json`
   - `outputs/qc_report_live.json`
3. Run data fix:
   ```powershell
   .\venv\Scripts\python.exe .\scripts\fix_dashboard_data_issues.py
   ```

### Spot Price Mismatch
If spot prices don't match live market:
1. Run data fix script:
   ```powershell
   .\venv\Scripts\python.exe .\scripts\fix_dashboard_data_issues.py
   ```
2. Restart dashboard backend
3. Check validation report in `outputs/validation/`

### Performance Issues
If dashboard is slow:
1. Check API response times:
   ```powershell
   .\scripts\PRODUCTION_DASHBOARD_TEST.ps1
   ```
2. Verify backend is not overloaded
3. Check network connectivity

---

## 📈 Best Practices

### For Traders
1. **Monitor Overview Tab Regularly**
   - Check QC status before making decisions
   - Verify market status
   - Monitor cycle duration (should be <60s)

2. **Use Chain Analytics for Research**
   - Filter by liquidity threshold
   - Focus on near-ATM options
   - Check PCR for sentiment

3. **Review Signals Tab**
   - Understand signal reasoning
   - Check confidence scores
   - Review QC gating status

4. **Track PnL in Paper Trading Tab**
   - Monitor equity curve
   - Review win rate
   - Check max drawdown

5. **Validate Data Quality**
   - Run validation before important decisions
   - Check validation reports
   - Verify spot prices match live market

### For System Administrators
1. **Monitor System Health**
   - Check logs in `logs/` directory
   - Review validation reports
   - Monitor API response times

2. **Run Regular Tests**
   - Daily: `.\scripts\PRODUCTION_DASHBOARD_TEST.ps1`
   - Weekly: Multi-user test
   - Monthly: Comprehensive validation

3. **Maintain Data Quality**
   - Fix data issues immediately
   - Monitor validation reports
   - Ensure spot prices are accurate

---

## 🔐 Security Notes

- Dashboard runs on localhost only (127.0.0.1)
- No external access by default
- API endpoints require local network access
- Secrets are redacted in logs

---

## 📞 Support

### Logs Location
- Backend logs: `logs/`
- Validation reports: `outputs/validation/`
- Test reports: `outputs/dashboard_production_test_report.json`

### Common Issues
See `DASHBOARD_PRODUCTION_GRADE_COMPLETE.md` for detailed troubleshooting.

---

## ✅ Production Checklist

Before using in production:
- [x] Multi-user testing completed
- [x] Data validation implemented
- [x] Performance tested (<100ms SLA)
- [x] All API endpoints verified
- [x] Error handling improved
- [x] Real-time data refresh enabled
- [x] Monitoring script running
- [x] Documentation complete

---

**Status**: ✅ **PRODUCTION READY**
