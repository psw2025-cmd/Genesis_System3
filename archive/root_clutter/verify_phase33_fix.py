"""
Quick verification script for Phase 33 fix
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_phase_33():
    """Test Phase 33: Ultra Promotion Planner"""
    print("\n" + "="*60)
    print("VERIFYING PHASE 33 FIX: Ultra Promotion Planner")
    print("="*60)
    try:
        from core.engine.system3_phase33_promotion_planner import run_phase33_promotion_planner
        result = run_phase33_promotion_planner()
        print(f"\n[PASS] Phase 33 completed: {result}")
        
        # Verify JSON output
        json_file = Path("storage/ultra/phase33_promotion_plan.json")
        if json_file.exists():
            import json
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[VERIFY] JSON file exists and is valid: {len(data)} underlyings")
            for underlying, plan in data.items():
                print(f"  {underlying}: eligible={plan.get('eligible')} (type: {type(plan.get('eligible')).__name__})")
        else:
            print(f"[FAIL] JSON file not found: {json_file}")
            return False
        
        # Verify MD output
        md_file = Path("storage/ultra/phase33_promotion_plan.md")
        if md_file.exists():
            print(f"[VERIFY] MD file exists: {md_file}")
        else:
            print(f"[FAIL] MD file not found: {md_file}")
            return False
        
        print("\n[SUCCESS] Phase 33 fix verified - JSON serialization working correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Phase 33 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase_33()
    sys.exit(0 if success else 1)

