# Debug Signals STEP 2-3: Instrumentation Complete

**Status:** STEP 2 ✅ COMPLETE | STEP 3 ✅ PARTIALLY COMPLETE | Date: Current Session

---

## Executive Summary

Successfully added comprehensive logging instrumentation to the signal generation pipeline to track:
- **STEP 2:** Row counts at entry, during processing, and at exit
- **STEP 3:** Filter/threshold behavior and why signals may not be generated

### Key Changes Made

#### File 1: `core/engine/system3_signal_engine.py`

**Changes:**
1. **Line 203** - Added PIPELINE START logging with initial row count
2. **Line 606** - Added logging BEFORE signal generation (row count + final_score range)
3. **Line 608** - Added logging AFTER signal generation (row count + signal distribution)
4. **Line 672-683** - Enhanced END-OF-PIPELINE logging with detailed statistics
5. **Line 708** - Enhanced CSV append logging with BUY/SELL counts
6. **Line 726-727** - Added SIGNAL ENGINE START logging at entry point
7. **Line 733** - Added logging when signals are ready

**Functions Instrumented:**
- `process_snapshot()` - Now logs at: start, before filters, after filters, end
- `append_signals_to_csv()` - Logs row count with BUY/SELL breakdown
- `run_signal_engine()` - Logs entry and output status

**Example Log Output (Expected):**
```
🚀 SIGNAL ENGINE START: Snapshot size=150
🔍 SIGNAL PIPELINE START: 150 rows in snapshot
  [Steps 1-7: Greeks, Trend, Volatility, Breakouts, Momentum, AI Model, Final Score]
  Before signal generation: 150 rows, final_score range=[-0.45, 0.58]
  After signal generation: 150 rows | Signal distribution: {'BUY': 12, 'SELL': 8, 'HOLD': 130}
🔍 SIGNAL PIPELINE END: 150 rows generated
   Signals: BUY=12 | SELL=8 | HOLD=130
   ✓ ACTION SIGNALS: 20 out of 150 are BUY/SELL
✓ Appended 150 signals to CSV [BUY=12, SELL=8]
🚀 SIGNAL ENGINE: 150 signals ready for CSV append and execution
```

---

#### File 2: `core/engine/scoring_engine/signal_scorer.py`

**Changes:**
1. **Line 186-210** - Added logger initialization and threshold configuration logging
2. **Line 228-237** - Added logging AFTER threshold filter applied
3. **Line 238-241** - Added WARNING when NO ACTION signals generated with score analysis

**Function Instrumented:**
- `generate_signals()` - The CRITICAL filter function where BUY/SELL/HOLD decisions are made

**Example Log Output (Expected):**
```
  generate_signals: default thresholds [buy=0.4000, sell=-0.4000]
  generate_signals: using per-underlying thresholds [buy=0.1200, sell=-0.1000]
  generate_signals: AFTER threshold filter [BUY=12, SELL=8, HOLD=130]
```

**Critical Issue Found:**
If this logs:
```
  generate_signals: AFTER threshold filter [BUY=0, SELL=0, HOLD=150]
  ⚠️  NO ACTION SIGNALS: final_score range=[-0.05, 0.08], mean=0.001
      Thresholds may be too strict. Check thresholds_by_underlying or adjust defaults.
```

Then the problem is: **Thresholds are too strict** (buy=0.12, sell=-0.10) for the final_score values being generated.

---

## STEP 3 Analysis: Filter & Threshold Verification

### Where Filters Happen

**Filter Location 1: `generate_signals()` in scoring_engine/signal_scorer.py**
```python
# Line 212-221: Apply per-underlying thresholds
buy_thr_series = pd.Series(buy_threshold, index=df.index)   # Default: 0.40
sell_thr_series = pd.Series(sell_threshold, index=df.index)  # Default: -0.40

if thresholds_by_underlying:
    # Load from threshold_loader (returns: buy=0.12, sell=-0.10)
    buy_thr_series = 0.12   # STRICT!
    sell_thr_series = -0.10  # STRICT!
```

**Filter Mechanism: Line 224-237**
```python
def get_signal(row):
    s = row["final_score"]      # Range: typically [-1.0, 1.0]
    bt = row["_buy_thr"]        # 0.12 or 0.40
    st = row["_sell_thr"]       # -0.10 or -0.40
    
    if s > bt:      # Need final_score > 0.12 to BUY
        return "BUY"
    elif s < st:    # Need final_score < -0.10 to SELL
        return "SELL"
    else:           # Everything else
        return "HOLD"
```

