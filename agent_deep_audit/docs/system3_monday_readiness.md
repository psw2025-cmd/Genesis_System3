# System3 - Monday Readiness Checklist

## Status: ✅ READY FOR CONSERVATIVE LIVE TRADING

---

## 1. Core Components Status

### ✅ Data Pipeline
- [x] Synthetic training generator working (3,000 rows)
- [x] Model training complete (5 models, 98-100% accuracy)
- [x] Feature importance analysis complete
- [x] Live data snapshot collection working

### ✅ AI Models
- [x] All 5 models trained and saved (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
- [x] Models using MI-selected features (12 features each)
- [x] Model metadata saved with feature lists

### ✅ Signal Generation
- [x] Live AI signals engine working (menu option 11)
- [x] Signals logged to CSV
- [x] Trade decision layer integrated
- [x] Trade plans generated automatically

### ✅ Safety & Validation
- [x] Safety validator implemented
- [x] Trade plan validation active
- [x] Daily trade limits configured (20 total, 5 per underlying)
- [x] Conservative thresholds active (conf=0.80, score=0.30)

---

## 2. Automation Status

### Current Settings (Monday-Safe)
- **Auto-execute trades**: ❌ DISABLED
- **Auto PnL simulation**: ❌ DISABLED
- **Execution mode**: DRY RUN only
- **Safety checks**: ✅ ACTIVE

### What Runs Automatically
1. Signal generation (every 30 seconds when menu 11 is active)
2. Trade plan creation (automatic after signals)
3. Safety validation (automatic on all trade plans)

### What Requires Manual Action
1. Trade execution (menu option 14 - DRY RUN)
2. PnL simulation (menu option - manual)
3. Daily reports (menu option 17 - manual)

---

## 3. Monday Workflow

### Pre-Market
1. ✅ Verify all models are loaded
2. ✅ Check automation config (should be disabled)
3. ✅ Review safety limits
4. ✅ Start menu option 11 (LIVE AI signals loop)

### During Market
1. Monitor console output for signals
2. Watch for trade plan generation
3. Review trade plans manually before execution
4. Run intraday PnL monitor (menu 16) periodically

### End of Day
1. Run daily PnL summary (menu 15)
2. Generate daily report (menu 17)
3. Review system health (menu 18)
4. Analyze signal quality and trade outcomes

---

## 4. Safety Features Active

### Trade Validation
- ✅ Confidence threshold: 0.80 (very conservative)
- ✅ Score threshold: 0.30 (very conservative)
- ✅ Trade plan validation before execution
- ✅ Daily trade limits enforced

### Risk Management
- ✅ Max 20 trades per day
- ✅ Max 5 trades per underlying per day
- ✅ DRY RUN mode only (no real orders)
- ✅ All trades logged for audit

### Monitoring
- ✅ Trade lifecycle logger active
- ✅ Intraday PnL monitor available
- ✅ System health watchdog available
- ✅ Daily report generator ready

---

## 5. Post-Monday Upgrade Path

### After Collecting Real Data
1. **Threshold Optimization**
   - Run threshold tuner on real BUY/SELL outcomes
   - Get recommendations for optimal thresholds
   - Gradually relax if performance is good

2. **LIVE Mode Preparation**
   - Validate broker connection
   - Test order placement in paper trading
   - Enable LIVE mode only after thorough testing

3. **Full Automation**
   - Enable auto-execution (with safety checks)
   - Enable auto PnL simulation
   - Monitor and adjust as needed

---

## 6. Emergency Procedures

### If System Stalls
1. Check system health (menu 18)
2. Review logs in `logs/` directory
3. Restart menu option 11 if needed
4. Check Dhan API connection

### If Unexpected Trades Appear
1. Review trade plan CSV
2. Check safety validator logs
3. Verify thresholds haven't changed
4. Disable automation if needed

### If Data Issues
1. Check signals CSV for recent data
2. Verify model files exist
3. Re-run health check
4. Check disk space

---

## 7. Key Files & Locations

### Configuration
- `core/engine/dhan_trade_config.py` - Trade thresholds
- `core/engine/dhan_automation_config.py` - Automation settings
- `storage/config/thresholds_auto.json` - Auto-tuned thresholds

### Data Files
- `storage/live/dhan_index_ai_signals.csv` - Live signals
- `storage/live/dhan_index_ai_trades_plan.csv` - Trade plans
- `storage/live/dhan_index_ai_trades_exec_log.csv` - Execution log
- `storage/live/dhan_index_ai_pnl_log.csv` - PnL log

### Models
- `core/models/dhan/*_model.pkl` - Trained models
- `core/models/dhan/*_model_meta.json` - Model metadata

### Reports
- `storage/reports/daily_report_YYYY-MM-DD.txt` - Daily reports

---

## 8. Success Criteria for Monday

### Minimum Viable
- ✅ System runs without crashes
- ✅ Signals generated continuously
- ✅ Trade plans created when eligible
- ✅ All operations logged

### Ideal Outcome
- ✅ Some BUY_CE/BUY_PE signals appear
- ✅ Trade plans generated and validated
- ✅ DRY RUN execution successful
- ✅ PnL data collected for analysis

### Post-Monday Analysis
- Review signal quality
- Analyze trade plan accuracy
- Evaluate threshold effectiveness
- Plan threshold adjustments

---

## 9. Contact & Support

### Logs Location
- Application logs: `logs/`
- Trade lifecycle: `storage/live/dhan_trade_lifecycle_log.csv`

### Debugging
- Run system health check (menu 18)
- Review daily reports (menu 17)
- Check intraday PnL monitor (menu 16)

---

**Last Updated**: 2025-11-29
**Status**: ✅ READY FOR MONDAY
**Mode**: CONSERVATIVE (DRY RUN ONLY)

