# Sprint 1: Deep Learning Enhancements - Implementation Specification
**Phases 249-260: LSTM-Based Forward Returns Prediction & Online Learning**  
**Version:** 1.0  
**Target Completion:** Q1 2026  
**Status:** ✅ Specification Ready for Implementation

---

## 📋 Executive Summary

### Objective
Implement Deep Learning (LSTM) models as **shadow models** to enhance forward returns prediction alongside existing RandomForest/XGBoost models. Phases 249-260 will provide online learning, drift detection, and model retraining infrastructure.

### Scope
- **Phases 249-260** (12 phases total)
- **Primary Focus:** LSTM for time-series forward returns prediction
- **Integration:** Non-invasive addition to existing Phase 221 pipeline
- **Safety:** DRY-RUN only, no impact on live trading paths

### Success Criteria
- LSTM model achieves accuracy ≥60% (at parity with RandomForest)
- Online learning updates improve model performance by ≥5% over 30 days
- Shadow model runs without errors for 5 consecutive trading days
- Drift detection triggers retraining when accuracy drops >10%

---

## 🎯 Phase-by-Phase Implementation Plan

### Phase 249: LSTM Forward Returns Predictor
**Module:** `core/engine/system3_phase249_lstm_forward_predictor.py`  
**Priority:** ⭐ CRITICAL (Foundation for phases 250-260)

#### Objective
Train LSTM model to predict forward returns (5min, 10min, 15min) for 5 underlyings (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX).

#### Inputs
- `storage/live/angel_index_ai_signals_with_forward.csv` (Phase 221 output)
- Historical signals with forward returns (target: forward_return_5m, forward_return_10m, forward_return_15m)

#### Data Preprocessing
```python
# Sequence length for LSTM (use last N timestamps)
SEQUENCE_LENGTH = 20  # Last 20 signals (~30 minutes of data)

# Features for LSTM input
FEATURE_COLUMNS = [
    "close", "high", "low", "volume",
    "iv_atm", "vix_analog", 
    "signal_strength", "trend_score",
    "forward_return_5m", "forward_return_10m", "forward_return_15m"
]

# Target (3-class classification: BUY=1, SELL=-1, NEUTRAL=0)
TARGET_COLUMN = "signal"  # or create new "lstm_signal" column
```

#### LSTM Architecture
```python
import torch
import torch.nn as nn

class ForwardReturnsLSTM(nn.Module):
    def __init__(self, input_size=10, hidden_size=64, num_layers=2, num_classes=3):
        super(ForwardReturnsLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2  # Dropout for regularization
        )
        
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_size)
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # LSTM forward pass
        out, _ = self.lstm(x, (h0, c0))
        
        # Take output from last timestamp
        out = self.fc(out[:, -1, :])
        return out
```

#### Training Loop
```python
def train_lstm_for_underlying(underlying: str, df: pd.DataFrame):
    """Train LSTM model for a single underlying."""
    from torch.utils.data import DataLoader, TensorDataset
    from sklearn.preprocessing import StandardScaler
    import torch.optim as optim
    
    # Filter data for underlying
    df_underlying = df[df["underlying"] == underlying].copy()
    
    # Create sequences (sliding window)
    sequences = []
    labels = []
    
    for i in range(SEQUENCE_LENGTH, len(df_underlying)):
        seq = df_underlying.iloc[i-SEQUENCE_LENGTH:i][FEATURE_COLUMNS].values
        label = df_underlying.iloc[i]["signal"]  # BUY=1, SELL=-1, NEUTRAL=0
        sequences.append(seq)
        labels.append(label)
    
    # Convert to tensors
    X = torch.tensor(sequences, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)
    
    # Train/test split
    train_size = int(0.8 * len(X))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # DataLoader
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    # Initialize model
    model = ForwardReturnsLSTM(
        input_size=len(FEATURE_COLUMNS),
        hidden_size=64,
        num_layers=2,
        num_classes=3
    )
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop (10 epochs)
    for epoch in range(10):
        model.train()
        total_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}/10 - Loss: {total_loss/len(train_loader):.4f}")
    
    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test)
        _, predicted = torch.max(test_outputs, 1)
        accuracy = (predicted == y_test).sum().item() / len(y_test)
    
    print(f"[{underlying}] LSTM Test Accuracy: {accuracy:.4f}")
    
    # Save model
    model_file = Path(f"core/models/angel_one/{underlying}_lstm_model.pth")
    torch.save(model.state_dict(), model_file)
    print(f"[SAVE] LSTM Model: {model_file}")
    
    return accuracy
```

