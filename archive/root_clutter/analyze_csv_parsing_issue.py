"""
CSV Parsing Issue Analysis - Detailed Investigation
Analyzes the "Expected 72 fields in line 32, saw 75" error
"""

import sys
import csv
from pathlib import Path

ROOT_DIR = Path(__file__).parent.absolute()
SIGNALS_CSV = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"

print("=" * 70)
print("CSV PARSING ISSUE - DETAILED ANALYSIS")
print("=" * 70)
print()

if not SIGNALS_CSV.exists():
    print(f"ERROR: Signals CSV not found: {SIGNALS_CSV}")
    sys.exit(1)

# Read header
with open(SIGNALS_CSV, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    print(f"Header fields: {len(header)}")
    print(f"Header: {', '.join(header[:10])}... (showing first 10)")
    print()

    # Read first few lines and analyze
    lines_data = []
    for i, row in enumerate(reader, start=2):  # Start at line 2 (after header)
        if i <= 35:  # Analyze first 35 lines
            lines_data.append({
                'line_num': i,
                'field_count': len(row),
                'fields': row
            })
        else:
            break

print("=" * 70)
print("FIELD COUNT ANALYSIS")
print("=" * 70)
print()

# Analyze field counts
field_counts = {}
for line_data in lines_data:
    count = line_data['field_count']
    if count not in field_counts:
        field_counts[count] = []
    field_counts[count].append(line_data['line_num'])

print("Field count distribution:")
for count in sorted(field_counts.keys()):
    lines = field_counts[count]
    print(f"  {count} fields: Lines {lines}")

print()

# Find problematic lines
expected_fields = len(header)
print(f"Expected fields (from header): {expected_fields}")
print()

problematic_lines = [ld for ld in lines_data if ld['field_count'] != expected_fields]
if problematic_lines:
    print("=" * 70)
    print("PROBLEMATIC LINES (field count mismatch)")
    print("=" * 70)
    print()
    
    for line_data in problematic_lines:
        print(f"Line {line_data['line_num']}:")
        print(f"  Expected: {expected_fields} fields")
        print(f"  Actual: {line_data['field_count']} fields")
        print(f"  Difference: {line_data['field_count'] - expected_fields} extra fields")
        print()
        
        # Compare with a good line
        good_line = next((ld for ld in lines_data if ld['field_count'] == expected_fields), None)
        if good_line:
            print(f"  Comparing with Line {good_line['line_num']} (correct):")
            print(f"  Good line fields (first 15): {good_line['fields'][:15]}")
            print(f"  Bad line fields (first 15): {line_data['fields'][:15]}")
            print()
            
            # Find where the difference starts
            min_len = min(len(good_line['fields']), len(line_data['fields']))
            diff_positions = []
            for i in range(min_len):
                if good_line['fields'][i] != line_data['fields'][i]:
                    diff_positions.append(i)
                    if len(diff_positions) <= 5:  # Show first 5 differences
                        print(f"    Position {i}: Good='{good_line['fields'][i]}' vs Bad='{line_data['fields'][i]}'")
            
            if len(line_data['fields']) > len(good_line['fields']):
                print(f"    Extra fields in bad line (positions {len(good_line['fields'])}-{len(line_data['fields'])-1}):")
                for i in range(len(good_line['fields']), len(line_data['fields'])):
                    print(f"      Position {i}: '{line_data['fields'][i]}'")
        
        print()

# Analyze specific line 32
line_32 = next((ld for ld in lines_data if ld['line_num'] == 32), None)
if line_32:
    print("=" * 70)
    print("LINE 32 DETAILED ANALYSIS")
    print("=" * 70)
    print()
    print(f"Field count: {line_32['field_count']}")
    print(f"Expected: {expected_fields}")
    print(f"Difference: {line_32['field_count'] - expected_fields} extra fields")
    print()
    print("All fields in Line 32:")
    for i, field in enumerate(line_32['fields']):
        print(f"  [{i:2d}] {field}")
    print()

# Check for CSV writing issues
print("=" * 70)
print("ROOT CAUSE ANALYSIS")
print("=" * 70)
print()

# Check where signals are written
print("Checking signal writing code...")
print("  File: core/engine/system3_signal_engine.py")
print("  Function: append_signals_to_csv()")
print()

# Check if there are multiple versions of the CSV format
print("Possible causes:")
print("  1. CSV file was written with different column counts at different times")
print("  2. Signal generation code changed column structure")
print("  3. CSV file was manually edited or corrupted")
print("  4. Multiple processes writing to same file simultaneously")
print()

print("=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print()
print("The CSV parsing error occurs because:")
print(f"  - Header defines {expected_fields} columns")
print(f"  - Line 32 has {line_32['field_count'] if line_32 else 'unknown'} columns")
print(f"  - Difference: {line_32['field_count'] - expected_fields if line_32 else 'unknown'} extra fields")
print()
print("This is handled gracefully by:")
print("  - system3_signal_engine.py: Uses 'on_bad_lines=\"skip\"' (line 77)")
print("  - Most phases: Use 'engine=\"python\", on_bad_lines=\"skip\"'")
print()
print("However, some files don't handle this:")
print("  - angel_pnl_simulator.py: Uses pd.read_csv() without error handling (line 43)")
print("  - angel_trade_decision.py: Uses pd.read_csv() without error handling (line 242)")
print("  - angel_real_data_extractor.py: Uses pd.read_csv() without error handling (line 42)")
print()
print("FIX REQUIRED: Add error handling to these files")
print()

