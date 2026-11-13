"""
Verification suite for CLOUD_GITHUB_TRUTH.xlsx.
Validates:
1. File existence and workbook structure
2. Exactly 5 required sheets:
   - DEPLOYMENT_CHAIN
   - GITHUB_FILE_HASHES
   - CLOUD_FILE_HASHES
   - HASH_COMPARISON
   - DRIFT_REPORT
3. All 7 required columns present on every sheet:
   - File
   - GitHub SHA256
   - Cloud SHA256
   - Match YES/NO
   - GitHub Commit
   - Cloud Revision
   - Evidence
4. All 6 verification points covered in DEPLOYMENT_CHAIN
5. All 4 target files present in GITHUB_FILE_HASHES, CLOUD_FILE_HASHES, HASH_COMPARISON, and DRIFT_REPORT
6. UNVERIFIED markings present where evidence cannot directly prove container in-situ filesystem bytes
"""

import os
import sys
import json
import openpyxl

TARGET_FILES = [
    "core/brokers/dhan/dhan_readonly.py",
    "dashboard/backend/routers/broker.py",
    "dashboard/backend/broker/dhan_auth.py",
    "dashboard/backend/gain_rank_spot_enrichment.py"
]

REQUIRED_SHEETS = [
    "DEPLOYMENT_CHAIN",
    "GITHUB_FILE_HASHES",
    "CLOUD_FILE_HASHES",
    "HASH_COMPARISON",
    "DRIFT_REPORT"
]

REQUIRED_COLUMNS = [
    "File",
    "GitHub SHA256",
    "Cloud SHA256",
    "Match YES/NO",
    "GitHub Commit",
    "Cloud Revision",
    "Evidence"
]

DEPLOYMENT_POINTS = [
    "GitHub Commit SHA",
    "GitHub Branch",
    "Dockerfile used by build",
    "Cloud Build source revision",
    "Cloud Run revision",
    "Cloud Run image digest"
]

def verify_cloud_github_truth(file_path: str = "CLOUD_GITHUB_TRUTH.xlsx") -> dict:
    if not os.path.exists(file_path):
        return {"verified": False, "error": f"File not found: {file_path}"}

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet_names = wb.sheetnames

    # Check sheet names
    for rs in REQUIRED_SHEETS:
        if rs not in sheet_names:
            return {"verified": False, "error": f"Missing required sheet: {rs}"}

    # Verify each sheet structure
    sheet_stats = {}
    for s_name in REQUIRED_SHEETS:
        ws = wb[s_name]
        headers = [cell.value for cell in ws[1] if cell.value is not None]
        if headers != REQUIRED_COLUMNS:
            return {
                "verified": False,
                "error": f"Headers in sheet {s_name} do not match required columns. Got: {headers}, Expected: {REQUIRED_COLUMNS}"
            }

        rows = list(ws.iter_rows(min_row=2, values_only=True))
        if len(rows) == 0:
            return {"verified": False, "error": f"Sheet {s_name} has no data rows"}
        sheet_stats[s_name] = len(rows)

    # Check DEPLOYMENT_CHAIN verification points
    ws_chain = wb["DEPLOYMENT_CHAIN"]
    chain_files = [row[0] for row in ws_chain.iter_rows(min_row=2, values_only=True) if row[0]]
    for pt in DEPLOYMENT_POINTS:
        if not any(pt.lower() in str(cf).lower() for cf in chain_files):
            return {"verified": False, "error": f"Missing deployment verification point: {pt}"}

    # Check target files presence in sheets
    for s_name in ["GITHUB_FILE_HASHES", "CLOUD_FILE_HASHES", "HASH_COMPARISON", "DRIFT_REPORT"]:
        ws = wb[s_name]
        files_in_sheet = [str(row[0]) for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]
        for tf in TARGET_FILES:
            if not any(tf in fs for fs in files_in_sheet):
                return {"verified": False, "error": f"Target file {tf} missing from sheet {s_name}"}

    # Check UNVERIFIED presence in CLOUD_FILE_HASHES or HASH_COMPARISON
    ws_cloud = wb["CLOUD_FILE_HASHES"]
    cloud_statuses = [str(row[3]) for row in ws_cloud.iter_rows(min_row=2, values_only=True)]
    cloud_hashes = [str(row[2]) for row in ws_cloud.iter_rows(min_row=2, values_only=True)]
    if not any("UNVERIFIED" in st for st in cloud_statuses) or not any("UNVERIFIED" in h for h in cloud_hashes):
        return {"verified": False, "error": "UNVERIFIED marking missing from CLOUD_FILE_HASHES"}

    return {
        "verified": True,
        "file_path": file_path,
        "sheets_verified": REQUIRED_SHEETS,
        "sheet_stats": sheet_stats,
        "target_files_count": len(TARGET_FILES),
        "deployment_points_verified": DEPLOYMENT_POINTS
    }

if __name__ == "__main__":
    result = verify_cloud_github_truth()
    print(json.dumps(result, indent=2))
    if not result.get("verified"):
        sys.exit(1)
    sys.exit(0)
