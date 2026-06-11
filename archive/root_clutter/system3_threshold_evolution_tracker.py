"""
System3 Phase 243 - Threshold Evolution Tracker

Track how thresholds change over time.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

META_DIR = PROJECT_ROOT / "storage" / "meta"
META_DIR.mkdir(parents=True, exist_ok=True)
THRESHOLD_CANDIDATES_PATH = META_DIR / "system3_threshold_candidates.json"
HISTORY_CSV = META_DIR / "system3_threshold_history.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_threshold_evolution.log"


def _log(message: str) -> None:
    """Log message."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass


def run_phase243() -> dict:
    """Run Phase 243: Threshold Evolution Tracker."""
    try:
        if not THRESHOLD_CANDIDATES_PATH.exists():
            _log("WARN: Threshold candidates file not found")
            return {
                "phase": 243,
                "status": "WARN",
                "details": "Threshold candidates file not found",
                "outputs": {},
                "errors": []
            }
        
        with THRESHOLD_CANDIDATES_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Get best candidate
        candidates = data.get("candidates", [])
        if not candidates:
            return {
                "phase": 243,
                "status": "WARN",
                "details": "No candidates found",
                "outputs": {},
                "errors": []
            }
        
        best_candidate = max(candidates, key=lambda x: x.get("buy_count", 0) + x.get("sell_count", 0))
        
        buy_thr = best_candidate.get("buy_threshold", 0.12)
        sell_thr = best_candidate.get("sell_threshold", -0.10)
        
        # Append to history
        run_ts = datetime.now().isoformat()
        
        # Append default + all underlyings
        new_rows = [
            {"run_ts": run_ts, "underlying": "default", "buy": buy_thr, "sell": sell_thr}
        ]
        for underlying in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
            new_rows.append({
                "run_ts": run_ts,
                "underlying": underlying,
                "buy": buy_thr,
                "sell": sell_thr
            })
        
        new_df = pd.DataFrame(new_rows)
        
        # Load existing history or create new
        if HISTORY_CSV.exists():
            try:
                history_df = pd.read_csv(HISTORY_CSV)
                if not history_df.empty:
                    history_df = pd.concat([history_df, new_df], ignore_index=True)
                else:
                    history_df = new_df
            except Exception:
                history_df = new_df
        else:
            history_df = new_df
        
        history_df.to_csv(HISTORY_CSV, index=False, encoding="utf-8")
        
        _log(f"Tracked thresholds: buy={buy_thr:.3f}, sell={sell_thr:.3f}")
        
        return {
            "phase": 243,
            "status": "OK",
            "details": f"Tracked thresholds: buy={buy_thr:.3f}, sell={sell_thr:.3f}",
            "outputs": {
                "buy_threshold": buy_thr,
                "sell_threshold": sell_thr,
                "history_file": str(HISTORY_CSV)
            },
            "errors": []
        }
        
    except Exception as e:
        error_msg = f"Error tracking thresholds: {e}"
        _log(f"ERROR: {error_msg}")
        return {
            "phase": 243,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg]
        }


if __name__ == "__main__":
    result = run_phase243()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

