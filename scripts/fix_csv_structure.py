"""
Fix CSV Structure - Standardize all CSV files for future-proofing
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def fix_paper_trades_csv(filepath):
    """Fix paper_trades_live.csv structure."""
    print("\n[1/3] FIXING PAPER TRADES CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: File not found")
        return False

    try:
        # Read with error handling
        df = pd.read_csv(filepath, on_bad_lines="skip", engine="python")

        print(f"  Original rows: {len(df)}")
        print(f"  Original columns: {len(df.columns)}")

        # Define standard columns
        standard_cols = [
            "position_id",
            "action",
            "timestamp",
            "time_ist",
            "underlying",
            "strike",
            "option_type",
            "price",
            "qty",
            "strategy",
        ]

        # Optional columns for CLOSE actions
        optional_cols = ["exit_reason", "realized_pnl", "realized_pnl_pct", "entry_price", "exit_price"]

        # Ensure all standard columns exist
        for col in standard_cols:
            if col not in df.columns:
                df[col] = None
                print(f"  Added missing column: {col}")

        # Ensure optional columns exist (fill with None for OPEN actions)
        for col in optional_cols:
            if col not in df.columns:
                df[col] = None

        # Fix data types
        if "strike" in df.columns:
            df["strike"] = pd.to_numeric(df["strike"], errors="coerce")

        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")

        if "qty" in df.columns:
            df["qty"] = pd.to_numeric(df["qty"], errors="coerce").fillna(0).astype(int)

        if "realized_pnl" in df.columns:
            df["realized_pnl"] = pd.to_numeric(df["realized_pnl"], errors="coerce")

        if "realized_pnl_pct" in df.columns:
            df["realized_pnl_pct"] = pd.to_numeric(df["realized_pnl_pct"], errors="coerce")

        # Order columns: standard first, then optional
        all_cols = standard_cols + [col for col in optional_cols if col in df.columns]
        df = df[all_cols]

        # Create backup
        backup_path = filepath.with_suffix(".csv.backup")
        if not backup_path.exists():
            import shutil

            shutil.copy2(filepath, backup_path)
            print(f"  Backup created: {backup_path.name}")

        # Save fixed file
        df.to_csv(filepath, index=False)
        print(f"  Fixed file saved")
        print(f"  Final rows: {len(df)}")
        print(f"  Final columns: {len(df.columns)}")
        print(f"  Status: FIXED")

        return True

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return False


def fix_chain_raw_csv(filepath):
    """Fix chain_raw_live.csv structure."""
    print("\n[2/3] FIXING CHAIN RAW CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: File not found")
        return False

    try:
        df = pd.read_csv(filepath, nrows=1000)  # Sample

        print(f"  Sampled rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Ensure numeric columns are numeric
        numeric_cols = [
            "strike",
            "ltp",
            "oi",
            "volume",
            "spot_price",
            "bidPrice",
            "offerPrice",
            "mid_price",
            "delta",
            "gamma",
            "theta",
            "vega",
            "iv",
        ]

        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        # Ensure timestamp columns exist
        if "timestamp_ist" not in df.columns:
            ist = pytz.timezone("Asia/Kolkata")
            df["timestamp_ist"] = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

        if "timestamp_epoch" not in df.columns:
            df["timestamp_epoch"] = datetime.now().timestamp()

        print(f"  Status: VALID (some NaN expected)")

        return True

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return False


def fix_underlying_rank_csv(filepath):
    """Fix underlying_rank_live.csv structure."""
    print("\n[3/3] FIXING UNDERLYING RANK CSV")
    print("-" * 80)

    if not filepath.exists():
        print("  Status: File not found")
        return False

    try:
        df = pd.read_csv(filepath)

        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Ensure numeric columns
        numeric_cols = [
            "underlying_score",
            "signal_strength",
            "execution_quality",
            "pcr",
            "pcr_delta_weighted",
            "expected_move",
        ]

        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == "object":
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        # Ensure timestamp
        if "timestamp_ist" not in df.columns:
            import pytz

            ist = pytz.timezone("Asia/Kolkata")
            df["timestamp_ist"] = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

        if "timestamp_epoch" not in df.columns:
            df["timestamp_epoch"] = datetime.now().timestamp()

        # Create backup
        backup_path = filepath.with_suffix(".csv.backup")
        if not backup_path.exists():
            import shutil

            shutil.copy2(filepath, backup_path)
            print(f"  Backup created: {backup_path.name}")

        # Save fixed file
        df.to_csv(filepath, index=False)
        print(f"  Status: FIXED")

        return True

    except Exception as e:
        print(f"  Error: {str(e)[:100]}")
        return False


def main():
    """Fix all CSV files."""
    print("\n" + "=" * 80)
    print("  CSV FILES STRUCTURE FIX")
    print("=" * 80)

    outputs_dir = ROOT_DIR / "outputs"

    results = {}
    results["paper_trades"] = fix_paper_trades_csv(outputs_dir / "paper_trades_live.csv")
    results["chain_raw"] = fix_chain_raw_csv(outputs_dir / "chain_raw_live.csv")
    results["underlying_rank"] = fix_underlying_rank_csv(outputs_dir / "underlying_rank_live.csv")

    print("\n" + "=" * 80)
    print("  FIX SUMMARY")
    print("=" * 80)

    fixed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"\nTotal Files: {total}")
    print(f"  Fixed: {fixed}")
    print(f"  Failed: {total - fixed}")

    print("\nFile Status:")
    for name, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"  {status_icon} {name}")

    print("\n" + "=" * 80)
    print("  FIX COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import pytz

    main()
