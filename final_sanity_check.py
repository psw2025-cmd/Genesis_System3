#!/usr/bin/env python3
"""
Final Sanity Check for System3 Repository
Checks:
1. All CSV readers use safe loading
2. No new CSV parsing errors after 2025-12-03 21:35
3. CSV files load with 72 columns and non-zero final_score values
"""

import os
import re
import glob
import pandas as pd
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("SYSTEM3 FINAL SANITY CHECK")
print("=" * 80)
print()

# Check 1: CSV Readers
print("CHECK 1: CSV Readers in core/engine and core/phases")
print("-" * 80)

issues = []
safe_pattern = re.compile(r'engine\s*=\s*["\']python["\'].*on_bad_lines\s*=\s*["\']skip["\']', re.IGNORECASE)
unsafe_pattern = re.compile(r'pd\.read_csv\s*\([^)]+\)', re.IGNORECASE)

checked_files = set()
unsafe_reads = []

for root_dir in ['core/engine', 'core/phases']:
    if not os.path.exists(root_dir):
        continue
    
    for file_path in glob.glob(f'{root_dir}/**/*.py', recursive=True):
        if file_path in checked_files:
            continue
        checked_files.add(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    if 'pd.read_csv' in line:
                        # Check if it has safe loading
                        # Look at the full statement (may span multiple lines)
                        full_line = line
                        j = i
                        while j < len(lines) and ')' not in full_line:
                            j += 1
                            if j < len(lines):
                                full_line += ' ' + lines[j]
                        
                        if safe_pattern.search(full_line):
                            continue  # Safe
                        
                        # Check if there's a fallback try-except with safe loading
                        # Look ahead a few lines
                        has_fallback = False
                        for k in range(i, min(i + 10, len(lines))):
                            if 'except' in lines[k] and safe_pattern.search(' '.join(lines[k:k+5])):
                                has_fallback = True
                                break
                        
                        if not has_fallback:
                            unsafe_reads.append((file_path, i, line.strip()))
        except Exception as e:
            issues.append(f"Error reading {file_path}: {e}")

if unsafe_reads:
    print(f"❌ FOUND {len(unsafe_reads)} UNSAFE CSV READS:")
    for file_path, line_num, line in unsafe_reads[:10]:
        print(f"  {file_path}:{line_num} - {line[:80]}")
    if len(unsafe_reads) > 10:
        print(f"  ... and {len(unsafe_reads) - 10} more")
    check1_pass = False
else:
    print("✅ All CSV readers use safe loading (engine='python', on_bad_lines='skip') or have fallback")
    check1_pass = True

print()

# Check 2: Log Errors After 2025-12-03 21:35
print("CHECK 2: CSV Parsing Errors in Logs After 2025-12-03 21:35")
print("-" * 80)

cutoff_time = datetime(2025, 12, 3, 21, 35, 0)
error_pattern = re.compile(r'Error tokenizing data|Expected \d+ fields|saw \d+', re.IGNORECASE)

log_errors = []
log_files = glob.glob('logs/*.log') + glob.glob('logs/**/*.log', recursive=True)

for log_file in log_files:
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(log_file))
        if mtime <= cutoff_time:
            continue
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if error_pattern.search(content):
                # Extract timestamp from log if possible
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if error_pattern.search(line):
                        # Try to find timestamp in nearby lines
                        timestamp = None
                        for j in range(max(0, i-5), min(len(lines), i+1)):
                            ts_match = re.search(r'(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})', lines[j])
                            if ts_match:
                                try:
                                    ts_str = ts_match.group(1).replace('T', ' ')
                                    ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                                    if ts > cutoff_time:
                                        timestamp = ts_str
                                        break
                                except:
                                    pass
                        
                        if timestamp:
                            log_errors.append((log_file, timestamp, line.strip()[:100]))
                        else:
                            log_errors.append((log_file, "unknown", line.strip()[:100]))
    except Exception as e:
        pass

if log_errors:
    print(f"❌ FOUND {len(log_errors)} CSV PARSING ERRORS AFTER 21:35:")
    for log_file, timestamp, error_line in log_errors[:10]:
        print(f"  {log_file} ({timestamp}): {error_line}")
    if len(log_errors) > 10:
        print(f"  ... and {len(log_errors) - 10} more")
    check2_pass = False
else:
    print("✅ No CSV parsing errors found in logs after 2025-12-03 21:35")
    check2_pass = True

print()

# Check 3: CSV Files Load with 72 Columns and Non-Zero final_score
print("CHECK 3: CSV Files Load with 72 Columns and Non-Zero final_score")
print("-" * 80)

csv_files = [
    'storage/live/angel_index_ai_signals.csv',
    'storage/live/angel_index_ai_signals_curated.csv'
]

check3_pass = True

for csv_file in csv_files:
    if not os.path.exists(csv_file):
        print(f"⚠️  {csv_file} not found (skipping)")
        continue
    
    try:
        df = pd.read_csv(csv_file, engine="python", on_bad_lines="skip")
        
        # Check column count
        col_count = len(df.columns)
        if col_count != 72:
            print(f"❌ {csv_file}: Expected 72 columns, found {col_count}")
            check3_pass = False
            continue
        
        # Check for final_score column
        if 'final_score' not in df.columns:
            print(f"❌ {csv_file}: 'final_score' column not found")
            check3_pass = False
            continue
        
        # Check for non-zero final_score values
        non_zero_count = (df['final_score'] != 0).sum()
        total_count = len(df)
        
        if total_count == 0:
            print(f"⚠️  {csv_file}: File is empty (0 rows)")
            continue
        
        if non_zero_count == 0:
            print(f"❌ {csv_file}: All {total_count} rows have final_score = 0")
            check3_pass = False
        else:
            print(f"✅ {csv_file}: {col_count} columns, {total_count} rows, {non_zero_count} rows with non-zero final_score")
    except Exception as e:
        print(f"❌ {csv_file}: Failed to load - {e}")
        check3_pass = False

print()
print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)

all_pass = check1_pass and check2_pass and check3_pass

if all_pass:
    print("✅ ALL CHECKS PASSED - SYSTEM3 CORE IS STABLE")
    verdict = "✅ ALL CHECKS PASSED - SYSTEM3 CORE IS STABLE"
else:
    print("❌ SOME CHECKS FAILED")
    print(f"  Check 1 (CSV Readers): {'✅ PASS' if check1_pass else '❌ FAIL'}")
    print(f"  Check 2 (Log Errors): {'✅ PASS' if check2_pass else '❌ FAIL'}")
    print(f"  Check 3 (CSV Files): {'✅ PASS' if check3_pass else '❌ FAIL'}")
    verdict = "❌ SOME CHECKS FAILED - REVIEW REQUIRED"

print()
print(f"Verdict: {verdict}")

# Write verdict file
if all_pass:
    os.makedirs('docs', exist_ok=True)
    with open('docs/SYSTEM3_CORE_STABLE_CONFIRMED.md', 'w') as f:
        f.write(verdict + '\n')
    print("\n✅ Verdict written to docs/SYSTEM3_CORE_STABLE_CONFIRMED.md")

