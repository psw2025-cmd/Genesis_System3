# PHASE 381-388: ULTRA MODELS IMPLEMENTATION PLAN

**Status:** 🚧 READY FOR IMPLEMENTATION
**Mode:** DRY-RUN ONLY (No live trading, no safety config changes)
**Python:** venv 3.10.11 @ `C:/Genesis_System3/venv/Scripts/python.exe`
**Date:** December 7, 2025

---

## EXECUTIVE SUMMARY

### Goal
Implement Path A (Ultra Models) to upgrade ML scoring from delta-based fallback to pre-trained per-underlying models, maintaining all safety controls and DRY-RUN enforcement.

### Current State Analysis

#### 1. Ultra Models Location ✅
```
core/models/angel_one_ultra/
├─ NIFTY_ultra_model.pkl        (exists)
├─ BANKNIFTY_ultra_model.pkl    (exists)
├─ FINNIFTY_ultra_model.pkl     (exists)
├─ MIDCPNIFTY_ultra_model.pkl   (exists)
└─ SENSEX_ultra_model.pkl       (exists)

Status: All 5 models present and ready
```

#### 2. Current ML Training Mechanism ❌
**File:** `core/engine/system3_signal_engine.py` (lines 390-460)
**Function:** Train ML model via `train_ml_model(hist_df, model_type="randomforest")`
**Result:** Returns `None` due to:
- Class imbalance (46% HOLD, 29% SELL, 24% BUY)
- Low feature variance (80% zeros)
- No correlation with profitability

**Fallback:** Delta-based scoring (66.7% win rate)
```python
# Line 426-431
df["ai_score"] = (
    (delta_proxy * 2.0 - 1.0)
    .clip(-1.0, 1.0)
    .fillna(0.0)
    * 0.3
)
```

#### 3. ML Predictor Module 📍
**File:** `core/engine/ai_model/ml_predictor.py`
**Key Functions:**
- `load_training_data()` - Robust CSV loader with fallback parser
- `train_ml_model()` - RandomForest/XGBoost training
- `predict_direction()` - Model prediction wrapper

**Training Data:**
- Curated: `storage/live/angel_index_ai_signals_curated.csv` (2,416 rows)
- Live: `storage/live/angel_index_ai_signals.csv`
- Min samples: 200 rows

#### 4. Ultra Models Loader ❌
**Status:** Does NOT exist yet
**Required:** `core/engine/ultra_models_loader.py`
**Purpose:** Load pre-trained per-underlying models with metadata tracking

---

## IMPLEMENTATION ARCHITECTURE

### Phase Distribution (8 Phases: 381-388)

```
Block 1: Discovery & Validation (381-382)
├─ Phase 381: Ultra Models Scanner
│  └─ Scan available models, generate inventory
├─ Phase 382: Sanity Validator
│  └─ Test load + predict on synthetic batch

Block 2: Analysis & Testing (383-384)
├─ Phase 383: Backtest Sampler
│  └─ Compare Ultra vs Delta on historical data
├─ Phase 384: Health Summary
│  └─ Aggregate metrics from 381-383

Block 3: Monitoring & Safety (385-386)
├─ Phase 385: Scoring Telemetry
│  └─ Track Ultra vs Delta usage in production
├─ Phase 386: Fail-Safe Guard
│  └─ Verify delta fallback works if Ultra fails

Block 4: Impact & Verification (387-388)
├─ Phase 387: Impact Preview
│  └─ Estimate win-rate change from Ultra models
└─ Phase 388: Health Gate
   └─ Final status check for entire 381-388 block
```

---

## IMPLEMENTATION DETAILS

### Component 1: Ultra Models Loader

**File:** `core/engine/ultra_models_loader.py` (NEW)

