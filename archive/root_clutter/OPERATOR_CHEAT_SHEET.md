# System3 Operator Cheat Sheet
**Production DRY-RUN Quick Reference**  
**Version:** 1.0  
**Last Updated:** 2025-12-05

---

## 🚀 Daily Startup (One Command)

```cmd
SYSTEM3_DAILY_START.bat
```

**What it does:**
1. ✅ Validates Python environment (3.10.11 required)
2. ✅ Checks critical dependencies (psutil, pandas, numpy, joblib, dotenv)
3. ✅ Runs pre-flight health check
4. ✅ Verifies DRY-RUN mode (LIVE_TRADING_ENABLED=False)
5. ✅ Validates data pipeline (forward returns CSV, models)
6. ✅ Updates heartbeat monitoring
7. ✅ Generates startup report
8. ✅ Offers launch options (interactive/autorun/watchdog/manual)

**Expected Time:** 10-15 seconds

---

## 📋 Pre-Flight Checklist

### Before Market Open
- [ ] Run `SYSTEM3_DAILY_START.bat`
- [ ] Verify all 6 phases show `[OK]` status
- [ ] Check startup log in `logs\system3_daily_start_YYYY-MM-DD_HHMM.log`
- [ ] Confirm DRY-RUN mode in output: `LIVE_TRADING_ENABLED=False`

### Critical Files to Monitor
```
✓ logs/system3_daily_start_*.log          ← Today's startup report
✓ system3_daily_heartbeat.json            ← Monitoring status
✓ storage/live/angel_index_ai_signals_with_forward.csv  ← Forward returns
✓ config/live_trade_config.py             ← DRY-RUN settings (NEVER edit during market hours)
```

---

## 🎯 Launch Modes

### Mode 1: Interactive Menu (Recommended for Operators)
```cmd
SYSTEM3_DAILY_START.bat → Option 1
```
- Access all 107 system operations via menu
- Run specific phases on-demand
- View real-time output
- **Use for:** Manual testing, specific phase execution

### Mode 2: Autorun Master (Automated Workflow)
```cmd
SYSTEM3_DAILY_START.bat → Option 2
```
- Runs pre-market phases (201-230) automatically
- Executes 30-minute interval phases (220-260) during market hours
- Autonomous operation with minimal supervision
- **Use for:** Daily production runs

### Mode 3: Watchdog Only (Monitoring)
```cmd
SYSTEM3_DAILY_START.bat → Option 3
```
- Process supervision and health monitoring
- Heartbeat updates every 60 seconds
- Auto-restart on crashes (if configured)
- **Use for:** Long-running monitoring sessions

### Mode 4: PowerShell Manual (Advanced)
```cmd
SYSTEM3_DAILY_START.bat → Option 4
```
- Opens PowerShell with venv activated
- Full manual control over commands
- **Use for:** Debugging, custom scripts, troubleshooting

---

## 🔍 Where to Look for Errors

### 1. Startup Errors (Most Common)
**Location:** `logs\system3_daily_start_*.log`

**Common Issues:**
```
[ERROR] Virtual environment not found
   → Fix: Run `python -m venv venv` in project root

[ERROR] Python check failed
   → Fix: Verify Python 3.10+ installed, check venv\Scripts\python.exe

[MISSING] psutil
   → Fix: Run `pip install -r requirements.txt`

[ERROR] LIVE TRADING IS ENABLED
   → Fix: Edit config/live_trade_config.py, set LIVE_TRADING_ENABLED = False
```

### 2. Phase Execution Errors
**Location:** `logs\system3_autorun.log` (if using autorun)

**Check for:**
```python
grep -i "ERROR" logs\system3_autorun.log
grep -i "FAILED" logs\system3_autorun.log
```

**Expected WARN statuses (safe to ignore):**
- Phase 222: Forward returns not available (until Phase 221 runs)
- Phase 239: Virtual orders CSV missing (expected before first trade simulation)
- Phases 249-260: Not implemented (documented gap)

### 3. Model Errors
**Location:** `logs\ml\*.log`

**Check:**
```
- core\models\angel_one\*.pkl files exist for NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX
- Model accuracy in logs (should be >60%)
- Training data size (minimum 200 samples)
```

### 4. Monitoring Errors
**Location:** `system3_daily_heartbeat.json`

