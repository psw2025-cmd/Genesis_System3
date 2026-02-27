# System3 - Status Check Commands

## Quick Status Check

```bash
# Overall system status
python check_system3_status.py
```

---

## Detailed Status Checks

### 1. Menu System
```bash
# View full menu (shows all 41 options)
python run_system3.py
# Then type '0' to exit
```

### 2. Configuration Status
```bash
# Check trade thresholds
python -c "from core.engine.angel_trade_config import DEFAULT_THRESHOLDS; print(f'Confidence: {DEFAULT_THRESHOLDS.min_confidence}, Score: {DEFAULT_THRESHOLDS.min_abs_score}')"

# Check automation config
python -c "from core.engine.angel_automation_config import AUTOMATION_CONFIG; print(f'Auto-execute: {AUTOMATION_CONFIG.auto_execute_trades}, Auto-PnL: {AUTOMATION_CONFIG.auto_simulate_pnl}')"

# Check Ultra-Mode status
python -m core.engine.angel_ultramode_prep
```

### 3. Data Files Status
```bash
# Check if key files exist and row counts
python -c "
import pandas as pd
from pathlib import Path

files = [
    ('Signals', 'storage/live/angel_index_ai_signals.csv'),
    ('Trade Plans', 'storage/live/angel_index_ai_trades_plan.csv'),
    ('PnL Log', 'storage/live/angel_index_ai_pnl_log.csv'),
    ('Training', 'storage/training/angel_index_options_training.csv'),
    ('Outcomes', 'storage/learning/angel_real_outcomes.csv'),
]

for name, path in files:
    p = Path(path)
    if p.exists():
        try:
            df = pd.read_csv(p)
            print(f'{name}: {len(df):,} rows')
        except:
            print(f'{name}: File exists but cannot read')
    else:
        print(f'{name}: Not found')
"
```

### 4. Model Status
```bash
# Check trained models
python -c "
from pathlib import Path
models_dir = Path('core/models/angel_one')
if models_dir.exists():
    models = list(models_dir.glob('*_model.pkl'))
    print(f'Found {len(models)} models:')
    for m in models:
        print(f'  - {m.name}')
else:
    print('Models directory not found')
"
```

### 5. Module Availability
```bash
# Test key modules (should all work)
python -m core.engine.angel_real_outcome_logger
python -m core.engine.angel_signal_outcome_analyzer
python -m core.engine.angel_misfire_detector
python -m core.engine.angel_daily_learning_report
python -m core.engine.angel_rolling_learning_dashboard
```

### 6. Reports Status
```bash
# List all reports
python -c "
from pathlib import Path
reports_dir = Path('storage/reports')
if reports_dir.exists():
    reports = list(reports_dir.glob('*.txt')) + list(reports_dir.glob('*.csv'))
    print(f'Found {len(reports)} reports:')
    for r in sorted(reports)[-10:]:  # Last 10
        print(f'  - {r.name}')
else:
    print('Reports directory not found')
"
```

---

## Complete System Verification

### Step 1: Overall Status
```bash
python check_system3_status.py
```

### Step 2: Menu System
```bash
python run_system3.py
# Navigate through menu to verify all options work
```

### Step 3: Key Modules Test
```bash
# Test outcome logger
python -m core.engine.angel_real_outcome_logger

# Test signal analyzer
python -m core.engine.angel_signal_outcome_analyzer

# Test Ultra-Mode prep
python -m core.engine.angel_ultramode_prep

# Test daily reports
python -m core.engine.angel_daily_auto_reports
```

### Step 4: Data Verification
```bash
# Check training data
python -c "import pandas as pd; df = pd.read_csv('storage/training/angel_index_options_training.csv'); print(f'Training rows: {len(df):,}'); print(f'Underlyings: {df[\"underlying\"].unique() if \"underlying\" in df.columns else \"N/A\"}')"

# Check signals (if exists)
python -c "import pandas as pd; from pathlib import Path; p = Path('storage/live/angel_index_ai_signals.csv'); print(f'Signals file exists: {p.exists()}'); df = pd.read_csv(p) if p.exists() else None; print(f'Signals rows: {len(df):,}' if df is not None else 'No signals yet')"
```

---

## Quick Health Check

```bash
# One-liner to check everything
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

print('=== SYSTEM3 HEALTH CHECK ===')
print()

# Check imports
try:
    from core.engine.angel_trade_config import DEFAULT_THRESHOLDS
    from core.engine.angel_automation_config import AUTOMATION_CONFIG
    from core.engine.angel_ultramode_prep import load_ultramode_config
    print('✅ All key modules importable')
except Exception as e:
    print(f'❌ Import error: {e}')

# Check configs
try:
    config = load_ultramode_config()
    print(f'✅ Ultra-Mode: Read-only={config.read_only_mode}, Auto-execute={config.auto_trade_execution}')
except:
    print('⚠️  Ultra-Mode check failed')

# Check files
files = [
    'run_system3.py',
    'core/engine/angel_live_ai_signals.py',
    'storage/training/angel_index_options_training.csv',
]
for f in files:
    p = Path(f)
    print(f'{\"✅\" if p.exists() else \"❌\"} {f}')

print()
print('=== CHECK COMPLETE ===')
"
```

---

## Expected Output

When everything is working, you should see:

1. **check_system3_status.py**: Shows all directories, files, models, configs
2. **Menu System**: 41 options available
3. **Configs**: All auto-features DISABLED, read-only mode ACTIVE
4. **Models**: 5 models (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
5. **Data Files**: Training CSV exists, other files may be empty (normal if no live data yet)

---

## Troubleshooting

If something fails:

1. **Import errors**: Make sure you're in the project root directory
2. **File not found**: Some files are created on first use (normal)
3. **Module errors**: Check that all dependencies are installed

---

**Run `python check_system3_status.py` for the quickest overview!**