**Functions:**
```python
def load_ultra_model(underlying: str) -> Optional[Any]:
    """
    Load pre-trained ultra model for given underlying.
    
    Args:
        underlying: "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"
    
    Returns:
        sklearn model or None if not found
    
    Behavior:
        - Checks core/models/angel_one_ultra/{underlying}_ultra_model.pkl
        - Returns None gracefully if model missing (enables delta fallback)
        - Logs success/failure explicitly
    """

def get_ultra_model_metadata(underlying: str) -> Dict[str, Any]:
    """
    Extract model metadata (file size, modified date, model type).
    
    Returns:
        {
            "underlying": "NIFTY",
            "model_path": "core/models/angel_one_ultra/NIFTY_ultra_model.pkl",
            "file_size_kb": 245.6,
            "last_modified": "2025-12-05 14:23:10",
            "exists": True
        }
    """

def load_ultra_models_all() -> Dict[str, Any]:
    """
    Load all 5 ultra models in one call.
    
    Returns:
        {"NIFTY": model, "BANKNIFTY": model, ...}
    """
```

**Safety:**
- NEVER raises exceptions (returns None)
- NEVER downloads external data
- NEVER modifies model files
- Uses only local pre-trained models

---

### Component 2: Signal Engine Integration

**File:** `core/engine/system3_signal_engine.py` (MODIFY lines 390-460)

**Current Flow:**
```
1. Load training data (hist_df)
2. Train RandomForest → Returns None
3. Fall back to delta-based scoring
```

**New Flow:**
```
1. Detect underlying from df (NIFTY, BANKNIFTY, etc.)
2. Try load_ultra_model(underlying)
   ├─ SUCCESS: Use Ultra model for prediction
   │           Log: "USING_ULTRA_MODEL for NIFTY (version=...)"
   │           Set ai_score from model
   └─ FAILURE: Fall back to delta-based scoring
               Log: "USING_DELTA_FALLBACK for BANKNIFTY (no ultra model)"
               Keep existing delta formula
```

**Changes Required:**
1. Import `ultra_models_loader` at top
2. Before line 395 `train_ml_model()`, add Ultra model attempt
3. Keep all existing delta fallback code (lines 420-460)
4. Add explicit logging for transparency

**Example Code:**
```python
# NEW: Try Ultra model first
underlying = df["underlying"].iloc[0] if "underlying" in df.columns else None
if underlying:
    ultra_model = load_ultra_model(underlying)
    if ultra_model:
        try:
            df = predict_direction(ultra_model, df)
            logger.info(f"✓ USING_ULTRA_MODEL for {underlying}")
        except Exception as e:
            logger.warning(f"Ultra model failed for {underlying}: {e}, using delta fallback")
            ultra_model = None

# If Ultra model not available or failed, use existing delta fallback
if not ultra_model:
    logger.info(f"USING_DELTA_FALLBACK for {underlying or 'unknown'}")
    # Existing delta-based code (lines 420-460)...
```

---

### Component 3: Phase 381 - Ultra Models Scanner

**File:** `core/engine/system3_phase381_ultra_models_scanner.py` (NEW)

**Purpose:** Discover all available Ultra models and create inventory

**Outputs:**
- `storage/metrics/ultra_models_inventory_381.json`
- `reports/ULTRA_MODELS_INVENTORY_381.md`

**Metrics:**
```json
{
  "scan_timestamp": "2025-12-07T20:45:00Z",
  "models_found": 5,
  "models": [
    {
      "underlying": "NIFTY",
      "path": "core/models/angel_one_ultra/NIFTY_ultra_model.pkl",
      "size_kb": 245.6,
      "last_modified": "2025-12-05T14:23:10Z",
      "exists": true,
      "loadable": true
    }
  ]
}
```

**Test:** Load each model, verify it returns valid object

---

### Component 4: Phase 382 - Sanity Validator

**File:** `core/engine/system3_phase382_ultra_models_validator.py` (NEW)

**Purpose:** Quick smoke test - load each model and predict on synthetic batch