**Check:**
```json
{
  "last_update": "2025-12-05T10:30:00",  ← Should be recent (within 5 minutes)
  "update_count": 42,                     ← Increments each cycle
  "system_health": "HEALTHY"              ← Should not be "DEGRADED" or "ERROR"
}
```

---

## ✅ Confirming a Clean Session

### Quick Validation (30 seconds)
```powershell
# 1. Check startup report
type logs\system3_daily_start_*.log | findstr "OK"
# Should see 6x "[OK]" for all phases

# 2. Verify DRY-RUN mode
python -c "from config.live_trade_config import LIVE_TRADING_ENABLED; print(f'DRY-RUN: {not LIVE_TRADING_ENABLED}')"
# Output: DRY-RUN: True

# 3. Check heartbeat
python system3_ultimate_heartbeat_manager.py --quick-status
# Should update without errors

# 4. Validate forward returns
python -m core.engine.system3_phase221_forward_returns
# Output: "Phase 221: Computed forward returns for XXX of YYY rows"

# 5. Test models
python -m core.engine.offline_angel_ai_test
# Should show predictions for all 5 underlyings
```

### Full Validation (5 minutes)
```powershell
# Run comprehensive validation
python run_validation_report.py

# Expected output:
#   ✓ Health Check: PASS
#   ✓ Psutil Dependency: PASS
#   ✓ Phase 221: Forward Returns: PASS
#   ✓ Heartbeat Manager: PASS
```

---

## 🛠️ Common Operations

### Run Specific Phase
```powershell
# Example: Run Phase 221 (Forward Returns)
python -m core.engine.system3_phase221_forward_returns
```

### Check Phase Status
```powershell
# View phase gaps analysis
type PHASE_GAPS_ANALYSIS.md | findstr "CRITICAL"
# Shows phases 249-260 as critical gap (expected)
```

### View Today's Signals
```powershell
# Check forward returns CSV
python -c "import pandas as pd; df=pd.read_csv('storage/live/angel_index_ai_signals_with_forward.csv'); print(f'{len(df)} signals, {df[\"underlying\"].nunique()} underlyings')"
```

### Check Model Status
```powershell
# List available models
dir core\models\angel_one\*.pkl

# Test model predictions
python -m core.engine.offline_angel_ai_test
```

### Monitor Live (Real-Time)
```powershell
# Tail autorun log
Get-Content logs\system3_autorun.log -Wait -Tail 20

# Tail watchdog log
Get-Content logs\system3_watchdog.log -Wait -Tail 20
```

---

## 📊 Expected Phase Behavior

### Pre-Market (Before 9:15 AM)
- Phases 201-230 run automatically (if using autorun)
- Expected: 25 OK, 6 WARN (normal)
- Duration: 3-5 minutes

### Market Hours (9:15 AM - 3:30 PM)
- Phases 220-260 run every 30 minutes (if using autorun)
- Expected: 10 OK, 21 SKIP (phases 249-260 not implemented yet)
- Duration: 2-3 minutes per cycle

### Post-Market (After 3:30 PM)
- No automatic phases unless explicitly triggered
- Good time for: Training models, analyzing results, reviewing logs

---

## 🚨 Safety Guardrails (Always Active)

### 1. DRY-RUN Enforcement
```python
# config/live_trade_config.py
LIVE_TRADING_ENABLED = False  # NEVER change to True in production DRY-RUN
AUTO_EXECUTE_TRADES = False   # Hardcoded safety
USE_LIVE_EXECUTION_ENGINE = False  # Additional safety layer
```

### 2. Safety Checks in Code
- 2,703 error handling references
- 1,527 logging references
- 369 heartbeat monitoring points
- 195 watchdog supervision points

### 3. No-Go Conditions (Abort if True)
- ❌ LIVE_TRADING_ENABLED = True
- ❌ Virtual environment missing
- ❌ Critical dependencies missing (psutil, pandas, numpy)
- ❌ Python version < 3.10

---

## 📈 Performance Benchmarks

### Startup Time
- Environment validation: 2-3 seconds
- Dependency check: 3-5 seconds
- Health check: 1-2 seconds
- **Total:** 10-15 seconds (first run may be slower)

### Phase Execution
- Phase 221 (Forward Returns): 5-10 seconds
- Phase 222 (Signal Edge): 3-5 seconds
- Phases 201-230 (Full Suite): 3-5 minutes
- Model predictions: 1-2 seconds per underlying

