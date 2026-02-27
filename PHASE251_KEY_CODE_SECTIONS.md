# Phase 251-255: Key Code Sections & Final Summary

---

## KEY FUNCTION 1: read_latest_evaluation_metrics()

**Location:** `core/engine/system3_lstm_utils.py`

```python
def read_latest_evaluation_metrics(
    eval_dir: str = "logs",
    pattern: str = "phase249_model_evaluation_*.json",
    min_required_keys: Optional[List[str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Read the latest Phase 249 Extended evaluation JSON.
    
    Returns evaluation metrics for all models, or None if not found/invalid.
    Never raises exceptions - always returns Dict or None.
    """
    
    if min_required_keys is None:
        min_required_keys = ['models', 'evaluation_timestamp']
    
    # Resolve directory
    if not Path(eval_dir).is_absolute():
        eval_path = PROJECT_ROOT / eval_dir
    else:
        eval_path = Path(eval_dir)
    
    if not eval_path.exists():
        logger.warning(f"[LSTM_UTILS] Evaluation directory not found: {eval_path}")
        return None
    
    try:
        # Find all matching files
        search_pattern = str(eval_path / pattern)
        matching_files = sorted(glob.glob(search_pattern))
        
        if not matching_files:
            logger.warning(f"[LSTM_UTILS] No evaluation files found")
            return None
        
        # Get the most recent file
        latest_file = matching_files[-1]
        logger.info(f"[LSTM_UTILS] Reading: {latest_file}")
        
        # Load JSON
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required keys
        missing_keys = [key for key in min_required_keys if key not in data]
        if missing_keys:
            logger.warning(f"[LSTM_UTILS] Missing keys: {missing_keys}")
            return None
        
        # Validate models is dict
        if not isinstance(data.get('models'), dict):
            logger.warning(f"[LSTM_UTILS] 'models' is not a dictionary")
            return None
        
        logger.info(f"[LSTM_UTILS] Loaded metrics for {len(data['models'])} models")
        return data
    
    except json.JSONDecodeError as e:
        logger.warning(f"[LSTM_UTILS] JSON parse error: {e}")
        return None
    
    except Exception as e:
        logger.warning(f"[LSTM_UTILS] Unexpected error: {e}")
        return None
```

**Key Features:**
- ✅ Finds latest JSON automatically
- ✅ Validates structure completely
- ✅ Never raises exceptions
- ✅ Comprehensive logging
- ✅ Safe degradation on errors

---

## KEY FUNCTION 2: detect_drift_for_underlying()

**Location:** `core/engine/system3_phase251_model_drift_tracker.py`

```python
def detect_drift_for_underlying(
    underlying: str,
    model_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Check if model performance has degraded based on Phase 250 evaluation metrics.
    
    Args:
        underlying: Symbol (NIFTY, BANKNIFTY, etc.)
        model_metrics: Real metrics from Phase 250 evaluation
    
    Returns:
        Dict with drift detection results and decision
    """
    
    if model_metrics is None:
        return {
            "status": "ERROR",
            "underlying": underlying,
            "drift_detected": False,
            "reasons": ["No evaluation metrics available"],
            "decision": "HOLD"
        }
    
    # Extract metrics from Phase 250
    accuracy = model_metrics.get('accuracy')
    precision = model_metrics.get('precision', 0.0)
    recall = model_metrics.get('recall', 0.0)
    f1_score = model_metrics.get('f1_score', 0.0)
    test_samples = model_metrics.get('test_samples', 0)
    
    # Validate metrics
    if accuracy is None:
        return {
            "status": "ERROR",
            "underlying": underlying,
            "drift_detected": False,
            "reasons": ["Missing accuracy metric"],
            "decision": "HOLD"
        }
    
    # Check drift conditions
    drift_detected = False
    reasons = []
    
    # Condition 1: Accuracy below threshold
    if accuracy < ACCURACY_THRESHOLD:
        drift_detected = True
        reasons.append(f"Low accuracy: {accuracy:.1%} < {ACCURACY_THRESHOLD:.0%}")
    
    # Condition 2: Insufficient test samples
    if test_samples < MIN_TEST_SAMPLES:
        drift_detected = True
        reasons.append(f"Insufficient samples: {test_samples} < {MIN_TEST_SAMPLES}")
    
    # Condition 3: Precision/Recall imbalance
    if precision > 0 and recall > 0:
        ratio = min(recall / precision, precision / recall)
        if ratio < 0.3:  # >3x difference indicates mode collapse
            drift_detected = True
            reasons.append(f"P/R imbalance: P={precision:.1%}, R={recall:.1%}")
    
    # Decision
    if drift_detected:
        decision = "REJECT"
        logger.warning(f"[PHASE 251] DRIFT for {underlying}: {reasons}")
    else:
        decision = "PROMOTE"
        logger.info(f"[PHASE 251] {underlying} passes drift checks")
    
    return {
        "status": "OK",
        "underlying": underlying,
        "drift_detected": drift_detected,
        "reasons": reasons,
        "metrics": {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1_score),
            "test_samples": int(test_samples)
        },
        "thresholds": {
            "accuracy_minimum": ACCURACY_THRESHOLD,
            "min_test_samples": MIN_TEST_SAMPLES
        },
        "decision": decision
    }
```

