# Quick Start - Live Simulation Monitoring

## 🚀 Fastest Way to See Live Performance

### **Step 1: Start Simulation (Terminal 1)**
```bash
cd C:\Genesis_System3
venv\Scripts\activate
python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5
```

### **Step 2: Start Monitor (Terminal 2 - New Window)**
```bash
cd C:\Genesis_System3
venv\Scripts\activate
python scripts/monitor_live_simulation.py
```

**That's it!** You'll see:
- ✅ Real-time cycle updates
- ✅ QC status (PASS/FAIL)
- ✅ Top underlying selected
- ✅ Trade signals (TRADE/NO TRADE)
- ✅ File status and sizes
- ✅ Performance metrics

---

## 📊 What You'll See

### **Dashboard Shows:**
1. **Latest Cycle Metrics** - Current cycle number, QC status, top underlying
2. **Top Trade Signal** - Best trade recommendation with strategy
3. **Quality Control** - QC results for each underlying
4. **Underlying Rankings** - Top 3 ranked indices
5. **Output Files Status** - File sizes and last update times
6. **Status Summary** - Overall system health

### **Updates Every 2 Seconds**

---

## 🎯 Alternative: Watch Logs Directly

### **PowerShell (Recommended)**
```powershell
# Watch metrics (one-line per cycle)
Get-Content logs\metrics.log -Wait -Tail 20

# Watch detailed log
Get-Content logs\2026-01-31.log -Wait -Tail 50
```

### **Watch JSON Files**
```powershell
# Latest trade signal
while ($true) {
    Clear-Host
    Get-Content outputs\top_trade_signal.json | ConvertFrom-Json | Format-List
    Start-Sleep -Seconds 5
}
```

---

## 📁 Output Files Location

All outputs are in `outputs/` folder:
- `chain_raw_live.csv` - Full option chain (open in Excel)
- `underlying_rank_live.csv` - Rankings (open in Excel)
- `top_trade_signal.json` - Trade signal (open in text editor)
- `qc_report_live.json` - QC results (open in text editor)

---

## 🔍 Quick Verification

**Check if simulation is running:**
```bash
dir outputs\*.csv
dir outputs\*.json
type logs\metrics.log | findstr CYCLE
```

**Expected output:**
- CSV files exist and have data
- JSON files exist and are valid
- metrics.log has cycle entries

---

## ⚡ Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `python -m scripts.replay_test --scenario TREND_UP --duration 2 --refresh 5` | Run 2-minute test |
| `python scripts/monitor_live_simulation.py` | Start live monitor |
| `run_sim_test.bat` | Run all scenarios (40 min) |
| `Get-Content logs\metrics.log -Wait -Tail 20` | Watch metrics log |

---

**Need Help?** See `docs/LIVE_SIMULATION_MONITORING_GUIDE.md` for detailed guide.
