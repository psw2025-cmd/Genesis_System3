"""
System3 Phase 131 - Master Session Config

Builds master session configuration for Dhan-only DRY-RUN mode.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_CONFIG.mkdir(parents=True, exist_ok=True)

STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

BASE_CONFIG_PATH = STORAGE_CONFIG / "system3_ultra_master_config.json"
OUTPUT_CONFIG_PATH = STORAGE_CONFIG / "system3_master_session_config.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase131_master_session_config_report.md"

# Safe defaults
SAFE_DEFAULTS = {
    "broker": "DHAN",
    "live_trading_enabled": False,
    "max_daily_trades": 10,
    "max_trades_per_underlying": 3,
    "max_loss_percent": 1.0,
    "dry_run": True,
    "timestamp": datetime.now().isoformat(),
}


def run_phase131_master_session_config(mode: str = "ANGEL_ONLY") -> Dict[str, Any]:
    """
    Build master session configuration.

    Args:
        mode: Must be "ANGEL_ONLY" (enforced)

    Returns:
        dict: {
            "phase": 131,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Enforce ANGEL_ONLY mode
        if mode != "ANGEL_ONLY":
            errors.append(f"Mode must be ANGEL_ONLY, got: {mode}")
            mode = "ANGEL_ONLY"  # Force to safe value

        # Start with safe defaults
        config = SAFE_DEFAULTS.copy()
        config["mode"] = mode
        config["timestamp"] = datetime.now().isoformat()

        # Load base config if exists
        overrides_applied = []
        if BASE_CONFIG_PATH.exists():
            try:
                with BASE_CONFIG_PATH.open("r", encoding="utf-8") as f:
                    base_config = json.load(f)

                # Merge overrides (but NEVER allow live_trading_enabled to become true)
                for key, value in base_config.items():
                    if key == "live_trading_enabled":
                        # Force to False regardless of base config
                        if value is True:
                            overrides_applied.append(f"OVERRIDE: {key} forced to False (safety)")
                        config[key] = False
                    elif key in SAFE_DEFAULTS:
                        if config[key] != value:
                            overrides_applied.append(f"OVERRIDE: {key} = {value}")
                        config[key] = value
                    else:
                        # New keys allowed
                        config[key] = value
                        overrides_applied.append(f"NEW: {key} = {value}")
            except Exception as e:
                errors.append(f"Error reading base config: {e}")

        # Ensure safety flags
        config["live_trading_enabled"] = False  # Always False
        config["dry_run"] = True  # Always True

        # Save final config
        with OUTPUT_CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Master Session Config Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Effective Configuration\n\n")
            f.write("| Key | Value |\n")
            f.write("|-----|-------|\n")
            for key, value in sorted(config.items()):
                if key != "timestamp":
                    f.write(f"| {key} | {value} |\n")

            f.write("\n## Safety Flags\n\n")
            f.write(f"- **dry_run**: {config['dry_run']} ✅\n")
            f.write(f"- **live_trading_enabled**: {config['live_trading_enabled']} ✅\n")
            f.write(f"- **broker**: {config['broker']} ✅\n")

            if overrides_applied:
                f.write("\n## Overrides Applied\n\n")
                for override in overrides_applied:
                    f.write(f"- {override}\n")
            else:
                f.write("\n## Overrides Applied\n\n")
                f.write("- No base config found, using safe defaults only.\n")

            f.write("\n## Summary\n\n")
            f.write("✅ **DRY_RUN_ONLY**: YES\n")
            f.write("✅ **LIVE_TRADING_ENABLED**: FALSE\n")
            f.write("✅ **BROKER**: DHAN\n")

        status = "OK" if not errors else "ERROR"
        details = "Master session config created with safe defaults"
        if overrides_applied:
            details += f" ({len(overrides_applied)} overrides applied)"

        return {
            "phase": 131,
            "status": status,
            "details": details,
            "outputs": {
                "config_path": str(OUTPUT_CONFIG_PATH),
                "report_path": str(OUTPUT_MD_PATH),
                "dry_run": config["dry_run"],
                "live_trading_enabled": config["live_trading_enabled"],
                "broker": config["broker"],
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 131,
            "status": "ERROR",
            "details": f"Phase 131 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 131 - MASTER SESSION CONFIG")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase131_master_session_config()

    print(f"Phase131: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nConfig: {result['outputs']['config_path']}")
        print(f"Report: {result['outputs']['report_path']}")
        print(f"DRY_RUN: {result['outputs']['dry_run']}")
        print(f"LIVE_TRADING_ENABLED: {result['outputs']['live_trading_enabled']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
