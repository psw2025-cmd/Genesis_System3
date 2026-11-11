import os
import sys
import json
import openpyxl

def verify_matrix():
    matrix_path = os.path.abspath("FEATURE_TRUTH_MATRIX.xlsx")
    if not os.path.isfile(matrix_path):
        print(f"FAIL: File not found at {matrix_path}")
        sys.exit(1)

    wb = openpyxl.load_workbook(matrix_path, data_only=True)
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

    actual_sheets = wb.sheetnames
    if actual_sheets != expected_sheets:
        print(f"FAIL: Sheets mismatch: {actual_sheets} != {expected_sheets}")
        sys.exit(1)

    expected_headers = [
        "Feature Name",
        "Classification",
        "Source File",
        "Destination File",
        "Winner",
        "Reason",
        "Evidence"
    ]

    allowed_classifications = {
        "Present in dashboard only",
        "Present in content only",
        "Present in both",
        "Better implementation in dashboard",
        "Better implementation in content",
        "Merge required",
        "Safe removal"
    }

    total_rows = 0
    sheet_row_counts = {}

    for s_name in expected_sheets:
        ws = wb[s_name]
        headers = [ws.cell(row=1, column=c).value for c in range(1, 8)]
        if headers != expected_headers:
            print(f"FAIL: Headers mismatch in {s_name}: {headers} != {expected_headers}")
            sys.exit(1)

        row_count = ws.max_row - 1
        if row_count < 5:
            print(f"FAIL: Insufficient rows in {s_name}: {row_count}")
            sys.exit(1)

        sheet_row_counts[s_name] = row_count
        total_rows += row_count

        for r in range(2, ws.max_row + 1):
            row_vals = [ws.cell(row=r, column=c).value for c in range(1, 8)]
            for col_idx, val in enumerate(row_vals, 1):
                if val is None or str(val).strip() == "":
                    print(f"FAIL: Empty cell in {s_name} row {r} col {col_idx}")
                    sys.exit(1)

            classification = str(ws.cell(row=r, column=2).value).strip()
            if classification not in allowed_classifications:
                print(f"FAIL: Invalid classification '{classification}' in {s_name} row {r}")
                sys.exit(1)

    result = {
        "verified": True,
        "sheets_count": len(actual_sheets),
        "total_rows": total_rows,
        "sheet_row_counts": sheet_row_counts
    }
    print(json.dumps(result))
    sys.exit(0)

if __name__ == '__main__':
    verify_matrix()
