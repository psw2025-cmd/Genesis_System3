# LIVE DRY-RUN LAUNCHER GUIDE

## Quick Start

```bash
cd C:\Genesis_System3
python tools/system3_live_dry_run_launcher.py
```

This launches an interactive helper that:
- ✅ Verifies all safety flags are set to DRY-RUN (False)
- ✅ Checks system health and required files
- ✅ Displays the day's checklist
- ✅ Provides quick access to troubleshooting guides
- ✅ Logs all pre-launch verification

**Duration:** ~5 minutes  
**No code changes:** Pure read-only status monitoring

---

## What This Script Does (NOT)

❌ **Does NOT:**
- Replace `run_system3.py` (the main menu)
- Modify any Phase 1–380 logic
- Execute trades or place orders
- Change safety flags
- Run the LIVE signals loop automatically

✅ **Does:**
- Verify safe configuration before you start
- Remind you of the step-by-step checklist
- Show expected output examples
- Provide quick troubleshooting reference
- Log all verification steps for audit

---

## Interactive Menu Options

After safety verification and pre-launch checks, you'll see:

```
1) Show pre-market checklist (print again)
2) Show expected output examples
3) Show troubleshooting guide
4) Generate session report
5) Open LIVE_DRY_RUN_DAY_PLAN.md in default viewer
0) Exit launcher (ready to start run_system3.py manually)
```

### Option 1: Pre-Market Checklist
Displays the full step-by-step timeline for the day (8:45 AM – 4:00 PM).
- Shows which menu option to run at each time
- Shows expected duration for each step
- Safe to print and reference during the day

### Option 2: Expected Output Examples
Shows sample console outputs you should expect to see from:
- Option 11 (LIVE AI signals)
- Option 12 (Synthetic backtest)
- Option 27 (Safety checks)

Useful for verifying that your run is progressing normally.

### Option 3: Troubleshooting Guide
Quick reference for common issues:
- Signals not generating → check AngelOne API
- Virtual orders not logging → check DRY-RUN flags
- Backtest crashes → try DEV profile or check plan file
- Reports not generating → ensure Option 11 still running

### Option 4: Generate Session Report
Creates a JSON file (`logs/live_dress_rehearsal/session_report_*.json`) documenting:
- What safety checks were run
- What files were verified
- What configuration was checked
- Timestamp of launcher execution

Useful for audit trail before starting the live day.

### Option 5: Open Plan Document
Opens `LIVE_DRY_RUN_DAY_PLAN.md` in your default text editor (Notepad).
- Full detailed reference guide
- All sections with expected outputs
- Complete troubleshooting appendix

### Option 0: Exit Launcher
Completes pre-launch verification and returns to command prompt.
- You are now ready to start `run_system3.py` manually
- Next command: `python run_system3.py`
- Then follow the printed checklist

---

## How Launcher Fits with run_system3.py

### Architecture

```
launcher.py (verification & checklist)
    ↓
    └─→ You start: python run_system3.py
            ↓
            ├─→ Option 2 (Health check)
            ├─→ Option 3 (Data pipeline test)
            ├─→ Option 109 (Phase 331-380 test)
            ├─→ Option 11 (LIVE signals) ← Keep running 6 hours
            ├─→ Option 12 (Backtest) ← Run periodically
            ├─→ Option 27 (Safety check) ← Run hourly
            ├─→ Option 28 (Outcome logger)
            ├─→ Option 36 (Daily report)
            ├─→ Option 37 (7-day dashboard)
            └─→ Option 40 (Auto-reports)
```

**Launcher:** One-time pre-launch verification (~5 min)  
**run_system3.py:** Main execution interface (6+ hours, then ~45 min reports)

They are **complementary, not competing:**
- Launcher helps you prepare and verify
- run_system3.py is where you actually run the live day
- You can run launcher as many times as needed
- run_system3.py runs independently

---

## Safety Verification Details

When you run the launcher, it checks:

### 1. Configuration Files
- `config/system3_trading_config.json`
  - `LIVE_TRADING_ENABLED` must be `False`
- `config/automation_config.json`
  - `auto_execute_trades` must be `False`
  - `USE_LIVE_EXECUTION_ENGINE` must be `False`

### 2. Environment Variables
- `LIVE_TRADING_ENABLED` environment variable must NOT be "true"

### 3. Directory Structure
- `storage/live/` exists (live CSV outputs)
- `storage/ultra/` exists (ultra phase outputs)
- `logs/` exists (execution logs)
- `models/` exists (trained models)

### 4. Required Files
- `config/angel_auth_config.json` (AngelOne credentials)
- `config/angel_instruments.csv` (instruments list)
- Trained model files in `models/` directory

### 5. CSV Files
- `angel_index_ai_signals.csv` (if has previous runs)
- `angel_virtual_orders.csv` (if has previous runs)
- `angel_index_ai_pnl_log.csv` (if has previous runs)

**Output:** Green checkmark (✅) for each item that passes, yellow warning (⚠️) for non-critical issues, red error (❌) for critical failures.