**Test Data:**
```python
# Synthetic 5-row DataFrame with typical features
synthetic_df = pd.DataFrame({
    "underlying": ["NIFTY"] * 5,
    "delta": [0.3, 0.5, 0.7, -0.3, -0.5],
    "gamma": [0.01] * 5,
    "theta": [-0.5] * 5,
    "side": ["CE", "CE", "CE", "PE", "PE"],
    # ... 40+ features total
})
```

**Test:** Call `predict_direction(model, synthetic_df)` for each model
**Expected:** Returns DataFrame with `ai_score` column, no crashes

**Outputs:**
- `storage/metrics/ultra_models_validation_382.json`
- `reports/ULTRA_MODELS_VALIDATION_382.md`

---

### Component 5: Phase 383 - Backtest Sampler

**File:** `core/engine/system3_phase383_ultra_backtest_sampler.py` (NEW)

**Purpose:** Compare Ultra models vs Delta scoring on historical sample

**Methodology:**
1. Load last 100 signals from `storage/live/angel_index_ai_signals_curated.csv`
2. For each underlying:
   - Score with Ultra model → `ai_score_ultra`
   - Score with delta formula → `ai_score_delta`
   - Compare distributions
3. Generate comparison metrics

**Metrics:**
```json
{
  "sample_size": 100,
  "underlyings_tested": ["NIFTY", "BANKNIFTY"],
  "results": {
    "NIFTY": {
      "ultra_mean": 0.45,
      "delta_mean": 0.30,
      "ultra_std": 0.25,
      "delta_std": 0.15,
      "correlation": 0.72
    }
  }
}
```

**Outputs:**
- `storage/metrics/ultra_vs_delta_backtest_383.json`
- `reports/ULTRA_VS_DELTA_BACKTEST_383.md`

---

### Component 6: Phase 384 - Health Summary

**File:** `core/engine/system3_phase384_ultra_health_summary.py` (NEW)

**Purpose:** Aggregate results from phases 381-383

**Report Structure:**
```markdown
# ULTRA MODELS HEALTH SUMMARY (PHASE 384)

## Discovery (Phase 381)
- Models Found: 5/5
- All Loadable: ✅

## Validation (Phase 382)
- Smoke Tests Passed: 5/5
- Prediction Success: 100%

## Backtest (Phase 383)
- Sample Size: 100 signals
- Ultra Mean Score: 0.45 vs Delta: 0.30
- Expected Improvement: +15% higher signal strength

## Overall Status: ✅ READY FOR PRODUCTION
```

**Outputs:**
- `reports/ULTRA_MODEL_HEALTH_384.md`

---

### Component 7: Phase 385 - Scoring Telemetry

**File:** `core/engine/system3_phase385_scoring_telemetry.py` (NEW)

**Purpose:** Track how often Ultra vs Delta scoring is used in live runs

**Mechanism:**
1. Parse recent logs from `logs/`
2. Count occurrences of:
   - `"USING_ULTRA_MODEL"` log entries
   - `"USING_DELTA_FALLBACK"` log entries
3. Generate usage statistics

**Metrics:**
```json
{
  "period": "last_24_hours",
  "total_signals": 120,
  "ultra_used": 85,
  "delta_fallback": 35,
  "ultra_percentage": 70.8,
  "by_underlying": {
    "NIFTY": {"ultra": 30, "delta": 5},
    "BANKNIFTY": {"ultra": 25, "delta": 10}
  }
}
```

**Outputs:**
- `storage/metrics/scoring_telemetry_385.json`
- `reports/SCORING_TELEMETRY_385.md`

---

### Component 8: Phase 386 - Fail-Safe Guard

**File:** `core/engine/system3_phase386_failsafe_guard.py` (NEW)

**Purpose:** Verify delta fallback still works if Ultra models are missing/broken

**Test Scenarios:**
1. Temporarily rename one Ultra model → Verify delta fallback activates
2. Corrupt one model file → Verify graceful None return
3. Pass invalid data to model → Verify exception handling
4. Test with missing `underlying` column → Verify safe degradation

**Expected:** All scenarios should fall back to delta scoring, NO CRASHES

