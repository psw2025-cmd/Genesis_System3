"""
System3 Phase 308 - Daily PnL & Accuracy Dashboard Generator (Research View)

Produces a single daily dashboard summarizing PnL-like metrics, accuracy, and confidence tiers.
"""

import sys
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

SIGNALS_WITH_FORWARD_CSV = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"
CONFIDENCE_TAGGED_CSV = STORAGE_LIVE / "angel_index_ai_signals_confidence_tagged_305.csv"
PERFORMANCE_301_JSON = STORAGE_META / "system3_daily_performance_301.json"
REGIME_302_JSON = STORAGE_META / "system3_regime_performance_302.json"
CONSISTENCY_307_JSON = STORAGE_META / "system3_live_vs_test_consistency_307.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_daily_dashboard_308.md"
DASHBOARD_JSON = STORAGE_META / "system3_daily_dashboard_308.json"


def load_csv_robust(path: Path) -> pd.DataFrame:
    """Load CSV with robust error handling."""
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, engine="python", on_bad_lines="skip")
    except Exception:
        return pd.DataFrame()


def load_json_safe(path: Path) -> Dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def run_phase308(**kwargs) -> Dict[str, Any]:
    """Run Phase 308: Daily PnL & Accuracy Dashboard Generator."""
    errors = []

    try:
        # Load all inputs
        df_signals = load_csv_robust(SIGNALS_WITH_FORWARD_CSV)
        df_confidence = load_csv_robust(CONFIDENCE_TAGGED_CSV)
        perf_301 = load_json_safe(PERFORMANCE_301_JSON)
        regime_302 = load_json_safe(REGIME_302_JSON)
        consistency_307 = load_json_safe(CONSISTENCY_307_JSON)

        # Filter to last trading day
        if not df_signals.empty and "ts" in df_signals.columns:
            df_signals["ts"] = pd.to_datetime(df_signals["ts"], errors="coerce")
            df_signals = df_signals.dropna(subset=["ts"]).sort_values("ts")
            if len(df_signals) > 0:
                latest_date = df_signals["ts"].max().date()
                cutoff = pd.Timestamp.combine(latest_date, pd.Timestamp.min.time())
                df_signals = df_signals[df_signals["ts"] >= cutoff].copy()

        # Compute overall metrics
        dashboard_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "date": datetime.now().date().isoformat(),
        }

        # Overall hit rate
        if not df_signals.empty:
            buy_signals = df_signals[df_signals["pred_label"] == "BUY"]
            sell_signals = df_signals[df_signals["pred_label"] == "SELL"]

            # Find forward return columns
            fwd_cols = [
                col for col in df_signals.columns if "forward_return_1" in col.lower() or "fwd_ret_1" in col.lower()
            ]
            if fwd_cols:
                fwd_col = fwd_cols[0]
                buy_fwd = pd.to_numeric(buy_signals[fwd_col], errors="coerce").dropna()
                sell_fwd = pd.to_numeric(sell_signals[fwd_col], errors="coerce").dropna()

                buy_hit_rate = (buy_fwd > 0).sum() / len(buy_fwd) * 100 if len(buy_fwd) > 0 else 0.0
                sell_hit_rate = (sell_fwd > 0).sum() / len(sell_fwd) * 100 if len(sell_fwd) > 0 else 0.0

                dashboard_data["overall_hit_rate"] = {
                    "BUY": float(buy_hit_rate),
                    "SELL": float(sell_hit_rate),
                }

        # EV by underlying and signal type (from Phase 301)
        if perf_301:
            dashboard_data["ev_by_underlying"] = perf_301.get("metrics_by_underlying_label", [])
            dashboard_data["global_totals"] = perf_301.get("global_totals", {})

        # EV by confidence tier
        if not df_confidence.empty and "confidence_tier" in df_confidence.columns:
            ev_by_tier = {}
            for tier in ["HIGH", "MEDIUM", "LOW"]:
                df_tier = df_confidence[df_confidence["confidence_tier"] == tier]
                fwd_cols = [
                    col for col in df_tier.columns if "forward_return_1" in col.lower() or "fwd_ret_1" in col.lower()
                ]
                if fwd_cols:
                    fwd_col = fwd_cols[0]
                    fwd_returns = pd.to_numeric(df_tier[fwd_col], errors="coerce").dropna()
                    if len(fwd_returns) > 0:
                        ev_by_tier[tier] = float(fwd_returns.mean())
            dashboard_data["ev_by_confidence_tier"] = ev_by_tier

        # Consistency score (from Phase 307)
        if consistency_307:
            dashboard_data["consistency_score"] = consistency_307.get("match_rate", 0.0)

        # Regime performance summary (from Phase 302)
        if regime_302:
            dashboard_data["regime_summary"] = regime_302.get("regime_aggregates", {})

        # Generate dashboard report
        report_lines = [
            "# System3 Daily Dashboard\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Date**: {datetime.now().date()}\n\n",
        ]

        # Overall Hit Rate
        if "overall_hit_rate" in dashboard_data:
            report_lines.append("## Overall Hit Rate\n\n")
            report_lines.append(f"- **BUY**: {dashboard_data['overall_hit_rate']['BUY']:.1f}%\n")
            report_lines.append(f"- **SELL**: {dashboard_data['overall_hit_rate']['SELL']:.1f}%\n\n")

        # EV by Underlying
        if "ev_by_underlying" in dashboard_data:
            report_lines.append("## EV by Underlying & Signal Type\n\n")
            report_lines.append("| Underlying | Label | EV (Fwd1) | Hit Rate | Grade |\n")
            report_lines.append("|------------|-------|-----------|----------|-------|\n")

            for metric in dashboard_data["ev_by_underlying"][:20]:  # Limit to 20
                ev = metric.get("mean_fwd1", 0.0)
                hit = metric.get("hit_rate_fwd1", 0.0)
                grade = metric.get("grade", "N/A")
                report_lines.append(
                    f"| {metric['underlying']} | {metric['label']} | {ev:.4f} | {hit:.1f}% | {grade} |\n"
                )

        # EV by Confidence Tier
        if "ev_by_confidence_tier" in dashboard_data:
            report_lines.append("\n## EV by Confidence Tier\n\n")
            for tier, ev in dashboard_data["ev_by_confidence_tier"].items():
                report_lines.append(f"- **{tier}**: {ev:.4f}\n")

        # Consistency
        if "consistency_score" in dashboard_data:
            score = dashboard_data["consistency_score"]
            icon = "✅" if score > 0.9 else "⚠️" if score > 0.8 else "❌"
            report_lines.append(f"\n## Consistency Score\n\n{icon} **{score * 100:.1f}%**\n")

        # Regime Summary
        if "regime_summary" in dashboard_data:
            report_lines.append("\n## Regime Performance Summary\n\n")
            for regime, stats in dashboard_data["regime_summary"].items():
                strength = stats.get("regime_strength", "UNKNOWN")
                icon = "✅" if strength == "STRONG" else "⚠️" if strength == "MIXED" else "❌"
                report_lines.append(f"{icon} **{regime} Regime**: {strength}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        with DASHBOARD_JSON.open("w", encoding="utf-8") as f:
            json.dump(dashboard_data, f, indent=2)

        return {
            "phase": 308,
            "status": "OK",
            "details": "Daily dashboard generated",
            "outputs": {
                "report_file": str(REPORT_PATH),
                "json_file": str(DASHBOARD_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 308,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(DASHBOARD_JSON)},
            "errors": errors,
        }