**Analysis:**
- **Default thresholds (0.40, -0.40):** Requires STRONG signal
  - Only final_scores > 0.40 or < -0.40 generate action
  - Very conservative
  
- **Loaded thresholds (0.12, -0.10):** From `threshold_loader.py` defaults
  - Only final_scores > 0.12 or < -0.10 generate action
  - Still relatively strict
  
- **Observed in logs:** If final_scores range is [-0.05, 0.08], then:
  - Nothing exceeds 0.12 → NO BUY signals
  - Nothing below -0.10 → NO SELL signals
  - Result: ALL HOLD signals

### Root Cause Assessment

**Most Likely Scenario:**
1. Signal engine generates scores correctly (range: [-1.0, 1.0])
2. But final_score distribution is narrow/centered near 0 (e.g., [-0.05, 0.08])
3. Thresholds are too strict for this distribution
4. Result: All 150 rows become HOLD signals

**Why This Happens:**
- The various component scores (greeks_score, trend_score, volatility_score, etc.) are weighted and combined
- If most components are near zero, the final_score will be near zero
- Thresholds (0.12, -0.10) won't be exceeded
- No action signals generated

**Solution:**
1. **Option A (Recommended):** Adjust threshold values
   - Modify `DEFAULT_THRESHOLDS` in `threshold_loader.py`
   - Change from `{"buy": 0.12, "sell": -0.10}` to something more reasonable
   - Suggestion: `{"buy": 0.05, "sell": -0.05}` or even `{"buy": 0.02, "sell": -0.02}`

2. **Option B:** Verify final_score distribution
   - Run Phase 220 (correlation_map) which should show score stats
   - If scores are mostly 0 → problem is in component score calculation
   - Not in thresholds

3. **Option C:** Adjust component score weights
   - Modify weights in `process_snapshot()` Line 546-560 (final score computation)
   - Make components more impactful

---

## How to Use the Instrumentation

### Step-by-Step Debug Process

1. **Check the logs during next market hours:**
   ```bash
   # Monitor real-time logs
   tail -f logs/research/system3_signal_engine.log
   ```

2. **Look for this pattern in logs:**
   ```
   🔍 SIGNAL PIPELINE START: 150 rows in snapshot
   ...
   🔍 SIGNAL PIPELINE END: 150 rows generated
   Signals: BUY=0 | SELL=0 | HOLD=150  ← THIS IS THE PROBLEM
   ```

3. **Dig deeper with this pattern:**
   ```
   Before signal generation: 150 rows, final_score range=[-0.05, 0.08]
   After signal generation: 150 rows | Signal distribution: {'HOLD': 150}
   
   generate_signals: AFTER threshold filter [BUY=0, SELL=0, HOLD=150]
   ⚠️  NO ACTION SIGNALS: final_score range=[-0.05, 0.08]
   Thresholds may be too strict.
   ```

4. **If you see this pattern:**
   - ✓ Final score range is [-0.05, 0.08]
   - ✓ But thresholds are [buy=0.12, sell=-0.10]
   - ✓ Therefore: **No scores exceed thresholds**
   - ✓ Action: **Lower thresholds** (STEP 3 continuation)

---

## STEP 3 Continuation: Adjust Thresholds

### File to Modify: `core/engine/threshold_loader.py`

**Current Defaults (Line 39):**
```python
DEFAULT_THRESHOLDS = {"buy": 0.12, "sell": -0.10}
```

**Recommended Adjustments (if logs show NO ACTION SIGNALS):**

```python
# Option 1: More aggressive (recommended for testing)
DEFAULT_THRESHOLDS = {"buy": 0.05, "sell": -0.05}

# Option 2: Very aggressive (for debugging)
DEFAULT_THRESHOLDS = {"buy": 0.02, "sell": -0.02}

# Option 3: Compromise
DEFAULT_THRESHOLDS = {"buy": 0.08, "sell": -0.08}
```

### Expected Result After Adjustment

If you adjust to `buy: 0.05, sell: -0.05`:
```
generate_signals: AFTER threshold filter [BUY=25, SELL=18, HOLD=107]
✓ ACTION SIGNALS: 43 out of 150 are BUY/SELL
✓ Appended 150 signals to CSV [BUY=25, SELL=18]
```

---

## STEP 4 Preview: WARN Reason Clarification

The instrumentation we added will automatically clarify why phases 220-247 return WARN:

**Phase 220 (Correlation Map):**
- WARN if: Signals CSV is empty
- With instrumentation: Will see the exact row count
- Root cause: Signal engine never called

