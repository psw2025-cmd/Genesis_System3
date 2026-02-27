"""
System3 Ultra - Phase 53: Ultra Monitoring AI Agent

AI agent that monitors system health and suggests actions.
Read-only, no auto-actions. All suggestions require manual review.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 115
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
OUTPUT_DIR = PROJECT_ROOT / "storage" / "ultra" / "ph46_ph55"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def check_system_health() -> Dict[str, Any]:
    """Check system health metrics."""
    health = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_status": "UNKNOWN",
    }

    # Check 1: Ultra storage directory
    health["checks"]["ultra_storage"] = {
        "status": "OK" if ULTRA_DIR.exists() else "ERROR",
        "message": "Ultra storage directory exists" if ULTRA_DIR.exists() else "Ultra storage directory missing",
    }

    # Check 2: Recent signals
    signals_path = LIVE_DIR / "angel_index_ai_signals.csv"
    if signals_path.exists():
        try:
            df = pd.read_csv(signals_path)
            recent_count = len(df) if len(df) > 0 else 0
            health["checks"]["recent_signals"] = {
                "status": "OK" if recent_count > 0 else "WARN",
                "message": f"Recent signals: {recent_count}",
                "count": recent_count,
            }
        except Exception:
            health["checks"]["recent_signals"] = {
                "status": "ERROR",
                "message": "Failed to read signals file",
            }
    else:
        health["checks"]["recent_signals"] = {
            "status": "WARN",
            "message": "Signals file not found",
        }

    # Check 3: Model files
    models_dir = PROJECT_ROOT / "core" / "models" / "angel_one"
    model_count = len(list(models_dir.glob("*.pkl"))) if models_dir.exists() else 0
    health["checks"]["models"] = {
        "status": "OK" if model_count > 0 else "WARN",
        "message": f"Model files: {model_count}",
        "count": model_count,
    }

    # Check 4: Ultra phase outputs
    phase_outputs = [
        "phase31_ultra_fused_decisions.csv",
        "phase35_decision_audit.csv",
        "phase37_policy_risk_dashboard.md",
    ]
    found_outputs = sum(1 for fname in phase_outputs if (ULTRA_DIR / fname).exists())
    health["checks"]["ultra_outputs"] = {
        "status": "OK" if found_outputs >= 2 else "WARN",
        "message": f"Ultra phase outputs: {found_outputs}/{len(phase_outputs)}",
        "count": found_outputs,
    }

    # Overall status
    statuses = [check["status"] for check in health["checks"].values()]
    if all(s == "OK" for s in statuses):
        health["overall_status"] = "HEALTHY"
    elif any(s == "ERROR" for s in statuses):
        health["overall_status"] = "ERROR"
    else:
        health["overall_status"] = "WARN"

    return health


def generate_suggestions(health: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate AI suggestions based on health check."""
    suggestions = []

    for check_name, check_result in health["checks"].items():
        if check_result["status"] == "ERROR":
            suggestions.append(
                {
                    "priority": "HIGH",
                    "category": check_name,
                    "issue": check_result["message"],
                    "suggestion": f"Investigate and fix {check_name} issue immediately.",
                    "action_required": True,
                }
            )
        elif check_result["status"] == "WARN":
            suggestions.append(
                {
                    "priority": "MEDIUM",
                    "category": check_name,
                    "issue": check_result["message"],
                    "suggestion": f"Monitor {check_name} and take preventive action if needed.",
                    "action_required": False,
                }
            )

    # General suggestions based on overall status
    if health["overall_status"] == "HEALTHY":
        suggestions.append(
            {
                "priority": "LOW",
                "category": "general",
                "issue": "System is healthy",
                "suggestion": "Continue monitoring. No immediate action required.",
                "action_required": False,
            }
        )
    elif health["overall_status"] == "WARN":
        suggestions.append(
            {
                "priority": "MEDIUM",
                "category": "general",
                "issue": "Some warnings detected",
                "suggestion": "Review warnings and address proactively.",
                "action_required": False,
            }
        )

    return suggestions


def run_phase53_monitoring_agent() -> None:
    """Run Phase 53: Ultra Monitoring AI Agent."""
    print("=== SYSTEM3 ULTRA - PHASE 53: ULTRA MONITORING AI AGENT ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Read-Only Monitoring - No Auto-Actions\n")

    # Check system health
    print("[MONITOR] Checking system health...")
    health = check_system_health()

    # Generate suggestions
    suggestions = generate_suggestions(health)

    # Save monitoring report
    report_md = OUTPUT_DIR / "phase53_monitoring_report.md"
    with report_md.open("w", encoding="utf-8") as f:
        f.write("# Phase 53: Ultra Monitoring Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
        f.write("## System Health Status\n\n")
        f.write(f"**Overall Status**: {health['overall_status']}\n\n")
        f.write("### Health Checks\n\n")
        for check_name, check_result in health["checks"].items():
            f.write(f"#### {check_name}\n\n")
            f.write(f"- **Status**: {check_result['status']}\n")
            f.write(f"- **Message**: {check_result['message']}\n")
            if "count" in check_result:
                f.write(f"- **Count**: {check_result['count']}\n")
            f.write("\n")
        f.write("## AI Suggestions\n\n")
        if suggestions:
            for i, sug in enumerate(suggestions, 1):
                f.write(f"### Suggestion {i}: {sug['category']}\n\n")
                f.write(f"- **Priority**: {sug['priority']}\n")
                f.write(f"- **Issue**: {sug['issue']}\n")
                f.write(f"- **Suggestion**: {sug['suggestion']}\n")
                f.write(f"- **Action Required**: {'Yes' if sug['action_required'] else 'No'}\n\n")
        else:
            f.write("No suggestions at this time.\n\n")
        f.write("\n## Important Note\n\n")
        f.write("**This is a read-only monitoring report. All suggestions require manual review and approval.**\n")
    print(f"[SAVE] Monitoring report saved to: {report_md}")

    # Save suggestions JSON
    suggestions_json = OUTPUT_DIR / "phase53_agent_suggestions.json"
    with suggestions_json.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "health": health,
                "suggestions": suggestions,
                "generated_at": datetime.now().isoformat(),
                "note": "Read-only monitoring. No auto-actions taken.",
            },
            f,
            indent=2,
            default=str,
        )
    print(f"[SAVE] Agent suggestions saved to: {suggestions_json}")

    # Summary
    print(f"\n=== MONITORING AGENT SUMMARY ===")
    print(f"Overall Status: {health['overall_status']}")
    print(f"\nHealth Checks:")
    for check_name, check_result in health["checks"].items():
        print(f"  {check_name}: {check_result['status']} - {check_result['message']}")
    print(f"\nSuggestions Generated: {len(suggestions)}")
    if suggestions:
        for i, sug in enumerate(suggestions, 1):
            print(f"\nSuggestion {i} ({sug['priority']}):")
            print(f"  Category: {sug['category']}")
            print(f"  Issue: {sug['issue']}")
            print(f"  Suggestion: {sug['suggestion']}")

    print("\n[OK] Phase 53 Ultra Monitoring AI Agent completed")
    print("[NOTE] Monitoring complete. Review suggestions manually.")


def main() -> None:
    """Main entry point."""
    run_phase53_monitoring_agent()


if __name__ == "__main__":
    main()