#### Outputs
- **Model Files:** `core/models/angel_one/{underlying}_lstm_model.pth` (5 files)
- **Metadata:** `core/models/angel_one/{underlying}_lstm_meta.json` (accuracy, training date, feature list)
- **Phase Report:** `logs/phase249_lstm_training_YYYY-MM-DD.log`

#### Integration with Phase 221
- Phase 249 runs **after** Phase 221 (forward returns calculated)
- LSTM predictions added as new columns: `lstm_signal`, `lstm_confidence`
- Original `signal` column preserved (RandomForest/XGBoost predictions)
- CSV output: `storage/live/angel_index_ai_signals_with_forward_lstm.csv`

#### Success Criteria
- ✅ LSTM trains without errors for all 5 underlyings
- ✅ Test accuracy ≥60% (at parity with RandomForest)
- ✅ Training completes in <5 minutes
- ✅ Model files saved successfully

---

### Phase 250: Online Learning Manager
**Module:** `core/engine/system3_phase250_online_learning_manager.py`  
**Priority:** ⭐ HIGH (Enables continuous improvement)

#### Objective
Implement online learning to update LSTM models with new data as trading days progress.

#### Strategy: Incremental Training
```python
def update_lstm_with_new_data(underlying: str, new_data: pd.DataFrame):
    """Update existing LSTM model with new sequences."""
    import torch
    
    # Load existing model
    model_file = Path(f"core/models/angel_one/{underlying}_lstm_model.pth")
    model = ForwardReturnsLSTM(input_size=10, hidden_size=64, num_layers=2, num_classes=3)
    model.load_state_dict(torch.load(model_file))
    model.train()  # Set to training mode
    
    # Create new sequences from recent data
    new_sequences = []
    new_labels = []
    for i in range(SEQUENCE_LENGTH, len(new_data)):
        seq = new_data.iloc[i-SEQUENCE_LENGTH:i][FEATURE_COLUMNS].values
        label = new_data.iloc[i]["signal"]
        new_sequences.append(seq)
        new_labels.append(label)
    
    X_new = torch.tensor(new_sequences, dtype=torch.float32)
    y_new = torch.tensor(new_labels, dtype=torch.long)
    
    # Incremental update (1 epoch with low learning rate)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)  # Low LR for stability
    criterion = nn.CrossEntropyLoss()
    
    optimizer.zero_grad()
    outputs = model(X_new)
    loss = criterion(outputs, y_new)
    loss.backward()
    optimizer.step()
    
    print(f"[{underlying}] Online Learning Update - Loss: {loss.item():.4f}")
    
    # Save updated model
    torch.save(model.state_dict(), model_file)
    print(f"[SAVE] Updated LSTM Model: {model_file}")
```

#### Trigger Conditions
- **Frequency:** Every 30 minutes during market hours (9:15 AM - 3:30 PM)
- **Data Threshold:** Minimum 50 new sequences (enough for stable update)
- **Validation:** Test on recent data before overwriting model

#### Outputs
- **Updated Models:** `core/models/angel_one/{underlying}_lstm_model.pth` (in-place update)
- **Update Log:** `logs/phase250_online_learning_YYYY-MM-DD.log`
- **Metadata:** Update `online_learning_count` in model metadata JSON

#### Success Criteria
- ✅ Model updates complete in <30 seconds
- ✅ No degradation in test accuracy (>5% drop triggers rollback)
- ✅ Update log shows consistent improvements

---

### Phase 251: Model Drift Tracker
**Module:** `core/engine/system3_phase251_model_drift_tracker.py`  
**Priority:** 🔶 MEDIUM (Quality assurance)

#### Objective
Detect when LSTM model performance degrades (drift) and trigger retraining.

#### Metrics to Track
```python
DRIFT_METRICS = {
    "prediction_accuracy": 0.60,  # Alert if drops below 60%
    "prediction_distribution": {
        "BUY": 0.33,  # Expect roughly balanced predictions
        "SELL": 0.33,
        "NEUTRAL": 0.34,
    },
    "confidence_mean": 0.70,  # Alert if confidence drops below 70%
}
```

