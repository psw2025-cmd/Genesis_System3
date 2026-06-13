"""
System3 Phase 301 - Daily Live-vs-Forward Performance Tracker

Converts recent signals + forward returns into real, money-like metrics per underlying and signal type.
"""

import sys
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

SIGNALS_WITH_FORWARD_CSV = STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_daily_live_vs_forward_report.md"
PERFORMANCE_JSON = STORAGE_META / "system3_daily_performance_301.json"

MIN_ROWS = 200


def load_signals_robust(path: Path) -> pd.DataFrame:
    """Load signals CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()

    try:
        df = pd.read_csv(path)
    except Exception:
        try:
            df = pd.read_csv(path, engine="python", on_bad_lines="skip")
        except Exception as e:
            return pd.DataFrame()

    return df


def get_recent_window(df: pd.DataFrame, hours: int = 24) -> pd.DataFrame:
    """Filter to recent window (last N hours or last trading day)."""
    if df.empty or "ts" not in df.columns:
        return df

    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df = df.dropna(subset=["ts"]).sort_values("ts")

    if len(df) == 0:
        return df

    # Get last trading day (most recent date)
    latest_date = df["ts"].max().date()
    cutoff = pd.Timestamp.combine(latest_date, pd.Timestamp.min.time())

    return df[df["ts"] >= cutoff].copy()


def compute_metrics(df: pd.DataFrame, underlying: str, label: str, horizons: List[int]) -> Dict[str, Any]:
    """Compute metrics for a specific underlying and label combination."""
    subset = df[(df["underlying"] == underlying) & (df["pred_label"] == label)].copy()

    if len(subset) == 0:
        return None

    metrics = {
        "underlying": underlying,
        "label": label,
        "count": len(subset),
    }

    # Compute metrics for each horizon
    for h in horizons:
        fwd_cols = [
            col for col in subset.columns if f"forward_return_{h}" in col.lower() or f"fwd_ret_{h}" in col.lower()
        ]
        if not fwd_cols:
            continue

        fwd_col = fwd_cols[0]
        fwd_returns = pd.to_numeric(subset[fwd_col], errors="coerce").dropna()

        if len(fwd_returns) == 0:
            continue

        metrics[f"mean_fwd{h}"] = float(fwd_returns.mean())
        metrics[f"median_fwd{h}"] = float(fwd_returns.median())
        metrics[f"hit_rate_fwd{h}"] = float((fwd_returns > 0).sum() / len(fwd_returns) * 100)
        metrics[f"worst_fwd{h}"] = float(fwd_returns.min())
        metrics[f"best_fwd{h}"] = float(fwd_returns.max())

    # Compute grade based on EV and hit rate
    mean_ev = metrics.get("mean_fwd1", 0.0) if "mean_fwd1" in metrics else 0.0
    hit_rate = metrics.get("hit_rate_fwd1", 0.0) if "hit_rate_fwd1" in metrics else 0.0

    if mean_ev > 0.01 and hit_rate > 55:
        metrics["grade"] = "GOOD"
    elif mean_ev > 0 and hit_rate > 50:
        metrics["grade"] = "NEUTRAL"
    else:
        metrics["grade"] = "POOR"

    return metrics


def run_phase301(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 301: Daily Live-vs-Forward Performance Tracker.

    Returns:
        dict: {
            "phase": 301,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "rows_processed": int,
                "underlyings_analyzed": int,
                "report_file": str,
                "json_file": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load signals with forward returns
        df = load_signals_robust(SIGNALS_WITH_FORWARD_CSV)

        if len(df) < MIN_ROWS:
            return {
                "phase": 301,
                "status": "WARN",
                "details": f"Insufficient data: {len(df)} rows (min {MIN_ROWS} required)",
                "outputs": {
                    "rows_processed": len(df),
                    "underlyings_analyzed": 0,
                    "report_file": str(REPORT_PATH),
                    "json_file": str(PERFORMANCE_JSON),
                },
                "errors": [],
            }

        # Filter to recent window
        df_recent = get_recent_window(df)

        if len(df_recent) == 0:
            return {
                "phase": 301,
                "status": "WARN",
                "details": "No recent data in window",
                "outputs": {
                    "rows_processed": len(df),
                    "underlyings_analyzed": 0,
                    "report_file": str(REPORT_PATH),
                    "json_file": str(PERFORMANCE_JSON),
                },
                "errors": [],
            }

        # Check required columns
        required_cols = ["underlying", "pred_label"]
        missing_cols = [col for col in required_cols if col not in df_recent.columns]
        if missing_cols:
            return {
                "phase": 301,
                "status": "WARN",
                "details": f"Missing required columns: {missing_cols}",
                "outputs": {
                    "rows_processed": len(df_recent),
                    "underlyings_analyzed": 0,
                    "report_file": str(REPORT_PATH),
                    "json_file": str(PERFORMANCE_JSON),
                },
                "errors": missing_cols,
            }

        # Filter to BUY and SELL only
        df_signals = df_recent[df_recent["pred_label"].isin(["BUY", "SELL"])].copy()

        if len(df_signals) == 0:
            return {
                "phase": 301,
                "status": "WARN",
                "details": "No BUY/SELL signals in recent window",
                "outputs": {
                    "rows_processed": len(df_recent),
                    "underlyings_analyzed": 0,
                    "report_file": str(REPORT_PATH),
                    "json_file": str(PERFORMANCE_JSON),
                },
                "errors": [],
            }

        # Find forward return columns
        horizons = [1, 3, 5]
        fwd_cols_found = []
        for h in horizons:
            for col in df_signals.columns:
                if f"forward_return_{h}" in col.lower() or f"fwd_ret_{h}" in col.lower():
                    fwd_cols_found.append(h)
                    break

        if not fwd_cols_found:
            # Try alternative naming
            for col in df_signals.columns:
                if "forward" in col.lower() and "return" in col.lower():
                    # Try to extract horizon number
                    import re

                    match = re.search(r"(\d+)", col)
                    if match:
                        fwd_cols_found.append(int(match.group(1)))

        if not fwd_cols_found:
            horizons = [1, 3, 5]  # Use defaults even if columns not found

        # Compute metrics per underlying × label
        all_metrics = []
        underlyings = df_signals["underlying"].unique()

        for underlying in underlyings:
            for label in ["BUY", "SELL"]:
                metrics = compute_metrics(df_signals, underlying, label, horizons)
                if metrics:
                    all_metrics.append(metrics)

        # Aggregate global totals
        global_buy = df_signals[df_signals["pred_label"] == "BUY"]
        global_sell = df_signals[df_signals["pred_label"] == "SELL"]

        global_metrics = {
            "BUY": {
                "count": len(global_buy),
            },
            "SELL": {
                "count": len(global_sell),
            },
        }

        # Compute global forward return metrics
        for label, df_label in [("BUY", global_buy), ("SELL", global_sell)]:
            for h in horizons:
                fwd_cols = [
                    col
                    for col in df_label.columns
                    if f"forward_return_{h}" in col.lower() or f"fwd_ret_{h}" in col.lower()
                ]
                if fwd_cols:
                    fwd_col = fwd_cols[0]
                    fwd_returns = pd.to_numeric(df_label[fwd_col], errors="coerce").dropna()
                    if len(fwd_returns) > 0:
                        global_metrics[label][f"mean_fwd{h}"] = float(fwd_returns.mean())
                        global_metrics[label][f"hit_rate_fwd{h}"] = float(
                            (fwd_returns > 0).sum() / len(fwd_returns) * 100
                        )

        # Generate report
        report_lines = [
            "# System3 Daily Live-vs-Forward Performance Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Rows Processed**: {len(df_recent)}\n",
            f"**Signals Analyzed**: {len(df_signals)} (BUY/SELL only)\n",
            f"**Underlyings**: {len(underlyings)}\n\n",
        ]

        # Per-underlying table
        report_lines.append("## Performance by Underlying & Label\n\n")
        report_lines.append(
            "| Underlying | Label | Count | Hit Rate (Fwd1) | Hit Rate (Fwd3) | Mean Fwd1 | Mean Fwd3 | Grade |\n"
        )
        report_lines.append(
            "|------------|-------|-------|------------------|------------------|-----------|-----------|-------|\n"
        )

        for metrics in all_metrics:
            hit1 = metrics.get("hit_rate_fwd1", 0.0)
            hit3 = metrics.get("hit_rate_fwd3", 0.0)
            mean1 = metrics.get("mean_fwd1", 0.0)
            mean3 = metrics.get("mean_fwd3", 0.0)
            report_lines.append(
                f"| {metrics['underlying']} | {metrics['label']} | {metrics['count']} | "
                f"{hit1:.1f}% | {hit3:.1f}% | {mean1:.4f} | {mean3:.4f} | {metrics.get('grade', 'N/A')} |\n"
            )

        # Global totals
        report_lines.append("\n## Global Totals\n\n")
        report_lines.append("### BUY Signals\n")
        report_lines.append(f"- Count: {global_metrics['BUY']['count']}\n")
        for h in horizons:
            if f"mean_fwd{h}" in global_metrics["BUY"]:
                report_lines.append(f"- Mean Forward Return ({h}): {global_metrics['BUY'][f'mean_fwd{h}']:.4f}\n")
                report_lines.append(f"- Hit Rate ({h}): {global_metrics['BUY'][f'hit_rate_fwd{h}']:.1f}%\n")

        report_lines.append("\n### SELL Signals\n")
        report_lines.append(f"- Count: {global_metrics['SELL']['count']}\n")
        for h in horizons:
            if f"mean_fwd{h}" in global_metrics["SELL"]:
                report_lines.append(f"- Mean Forward Return ({h}): {global_metrics['SELL'][f'mean_fwd{h}']:.4f}\n")
                report_lines.append(f"- Hit Rate ({h}): {global_metrics['SELL'][f'hit_rate_fwd{h}']:.1f}%\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        json_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "rows_processed": len(df_recent),
            "signals_analyzed": len(df_signals),
            "underlyings": list(underlyings),
            "metrics_by_underlying_label": all_metrics,
            "global_totals": global_metrics,
        }

        with PERFORMANCE_JSON.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        status = "OK" if len(all_metrics) > 0 else "WARN"
        details = f"Processed {len(df_recent)} rows, analyzed {len(all_metrics)} combinations"

        return {
            "phase": 301,
            "status": status,
            "details": details,
            "outputs": {
                "rows_processed": len(df_recent),
                "underlyings_analyzed": len(underlyings),
                "combinations_analyzed": len(all_metrics),
                "report_file": str(REPORT_PATH),
                "json_file": str(PERFORMANCE_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 301,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {
                "rows_processed": 0,
                "underlyings_analyzed": 0,
                "report_file": str(REPORT_PATH),
                "json_file": str(PERFORMANCE_JSON),
            },
            "errors": errors,
        }
