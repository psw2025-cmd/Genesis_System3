"""
System3 Pipeline Orchestrator - Phase 220 → 221 → 225 → 239

Runs the complete forward return and PnL enrichment pipeline in order.
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all phases
from core.engine.system3_phase220_historical_aggregation import run_phase220
from core.engine.system3_phase221_forward_returns import run_phase221
from system3_virtual_trades_enrichment import run_phase239


def run_full_pipeline():
    """Run the complete System3 forward return pipeline."""
    print("=" * 80)
    print("SYSTEM3 FULL PIPELINE EXECUTION")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {}
    
    # Phase 220: Historical Signal Aggregation
    print("\n" + "=" * 80)
    print("PHASE 220: Historical Curated Signals Aggregation")
    print("=" * 80)
    result_220 = run_phase220(days_back=14)
    results[220] = result_220
    print(f"\nPhase 220: {result_220['status']} - {result_220['details']}")
    
    if result_220['status'] == 'ERROR':
        print("\n❌ Phase 220 failed - stopping pipeline")
        return results
    
    if result_220.get('outputs', {}).get('unique_dates', 0) < 2:
        print("\n⚠️  WARNING: Only 1 unique date in aggregated signals")
        print("Forward returns require multiple timestamps - continuing anyway")
    
    # Phase 221: Forward Return Computation
    print("\n" + "=" * 80)
    print("PHASE 221: Forward Return Computation")
    print("=" * 80)
    result_221 = run_phase221()
    results[221] = result_221
    print(f"\nPhase 221: {result_221['status']} - {result_221['details']}")
    
    if result_221['status'] == 'ERROR':
        print("\n❌ Phase 221 failed - stopping pipeline")
        return results
    
    # Phase 239: Virtual Trades PnL Enrichment
    print("\n" + "=" * 80)
    print("PHASE 239: Virtual Trades PnL Enrichment")
    print("=" * 80)
    result_239 = run_phase239()
    results[239] = result_239
    print(f"\nPhase 239: {result_239['status']} - {result_239['details']}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    for phase, result in results.items():
        status_icon = "✅" if result['status'] == 'OK' else ("⚠️" if result['status'] == 'WARN' else "❌")
        print(f"{status_icon} Phase {phase}: {result['status']} - {result['details']}")
    
    # Detailed metrics
    print("\n" + "-" * 80)
    print("DETAILED METRICS")
    print("-" * 80)
    
    if 220 in results:
        r = results[220].get('outputs', {})
        print(f"\nPhase 220 (Historical Aggregation):")
        print(f"  - Total rows: {r.get('total_rows', 'N/A')}")
        print(f"  - Unique dates: {r.get('unique_dates', 'N/A')}")
        print(f"  - Date range: {r.get('date_range', {}).get('min', 'N/A')} → {r.get('date_range', {}).get('max', 'N/A')}")
    
    if 221 in results:
        r = results[221].get('outputs', {})
        print(f"\nPhase 221 (Forward Returns):")
        print(f"  - Total rows: {r.get('rows_processed', 'N/A')}")
        print(f"  - Rows with forward returns: {r.get('rows_with_forward_returns', 'N/A')}")
        fwd_coverage = r.get('forward_return_coverage', {})
        if fwd_coverage:
            print(f"  - Forward return coverage:")
            for horizon, count in sorted(fwd_coverage.items()):
                print(f"    • {horizon}: {count} rows")
    
    if 239 in results:
        r = results[239].get('outputs', {})
        print(f"\nPhase 239 (PnL Enrichment):")
        print(f"  - Total orders: {r.get('total_orders', 'N/A')}")
        print(f"  - Matched: {r.get('matched', 'N/A')}")
        print(f"  - Unmatched: {r.get('unmatched', 'N/A')}")
        print(f"  - Match rate: {r.get('match_rate_pct', 0):.1f}%")
        
        # Check if match rate meets target
        match_rate = r.get('match_rate_pct', 0)
        if match_rate >= 85:
            print(f"  ✅ Match rate exceeds 85% target")
        elif match_rate >= 50:
            print(f"  ⚠️  Match rate below 85% target")
        else:
            print(f"  ❌ Match rate critically low")
    
    print("\n" + "=" * 80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    results = run_full_pipeline()
    
    # Exit with appropriate code
    if all(r['status'] in ['OK', 'WARN'] for r in results.values()):
        sys.exit(0)
    else:
        sys.exit(1)
