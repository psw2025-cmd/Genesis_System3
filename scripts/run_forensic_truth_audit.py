"""
Run the Full Truth Audit for Genesis System3 across src, core, dashboard.
Produces FULL_TRUTH_AUDIT.txt and summarizes all findings.
"""
import os
import subprocess
import json
from pathlib import Path

ROOT = Path("c:/Genesis_System3_clean")

def run_rg(cmd_str):
    res = subprocess.run(cmd_str, shell=True, cwd=str(ROOT), capture_output=True, text=True, errors="replace")
    return res.stdout, res.stderr, res.returncode

def main():
    print("[1/17] Running Biggest Command: FULL_TRUTH_AUDIT.txt ...")
    cmd_full = 'rg -n -i "live|real|verified|certified|simulated|synthetic|mock|demo|placeholder|dummy|fallback|cache|csv|parquet|duckdb|option_chain|marketfeed|dhan" src core dashboard > FULL_TRUTH_AUDIT.txt'
    subprocess.run(cmd_full, shell=True, cwd=str(ROOT))
    full_audit_size = os.path.getsize(ROOT / "FULL_TRUTH_AUDIT.txt") if (ROOT / "FULL_TRUTH_AUDIT.txt").exists() else 0
    print(f"       -> FULL_TRUTH_AUDIT.txt written ({full_audit_size} bytes)")

    tasks = {
        "fake_simulated_demo": 'rg -n -i "simulated|synthetic|demo|mock|placeholder|sample|test_data|fallback|dummy|prototype" src core dashboard',
        "dhan_api_usage": 'rg -n -i "dhan|marketfeed|market quote|option chain|option_chain|historical|api.dhan" src core',
        "files_writing_csv": 'rg -n "to_csv\\(" src core',
        "files_reading_csv": 'rg -n "read_csv\\(" src core',
        "storage_live_deps": 'rg -n "storage/live" src core',
        "option_chain_producers": 'rg -n -i "option_chain|option chain" src core',
        "who_writes_watch_file": 'rg -n "dhan_index_options_watch.csv" src core',
        "who_writes_ai_signals": 'rg -n "dhan_index_ai_signals.csv" src core',
        "places_claiming_live": 'rg -n -i "live|real-time|real time|verified|certified" src core dashboard',
        "ui_warning_source": 'rg -n "NOT CERTIFIED|LIVE-VERIFIED|locally configured symbols|AUTH_REQUIRED|market data credentials not configured" src core dashboard content',
        "stale_cache_paths": 'rg -n -i "cache|cached|stale|refresh|ttl" src core',
        "hardcoded_prices_nifty": 'rg -n "NIFTY.*=" src core dashboard content',
        "hardcoded_prices_banknifty": 'rg -n "BANKNIFTY.*=" src core dashboard content',
        "localhost_apis_by_ui": 'rg -n -i "api/|fetch\\(|axios|localhost|127.0.0.1" dashboard src content',
        "every_csv_dep": 'rg -n -i "\\.csv" src core dashboard',
        "parquet_opportunities": 'rg -n -i "parquet|duckdb|clickhouse|sqlite|postgres" src core'
    }

    results = {}
    for name, cmd in tasks.items():
        stdout, stderr, code = run_rg(cmd)
        lines = [line.strip() for line in stdout.splitlines() if line.strip()]
        results[name] = {
            "cmd": cmd,
            "count": len(lines),
            "samples": lines[:10]
        }
        print(f"[{name}] {len(lines)} occurrences found.")

    with open(ROOT / "reports" / "FORENSIC_TRUTH_AUDIT_SUMMARY.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("Summary written to reports/FORENSIC_TRUTH_AUDIT_SUMMARY.json")

if __name__ == "__main__":
    main()
