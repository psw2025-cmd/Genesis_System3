"""
Check output files and display summary.
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def main():
    print("=" * 80)
    print("  OUTPUT FILES ANALYSIS")
    print("=" * 80)
    print()

    outputs_dir = ROOT_DIR / "outputs"

    # Check chain_raw_live.csv
    csv_file = outputs_dir / "chain_raw_live.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        print(f"[1] chain_raw_live.csv")
        print(f"    ✅ EXISTS")
        print(f"    Size: {len(df)} rows, {len(df.columns)} columns")
        print(f"    File size: {csv_file.stat().st_size / 1024:.2f} KB")
        print(f"    Latest timestamp: {df['timestamp_ist'].iloc[-1] if 'timestamp_ist' in df.columns else 'N/A'}")
        print(f"    Indices: {df['underlying'].unique() if 'underlying' in df.columns else 'N/A'}")
        print()
    else:
        print(f"[1] chain_raw_live.csv")
        print(f"    ❌ NOT FOUND")
        print()

    # Check underlying_rank_live.csv
    rank_file = outputs_dir / "underlying_rank_live.csv"
    if rank_file.exists():
        df_rank = pd.read_csv(rank_file)
        print(f"[2] underlying_rank_live.csv")
        print(f"    ✅ EXISTS")
        print(f"    Size: {len(df_rank)} rows")
        print(f"    Columns: {', '.join(df_rank.columns[:5])}...")
        print()
        print("    Top 5 Rankings:")
        for idx, row in df_rank.head().iterrows():
            print(f"      {idx+1}. {row.get('underlying', 'N/A')}: Score {row.get('underlying_score', 'N/A'):.2f}")
        print()
    else:
        print(f"[2] underlying_rank_live.csv")
        print(f"    ❌ NOT FOUND")
        print()

    # Check top_trade_signal.json
    signal_file = outputs_dir / "top_trade_signal.json"
    if signal_file.exists():
        with open(signal_file, "r") as f:
            signal = json.load(f)
        print(f"[3] top_trade_signal.json")
        print(f"    ✅ EXISTS")
        print(f"    Action: {signal.get('action', 'N/A')}")
        print(f"    Underlying: {signal.get('underlying', 'N/A')}")
        print(f"    Strategy: {signal.get('strategy', 'N/A')}")
        print(f"    Confidence: {signal.get('confidence', 'N/A')}")
        print()
    else:
        print(f"[3] top_trade_signal.json")
        print(f"    ❌ NOT FOUND")
        print()

    # Check qc_report_live.json
    qc_file = outputs_dir / "qc_report_live.json"
    if qc_file.exists():
        with open(qc_file, "r") as f:
            qc = json.load(f)
        print(f"[4] qc_report_live.json")
        print(f"    ✅ EXISTS")
        print(f"    Overall Passed: {qc.get('overall_passed', 'N/A')}")
        print(f"    Reason: {qc.get('reason', 'N/A')}")
        if "underlying_results" in qc:
            print(f"    Underlying Results: {len(qc['underlying_results'])} indices checked")
        print()
    else:
        print(f"[4] qc_report_live.json")
        print(f"    ❌ NOT FOUND")
        print()

    # Check pnl_live.json
    pnl_file = outputs_dir / "pnl_live.json"
    if pnl_file.exists():
        with open(pnl_file, "r") as f:
            pnl = json.load(f)
        print(f"[5] pnl_live.json")
        print(f"    ✅ EXISTS")
        print(f"    Total PnL: Rs {pnl.get('total_pnl', 0):,.2f}")
        print(f"    Total Trades: {pnl.get('total_trades', 0)}")
        print(f"    Win Rate: {pnl.get('win_rate', 0):.1f}%")
        print()
    else:
        print(f"[5] pnl_live.json")
        print(f"    ❌ NOT FOUND")
        print()

    print("=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    files_found = sum(
        [csv_file.exists(), rank_file.exists(), signal_file.exists(), qc_file.exists(), pnl_file.exists()]
    )
    print(f"Files found: {files_found}/5")
    print()


if __name__ == "__main__":
    main()
