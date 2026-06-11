# Market Open Time - Complete Workflow

## 🕐 Market Opening Time (IST)
- **Pre-Market:** 9:00 AM - 9:15 AM
- **Market Open:** 9:15 AM
- **Market Close:** 3:30 PM
- **Post-Market:** 3:30 PM - 4:00 PM

---

## 🔄 COMPLETE MARKET OPEN WORKFLOW

### **PHASE 1: Pre-Market (9:00 AM - 9:15 AM)**

#### **System Status:**
- ✅ Dashboard running with **SYNTHETIC DATA**
- ✅ All features operational
- ✅ Monitor actively checking every 30 seconds
- ✅ Backend ready for market data

#### **What Happens:**
1. **Market Detection:**
   - System checks market hours every cycle
   - `is_market_open()` function evaluates:
     - Current time vs market hours (9:15 AM - 3:30 PM IST)
     - Day of week (Monday-Friday)
     - Holiday calendar check
     - Pre-market/post-market periods

2. **Data Source:**
   - Currently: **SYNTHETIC**
   - API endpoints return `data_source: "synthetic"`
   - Frontend displays: **"📊 SYNTHETIC DATA (Market Closed)"** badge

3. **System Readiness:**
   - Backend health checks passing
   - Frontend accessible
   - All API endpoints responding
   - Monitor tracking system status

---

### **PHASE 2: Market Opening Detection (9:15 AM)**

#### **Automatic Detection:**
When the clock hits **9:15 AM IST**:

1. **Market Hours Check:**
   ```python
   # In market_hours.py
   current_time = datetime.now(IST)
   market_open_time = current_time.replace(hour=9, minute=15, second=0)
   
   if current_time >= market_open_time and current_time < market_close_time:
       return "OPEN"
   ```

2. **Status Change:**
   - `is_market_open()` returns `True`
   - Market status changes: `"closed"` → `"open"`
   - System mode remains: `"LIVE"`

3. **Data Source Switch:**
   - Backend detects market is now open
   - Switches from synthetic to real data
   - API endpoints start returning `data_source: "real"`

---

### **PHASE 3: Data Source Transition (9:15 AM - 9:16 AM)**

#### **What Happens:**

1. **Backend API Changes:**
   - All endpoints check `is_market_open()` first
   - If market is open:
     - Reads from `chain_raw_live.csv` (real data)
     - Fetches live data from broker API
     - Updates positions with real prices
     - Calculates real-time PnL

2. **Frontend Updates:**
   - Badge changes: **"📊 SYNTHETIC DATA"** → **"✅ LIVE MARKET DATA"**
   - Color changes: Yellow → Green
   - Data refreshes automatically (every 2-5 seconds)

3. **API Endpoints Affected:**
   - `/api/health` → Returns `data_source: "real"`
   - `/api/chain/{underlying}` → Returns real option chain data
   - `/api/positions` → Returns positions with real-time prices
   - `/api/pnl` → Calculates PnL from real prices
   - `/api/signal/top` → Generates signals from real data
   - `/api/perf` → Tracks performance with real data

---

### **PHASE 4: Market Open Operations (9:15 AM - 3:30 PM)**

#### **Continuous Operations:**

1. **Data Fetching:**
   - **Every 5 seconds:** Main system fetches option chain data
   - **Real-time:** WebSocket connections for live prices
   - **REST Fallback:** If WebSocket fails
   - **Data Storage:** Updates `chain_raw_live.csv`

2. **Signal Generation:**
   - ML models analyze real market data
   - Generate trading signals with confidence scores
   - Risk management validates signals
   - Paper trading executes qualified signals

3. **Position Management:**
   - Real-time PnL calculation
   - Stop-loss and target monitoring
   - Position sizing based on real prices
   - Risk limit checks

4. **Dashboard Updates:**
   - **Overview Tab:** Real-time system status
   - **Chain Tab:** Live option chain data
   - **Trading Tab:** Real positions and PnL
   - **Alerts Tab:** Real-time alerts
   - **Risk Tab:** Real-time risk metrics
   - **Charts Tab:** Live charting data

5. **Monitoring:**
   - 24-hour monitor checks every 30 seconds
   - Verifies data source is "real"
   - Tracks market status
   - Logs all events

---

### **PHASE 5: Market Closing Detection (3:30 PM)**

#### **Automatic Detection:**
When the clock hits **3:30 PM IST**:

1. **Market Hours Check:**
   ```python
   market_close_time = current_time.replace(hour=15, minute=30, second=0)
   
   if current_time >= market_close_time:
       return "CLOSED"
   ```

2. **Status Change:**
   - `is_market_open()` returns `False`
   - Market status changes: `"open"` → `"closed"`
   - System switches back to synthetic data

3. **Data Source Switch:**
   - Backend detects market is closed
   - Switches from real to synthetic data
   - API endpoints return `data_source: "synthetic"`

