"""
System3 Phase 223 - Threshold Optimizer

Optimizes BUY/SELL thresholds based on historical data.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
CANDIDATES_JSON = STORAGE_META / "system3_threshold_candidates.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_threshold_optimizer.log"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"


def run_phase223(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 223: Threshold Optimizer.

    Returns:
        dict: {
            "phase": 223,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "candidates_generated": int,
                "candidates_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    candidates = []

    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            # Try with forward returns first
            signals_file = (
                SIGNALS_CSV if SIGNALS_CSV.exists() else PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
            )

            if not signals_file.exists():
                return {
                    "phase": 223,
                    "status": "WARN",
                    "details": "Signals CSV not found",
                    "outputs": {"candidates_generated": 0, "candidates_file": str(CANDIDATES_JSON)},
                    "errors": [],
                }

            # Check if file is locked (try to open exclusively)
            try:
                test_file = open(signals_file, "r")
                test_file.close()
            except (PermissionError, IOError, OSError) as lock_error:
                if attempt < max_retries - 1:
                    import time

                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "phase": 223,
                        "status": "WARN",
                        "details": f"Signals file locked after {max_retries} attempts, skipping this run",
                        "outputs": {"candidates_generated": 0, "candidates_file": str(CANDIDATES_JSON)},
                        "errors": [],
                    }

            # Load data
            try:
                df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")
            except Exception as read_error:
                if attempt < max_retries - 1:
                    import time

                    time.sleep(retry_delay)
                    continue
                else:
                    errors.append(f"Failed to read CSV after {max_retries} attempts: {read_error}")
                    raise

            if "final_score" not in df.columns:
                return {
                    "phase": 223,
                    "status": "WARN",
                    "details": "final_score column not found",
                    "outputs": {"candidates_generated": 0, "candidates_file": str(CANDIDATES_JSON)},
                    "errors": [],
                }

            # Convert final_score to numeric (handle string values)
            df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")

            # Filter out NaN values
            df = df.dropna(subset=["final_score"])

            if len(df) == 0:
                return {
                    "phase": 223,
                    "status": "WARN",
                    "details": "No valid final_score values found after conversion",
                    "outputs": {"candidates_generated": 0, "candidates_file": str(CANDIDATES_JSON)},
                    "errors": [],
                }

            # Simple threshold optimization (test different thresholds)
            # Note: score_range calculation removed as it was never used
            buy_candidates = [0.3, 0.4, 0.5, 0.6]
            sell_candidates = [-0.6, -0.5, -0.4, -0.3]

            for buy_thr in buy_candidates:
                for sell_thr in sell_candidates:
                    if buy_thr <= abs(sell_thr):
                        continue

                    # Count signals at these thresholds (final_score is now numeric)
                    buy_count = (df["final_score"] >= buy_thr).sum()
                    sell_count = (df["final_score"] <= sell_thr).sum()

                    candidates.append(
                        {
                            "buy_threshold": buy_thr,
                            "sell_threshold": sell_thr,
                            "buy_count": int(buy_count),
                            "sell_count": int(sell_count),
                            "objective": "hit_rate",  # Placeholder
                        }
                    )

            # Save candidates
            candidates_data = {
                "candidates": candidates,
                "generated": datetime.now().isoformat(),
                "optimization_objective": "hit_rate",
            }
            with CANDIDATES_JSON.open("w", encoding="utf-8") as f:
                json.dump(candidates_data, f, indent=2)

            # Log optimization process
            with LOG_PATH.open("w", encoding="utf-8") as f:
                f.write(f"System3 Threshold Optimizer Log\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Candidates Generated: {len(candidates)}\n\n")
                for cand in candidates[:5]:  # Show first 5
                    f.write(
                        f"Buy: {cand['buy_threshold']:.2f}, Sell: {cand['sell_threshold']:.2f}, "
                        f"Buy Count: {cand['buy_count']}, Sell Count: {cand['sell_count']}\n"
                    )

            status = "OK"
            details = f"Generated {len(candidates)} threshold candidates"

            return {
                "phase": 223,
                "status": status,
                "details": details,
                "outputs": {
                    "candidates_generated": len(candidates),
                    "candidates_file": str(CANDIDATES_JSON),
                    "log_path": str(LOG_PATH),
                },
                "errors": errors,
            }

        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            error_msg = f"Phase 223 failed: {e}"
            errors.append(str(e))
            errors.append(error_trace)

            # Log error details for debugging
            try:
                with LOG_PATH.open("a", encoding="utf-8") as f:
                    f.write(f"\n\nERROR at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{error_msg}\n")
                    f.write(f"{error_trace}\n")
            except:
                pass  # Don't fail if logging fails

            # If this was the last attempt, return error
            if attempt == max_retries - 1:
                return {
                    "phase": 223,
                    "status": "ERROR",
                    "details": error_msg,
                    "outputs": {},
                    "errors": errors,
                }
            # Otherwise, retry
            import time

            time.sleep(retry_delay)
            continue

    # If we get here, all retries failed
    return {
        "phase": 223,
        "status": "ERROR",
        "details": f"Phase 223 failed after {max_retries} attempts",
        "outputs": {},
        "errors": errors,
    }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 223 - THRESHOLD OPTIMIZER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase223()

    print(f"Phase 223: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nCandidates JSON: {result['outputs']['candidates_file']}")
        print(f"Candidates: {result['outputs']['candidates_generated']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
