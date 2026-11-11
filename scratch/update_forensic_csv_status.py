import csv
from pathlib import Path

csv_path = Path("reports/latest/ui_recovery/FORENSIC_UI_UX_WORLD_CLASS_AUDIT.csv")
with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f)
    headers = next(reader)
    rows = list(reader)

status_col = headers.index("Current_Status")

resolved_ids = {
    "F01", "F02", "F03", "F04", "F05", "F06", "F07", 
    "F08", "F09", "F10", "F11", "F12", "F17"
}

updated_rows = []
for r in rows:
    if len(r) > status_col:
        item_id = r[0]
        if item_id in resolved_ids:
            r[status_col] = "RESOLVED_LOCAL_VERIFIED"
        elif item_id in {"F13", "F14", "F15"}:
            r[status_col] = "PASS_VERIFIED"
        elif item_id == "F16":
            r[status_col] = "PENDING_OWNER_DEPLOY_CONSENT"
    updated_rows.append(r)

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(updated_rows)

print(f"Updated {len(updated_rows)} rows in {csv_path}")
for r in updated_rows:
    print(f"[{r[0]}] Status: {r[status_col]} | Title: {r[3][:60]}")
