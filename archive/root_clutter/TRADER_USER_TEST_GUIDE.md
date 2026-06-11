# Trader & User Test Guide - Dashboard Verification

## 🎯 Purpose
This guide helps multiple traders and users verify all dashboard features are working correctly and visible in the UI.

---

## 📋 PRE-TEST CHECKLIST

### System Requirements
- ✅ Backend running on `http://localhost:8000` (or network IP)
- ✅ Frontend running on `http://localhost:3000` (or network IP)
- ✅ Browser: Google Chrome (recommended)
- ✅ Network access if testing from different machines

### Access Dashboard
1. Open browser: `http://localhost:3000` (or network IP)
2. Verify dashboard loads without errors
3. Check all navigation tabs are visible

---

## 🧪 FEATURE VERIFICATION TESTS

### **TEST 1: Overview Tab** ✅
**Location:** Home page (`/`)

**What to Check:**
- [ ] System status cards visible (Mode, Market Status, QC Status, Cycles)
- [ ] Data source badge visible (LIVE DATA or SYNTHETIC DATA)
- [ ] Trading stats visible (Trades Executed, Open Positions, Total PnL, Daily PnL)
- [ ] Performance SLA chart visible
- [ ] All data updates automatically (every 2 seconds)

**Expected Results:**
- All cards display data
- Badge shows correct data source
- Charts render properly
- No error messages

---

### **TEST 2: Chain Analytics Tab** ✅
**Location:** `/chain`

**What to Check:**
- [ ] Underlying selector works (NIFTY, BANKNIFTY, etc.)
- [ ] Data source badge visible
- [ ] Spot price displayed correctly
- [ ] Put-Call Ratio displayed
- [ ] Option chain table visible with contracts
- [ ] Filters work (Near ATM, Liquidity threshold)
- [ ] Data updates automatically

**Expected Results:**
- Can switch between underlyings
- Chain data loads and displays
- Filters reduce number of contracts
- No "Loading..." stuck state

---

### **TEST 3: Signals Tab** ✅
**Location:** `/signals`

**What to Check:**
- [ ] Top signal displayed
- [ ] Signal details visible (Action, Underlying, Strategy, Confidence)
- [ ] QC status displayed
- [ ] Signal updates automatically

**Expected Results:**
- Signal information displays correctly
- Confidence values show properly
- No crashes if confidence is missing

---

### **TEST 4: Trading Tab** ✅
**Location:** `/trading`

**What to Check:**
- [ ] Open positions table visible
- [ ] Position details displayed (ID, Symbol, Qty, Entry, Current, PnL)
- [ ] Equity curve chart visible
- [ ] PnL summary displayed
- [ ] Win rate chart visible
- [ ] Risk panel visible
- [ ] **NEW:** Predicted PnL card visible (top right)
- [ ] **NEW:** Profit validation status visible
- [ ] Close position button works

**Expected Results:**
- All positions display correctly
- Charts render properly
- PnL calculations are accurate
- Predictions and validations show

---

### **TEST 5: Alerts Tab** ✅ **NEW**
**Location:** `/alerts`

**What to Check:**
- [ ] Alerts list visible
- [ ] Unread count badge visible (if any)
- [ ] Alert types displayed (Price, Position, System, PnL, Risk)
- [ ] Alert severity colors correct (Critical=Red, Warning=Yellow, Info=Blue)
- [ ] Alert timestamps displayed
- [ ] Alerts update automatically

**Expected Results:**
- Alerts display correctly
- Colors match severity
- No errors loading alerts

---

### **TEST 6: Risk Dashboard Tab** ✅ **NEW**
**Location:** `/risk`

**What to Check:**
- [ ] Value at Risk (VaR) displayed
- [ ] Expected Shortfall displayed
- [ ] Total Exposure displayed
- [ ] Concentration Risk displayed
- [ ] Greeks Exposure section visible (Delta, Gamma, Theta, Vega)
- [ ] Risk Limits Status visible
- [ ] Breaches/Warnings displayed (if any)
- [ ] Underlying exposures listed

**Expected Results:**
- All risk metrics display
- Limits status shows PASS/WARN/FAIL
- Data updates automatically

---

### **TEST 7: Advanced Charts Tab** ✅ **NEW**
**Location:** `/charts`