#### Drift Detection Logic
```python
def detect_model_drift(underlying: str, recent_predictions: pd.DataFrame):
    """Check if model performance has degraded."""
    # Calculate recent accuracy (last 100 predictions)
    recent_accuracy = (
        recent_predictions["lstm_signal"] == recent_predictions["actual_signal"]
    ).mean()
    
    # Check prediction distribution (detect bias)
    prediction_counts = recent_predictions["lstm_signal"].value_counts(normalize=True)
    
    # Drift conditions
    drift_detected = False
    reasons = []
    
    if recent_accuracy < 0.60:
        drift_detected = True
        reasons.append(f"Low accuracy: {recent_accuracy:.2%}")
    
    if prediction_counts.get(1, 0) > 0.70:  # >70% BUY signals
        drift_detected = True
        reasons.append("Prediction bias: Too many BUY signals")
    
    if drift_detected:
        print(f"[DRIFT ALERT] {underlying} - {', '.join(reasons)}")
        # Trigger Phase 252 (Model Retraining Scheduler)
        return {"drift": True, "reasons": reasons}
    
    return {"drift": False}
```

#### Outputs
- **Drift Report:** `logs/phase251_drift_report_YYYY-MM-DD.json`
- **Alert Triggers:** Email/Slack notification if drift detected (optional)

---

### Phase 252: Model Retraining Scheduler
**Module:** `core/engine/system3_phase252_model_retraining_scheduler.py`  
**Priority:** 🔶 MEDIUM (Automation)

#### Objective
Automatically schedule and execute full LSTM retraining when drift is detected.

#### Trigger Conditions
- **Drift Detected:** Phase 251 alerts
- **Time-Based:** Every 7 days (weekly retraining)
- **Data Threshold:** Minimum 500 new sequences since last training

#### Retraining Flow
```python
def schedule_retraining(underlying: str):
    """Schedule full model retraining."""
    print(f"[RETRAINING SCHEDULED] {underlying} - Queued for next off-market window")
    
    # Add to retraining queue
    queue_file = Path("logs/retraining_queue.json")
    queue = json.load(queue_file.open()) if queue_file.exists() else []
    queue.append({
        "underlying": underlying,
        "scheduled_at": datetime.utcnow().isoformat(),
        "trigger": "drift_detected",
        "status": "PENDING",
    })
    with queue_file.open("w") as f:
        json.dump(queue, f, indent=2)
```

#### Execution Window
- **Preferred Time:** Post-market (after 3:30 PM) or pre-market (before 9:15 AM)
- **Avoid:** Market hours (to prevent interruption)

---

### Phase 253: Shadow Model Validator
**Module:** `core/engine/system3_phase253_shadow_model_validator.py`  
**Priority:** 🔶 MEDIUM (Safety)

#### Objective
Validate retrained LSTM models before promoting them to production.

#### Validation Tests
```python
VALIDATION_TESTS = [
    "model_loads_without_errors",
    "predictions_run_successfully",
    "accuracy_above_threshold",  # ≥60%
    "no_prediction_bias",  # Max 60% in any single class
    "inference_time_acceptable",  # <500ms per prediction
]
```

#### Test Execution
```python
def validate_retrained_model(underlying: str, model_path: Path):
    """Run validation suite on retrained model."""
    results = {"status": "PASS", "tests": {}}
    
    # Test 1: Model loads
    try:
        model = ForwardReturnsLSTM(...)
        model.load_state_dict(torch.load(model_path))
        results["tests"]["model_loads"] = "PASS"
    except Exception as e:
        results["tests"]["model_loads"] = f"FAIL - {e}"
        results["status"] = "FAIL"
        return results
    
    # Test 2: Predictions run
    # ... (similar checks for remaining tests)
    
    return results
```

#### Promotion Logic
- If all tests PASS → Promote to production (overwrite existing model)
- If any test FAIL → Rollback to previous model, alert operator

---

### Phase 254: Production Model Switcher
**Module:** `core/engine/system3_phase254_production_model_switcher.py`  
**Priority:** 🔶 MEDIUM (Automation)

