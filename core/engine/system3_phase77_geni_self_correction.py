"""
System3 Phase 77 - GENI Self-Correction Engine

Use Phase 76 self-critique to propose concrete corrections (not apply them automatically)
to thresholds and rules.
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
PHASE76_JSON = STORAGE_ULTRA / "phase76_geni_self_review.json"

# Output files
OUTPUT_JSON = STORAGE_ULTRA / "phase77_geni_self_corrections.json"
OUTPUT_MD = STORAGE_ULTRA / "phase77_geni_self_corrections.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def load_phase76_review() -> Dict[str, Any]:
    """Load Phase 76 self-review JSON."""
    if not PHASE76_JSON.exists():
        print(f"[PH77] Phase 76 review not found: {PHASE76_JSON}")
        return {}

    try:
        with PHASE76_JSON.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[PH77] Error loading Phase 76 review: {e}")
        return {}


def propose_corrections(review: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Propose corrections based on self-review."""
    recommendations = []

    if not review or "per_underlying" not in review:
        return recommendations

    per_underlying = review.get("per_underlying", {})

    # Default confidence thresholds (would normally come from config)
    default_conf = 0.80

    for underlying, stats in per_underlying.items():
        total_signals = stats.get("total_signals", 0)
        too_conservative = stats.get("too_conservative_count", 0)
        too_aggressive = stats.get("too_aggressive_count", 0)
        correct_count = stats.get("correct_direction_count", 0)
        incorrect_count = stats.get("incorrect_direction_count", 0)
        total_trades = stats.get("total_trades", 0)

        if total_signals == 0:
            continue

        # Calculate accuracy
        total_outcomes = correct_count + incorrect_count
        accuracy = correct_count / total_outcomes if total_outcomes > 0 else 0.0

        # Too conservative: high missed opportunities, good accuracy
        conservative_ratio = too_conservative / total_signals if total_signals > 0 else 0.0
        if conservative_ratio > 0.1 and accuracy > 0.6:
            # Propose lower confidence threshold
            suggested_conf = max(0.60, default_conf - 0.05)
            recommendations.append(
                {
                    "underlying": underlying,
                    "current_conf": default_conf,
                    "suggested_conf": suggested_conf,
                    "reason": f"Too conservative: missed {too_conservative} profitable opportunities. "
                    f"Accuracy is {accuracy:.1%}, suggesting we can lower threshold safely.",
                }
            )

        # Too aggressive: high losses, poor accuracy
        aggressive_ratio = too_aggressive / total_trades if total_trades > 0 else 0.0
        if aggressive_ratio > 0.15 and accuracy < 0.55:
            # Propose higher confidence threshold
            suggested_conf = min(0.95, default_conf + 0.05)
            recommendations.append(
                {
                    "underlying": underlying,
                    "current_conf": default_conf,
                    "suggested_conf": suggested_conf,
                    "reason": f"Too aggressive: {too_aggressive} trades resulted in significant losses. "
                    f"Accuracy is {accuracy:.1%}, suggesting we need higher threshold.",
                }
            )

    return recommendations


def generate_corrections() -> Dict[str, Any]:
    """Generate self-correction recommendations."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 77 - GENI SELF-CORRECTION ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Load Phase 76 review
    print(f"[PH77] Loading self-review from {PHASE76_JSON}")
    review = load_phase76_review()

    if not review:
        print("[PH77] No Phase 76 review found. Creating empty recommendations.")
        recommendations = []
    else:
        # Generate recommendations
        recommendations = propose_corrections(review)
        print(f"[PH77] Generated {len(recommendations)} correction recommendations")

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "recommendations": recommendations,
    }

    # Save JSON
    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[PH77] Saved JSON + MD to {OUTPUT_JSON}")

    # Generate MD
    generate_markdown(report)
    print(f"[PH77] Markdown report written to {OUTPUT_MD}")

    return report


def generate_markdown(report: Dict[str, Any]) -> None:
    """Generate markdown summary."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 77 - GENI Self-Correction Recommendations\n\n")
        f.write(f"**Date**: {report['timestamp']}\n\n")

        recommendations = report.get("recommendations", [])

        if not recommendations:
            f.write("## No Recommendations\n\n")
            f.write("Insufficient data to generate recommendations. ")
            f.write("Run Phase 76 first to generate self-critique data.\n\n")
            return

        # Table
        f.write("## Recommendations\n\n")
        f.write("| Underlying | Current Conf | Suggested Conf | Reason |\n")
        f.write("|------------|--------------|----------------|--------|\n")

        for rec in recommendations:
            f.write(
                f"| {rec['underlying']} | {rec['current_conf']:.2f} | "
                f"{rec['suggested_conf']:.2f} | {rec['reason']} |\n"
            )
        f.write("\n")

        # Detailed explanations
        f.write("## Detailed Recommendations\n\n")
        for i, rec in enumerate(recommendations, 1):
            f.write(f"### {i}. {rec['underlying']}\n\n")
            f.write(f"- **Current Confidence Threshold**: {rec['current_conf']:.2f}\n")
            f.write(f"- **Suggested Confidence Threshold**: {rec['suggested_conf']:.2f}\n")
            f.write(f"- **Reason**: {rec['reason']}\n\n")


def main():
    """Main entry point."""
    try:
        report = generate_corrections()
        print("\n[PH77] Self-correction generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH77] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
