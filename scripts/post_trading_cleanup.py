"""
Post-Trading Cleanup and Archival
Handles session end, data archival, and preparation for next session
"""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def archive_session_data():
    """Archive current session data."""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    session_date = now.strftime("%Y%m%d")
    session_time = now.strftime("%H%M%S")

    archive_dir = ROOT_DIR / "storage" / "archive" / f"session_{session_date}_{session_time}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/4] Archiving session data to: {archive_dir.name}")

    # Archive files
    files_to_archive = [
        ("outputs/pnl_live.json", "pnl.json"),
        ("outputs/positions_live.json", "positions.json"),
        ("outputs/paper_trades_live.csv", "trades.csv"),
        ("outputs/top_trade_signal.json", "signals.json"),
        ("outputs/qc_report_live.json", "qc_report.json"),
        ("outputs/chain_raw_live.csv", "chain_raw.csv"),
        ("outputs/underlying_rank_live.csv", "underlying_rank.csv"),
    ]

    archived = []
    for src, dst in files_to_archive:
        src_path = ROOT_DIR / src
        if src_path.exists():
            dst_path = archive_dir / dst
            try:
                shutil.copy2(src_path, dst_path)
                archived.append(dst)
                print(f"  [OK] Archived: {dst}")
            except Exception as e:
                print(f"  [WARN] Failed to archive {dst}: {e}")

    # Create session summary
    summary = {
        "session_date": session_date,
        "session_time": session_time,
        "archived_files": archived,
        "archive_path": str(archive_dir),
    }

    summary_path = archive_dir / "session_summary.json"
    json.dump(summary, open(summary_path, "w"), indent=2)

    print(f"  [OK] Session summary saved")
    return archive_dir


def clear_current_session():
    """Clear current session files (optional - for fresh start)."""
    print(f"\n[2/4] Clearing current session files...")

    files_to_clear = [
        "outputs/pnl_live.json",
        "outputs/positions_live.json",
        "outputs/paper_trades_live.csv",
    ]

    cleared = []
    for file_path in files_to_clear:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                cleared.append(file_path)
                print(f"  [OK] Cleared: {file_path}")
            except Exception as e:
                print(f"  [WARN] Failed to clear {file_path}: {e}")

    return cleared


def prepare_next_session():
    """Prepare for next session."""
    print(f"\n[3/4] Preparing for next session...")

    # Ensure directories exist
    (ROOT_DIR / "outputs").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "storage" / "archive").mkdir(parents=True, exist_ok=True)

    print(f"  [OK] Directories ready")

    # Initialize empty PnL file
    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    if not pnl_file.exists():
        initial_pnl = {
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_realized_pnl": 0.0,
            "total_unrealized_pnl": 0.0,
            "total_pnl": 0.0,
            "open_positions": 0,
        }
        json.dump(initial_pnl, open(pnl_file, "w"), indent=2)
        print(f"  [OK] Initialized PnL file")

    return True


def generate_session_report(archive_dir):
    """Generate session report."""
    print(f"\n[4/4] Generating session report...")

    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    if pnl_file.exists():
        try:
            pnl = json.load(open(pnl_file))
            report = {
                "session_end": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                "total_trades": pnl.get("total_trades", 0),
                "win_rate": pnl.get("win_rate", 0),
                "total_pnl": pnl.get("total_pnl", 0),
                "archive_location": str(archive_dir),
            }

            report_path = archive_dir / "session_report.json"
            json.dump(report, open(report_path, "w"), indent=2)
            print(f"  [OK] Session report generated")
            return report
        except:
            pass

    return None


def main(clear_files=False):
    """Main cleanup function."""
    print("\n" + "=" * 80)
    print("  POST-TRADING CLEANUP AND ARCHIVAL")
    print("=" * 80)

    # Archive
    archive_dir = archive_session_data()

    # Clear if requested
    if clear_files:
        clear_current_session()

    # Prepare next session
    prepare_next_session()

    # Generate report
    generate_session_report(archive_dir)

    print("\n" + "=" * 80)
    print("  CLEANUP COMPLETE")
    print("=" * 80 + "\n")

    return archive_dir


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--clear", action="store_true", help="Clear current session files")
    args = parser.parse_args()

    main(clear_files=args.clear)
