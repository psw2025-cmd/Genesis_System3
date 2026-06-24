"""
System3 Phase 150 - Phase Dependency Graph (Static)

Maps each phase to its inputs/outputs (static mapping).
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON_PATH = STORAGE_ULTRA / "phase150_dependency_graph.json"

# Static dependency mapping (hard-coded)
DEPENDENCY_GRAPH = {
    "131": {
        "inputs": [],
        "outputs": [
            "storage/config/system3_master_session_config.json",
            "storage/ultra/phase131_master_session_config_report.md",
        ],
    },
    "132": {
        "inputs": ["storage/config/system3_master_session_config.json"],
        "outputs": [
            "storage/ultra/phase132_master_health_snapshot.json",
            "storage/ultra/phase132_master_health_snapshot.md",
        ],
    },
    "133": {
        "inputs": [
            "storage/config/system3_master_session_config.json",
            "storage/ultra/phase132_master_health_snapshot.json",
        ],
        "outputs": [
            "storage/config/system3_master_safety_state.json",
            "storage/ultra/phase133_master_safety_report.md",
        ],
    },
    "134": {
        "inputs": [
            "storage/config/system3_master_session_config.json",
            "storage/config/system3_master_safety_state.json",
        ],
        "outputs": ["storage/ultra/phase134_master_session_plan.json", "storage/ultra/phase134_master_session_plan.md"],
    },
    "135": {
        "inputs": [
            "storage/config/system3_master_session_config.json",
            "storage/ultra/phase132_master_health_snapshot.json",
            "storage/config/system3_master_safety_state.json",
            "storage/ultra/phase134_master_session_plan.json",
        ],
        "outputs": ["storage/ultra/phase135_master_session_summary.md"],
    },
    "136": {
        "inputs": [],
        "outputs": [
            "storage/ultra/phase136_dhan_symbol_universe.csv",
            "storage/ultra/phase136_dhan_symbol_universe.json",
        ],
    },
    "137": {
        "inputs": ["storage/ultra/phase136_dhan_symbol_universe.csv"],
        "outputs": ["storage/ultra/phase137_expiry_calendar_map.csv"],
    },
    "138": {
        "inputs": ["storage/ultra/phase136_dhan_symbol_universe.csv"],
        "outputs": ["storage/ultra/phase138_risk_tiers.csv"],
    },
    "139": {
        "inputs": ["storage/ultra/phase136_dhan_symbol_universe.csv"],
        "outputs": ["storage/ultra/phase139_lot_margin.csv"],
    },
    "140": {
        "inputs": ["storage/ultra/phase139_lot_margin.csv"],
        "outputs": ["storage/ultra/phase140_capital_guardrail.csv", "storage/ultra/phase140_capital_guardrail.md"],
    },
    "141": {
        "inputs": ["storage/live/dhan_index_ai_signals.csv"],
        "outputs": ["storage/ultra/phase141_spread_liquidity_metrics.csv"],
    },
    "142": {
        "inputs": ["storage/live/live_orders_ledger.csv", "storage/ultra/phase141_spread_liquidity_metrics.csv"],
        "outputs": ["storage/ultra/phase142_slippage_results.csv", "storage/ultra/phase142_slippage_summary.md"],
    },
    "143": {
        "inputs": ["storage/ultra/phase142_slippage_results.csv"],
        "outputs": ["storage/ultra/phase143_execution_quality.csv", "storage/ultra/phase143_execution_quality.md"],
    },
    "144": {
        "inputs": [
            "storage/live/live_orders_ledger.csv",
            "storage/ultra/phase142_slippage_results.csv",
            "storage/ultra/phase143_execution_quality.csv",
        ],
        "outputs": [
            "storage/ultra/phase144_pnl_execution_scenarios.csv",
            "storage/ultra/phase144_pnl_execution_scenarios.md",
        ],
    },
    "145": {
        "inputs": [
            "storage/ultra/phase140_capital_guardrail.csv",
            "storage/ultra/phase142_slippage_results.csv",
            "storage/ultra/phase143_execution_quality.csv",
            "storage/ultra/phase144_pnl_execution_scenarios.csv",
        ],
        "outputs": ["storage/ultra/phase145_one_lot_health_report.md"],
    },
}


def run_phase150_dependency_graph() -> Dict[str, Any]:
    """
    Generate phase dependency graph.

    Returns:
        dict: {
            "phase": 150,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Build dependency graph data
        graph_data = {
            "timestamp": datetime.now().isoformat(),
            "dependency_graph": DEPENDENCY_GRAPH,
        }

        # Save JSON
        with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)

        status = "OK"
        details = f"Dependency graph generated: {len(DEPENDENCY_GRAPH)} phases"

        return {
            "phase": 150,
            "status": status,
            "details": details,
            "outputs": {
                "json_path": str(OUTPUT_JSON_PATH),
                "phase_count": len(DEPENDENCY_GRAPH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 150,
            "status": "ERROR",
            "details": f"Phase 150 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 150 - PHASE DEPENDENCY GRAPH")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase150_dependency_graph()

    print(f"Phase150: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nPhases mapped: {result['outputs']['phase_count']}")
        print(f"JSON: {result['outputs']['json_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
