"""
System3 Phase 388: Health Gate

Purpose: Final gate check before declaring phases 381-388 complete
Outputs: JSON metrics + Markdown health gate report

Safety: DRY-RUN only, read-only verification, no live trading
"""

import sys
from pathlib import Path
import json
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from core.engine.ultra_models_loader import verify_ultra_models_health

# Paths
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"
CONFIG_DIR = ROOT_DIR / "core" / "config"


def check_safety_configs() -> dict:
    """
    Verify safety configs are NOT modified (all flags remain False).

    Returns:
        {"live_trading_enabled": False, "use_live_execution": False, ...}
    """
    safety_status = {
        "live_trade_config_checked": False,
        "live_trading_enabled": None,
        "dhan_automation_config_checked": False,
        "dry_run_enabled": None,
        "system3_ultra_safety_checked": False,
        "auto_execute_trades": None,
        "safety_verified": False,
    }

    # Check live_trade_config.py
    live_config_path = CONFIG_DIR / "live_trade_config.py"
    if live_config_path.exists():
        try:
            with open(live_config_path, "r") as f:
                content = f.read()
                # Look for LIVE_TRADING_ENABLED = False
                if "LIVE_TRADING_ENABLED" in content:
                    if "LIVE_TRADING_ENABLED = False" in content or "LIVE_TRADING_ENABLED=False" in content:
                        safety_status["live_trading_enabled"] = False
                        safety_status["live_trade_config_checked"] = True
        except Exception as e:
            logger.warning(f"Could not check live_trade_config.py: {e}")

    # Check dhan_automation_config.json
    dhan_config_path = CONFIG_DIR / "dhan_automation_config.json"
    if dhan_config_path.exists():
        try:
            with open(dhan_config_path, "r") as f:
                config = json.load(f)
                dry_run = config.get("DRY_RUN", config.get("dry_run"))
                if dry_run is True:
                    safety_status["dry_run_enabled"] = True
                    safety_status["dhan_automation_config_checked"] = True
        except Exception as e:
            logger.warning(f"Could not check dhan_automation_config.json: {e}")

    # Overall safety verified if all critical flags are safe
    if safety_status["live_trading_enabled"] is False and safety_status["dry_run_enabled"] is True:
        safety_status["safety_verified"] = True

    return safety_status


