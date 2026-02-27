"""
System3 Phase 207 - Hotfix Registry Manager

Maintains a JSON registry of applied hotfixes.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
REGISTRY_PATH = STORAGE_META / "system3_hotfix_registry.json"

LOG_DIR = PROJECT_ROOT / "logs" / "meta"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_hotfix_registry.log"


def run_phase207(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 207: Hotfix Registry Manager.

    Returns:
        dict: {
            "phase": 207,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "active_hotfixes": int,
                "retired_hotfixes": int,
                "new_hotfixes": int,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        # Load existing registry
        registry = {"hotfixes": [], "last_updated": datetime.now().isoformat()}
        if REGISTRY_PATH.exists():
            try:
                with REGISTRY_PATH.open("r", encoding="utf-8") as f:
                    registry = json.load(f)
            except Exception as e:
                errors.append(f"Failed to load registry: {e}")

        # For now, this is a stub that maintains the registry structure
        # In production, this would check code changes/patches
        active_hotfixes = [h for h in registry.get("hotfixes", []) if h.get("status") == "active"]
        retired_hotfixes = [h for h in registry.get("hotfixes", []) if h.get("status") == "retired"]

        # Save updated registry
        registry["last_updated"] = datetime.now().isoformat()
        with REGISTRY_PATH.open("w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        # Log summary
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Hotfix Registry Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Active Hotfixes: {len(active_hotfixes)}\n")
            f.write(f"Retired Hotfixes: {len(retired_hotfixes)}\n")
            f.write(f"New Hotfixes: 0\n")
            f.write(f"\nRegistry Path: {REGISTRY_PATH}\n")

        status = "OK"
        details = f"Registry maintained: {len(active_hotfixes)} active, {len(retired_hotfixes)} retired"

        return {
            "phase": 207,
            "status": status,
            "details": details,
            "outputs": {
                "active_hotfixes": len(active_hotfixes),
                "retired_hotfixes": len(retired_hotfixes),
                "new_hotfixes": 0,
                "registry_path": str(REGISTRY_PATH),
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 207,
            "status": "ERROR",
            "details": f"Phase 207 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 207 - HOTFIX REGISTRY MANAGER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase207()

    print(f"Phase 207: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nRegistry: {result['outputs']['registry_path']}")
        print(f"Active: {result['outputs']['active_hotfixes']}")
        print(f"Retired: {result['outputs']['retired_hotfixes']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
