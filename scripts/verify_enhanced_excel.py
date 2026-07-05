"""Quick verification of enhanced Excel file"""

from pathlib import Path

import pandas as pd

excel_path = Path("outputs/OptionChain_Master_v3_AI_FINAL.xlsx")

xl = pd.ExcelFile(excel_path)
print("=" * 80)
print("ENHANCED EXCEL FILE VERIFICATION")
print("=" * 80)
print(f"\nTotal Sheets: {len(xl.sheet_names)}")
print(f"\nSheet Names:")
for i, sheet in enumerate(xl.sheet_names, 1):
    try:
        df = pd.read_excel(xl, sheet_name=sheet, nrows=5)
        full_df = pd.read_excel(xl, sheet_name=sheet)
        print(f"  {i:2d}. {sheet:30s} - {len(full_df):5d} rows, {len(df.columns):2d} columns")
    except:
        print(f"  {i:2d}. {sheet:30s} - ERROR reading")

# Check for new sheets
new_sheets = ["ML_PREDICTIONS", "TOP_OPPORTUNITIES", "TRADE_SIGNALS", "PAPER_TRADES", "OPEN_POSITIONS", "PNL_SUMMARY"]
print(f"\nNew Enhancement Sheets:")
for sheet in new_sheets:
    if sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        print(f"  ✓ {sheet:30s} - {len(df):5d} rows")
        if len(df) > 0:
            print(f"    Columns: {', '.join(list(df.columns)[:5])}...")
    else:
        print(f"  ✗ {sheet:30s} - NOT FOUND")

print("\n" + "=" * 80)
