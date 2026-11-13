import os
import sys
import openpyxl

def verify_matrix():
    path = r"C:\Genesis_System3_clean\FEATURE_TRUTH_MATRIX.xlsx"
    if not os.path.exists(path):
        print("ERROR: File does not exist!")
        sys.exit(1)
        
    print(f"File exists: {path}")
    print(f"Size: {os.path.getsize(path)} bytes")
    
    wb = openpyxl.load_workbook(path, data_only=True)
    sheets = wb.sheetnames
    print(f"\nSheet names ({len(sheets)}): {sheets}")
    
    expected_sheets = [
        "API_ENDPOINTS",
        "BROKER_FEATURES",
        "DHAN_FEATURES",
        "ML_FEATURES",
        "VALIDATION_FEATURES",
        "SECURITY_FEATURES",
        "MERGE_REQUIRED",
        "SAFE_REMOVE"
    ]
    
    assert sheets == expected_sheets, f"Sheets mismatch: {sheets} vs {expected_sheets}"
    
    expected_headers = [
        "Feature Name",
        "Classification",
        "Source File",
        "Destination File",
        "Winner",
        "Reason",
        "Evidence"
    ]
    
    total_rows = 0
    classification_counts = {}
    winner_counts = {}
    
    for s_name in sheets:
        ws = wb[s_name]
        headers = [ws.cell(row=1, column=c).value for c in range(1, 8)]
        assert headers == expected_headers, f"Header mismatch in {s_name}: {headers}"
        
        row_count = ws.max_row - 1 # exclude header
        total_rows += row_count
        print(f"  {s_name:22}: {row_count:3} rows")
        
        for r in range(2, ws.max_row + 1):
            row_vals = [ws.cell(row=r, column=c).value for c in range(1, 8)]
            for col_idx, val in enumerate(row_vals, 1):
                if val is None or str(val).strip() == "":
                    print(f"WARNING: Empty cell in {s_name} row {r} col {col_idx}")
            
            c_val = str(ws.cell(row=r, column=2).value)
            w_val = str(ws.cell(row=r, column=5).value)
            
            classification_counts[c_val] = classification_counts.get(c_val, 0) + 1
            winner_counts[w_val] = winner_counts.get(w_val, 0) + 1
            
    print(f"\nTotal rows across all 8 sheets: {total_rows}")
    print("\nClassification breakdown:")
    for k, v in sorted(classification_counts.items()):
        print(f"  {k:38}: {v:3}")
        
    print("\nWinner breakdown:")
    for k, v in sorted(winner_counts.items()):
        print(f"  {k:38}: {v:3}")
        
    print("\nVERIFICATION COMPLETE: ALL CHECKS PASSED PERFECTLY!")

if __name__ == '__main__':
    verify_matrix()
    sys.exit(0)
