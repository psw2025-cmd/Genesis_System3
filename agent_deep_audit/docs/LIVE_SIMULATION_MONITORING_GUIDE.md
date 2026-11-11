# Live Simulation Monitoring Guide

**Date**: 2026-01-31  
**Status**: ✅ Complete Implementation

---

## 📋 What Was Implemented

### 1. **Virtual Realistic Market Test Harness**
A complete simulation system that generates realistic option chain data at 5-second intervals, mimicking live market conditions.

**Key Components:**
- ✅ **Replay Engine** (`src/sim/replay_engine.py`) - Generates realistic market snapshots
- ✅ **8 Simulation Scenarios** - TREND_UP, TREND_DOWN, RANGE, HIGH_VOL, LOW_LIQUIDITY, DATA_ERROR, WS_FAIL, PARTIAL_FAILURE
- ✅ **Market Hours Detection** - Mon-Fri, 09:15-15:30 IST
- ✅ **Full Pipeline Integration** - QC → Ranking → Strategy → Exports → SQLite Storage

### 2. **Live Option Chain System**
Real-time option chain processing with:
- ✅ **WebSocket (Primary)** + **REST Fallback**
- ✅ **Weekly Expiry Prioritization**
- ✅ **Delta Computations** (dOI, dVolume, dMid, dSpread)
- ✅ **IV & Greeks Calculation** (Black-Scholes fallback)
- ✅ **OI Buildup Classification** (Long/Short Buildup, Covering, Unwinding)
- ✅ **Top Symbol Selector** - Ranks underlyings every cycle
- ✅ **Strategy Engine** - Recommends trading strategies
- ✅ **QC Validation** - Blocks trades on bad data

### 3. **Output Files Generated**
Every cycle (5 seconds by default), the system generates:

| File | Description | Update Frequency |
|------|-------------|------------------|
| `outputs/chain_raw_live.csv` | Full option chain data (Excel-ready) | Every 5s |
| `outputs/underlying_rank_live.csv` | Ranking of all indices | Every 5s |
| `outputs/top_trade_signal.json` | Best trade recommendation | Every 5s |
| `outputs/qc_report_live.json` | Quality control results | Every 5s |
| `logs/metrics.log` | One-line per cycle metrics | Every 5s |
| `storage/live/option_chain.db` | SQLite database snapshots | Every 5s |

---

## 🎯 How to Monitor Live Performance

### **Option 1: Real-Time Dashboard (Recommended)**

Run the live monitoring dashboard in a separate terminal:

```bash
# Terminal 1: Start simulation
python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5

# Terminal 2: Monitor live (run this in a new window)
python scripts/monitor_live_simulation.py
```

The dashboard shows:
- ✅ Current cycle number
- ✅ QC status (PASS/FAIL)
- ✅ Top underlying selected
- ✅ Trade action (TRADE/NO TRADE)
- ✅ Contract counts
- ✅ Real-time updates every 2 seconds

### **Option 2: Watch Logs in Real-Time**

**Windows PowerShell:**
```powershell
# Watch metrics log (one-line per cycle)
Get-Content logs\metrics.log -Wait -Tail 20

# Watch main log (detailed)
Get-Content logs\2026-01-31.log -Wait -Tail 50
```

**Windows CMD:**
```cmd
# Watch metrics log
powershell -Command "Get-Content logs\metrics.log -Wait -Tail 20"
```

### **Option 3: Monitor Output Files**

**Watch CSV files update:**
```powershell
# Check file size and last modified time
while ($true) {
    Clear-Host
    Get-ChildItem outputs\*.csv | Select-Object Name, Length, LastWriteTime
    Start-Sleep -Seconds 2
}
```

**Watch JSON files:**
```powershell
# Display latest trade signal
while ($true) {
    Clear-Host
    Get-Content outputs\top_trade_signal.json | ConvertFrom-Json | Format-List
    Start-Sleep -Seconds 5
}
```

### **Option 4: Excel Power Query (Real-Time)**

1. Open Excel
2. Data → Get Data → From File → From Text/CSV
3. Select `outputs/chain_raw_live.csv`
4. Click "Load"
5. Data → Refresh All (or press F5) every few seconds

**Auto-refresh setup:**
- Right-click the query → Properties
- Check "Refresh every X minutes" (set to 1 minute)
- Check "Refresh data when opening the file"

---

## 📊 Understanding the Outputs

### **1. chain_raw_live.csv**
Full option chain with all calculated columns:
- Contract info: `symbol`, `strike`, `expiry`, `option_type`
- Price data: `ltp`, `bidPrice`, `offerPrice`, `mid_price`
- Greeks: `delta`, `gamma`, `theta`, `vega`, `iv`
- Deltas: `dOI`, `dVolume`, `dMid`, `dSpread`
- OI Buildup: `oi_buildup_class`
- Calculated: `intrinsic_value`, `extrinsic_value`, `atm_distance`, etc.

