"""
System3 Phase 247 - Edge-by-Score-Bucket Tracker
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
META_DIR = PROJECT_ROOT / "storage" / "meta"
INPUT_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"
OUTPUT_CSV = META_DIR / "system3_edge_by_score_bucket.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_edge_by_score_bucket.log"


def _log(message: str) -> None:
    """Log message."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass


def run_phase247() -> dict:
    """Run Phase 247: Edge-by-Score-Bucket Tracker."""
    if not INPUT_CSV.exists():
        return {
            "phase": 247,
            "status": "WARN",
            "details": "Input file not found",
            "outputs": {},
            "errors": []
        }
    
    try:
        df = pd.read_csv(INPUT_CSV, engine="python", on_bad_lines="skip")
        
        if df.empty or "final_score" not in df.columns:
            return {
                "phase": 247,
                "status": "WARN",
                "details": "No data or missing final_score",
                "outputs": {},
                "errors": []
            }
        
        # Define buckets
        df["score_bucket"] = pd.cut(
            df["final_score"],
            bins=[-float('inf'), 0.0, 0.1, 0.2, 0.3, float('inf')],
            labels=["(-inf, 0.0)", "[0.0, 0.1)", "[0.1, 0.2)", "[0.2, 0.3)", "[0.3, inf)"]
        )
        
        # Find PnL column
        pnl_col = [c for c in df.columns if "pnl" in c.lower()][0] if any("pnl" in c.lower() for c in df.columns) else None
        
        # Aggregate by bucket
        bucket_stats = []
        for bucket, group in df.groupby("score_bucket", observed=False):
            trades = len(group)
            wins = len(group[group[pnl_col] > 0]) if pnl_col else 0
            win_rate = (wins / trades * 100) if trades > 0 else 0
            avg_pnl = group[pnl_col].mean() if pnl_col else 0
            
            bucket_stats.append({
                "bucket": str(bucket),
                "trades": trades,
                "wins": wins,
                "win_rate": win_rate,
                "avg_pnl": avg_pnl
            })
        
        # Append to CSV
        bucket_df = pd.DataFrame(bucket_stats)
        if OUTPUT_CSV.exists():
            existing_df = pd.read_csv(OUTPUT_CSV)
            bucket_df = pd.concat([existing_df, bucket_df], ignore_index=True)
        bucket_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        
        _log(f"Tracked edge by bucket: {len(bucket_stats)} buckets")
        
        return {
            "phase": 247,
            "status": "OK",
            "details": f"Edge tracked: {len(bucket_stats)} buckets",
            "outputs": {
                "buckets": len(bucket_stats),
                "output_file": str(OUTPUT_CSV)
            },
            "errors": []
        }
        
    except Exception as e:
        error_msg = f"Error: {e}"
        _log(f"ERROR: {error_msg}")
        return {
            "phase": 247,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg]
        }


if __name__ == "__main__":
    result = run_phase247()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

