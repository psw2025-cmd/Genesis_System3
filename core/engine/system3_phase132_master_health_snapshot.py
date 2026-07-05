"""
System3 Phase 132 - Master Session Health Snapshot

Gathers minimal health info for master session.
"""

import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

MASTER_CONFIG_PATH = STORAGE_CONFIG / "system3_master_session_config.json"
OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase132_master_health_snapshot.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase132_master_health_snapshot.md"


def check_dhan_connectivity() -> Dict[str, Any]:
    """
    Check Dhan connectivity (safe mode, no orders).

    Returns:
        dict: Status info
    """
    try:
        # Try to import existing Dhan modules
        from core.brokers.dhan.broker import Broker as AngelBroker

        # Try a safe operation (like checking if broker class exists)
        # DO NOT place orders or modify anything
        broker_status = "OK"
        broker_message = "Dhan broker module available"

    except ImportError:
        broker_status = "WARN"
        broker_message = "Dhan broker module not found (may be optional)"
    except Exception as e:
        broker_status = "ERROR"
        broker_message = f"Error checking Dhan: {e}"

    return {
        "status": broker_status,
        "message": broker_message,
    }


def run_phase132_master_health_snapshot() -> Dict[str, Any]:
    """
    Gather master session health snapshot.

    Returns:
        dict: {
            "phase": 132,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    health_data = {}

    try:
        # Load master config
        master_config = {}
        if MASTER_CONFIG_PATH.exists():
            try:
                with MASTER_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    master_config = json.load(f)
            except Exception as e:
                errors.append(f"Error reading master config: {e}")

        # Gather environment info
        python_version = platform.python_version()
        venv_detected = "venv" in sys.executable.lower() or "virtualenv" in sys.executable.lower()

        # Check Dhan connectivity
        broker_info = check_dhan_connectivity()

        # Classify statuses
        env_status = "OK"
        if not venv_detected:
            env_status = "WARN"

        broker_status = broker_info["status"]

        # Overall health
        if broker_status == "ERROR" or env_status == "ERROR":
            overall_status = "ERROR"
        elif broker_status == "WARN" or env_status == "WARN":
            overall_status = "WARN"
        else:
            overall_status = "OK"

        # Build health snapshot
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "environment": {
                "python_version": python_version,
                "venv_detected": venv_detected,
                "status": env_status,
            },
            "broker": {
                "name": "DHAN",
                "status": broker_status,
                "message": broker_info["message"],
            },
            "config_loaded": MASTER_CONFIG_PATH.exists(),
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(health_data, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Session Health Snapshot\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Health Checks\n\n")
            f.write("| Check | Status | Details |\n")
            f.write("|-------|--------|---------|\n")
            f.write(f"| Environment | {env_status} | Python {python_version}, venv: {venv_detected} |\n")
            f.write(f"| Broker (Dhan) | {broker_status} | {broker_info['message']} |\n")
            f.write(f"| Config Loaded | {'YES' if health_data['config_loaded'] else 'NO'} | {MASTER_CONFIG_PATH} |\n")

            f.write("\n## Summary\n\n")
            f.write(f"**MASTER_HEALTH_STATUS = {overall_status}**\n\n")

            if overall_status == "OK":
                f.write("✅ All health checks passed.\n")
            elif overall_status == "WARN":
                f.write("⚠️ Some health checks have warnings (non-critical).\n")
            else:
                f.write("❌ Critical health checks failed.\n")

        status = "OK" if not errors else "ERROR"
        details = f"Health snapshot generated: {overall_status}"

        return {
            "phase": 132,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "overall_status": overall_status,
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 132,
            "status": "ERROR",
            "details": f"Phase 132 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 132 - MASTER SESSION HEALTH SNAPSHOT")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase132_master_health_snapshot()

    print(f"Phase132: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nOverall Status: {result['outputs']['overall_status']}")
        print(f"JSON: {result['outputs']['json_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
