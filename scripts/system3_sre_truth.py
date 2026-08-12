#!/usr/bin/env python3
"""Classify Genesis System3 SRE inventory and SLO evidence without mutations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.ops.operations_truth import REQUIRED_INVENTORY_CATEGORIES, evaluate_operations_truth

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT / "reports" / "latest" / "sre_operations_truth" / "inventory.json"
DEFAULT_SCORECARD = ROOT / "reports" / "latest" / "sre_operations_truth" / "scorecard_input.json"
DEFAULT_TARGETS = ROOT / "config" / "system3_sre_targets.json"
DEFAULT_OUTPUT = ROOT / "reports" / "latest" / "sre_operations_truth" / "evaluation.json"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _unknown_inventory() -> dict[str, Any]:
    return {
        category: {
            "state": "UNKNOWN",
            "items": [],
            "source": "not_collected",
            "observed_at": None,
            "reason": "inventory_evidence_missing",
        }
        for category in REQUIRED_INVENTORY_CATEGORIES
    }


def build_evidence(inventory_path: Path, scorecard_path: Path) -> dict[str, Any]:
    if inventory_path.is_file():
        raw_inventory = _read_json(inventory_path)
        inventory = raw_inventory.get("inventory")
        if not isinstance(inventory, dict):
            inventory = _unknown_inventory()
        architecture_map = raw_inventory.get("architecture_map", {"state": "UNKNOWN", "nodes": [], "edges": []})
        risk_register = raw_inventory.get("risk_register", [])
    else:
        inventory = _unknown_inventory()
        architecture_map = {"state": "UNKNOWN", "nodes": [], "edges": []}
        risk_register = []

    scorecard: dict[str, Any] = {}
    trends: dict[str, Any] = {}
    if scorecard_path.is_file():
        raw_scorecard = _read_json(scorecard_path)
        scorecard = raw_scorecard.get("scorecard") if isinstance(raw_scorecard.get("scorecard"), dict) else {}
        trends = raw_scorecard.get("trends") if isinstance(raw_scorecard.get("trends"), dict) else {}

    return {
        "inventory": inventory,
        "architecture_map": architecture_map,
        "risk_register": risk_register,
        "scorecard": scorecard,
        "trends": trends,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY))
    parser.add_argument("--scorecard", default=str(DEFAULT_SCORECARD))
    parser.add_argument("--targets", default=str(DEFAULT_TARGETS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    targets = _read_json(Path(args.targets))
    evidence = build_evidence(Path(args.inventory), Path(args.scorecard))
    report = evaluate_operations_truth(evidence, targets)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "OPERATIONS_TRUTH",
        json.dumps(
            {
                "state": report["state"],
                "inventory_state": report["inventory_state"],
                "scorecard_state": report["scorecard_state"],
                "full_sre_program_closed": report["full_sre_program_closed"],
                "live_trading_enabled": report["live_trading_enabled"],
                "real_orders_attempted": report["real_orders_attempted"],
                "output": str(output),
            },
            sort_keys=True,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