If any **critical failures** are found, launcher aborts and prevents run_system3.py.

---

## Log Files

All launcher actions are logged to:
```
logs/live_dress_rehearsal/live_dry_run_YYYYMMDD_HHMMSS.log
```

**What's Logged:**
- All safety verification steps
- File existence checks
- Configuration verification
- Menu selections and actions
- Session timestamps
- Any errors or warnings

**Use For:**
- Audit trail (what was checked before live day)
- Debugging (if something went wrong)
- Compliance (documented pre-launch verification)

---

## Typical Execution Timeline

```
8:40 AM — Run launcher.py (5 min)
         ↓ Verifies everything is safe
8:45 AM — Done with launcher
         ↓ User starts: python run_system3.py
         ↓ Follows the printed checklist
9:10 AM — Option 11 (LIVE signals) STARTS in background terminal
         ↓ Keep this running for 6 hours
3:20 PM — Option 11 STOPS (Ctrl+C)
         ↓ User runs report options (36, 37, 40)
3:40 PM — All reports generated
         ↓ User verifies data and archives
4:00 PM — LIVE DRY-RUN DAY COMPLETE ✅
```

---

## Troubleshooting the Launcher Itself

### Issue: "Module not found" error
**Solution:**
```bash
# Make sure you're in the project root directory
cd C:\Genesis_System3

# Then run:
python tools/system3_live_dry_run_launcher.py
```

### Issue: "Safety verification failed - aborting"
**Solution:**
```bash
# Check config/system3_trading_config.json
# Make sure these lines exist:
# "LIVE_TRADING_ENABLED": false,
# "USE_LIVE_EXECUTION_ENGINE": false,
# "auto_execute_trades": false,

# If missing, add them and try launcher again
python tools/system3_live_dry_run_launcher.py
```

### Issue: "Models not found" warning
**Solution:**
```bash
# Run Option 10 from run_system3.py first to train models:
python run_system3.py
# Then select Option 10

# After models are trained, run launcher again
python tools/system3_live_dry_run_launcher.py
```

### Issue: "AngelOne credentials incomplete"
**Solution:**
```bash
# Check config/angel_auth_config.json has:
# - "client_code": "YOUR_CLIENT_CODE"
# - "password": "YOUR_PASSWORD"
# - "api_key": "YOUR_API_KEY" (if needed)

# Add missing fields, then run launcher again
```

---

## Integration with Full System3

### Before Live Day
1. Run launcher to verify everything is ready
2. Review the printed checklist and save it
3. Start `run_system3.py` manually

### During Live Day
- Follow checklist from launcher output
- Option 11 (LIVE signals) runs in background
- Use other terminals for periodic checks (Options 12, 27, 28)
- Launcher is no longer needed

### After Live Day
- Generate reports (Options 36, 37, 40)
- Verify data integrity
- Archive results to `storage/archive/`
- Optional: Run launcher again for next day's preparation

---

## Key Takeaways

| Item | Purpose | Role |
|------|---------|------|
| **Launcher** | Pre-flight checklist | One-time, 5 min |
| **run_system3.py** | Actual execution | Main interface, 6+ hours |
| **LIVE_DRY_RUN_DAY_PLAN.md** | Detailed guide | Reference during day |
| **Safety flags** | Prevent live execution | Must all be False |
| **Log files** | Audit trail | Created automatically |

---

## FAQ

**Q: Do I need to run the launcher every time?**  
A: No. Run it once before your first live day to verify setup. After that, only run it if you change configuration files.

**Q: Can the launcher execute trades?**  
A: No. It only reads and verifies; it makes no changes to the system.

**Q: What if launcher says "DRY-RUN verified" but I still don't trust it?**  
A: Check the config files manually:
```bash
cat config/system3_trading_config.json | grep LIVE_TRADING_ENABLED
cat config/automation_config.json | grep auto_execute_trades
```
Should show `false` for both.

**Q: Where are the launcher logs?**  
A: `logs/live_dress_rehearsal/` directory. Each run creates a new timestamped log file.

**Q: Can launcher access real broker data?**  
A: Yes, it can TEST the AngelOne connection (Option 4 in run_system3.py), but it never submits orders.

**Q: How long does launcher take?**  
A: ~5 minutes. It's fast and doesn't run actual trading logic.

---

## Next Steps

1. **Verify Environment:**
   ```bash
   python tools/system3_live_dry_run_launcher.py
   ```

2. **Review Results:** Read the safety verification output

3. **Print the Checklist:** Save the printed checklist for reference

4. **Start Live Day:** When ready, run `python run_system3.py` and follow checklist

5. **Monitor Progress:** Watch CSVs and logs during the day using the guidance in LIVE_DRY_RUN_DAY_PLAN.md

---

**Status:** ✅ Ready for Live DRY-RUN Execution  
**Safety Mode:** DRY-RUN (All flags False)  
**Last Updated:** 2025-12-07

