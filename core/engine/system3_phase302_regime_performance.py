"""
System3 Phase 302 - Regime-Aware Performance Profiler

Combines volatility regime info with Phase 301 metrics to see where the system performs best.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

REGIMES_CSV = STORAGE_META / "system3_vol_regimes.csv"
PERFORMANCE_301_JSON = STORAGE_META / "system3_daily_performance_301.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_regime_performance_302.md"
REGIME_PERF_JSON = STORAGE_META / "system3_regime_performance_302.json"


def load_csv_robust(path: Path) -> pd.DataFrame:
    """Load CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def run_phase302(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 302: Regime-Aware Performance Profiler.

    Returns:
        dict: PhaseResult with status, details, outputs, errors
    """
    errors = []

    try:
        # Load Phase 301 performance data
        if not PERFORMANCE_301_JSON.exists():
            return {
                "phase": 302,
                "status": "WARN",
                "details": "Phase 301 output not found",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(REGIME_PERF_JSON)},
                "errors": [],
            }

        with PERFORMANCE_301_JSON.open("r", encoding="utf-8") as f:
            perf_301 = json.load(f)

        # Load regime data
        regimes_df = load_csv_robust(REGIMES_CSV)

        if regimes_df.empty:
            return {
                "phase": 302,
                "status": "WARN",
                "details": "Regime CSV not found or empty",
                "outputs": {"report_file": str(REPORT_PATH), "json_file": str(REGIME_PERF_JSON)},
                "errors": [],
            }

        # Get latest regime per underlying
        if "date" in regimes_df.columns:
            regimes_df["date"] = pd.to_datetime(regimes_df["date"], errors="coerce")
            latest_date = regimes_df["date"].max()
            latest_regimes = regimes_df[regimes_df["date"] == latest_date].copy()
        else:
            latest_regimes = regimes_df.copy()

        # Join with Phase 301 metrics
        underlying_metrics = {}
        for metric in perf_301.get("metrics_by_underlying_label", []):
            underlying = metric["underlying"]
            if underlying not in underlying_metrics:
                underlying_metrics[underlying] = {
                    "underlying": underlying,
                    "regime": "UNKNOWN",
                    "metrics": [],
                }
            underlying_metrics[underlying]["metrics"].append(metric)

        # Attach regime to each underlying
        for underlying, data in underlying_metrics.items():
            regime_row = latest_regimes[latest_regimes["underlying"] == underlying]
            if not regime_row.empty:
                data["regime"] = regime_row.iloc[0].get("vol_regime", "UNKNOWN")

        # Aggregate by regime
        regime_stats = {"LOW": [], "NORMAL": [], "HIGH": []}
        for underlying, data in underlying_metrics.items():
            regime = data["regime"]
            if regime in regime_stats:
                regime_stats[regime].append(data)

        # Compute aggregate stats per regime
        regime_aggregates = {}
        for regime, items in regime_stats.items():
            if not items:
                continue

            buy_ev = []
            sell_ev = []
            buy_hit_rate = []
            sell_hit_rate = []

            for item in items:
                for metric in item["metrics"]:
                    if metric["label"] == "BUY":
                        if "mean_fwd1" in metric:
                            buy_ev.append(metric["mean_fwd1"])
                        if "hit_rate_fwd1" in metric:
                            buy_hit_rate.append(metric["hit_rate_fwd1"])
                    elif metric["label"] == "SELL":
                        if "mean_fwd1" in metric:
                            sell_ev.append(metric["mean_fwd1"])
                        if "hit_rate_fwd1" in metric:
                            sell_hit_rate.append(metric["hit_rate_fwd1"])

            avg_buy_ev = sum(buy_ev) / len(buy_ev) if buy_ev else 0.0
            avg_sell_ev = sum(sell_ev) / len(sell_ev) if sell_ev else 0.0
            avg_buy_hit = sum(buy_hit_rate) / len(buy_hit_rate) if buy_hit_rate else 0.0
            avg_sell_hit = sum(sell_hit_rate) / len(sell_hit_rate) if sell_hit_rate else 0.0

            # Determine regime strength
            if avg_buy_ev > 0.01 and avg_buy_hit > 55 and avg_sell_ev < -0.01 and avg_sell_hit > 55:
                strength = "STRONG"
            elif (avg_buy_ev > 0 or avg_sell_ev < 0) and (avg_buy_hit > 50 or avg_sell_hit > 50):
                strength = "MIXED"
            else:
                strength = "WEAK"

            regime_aggregates[regime] = {
                "avg_buy_ev": avg_buy_ev,
                "avg_sell_ev": avg_sell_ev,
                "avg_buy_hit_rate": avg_buy_hit,
                "avg_sell_hit_rate": avg_sell_hit,
                "regime_strength": strength,
            }

        # Generate report
        report_lines = [
            "# System3 Regime-Aware Performance Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        ]

        # Per-underlying table
        report_lines.append("## Performance by Underlying & Regime\n\n")
        report_lines.append("| Underlying | Regime | BUY EV | BUY Hit Rate | SELL EV | SELL Hit Rate |\n")
        report_lines.append("|------------|--------|--------|--------------|---------|---------------|\n")

        for underlying, data in underlying_metrics.items():
            buy_metrics = next((m for m in data["metrics"] if m["label"] == "BUY"), None)
            sell_metrics = next((m for m in data["metrics"] if m["label"] == "SELL"), None)

            buy_ev = buy_metrics.get("mean_fwd1", 0.0) if buy_metrics else 0.0
            buy_hit = buy_metrics.get("hit_rate_fwd1", 0.0) if buy_metrics else 0.0
            sell_ev = sell_metrics.get("mean_fwd1", 0.0) if sell_metrics else 0.0
            sell_hit = sell_metrics.get("hit_rate_fwd1", 0.0) if sell_metrics else 0.0

            report_lines.append(
                f"| {underlying} | {data['regime']} | {buy_ev:.4f} | {buy_hit:.1f}% | "
                f"{sell_ev:.4f} | {sell_hit:.1f}% |\n"
            )

        # Per-regime aggregates
        report_lines.append("\n## Regime-Level Aggregates\n\n")
        for regime, stats in regime_aggregates.items():
            report_lines.append(f"### {regime} Regime\n")
            report_lines.append(f"- **Regime Strength**: {stats['regime_strength']}\n")
            report_lines.append(f"- Average BUY EV: {stats['avg_buy_ev']:.4f}\n")
            report_lines.append(f"- Average BUY Hit Rate: {stats['avg_buy_hit_rate']:.1f}%\n")
            report_lines.append(f"- Average SELL EV: {stats['avg_sell_ev']:.4f}\n")
            report_lines.append(f"- Average SELL Hit Rate: {stats['avg_sell_hit_rate']:.1f}%\n\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        json_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "underlying_level": underlying_metrics,
            "regime_aggregates": regime_aggregates,
        }

        with REGIME_PERF_JSON.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        status = "OK" if len(underlying_metrics) > 0 else "WARN"
        details = f"Analyzed {len(underlying_metrics)} underlyings across {len(regime_aggregates)} regimes"

        return {
            "phase": 302,
            "status": status,
            "details": details,
            "outputs": {
                "underlyings_analyzed": len(underlying_metrics),
                "regimes_analyzed": len(regime_aggregates),
                "report_file": str(REPORT_PATH),
                "json_file": str(REGIME_PERF_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 302,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(REGIME_PERF_JSON)},
            "errors": errors,
        }