**What to Check:**
- [ ] Underlying selector works
- [ ] Heatmap section visible
- [ ] Metric selector works (OI, Volume, IV, LTP)
- [ ] IV Surface section visible
- [ ] Greeks Chart section visible
- [ ] Greek selector works (Delta, Gamma, Theta, Vega)
- [ ] PCR Chart section visible
- [ ] All data loads correctly

**Expected Results:**
- All chart sections display
- Data loads for selected underlying
- Selectors work properly

---

### **TEST 8: ML Performance Tab** ✅ **NEW**
**Location:** `/ml`

**What to Check:**
- [ ] Model comparison section visible
- [ ] Best model highlighted
- [ ] All models listed with metrics
- [ ] Accuracy percentages displayed
- [ ] Confidence values displayed
- [ ] Prediction counts displayed

**Expected Results:**
- Model data displays correctly
- Metrics are accurate
- No errors if no models exist

---

### **TEST 9: Model Tab** ✅
**Location:** `/model`

**What to Check:**
- [ ] Model behavior data visible
- [ ] Performance metrics displayed
- [ ] Charts render properly

**Expected Results:**
- Model data displays
- No errors

---

### **TEST 10: Control Plane Tab** ✅
**Location:** `/control`

**What to Check:**
- [ ] System controls visible
- [ ] Settings accessible
- [ ] Controls work properly

**Expected Results:**
- Control panel functional
- No errors

---

## 🔍 DETAILED VERIFICATION CHECKLIST

### **Data Accuracy Verification**

#### Spot Price Verification
1. Go to Chain Analytics tab
2. Note the spot price for NIFTY
3. Compare with:
   - Yahoo Finance: https://finance.yahoo.com/quote/%5ENSEI
   - NSE Website: https://www.nseindia.com
4. **Expected:** Spot price should match within 0.1% tolerance

#### PnL Verification
1. Go to Trading tab
2. Note the Total PnL
3. Manually calculate: Sum of all position unrealized PnL + Realized PnL
4. **Expected:** Should match exactly

#### Position Data Verification
1. Go to Trading tab
2. Check each position's:
   - Entry price
   - Current price
   - Unrealized PnL = (Current - Entry) × Qty
3. **Expected:** Calculations should match

---

### **Real-Time Updates Verification**

1. Open dashboard in browser
2. Watch any tab for 10 seconds
3. **Expected:** Data should update automatically (every 2-5 seconds)
4. Check browser console (F12) for errors
5. **Expected:** No continuous errors

---

### **Market Status Verification**

#### When Market is Open
1. Check Overview tab
2. **Expected:** Badge shows "✅ LIVE DATA" (green)
3. Check Chain Analytics tab
4. **Expected:** Badge shows "✅ LIVE MARKET DATA" (green)
5. Data should be real-time

#### When Market is Closed
1. Check Overview tab
2. **Expected:** Badge shows "📊 SYNTHETIC DATA" (yellow)
3. Check Chain Analytics tab
4. **Expected:** Badge shows "📊 SYNTHETIC DATA (Market Closed)" (yellow)
5. Data should still display (synthetic)

---

### **Multi-User Testing**

#### Test Concurrent Access
1. **User 1:** Open dashboard on Machine 1
2. **User 2:** Open dashboard on Machine 2 (different IP if possible)
3. **User 3:** Open dashboard on Machine 3
4. All users navigate through all tabs simultaneously
5. **Expected:** 
   - All users see same data
   - No crashes
   - No data inconsistencies
   - All features work for all users

#### Test Data Consistency
1. Multiple users check same metric (e.g., Total PnL)
2. Compare values across users
3. **Expected:** All users see same value

---

## 📊 FEATURE-SPECIFIC TESTS

### **Alerts System Test**
1. Go to Alerts tab
2. **Expected:** Alerts list displays
3. Check if alerts are categorized correctly
4. **Expected:** Alerts show correct type and severity

### **Risk Dashboard Test**
1. Go to Risk tab
2. **Expected:** All risk metrics display
3. Check if VaR and Expected Shortfall are calculated
4. **Expected:** Values are reasonable (not zero if positions exist)

### **Advanced Charts Test**
1. Go to Charts tab
2. Select different underlyings
3. **Expected:** Data loads for each underlying
4. Change metric selector
5. **Expected:** Heatmap data updates
6. Change Greek selector
7. **Expected:** Greeks data updates

