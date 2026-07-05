"""
Simple Micro-Level Monitor - Direct output, no subprocess complications
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fix Unicode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

IST = pytz.timezone("Asia/Kolkata")


def check_file_status(filepath: Path, max_age: int = 60):
    """Check if file exists and is fresh."""
    if not filepath.exists():
        return {"status": "MISSING", "age": None, "size": 0}

    age = datetime.now().timestamp() - filepath.stat().st_mtime
    size = filepath.stat().st_size

    if age < max_age:
        return {"status": "FRESH", "age": age, "size": size}
    else:
        return {"status": "STALE", "age": age, "size": size}


def check_data_content(filepath: Path):
    """Check data content."""
    if not filepath.exists():
        return {"valid": False, "error": "File not found"}

    try:
        if filepath.suffix == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {"valid": True, "data": data}
        elif filepath.suffix == ".csv":
            import pandas as pd

            df = pd.read_csv(filepath, nrows=5)
            return {"valid": True, "rows": len(df), "cols": list(df.columns)}
    except Exception as e:
        return {"valid": False, "error": str(e)}


def monitor_once():
    """Perform one monitoring check."""
    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    now = datetime.now(IST)
    print(f"\n[{now.strftime('%H:%M:%S IST')}] CHECK")
    print("-" * 80)

    issues = []

    # Check files
    print("[FILES]")
    files_to_check = {
        "chain_raw_live.csv": 60,
        "pnl_live.json": 60,
        "positions_live.json": 60,
        "top_trade_signal.json": 60,
    }

    for filename, max_age in files_to_check.items():
        filepath = outputs_dir / filename
        status = check_file_status(filepath, max_age)

        if status["status"] == "MISSING":
            print(f"  ⚠️  {filename}: MISSING")
            issues.append(f"{filename} missing")
        elif status["status"] == "STALE":
            print(f"  ⚠️  {filename}: STALE ({status['age']:.1f}s old)")
            issues.append(f"{filename} stale ({status['age']:.1f}s old)")
        else:
            print(f"  ✅ {filename}: FRESH ({status['age']:.1f}s old, {status['size']} bytes)")

    print()

    # Check content
    print("[CONTENT]")
    pnl_file = outputs_dir / "pnl_live.json"
    if pnl_file.exists():
        content = check_data_content(pnl_file)
        if content["valid"]:
            pnl = content["data"].get("total_pnl", 0)
            trades = content["data"].get("total_trades", 0)
            print(f"  ✅ PnL: Valid (Total: Rs {pnl:.2f}, Trades: {trades})")
        else:
            print(f"  ❌ PnL: {content['error']}")
            issues.append(f"PnL content error: {content['error']}")

    pos_file = outputs_dir / "positions_live.json"
    if pos_file.exists():
        content = check_data_content(pos_file)
        if content["valid"]:
            open_pos = len(content["data"].get("open_positions", []))
            print(f"  ✅ Positions: Valid ({open_pos} open)")
        else:
            print(f"  ❌ Positions: {content['error']}")
            issues.append(f"Positions content error: {content['error']}")

    print()

    # Check auto-updates
    print("[AUTO-UPDATE]")
    chain_file = outputs_dir / "chain_raw_live.csv"
    if chain_file.exists():
        mtime_before = chain_file.stat().st_mtime
        size_before = chain_file.stat().st_size
        print("  [WAIT] Monitoring for 7 seconds...")
        time.sleep(7)

        if chain_file.exists():
            mtime_after = chain_file.stat().st_mtime
            size_after = chain_file.stat().st_size
            age = datetime.now().timestamp() - mtime_after

            if mtime_after > mtime_before:
                print(f"  ✅ Auto-updating: File updated")
                print(f"     Size: {size_before} → {size_after} bytes")
                print(f"     Age: {age:.1f}s")
            else:
                print(f"  ⚠️  Not updating: File unchanged ({age:.1f}s old)")
                issues.append(f"Data not auto-updating ({age:.1f}s old)")
        else:
            print(f"  ⚠️  File disappeared")
            issues.append("Data file disappeared")
    else:
        print(f"  ⚠️  File not found")
        issues.append("Data file not found")

    print()

    # Summary
    if issues:
        print(f"  ⚠️  {len(issues)} ISSUES FOUND")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print(f"  ✅ ALL CHECKS PASSED - NO WARNINGS")

    print()
    print("=" * 80)

    return len(issues) == 0


def main():
    """Main monitoring loop."""
    import argparse

    parser = argparse.ArgumentParser(description="Simple Micro-Level Monitor")
    parser.add_argument("--duration", type=int, default=10, help="Monitor for N minutes (default: 10, 0 = infinite)")
    parser.add_argument("--interval", type=int, default=10, help="Check interval in seconds (default: 10)")

    args = parser.parse_args()

    print("=" * 80)
    print("  SIMPLE MICRO-LEVEL MONITOR")
    print("=" * 80)
    print()
    print("Monitoring system components, data files, and auto-triggers...")
    if args.duration > 0:
        print(f"Duration: {args.duration} minutes")
    else:
        print("Duration: Infinite (Press Ctrl+C to stop)")
    print(f"Check interval: {args.interval} seconds")
    print()

    check_count = 0
    all_passed = True
    issues_found = []
    start_time = datetime.now()

    end_time = None
    if args.duration > 0:
        end_time = start_time + timedelta(minutes=args.duration)

    try:
        while True:
            if end_time and datetime.now() >= end_time:
                break

            check_count += 1
            passed = monitor_once()
            if not passed:
                all_passed = False
                issues_found.append(f"Check {check_count} failed")

            if end_time:
                remaining = (end_time - datetime.now()).total_seconds()
                if remaining > 0:
                    print(f"[INFO] {check_count} checks done, {remaining/60:.1f} minutes remaining")
                    print()

            time.sleep(args.interval)
    except KeyboardInterrupt:
        print()
        print("Monitoring interrupted by user")

    # Final summary
    print()
    print("=" * 80)
    print("  FINAL SUMMARY")
    print("=" * 80)
    print()
    duration = (datetime.now() - start_time).total_seconds() / 60
    print(f"  Monitoring Duration: {duration:.1f} minutes")
    print(f"  Checks Performed: {check_count}")
    print(f"  Status: {'✅ ALL PASSED - NO WARNINGS' if all_passed else '⚠️  ISSUES FOUND'}")
    if issues_found:
        print(f"  Issues: {len(issues_found)}")
    print()

    # Save report
    report = {
        "start_time": start_time.isoformat(),
        "end_time": datetime.now().isoformat(),
        "duration_minutes": duration,
        "checks_performed": check_count,
        "all_passed": all_passed,
        "issues_count": len(issues_found),
    }

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(exist_ok=True)
    report_file = outputs_dir / "micro_monitor_report.json"

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"  Report saved: {report_file}")
    except Exception as e:
        print(f"  Failed to save report: {e}")

    print()
    print("=" * 80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