#### Objective
Atomically switch from shadow LSTM model to production after validation.

#### Switching Strategy
```python
def promote_shadow_model(underlying: str):
    """Promote validated shadow model to production."""
    shadow_model = Path(f"core/models/angel_one/{underlying}_lstm_model_shadow.pth")
    prod_model = Path(f"core/models/angel_one/{underlying}_lstm_model.pth")
    backup_model = Path(f"core/models/angel_one/{underlying}_lstm_model_backup.pth")
    
    # Backup current production model
    if prod_model.exists():
        shutil.copy(prod_model, backup_model)
        print(f"[BACKUP] {prod_model} → {backup_model}")
    
    # Promote shadow to production
    shutil.move(shadow_model, prod_model)
    print(f"[PROMOTE] {shadow_model} → {prod_model}")
```

---

### Phase 255: Model Performance Logger
**Module:** `core/engine/system3_phase255_model_performance_logger.py`  
**Priority:** 🟢 LOW (Observability)

#### Objective
Log LSTM model predictions, accuracy, and confidence over time.

#### Metrics to Log
- **Prediction counts:** BUY/SELL/NEUTRAL per underlying
- **Accuracy:** Rolling 7-day accuracy
- **Confidence:** Average confidence score per prediction
- **Execution time:** Inference latency

#### Log Format (JSON)
```json
{
  "timestamp": "2025-12-05T10:30:00Z",
  "underlying": "NIFTY",
  "model_version": "lstm_v1",
  "prediction": "BUY",
  "confidence": 0.87,
  "accuracy_7d": 0.63,
  "inference_time_ms": 42
}
```

---

### Phase 256-260: Live Recalibration (Reserved)
**Modules:** `core/engine/system3_phase256-260_*.py`  
**Priority:** 🟢 LOW (Future enhancement)

#### Placeholder Objectives
- **Phase 256:** Live feature recalibrator (adjust feature scaling dynamically)
- **Phase 257:** Confidence interval adjuster (tune prediction thresholds)
- **Phase 258:** Multi-model ensemble coordinator (blend LSTM + RandomForest)
- **Phase 259:** Real-time feedback loop (incorporate trade outcomes)
- **Phase 260:** A/B testing framework (compare model variants)

**Status:** ⚠️ **DEFERRED to Sprint 2** (after Phase 249-255 proven stable)

---

## 🛠️ Technical Requirements

### New Dependencies
Add to `requirements.txt`:
```txt
# Deep Learning (Phase 249-260)
torch>=2.0.0
tensorboard>=2.15.0  # For training monitoring (optional)
```

### File Structure
```
core/
├── engine/
│   ├── system3_phase249_lstm_forward_predictor.py  ⭐ NEW
│   ├── system3_phase250_online_learning_manager.py  ⭐ NEW
│   ├── system3_phase251_model_drift_tracker.py  ⭐ NEW
│   ├── system3_phase252_model_retraining_scheduler.py  ⭐ NEW
│   ├── system3_phase253_shadow_model_validator.py  ⭐ NEW
│   ├── system3_phase254_production_model_switcher.py  ⭐ NEW
│   ├── system3_phase255_model_performance_logger.py  ⭐ NEW
│   └── system3_phase256-260_*.py  (deferred to Sprint 2)
│
├── models/
│   └── angel_one/
│       ├── NIFTY_lstm_model.pth  ⭐ NEW
│       ├── BANKNIFTY_lstm_model.pth  ⭐ NEW
│       ├── FINNIFTY_lstm_model.pth  ⭐ NEW
│       ├── MIDCPNIFTY_lstm_model.pth  ⭐ NEW
│       ├── SENSEX_lstm_model.pth  ⭐ NEW
│       └── *_lstm_meta.json  (metadata for each model)
│
logs/
├── phase249_lstm_training_YYYY-MM-DD.log
├── phase250_online_learning_YYYY-MM-DD.log
├── phase251_drift_report_YYYY-MM-DD.json
├── retraining_queue.json
└── phase255_model_performance_YYYY-MM-DD.jsonl

storage/
└── live/
    └── angel_index_ai_signals_with_forward_lstm.csv  ⭐ NEW
```

### Integration Points

