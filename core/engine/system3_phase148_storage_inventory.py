"""
System3 Phase 148 - Storage Inventory

Summarizes storage/ultra and storage/config files.
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
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_CONFIG = PROJECT_ROOT / "storage" / "config"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_MD_PATH = STORAGE_ULTRA / "phase148_storage_inventory.md"


def run_phase148_storage_inventory() -> Dict[str, Any]:
    """
    Generate storage inventory.

    Returns:
        dict: {
            "phase": 148,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Scan storage/ultra
        ultra_files = []
        if STORAGE_ULTRA.exists():
            for file_path in STORAGE_ULTRA.glob("*"):
                if file_path.is_file():
                    ultra_files.append(
                        {
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        }
                    )

        # Scan storage/config
        config_files = []
        if STORAGE_CONFIG.exists():
            for file_path in STORAGE_CONFIG.glob("*.json"):
                config_files.append(
                    {
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    }
                )

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Storage Inventory\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Storage/Ultra Files\n\n")
            if ultra_files:
                f.write(f"**Total Files**: {len(ultra_files)}\n\n")
                f.write("| File Name | Size (bytes) | Last Modified |\n")
                f.write("|-----------|--------------|---------------|\n")
                for file_info in sorted(ultra_files, key=lambda x: x["name"]):
                    f.write(f"| {file_info['name']} | {file_info['size']} | {file_info['modified'][:19]} |\n")
            else:
                f.write("No files found in `storage/ultra/`.\n")

            f.write("\n## Storage/Config Files\n\n")
            if config_files:
                f.write(f"**Total Files**: {len(config_files)}\n\n")
                f.write("| File Name | Size (bytes) | Last Modified |\n")
                f.write("|-----------|--------------|---------------|\n")
                for file_info in sorted(config_files, key=lambda x: x["name"]):
                    f.write(f"| {file_info['name']} | {file_info['size']} | {file_info['modified'][:19]} |\n")
            else:
                f.write("No config files found in `storage/config/`.\n")

        status = "OK"
        details = f"Storage inventory generated: {len(ultra_files)} ultra files, {len(config_files)} config files"

        return {
            "phase": 148,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "ultra_file_count": len(ultra_files),
                "config_file_count": len(config_files),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 148,
            "status": "ERROR",
            "details": f"Phase 148 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 148 - STORAGE INVENTORY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase148_storage_inventory()

    print(f"Phase148: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nUltra files: {result['outputs']['ultra_file_count']}")
        print(f"Config files: {result['outputs']['config_file_count']}")
        print(f"Report: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
