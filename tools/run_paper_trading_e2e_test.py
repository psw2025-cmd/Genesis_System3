"""E2E Paper Trading Test - Phase 106
Clean single-file implementation.

Run with the repository venv Python, e.g.:
  .\venv\Scripts\python.exe tools\run_paper_trading_e2e_test.py
"""

import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "logs"
INSPECTOR_DIR = LOGS_DIR / "inspector"
STORAGE_LIVE = ROOT / "storage" / "live"
LEDGER_CSV = STORAGE_LIVE / "live_orders_ledger.csv"
PHASE106_LOG = LOGS_DIR / "phase106_dryrun_execution.log"
REPORT_MD = INSPECTOR_DIR / f'e2e_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'

for d in (INSPECTOR_DIR, STORAGE_LIVE, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd, cwd=ROOT, timeout=120):
    """Run a subprocess command and return (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), shell=False, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired:
        return 2, "", "timeout"
    except Exception as e:
        return 3, "", str(e)


def write_sample_ledger(path: Path):
    fieldnames = [
        "local_order_id",
        "timestamp",
        "status",
        "underlying",
        "strike",
        "option_type",
        "entry_price",
        "qty",
        "broker_status",
        "last_update_ts",
    ]
    sample_row = {
        "local_order_id": "TEST-PLANNED-1",
        "timestamp": datetime.now().isoformat(),
        "status": "PLANNED",
        "underlying": "NIFTY",
        "strike": "18000",
        "option_type": "CE",
        "entry_price": 100.0,
        "qty": 1,
        "broker_status": "PLANNED",
        "last_update_ts": datetime.now().isoformat(),
    }
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(sample_row)


def import_and_run_phase106():
    """Import and call the Phase106 dry-run bridge inside this process.

    Returns (code, result) where result is typically a dict from the bridge.
    """
    try:
        sys.path.insert(0, str(ROOT))
        from core.engine import system3_phase106_dryrun_execution_bridge as ph106

        res = ph106.run_phase106()
        return 0, res
    except Exception as e:
        return 1, {"error": str(e)}


def tail_file(path: Path, lines: int = 60) -> str:
    if not path.exists():
        return "(file not found)"
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            ln = f.read().splitlines()
            return "\n".join(ln[-lines:])
    except Exception:
        return "(read error)"


def main():
    report_lines = []
    report_lines.append("# System3 E2E Paper Trading Test Report")
    report_lines.append("Generated: " + datetime.now().isoformat())
    report_lines.append("")

    # 1) Startup verification
    report_lines.append("## 1) Startup Verification")
    code1, out1, err1 = run_cmd([sys.executable, "system3_startup_verification.py"])
    report_lines.append("Return code: " + str(code1))
    report_lines.append("STDOUT:")
    report_lines.append(out1 or "(no stdout)")
    report_lines.append("STDERR:")
    report_lines.append(err1 or "(no stderr)")
    report_lines.append("")

    # 2) Pre-market dry-run
    report_lines.append("## 2) Pre-market Signal Dry-Run")
    code2, out2, err2 = run_cmd([sys.executable, "core/validation/pre_market_signal_dryrun.py"])
    report_lines.append("Return code: " + str(code2))
    report_lines.append("STDOUT:")
    report_lines.append(out2 or "(no stdout)")
    report_lines.append("STDERR:")
    report_lines.append(err2 or "(no stderr)")
    report_lines.append("")

    # 3) Prepare sample ledger
    report_lines.append("## 3) Prepare Sample PLANNED Ledger")
    try:
        write_sample_ledger(LEDGER_CSV)
        report_lines.append("Wrote sample ledger to: " + str(LEDGER_CSV))
    except Exception as e:
        report_lines.append("Failed to write ledger: " + str(e))
    report_lines.append("")

    # 4) Run Phase 106 (dry-run)
    report_lines.append("## 4) Run Phase 106 (DRY-RUN)")
    code3, res3 = import_and_run_phase106()
    report_lines.append("Phase106 return code: " + str(code3))
    try:
        report_lines.append("Phase106 result:")
        report_lines.append(json.dumps(res3, indent=2, default=str))
    except Exception:
        report_lines.append(str(res3))
    report_lines.append("")

    # 5) Phase106 log tail
    report_lines.append("## 5) Phase106 Log (tail 200 lines)")
    report_lines.append(tail_file(PHASE106_LOG, 200))
    report_lines.append("")

    # 6) Ledger tail
    report_lines.append("## 6) Ledger (tail 50 lines)")
    report_lines.append(tail_file(LEDGER_CSV, 50))
    report_lines.append("")

    # Write report
    try:
        with REPORT_MD.open("w", encoding="utf-8", newline="") as f:
            f.write("\n".join(report_lines))
        print("E2E test completed. Report:", str(REPORT_MD))
    except Exception as e:
        print("Failed to write report:", e, file=sys.stderr)

    # Exit code: success only if all three steps returned 0
    overall_ok = code1 == 0 and code2 == 0 and code3 == 0
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
