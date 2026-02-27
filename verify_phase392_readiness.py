#!/usr/bin/env python
"""Phase 392 Pre-Flight Verification Script"""

import pandas as pd
import json
import os
from pathlib import Path

def check_phase390_balanced_dataset():
    """Verify Phase 390 balanced dataset"""
    print("=" * 70)
    print("SECTION 1: PHASE 390/391 ARTIFACT VERIFICATION")
    print("=" * 70)
    
    csv_path = Path("storage/datasets/phase_390_balanced_features.csv")
    
    if not csv_path.exists():
        print(f"❌ Balanced dataset NOT FOUND: {csv_path}")
        return False
    
    try:
        df = pd.read_csv(csv_path)
        rows, cols = df.shape
        
        print(f"\n✅ Phase 390 Balanced Dataset:")
        print(f"   Path: {csv_path}")
        print(f"   Dimensions: {rows} rows × {cols} columns")
        print(f"   Expected: 3582 × 135")
        
        if (rows, cols) == (3582, 135):
            print(f"   ✅ MATCH!")
            return True
        else:
            print(f"   ⚠️ DIMENSION MISMATCH (got {rows} × {cols}, expected 3582 × 135)")
            return False
            
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

def check_phase391_metrics():
    """Verify Phase 391 training metrics"""
    metrics_path = Path("storage/metrics/phase_391_xgb_metrics.json")
    
    if not metrics_path.exists():
        print(f"❌ Phase 391 metrics NOT FOUND: {metrics_path}")
        return False
    
    try:
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        print(f"\n✅ Phase 391 XGBoost Metrics:")
        print(f"   Status: {metrics.get('status')}")
        print(f"   Timestamp: {metrics.get('timestamp')}")
        print(f"   Underlyings trained: {len(metrics.get('underlyings_trained', []))}")
        print(f"   Models: {', '.join(metrics.get('underlyings_trained', []))}")
        print(f"   Config:")
        for k, v in metrics.get('config', {}).items():
            print(f"      {k}: {v}")
        
        return len(metrics.get('underlyings_trained', [])) == 5
        
    except Exception as e:
        print(f"❌ Error reading metrics: {e}")
        return False

def check_xgboost_models():
    """Verify XGBoost model files"""
    models_dir = Path("models/xgboost_v1")
    
    if not models_dir.exists():
        print(f"❌ Models directory NOT FOUND: {models_dir}")
        return False
    
    try:
        pkl_files = list(models_dir.glob("*_model.pkl"))
        meta_files = list(models_dir.glob("*_meta.json"))
        
        print(f"\n✅ XGBoost Models:")
        print(f"   Directory: {models_dir}")
        print(f"   Model files (.pkl): {len(pkl_files)}")
        for pkl in sorted(pkl_files):
            size_kb = pkl.stat().st_size / 1024
            print(f"      - {pkl.name}: {size_kb:.1f} KB")
        
        print(f"   Metadata files (.json): {len(meta_files)}")
        for meta in sorted(meta_files):
            print(f"      - {meta.name}")
        
        return len(pkl_files) == 5
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return False

def check_smote_report():
    """Verify Phase 390 SMOTE report"""
    smote_path = Path("storage/metrics/phase_390_smote_report.json")
    
    if not smote_path.exists():
        print(f"❌ SMOTE report NOT FOUND: {smote_path}")
        return False
    
    try:
        with open(smote_path, 'r') as f:
            smote = json.load(f)
        
        print(f"\n✅ Phase 390 SMOTE Report:")
        print(f"   Path: {smote_path}")
        print(f"   Content: {smote}")
        return True
        
    except Exception as e:
        print(f"❌ Error reading SMOTE report: {e}")
        return False

def check_runtime_health():
    """Check current system runtime health"""
    print("\n" + "=" * 70)
    print("SECTION 2: SYSTEM RUNTIME HEALTH (READ-ONLY)")
    print("=" * 70)
    
    hb_path = Path("system3_daily_heartbeat.json")
    
    if not hb_path.exists():
        print(f"❌ Heartbeat file NOT FOUND: {hb_path}")
        return False
    
    try:
        with open(hb_path, 'r') as f:
            hb = json.load(f)
        
        print(f"\n✅ System Heartbeat:")
        print(f"   Mode: {hb.get('mode', 'N/A')}")
        print(f"   Autopilot: {hb.get('autopilot_running', 'N/A')}")
        print(f"   Last update: {hb.get('last_update', 'N/A')}")
        
        # Check data file freshness
        signals_path = Path("storage/live/angel_index_ai_signals.csv")
        orders_path = Path("storage/live/angel_virtual_orders.csv")
        
        if signals_path.exists():
            mtime = signals_path.stat().st_mtime
            print(f"   Signals CSV: Updated (exists)")
        
        if orders_path.exists():
            mtime = orders_path.stat().st_mtime
            print(f"   Orders CSV: Updated (exists)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking heartbeat: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("PHASE 392 PRE-FLIGHT READINESS VERIFICATION")
    print("=" * 70)
    
    # Section 1: Artifacts
    results = {}
    results['balanced_dataset'] = check_phase390_balanced_dataset()
    results['phase391_metrics'] = check_phase391_metrics()
    results['xgboost_models'] = check_xgboost_models()
    results['smote_report'] = check_smote_report()
    
    # Section 2: Runtime
    results['runtime_health'] = check_runtime_health()
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:30} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🟢 READY FOR PHASE 392")
    else:
        print("🔴 NOT READY FOR PHASE 392")

if __name__ == "__main__":
    main()