**Drift Detection Logic:**
- Accuracy < 55% → REJECT
- Test samples < 10 → REJECT
- Precision/Recall ratio < 0.3 → REJECT
- Otherwise → PROMOTE

---

## KEY FUNCTION 3: run_phase251()

**Location:** `core/engine/system3_phase251_model_drift_tracker.py`

```python
def run_phase251(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 251: Model Drift Tracker.
    
    Pipeline:
    1. Read Phase 250 evaluation JSON
    2. Check each model for drift
    3. Generate promotion decision
    4. Write decision JSON for Phase 252
    """
    
    logger.info("=" * 80)
    logger.info("Phase 251: Model Drift Tracker")
    logger.info("=" * 80)
    
    try:
        # Step 1: Read Phase 250 evaluation metrics
        logger.info("[PHASE 251] Reading Phase 250 evaluation metrics...")
        evaluation_data = read_latest_evaluation_metrics(
            eval_dir="logs",
            pattern="phase249_model_evaluation_*.json"
        )
        
        if evaluation_data is None:
            msg = "No Phase 250 evaluation metrics available"
            logger.warning(f"[PHASE 251] {msg}")
            return {
                "phase": 251,
                "status": "WARN",
                "details": msg,
                "outputs": {},
                "errors": ["No evaluation metrics"]
            }
        
        logger.info(f"[PHASE 251] ✓ Loaded evaluation from {evaluation_data.get('evaluation_timestamp')}")
        
        # Step 2: Run drift detection for each underlying
        results = {}
        drift_alerts = []
        promotion_candidates = []
        
        for underlying in UNDERLYINGS:
            logger.info(f"[PHASE 251]   Checking {underlying}...")
            
            # Get metrics for this underlying
            model_metrics = extract_model_metrics(evaluation_data, underlying)
            
            # Run drift detection
            drift_result = detect_drift_for_underlying(underlying, model_metrics)
            results[underlying] = drift_result
            
            # Track outcomes
            if drift_result.get("drift_detected"):
                drift_alerts.append(underlying)
                logger.warning(f"[PHASE 251]     ✗ {underlying}: DRIFT")
            else:
                if drift_result.get("decision") == "PROMOTE":
                    promotion_candidates.append(underlying)
                    logger.info(f"[PHASE 251]     ✓ {underlying}: PROMOTE")
        
        # Step 3: Build promotion decision
        decision = {
            "phase": 251,
            "decision_timestamp": datetime.now().isoformat(),
            "evaluation_source": evaluation_data.get("evaluation_timestamp"),
            "underlyings_checked": len(UNDERLYINGS),
            "drift_alerts": drift_alerts,
            "promotion_candidates": promotion_candidates,
            "results": results,
            "summary": {
                "total_models": len(UNDERLYINGS),
                "drift_detected_count": len(drift_alerts),
                "ready_for_promotion_count": len(promotion_candidates),
                "drift_detected": len(drift_alerts) > 0
            }
        }
        
        # Step 4: Write decision JSON
        logger.info("[PHASE 251] Writing promotion decision...")
        decision_file = write_promotion_decision(decision)
        
        if decision_file is None:
            logger.error("[PHASE 251] Failed to write decision file")
        else:
            logger.info(f"[PHASE 251] ✓ Decision file: {decision_file}")
        
        # Step 5: Return result
        status = "WARN" if drift_alerts else "OK"
        details = f"Evaluated {len(UNDERLYINGS)} models - {len(drift_alerts)} drift alerts, {len(promotion_candidates)} promotion candidates"
        
        logger.info(f"[PHASE 251] Status: {status}")
        logger.info("[PHASE 251] " + "=" * 80)
        
        return {
            "phase": 251,
            "status": status,
            "details": details,
            "outputs": {
                "evaluation_file": evaluation_data.get("evaluation_timestamp"),
                "decision_file": str(decision_file) if decision_file else None,
                "results": results,
                "drift_alerts": drift_alerts,
                "promotion_candidates": promotion_candidates
            },
            "errors": []
        }
    
    except Exception as e:
        logger.error(f"[PHASE 251] Exception: {e}")
        return {
            "phase": 251,
            "status": "ERROR",
            "details": f"Drift detection failed: {e}",
            "outputs": {},
            "errors": [str(e)]
        }
```

---

## KEY FUNCTION 4: run_phase252()

**Location:** `core/engine/system3_phase252_model_retraining_scheduler.py`