### Memory Usage
- Idle: ~200 MB
- Active (with models): ~500-800 MB
- Peak (training): ~1.5-2 GB

---

## 🆘 Emergency Procedures

### System Not Starting
1. Check Python version: `python --version` (need 3.10+)
2. Recreate venv: `rmdir /s venv`, then `python -m venv venv`
3. Reinstall dependencies: `venv\Scripts\pip install -r requirements.txt`
4. Verify project path in batch file

### Autorun Stuck
1. Press Ctrl+C to interrupt
2. Check logs: `type logs\system3_autorun.log`
3. Restart with: `SYSTEM3_DAILY_START.bat → Option 2`

### Models Not Loading
1. Check model files: `dir core\models\angel_one\*.pkl`
2. Retrain if missing: `python run_system3.py → Option 10`
3. Verify training data: `dir storage\training\*.csv`

### Data Pipeline Broken
1. Check forward returns: `dir storage\live\angel_index_ai_signals_with_forward.csv`
2. Regenerate: `python -m core.engine.system3_phase221_forward_returns`
3. Verify signals: `dir storage\live\angel_index_ai_signals.csv`

---

## 📚 Key Documentation

### Quick References
- **This Cheat Sheet:** `OPERATOR_CHEAT_SHEET.md` (you are here)
- **Phase Gaps:** `PHASE_GAPS_ANALYSIS.md` (143 missing phases documented)
- **Implementation Summary:** `PRIORITY_IMPLEMENTATION_SUMMARY.md` (all 5 priorities)
- **Validation Report:** `VALIDATION_REPORT.md` (latest test results)

### Deep Dives
- **Safety Audit:** `SYSTEM3_SAFETY_AUDIT.md` (DRY-RUN confirmation)
- **Phase References:** `SYSTEM3_PHASE_REFERENCES_AUDIT.md` (268 implemented)
- **Signal Pipeline:** `SYSTEM3_SIGNAL_PIPELINE_AUDIT.md` (pipeline flow)
- **Model Audit:** `SYSTEM3_MODEL_AUDIT.md` (ML/DL infrastructure)

### Configuration Files (Read-Only for Operators)
- `config/live_trade_config.py` - Trading settings (NEVER edit during market hours)
- `requirements.txt` - Python dependencies
- `system3_daily_heartbeat.json` - Monitoring status

---

## 🎓 Operator Training Checklist

- [ ] Can run `SYSTEM3_DAILY_START.bat` successfully
- [ ] Understands all 6 startup phases
- [ ] Can identify `[OK]` vs `[WARN]` vs `[ERROR]` status
- [ ] Knows where to find startup logs
- [ ] Can confirm DRY-RUN mode is active
- [ ] Can launch all 4 modes (interactive/autorun/watchdog/manual)
- [ ] Can run Phase 221 (forward returns) manually
- [ ] Can validate model predictions (offline AI test)
- [ ] Can check heartbeat status
- [ ] Knows how to tail live logs
- [ ] Can identify expected WARN statuses (phases 222, 239, 249-260)
- [ ] Can perform emergency restart procedures
- [ ] Understands safety guardrails (DRY-RUN enforcement)

---

## 📞 Support & Escalation

### Self-Service (Try First)
1. Read error message in startup log
2. Check this cheat sheet for common issues
3. Review relevant documentation (phase gaps, validation report)
4. Restart with `SYSTEM3_DAILY_START.bat`

### Escalation Triggers
- ❌ LIVE_TRADING_ENABLED = True (IMMEDIATE - abort all operations)
- ❌ Python environment completely broken (cannot start)
- ❌ All models missing or corrupted
- ❌ Data pipeline producing zero signals for >2 hours during market hours
- ❌ Heartbeat stopped updating for >10 minutes

### Contact
- **System Owner:** System3 Development Team
- **Emergency:** Check `config/live_trade_config.py` comments for contact info

---

**Remember:**
- ✅ **Always use DRY-RUN mode** (no real money at risk)
- ✅ **One command to start:** `SYSTEM3_DAILY_START.bat`
- ✅ **6 phases should show [OK]** in startup report
- ✅ **WARN statuses are often expected** (check documentation)
- ✅ **When in doubt, restart** - system is designed to be resilient

**System3 is production-ready for DRY-RUN operations. Follow this cheat sheet for smooth daily operations.**
