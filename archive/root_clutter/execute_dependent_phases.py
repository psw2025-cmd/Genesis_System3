#!/usr/bin/env python3
"""
Execute dependent WARN phases (332, 334, 338, 339, 340, 343, 344) individually
Capture detailed results for reality verification
"""

import sys
import os
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / "core"))
sys.path.insert(0, str(Path(__file__).parent))

results = []

def get_csv_stats(filepath):
    """Get row count and timestamps from CSV"""
    if not Path(filepath).exists():
        return None, None, None
    
    rows = 0
    first_ts = None
    last_ts = None
    
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                rows = i + 1
                if i == 0 and 'ts' in row:
                    first_ts = row['ts']
                if 'ts' in row:
                    last_ts = row['ts']
    except:
        pass
    
    return rows, first_ts, last_ts

def get_file_age_minutes(filepath):
    """Get file age in minutes"""
    if not Path(filepath).exists():
        return None
    mtime = Path(filepath).stat().st_mtime
    return round((time.time() - mtime) / 60, 1)

# Phase 332: Signal Volume Monitor
print("\n" + "="*60)
print("PHASE 332: Signal Volume Monitor")
print("="*60)
try:
    from core.engine.system3_phase332_signal_volume_monitor import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 332,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 332,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 334: Model Drift Snapshot
print("\n" + "="*60)
print("PHASE 334: Model Drift Snapshot")
print("="*60)
try:
    from core.engine.system3_phase334_model_drift_snapshot import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 334,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 334,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 338: Signal-Outcome Correlation
print("\n" + "="*60)
print("PHASE 338: Signal-Outcome Correlation")
print("="*60)
try:
    from core.engine.system3_phase338_signal_outcome_correlation import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 338,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 338,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 339: Daily Pipeline Summary
print("\n" + "="*60)
print("PHASE 339: Daily Pipeline Summary")
print("="*60)
try:
    from core.engine.system3_phase339_daily_pipeline_summary import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 339,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 339,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 340: Regression Guard
print("\n" + "="*60)
print("PHASE 340: Regression Guard")
print("="*60)
try:
    from core.engine.system3_phase340_regression_guard import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 340,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 340,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 343: Signals Freshness Enforcer
print("\n" + "="*60)
print("PHASE 343: Signals Freshness Enforcer")
print("="*60)
try:
    from core.engine.system3_phase343_signals_freshness_enforcer import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 343,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 343,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Phase 344: Pipeline Schema Guard
print("\n" + "="*60)
print("PHASE 344: Pipeline Schema Guard")
print("="*60)
try:
    from core.engine.system3_phase344_pipeline_schema_guard import run_phase
    start = time.time()
    result = run_phase()
    duration = round(time.time() - start, 3)
    
    status = result.get('status', 'UNKNOWN')
    print(f"Status: {status}")
    print(f"Duration: {duration}s")
    if 'details' in result:
        print(f"Details: {result.get('details', '')}")
    
    results.append({
        'phase': 344,
        'status': status,
        'duration': duration,
        'notes': str(result.get('details', ''))
    })
except Exception as e:
    print(f"ERROR: {str(e)}")
    results.append({
        'phase': 344,
        'status': 'ERROR',
        'duration': 0,
        'notes': str(e)
    })

# Print summary
print("\n" + "="*60)
print("EXECUTION SUMMARY")
print("="*60)
print("\nPhase Results:")
for r in results:
    print(f"  Phase {r['phase']}: {r['status']} ({r['duration']}s)")

# CSV stats
print("\n" + "="*60)
print("DATA STATISTICS")
print("="*60)

csv_files = {
    'angel_index_ai_signals.csv': 'storage/live/angel_index_ai_signals.csv',
    'angel_index_ai_signals_curated.csv': 'storage/live/angel_index_ai_signals_curated.csv',
    'angel_index_ai_signals_with_forward.csv': 'storage/live/angel_index_ai_signals_with_forward.csv',
    'angel_virtual_orders.csv': 'storage/live/angel_virtual_orders.csv',
    'angel_index_ai_pnl_log.csv': 'storage/live/angel_index_ai_pnl_log.csv',
}

for name, path in csv_files.items():
    rows, first_ts, last_ts = get_csv_stats(path)
    age = get_file_age_minutes(path)
    
    if rows is not None:
        print(f"\n{name}:")
        print(f"  Rows: {rows}")
        print(f"  Age: {age} minutes")
        print(f"  First TS: {first_ts}")
        print(f"  Last TS: {last_ts}")
    else:
        print(f"\n{name}: NOT FOUND")

print("\n" + "="*60)
print("END OF EXECUTION REPORT")
print("="*60)
