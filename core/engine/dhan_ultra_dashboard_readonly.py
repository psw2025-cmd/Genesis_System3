"""
Dhan Index Options - Ultra Dashboard (Read-Only)

Mini dashboard with summaries.
Read-only dashboard.
SAFE MODE ONLY - No changes, display only.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
ULTRA_OBS_DIR = REPORTS_DIR / "ultra_obs"

ULTRA_OBS_DIR.mkdir(parents=True, exist_ok=True)


def generate_dashboard() -> Dict[str, Any]:
    """
    Generate read-only dashboard with summaries.

    Returns:
        Dict with dashboard data
    """
    print("=== ANGEL ONE INDEX OPTIONS - ULTRA DASHBOARD (READ-ONLY) ===\n")

    dashboard = {
        "generated_at": datetime.utcnow().isoformat(),
        "mode": "READ_ONLY",
        "sections": {},
    }

    # Section 1: System Status
    try:
        from core.engine.dhan_ultra_health_tree import build_health_tree

        health_tree = build_health_tree()
        dashboard["sections"]["system_health"] = {
            "overall_score": health_tree.get("overall_health_score", 0.0),
            "overall_status": health_tree.get("overall_status", "UNKNOWN"),
            "components": {k: v.get("status", "UNKNOWN") for k, v in health_tree.get("components", {}).items()},
        }
    except Exception as e:
        dashboard["sections"]["system_health"] = {
            "error": str(e),
        }

    # Section 2: Execution Readiness
    try:
        from core.engine.dhan_execution_readiness_auditor import (
            audit_execution_readiness,
        )

        audit = audit_execution_readiness()
        dashboard["sections"]["execution_readiness"] = {
            "overall_ready": audit.get("overall_ready", False),
            "checks_passed": sum(1 for c in audit.get("checks", []) if c.get("status") == "PASS"),
            "total_checks": len(audit.get("checks", [])),
        }
    except Exception as e:
        dashboard["sections"]["execution_readiness"] = {
            "error": str(e),
        }

    # Section 3: Failure Points
    try:
        from core.engine.dhan_failure_point_predictor import predict_failure_points

        failure_analysis = predict_failure_points()
        dashboard["sections"]["failure_points"] = {
            "overall_risk": failure_analysis.get("overall_risk", "UNKNOWN"),
            "total_issues": failure_analysis.get("total_issues", 0),
            "risk_counts": failure_analysis.get("risk_counts", {}),
        }
    except Exception as e:
        dashboard["sections"]["failure_points"] = {
            "error": str(e),
        }

    # Section 4: Latency/Drift
    try:
        from core.engine.dhan_latency_drift_observatory import analyze_latency_drift

        latency_analysis = analyze_latency_drift()
        if latency_analysis.get("status") == "SUCCESS":
            dashboard["sections"]["latency_drift"] = {
                "total_signals": latency_analysis.get("total_signals", 0),
                "mean_latency": latency_analysis.get("latency_stats", {}).get("mean_seconds", 0.0),
                "drift_detected": latency_analysis.get("latency_drift", {}).get("detected", False),
            }
        else:
            dashboard["sections"]["latency_drift"] = {
                "status": latency_analysis.get("status", "UNKNOWN"),
            }
    except Exception as e:
        dashboard["sections"]["latency_drift"] = {
            "error": str(e),
        }

    # Section 5: Configuration Summary
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG

        dashboard["sections"]["configuration"] = {
            "auto_execute": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
            "safe_mode": not AUTOMATION_CONFIG.auto_execute_trades and not AUTOMATION_CONFIG.auto_simulate_pnl,
        }
    except Exception:
        dashboard["sections"]["configuration"] = {
            "error": "Configuration not available",
        }

    return dashboard


def save_dashboard(dashboard: Dict[str, Any]) -> Path:
    """
    Save dashboard to JSON.

    Returns:
        Path to saved JSON
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    json_path = ULTRA_OBS_DIR / f"dashboard_{today}.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2)

    return json_path


def main() -> None:
    """Main entry point."""
    dashboard = generate_dashboard()

    print("=== SYSTEM3 ULTRA DASHBOARD (READ-ONLY) ===\n")

    # System Health
    if "system_health" in dashboard["sections"]:
        health = dashboard["sections"]["system_health"]
        if "error" not in health:
            print("=== SYSTEM HEALTH ===")
            print(f"Overall Score: {health.get('overall_score', 0):.1f}%")
            print(f"Overall Status: {health.get('overall_status', 'UNKNOWN')}")
            for comp, status in health.get("components", {}).items():
                icon = "✅" if status == "HEALTHY" else "⚠️"
                print(f"  {icon} {comp}: {status}")

    # Execution Readiness
    if "execution_readiness" in dashboard["sections"]:
        readiness = dashboard["sections"]["execution_readiness"]
        if "error" not in readiness:
            print("\n=== EXECUTION READINESS ===")
            status_icon = "✅" if readiness.get("overall_ready") else "❌"
            print(f"{status_icon} Ready: {readiness.get('overall_ready', False)}")
            print(f"  Checks Passed: {readiness.get('checks_passed', 0)}/{readiness.get('total_checks', 0)}")

    # Failure Points
    if "failure_points" in dashboard["sections"]:
        failures = dashboard["sections"]["failure_points"]
        if "error" not in failures:
            print("\n=== FAILURE POINTS ===")
            print(f"Overall Risk: {failures.get('overall_risk', 'UNKNOWN')}")
            print(f"Total Issues: {failures.get('total_issues', 0)}")
            for risk, count in failures.get("risk_counts", {}).items():
                if count > 0:
                    print(f"  {risk}: {count}")

    # Latency/Drift
    if "latency_drift" in dashboard["sections"]:
        latency = dashboard["sections"]["latency_drift"]
        if "error" not in latency:
            print("\n=== LATENCY & DRIFT ===")
            if "total_signals" in latency:
                print(f"Total Signals: {latency.get('total_signals', 0)}")
                print(f"Mean Latency: {latency.get('mean_latency', 0):.2f}s")
                drift_icon = "⚠️" if latency.get("drift_detected") else "✅"
                print(f"{drift_icon} Drift Detected: {latency.get('drift_detected', False)}")

    # Configuration
    if "configuration" in dashboard["sections"]:
        config = dashboard["sections"]["configuration"]
        if "error" not in config:
            print("\n=== CONFIGURATION ===")
            safe_icon = "✅" if config.get("safe_mode") else "⚠️"
            print(f"{safe_icon} Safe Mode: {config.get('safe_mode', False)}")
            print(f"  Auto-Execute: {config.get('auto_execute', False)}")
            print(f"  Auto-PnL: {config.get('auto_pnl', False)}")

    # Save
    save_path = save_dashboard(dashboard)
    print(f"\n[SAVE] Dashboard saved to: {save_path}")
    print("\n[NOTE] This is a read-only dashboard. No changes made.")


if __name__ == "__main__":
    main()