---

### **PHASE 6: Post-Market (3:30 PM - Next Day)**

#### **System Status:**
- ✅ Dashboard continues running with **SYNTHETIC DATA**
- ✅ All features remain operational
- ✅ Monitor continues tracking
- ✅ System ready for next market open

---

## 📊 DETAILED TRANSITION LOGIC

### **Backend Code Flow:**

```python
# In app.py - get_chain() endpoint
def get_chain(underlying: str):
    # 1. Check market status
    market_status = is_market_open()
    
    # 2. If market is closed, use synthetic data
    if not market_status:
        synthetic_data = generate_synthetic_chain(underlying)
        return {
            "status": "ok",
            "data_source": "synthetic",
            "chain": synthetic_data
        }
    
    # 3. If market is open, use real data
    try:
        real_data = read_chain_from_csv(underlying)
        return {
            "status": "ok",
            "data_source": "real",
            "chain": real_data
        }
    except:
        # Fallback to synthetic if real data unavailable
        return generate_synthetic_chain(underlying)
```

### **Market Hours Detection:**

```python
# In market_hours.py
def is_market_open():
    now = datetime.now(IST)
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False
    
    # Check if holiday
    if is_holiday(now.date()):
        return False
    
    # Check market hours (9:15 AM - 3:30 PM IST)
    market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
    market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
    
    return market_open <= now < market_close
```

---

## 🔍 MONITORING DURING MARKET OPEN

### **What Gets Monitored:**

1. **Market Status:**
   - Open/Closed detection
   - Transition timing
   - Data source accuracy

2. **Data Quality:**
   - Real data availability
   - Data freshness
   - Price accuracy

3. **System Health:**
   - Backend responsiveness
   - Frontend accessibility
   - API endpoint status

4. **Performance:**
   - Response times
   - Data fetch latency
   - Signal generation speed

---

## 📝 LOGGED EVENTS

### **Market Open Events:**
- `market_opened` - Market transition detected
- `data_source_changed` - Switched to real data
- `real_data_fetch_started` - Started fetching real data
- `all_endpoints_verified` - All endpoints verified with real data

### **During Market Hours:**
- `real_data_fetched` - Real data fetched successfully
- `signal_generated` - Trading signal generated
- `position_opened` - New position opened
- `position_closed` - Position closed
- `pnl_updated` - PnL calculated with real prices

### **Market Close Events:**
- `market_closed` - Market transition detected
- `data_source_changed` - Switched to synthetic data
- `synthetic_data_active` - Synthetic data generation active

---

## ✅ VERIFICATION CHECKLIST

### **Before Market Open:**
- [ ] System running with synthetic data
- [ ] All endpoints responding
- [ ] Monitor active
- [ ] Frontend accessible

### **At Market Open (9:15 AM):**
- [ ] Market status changes to "open"
- [ ] Data source changes to "real"
- [ ] Frontend badge updates to green
- [ ] Real data starts flowing
- [ ] All endpoints return real data

### **During Market Hours:**
- [ ] Real-time data updates
- [ ] Positions update with real prices
- [ ] PnL calculated correctly
- [ ] Signals generated from real data
- [ ] Risk metrics accurate

### **At Market Close (3:30 PM):**
- [ ] Market status changes to "closed"
- [ ] Data source changes to "synthetic"
- [ ] Frontend badge updates to yellow
- [ ] System continues running
- [ ] Synthetic data active

---

## 🎯 KEY POINTS

### **Automatic & Seamless:**
- ✅ No manual intervention needed
- ✅ Automatic market detection
- ✅ Seamless data source switching
- ✅ Continuous operation 24/7

### **Real-Time Updates:**
- ✅ Data refreshes every 5 seconds
- ✅ Frontend updates every 2 seconds
- ✅ Monitor checks every 30 seconds
- ✅ All changes logged

### **Reliability:**
- ✅ Fallback to synthetic if real data unavailable
- ✅ Auto-recovery if services fail
- ✅ Comprehensive error handling
- ✅ Full event logging

---

## 📊 EXPECTED BEHAVIOR SUMMARY

| Time | Market Status | Data Source | Frontend Badge | System State |
|------|--------------|-------------|----------------|--------------|
| 9:00 AM | Closed | Synthetic | 📊 Yellow | Pre-Market |
| 9:15 AM | **OPEN** | **Real** | ✅ Green | **Market Open** |
| 9:15 AM - 3:30 PM | Open | Real | ✅ Green | Trading Active |
| 3:30 PM | **CLOSED** | **Synthetic** | 📊 Yellow | **Market Closed** |
| 3:30 PM - 9:15 AM | Closed | Synthetic | 📊 Yellow | Post-Market |

---

**Last Updated:** 2026-02-06  
**Status:** ✅ Complete Workflow Documented  
**Next Market Open:** Automatic Detection at 9:15 AM IST
