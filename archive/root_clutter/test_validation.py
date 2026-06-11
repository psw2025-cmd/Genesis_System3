"""Quick test script to run validation and show results"""
import sys
sys.path.insert(0, '.')

from core.validation.option_chain_validator import OptionChainValidator
import pandas as pd

print("="*80)
print("OPTION CHAIN VALIDATION TEST")
print("="*80)

csv_path = "storage/live/option_chain_NIFTY_NFO.csv"

# Step 1: Analyze current data
print("\n1. ANALYZING CURRENT DATA...")
df = pd.read_csv(csv_path)
print(f"   Total rows: {len(df)}")

critical_cols = ['ltp', 'oi', 'bidPrice', 'offerPrice', 'delta']
print("\n   Missing data analysis:")
for col in critical_cols:
    if col in df.columns:
        missing = df[col].isna().sum()
        pct = missing / len(df) * 100
        status = "❌ FAIL" if pct > 10 else "✅ PASS"
        print(f"   {col:12} {missing:3} missing ({pct:5.1f}%) {status}")
    else:
        print(f"   {col:12} COLUMN MISSING ❌")

# Step 2: Run validation
print("\n2. RUNNING VALIDATION...")
validator = OptionChainValidator()

try:
    result = validator.validate_and_correct(
        csv_path, 
        underlying="NIFTY",
        exchange="NFO"
    )
    
    print("\n3. VALIDATION RESULTS:")
    print(f"   Status: {result['final_status']}")
    print(f"   Failed checks: {len(result['validation']['failed_checks'])}")
    for check in result['validation']['failed_checks']:
        print(f"     - {check}")
    
    if result.get('correction'):
        print(f"\n4. CORRECTION STATS:")
        print(f"   LTP fixed: {result['correction'].get('ltp_fixed', 0)}")
        print(f"   OI fixed: {result['correction'].get('oi_fixed', 0)}")
        print(f"   Greeks fixed: {result['correction'].get('greeks_fixed', 0)}")
        print(f"   Attempts: {result['correction'].get('attempts', 0)}")
    
    print(f"\n5. OUTPUT FILE: {result.get('output_file', 'N/A')}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