#### 1. Phase 221 → Phase 249 (Forward Returns → LSTM Training)
```python
# In system3_autorun_master.py (or equivalent)
def run_pre_market_phases():
    # ... existing phases 201-230 ...
    
    # Phase 221: Compute forward returns
    result_221 = run_phase221()
    if result_221["status"] == "OK":
        # Phase 249: Train LSTM (runs after Phase 221)
        result_249 = run_phase249()
        print(f"Phase 249: {result_249['status']}")
```

#### 2. Phase 250 → Phase 251 (Online Learning → Drift Detection)
```python
# During market hours (every 30 minutes)
def run_market_hours_cycle():
    # ... existing phases 220-260 ...
    
    # Phase 250: Update LSTM with new data
    result_250 = run_phase250()
    
    # Phase 251: Check for model drift
    result_251 = run_phase251()
    if result_251.get("drift_detected"):
        # Phase 252: Schedule retraining
        run_phase252()
```

---

## 📊 Performance Benchmarks

### Training Time (Expected)
- **Phase 249 (Initial Training):** 2-5 minutes per underlying (10-25 minutes total for 5 underlyings)
- **Phase 250 (Online Learning):** <30 seconds per underlying
- **Phase 252 (Full Retraining):** Same as Phase 249 (2-5 minutes)

### Inference Time (Expected)
- **LSTM Prediction:** <100ms per sequence (20 timestamps)
- **Batch Prediction (100 sequences):** <1 second

### Memory Usage (Expected)
- **Training:** ~500 MB per underlying (peaks at 1 GB with optimizer states)
- **Inference:** ~200 MB (model loaded in memory)

---

## 🚦 Rollout Plan

### Stage 1: Development (Week 1-2)
- ✅ Implement Phase 249 (LSTM training)
- ✅ Verify training completes without errors
- ✅ Validate accuracy ≥60% on test data

### Stage 2: Shadow Testing (Week 3-4)
- ✅ Run Phase 249 daily post-market
- ✅ Compare LSTM predictions vs. RandomForest (no live usage yet)
- ✅ Log prediction accuracy, confidence, execution time

### Stage 3: Online Learning (Week 5-6)
- ✅ Implement Phase 250 (online learning)
- ✅ Update models every 30 minutes during market hours
- ✅ Monitor for accuracy improvements

### Stage 4: Automation (Week 7-8)
- ✅ Implement Phases 251-255 (drift detection, retraining, validation, promotion, logging)
- ✅ Test full pipeline: Drift detected → Retrain → Validate → Promote
- ✅ Verify rollback works if validation fails

### Stage 5: Production Integration (Week 9-10)
- ✅ Add LSTM predictions to signal pipeline (Phase 222 uses `lstm_signal` column)
- ✅ Ensemble logic: Combine RandomForest + LSTM predictions (weighted average)
- ✅ Monitor for 5 consecutive trading days without errors

---

## ⚠️ Risks & Mitigations

### Risk 1: LSTM Overfitting
**Mitigation:**
- Use dropout (0.2) in LSTM architecture
- Early stopping if validation loss increases
- Cross-validation on multiple date ranges

### Risk 2: Online Learning Instability
**Mitigation:**
- Low learning rate (0.0001) for incremental updates
- Rollback to previous model if accuracy drops >5%
- Limit update frequency (max 1 per 30 minutes)

### Risk 3: Training Time Too Long
**Mitigation:**
- Train models post-market (after 3:30 PM) when no time pressure
- Use GPU acceleration if available (check `torch.cuda.is_available()`)
- Parallelize training across underlyings (use `multiprocessing`)

### Risk 4: Model Drift Goes Undetected
**Mitigation:**
- Phase 251 runs every 30 minutes during market hours
- Alert operator via log message if drift detected
- Automated retraining (Phase 252) triggers within 24 hours

---

## ✅ Definition of Done (Sprint 1)

### Phase 249: LSTM Training
- [ ] LSTM trains successfully for all 5 underlyings
- [ ] Test accuracy ≥60% for each underlying
- [ ] Model files saved to `core/models/angel_one/`
- [ ] Metadata JSON includes accuracy, training date, feature list
- [ ] Training log saved to `logs/phase249_*.log`

