"""
System3 Phase 365 - Live Accuracy Tracker

Tracks rolling accuracy metrics over time using forward returns and virtual orders.
Provides hit-rate, average gain/loss, per-symbol performance, and time-window stats.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def load_signals_with_forward_returns() -> pd.DataFrame:
    """Load signal data with forward returns."""
    signal_file = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"

    if not signal_file.exists():
        logger.warning(f"Signal file not found: {signal_file}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(signal_file, on_bad_lines="skip", low_memory=False)
        logger.info(f"Loaded {len(df)} rows from {signal_file.name}")
        return df
    except Exception as e:
        logger.error(f"Error loading signal file: {e}")
        return pd.DataFrame()


def compute_hit_rate(df: pd.DataFrame, signal_col: str = "signal") -> Dict[str, Any]:
    """
    Compute hit rate for each signal type.
    Hit = signal direction matches forward return direction.
    """
    if signal_col not in df.columns:
        return {"error": f"Signal column '{signal_col}' not found"}

    # Identify forward return columns
    fwd_cols = [col for col in df.columns if "fwd_ret" in col.lower()]

    if not fwd_cols:
        return {"error": "No forward return columns found"}

    # Use primary forward return (typically fwd_ret_1)
    primary_fwd_col = fwd_cols[0]
    logger.info(f"Using forward return column: {primary_fwd_col}")

    hit_rate_results = {}

    for signal_type in df[signal_col].unique():
        if pd.isna(signal_type):
            continue

        signal_subset = df[df[signal_col] == signal_type].copy()
        signal_subset = signal_subset.dropna(subset=[primary_fwd_col])

        if len(signal_subset) == 0:
            continue

        # Convert forward returns to numeric
        fwd_returns = pd.to_numeric(signal_subset[primary_fwd_col], errors="coerce").dropna()

        if len(fwd_returns) == 0:
            continue

        # Determine hits based on signal type
        if "BUY" in str(signal_type).upper() or "CALL" in str(signal_type).upper():
            hits = (fwd_returns > 0).sum()
        elif "SELL" in str(signal_type).upper() or "PUT" in str(signal_type).upper():
            hits = (fwd_returns < 0).sum()
        else:
            # For HOLD or unclear signals, consider positive returns as hits
            hits = (fwd_returns > 0).sum()

        hit_rate = (hits / len(fwd_returns)) * 100 if len(fwd_returns) > 0 else 0

        hit_rate_results[str(signal_type)] = {
            "count": len(fwd_returns),
            "hits": int(hits),
            "hit_rate_pct": round(hit_rate, 2),
            "avg_return": round(float(fwd_returns.mean()), 4),
            "median_return": round(float(fwd_returns.median()), 4),
            "max_return": round(float(fwd_returns.max()), 4),
            "min_return": round(float(fwd_returns.min()), 4),
        }

    return hit_rate_results


def compute_per_symbol_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute performance metrics grouped by underlying symbol."""
    if "underlying" not in df.columns:
        return {"error": "No 'underlying' column found"}

    # Identify forward return column
    fwd_cols = [col for col in df.columns if "fwd_ret" in col.lower()]
    if not fwd_cols:
        return {"error": "No forward return columns found"}

    primary_fwd_col = fwd_cols[0]

    symbol_performance = {}

    for symbol in df["underlying"].unique():
        if pd.isna(symbol):
            continue

        symbol_subset = df[df["underlying"] == symbol].copy()
        symbol_subset = symbol_subset.dropna(subset=[primary_fwd_col])

        if len(symbol_subset) == 0:
            continue

        fwd_returns = pd.to_numeric(symbol_subset[primary_fwd_col], errors="coerce").dropna()

        if len(fwd_returns) == 0:
            continue

        wins = (fwd_returns > 0).sum()
        losses = (fwd_returns < 0).sum()

        symbol_performance[str(symbol)] = {
            "count": len(fwd_returns),
            "wins": int(wins),
            "losses": int(losses),
            "win_rate_pct": round((wins / len(fwd_returns)) * 100, 2),
            "avg_return": round(float(fwd_returns.mean()), 4),
            "total_return": round(float(fwd_returns.sum()), 4),
        }

    return symbol_performance


