import csv
from pathlib import Path
import json

files_to_check = {
    "FORENSIC_UI_UX": "reports/latest/ui_recovery/FORENSIC_UI_UX_WORLD_CLASS_AUDIT.csv",
    "PENDING_ISSUES_MASTER": "reports/latest/pending_issues/PENDING_ISSUES_MASTER_20260825.csv",
    "MRI_TRUTH_120": "reports/latest/mri/GENESIS_SYSTEM3_MASTER_120_MRI_TRUTH.csv",
    "MRI_CHECKLIST": "reports/latest/mri_watch/CHECKLIST.csv",
    "COORDINATION_PENDING": "reports/coordination/pending_issues_master.csv",
    "COORDINATION_SESSION": "reports/coordination/session_issues_master.csv"
}

summary = {}
for name, fpath in files_to_check.items():
    p = Path(fpath)
    if not p.exists():
        continue
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        rows = list(reader)
    summary[name] = {
        "file": fpath,
        "total_rows": len(rows),
        "headers": headers,
        "rows": rows
    }

print("=== CSV INSPECTION SUMMARY ===")
for name, d in summary.items():
    print(f"\n{name} ({d['file']}) - {d['total_rows']} rows:")
    print("Headers:", d["headers"][:6])
    for r in d["rows"][:5]:
        print(" ", r[:5])

# Specifically print all items from PENDING_ISSUES_MASTER_20260825.csv
print("\n=== PENDING_ISSUES_MASTER DETAILS ===")
for r in summary.get("PENDING_ISSUES_MASTER", {}).get("rows", []):
    print(r)

# Specifically print all items from MRI_TRUTH_120 that are FAIL/PENDING/BLOCKED
print("\n=== MRI_TRUTH_120 FAIL/PENDING/BLOCKED DETAILS ===")
for r in summary.get("MRI_TRUTH_120", {}).get("rows", []):
    row_text = " ".join(r).upper()
    if any(k in row_text for k in ["FAIL", "PENDING", "BLOCKED"]):
        print(r)
