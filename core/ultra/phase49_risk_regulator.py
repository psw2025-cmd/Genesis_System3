"""
System3 Ultra - Phase 49: Smart Risk Regulator (AI Suggestions Only)

AI-powered risk adjustment suggestions.
Read-only, no auto-apply. All suggestions must be manually reviewed.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 111
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_current_risk_params() -> Dict[str, Any]:
    """Load current risk parameters."""
    # Try to load from config
    config_path = CONFIG_DIR / "dhan_trade_config.json"
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Default risk parameters
    return {
        "min_confidence": 0.80,
        "min_abs_score": 0.30,
        "max_moneyness_pct": 5.0,
        "target_pct": 3.0,
        "stoploss_pct": 2.0,
        "max_trades_per_day": 10,
        "max_trades_per_underlying": 3,
    }


def load_performance_metrics() -> Dict[str, float]:
    """Load recent performance metrics."""
    # Try to load from PnL logs
    pnl_path = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_pnl_log.csv"
    if pnl_path.exists():
        try:
            df = pd.read_csv(pnl_path)
            if "pnl_pct" in df.columns and len(df) > 0:
                return {
                    "win_rate": len(df[df["pnl_pct"] > 0]) / len(df) if len(df) > 0 else 0.5,
                    "avg_pnl": df["pnl_pct"].mean() if len(df) > 0 else 0.0,
                    "total_trades": len(df),
                }
        except Exception:
            pass

    # Default metrics
    return {
        "win_rate": 0.60,
        "avg_pnl": 1.5,
        "total_trades": 0,
    }


def generate_risk_suggestions(current_params: Dict[str, Any], performance: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Generate AI-powered risk adjustment suggestions.

    Args:
        current_params: Current risk parameters
        performance: Recent performance metrics

    Returns:
        List of suggestion dicts
    """
    suggestions = []

    # Analyze win rate
    win_rate = performance.get("win_rate", 0.5)
    avg_pnl = performance.get("avg_pnl", 0.0)
    total_trades = performance.get("total_trades", 0)

    # Suggestion 1: Confidence threshold
    if win_rate < 0.55 and total_trades > 10:
        suggestions.append(
            {
                "parameter": "min_confidence",
                "current_value": current_params.get("min_confidence", 0.80),
                "suggested_value": min(0.90, current_params.get("min_confidence", 0.80) + 0.05),
                "reason": f"Win rate ({win_rate:.2%}) is below target. Increase confidence threshold to improve quality.",
                "priority": "MEDIUM",
                "impact": "REDUCE_TRADE_FREQUENCY",
            }
        )
    elif win_rate > 0.70 and total_trades < 5:
        suggestions.append(
            {
                "parameter": "min_confidence",
                "current_value": current_params.get("min_confidence", 0.80),
                "suggested_value": max(0.70, current_params.get("min_confidence", 0.80) - 0.05),
                "reason": f"Win rate ({win_rate:.2%}) is excellent but trade frequency is low. Slightly reduce threshold.",
                "priority": "LOW",
                "impact": "INCREASE_TRADE_FREQUENCY",
            }
        )

    # Suggestion 2: Score threshold
    if avg_pnl < 0.5 and total_trades > 10:
        suggestions.append(
            {
                "parameter": "min_abs_score",
                "current_value": current_params.get("min_abs_score", 0.30),
                "suggested_value": min(0.40, current_params.get("min_abs_score", 0.30) + 0.05),
                "reason": f"Average PnL ({avg_pnl:.2f}%) is low. Increase score threshold to focus on stronger signals.",
                "priority": "MEDIUM",
                "impact": "IMPROVE_QUALITY",
            }
        )

    # Suggestion 3: Position sizing (if applicable)
    if win_rate > 0.65 and avg_pnl > 1.0:
        suggestions.append(
            {
                "parameter": "max_trades_per_day",
                "current_value": current_params.get("max_trades_per_day", 10),
                "suggested_value": min(15, current_params.get("max_trades_per_day", 10) + 2),
                "reason": f"Performance is strong (win rate: {win_rate:.2%}, avg PnL: {avg_pnl:.2f}%). Consider increasing trade limit.",
                "priority": "LOW",
                "impact": "INCREASE_EXPOSURE",
            }
        )

    # Suggestion 4: Stop-loss adjustment
    if avg_pnl < -1.0:
        suggestions.append(
            {
                "parameter": "stoploss_pct",
                "current_value": current_params.get("stoploss_pct", 2.0),
                "suggested_value": max(1.5, current_params.get("stoploss_pct", 2.0) - 0.5),
                "reason": f"Average PnL is negative ({avg_pnl:.2f}%). Tighten stop-loss to limit losses.",
                "priority": "HIGH",
                "impact": "REDUCE_LOSSES",
            }
        )

    return suggestions


