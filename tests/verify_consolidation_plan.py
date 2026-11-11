import openpyxl
import json
import sys
import os

def verify():
    filename = "FINAL_CONSOLIDATION_PLAN.xlsx"
    if not os.path.exists(filename):
        print(json.dumps({"verified": False, "error": f"{filename} does not exist"}))
        sys.exit(1)

    wb = openpyxl.load_workbook(filename, data_only=True)
    expected_sheets = [
        "P0_CRITICAL_MERGES",
        "P1_IMPORTANT_MERGES",
        "P2_OPTIONAL_MERGES",
        "SAFE_REMOVE_AFTER_MERGE"
    ]

    for s in expected_sheets:
        if s not in wb.sheetnames:
            print(json.dumps({"verified": False, "error": f"Missing sheet: {s}"}))
            sys.exit(1)

    # Required columns for merge sheets
    required_merge_cols = [
        "Priority",
        "Source File",
        "Source Function",
        "Destination File",
        "Destination Function",
        "Dependencies",
        "Risk",
        "Estimated Code Size",
        "Merge Order"
    ]

    merge_counts = {}
    for p_sheet, expected_p in [
        ("P0_CRITICAL_MERGES", "P0"),
        ("P1_IMPORTANT_MERGES", "P1"),
        ("P2_OPTIONAL_MERGES", "P2")
    ]:
        ws = wb[p_sheet]
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 5:
            print(json.dumps({"verified": False, "error": f"{p_sheet} has too few rows ({len(rows)})"}))
            sys.exit(1)

        # Header is at row 4
        headers = [str(h).strip() if h is not None else "" for h in rows[3]]
        for req in required_merge_cols:
            matching = [h for h in headers if req.lower() in h.lower()]
            if not matching:
                print(json.dumps({"verified": False, "error": f"Sheet {p_sheet} missing required column matching '{req}'. Found: {headers}"}))
                sys.exit(1)

        # Validate data rows (row index 4 onwards in 0-indexed list)
        data_rows = rows[4:]
        merge_counts[p_sheet] = len(data_rows)
        for r_idx, r in enumerate(data_rows, 5):
            row_dict = dict(zip(headers, r))
            # Find priority
            priority_val = None
            source_file_val = None
            dest_file_val = None
            for k, v in row_dict.items():
                if "priority" in k.lower():
                    priority_val = str(v).strip() if v else ""
                elif "source file" in k.lower():
                    source_file_val = str(v).strip() if v else ""
                elif "destination file" in k.lower():
                    dest_file_val = str(v).strip() if v else ""

            if priority_val != expected_p:
                print(json.dumps({"verified": False, "error": f"Row {r_idx} in {p_sheet} has priority '{priority_val}' expected '{expected_p}'"}))
                sys.exit(1)

            if not source_file_val or ":" not in source_file_val:
                print(json.dumps({"verified": False, "error": f"Row {r_idx} in {p_sheet} missing line number in source file: '{source_file_val}'"}))
                sys.exit(1)

            if not dest_file_val:
                print(json.dumps({"verified": False, "error": f"Row {r_idx} in {p_sheet} missing destination file"}))
                sys.exit(1)

    # Validate SAFE_REMOVE_AFTER_MERGE
    ws_safe = wb["SAFE_REMOVE_AFTER_MERGE"]
    safe_rows = list(ws_safe.iter_rows(values_only=True))
    if len(safe_rows) < 5:
        print(json.dumps({"verified": False, "error": f"SAFE_REMOVE_AFTER_MERGE has too few rows ({len(safe_rows)})"}))
        sys.exit(1)

    safe_headers = [str(h).strip() if h is not None else "" for h in safe_rows[3]]
    safe_data = safe_rows[4:]
    for r_idx, r in enumerate(safe_data, 5):
        if not r[1] or not r[3]: # Name and path
            print(json.dumps({"verified": False, "error": f"Row {r_idx} in SAFE_REMOVE_AFTER_MERGE missing name or path"}))
            sys.exit(1)

    total_merges = sum(merge_counts.values())
    result = {
        "verified": True,
        "filename": filename,
        "sheets": wb.sheetnames,
        "merge_counts": merge_counts,
        "total_merges": total_merges,
        "safe_remove_items": len(safe_data)
    }
    print(json.dumps(result, indent=2))
    return True

if __name__ == "__main__":
    verify()