**Outputs:**
- `storage/metrics/failsafe_guard_386.json`
- `reports/FAILSAFE_GUARD_386.md`

---

### Component 9: Phase 387 - Impact Preview

**File:** `core/engine/system3_phase387_impact_preview.py` (NEW)

**Purpose:** Estimate expected improvement in win-rate from Ultra models

**Calculation:**
1. Historical win rate with delta scoring: 66.7%
2. Backtest results from Phase 383:
   - Ultra models show +15% higher signal strength
   - Estimated win rate improvement: +5-10%
3. Project impact over 100 future trades

**Report:**
```markdown
# ULTRA MODELS IMPACT PREVIEW

## Current Performance (Delta Fallback)
- Win Rate: 66.7%
- Average Signal Strength: 0.30

## Projected Performance (Ultra Models)
- Estimated Win Rate: 70-72%
- Average Signal Strength: 0.45
- Improvement: +5-10 percentage points

## Risk Assessment
- Fallback Available: ✅
- Safety Impact: NONE (DRY-RUN enforced)
- Rollback Plan: Remove Ultra loader import
```

**Outputs:**
- `reports/ULTRA_MODELS_IMPACT_PREVIEW_387.md`

---

### Component 10: Phase 388 - Health Gate

**File:** `core/engine/system3_phase388_health_gate.py` (NEW)

**Purpose:** Final gate check before declaring phases 381-388 complete

**Checks:**
1. ✅ All 5 Ultra models loadable (Phase 381)
2. ✅ All models pass smoke test (Phase 382)
3. ✅ Backtest shows improvement (Phase 383)
4. ✅ Health summary positive (Phase 384)
5. ✅ Telemetry tracking working (Phase 385)
6. ✅ Fail-safe verified (Phase 386)
7. ✅ Impact preview generated (Phase 387)
8. ✅ No safety config changes
9. ✅ DRY-RUN still enforced

**Status Levels:**
- ✅ OK: All checks pass, ready for production
- ⚠️ WARN: Minor issues, safe to proceed
- ❌ FAIL: Critical issues, block deployment

**Outputs:**
- `storage/metrics/phase_381_388_health_gate.json`
- `reports/PHASE_381_388_HEALTH_GATE.md`

---

## SAFETY CONSTRAINTS

### Files That MUST NOT Be Modified
```
❌ core/config/live_trade_config.py
❌ core/config/angel_automation_config.json
❌ core/config/system3_ultra_safety.json
❌ Any phase files 1-380
❌ Broker integration modules
❌ Order execution modules
```

### Safety Flags That MUST Remain FALSE
```python
LIVE_TRADING_ENABLED = False        # MUST stay False
USE_LIVE_EXECUTION_ENGINE = False   # MUST stay False
AUTO_EXECUTE_TRADES = False         # MUST stay False
```

### Allowed Modifications
```
✅ core/engine/ultra_models_loader.py (NEW)
✅ core/engine/system3_signal_engine.py (lines 390-460 only)
✅ core/engine/system3_phase381_*.py (NEW, 8 files)
✅ core/engine/system3_phases_381_388_registry.py (NEW)
✅ storage/metrics/*.json (NEW)
✅ reports/*.md (NEW)
✅ tools/run_phases_381_388_block_test.py (NEW)
```

---

## TESTING STRATEGY

### Test Script: `tools/run_phases_381_388_block_test.py`

**Purpose:** Execute all 8 phases sequentially and generate pass/fail report

**Execution:**
```powershell
C:/Genesis_System3/venv/Scripts/python.exe tools/run_phases_381_388_block_test.py
```