def run_phase49_risk_regulator() -> None:
    """Run Phase 49: Smart Risk Regulator."""
    print("=== SYSTEM3 ULTRA - PHASE 49: SMART RISK REGULATOR ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] AI Suggestions Only - No Auto-Apply\n")

    # Load current risk parameters
    current_params = load_current_risk_params()
    print(f"[LOAD] Current risk parameters loaded")

    # Load performance metrics
    performance = load_performance_metrics()
    print(f"[LOAD] Performance metrics loaded")
    print(f"  Win rate: {performance['win_rate']:.2%}")
    print(f"  Avg PnL: {performance['avg_pnl']:.2f}%")
    print(f"  Total trades: {performance['total_trades']}")

    # Generate suggestions
    suggestions = generate_risk_suggestions(current_params, performance)

    # Save suggestions
    suggestions_json = OUTPUT_DIR / "phase49_risk_suggestions.json"
    with suggestions_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "current_parameters": current_params,
                "performance_metrics": performance,
                "suggestions": suggestions,
                "generated_at": datetime.now().isoformat(),
                "note": "These are suggestions only. Manual review and approval required before applying.",
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Risk suggestions saved to: {suggestions_json}")

    # Generate analysis report
    analysis_md = OUTPUT_DIR / "phase49_risk_analysis.md"
    with analysis_md.open("w", encoding="utf-8") as f:
        f.write("# Phase 49: Risk Analysis Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
        f.write("## Current Risk Parameters\n\n")
        for param, value in current_params.items():
            f.write(f"- **{param}**: {value}\n")
        f.write("\n## Performance Metrics\n\n")
        for metric, value in performance.items():
            f.write(f"- **{metric}**: {value}\n")
        f.write("\n## AI Suggestions\n\n")
        if suggestions:
            for i, sug in enumerate(suggestions, 1):
                f.write(f"### Suggestion {i}: {sug['parameter']}\n\n")
                f.write(f"- **Current**: {sug['current_value']}\n")
                f.write(f"- **Suggested**: {sug['suggested_value']}\n")
                f.write(f"- **Priority**: {sug['priority']}\n")
                f.write(f"- **Impact**: {sug['impact']}\n")
                f.write(f"- **Reason**: {sug['reason']}\n\n")
        else:
            f.write("No suggestions at this time. Current parameters appear optimal.\n\n")
        f.write("\n## Important Note\n\n")
        f.write("**These are suggestions only. Manual review and approval required before applying any changes.**\n")
    print(f"[SAVE] Risk analysis report saved to: {analysis_md}")

    # Summary
    print(f"\n=== RISK REGULATOR SUMMARY ===")
    print(f"Suggestions generated: {len(suggestions)}")
    if suggestions:
        for i, sug in enumerate(suggestions, 1):
            print(f"\nSuggestion {i}: {sug['parameter']}")
            print(f"  Current: {sug['current_value']}")
            print(f"  Suggested: {sug['suggested_value']}")
            print(f"  Priority: {sug['priority']}")
            print(f"  Reason: {sug['reason']}")
    else:
        print("No suggestions - current parameters appear optimal")

    print("\n[OK] Phase 49 Smart Risk Regulator completed")
    print("[NOTE] Suggestions saved. Manual review required before applying.")


def main() -> None:
    """Main entry point."""
    run_phase49_risk_regulator()


if __name__ == "__main__":
    main()
