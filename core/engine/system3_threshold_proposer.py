#!/usr/bin/env python3
"""
System3 Threshold Proposer
Automatically proposes BUY/SELL thresholds based on EV tables from Phase 222.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

THRESHOLD_CANDIDATES_JSON = STORAGE_META / "system3_threshold_candidates.json"
THRESHOLD_OPTIMIZER_LOG = PROJECT_ROOT / "logs" / "research" / "system3_threshold_optimizer.log"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_ev_tables_from_report(report_path: Path) -> List[Dict[str, Any]]:
    """Load EV tables from Phase 222 report."""
    ev_tables = []

    if not report_path.exists():
        return ev_tables

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse markdown table format
        lines = content.split("\n")
        current_underlying = None
        current_horizon = None

        for line in lines:
            line = line.strip()

            # Detect underlying section
            if line.startswith("## ") and not line.startswith("###"):
                current_underlying = line.replace("## ", "").strip()

            # Detect horizon section
            elif line.startswith("### Forward Return Horizon:"):
                horizon_match = line.split(":")[1].strip().split()[0]
                current_horizon = horizon_match

            # Parse table rows
            elif line.startswith("|") and "Score Bin" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 4:
                    score_bin = parts[0]
                    avg_return = float(parts[1]) if parts[1] else 0.0
                    trade_count = int(parts[2]) if parts[2].isdigit() else 0
                    hit_rate = float(parts[3].replace("%", "")) if parts[3] else 0.0

                    if current_underlying and current_horizon:
                        ev_tables.append(
                            {
                                "underlying": current_underlying,
                                "horizon": current_horizon,
                                "score_bin": score_bin,
                                "avg_forward_return": avg_return,
                                "trade_count": trade_count,
                                "hit_rate": hit_rate,
                            }
                        )
    except Exception as e:
        print(f"[WARN] Failed to parse EV report: {e}")

    return ev_tables


def propose_thresholds(ev_tables: List[Dict[str, Any]], min_samples: int = 20) -> Dict[str, Any]:
    """
    Propose thresholds based on EV tables.

    Criteria:
    - BUY: Score bins with positive avg_forward_return and sufficient samples
    - SELL: Score bins with negative avg_forward_return and sufficient samples
    """
    proposals = {
        "global": {"buy": 0.40, "sell": -0.40},  # Defaults
        "per_underlying": {},
        "candidates": [],
    }

    # Group by underlying
    by_underlying = {}
    for ev in ev_tables:
        underlying = ev["underlying"]
        if underlying not in by_underlying:
            by_underlying[underlying] = []
        by_underlying[underlying].append(ev)

    # Propose per-underlying thresholds
    for underlying, evs in by_underlying.items():
        # Filter to horizon 1 (most immediate)
        horizon1_evs = [e for e in evs if e["horizon"] == "1"]

        if not horizon1_evs:
            continue

        # Helper to parse bin start value
        def get_bin_start(bin_str):
            try:
                return float(str(bin_str).split(",")[0].replace("[", "").replace("(", ""))
            except:
                return 0.0

        # Helper to parse bin end value
        def get_bin_end(bin_str):
            try:
                return float(str(bin_str).split(",")[1].replace(")", "").replace("]", ""))
            except:
                return 0.0

        # Find best BUY bin (positive return, sufficient samples)
        # First try: bins starting at >= 0.0 (positive scores only)
        buy_candidates_strict = [
            e
            for e in horizon1_evs
            if e["avg_forward_return"] > 0 and e["trade_count"] >= min_samples and get_bin_start(e["score_bin"]) >= 0.0
        ]

        # Fallback: if no strict candidates, use any bin with positive return and good hit-rate
        if not buy_candidates_strict:
            buy_candidates_fallback = [
                e
                for e in horizon1_evs
                if e["avg_forward_return"] > 0
                and e["trade_count"] >= min_samples
                and e.get("hit_rate", 0) >= 45.0  # At least 45% hit rate
            ]
            buy_candidates = buy_candidates_fallback
        else:
            buy_candidates = buy_candidates_strict

        # Find best SELL bin (negative return, sufficient samples)
        # First try: bins ending at <= 0.0 (negative scores only)
        sell_candidates_strict = [
            e
            for e in horizon1_evs
            if e["avg_forward_return"] < 0 and e["trade_count"] >= min_samples and get_bin_end(e["score_bin"]) <= 0.0
        ]

        # Fallback: if no strict candidates, use any bin with negative return
        if not sell_candidates_strict:
            sell_candidates_fallback = [
                e for e in horizon1_evs if e["avg_forward_return"] < 0 and e["trade_count"] >= min_samples
            ]
            sell_candidates = sell_candidates_fallback
        else:
            sell_candidates = sell_candidates_strict

        if buy_candidates:
            # Use the bin with best combination of return and hit-rate
            # Prefer bins starting at >= 0.0, but if none exist, use the best available
            best_buy = max(
                buy_candidates,
                key=lambda x: (
                    get_bin_start(x["score_bin"]) >= 0.0,  # Prefer positive start
                    x["avg_forward_return"] * x["trade_count"],  # Weight by return * count
                    x.get("hit_rate", 0),
                ),
            )
            buy_threshold = max(0.0, get_bin_start(best_buy["score_bin"]))
            # Ensure minimum reasonable threshold
            if buy_threshold < 0.05:
                buy_threshold = 0.10  # Minimum reasonable threshold
        else:
            buy_threshold = 0.40  # Default

        if sell_candidates:
            # Use the bin with best (most negative) return
            best_sell = min(
                sell_candidates,
                key=lambda x: (
                    x["avg_forward_return"],  # Most negative return
                    -x["trade_count"],  # More samples is better
                ),
            )
            sell_threshold = min(0.0, get_bin_end(best_sell["score_bin"]))
            # Ensure maximum reasonable threshold (most negative)
            if sell_threshold > -0.05:
                sell_threshold = -0.10  # Minimum reasonable threshold
        else:
            sell_threshold = -0.40  # Default

        proposals["per_underlying"][underlying] = {
            "buy": buy_threshold,
            "sell": sell_threshold,
        }

        proposals["candidates"].append(
            {
                "underlying": underlying,
                "buy_threshold": buy_threshold,
                "sell_threshold": sell_threshold,
                "buy_count": sum(e["trade_count"] for e in buy_candidates),
                "sell_count": sum(e["trade_count"] for e in sell_candidates),
                "buy_avg_return": (
                    sum(e["avg_forward_return"] * e["trade_count"] for e in buy_candidates)
                    / sum(e["trade_count"] for e in buy_candidates)
                    if buy_candidates
                    else 0.0
                ),
                "sell_avg_return": (
                    sum(e["avg_forward_return"] * e["trade_count"] for e in sell_candidates)
                    / sum(e["trade_count"] for e in sell_candidates)
                    if sell_candidates
                    else 0.0
                ),
            }
        )

    # Compute global thresholds (average of per-underlying if available)
    if proposals["per_underlying"]:
        avg_buy = sum(v["buy"] for v in proposals["per_underlying"].values()) / len(proposals["per_underlying"])
        avg_sell = sum(v["sell"] for v in proposals["per_underlying"].values()) / len(proposals["per_underlying"])
        proposals["global"] = {"buy": avg_buy, "sell": avg_sell}

    return proposals


def save_threshold_proposals(proposals: Dict[str, Any]) -> None:
    """Save threshold proposals to JSON files."""
    # Save to candidates file (for compatibility)
    output_candidates = {
        "candidates": proposals["candidates"],
        "generated": datetime.now().isoformat(),
        "optimization_objective": "hit_rate",
    }

    with open(THRESHOLD_CANDIDATES_JSON, "w", encoding="utf-8") as f:
        json.dump(output_candidates, f, indent=2)

    # Save to live_thresholds.json (new format for signal engine)
    output_live = {
        "global": proposals["global"],
        "per_underlying": proposals["per_underlying"],
        "generated": datetime.now().isoformat(),
        "source": "phase_222_ev_analysis",
    }

    live_thresholds_path = PROJECT_ROOT / "storage" / "meta" / "system3_live_thresholds.json"
    with open(live_thresholds_path, "w", encoding="utf-8") as f:
        json.dump(output_live, f, indent=2)


def generate_threshold_log(proposals: Dict[str, Any]) -> None:
    """Generate markdown summary log."""
    with open(THRESHOLD_OPTIMIZER_LOG, "w", encoding="utf-8") as f:
        f.write("# System3 Threshold Optimizer Summary\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Global Thresholds\n\n")
        f.write(f"- **BUY Threshold**: {proposals['global']['buy']:.3f}\n")
        f.write(f"- **SELL Threshold**: {proposals['global']['sell']:.3f}\n\n")

        if proposals["per_underlying"]:
            f.write("## Per-Underlying Thresholds\n\n")
            f.write("| Underlying | BUY Threshold | SELL Threshold |\n")
            f.write("|------------|---------------|----------------|\n")
            for underlying, thresh in sorted(proposals["per_underlying"].items()):
                f.write(f"| {underlying} | {thresh['buy']:.3f} | {thresh['sell']:.3f} |\n")
            f.write("\n")

        if proposals["candidates"]:
            f.write("## EV Metrics Used\n\n")
            f.write(
                "| Underlying | BUY Threshold | SELL Threshold | BUY Count | SELL Count | BUY Avg Return | SELL Avg Return |\n"
            )
            f.write(
                "|------------|---------------|----------------|-----------|------------|----------------|-----------------|\n"
            )
            for cand in proposals["candidates"]:
                f.write(
                    f"| {cand['underlying']} | {cand['buy_threshold']:.3f} | {cand['sell_threshold']:.3f} | "
                    f"{cand['buy_count']} | {cand['sell_count']} | {cand['buy_avg_return']:.4f} | {cand['sell_avg_return']:.4f} |\n"
                )


def main():
    """Main entry point."""
    print("=" * 80)
    print("SYSTEM3 THRESHOLD PROPOSER")
    print("=" * 80)
    print()

    # Load EV tables from Phase 222 report
    report_path = LOG_DIR / "system3_signal_edge_report.md"
    ev_tables = load_ev_tables_from_report(report_path)

    if not ev_tables:
        print("[WARN] No EV tables found. Run Phase 222 first.")
        return 1

    print(f"Loaded {len(ev_tables)} EV table entries")

    # Propose thresholds
    proposals = propose_thresholds(ev_tables, min_samples=20)

    # Save proposals
    save_threshold_proposals(proposals)
    generate_threshold_log(proposals)

    print("\nThreshold Proposals:")
    print(f"Global: BUY >= {proposals['global']['buy']:.3f}, SELL <= {proposals['global']['sell']:.3f}")

    if proposals["per_underlying"]:
        print("\nPer-Underlying:")
        for underlying, thresh in sorted(proposals["per_underlying"].items()):
            print(f"  {underlying}: BUY >= {thresh['buy']:.3f}, SELL <= {thresh['sell']:.3f}")

    print(f"\nSaved to: {THRESHOLD_CANDIDATES_JSON}")
    print(f"Log: {THRESHOLD_OPTIMIZER_LOG}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
