import csv
import os
import glob
from pathlib import Path

csv_paths = [
    "reports/latest/ui_recovery/FORENSIC_UI_UX_WORLD_CLASS_AUDIT.csv",
    "reports/latest/pending_issues/PENDING_ISSUES_MASTER_20260825.csv",
    "reports/latest/mri/GENESIS_SYSTEM3_MASTER_120_MRI_TRUTH.csv",
    "reports/latest/mri_watch/CHECKLIST.csv",
    "reports/latest/dhan_advance_platform_verification/claim_verification_matrix.csv",
    "reports/coordination/pending_issues_master.csv",
    "reports/coordination/session_issues_master.csv",
    ".agents/state/INDEPENDENT_VERIFICATION.csv"
]

pending_keywords = ["PENDING", "PARTIAL", "FAIL", "BLOCKED", "UNKNOWN", "NOT_VERIFIED", "TODO", "NOT_READY"]

findings = []

for cp in csv_paths:
    p = Path(cp)
    if not p.exists():
        continue
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            for row_idx, row in enumerate(reader, 1):
                row_str = " ".join(row).upper()
                matched_kw = [kw for kw in pending_keywords if kw in row_str]
                if matched_kw:
                    findings.append({
                        "file": cp,
                        "row_num": row_idx,
                        "keywords": matched_kw,
                        "row_data": dict(zip(headers[:len(row)], row)) if headers else row
                    })
    except Exception as e:
        print(f"Error reading {cp}: {e}")

print(f"Total pending/partial/blocked items found across recent CSVs: {len(findings)}")

# Group by file
by_file = {}
for f in findings:
    by_file.setdefault(f["file"], []).append(f)

for fpath, items in by_file.items():
    print(f"\n=== {fpath} ({len(items)} items) ===")
    for item in items[:10]:
        # Print summary
        data = item["row_data"]
        item_id = data.get("Item_ID") or data.get("ID") or data.get("item_id") or data.get("Check_ID") or f"Row {item['row_num']}"
        title = data.get("Finding_Title") or data.get("Title") or data.get("Description") or data.get("name") or str(list(data.values())[:3])
        status = data.get("Current_Status") or data.get("Status") or data.get("status") or item["keywords"]
        print(f"  [{item_id}] Status: {status} | Title: {str(title)[:80]}")
    if len(items) > 10:
        print(f"  ... and {len(items) - 10} more items")