### **2. underlying_rank_live.csv**
Ranking table showing:
- `underlying` - Index name (NIFTY, BANKNIFTY, etc.)
- `score` - Overall score (0-100)
- `liquidity_score` - Liquidity rating
- `signal_strength` - Signal quality
- `execution_quality` - Execution readiness
- `pcr` - Put-Call Ratio
- `expected_move` - Expected price movement
- `rank` - Ranking (1 = best)

### **3. top_trade_signal.json**
Best trade recommendation:
```json
{
  "action": "TRADE" or "NO TRADE",
  "strategy": "BUY_CE", "BUY_PE", "BULL_CALL_SPREAD", etc.,
  "underlying": "NIFTY",
  "strikes": [24500, 24600],
  "tokens": ["12345", "12346"],
  "entry_mid": 150.50,
  "stop_loss": 140.00,
  "target": 170.00,
  "confidence": 0.85,
  "reason": "Strong bullish signal with high liquidity"
}
```

### **4. qc_report_live.json**
Quality control results:
```json
{
  "overall_passed": true,
  "underlying_results": {
    "NIFTY": {
      "passed": true,
      "contract_count": 98,
      "reasons": []
    }
  },
  "timestamp_ist": "2026-01-31 01:17:27 IST"
}
```

### **5. metrics.log**
One-line per cycle:
```
2026-01-31 01:14:55 | CYCLE=5 | QC=PASS | TOP=NIFTY | ACTION=TRADE | UNDERLYINGS=4 | CONTRACTS=358
```

---

## 🚀 Quick Start Commands

### **Run Single Scenario (2 minutes)**
```bash
python -m scripts.replay_test --scenario TREND_UP --duration 2 --refresh 5
```

### **Run All Scenarios (40 minutes)**
```bash
run_sim_test.bat
```
Or:
```bash
python -m scripts.replay_test --all-scenarios --duration 5 --refresh 5
```

### **Run with Custom Settings**
```bash
python -m scripts.replay_test --scenario RANGE --duration 10 --refresh 3
```

### **Available Scenarios**
- `TREND_UP` - Bullish trending day
- `TREND_DOWN` - Bearish trending day
- `RANGE` - Sideways/neutral day
- `HIGH_VOL` - High volatility whipsaw
- `LOW_LIQUIDITY` - Wide spreads, low volume
- `DATA_ERROR` - Injected errors (QC should fail)
- `WS_FAIL` - Simulates WebSocket failure
- `PARTIAL_FAILURE` - One index missing

---

## 📈 Performance Metrics to Watch

### **Cycle Metrics (in metrics.log)**
- **CYCLE** - Cycle number (should increment)
- **QC** - PASS/FAIL (should be PASS for normal scenarios)
- **TOP** - Top underlying (should be stable, not flip every cycle)
- **ACTION** - TRADE/NO TRADE (should vary based on conditions)
- **UNDERLYINGS** - Number of indices processed (should be 4-5)
- **CONTRACTS** - Total contracts (should be 300-400)

### **Expected Behavior**
- ✅ **Normal scenarios**: QC=PASS, stable TOP, reasonable ACTION frequency
- ✅ **DATA_ERROR scenario**: QC=FAIL, ACTION=NO TRADE
- ✅ **TREND_UP/DOWN**: TOP should favor trending underlyings
- ✅ **RANGE**: More NO TRADE signals

---

## 🔍 Troubleshooting

### **No Output Files Generated**
- Check if simulation is running: `dir outputs\*.csv`
- Check logs: `type logs\2026-01-31.log | findstr ERROR`
- Verify base CSV exists: `dir option_chain_ALL_INDICES.csv`

### **QC Always Failing**
- Check `outputs/qc_report_live.json` for specific reasons
- Verify data quality in `chain_raw_live.csv`
- Check for missing columns or NaN values

### **No Trade Signals**
- Check `underlying_rank_live.csv` for scores
- Verify liquidity and signal strength values
- Check `top_trade_signal.json` for reason codes

---

## 📝 Files Created/Modified

### **New Files**
- `src/sim/replay_engine.py` - Simulation engine
- `scripts/replay_test.py` - Test runner
- `scripts/monitor_live_simulation.py` - Real-time monitor
- `src/output/metrics_logger.py` - Metrics logging
- `run_sim_test.bat` - Batch file for all scenarios

### **Modified Files**
- `scripts/run_live_chain.py` - Added sim_mode support
- `src/utils/market_hours.py` - Market hours detection
- `src/validation/qc_validator.py` - Enhanced validation

---

## ✅ Verification Checklist

After running simulation, verify:
- [ ] `outputs/chain_raw_live.csv` exists and has data
- [ ] `outputs/underlying_rank_live.csv` has rankings
- [ ] `outputs/top_trade_signal.json` has valid JSON
- [ ] `outputs/qc_report_live.json` shows QC results
- [ ] `logs/metrics.log` has cycle entries
- [ ] `storage/live/option_chain.db` exists (SQLite)

---

**Last Updated**: 2026-01-31  
**Status**: ✅ Production Ready
