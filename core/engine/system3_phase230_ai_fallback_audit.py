"""
System3 Phase 230 - AI Fallback Behavior Auditor

Reviews logs to count delta-based ai_score fallback usage.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "ml"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_ai_fallback_audit.md"

ML_LOGS_DIR = PROJECT_ROOT / "logs" / "ml"
MODEL_DIAGNOSTICS_DIR = PROJECT_ROOT / "logs" / "model_diagnostics"


def count_fallback_usage(log_dir: Path) -> tuple[int, list[str]]:
    """Count fallback usage in log files."""
    fallback_count = 0
    reasons = []

    if not log_dir.exists():
        return 0, []

    # Search for fallback patterns in log files
    for log_file in log_dir.rglob("*.log"):
        try:
            with log_file.open("r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Look for fallback-related messages
                if "fallback" in content.lower() or "delta-based" in content.lower():
                    matches = re.findall(r"(?i)(fallback|delta-based|uniform.*probability)", content)
                    fallback_count += len(matches)
                    if "no curated data" in content.lower():
                        reasons.append("Lack of curated data")
                    if "load error" in content.lower() or "parse" in content.lower():
                        reasons.append("Data load errors")
        except Exception:
            pass

    return fallback_count, list(set(reasons))


def run_phase230(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 230: AI Fallback Behavior Auditor.

    Returns:
        dict: {
            "phase": 230,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "fallback_count": int,
                "fallback_reasons": list,
                "report_path": str,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        # Count fallback usage in ML logs
        ml_fallback_count, ml_reasons = count_fallback_usage(ML_LOGS_DIR)
        diag_fallback_count, diag_reasons = count_fallback_usage(MODEL_DIAGNOSTICS_DIR)

        total_fallback = ml_fallback_count + diag_fallback_count
        all_reasons = list(set(ml_reasons + diag_reasons))

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 AI Fallback Behavior Audit\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Fallback Occurrences**: {total_fallback}\n\n")

            f.write("## Fallback Usage Summary\n\n")
            f.write(f"- **ML Logs**: {ml_fallback_count} occurrences\n")
            f.write(f"- **Model Diagnostics**: {diag_fallback_count} occurrences\n\n")

            if all_reasons:
                f.write("## Identified Reasons\n\n")
                for reason in all_reasons:
                    f.write(f"- {reason}\n")
            else:
                f.write("## Reasons\n\n")
                f.write("No specific reasons identified in logs.\n")

            f.write("\n## Recommendations\n\n")
            if total_fallback > 0:
                f.write("1. **Increase Training Data**: Ensure curated training data is available\n")
                f.write("2. **Fix Data Loading**: Resolve any CSV parsing errors\n")
                f.write("3. **Model Training**: Ensure ML models are trained regularly\n")
                f.write("4. **Monitor Fallback Rate**: Track fallback usage over time\n")
            else:
                f.write("✅ No fallback usage detected. ML model is functioning normally.\n")

        status = "WARN" if total_fallback > 0 else "OK"
        details = f"Found {total_fallback} fallback occurrence(s)"
        if all_reasons:
            details += f", reasons: {', '.join(all_reasons[:2])}"

        return {
            "phase": 230,
            "status": status,
            "details": details,
            "outputs": {
                "fallback_count": total_fallback,
                "fallback_reasons": all_reasons,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 230,
            "status": "ERROR",
            "details": f"Phase 230 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 230 - AI FALLBACK BEHAVIOR AUDITOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase230()

    print(f"Phase 230: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Fallback Count: {result['outputs']['fallback_count']}")
        if result["outputs"]["fallback_reasons"]:
            print(f"Reasons: {', '.join(result['outputs']['fallback_reasons'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