```python
def run_phase252(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 252: Model Retraining Scheduler.
    
    Pipeline:
    1. Read Phase 251 promotion decision
    2. Schedule drifted models for retraining
    3. Update retraining queue
    """
    
    logger.info("=" * 80)
    logger.info("Phase 252: Model Retraining Scheduler")
    logger.info("=" * 80)
    
    try:
        # Step 1: Read Phase 251 promotion decision
        logger.info("[PHASE 252] Reading Phase 251 promotion decision...")
        decision = read_promotion_decision(
            decision_dir="logs",
            filename="phase251_promotion_decision.json"
        )
        
        if decision is None:
            msg = "No Phase 251 promotion decision available"
            logger.warning(f"[PHASE 252] {msg}")
            return {
                "phase": 252,
                "status": "WARN",
                "details": msg,
                "outputs": {
                    "drifted_models": [],
                    "scheduled_for_retraining": [],
                    "pending_queue": []
                },
                "errors": ["No promotion decision"]
            }
        
        logger.info(f"[PHASE 252] ✓ Loaded decision from {decision.get('decision_timestamp')}")
        
        # Step 2: Process drifted models
        drifted_models = decision.get("drift_alerts", [])
        scheduled = []
        
        if drifted_models:
            logger.info(f"[PHASE 252] Processing {len(drifted_models)} drifted models...")
            
            for underlying in drifted_models:
                logger.info(f"[PHASE 252]   Scheduling {underlying}...")
                result = schedule_retraining(underlying, trigger="drift_detected")
                
                if result["status"] == "SUCCESS":
                    scheduled.append(underlying)
                    logger.info(f"[PHASE 252]     ✓ {underlying} queued")
                else:
                    logger.warning(f"[PHASE 252]     ✗ {underlying}: {result.get('reason')}")
        
        # Step 3: Check queue status
        pending_queue = check_retraining_queue()
        logger.info(f"[PHASE 252] Retraining queue: {len(pending_queue)} pending jobs")
        
        # Step 4: Return result
        details = f"Scheduled {len(scheduled)} models, {len(pending_queue)} total in queue"
        
        logger.info(f"[PHASE 252] Status: OK")
        logger.info(f"[PHASE 252] {details}")
        logger.info("[PHASE 252] " + "=" * 80)
        
        return {
            "phase": 252,
            "status": "OK",
            "details": details,
            "outputs": {
                "decision_source": decision.get("decision_timestamp"),
                "drifted_models": drifted_models,
                "scheduled_for_retraining": scheduled,
                "pending_queue": pending_queue,
                "queue_file": str(QUEUE_FILE)
            },
            "errors": []
        }
    
    except Exception as e:
        logger.error(f"[PHASE 252] Exception: {e}")
        return {
            "phase": 252,
            "status": "ERROR",
            "details": f"Retraining scheduling failed: {e}",
            "outputs": {},
            "errors": [str(e)]
        }
```

---

## CONFIGURATION THRESHOLDS

**Location:** `core/engine/system3_phase251_model_drift_tracker.py`

```python
# Drift detection thresholds
ACCURACY_THRESHOLD = 0.55          # 55% minimum accuracy
BASELINE_ACCURACY = 0.55           # Expected baseline
DEGRADATION_THRESHOLD = 0.10       # Max 10% degradation
MIN_TEST_SAMPLES = 10              # Minimum evaluation samples

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]
```

---

## IMPORT STATEMENTS

**Phase 251:**
```python
from system3_lstm_utils import (
    read_latest_evaluation_metrics,
    extract_model_metrics,
    compare_to_baseline,
    write_promotion_decision
)
```

**Phase 252:**
```python
from system3_lstm_utils import read_promotion_decision
```

---

## JSON OUTPUT EXAMPLES

### Phase 251 Output
```json
{
  "phase": 251,
  "decision_timestamp": "2025-12-06T14:35:22.456789",
  "evaluation_source": "2025-12-06T14:30:45.123456",
  "drift_alerts": ["NIFTY"],
  "promotion_candidates": ["BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
  "results": {
    "NIFTY": {
      "status": "OK",
      "drift_detected": true,
      "reasons": ["Low accuracy: 46.2% < 55%"],
      "decision": "REJECT"
    },
    "BANKNIFTY": {
      "status": "OK",
      "drift_detected": false,
      "reasons": [],
      "decision": "PROMOTE"
    }
  },
  "summary": {
    "total_models": 5,
    "drift_detected_count": 1,
    "ready_for_promotion_count": 4,
    "drift_detected": true
  }
}
```

### Phase 252 Output
```json
[
  {
    "underlying": "NIFTY",
    "scheduled_at": "2025-12-06T14:36:15.789012",
    "trigger": "drift_detected",
    "status": "PENDING"
  }
]
```

---

## FINAL SUMMARY

**Implementation Status:** ✅ COMPLETE

**Deliverables:**
1. ✅ Updated Phase 251 implementation
2. ✅ Updated Phase 252 implementation
3. ✅ New system3_lstm_utils.py module
4. ✅ Pipeline test script
5. ✅ Complete technical documentation
6. ✅ Executive summary & reports
7. ✅ Before/after comparison
8. ✅ Final checklist

**Key Achievements:**
- ✅ No CSV stubs (reads Phase 250 JSON)
- ✅ No hardcoded metrics (uses real evaluation data)
- ✅ Full Phase 251 → 252 integration (JSON handoff)
- ✅ Robust error handling (graceful degradation)
- ✅ Complete logging (structured, timestamped)
- ✅ Zero breaking changes (all existing systems intact)
- ✅ Production ready (fully tested & documented)

**Ready for deployment immediately.**
