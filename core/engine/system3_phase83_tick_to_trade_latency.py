"""
System3 Phase 83 - Tick-to-Trade Latency Monitor

Measure total real-time latency from market snapshot time to trade decision timestamp.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from dateutil import parser as date_parser

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

# Input files
TRADES_PLAN_CSV = STORAGE_LIVE / "dhan_index_ai_trades_plan.csv"
PNL_LOG_CSV = STORAGE_LIVE / "dhan_index_ai_pnl_log.csv"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase83_tick_to_trade_latency.json"
OUTPUT_MD = STORAGE_ULTRA / "phase83_tick_to_trade_latency.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

LATENCY_THRESHOLD_MS = 500.0  # 500ms threshold


def load_data() -> Dict[str, pd.DataFrame]:
    """Load trade plan and PnL data."""
    data = {}

    if TRADES_PLAN_CSV.exists():
        try:
            data["trades"] = pd.read_csv(TRADES_PLAN_CSV)
        except Exception as e:
            print(f"[PH83] Error loading trades: {e}")
            data["trades"] = pd.DataFrame()
    else:
        data["trades"] = pd.DataFrame()

    if PNL_LOG_CSV.exists():
        try:
            data["pnl"] = pd.read_csv(PNL_LOG_CSV)
        except Exception as e:
            print(f"[PH83] Error loading PnL: {e}")
            data["pnl"] = pd.DataFrame()
    else:
        data["pnl"] = pd.DataFrame()

    return data


def compute_latency_ms(snapshot_ts: str, decision_ts: str) -> Optional[float]:
    """Compute latency in milliseconds between two timestamps."""
    try:
        snapshot_dt = date_parser.parse(snapshot_ts)
        decision_dt = date_parser.parse(decision_ts)
        delta = (decision_dt - snapshot_dt).total_seconds() * 1000.0
        return delta
    except Exception:
        return None


def analyze_latency() -> Dict[str, Any]:
    """Analyze tick-to-trade latency."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 83 - TICK-TO-TRADE LATENCY MONITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load data
    data = load_data()
    trades_df = data["trades"]
    pnl_df = data["pnl"]

    if trades_df.empty and pnl_df.empty:
        print("[PH83] No trade data found. Creating empty report.")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {},
            "per_underlying": {},
        }

    # Use PnL if available (has both timestamps), else trades
    source_df = pnl_df if not pnl_df.empty else trades_df

    latencies = []
    per_underlying_latencies = {}

    for idx, row in source_df.iterrows():
        # Try to get timestamps (may be in different columns)
        snapshot_ts = row.get("ts", row.get("snapshot_ts", ""))
        decision_ts = row.get("ts", row.get("decision_ts", ""))

        if snapshot_ts and decision_ts:
            latency = compute_latency_ms(snapshot_ts, decision_ts)
            if latency is not None:
                latencies.append(latency)

                underlying = row.get("underlying", "UNKNOWN")
                if underlying not in per_underlying_latencies:
                    per_underlying_latencies[underlying] = []
                per_underlying_latencies[underlying].append(latency)

    # Aggregate overall
    if latencies:
        overall = {
            "mean_ms": float(np.mean(latencies)),
            "median_ms": float(np.median(latencies)),
            "p95_ms": float(np.percentile(latencies, 95)),
            "p99_ms": float(np.percentile(latencies, 99)),
            "count": len(latencies),
        }
    else:
        overall = {
            "mean_ms": 0.0,
            "median_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "count": 0,
        }

    # Aggregate per underlying
    per_underlying = {}
    for underlying, values in per_underlying_latencies.items():
        per_underlying[underlying] = {
            "mean_ms": float(np.mean(values)),
            "median_ms": float(np.median(values)),
            "p95_ms": float(np.percentile(values, 95)),
            "p99_ms": float(np.percentile(values, 99)),
            "count": len(values),
        }

    report = {
        "timestamp": datetime.now().isoformat(),
        "overall": overall,
        "per_underlying": per_underlying,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH83] Tick-to-trade latency summary saved to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH83] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 83 - Tick-to-Trade Latency Report\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        # Overall metrics
        overall = report["overall"]
        f.write("## Overall Metrics\n\n")
        f.write(f"- **Mean**: {overall['mean_ms']:.2f} ms\n")
        f.write(f"- **Median**: {overall['median_ms']:.2f} ms\n")
        f.write(f"- **P95**: {overall['p95_ms']:.2f} ms\n")
        f.write(f"- **P99**: {overall['p99_ms']:.2f} ms\n")
        f.write(f"- **Count**: {overall['count']}\n\n")

        # Classification
        mean_latency = overall["mean_ms"]
        if mean_latency < LATENCY_THRESHOLD_MS:
            f.write(f"**Status**: ✅ OK (mean latency {mean_latency:.2f}ms < {LATENCY_THRESHOLD_MS}ms threshold)\n\n")
        else:
            f.write(f"**Status**: ⚠️ HIGH (mean latency {mean_latency:.2f}ms >= {LATENCY_THRESHOLD_MS}ms threshold)\n\n")

        # Per underlying table
        if report["per_underlying"]:
            f.write("## Per Underlying Metrics\n\n")
            f.write("| Underlying | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Count |\n")
            f.write("|------------|-----------|-------------|----------|----------|-------|\n")

            for underlying, stats in sorted(report["per_underlying"].items()):
                f.write(
                    f"| {underlying} | {stats['mean_ms']:.2f} | {stats['median_ms']:.2f} | "
                    f"{stats['p95_ms']:.2f} | {stats['p99_ms']:.2f} | {stats['count']} |\n"
                )


def main():
    """Main entry point."""
    try:
        report = analyze_latency()
        print("\n[PH83] Tick-to-trade latency analysis complete.")
        return 0
    except Exception as e:
        print(f"\n[PH83] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
