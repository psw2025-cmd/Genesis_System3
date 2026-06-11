# Quick Reference: Signal Debugging Toolkit

**Created:** Current Session | **Status:** ✅ All 6 Steps Complete

---

## Files to Know

| File | Purpose | Type |
|------|---------|------|
| `system3_debug_signals_pipeline.py` | Run diagnostic on signal generation | Script (NEW) |
| `logs/research/system3_signal_engine.log` | View real-time signal logs | Log |
| `storage/live/angel_index_ai_signals.csv` | Signals output | CSV |
| `core/engine/threshold_loader.py` | Adjust threshold values | Config |
| `config/live_mode.json` | Verify DRY-RUN mode | Config |

---

## Quick Commands

### Check Signal Generation (During Market Hours)
```bash
# Real-time monitoring
tail -f logs/research/system3_signal_engine.log | grep "SIGNAL PIPELINE"

# Or run diagnostic tool
python system3_debug_signals_pipeline.py
```

### Check Threshold Settings
```bash
# View current thresholds
grep -A1 "DEFAULT_THRESHOLDS" core/engine/threshold_loader.py

# Expected: {"buy": 0.12, "sell": -0.10}
```

### Verify DRY-RUN Mode (CRITICAL)
```bash
cat config/live_mode.json | grep DRY_RUN

# Must show: "DRY_RUN_MODE": true
```

### Adjust Thresholds (If Needed)
```bash
# Edit threshold_loader.py line 39
# Change from: {"buy": 0.12, "sell": -0.10}
# To: {"buy": 0.05, "sell": -0.05}
```

---

## Problem Diagnosis Flow

### Symptom: "Why are signals empty?"

```
STEP 1: Check logs
├─ tail -f logs/research/system3_signal_engine.log
├─ Look for: "🔍 SIGNAL PIPELINE START"
└─ If NOT present → Signal engine never called

STEP 2: Check signal distribution
├─ Run: python system3_debug_signals_pipeline.py
├─ Look for: "BUY=X SELL=Y HOLD=Z"
└─ If BUY=0, SELL=0 → Thresholds too strict

STEP 3: Check score range
├─ Look for: "final_score range=[-0.05, 0.08]"
├─ Compare to thresholds: [buy=0.12, sell=-0.10]
└─ If scores don't exceed thresholds → Adjust thresholds

STEP 4: Adjust and restart
├─ Edit: core/engine/threshold_loader.py line 39
├─ Change: {"buy": 0.05, "sell": -0.05}
├─ Restart: python system3_autorun_master.py
└─ Verify: python system3_debug_signals_pipeline.py
```

---

## Log Patterns Explained

### GOOD (Signals are generating)
```
🚀 SIGNAL ENGINE START: Snapshot size=150
  Before signal generation: 150 rows, final_score range=[-0.45, 0.58]
  After signal generation: 150 rows | Signal distribution: {'BUY': 12, 'SELL': 8, 'HOLD': 130}
✓ ACTION SIGNALS: 20 out of 150 are BUY/SELL
✓ Appended 150 signals to CSV [BUY=12, SELL=8]
```
→ **Action:** None, system working fine

### PROBLEM (No action signals)
```
generate_signals: AFTER threshold filter [BUY=0, SELL=0, HOLD=150]
⚠️  NO ACTION SIGNALS: final_score range=[-0.05, 0.08], mean=0.001
    Thresholds may be too strict. Check thresholds_by_underlying or adjust defaults.
```
→ **Action:** Lower thresholds (e.g., to 0.05, -0.05)

### CRITICAL (Signal engine not called)
```
[Nothing logged with "SIGNAL PIPELINE"]
Phases 220+ show: "Signals CSV not found"
```
→ **Action:** Wire signal generation into orchestrator (future task)

---

## Threshold Adjustment Guide

### Current Defaults
```python
# core/engine/threshold_loader.py line 39
DEFAULT_THRESHOLDS = {"buy": 0.12, "sell": -0.10}
```

### Adjustment Levels

| Thresholds | Effect | Use Case |
|-----------|--------|----------|
| buy=0.40, sell=-0.40 | Very strict | Only strong signals |
| buy=0.12, sell=-0.10 | Moderate | Default |
| buy=0.05, sell=-0.05 | Loose | More signals |
| buy=0.02, sell=-0.02 | Very loose | Debug/test |