### Phase 250: Online Learning
- [ ] Incremental updates complete in <30 seconds
- [ ] No accuracy degradation (>5% drop triggers rollback)
- [ ] Update log shows consistent model improvements
- [ ] Metadata JSON tracks `online_learning_count`

### Phase 251: Drift Detection
- [ ] Drift detection runs every 30 minutes during market hours
- [ ] Alerts logged to `logs/phase251_drift_report_*.json`
- [ ] Drift triggers Phase 252 (retraining scheduler)

### Phase 252: Retraining Scheduler
- [ ] Queues retraining tasks for post-market execution
- [ ] Retraining queue JSON file persists across restarts
- [ ] Full retraining completes in <10 minutes per underlying

### Phase 253: Shadow Model Validator
- [ ] All 5 validation tests run successfully
- [ ] Failed validation prevents model promotion
- [ ] Validation results logged to `logs/phase253_validation_*.log`

### Phase 254: Production Model Switcher
- [ ] Atomic model promotion (shadow → production)
- [ ] Backup model created before promotion
- [ ] Rollback works if promoted model fails

### Phase 255: Model Performance Logger
- [ ] Predictions logged to `logs/phase255_model_performance_*.jsonl`
- [ ] Metrics include accuracy, confidence, inference time
- [ ] Log format parseable by pandas (`pd.read_json(..., lines=True)`)

### Integration Tests
- [ ] Phase 221 → Phase 249 pipeline works end-to-end
- [ ] Phase 250 → Phase 251 → Phase 252 automation works
- [ ] LSTM predictions appear in `angel_index_ai_signals_with_forward_lstm.csv`
- [ ] No errors in System3 startup after adding phases 249-255

### Documentation
- [ ] This spec document (`SPRINT1_DL_SPEC.md`) committed to repo
- [ ] Phase implementation documented in code docstrings
- [ ] Operator cheat sheet updated with Phase 249-255 usage

---

## 📚 References

### Existing Codebase (Patterns to Follow)
- **Training Pattern:** `core/engine/ultra_train_models.py` (lines 180-250) - RandomForest training
- **Phase Structure:** `core/engine/system3_phase221_forward_returns.py` - Phase return format
- **Model Metadata:** `core/models/angel_one/*_meta.json` - JSON structure

### Documentation
- **Phase Gaps Analysis:** `PHASE_GAPS_ANALYSIS.md` (phases 249-260 identified as critical gap)
- **Priority Summary:** `PRIORITY_IMPLEMENTATION_SUMMARY.md` (Priority 4 DL roadmap)
- **Operator Cheat Sheet:** `OPERATOR_CHEAT_SHEET.md` (how to run phases)

### External Resources
- **PyTorch LSTM Tutorial:** https://pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html
- **Time Series Classification:** https://arxiv.org/abs/1809.04356 (InceptionTime paper)
- **Online Learning:** https://scikit-learn.org/stable/modules/computing.html#incremental-learning

---

## 🎓 Operator Training for DL Phases

### Running Phase 249 (LSTM Training)
```powershell
# Manual execution (post-market recommended)
python -m core.engine.system3_phase249_lstm_forward_predictor

# Check training log
type logs\phase249_lstm_training_*.log | findstr "accuracy"

# Verify models created
dir core\models\angel_one\*_lstm_model.pth
```

### Monitoring Online Learning (Phase 250)
```powershell
# Tail online learning log
Get-Content logs\phase250_online_learning_*.log -Wait -Tail 10

# Check update count in metadata
python -c "import json; meta=json.load(open('core/models/angel_one/NIFTY_lstm_meta.json')); print(f'Updates: {meta[\"online_learning_count\"]}')"
```

### Drift Detection (Phase 251)
```powershell
# View drift report
type logs\phase251_drift_report_*.json

# Check for drift alerts
findstr "DRIFT ALERT" logs\phase251_drift_report_*.json
```

---

**This specification is production-ready. Proceed with Phase 249 implementation first, then incrementally add Phases 250-255.**

**Questions? Refer to:**
- `OPERATOR_CHEAT_SHEET.md` for daily operations
- `PHASE_GAPS_ANALYSIS.md` for phase context
- `PRIORITY_IMPLEMENTATION_SUMMARY.md` for DL roadmap

**Happy coding! 🚀**