def compute_time_window_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute performance for different time windows."""
    time_windows = {"all_time": len(df), "today": 0, "last_7_days": 0, "last_30_days": 0}

    # Check if timestamp column exists
    timestamp_cols = [
        col for col in df.columns if "timestamp" in col.lower() or "date" in col.lower() or "time" in col.lower()
    ]

    if not timestamp_cols:
        logger.warning("No timestamp column found, cannot compute time-window performance")
        return {"error": "No timestamp column available"}

    # Try to parse timestamps
    timestamp_col = timestamp_cols[0]
    logger.info(f"Using timestamp column: {timestamp_col}")

    try:
        # Parse timestamps, suppress pandas date inference warning
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df["parsed_timestamp"] = pd.to_datetime(df[timestamp_col], errors="coerce")

        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        time_windows["today"] = len(df[df["parsed_timestamp"] >= today_start])
        time_windows["last_7_days"] = len(df[df["parsed_timestamp"] >= week_ago])
        time_windows["last_30_days"] = len(df[df["parsed_timestamp"] >= month_ago])

    except Exception as e:
        logger.warning(f"Could not parse timestamps: {e}")

    return time_windows


def load_virtual_orders_pnl() -> Dict[str, Any]:
    """Load virtual orders and compute PnL if available."""
    virtual_orders_file = STORAGE_LIVE / "angel_virtual_orders.csv"

    if not virtual_orders_file.exists():
        return {"status": "not_available", "message": "Virtual orders file not found"}

    try:
        df = pd.read_csv(virtual_orders_file, on_bad_lines="skip", low_memory=False)

        if len(df) == 0:
            return {"status": "empty", "message": "Virtual orders file is empty"}

        pnl_summary = {"total_orders": len(df), "columns": list(df.columns)}

        # Try to compute PnL if relevant columns exist
        if "pnl" in df.columns:
            pnl_values = pd.to_numeric(df["pnl"], errors="coerce").dropna()
            pnl_summary["total_pnl"] = round(float(pnl_values.sum()), 2)
            pnl_summary["avg_pnl_per_trade"] = round(float(pnl_values.mean()), 2)
            pnl_summary["max_pnl"] = round(float(pnl_values.max()), 2)
            pnl_summary["min_pnl"] = round(float(pnl_values.min()), 2)

        return {"status": "ok", "data": pnl_summary}

    except Exception as e:
        logger.error(f"Error loading virtual orders: {e}")
        return {"status": "error", "error": str(e)}


def run_phase365(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 365: Live Accuracy Tracker.

    Returns:
        dict: {
            "status": "ok" | "warn" | "error",
            "overall_accuracy": float,
            "outputs": {"json": path, "report": path}
        }
    """
    logger.info("=== Phase 365: Live Accuracy Tracker ===")

    result = {
        "phase": 365,
        "name": "Live Accuracy Tracker",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "outputs": {},
    }

    try:
        # Load signal data with forward returns
        df = load_signals_with_forward_returns()

        if df.empty:
            result["status"] = "warn"
            result["message"] = "No signal data with forward returns available"
            logger.warning(result["message"])
            return result

        logger.info(f"Analyzing {len(df)} signals")

        # Compute hit rates by signal type
        hit_rates = compute_hit_rate(df)

        # Compute per-symbol performance
        symbol_performance = compute_per_symbol_performance(df)

        # Compute time window performance
        time_windows = compute_time_window_performance(df)

        # Load virtual orders PnL if available
        virtual_pnl = load_virtual_orders_pnl()

        # Calculate overall accuracy (weighted average of hit rates)
        if hit_rates and not hit_rates.get("error"):
            total_signals = sum(metrics["count"] for metrics in hit_rates.values())
            weighted_hit_rate = sum(metrics["hit_rate_pct"] * metrics["count"] for metrics in hit_rates.values())
            overall_accuracy = (weighted_hit_rate / total_signals) if total_signals > 0 else 0
        else:
            overall_accuracy = 0

        result["overall_accuracy"] = round(overall_accuracy, 2)
        result["total_signals_analyzed"] = len(df)
        result["hit_rates_by_signal"] = hit_rates
        result["symbol_performance"] = symbol_performance
        result["time_windows"] = time_windows
        result["virtual_orders_pnl"] = virtual_pnl

        # Write JSON output
        json_output = STORAGE_METRICS / "accuracy_tracker_365.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        result["outputs"]["json"] = str(json_output)
        logger.info(f"JSON written to: {json_output}")

        # Write Markdown report
        md_output = REPORTS_DIR / "ACCURACY_TRACKER_365.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Live Accuracy Tracker - Phase 365\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            f.write(f"## Overall Accuracy: {overall_accuracy:.2f}%\n\n")
            f.write(f"**Total Signals Analyzed:** {len(df)}\n\n")

            f.write("---\n\n")
            f.write("## Hit Rates by Signal Type\n\n")

            if hit_rates and not hit_rates.get("error"):
                f.write("| Signal Type | Count | Hits | Hit Rate | Avg Return | Med Return |\n")
                f.write("|-------------|-------|------|----------|------------|------------|\n")

                for signal_type, metrics in sorted(hit_rates.items(), key=lambda x: x[1]["hit_rate_pct"], reverse=True):
                    f.write(
                        f"| {signal_type} | {metrics['count']} | {metrics['hits']} | "
                        f"{metrics['hit_rate_pct']:.2f}% | {metrics['avg_return']:.4f} | "
                        f"{metrics['median_return']:.4f} |\n"
                    )
                f.write("\n")
            else:
                f.write(f"*{hit_rates.get('error', 'No data available')}*\n\n")

            f.write("---\n\n")
            f.write("## Performance by Underlying Symbol\n\n")

            if symbol_performance and not symbol_performance.get("error"):
                f.write("| Symbol | Count | Wins | Losses | Win Rate | Avg Return | Total Return |\n")
                f.write("|--------|-------|------|--------|----------|------------|-------------|\n")

                for symbol, metrics in sorted(
                    symbol_performance.items(), key=lambda x: x[1]["win_rate_pct"], reverse=True
                ):
                    f.write(
                        f"| {symbol} | {metrics['count']} | {metrics['wins']} | "
                        f"{metrics['losses']} | {metrics['win_rate_pct']:.2f}% | "
                        f"{metrics['avg_return']:.4f} | {metrics['total_return']:.4f} |\n"
                    )
                f.write("\n")
            else:
                f.write(f"*{symbol_performance.get('error', 'No data available')}*\n\n")

            f.write("---\n\n")
            f.write("## Time Window Performance\n\n")

            if not time_windows.get("error"):
                f.write(f"**All Time:** {time_windows.get('all_time', 0)} signals\n")
                f.write(f"**Today:** {time_windows.get('today', 0)} signals\n")
                f.write(f"**Last 7 Days:** {time_windows.get('last_7_days', 0)} signals\n")
                f.write(f"**Last 30 Days:** {time_windows.get('last_30_days', 0)} signals\n\n")
            else:
                f.write(f"*{time_windows.get('error', 'No timestamp data available')}*\n\n")

            f.write("---\n\n")
            f.write("## Virtual Orders PnL\n\n")

            if virtual_pnl.get("status") == "ok":
                pnl_data = virtual_pnl["data"]
                f.write(f"**Total Orders:** {pnl_data.get('total_orders', 0)}\n")

                if "total_pnl" in pnl_data:
                    f.write(f"**Total PnL:** ₹{pnl_data['total_pnl']:.2f}\n")
                    f.write(f"**Avg PnL per Trade:** ₹{pnl_data['avg_pnl_per_trade']:.2f}\n")
                    f.write(f"**Max PnL:** ₹{pnl_data['max_pnl']:.2f}\n")
                    f.write(f"**Min PnL:** ₹{pnl_data['min_pnl']:.2f}\n\n")
                else:
                    f.write("*PnL columns not found in virtual orders file*\n\n")
            else:
                f.write(f"*{virtual_pnl.get('message', 'Not available')}*\n\n")

            f.write("---\n\n")
            f.write(
                f"**Recommendation:** {'Model performance is acceptable' if overall_accuracy >= 55 else 'Consider model retraining or threshold adjustment'}\n"
            )

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Report written to: {md_output}")

        logger.info(f"Phase 365 complete: overall_accuracy={overall_accuracy:.2f}%")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 365 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    result = run_phase365()

    print("\n" + "=" * 60)
    print("PHASE 365 - LIVE ACCURACY TRACKER")
    print("=" * 60)
    print(f"Status: {result['status'].upper()}")
    print(f"Overall Accuracy: {result.get('overall_accuracy', 'N/A')}%")
    print(f"Total Signals: {result.get('total_signals_analyzed', 0)}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    print("=" * 60)


if __name__ == "__main__":
    main()