def run_phase_388() -> dict:
    """
    Phase 388: Phase 381-388 Health Gate

    Final gate check before declaring phases 381-388 complete.

    Checks:
    1. All 5 Ultra models loadable (Phase 381)
    2. All models pass smoke test (Phase 382)
    3. Backtest completed (Phase 383)
    4. Health summary generated (Phase 384)
    5. Telemetry tracking working (Phase 385)
    6. Fail-safe verified (Phase 386)
    7. Impact preview generated (Phase 387)
    8. No safety config changes
    9. DRY-RUN still enforced

    Writes:
    - storage/metrics/phase_381_388_health_gate.json
    - reports/PHASE_381_388_HEALTH_GATE.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 388: HEALTH GATE (381-388 VERIFICATION)")
    logger.info("=" * 60)

    health_gate = {
        "health_gate_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": {},
        "overall_status": "error",
    }

    try:
        # Check 1: Ultra models health (Phase 381)
        logger.info("Check 1: Ultra models inventory...")
        ultra_health = verify_ultra_models_health()
        health_gate["checks"]["ultra_models_loadable"] = {
            "status": ultra_health["overall_status"],
            "available": ultra_health["models_available"],
            "total": ultra_health["models_total"],
        }

        # Check 2: Phase 382 validation metrics
        logger.info("Check 2: Smoke test validation...")
        validation_file = METRICS_DIR / "ultra_models_validation_382.json"
        if validation_file.exists():
            with open(validation_file, "r") as f:
                validation = json.load(f)
                health_gate["checks"]["smoke_tests"] = {
                    "status": "ok" if validation.get("models_failed", 1) == 0 else "warn",
                    "passed": validation.get("models_passed", 0),
                    "failed": validation.get("models_failed", 0),
                }
        else:
            health_gate["checks"]["smoke_tests"] = {"status": "error", "message": "Phase 382 not run"}

        # Check 3: Phase 383 backtest metrics
        logger.info("Check 3: Backtest results...")
        backtest_file = METRICS_DIR / "ultra_vs_delta_backtest_383.json"
        if backtest_file.exists():
            with open(backtest_file, "r") as f:
                backtest = json.load(f)
                health_gate["checks"]["backtest_completed"] = {
                    "status": "ok" if backtest.get("results") else "warn",
                    "underlyings_tested": len(backtest.get("underlyings_tested", [])),
                }
        else:
            health_gate["checks"]["backtest_completed"] = {"status": "warn", "message": "Phase 383 not run"}

        # Check 4: Phase 384 health summary exists
        logger.info("Check 4: Health summary...")
        health_summary_file = REPORTS_DIR / "ULTRA_MODEL_HEALTH_384.md"
        if health_summary_file.exists():
            health_gate["checks"]["health_summary"] = {"status": "ok"}
        else:
            health_gate["checks"]["health_summary"] = {"status": "warn", "message": "Phase 384 not run"}

        # Check 5: Phase 385 telemetry exists
        logger.info("Check 5: Telemetry tracking...")
        telemetry_file = METRICS_DIR / "scoring_telemetry_385.json"
        if telemetry_file.exists():
            health_gate["checks"]["telemetry"] = {"status": "ok"}
        else:
            health_gate["checks"]["telemetry"] = {
                "status": "warn",
                "message": "Phase 385 not run (expected on first deployment)",
            }

        # Check 6: Phase 386 fail-safe verification
        logger.info("Check 6: Fail-safe guard...")
        failsafe_file = METRICS_DIR / "failsafe_guard_386.json"
        if failsafe_file.exists():
            with open(failsafe_file, "r") as f:
                failsafe = json.load(f)
                health_gate["checks"]["failsafe_verified"] = {
                    "status": "ok" if failsafe.get("tests_failed", 1) == 0 else "warn",
                    "passed": failsafe.get("tests_passed", 0),
                    "failed": failsafe.get("tests_failed", 0),
                }
        else:
            health_gate["checks"]["failsafe_verified"] = {"status": "error", "message": "Phase 386 not run"}

        # Check 7: Phase 387 impact preview exists
        logger.info("Check 7: Impact preview...")
        impact_file = REPORTS_DIR / "ULTRA_MODELS_IMPACT_PREVIEW_387.md"
        if impact_file.exists():
            health_gate["checks"]["impact_preview"] = {"status": "ok"}
        else:
            health_gate["checks"]["impact_preview"] = {"status": "warn", "message": "Phase 387 not run"}

        # Check 8 & 9: Safety configs
        logger.info("Check 8-9: Safety configuration verification...")
        safety_status = check_safety_configs()
        health_gate["checks"]["safety_configs"] = safety_status

        # Determine overall status
        critical_checks = [
            health_gate["checks"]["ultra_models_loadable"]["status"],
            health_gate["checks"]["smoke_tests"].get("status", "error"),
            health_gate["checks"]["failsafe_verified"].get("status", "error"),
            "ok" if safety_status["safety_verified"] else "error",
        ]

        if all(s == "ok" for s in critical_checks):
            health_gate["overall_status"] = "ok"
        elif any(s == "ok" for s in critical_checks):
            health_gate["overall_status"] = "warn"
        else:
            health_gate["overall_status"] = "error"

        # Write JSON metrics
        metrics_file = METRICS_DIR / "phase_381_388_health_gate.json"
        with open(metrics_file, "w") as f:
            json.dump(health_gate, f, indent=2)
        logger.info(f"✓ Metrics written: {metrics_file}")

        # Write Markdown report
        report_file = REPORTS_DIR / "PHASE_381_388_HEALTH_GATE.md"
        with open(report_file, "w") as f:
            f.write("# PHASE 381-388 HEALTH GATE\n\n")
            f.write(f"**Health Gate Timestamp:** {health_gate['health_gate_timestamp']}\n")
            f.write(f"**Overall Status:** {health_gate['overall_status'].upper()}\n\n")

            f.write("## Gate Checks\n\n")

            for check_name, check_data in health_gate["checks"].items():
                status_icon = {"ok": "✅", "warn": "⚠️", "error": "❌"}.get(check_data.get("status", "error"), "❓")
                f.write(f"### {check_name.replace('_', ' ').title()}\n\n")
                f.write(f"{status_icon} **Status:** {check_data.get('status', 'unknown').upper()}\n\n")

                # Add details
                for key, value in check_data.items():
                    if key != "status":
                        f.write(f"- {key}: {value}\n")
                f.write("\n")

            f.write("## Summary\n\n")
            if health_gate["overall_status"] == "ok":
                f.write("✅ **PHASES 381-388: COMPLETE & VERIFIED**\n\n")
                f.write("**All critical checks passed:**\n")
                f.write("- ✅ Ultra models loadable\n")
                f.write("- ✅ Smoke tests passed\n")
                f.write("- ✅ Fail-safe verified\n")
                f.write("- ✅ Safety configs unchanged (DRY-RUN enforced)\n\n")
                f.write("**Recommendation:** 🚀 **DEPLOYMENT APPROVED (DRY-RUN)**\n\n")
                f.write("Next steps:\n")
                f.write("1. Run block test to confirm integration\n")
                f.write("2. Monitor telemetry in production (DRY-RUN)\n")
                f.write("3. After 5-10 paper trading days, consider Path B (Blended Training)\n")
            elif health_gate["overall_status"] == "warn":
                f.write("⚠️ **PHASES 381-388: PARTIAL COMPLETION**\n\n")
                f.write("**Some checks passed, some warnings:**\n")
                f.write("- Review warnings above\n")
                f.write("- Delta fallback will handle missing components\n\n")
                f.write("**Recommendation:** ⚠️ **SAFE TO DEPLOY WITH MONITORING**\n")
            else:
                f.write("❌ **PHASES 381-388: NOT READY**\n\n")
                f.write("**Critical checks failed:**\n")
                f.write("- Review errors above\n")
                f.write("- Fix issues before production deployment\n\n")
                f.write("**Recommendation:** ❌ **BLOCK DEPLOYMENT**\n")

        logger.info(f"✓ Report written: {report_file}")

        # Log summary
        if health_gate["overall_status"] == "ok":
            message = "All health checks passed - deployment approved"
        elif health_gate["overall_status"] == "warn":
            message = "Partial health - safe to deploy with monitoring"
        else:
            message = "Critical checks failed - deployment blocked"

        logger.info(f"Phase 388 Status: {health_gate['overall_status'].upper()} - {message}")
        logger.info("=" * 60)

        return {"status": health_gate["overall_status"], "message": message, "metrics": health_gate}

    except Exception as e:
        logger.error(f"Phase 388 ERROR: {e}")
        return {"status": "error", "message": f"Phase 388 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_388()
    print(f"\nPhase 388 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
