# Auto Market Detection & Synthetic Data System - COMPLETE

## Overview
The dashboard system now **automatically detects market status** and seamlessly switches between:
- **Real market data** when market is open (9:15 AM - 3:30 PM IST)
- **Synthetic data** when market is closed (nights, weekends, holidays)

This ensures the dashboard is **always functional** and provides a **production-grade experience** regardless of market hours.

---

## Features Implemented

### 1. Automatic Market Detection ✅
- Uses `src/utils/market_hours.py` to detect market status
- Checks:
  - Time of day (9:15 AM - 3:30 PM IST)
  - Weekends (Saturday/Sunday)
  - Trading holidays
  - Special trading days

### 2. Synthetic Data Generator ✅
- **Location:** `dashboard/backend/synthetic_data_generator.py`
- Generates realistic option chain data with:
  - Realistic strike prices (±20 strikes around ATM)
  - Multiple expiry dates (weekly expiries)
  - Calculated option premiums (Black-Scholes approximation)
  - Greeks (Delta, Gamma, Theta, Vega)
  - OI and Volume (higher near ATM)
  - Bid/Ask spreads
  - Implied Volatility

### 3. Seamless Data Switching ✅
- **Backend automatically switches** between real and synthetic data
- **No manual intervention** required
- **Transparent to frontend** - dashboard works identically in both modes

### 4. Data Source Indicators ✅
- **Frontend shows clear indicators:**
  - 🟢 **"✅ LIVE MARKET DATA"** - Green badge when using real data
  - 🟡 **"📊 SYNTHETIC DATA (Market Closed)"** - Yellow badge when using synthetic data
- **Backend API responses** include `data_source` field:
  - `"data_source": "real"` - Real market data
  - `"data_source": "synthetic"` - Synthetic data

---

## Modified Files

### Backend
1. **`dashboard/backend/app.py`**
   - Added market detection imports
   - Added synthetic data generator imports
   - Modified `/api/health` to use synthetic data when market closed
   - Modified `/api/chain/{underlying}` to use synthetic data when market closed
   - Modified `/api/qc` to use synthetic data when market closed
   - Modified `/api/signal/top` to use synthetic data when market closed
   - Modified `/api/perf` to use synthetic data when market closed
   - All endpoints now include `data_source` field

### Frontend
2. **`dashboard/frontend/src/components/Overview.tsx`**
   - Added `data_source` to HealthData interface
   - Added data source indicator badge in Market Status card

3. **`dashboard/frontend/src/components/ChainAnalytics.tsx`**
   - Added data source detection
   - Added data source indicator badge in header
   - Removed "Market Closed" error message (now shows synthetic data instead)

### New Files
4. **`dashboard/backend/synthetic_data_generator.py`**
   - Complete synthetic data generation system
   - Functions:
     - `generate_synthetic_chain_data()` - Option chain data
     - `generate_synthetic_health_data()` - Health metrics
     - `generate_synthetic_qc_data()` - QC reports
     - `generate_synthetic_signal_data()` - Trade signals
     - `generate_synthetic_perf_data()` - Performance metrics

---

## How It Works

### Market Open (9:15 AM - 3:30 PM IST, Weekdays)
1. Backend detects market is open
2. Fetches real data from:
   - `outputs/chain_raw_live.csv`
   - `outputs/health.json`
   - `outputs/qc_report_live.json`
   - `outputs/top_trade_signal.json`
   - `outputs/perf_metrics.json`
3. Returns data with `"data_source": "real"`
4. Frontend shows **"✅ LIVE MARKET DATA"** badge

### Market Closed (Nights, Weekends, Holidays)
1. Backend detects market is closed
2. Generates synthetic data using `synthetic_data_generator.py`
3. Returns data with `"data_source": "synthetic"`
4. Frontend shows **"📊 SYNTHETIC DATA (Market Closed)"** badge
5. Dashboard works **exactly the same** as with real data

### Automatic Switching
- **No restart required** - switching happens automatically
- **Seamless transition** - frontend updates every 2-5 seconds
- **No data loss** - synthetic data maintains same structure as real data

---

## Testing

### Test Market Detection
```bash
python -c "import sys; sys.path.insert(0, 'src'); from utils.market_hours import is_market_open; print(is_market_open())"
```

### Test Synthetic Data
```bash
# Start backend
cd dashboard/backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# In another terminal, test API (when market is closed)
curl http://localhost:8000/api/chain/NIFTY
# Should return synthetic data with "data_source": "synthetic"
```

### Test Frontend
1. Start backend: `python -m uvicorn app:app --host 0.0.0.0 --port 8000`
2. Start frontend: `npm run dev`
3. Open dashboard: `http://localhost:3000`
4. Check for data source indicator badges

---

## Production Benefits

### ✅ Always Functional
- Dashboard works 24/7, even when market is closed
- No "Market Closed" errors or empty screens
- Full functionality available at all times

### ✅ Realistic Data
- Synthetic data uses realistic option pricing models
- Maintains same data structure as real data
- Allows testing and development during off-hours

### ✅ Seamless Experience
- Automatic switching - no manual intervention
- Clear indicators show data source
- Same UI/UX in both modes

### ✅ Production-Grade
- Robust error handling
- Fallback to real data if synthetic generation fails
- Proper market detection with timezone handling

---

## Configuration

### Market Hours
- **Open:** 9:15 AM IST
- **Close:** 3:30 PM IST
- **Timezone:** Asia/Kolkata (IST)

### Synthetic Data Parameters
- **Base Spot Prices:** Configurable in `synthetic_data_generator.py`
- **Strike Intervals:** Per underlying (NIFTY: 50, BANKNIFTY: 100, etc.)
- **Expiry Dates:** Weekly expiries (Thursdays)

### Update Base Prices
Edit `BASE_SPOT_PRICES` in `synthetic_data_generator.py`:
```python
BASE_SPOT_PRICES = {
    'NIFTY': 24000.0,      # Update to current levels
    'BANKNIFTY': 52000.0,  # Update to current levels
    # ...
}
```

---

## Future Enhancements

### Optional Improvements
1. **Historical Data Integration:** Use last known real prices as base for synthetic data
2. **Volatility Surface:** Generate more realistic IV curves
3. **Market Microstructure:** Add realistic bid-ask spreads and order book depth
4. **Time Decay:** Simulate theta decay in synthetic data
5. **News Events:** Simulate market reactions to news

---

## Status

✅ **COMPLETE AND PRODUCTION-READY**

- All features implemented
- Automatic market detection working
- Synthetic data generation working
- Seamless switching working
- Frontend indicators working
- Tested and verified

**System is ready for production use!**

---

## Support

If you encounter any issues:
1. Check market detection: `python -c "from src.utils.market_hours import is_market_open; print(is_market_open())"`
2. Check backend logs for import errors
3. Verify synthetic data generator is accessible
4. Check frontend console for API errors

---

**Last Updated:** 2026-02-06  
**Status:** ✅ Production Ready
