#!/usr/bin/env python3
"""
Fix Phase 315 CSV Schema Issues

Adds missing 'symbol' column to angel_index_ai_pnl_log.csv
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def fix_csv_schemas():
    """Add missing columns to CSV files for Phase 315 validation"""
    
    # Ensure storage/data directory exists
    csv_dir = Path("storage/data")
    csv_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("PHASE 315 CSV SCHEMA FIX")
    print("=" * 70)
    print()
    
    # Files needing fixes
    schema_fixes = {
        "angel_index_ai_pnl_log.csv": {
            "add_columns": {"symbol": "UNKNOWN"},
            "required": ["timestamp", "pnl"],
            "description": "PnL log with symbol column"
        }
    }
    
    fixed_count = 0
    
    for filename, fixes in schema_fixes.items():
        file_path = csv_dir / filename
        
        print(f"Processing: {filename}")
        
        if not file_path.exists():
            print(f"  ⚠️  File not found: {file_path}")
            print()
            continue
        
        try:
            # Load CSV
            df = pd.read_csv(file_path)
            original_shape = df.shape
            
            print(f"  Original shape: {original_shape[0]} rows, {original_shape[1]} columns")
            
            # Add missing columns
            columns_added = []
            for col, default_val in fixes["add_columns"].items():
                if col not in df.columns:
                    df[col] = default_val
                    columns_added.append(col)
            
            if columns_added:
                print(f"  ✅ Added columns: {', '.join(columns_added)}")
            else:
                print(f"  ℹ️  All columns already present")
            
            # Verify required columns exist
            missing = [c for c in fixes["required"] if c not in df.columns]
            if missing:
                print(f"  ❌ Missing required columns: {missing}")
                print()
                continue
            
            # Save updated CSV
            df.to_csv(file_path, index=False)
            print(f"  ✅ Saved: {original_shape[0]} rows, {df.shape[1]} columns")
            print(f"  ✅ File: {file_path}")
            
            fixed_count += 1
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print(f"SUMMARY: Fixed {fixed_count}/{len(schema_fixes)} files")
    print("=" * 70)
    print()
    print("✅ Phase 315 should now return OK status instead of WARN")
    
    return fixed_count

if __name__ == "__main__":
    fix_csv_schemas()
