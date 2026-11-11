# System3 Phases 7-9: Verification Commands

Quick reference for checking Phase 7-9 results.

---

## Phase 7: Verify Master Dataset

### Check if CSV file exists:
```bash
dir storage\learning\dhan_index_real_master_dataset.csv
```

### View first 10 rows of master dataset:
```bash
python -c "import pandas as pd; df=pd.read_csv(r'storage\learning\dhan_index_real_master_dataset.csv'); print(df.head(10).to_string()); print(f'\nTotal rows: {len(df)}'); print(f'\nColumns: {list(df.columns)}')"
```

### Check file size and row count:
```bash
python -c "import pandas as pd; df=pd.read_csv(r'storage\learning\dhan_index_real_master_dataset.csv'); print(f'Total Rows: {len(df)}'); print(f'Total Columns: {len(df.columns)}'); print(f'\nColumn Names:\n{list(df.columns)}'); print(f'\nData Types:\n{df.dtypes}')"
```

### View summary statistics:
```bash
python -c "import pandas as pd; df=pd.read_csv(r'storage\learning\dhan_index_real_master_dataset.csv'); print(df.describe())"
```

---

## Phase 8: Verify Blended Models

### Check if blended models directory exists:
```bash
dir core\models\dhan_real_blended
```

### List all blended model files:
```bash
dir core\models\dhan_real_blended\*.pkl
dir core\models\dhan_real_blended\*.json
```

### View NIFTY model metadata:
```bash
type core\models\dhan_real_blended\NIFTY_model_blended_v3_meta.json
```

### View all model metadata files:
```bash
type core\models\dhan_real_blended\*_meta.json
```

### Verify baseline models are untouched:
```bash
dir core\models\dhan\*.pkl
```

### Count total files in blended directory:
```bash
python -c "from pathlib import Path; p = Path('core/models/dhan_real_blended'); files = list(p.glob('*')); print(f'Total files: {len(files)}'); [print(f.name) for f in files]"
```

---

## Phase 9: Verify Profile System

### Run profile display (Menu Option 72):
```bash
python run_system3.py
# Then select option 72
```

### Or run directly:
```bash
python -m core.engine.dhan_model_selector
```

### Check current profile config:
```bash
type storage\config\system3_live_beta_profile.json
```

### Verify model selector can load models:
```bash
python -c "from core.engine.dhan_model_selector import get_active_profile, load_models_for_profile; profile = get_active_profile(); print(f'Active Profile: {profile}'); models = load_models_for_profile(profile); print(f'Models loaded: {len(models[\"models\"])}'); [print(f'{u}: {p}') for u, p in models['model_paths'].items()]"
```

---

## Quick All-in-One Verification

### Run this single command to check everything:
```bash
python -c "
import pandas as pd
from pathlib import Path

print('=== PHASE 7 VERIFICATION ===')
csv_path = Path('storage/learning/dhan_index_real_master_dataset.csv')
if csv_path.exists():
    df = pd.read_csv(csv_path)
    print(f'✅ Master Dataset CSV: {len(df)} rows, {len(df.columns)} columns')
    print(f'   File: {csv_path}')
else:
    print('❌ Master Dataset CSV: NOT FOUND')

print('\n=== PHASE 8 VERIFICATION ===')
blended_dir = Path('core/models/dhan_real_blended')
if blended_dir.exists():
    pkl_files = list(blended_dir.glob('*.pkl'))
    json_files = list(blended_dir.glob('*.json'))
    print(f'✅ Blended Models Directory: EXISTS')
    print(f'   Model files: {len(pkl_files)}')
    print(f'   Meta files: {len(json_files)}')
    for f in pkl_files:
        print(f'   - {f.name}')
else:
    print('❌ Blended Models Directory: NOT FOUND')

print('\n=== PHASE 9 VERIFICATION ===')
from core.engine.dhan_model_selector import get_active_profile, load_models_for_profile
profile = get_active_profile()
models = load_models_for_profile(profile)
print(f'✅ Active Profile: {profile}')
print(f'   Models loaded: {len(models[\"models\"])}')
for u, p in models['model_paths'].items():
    print(f'   {u}: {Path(p).name}')
"
```

---

## Expected Results

### Phase 7 Expected Output:
```
✅ Master Dataset CSV: <N> rows, <M> columns
   File: storage/learning/dhan_index_real_master_dataset.csv
```

### Phase 8 Expected Output:
```
✅ Blended Models Directory: EXISTS
   Model files: 5
   Meta files: 5
   - NIFTY_model_blended_v3.pkl
   - BANKNIFTY_model_blended_v3.pkl
   - FINNIFTY_model_blended_v3.pkl
   - MIDCPNIFTY_model_blended_v3.pkl
   - SENSEX_model_blended_v3.pkl
```

### Phase 9 Expected Output:
```
✅ Active Profile: BASELINE
   Models loaded: 5
   NIFTY: NIFTY_model.pkl
   BANKNIFTY: BANKNIFTY_model.pkl
   FINNIFTY: FINNIFTY_model.pkl
   MIDCPNIFTY: MIDCPNIFTY_model.pkl
   SENSEX: SENSEX_model.pkl
```

---

## Troubleshooting

### If Phase 7 CSV not found:
```bash
# Re-run Phase 7
python run_system3.py
# Select option 70
```

### If Phase 8 models not found:
```bash
# Re-run Phase 8
python run_system3.py
# Select option 71
```

### If Phase 9 profile not working:
```bash
# Check config file
type storage\config\system3_live_beta_profile.json

# Run directly
python -m core.engine.dhan_model_selector
```

---

**Quick Reference**: Save this file for easy access to verification commands!

