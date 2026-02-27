"""
System3 Phase 80 - GENI Evolution Status

Create a high-level evolution status overview describing how GENI should evolve
(more aggressive, more conservative, feature focus, etc.).
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Input files (Phase 76-79 outputs)
PHASE76_JSON = STORAGE_ULTRA / "phase76_geni_self_review.json"
PHASE77_JSON = STORAGE_ULTRA / "phase77_geni_self_corrections.json"
PHASE78_PARQUET = STORAGE_ULTRA / "phase78_geni_consensus.parquet"
PHASE79_JSON = STORAGE_ULTRA / "phase79_adaptive_thresholds.json"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase80_geni_evolution_status.json"
OUTPUT_MD = STORAGE_ULTRA / "phase80_geni_evolution_status.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_phase_outputs() -> Dict[str, Any]:
    """Load outputs from phases 76-79."""
    outputs = {}

    if PHASE76_JSON.exists():
        try:
            with PHASE76_JSON.open("r", encoding="utf-8") as f:
                outputs["phase76"] = json.load(f)
        except Exception as e:
            print(f"[PH80] Error loading Phase 76: {e}")
            outputs["phase76"] = {}
    else:
        outputs["phase76"] = {}

    if PHASE77_JSON.exists():
        try:
            with PHASE77_JSON.open("r", encoding="utf-8") as f:
                outputs["phase77"] = json.load(f)
        except Exception as e:
            print(f"[PH80] Error loading Phase 77: {e}")
            outputs["phase77"] = {}
    else:
        outputs["phase77"] = {}

    if PHASE79_JSON.exists():
        try:
            with PHASE79_JSON.open("r", encoding="utf-8") as f:
                outputs["phase79"] = json.load(f)
        except Exception as e:
            print(f"[PH80] Error loading Phase 79: {e}")
            outputs["phase79"] = {}
    else:
        outputs["phase79"] = {}

    return outputs


def generate_evolution_status() -> Dict[str, Any]:
    """Generate evolution status report."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 80 - GENI EVOLUTION STATUS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load phase outputs
    outputs = load_phase_outputs()

    # Extract insights
    strengths = []
    weaknesses = []
    threshold_adjustments = []
    risk_profile_changes = []
    feature_emphasis = []
    next_actions = []

    # From Phase 76 (self-critique)
    if outputs["phase76"]:
        overall = outputs["phase76"].get("overall", {})
        if overall.get("correct_direction_count", 0) > overall.get("incorrect_direction_count", 0):
            strengths.append("Good directional accuracy")
        if overall.get("too_conservative_count", 0) > overall.get("too_aggressive_count", 0):
            weaknesses.append("Too conservative - missing opportunities")
            risk_profile_changes.append("Consider lowering confidence thresholds slightly")
        if overall.get("too_aggressive_count", 0) > 0:
            weaknesses.append("Some trades too aggressive - resulting in losses")
            risk_profile_changes.append("Tighten risk management for high-confidence signals")

    # From Phase 77 (self-correction)
    if outputs["phase77"]:
        recommendations = outputs["phase77"].get("recommendations", [])
        for rec in recommendations:
            threshold_adjustments.append(
                {
                    "underlying": rec.get("underlying", "UNKNOWN"),
                    "current": rec.get("current_conf", 0.80),
                    "suggested": rec.get("suggested_conf", 0.80),
                    "reason": rec.get("reason", ""),
                }
            )
            next_actions.append(
                f"Adjust {rec.get('underlying')} confidence threshold from {rec.get('current_conf')} to {rec.get('suggested_conf')}"
            )

    # From Phase 79 (adaptive thresholds)
    if outputs["phase79"]:
        regimes = outputs["phase79"].get("regimes", {})
        if regimes:
            feature_emphasis.append("Regime-based adaptive thresholds show promise")
            next_actions.append("Implement regime-aware threshold selection in live trading")

    # Default actions if no data
    if not next_actions:
        next_actions = [
            "Run Phase 76 to generate self-critique data",
            "Run Phase 77 to get threshold recommendations",
            "Review historical performance patterns",
            "Consider implementing adaptive thresholds per regime",
            "Monitor for over-conservative behavior",
        ]

    report = {
        "timestamp": datetime.now().isoformat(),
        "current_strengths": strengths,
        "current_weaknesses": weaknesses,
        "proposed_threshold_adjustments": threshold_adjustments,
        "suggested_risk_profile_changes": risk_profile_changes,
        "suggested_feature_emphasis": feature_emphasis,
        "next_step_actions": next_actions[:10],  # Top 10
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH80] Evolution status saved to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH80] Markdown report written to {OUTPUT_MD}")
    print("[PH80] Aggregated GENI evolution recommendations")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 80 - GENI Evolution Status\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        # Accuracy improvements
        f.write("## Accuracy Improvements\n\n")
        if report["current_strengths"]:
            for strength in report["current_strengths"]:
                f.write(f"- ✅ {strength}\n")
        if report["current_weaknesses"]:
            for weakness in report["current_weaknesses"]:
                f.write(f"- ⚠️ {weakness}\n")
        f.write("\n")

        # Risk adjustments
        f.write("## Risk Adjustments\n\n")
        for change in report["suggested_risk_profile_changes"]:
            f.write(f"- {change}\n")
        if not report["suggested_risk_profile_changes"]:
            f.write("- No immediate risk profile changes recommended\n")
        f.write("\n")

        # Threshold recommendations
        f.write("## Threshold Recommendations\n\n")
        if report["proposed_threshold_adjustments"]:
            f.write("| Underlying | Current | Suggested | Reason |\n")
            f.write("|------------|---------|-----------|--------|\n")
            for adj in report["proposed_threshold_adjustments"]:
                f.write(
                    f"| {adj['underlying']} | {adj['current']:.2f} | {adj['suggested']:.2f} | {adj['reason'][:50]} |\n"
                )
        else:
            f.write("No threshold adjustments recommended at this time.\n")
        f.write("\n")

        # Next-step actions
        f.write("## Next-Step Actions\n\n")
        for i, action in enumerate(report["next_step_actions"], 1):
            f.write(f"{i}. {action}\n")
        f.write("\n")


def main():
    """Main entry point."""
    try:
        report = generate_evolution_status()
        print("\n[PH80] Evolution status generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH80] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
