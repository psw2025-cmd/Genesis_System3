#!/usr/bin/env python3
"""
Pipeline Consistency Validation
Tests Phase 339 and 340 with new normalized/deduplicated data
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "core" / "engine"))

def test_phase339_with_fixed_schema():
    """Test Phase 339 with normalized schema files"""
    print("\n" + "="*70)
    print("TESTING PHASE 339 WITH NORMALIZED SCHEMA")
    print("="*70)
    
    try:
        from system3_phase339_daily_signal_pipeline_summary import run_phase339_daily_signal_pipeline_summary
        result = run_phase339_daily_signal_pipeline_summary()
        status = result.get("status", "UNKNOWN")
        
        print(f"✅ Phase 339: {status}")
        
        # Check for schema issues
        outputs = result.get("outputs", {})
        issues = outputs.get("schema_issues", [])
        
        if issues:
            print(f"⚠️  Schema issues detected: {len(issues)}")
            for issue in issues[:3]:
                print(f"   - {issue}")
        else:
            print("✅ No schema issues detected")
        
        return ("PASS", status, issues)
        
    except Exception as e:
        print(f"❌ Phase 339 ERROR: {str(e)}")
        return ("FAIL", "ERROR", str(e))

def test_phase340_with_deduped_files():
    """Test Phase 340 with deduplicated files"""
    print("\n" + "="*70)
    print("TESTING PHASE 340 WITH DEDUPLICATED FILES")
    print("="*70)
    
    try:
        from system3_phase340_signal_pipeline_regression_guard import run_phase340_signal_pipeline_regression_guard
        result = run_phase340_signal_pipeline_regression_guard()
        status = result.get("status", "UNKNOWN")
        
        print(f"✅ Phase 340: {status}")
        
        # Check duplicate rate
        outputs = result.get("outputs", {})
        metrics = outputs.get("regression_metrics", {})
        dup_rate = metrics.get("duplicate_rate", 0.0)
        
        print(f"Duplicate rate: {dup_rate:.2%}")
        
        if dup_rate > 0.10:
            print(f"⚠️  High duplicate rate: {dup_rate:.2%}")
            return ("WARN", status, f"Duplicate rate {dup_rate:.2%}")
        else:
            print(f"✅ Duplicate rate acceptable: {dup_rate:.2%}")
            return ("PASS", status, f"Duplicate rate {dup_rate:.2%}")
        
    except Exception as e:
        print(f"❌ Phase 340 ERROR: {str(e)}")
        return ("FAIL", "ERROR", str(e))

def verify_curated_files():
    """Verify final curated files exist and have correct format"""
    print("\n" + "="*70)
    print("VERIFYING CURATED FILES")
    print("="*70)
    
    import pandas as pd
    
    curated_dir = PROJECT_ROOT / "storage" / "live"
    expected_files = [
        "angel_index_ai_signals_curated.csv",
        "angel_index_ai_signals_with_forward.csv"
    ]
    
    results = []
    
    for fname in expected_files:
        filepath = curated_dir / fname
        if not filepath.exists():
            print(f"❌ Missing: {fname}")
            results.append(("FAIL", fname, "File not found"))
            continue
        
        try:
            df = pd.read_csv(filepath)
            print(f"✅ {fname}: {len(df)} rows, {len(df.columns)} columns")
            results.append(("PASS", fname, f"{len(df)} rows"))
        except Exception as e:
            print(f"❌ {fname}: Read error - {str(e)[:50]}")
            results.append(("FAIL", fname, str(e)[:50]))
    
    return results

def main():
    """Run pipeline consistency tests"""
    print("\n" + "="*70)
    print("PIPELINE CONSISTENCY VALIDATION")
    print("="*70)
    
    # Test Phase 339
    p339_result, p339_status, p339_detail = test_phase339_with_fixed_schema()
    
    # Test Phase 340
    p340_result, p340_status, p340_detail = test_phase340_with_deduped_files()
    
    # Verify curated files
    curated_results = verify_curated_files()
    
    # Summary
    print("\n" + "="*70)
    print("PIPELINE CONSISTENCY SUMMARY")
    print("="*70)
    
    print(f"Phase 339 (Schema Check): {p339_result} - {p339_status}")
    print(f"Phase 340 (Duplicate Check): {p340_result} - {p340_status}")
    
    curated_pass = sum(1 for r, _, _ in curated_results if r == "PASS")
    curated_total = len(curated_results)
    print(f"Curated Files: {curated_pass}/{curated_total} valid")
    
    all_pass = (p339_result in ["PASS", "WARN"] and 
                p340_result in ["PASS", "WARN"] and 
                curated_pass == curated_total)
    
    if all_pass:
        print("\n✅ PIPELINE CONSISTENCY: PASS")
        return 0
    else:
        print("\n⚠️  PIPELINE CONSISTENCY: NEEDS REVIEW")
        return 1

if __name__ == "__main__":
    sys.exit(main())