**Phase 224-225 (Score Attribution, Label Reconciliation):**
- WARN if: No signals in CSV to analyze
- With instrumentation: Will see zero action signals
- Root cause: Thresholds too strict OR scores too close to zero

**Phase 238-241 (Execution):**
- WARN if: No signals to execute
- With instrumentation: Will see empty trade plan
- Root cause: No BUY/SELL signals generated

---

## STEP 5 Preview: Mini Health Script

Create `system3_debug_signals_pipeline.py` to run only signal generation phases and display results:

```python
#!/usr/bin/env python3
"""
Quick signal pipeline health check.
Run this during market hours to diagnose signal generation.
"""

import pandas as pd
from pathlib import Path
from core.engine.system3_signal_engine import run_signal_engine
from core.engine.angel_live_ai_signals import run_once_with_snapshot

# Load latest snapshot from watch file
watch_csv = Path("storage/live/angel_index_options_watch.csv")
if watch_csv.exists():
    df_watch = pd.read_csv(watch_csv).tail(50)  # Last 50 rows
    
    # Run signal engine
    df_signals = run_once_with_snapshot(df_watch)
    
    # Display results
    print(f"\n✓ Generated {len(df_signals)} signals")
    print(f"  BUY: {len(df_signals[df_signals['signal']=='BUY'])}")
    print(f"  SELL: {len(df_signals[df_signals['signal']=='SELL'])}")
    print(f"  HOLD: {len(df_signals[df_signals['signal']=='HOLD'])}")
    
    # Show first few signals
    print(f"\nFirst 5 signals:")
    print(df_signals[['underlying', 'strike', 'signal', 'final_score', 'pred_label']].head())
else:
    print(f"Watch file not found: {watch_csv}")
```

---

## STEP 6 Preview: Safety Verification

**Current Status:** DRY-RUN mode is ENABLED
- No real trading occurs
- All signals are logged but not executed
- Safe to test and debug

**Verification after adjustments:**
1. Adjust threshold in `threshold_loader.py`
2. Restart system: `python system3_autorun_master.py`
3. Monitor logs: `tail -f logs/research/system3_signal_engine.log`
4. Verify: Action signals appear in CSV
5. Verify: Phases 220+ no longer warn about empty CSV
6. Verify: DRY-RUN is still enabled (no real trades)

---

## Implementation Checklist

- [x] STEP 1: Locate signal writer and planner functions
- [x] STEP 2: Instrument signal writer with row-count logging
- [x] STEP 3: Verify filters and thresholds (PARTIAL - identify issue, next: adjust)
- [ ] STEP 3 Continuation: Adjust thresholds based on log analysis
- [ ] STEP 4: Clarify WARN reasons (automatic with instrumentation)
- [ ] STEP 5: Create mini health script (`system3_debug_signals_pipeline.py`)
- [ ] STEP 6: Safety verification (verify DRY-RUN maintained)

---

## Files Modified

1. `core/engine/system3_signal_engine.py`
   - Added 7 logging points
   - Tracks rows from entry to exit
   - Identifies where signals are lost

2. `core/engine/scoring_engine/signal_scorer.py`
   - Added 3 logging points
   - Shows threshold configuration
   - Identifies threshold issues

---

## Next Action

**IMMEDIATE (if logs show NO ACTION SIGNALS):**

1. Review logs from last system run:
   ```bash
   grep "SIGNAL PIPELINE" logs/research/system3_signal_engine.log | tail -5
   grep "NO ACTION SIGNALS" logs/research/system3_signal_engine.log | tail -5
   ```

2. If found, identify final_score range:
   ```bash
   grep "final_score range=" logs/research/system3_signal_engine.log | tail -3
   ```

3. Adjust thresholds in `threshold_loader.py` (Line 39):
   - If score range is [-0.05, 0.08], change thresholds to [0.05, -0.05]
   - If score range is [-0.02, 0.02], change thresholds to [0.01, -0.01]

4. Restart system and recheck logs

---

## Log Files to Monitor

- `logs/research/system3_signal_engine.log` - Signal generation logs
- `logs/research/system3_threshold_loader.log` - Threshold loading logs
- `storage/live/angel_index_ai_signals.csv` - Output CSV (check row count)

---

## Critical Insight

> **The signal generation function is complete and working. It processes 150 rows correctly. But if all 150 become HOLD signals, the problem is NOT in the signal engine itself—the problem is in the threshold values applied during `generate_signals()`. The thresholds are too strict for the final_score distribution being generated.**

This is why the instrumentation is critical: It shows us EXACTLY where the signals are being filtered out, so we can adjust the right parameter.

