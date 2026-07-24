import os
import json
from datetime import datetime

print("================================================================")
print("     SYSTEM3 MICRO-LEVEL X-Y-Z REPOSITORY AUDIT & FIXER         ")
print("================================================================")

audit_report = {
    "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    "workflow_fixes_applied": [],
    "blocker_analysis": []
}

# 1. Target Workflow Files to strictly enforce local endpoint & clean X, Y, Z factors
workflow_path = ".github/workflows/system3-autopilot-proof-board.yml"

if os.path.exists(workflow_path):
    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace render URL with localhost if present
    if "https://genesis-system3-backend.onrender.com" in content:
        content = content.replace("https://genesis-system3-backend.onrender.com", "http://127.0.0.1:8000")
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(content)
        audit_report["workflow_fixes_applied"].append(workflow_path)
        print(" [FIXED] Updated DASHBOARD_BASE_URL to localhost inside workflow file.")
    else:
        print(" [PASS] Workflow DASHBOARD_BASE_URL is already locally aligned.")

# 2. Inspect latest auto recovery & blocker reports for micro details
blocker_file = "reports/latest/auto_recovery_blockers/auto_recovery_blockers.json"
if os.path.exists(blocker_file):
    try:
        with open(blocker_file, "r", encoding="utf-8") as f:
            b_data = json.load(f)
            audit_report["blocker_analysis"] = b_data.get("categories", {})
            print(" [INFO] Successfully parsed active blocker categories.")
    except Exception as e:
        print(f" [WARN] Could not parse blocker JSON: {e}")

# Save comprehensive micro report
os.makedirs("reports/latest/micro_audit", exist_ok=True)
report_out = "reports/latest/micro_audit/summary.json"
with open(report_out, "w", encoding="utf-8") as f:
    json.dump(audit_report, f, indent=2)

print(f" [SUCCESS] Micro-level audit report written to {report_out}")
print("================================================================")