import os
import json
import csv
import traceback
from pathlib import Path
import pandas as pd
import numpy as np
import datetime
 
ROOT = Path(__file__).resolve().parent
REPORT_FILE = ROOT / "SYSTEM3_FULL_DIAGNOSTIC_REPORT.json"
 
report = {
    "timestamp": str(datetime.datetime.now()),
    "root": str(ROOT),
    "structure": {},
    "logs_summary": {},
    "csv_validation": {},
    "pipeline_outputs": {},
    "critical_findings": [],
    "errors": []
}
 
# ---------------------------
# 1. DIRECTORY STRUCTURE SCAN
# ---------------------------
 
EXPECTED_DIRS = [
    "phases",
    "storage",
    "storage/live",
    "storage/live/meta",
    "storage/live/enriched",
    "storage/live/forward",
    "logs",
    "config",
    "models",
    "core"
]
 
for d in EXPECTED_DIRS:
    p = ROOT / d
    report["structure"][d] = p.exists()
 
# ---------------------------
# 2. LOG FILE ERROR SCANNER
# ---------------------------
 
log_dir = ROOT / "logs"
if log_dir.exists():
    for log_file in log_dir.glob("*.log"):
        errors = 0
        critical = 0
        try:
            with open(log_file, "r", errors="ignore") as f:
                for line in f:
                    if "ERROR" in line:
                        errors += 1
                    if "CRITICAL" in line:
                        critical += 1
        except:
            pass
 
        report["logs_summary"][log_file.name] = {
            "errors": errors,
            "critical": critical
        }
 
# ---------------------------
# 3. CSV STRUCTURE VALIDATION
# ---------------------------
 
def validate_csv(path):
    result = {"exists": True, "rows": 0, "columns": 0,
              "null_counts": {}, "dtype": {}, "head": []}
    try:
        df = pd.read_csv(path)
        result["rows"] = len(df)
        result["columns"] = len(df.columns)
        result["null_counts"] = df.isna().sum().to_dict()
        result["dtype"] = {col: str(df[col].dtype) for col in df.columns}
        result["head"] = df.head(5).to_dict(orient="records")
    except Exception as e:
        result["exists"] = False
        result["error"] = str(e)
    return result
 
 
CSV_TARGETS = {
    "phase220": ROOT / "storage/live/forward/phase220_aggregated_signals.csv",
    "phase221": ROOT / "storage/live/forward/phase221_forward_returns.csv",
    "phase239": ROOT / "storage/live/enriched/angel_virtual_orders_with_pnl.csv"
}
 
for name, path in CSV_TARGETS.items():
    if path.exists():
        report["csv_validation"][name] = validate_csv(path)
    else:
        report["csv_validation"][name] = {"exists": False}
 
# ---------------------------
# 4. MERGE-KEY CONSISTENCY CHECK
# ---------------------------
 
def normalize_timestamp(x):
    try:
        return pd.to_datetime(x)
    except:
        return None
 
def merge_key_scan(df):
    issues = []
 
    # SIDE mismatch
    if "side" in df.columns:
        unique = set(str(x).upper() for x in df["side"].dropna().unique())
        if not unique.issubset({"BUY", "SELL", "CE", "PE", "CALL", "PUT"}):
            issues.append("Irregular side values: " + str(unique))
 
    # EXPIRY mismatch
    if "expiry" in df.columns:
        expiry_samples = df["expiry"].dropna().astype(str).head(10).tolist()
        issues.append("Expiry samples: " + str(expiry_samples))
 
    return issues
 
 
# Scan merge-key issues
for name, path in CSV_TARGETS.items():
    if path.exists():
        try:
            df = pd.read_csv(path)
            report["csv_validation"][name]["merge_key_issues"] = merge_key_scan(df)
        except:
            pass
 
# ---------------------------
# 5. PIPELINE EXECUTION REPORTS
# ---------------------------
 
meta_dir = ROOT / "storage/live/meta"
if meta_dir.exists():
    reports = sorted(meta_dir.glob("pipeline_execution_report_*.json"))
    if reports:
        latest = reports[-1]
        try:
            report["pipeline_outputs"]["latest"] = json.load(open(latest))
        except:
            report["pipeline_outputs"]["latest"] = {"error": "cannot parse"}
 
# ---------------------------
# 6. FINAL SAVE
# ---------------------------
 
with open(REPORT_FILE, "w") as f:
    json.dump(report, f, indent=4)
 
print("\n==============================================")
print(" SYSTEM3 DIAGNOSTIC REPORT GENERATED")
print(" File:", REPORT_FILE)
print("==============================================")
 