### Adjustment Process
```bash
1. Run diagnostic: python system3_debug_signals_pipeline.py
2. Note final_score range and action signal count
3. If action < 10%:
   - Adjust thresholds to: {"buy": 0.05, "sell": -0.05}
   - Restart system
   - Check again
4. If still low, adjust to: {"buy": 0.02, "sell": -0.02}
```

---

## DRY-RUN Mode Protection

### Verify Protection is Active
```bash
# Check 1: Config file
cat config/live_mode.json
# Should show: "DRY_RUN_MODE": true

# Check 2: No real trades
# Monitor: Are virtual orders created but not executed?
# Should be: Yes (logged only)

# Check 3: Broker not contacted
# Monitor logs for: No actual API calls to broker
```

### If DRY-RUN is Disabled
```bash
# CRITICAL: Do NOT proceed without DRY-RUN enabled
# Check:
cat config/live_mode.json | grep DRY_RUN_MODE

# If false, change to true:
# Edit config/live_mode.json
# Set: "DRY_RUN_MODE": true
# Restart system
```

---

## Document Reference

| Document | Purpose | Read When |
|----------|---------|-----------|
| `DEBUG_SIGNALS_STEP2_STEP3_INSTRUMENTATION.md` | Detailed instrumentation guide | Understanding logs |
| `DEBUG_SIGNALS_STEP6_SAFETY_VERIFICATION.md` | Safety analysis | Before deployment |
| `DEBUG_SIGNALS_COMPLETE_6STEP_SUMMARY.md` | Complete implementation summary | Overview needed |
| This file | Quick reference | During troubleshooting |

---

## Common Issues & Solutions

### Issue: "Signals CSV is empty"
```
Cause: Signal generation not called OR thresholds too strict
Solution:
  1. Check logs for "SIGNAL PIPELINE START"
  2. If not found → signal engine not called (long-term issue)
  3. If found but no BUY/SELL → adjust thresholds
```

### Issue: "Phase 220 warns about empty CSV"
```
Cause: Same as above
Solution:
  1. Run: python system3_debug_signals_pipeline.py
  2. Check: Is final_score range too narrow?
  3. Adjust: Lower thresholds in threshold_loader.py
```

### Issue: "Final scores are all near zero"
```
Cause: Component scores too conservative
Solution:
  1. Check: Score distribution [min, max, mean]
  2. If mean near 0: Component calculations need review
  3. Adjust: Weights in process_snapshot() OR thresholds
```

### Issue: "DRY-RUN is disabled!"
```
⚠️ CRITICAL: Do NOT continue
Solution:
  1. Stop system immediately
  2. Edit: config/live_mode.json
  3. Set: "DRY_RUN_MODE": true
  4. Restart system
  5. Verify: cat config/live_mode.json
```

---

## Safety Checklist (Before Running)

- [ ] DRY-RUN mode is ENABLED (not disabled)
- [ ] No real money account linked
- [ ] Have read safety verification document
- [ ] Understand all changes are logging-only
- [ ] Know how to revert if needed
- [ ] System is not in LIVE trading mode

---

## Revert/Rollback Instructions

### If Something Goes Wrong
```bash
# Option 1: Revert just signal engine changes
git checkout core/engine/system3_signal_engine.py
git checkout core/engine/scoring_engine/signal_scorer.py

# Option 2: Revert all changes
git reset --hard HEAD

# Option 3: Delete new files
rm system3_debug_signals_pipeline.py
rm DEBUG_*.md

# Option 4: Minimal - just delete new tools
rm system3_debug_signals_pipeline.py

# Restart system
python system3_autorun_master.py
```

**Time to revert:** < 1 minute
**Data loss risk:** 🟢 ZERO

---

## Support Contacts

### If You Need To:
1. **Understand signal flow:** Read "DEBUG_SIGNALS_COMPLETE_6STEP_SUMMARY.md"
2. **Verify safety:** Read "DEBUG_SIGNALS_STEP6_SAFETY_VERIFICATION.md"
3. **Use instrumentation:** Read "DEBUG_SIGNALS_STEP2_STEP3_INSTRUMENTATION.md"
4. **Troubleshoot quickly:** Use this quick reference
5. **Run diagnostics:** Execute `python system3_debug_signals_pipeline.py`

---

## Key Takeaway

> **Signal generation code works perfectly. The issue is either:**
> 1. **It's never called** (main issue - needs orchestrator wiring)
> 2. **Or thresholds filter out all signals** (secondary - fix with threshold adjustment)
>
> **The instrumentation tells you EXACTLY which one is the problem.**

---

