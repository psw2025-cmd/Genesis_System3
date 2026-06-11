"""
Signal Files Validation Report

Checks all three signal CSV files for schema completeness and data quality.
"""

import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"

FILES = {
    'signals': LIVE_DIR / "angel_index_ai_signals.csv",
    'curated': LIVE_DIR / "angel_index_ai_signals_curated.csv",
    'with_forward': LIVE_DIR / "angel_index_ai_signals_with_forward.csv",
}

REQUIRED_COLUMNS = {
    'core': ['underlying', 'strike', 'side', 'spot', 'ltp', 'symbol', 'ts'],
    'greeks': ['delta', 'gamma', 'theta', 'vega', 'moneyness'],
    'iv_metrics': ['iv', 'iv_estimate', 'iv_percentile', 'iv_rank', 'iv_change_rate', 'iv_spike'],
    'indicators': ['rsi', 'macd', 'macd_signal', 'macd_histogram', 'sma_5', 'sma_10', 'sma_20', 'vwap', 'supertrend'],
    'trend': ['trend_score', 'multi_tf_trend_score', 'trend_strength', 'trend_1m', 'trend_3m', 'trend_5m', 'trend_15m'],
    'momentum': ['momentum_score', 'breakout_score', 'roc_1', 'roc_3', 'roc_5', 'roc_10', 'acceleration'],
    'volatility': ['volatility_regime', 'volatility_score', 'regime_transition'],
    'ml': ['ml_prediction', 'ml_probability', 'ai_score'],
    'signals': ['signal', 'final_score', 'signal_strength', 'greeks_score'],
    'entry_exit': ['entry_buy', 'entry_sell', 'entry_hold', 'entry_confidence', 'stop_loss', 'target_price', 'risk_amount', 'entry_price'],
    'forward': ['fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5', 'reconciled_label'],
}

def check_file(file_path: Path, file_type: str) -> dict:
    """Check a single file for completeness."""
    if not file_path.exists():
        return {
            'exists': False,
            'error': f'File not found: {file_path}'
        }
    
    try:
        df = pd.read_csv(file_path)
        
        result = {
            'exists': True,
            'rows': len(df),
            'columns': len(df.columns),
            'missing_cells': df.isnull().sum().sum(),
            'missing_pct': (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100) if len(df) > 0 else 0,
            'schema_check': {},
        }
        
        # Check each category
        for category, required_cols in REQUIRED_COLUMNS.items():
            present = [c for c in required_cols if c in df.columns]
            missing = [c for c in required_cols if c not in df.columns]
            
            result['schema_check'][category] = {
                'required': len(required_cols),
                'present': len(present),
                'missing': missing,
                'complete': len(missing) == 0,
            }
        
        # Specific checks for forward returns file
        if file_type == 'with_forward':
            fwd_cols = ['fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5']
            fwd_populated = df[fwd_cols].notna().all(axis=1).sum()
            result['forward_returns_populated'] = fwd_populated
            result['forward_returns_pct'] = (fwd_populated / len(df) * 100) if len(df) > 0 else 0
        
        # Signal distribution
        if 'signal' in df.columns:
            result['signal_distribution'] = df['signal'].value_counts().to_dict()
        
        return result
        
    except Exception as e:
        return {
            'exists': True,
            'error': str(e)
        }


def print_report():
    """Generate and print validation report."""
    print("=" * 80)
    print("SIGNAL FILES VALIDATION REPORT")
    print("=" * 80)
    
    from datetime import datetime
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    for name, path in FILES.items():
        print(f"\n{'='*80}")
        print(f"FILE: {path.name}")
        print(f"{'='*80}")
        
        result = check_file(path, name)
        results[name] = result
        
        if not result['exists']:
            print(f"[ERROR] {result['error']}")
            continue
        
        if 'error' in result:
            print(f"[ERROR] {result['error']}")
            continue
        
        print(f"\n[BASIC STATS]")
        print(f"  Rows: {result['rows']}")
        print(f"  Columns: {result['columns']}")
        print(f"  Missing cells: {result['missing_cells']} ({result['missing_pct']:.1f}%)")
        
        print(f"\n[SCHEMA VALIDATION]")
        all_complete = True
        for category, check in result['schema_check'].items():
            status = "[OK]" if check['complete'] else "[INCOMPLETE]"
            print(f"  {status} {category}: {check['present']}/{check['required']} columns")
            if check['missing']:
                print(f"      Missing: {', '.join(check['missing'])}")
                all_complete = False
        
        if all_complete:
            print(f"\n  [OK] All required columns present!")
        else:
            print(f"\n  [WARNING] Some required columns missing")
        
        if 'signal_distribution' in result:
            print(f"\n[SIGNAL DISTRIBUTION]")
            for signal, count in result['signal_distribution'].items():
                print(f"  {signal}: {count}")
        
        if 'forward_returns_populated' in result:
            print(f"\n[FORWARD RETURNS]")
            print(f"  Populated rows: {result['forward_returns_populated']}/{result['rows']} ({result['forward_returns_pct']:.1f}%)")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    
    all_exist = all(r['exists'] for r in results.values())
    all_complete = all(
        all(c['complete'] for c in r.get('schema_check', {}).values())
        for r in results.values()
        if 'schema_check' in r
    )
    
    if all_exist and all_complete:
        print("\n[OK] All files exist and have complete schemas!")
        print("\n[COMPATIBILITY]")
        print("  - Phase 339 (signal freshness): READY")
        print("  - Phases 370-375 (data quality): READY")
        print("  - Phase 379 (edge cases): READY")
        print("\n[STATUS] Signal files are production-ready for paper trading.")
    else:
        print("\n[WARNING] Some files have issues - review details above")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print_report()
