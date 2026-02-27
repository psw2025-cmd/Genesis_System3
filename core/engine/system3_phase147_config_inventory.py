"""
System3 Phase 147 - Config Inventory

Lists all config JSON files and their purpose.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_MD_PATH = STORAGE_ULTRA / "phase147_config_inventory.md"


def run_phase147_config_inventory() -> Dict[str, Any]:
    """
    Generate config inventory.

    Returns:
        dict: {
            "phase": 147,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Scan config directory
        config_files = []
        if STORAGE_CONFIG.exists():
            for config_file in STORAGE_CONFIG.glob("*.json"):
                config_files.append(
                    {
                        "name": config_file.name,
                        "path": str(config_file),
                        "size": config_file.stat().st_size,
                        "modified": datetime.fromtimestamp(config_file.stat().st_mtime).isoformat(),
                    }
                )

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Config Inventory\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Config Files\n\n")
            if config_files:
                f.write("| File Name | Size (bytes) | Last Modified | Purpose |\n")
                f.write("|-----------|--------------|--------------|---------|\n")
                for cfg in sorted(config_files, key=lambda x: x["name"]):
                    # Infer purpose from filename
                    purpose = "Configuration file"
                    if "safety" in cfg["name"].lower():
                        purpose = "Safety configuration"
                    elif "master" in cfg["name"].lower():
                        purpose = "Master session configuration"
                    elif "threshold" in cfg["name"].lower():
                        purpose = "Trading thresholds"
                    elif "risk" in cfg["name"].lower():
                        purpose = "Risk profile"
                    elif "ultra" in cfg["name"].lower():
                        purpose = "Ultra mode configuration"

                    f.write(f"| {cfg['name']} | {cfg['size']} | {cfg['modified'][:19]} | {purpose} |\n")
            else:
                f.write("No config files found in `storage/config/`.\n")

        status = "OK"
        details = f"Config inventory generated: {len(config_files)} files"

        return {
            "phase": 147,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "config_count": len(config_files),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 147,
            "status": "ERROR",
            "details": f"Phase 147 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 147 - CONFIG INVENTORY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase147_config_inventory()

    print(f"Phase147: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nConfig files: {result['outputs']['config_count']}")
        print(f"Report: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