**Output:**
```
PHASE 381-388 BLOCK TEST
========================
Phase 381 (Scanner)        : ✅ PASS (5 models found)
Phase 382 (Validator)      : ✅ PASS (5/5 smoke tests OK)
Phase 383 (Backtest)       : ✅ PASS (100 samples compared)
Phase 384 (Health Summary) : ✅ PASS (report generated)
Phase 385 (Telemetry)      : ✅ PASS (tracking active)
Phase 386 (Fail-Safe)      : ✅ PASS (4/4 scenarios OK)
Phase 387 (Impact Preview) : ✅ PASS (report generated)
Phase 388 (Health Gate)    : ✅ PASS (all checks OK)

OVERALL: ✅ 8/8 PHASES PASSED

Safety Verification:
├─ live_trade_config.py : LIVE_TRADING_ENABLED = False ✅
├─ angel_automation_config.json : DRY_RUN = true ✅
└─ system3_ultra_safety.json : AUTO_EXECUTE = false ✅
```

---

## EXPECTED OUTCOMES

### After Phase 381-388 Implementation

1. **Scoring Mechanism:**
   - Ultra models used when available (70-80% of signals)
   - Delta fallback used when Ultra not available (20-30% of signals)
   - Explicit logging of which path taken

2. **Accuracy Improvement:**
   - Current: 66.7% win rate (delta fallback)
   - Expected: 70-72% win rate (Ultra models)
   - Improvement: +5-10 percentage points

3. **Safety Maintained:**
   - All DRY-RUN flags remain False
   - No live trading enabled
   - No broker API calls
   - Fallback mechanism intact

4. **Monitoring:**
   - Telemetry tracks Ultra vs Delta usage
   - Health gate confirms all phases operational
   - Fail-safe guard verified

---

## IMPLEMENTATION TIMELINE

### Immediate (Next 30 Minutes)
1. Create `ultra_models_loader.py` (10 min)
2. Modify `system3_signal_engine.py` (10 min)
3. Create phases 381-384 (10 min)

### Phase 2 (Next 30 Minutes)
4. Create phases 385-388 (15 min)
5. Create phase registry (5 min)
6. Create block test script (10 min)

### Testing (Next 15 Minutes)
7. Run block test (5 min)
8. Verify all phases pass (5 min)
9. Generate implementation summary (5 min)

**Total Time:** ~75 minutes

---

## ROLLBACK PLAN

If Ultra models cause issues:

1. **Quick Rollback:**
   ```python
   # In system3_signal_engine.py, comment out Ultra model attempt
   # ultra_model = load_ultra_model(underlying)  # DISABLED
   ```

2. **Full Rollback:**
   ```powershell
   git checkout core/engine/system3_signal_engine.py
   git checkout core/engine/ultra_models_loader.py
   ```

3. **Verify:**
   - System reverts to delta-based fallback (66.7% win rate)
   - All safety flags still False
   - No live trading enabled

---

## SUCCESS CRITERIA

### Phase 381-388 is COMPLETE when:

✅ All 8 phase files created and functional
✅ Ultra models loader working (5/5 models loadable)
✅ Signal engine integration successful
✅ Block test shows 8/8 PASS
✅ Telemetry confirms Ultra models being used
✅ Fail-safe guard verified (delta fallback works)
✅ No safety config changes detected
✅ DRY-RUN enforcement confirmed
✅ Implementation summary generated

---

## NEXT STEPS (AFTER 381-388)

### Future Phases (389-400)
- **Path B:** Blended Training with SMOTE (Phases 389-394)
- **Path C:** Auto-Retraining Pipeline (Phases 395-400)

**Condition:** Only implement after successful paper trading with Ultra models for 5-10 days

---

## REFERENCES

- `ML_ISSUE_COMPLETE_SUMMARY.md` - Root cause analysis
- `QUICK_IMPLEMENTATION_ULTRA_MODELS.md` - Implementation guide
- `WORLD_CLASS_ML_SOLUTIONS.md` - Technical deep dive
- `ML_SOLUTION_VISUAL_GUIDE.md` - Visual explanations
- `ACTION_PLAN_ML_TRAINING.md` - Complete action plan
- `SYSTEM3_PHASES_361_380_BLOCK_HEALTH.md` - Previous phase status

---

**END OF PLAN - READY FOR IMPLEMENTATION**
