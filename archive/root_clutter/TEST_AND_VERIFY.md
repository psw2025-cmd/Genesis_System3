# Test and Verify SSOT Implementation

## Quick Test

### 1. Start Backend with SSOT
```bash
# Option 1: Use the batch script
RESTART_WITH_SSOT.bat

# Option 2: Manual start
cd dashboard\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Run Validation Tests
```bash
# Option 1: Use the batch script
VALIDATE_SSOT_IMPLEMENTATION.bat

# Option 2: Manual run
python scripts\test_ssot_implementation.py
```

## Manual Verification

### 1. Test SSOT Endpoint
```bash
curl http://localhost:8000/api/state
```

**Expected:**
- Returns JSON with all required fields
- `state_version` increments on each request
- `data_source` is "SYNTHETIC" or "BROKER"
- `positions`, `pnl`, `qc`, `signals` are present

### 2. Test Synthetic Data
Open: http://localhost:8000/api/chain/NIFTY

**Check:**
- If `data_source` is "synthetic", IV should be 8-40% (not 1900-2400%)
- Greeks should be within bounds
- Timestamps should be ISO format

### 3. Test Risk Limits
```bash
curl -X POST http://localhost:8000/api/risk/check-limits -H "Content-Type: application/json" -d "{\"max_positions\": 5}"
```

**Check:**
- If you have 5 positions, should PASS (not breach)
- If you have 6 positions, should FAIL (breach)

### 4. Test Page Consistency

**Open Dashboard:** http://localhost:3000

**Check:**
1. **Overview Page:**
   - PnL should match Trading page
   - Positions count should match Trading page
   - QC status should match Signals page

2. **Signals Page:**
   - If positions exist, should show "MANAGING_POSITION"
   - Should show blocking reasons if no trade

3. **Risk Page:**
   - Should show Greeks from SSOT
   - Should show warning if Greeks are zero despite positions

4. **ML Page:**
   - Should show active model from SSOT
   - Should handle empty states gracefully

5. **Trading Page:**
   - Equity curve should not show "Invalid Date"
   - Timestamps should be valid

## Expected Results

### ✅ All Tests Should Pass

1. **SSOT Endpoint** - Returns valid state
2. **Synthetic Data** - IV 8-40%, realistic Greeks
3. **Risk Limits** - Only breaches when > limit
4. **Timestamps** - ISO format, no "Invalid Date"
5. **Page Consistency** - All pages show same data

## Troubleshooting

### Backend Not Starting
- Check if port 8000 is in use: `netstat -ano | findstr :8000`
- Kill process: `taskkill /F /PID <PID>`
- Check Python dependencies: `pip install -r requirements.txt`

### SSOT Not Working
- Check backend logs for errors
- Verify `runtime_state_store.py` exists
- Check `outputs/runtime_state.json` is being created

### Pages Showing Different Data
- Clear browser cache
- Check browser console for errors
- Verify all pages are using SSOT (check network tab)

## Success Criteria

✅ SSOT endpoint returns valid state
✅ Synthetic data has realistic IV (8-40%)
✅ Risk limits work correctly (breach only when > limit)
✅ No "Invalid Date" in equity curve
✅ All pages show consistent data

---

**If all tests pass, the SSOT implementation is working correctly!**
