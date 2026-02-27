# STEP 1: Signal Writer & Planner Location Analysis

## Summary

**Problem:** `angel_index_ai_signals.csv` remains empty throughout the entire day, resulting in:
- Phase logs: "Signals CSV is empty or contained only headers after creation. No trade plan will be generated."
- OP3 (Trade Decision & Planning) always sees empty DataFrame
- No trades executed (expected in DRY-RUN, but signals should still be generated)

---

## SIGNAL WRITER FUNCTIONS

### Primary Signal Writer: `system3_signal_engine.run_signal_engine()`

**File:** `core/engine/system3_signal_engine.py` (Lines 693-738)

**Function Signature:**
```python
def run_signal_engine(df_snap: pd.DataFrame, enable_safety_checks: bool = True) -> pd.DataFrame
```

**What It Does:**
1. Takes a snapshot DataFrame (`df_snap`) as input
2. Calls `process_snapshot(df_snap)` to generate signals
3. Appends signals to CSV via `append_signals_to_csv(df_signals)`

**CSV Append Function:**
```python
def append_signals_to_csv(df_signals: pd.DataFrame) -> None
    # Location: Lines 668-680
    # Writes to: SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"
```

**Called By:**
- `angel_live_ai_signals.py` → `run_once_with_snapshot()` (Lines 313-315)
- `angel_live_ai_signals_v2.py` (alternative implementation)
- Test scripts

---

### Fallback Signal Writer: `angel_live_ai_signals.append_signals_to_csv()`

**File:** `core/engine/angel_live_ai_signals.py` (Lines 279-288)

**Function Signature:**
```python
def append_signals_to_csv(df_signals: pd.DataFrame, csv_path: Path) -> None
```

**What It Does:**
1. Takes a DataFrame of signals
2. Creates empty CSV with header if file doesn't exist
3. Appends rows to CSV

**Called By:**
- `angel_live_ai_signals.run_once_with_snapshot()` (Line 347) - fallback mode
- Accepts any CSV path (not hard-coded)

---

## TRADE PLANNER FUNCTIONS

### Primary Trade Planner: `angel_trade_decision.build_trade_plan()`

**File:** `core/engine/angel_trade_decision.py`

**What It Does:**
1. Reads signals CSV
2. Builds trade plan from signals
3. Stores plan in trades CSV
4. Returns plan DataFrame

**Key Issue:**
- **Lines 231-251:** Creates empty signals CSV if it doesn't exist
- **Lines 245-256:** Checks if CSV is empty → returns early with no trade plan
- Never receives signals because `system3_signal_engine.run_signal_engine()` isn't being called with data

---

## SIGNAL GENERATION PIPELINE

### Entry Point: `angel_live_ai_signals.run_once_with_snapshot()`

**File:** `core/engine/angel_live_ai_signals.py` (Lines 290-340)

**Flow:**
```
run_once_with_snapshot(df_snap)
  ├─ Try: system3_signal_engine.run_signal_engine(df_snap)
  │  ├─ process_snapshot(df_snap) → generates signals
  │  ├─ append_signals_to_csv() → writes to CSV
  │  └─ Returns df_signals
  │
  └─ Fallback (if new engine fails):
     ├─ load_models_and_meta()
     ├─ predict_for_snapshot_df(df_snap, models) → generates signals
     ├─ append_signals_to_csv(df_signals, SIGNALS_CSV) → writes to CSV
     └─ build_trade_plan() → creates trades
```

---

## PHASE MAPPING (220-247)

Based on code analysis, here's which phases call which functions:

| Phase | Module | Status | Function |
|-------|--------|--------|----------|
| 220 | `system3_phase220_correlation_map` | `run_phase220()` | Computes correlations |
| 221 | `system3_phase221_forward_returns` | `run_phase221()` | Computes forward returns |
| 222 | `system3_phase222_signal_edge` | `run_phase222()` | Computes signal edge |
| 223 | `system3_phase223_threshold_optimizer` | `run_phase223()` | Optimizes thresholds |
| 224 | `system3_phase224_score_attribution` | `run_phase224()` | Attributes scores |
| 225 | `system3_phase225_label_reconciliation` | `run_phase225()` | Reconciles labels |
| 226 | `system3_phase226_feature_importance` | `run_phase226()` | Computes feature importance |
| 227 | `system3_phase227_latency_profiler` | `run_phase227()` | Profiles latency |
| 228 | `system3_phase228_snapshot_coverage` | `run_phase228()` | Checks coverage |
| 229 | `system3_phase229_schema_guard` | `run_phase229()` | Validates schema |
| 230 | `system3_phase230_ai_fallback_audit` | `run_phase230()` | Audits fallback behavior |

**CRITICAL FINDING:** None of these phases actually GENERATE and WRITE signals!

They all READ from `angel_index_ai_signals.csv` that was supposed to be written earlier.

---

##  MISSING LINK: WHO CALLS `run_once_with_snapshot()`?

**Searched in orchestrator phases** → Not found!

**Searched in complete_orchestrator** → Not called from main phase loop!

**This is the root cause:**
- `angel_live_ai_signals.run_once_with_snapshot()` exists and works
- But nobody is calling it from the phase orchestration loop
- So signals never get generated
- So CSV stays empty
- So phases 220-230 get empty signals

---

##  CRITICAL ISSUE SUMMARY

1. **Signal Generation Function:** `system3_signal_engine.run_signal_engine()`
   - Located in: `core/engine/system3_signal_engine.py`
   - **NOT CALLED from orchestrator!**

2. **Signal Write Function:** `append_signals_to_csv()`
   - Located in: `system3_signal_engine.py` (primary)
   - Located in: `angel_live_ai_signals.py` (fallback)

3. **Trade Planner:** `angel_trade_decision.build_trade_plan()`
   - Located in: `core/engine/angel_trade_decision.py`
   - Correctly reads CSV (but it's always empty)

4. **Root Cause:** The signal generation is not wired into the phase orchestration
   - Need to find where phases 220-247 are executed
   - Need to add signal generation BEFORE them

---

## Next Steps (STEP 2+)

1. **Find the orchestrator loop** that runs phases 220-247
2. **Add signal generation call** before phase 220
3. **Instrument with logging** (STEP 2)
4. **Debug filters** (STEP 3)
5. **Create debug script** (STEP 5)