### **ML Performance Test**
1. Go to ML tab
2. **Expected:** Model comparison displays
3. Check if best model is highlighted
4. **Expected:** Metrics are displayed correctly

### **Profit Prediction Test**
1. Go to Trading tab
2. **Expected:** Predicted PnL card visible (top right)
3. Check predicted value
4. **Expected:** Value is reasonable

### **Profit Validation Test**
1. Go to Trading tab
2. **Expected:** Profit validation status visible
3. Check Pass/Warn/Fail counts
4. **Expected:** Status matches actual validation

---

## 🐛 COMMON ISSUES TO CHECK

### Issue 1: "Loading..." Stuck
**Symptom:** Page shows "Loading..." indefinitely
**Check:**
- Browser console for errors
- Backend is running
- Network connectivity
- API endpoint accessibility

### Issue 2: Data Not Updating
**Symptom:** Data stays the same
**Check:**
- Browser console for errors
- Network tab shows API calls
- Backend is processing data
- Refresh interval is working

### Issue 3: CORS Errors
**Symptom:** Browser console shows CORS errors
**Check:**
- Backend CORS settings
- Frontend and backend URLs match
- Network access if testing from different machine

### Issue 4: Missing Features
**Symptom:** New tabs/features not visible
**Check:**
- Frontend is rebuilt (`npm run build` or `npm run dev`)
- Browser cache cleared
- All components imported correctly

---

## ✅ TEST RESULTS TEMPLATE

### Trader/User Information
- **Name:** ________________
- **Date:** ________________
- **Time:** ________________
- **Browser:** ________________
- **Machine IP:** ________________

### Test Results

| Feature | Status | Notes |
|---------|--------|-------|
| Overview Tab | ✅/❌ | |
| Chain Analytics | ✅/❌ | |
| Signals Tab | ✅/❌ | |
| Trading Tab | ✅/❌ | |
| Alerts Tab | ✅/❌ | |
| Risk Dashboard | ✅/❌ | |
| Advanced Charts | ✅/❌ | |
| ML Performance | ✅/❌ | |
| Model Tab | ✅/❌ | |
| Control Plane | ✅/❌ | |
| Data Accuracy | ✅/❌ | |
| Real-Time Updates | ✅/❌ | |
| Market Status Detection | ✅/❌ | |
| Multi-User Access | ✅/❌ | |

### Issues Found
1. ________________________________
2. ________________________________
3. ________________________________

### Recommendations
1. ________________________________
2. ________________________________
3. ________________________________

---

## 🎯 QUICK TEST SCENARIO

### 5-Minute Quick Test
1. **Open Dashboard** → Check Overview tab loads
2. **Navigate to Chain** → Verify chain data displays
3. **Navigate to Trading** → Verify positions and PnL
4. **Navigate to Alerts** → Verify alerts display
5. **Navigate to Risk** → Verify risk metrics
6. **Navigate to Charts** → Verify charts load
7. **Navigate to ML** → Verify ML data
8. **Check Data Source Badges** → Verify correct badge (Live/Synthetic)
9. **Wait 10 seconds** → Verify auto-refresh works
10. **Check Browser Console** → Verify no errors

**Expected:** All steps pass without errors

---

## 📝 REPORTING ISSUES

### When Reporting Issues, Include:
1. **Feature/Tab:** Which tab or feature
2. **Steps to Reproduce:** What you did
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happened
5. **Screenshot:** If possible
6. **Browser Console Errors:** Copy any errors
7. **Browser/OS:** Chrome version, Windows version
8. **Time:** When the issue occurred

---

## 🚀 TESTING COMMANDS

### Start Backend
```bash
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd dashboard\frontend
npm run dev
```

### Access Dashboard
- Local: `http://localhost:3000`
- Network: `http://<YOUR_IP>:3000`

---

## ✅ SUCCESS CRITERIA

### All Tests Pass If:
- ✅ All 10 tabs load without errors
- ✅ All features display correctly
- ✅ Data updates automatically
- ✅ Data source badges show correctly
- ✅ Multi-user access works
- ✅ Data accuracy verified
- ✅ No console errors
- ✅ All new features visible

---

**Last Updated:** 2026-02-06  
**Status:** Ready for Multi-User Testing
