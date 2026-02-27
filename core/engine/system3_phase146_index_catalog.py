"""
System3 Phase 146 - Phase Index Catalog

Lists all phases and their primary role.
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
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase146_phase_index_catalog.json"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase146_phase_index_catalog.md"

# Phase catalog (static mapping)
PHASE_CATALOG = {
    "131": "Master Session Config",
    "132": "Master Session Health Snapshot",
    "133": "Master Safety & Kill-Switch",
    "134": "Master DRY-RUN Session Plan",
    "135": "Master Session Human Summary",
    "136": "Angel Symbol Universe",
    "137": "Expiry & Calendar Map",
    "138": "Angel Risk Tier Assignment",
    "139": "Lot Size & Margin Estimation",
    "140": "Capital Guard & One-Lot Guardrail",
    "141": "Spread & Liquidity Estimation",
    "142": "DRY-RUN Slippage Calculator",
    "143": "Execution Quality & Fill Heatmap",
    "144": "DRY-RUN PnL vs Execution Scenario",
    "145": "One-Lot Test-Mode Health Report",
    "146": "Phase Index Catalog",
    "147": "Config Inventory",
    "148": "Storage Inventory",
    "149": "Log Inventory",
    "150": "Phase Dependency Graph",
    "151": "Reserved Stub",
    "152": "Reserved Stub",
    "153": "Reserved Stub",
    "154": "Reserved Stub",
    "155": "Reserved Stub",
}


def run_phase146_index_catalog() -> Dict[str, Any]:
    """
    Generate phase index catalog.

    Returns:
        dict: {
            "phase": 146,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Build catalog data
        catalog_data = {
            "timestamp": datetime.now().isoformat(),
            "phases": [
                {
                    "phase": phase_num,
                    "role": role,
                }
                for phase_num, role in sorted(PHASE_CATALOG.items(), key=lambda x: int(x[0]))
            ],
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(catalog_data, f, indent=2)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Phase Index Catalog\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Phase Catalog\n\n")
            f.write("| Phase | Primary Role |\n")
            f.write("|-------|--------------|\n")
            for phase_num, role in sorted(PHASE_CATALOG.items(), key=lambda x: int(x[0])):
                f.write(f"| {phase_num} | {role} |\n")

        status = "OK"
        details = f"Phase catalog generated: {len(PHASE_CATALOG)} phases"

        return {
            "phase": 146,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "md_path": str(OUTPUT_MD_PATH),
                "phase_count": len(PHASE_CATALOG),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 146,
            "status": "ERROR",
            "details": f"Phase 146 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 146 - PHASE INDEX CATALOG")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase146_index_catalog()

    print(f"Phase146: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nPhases cataloged: {result['outputs']['phase_count']}")
        print(f"JSON: {result['outputs']['json_path']}")
        print(f"MD: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
