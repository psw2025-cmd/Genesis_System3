#!/usr/bin/env python3
"""Evaluate predeclared OOS factor/model decay evidence.

The command is read-only with respect to trading. It never retrains or promotes
models; a >15% configured IR deterioration can only emit RESEARCH_REQUIRED.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.quant.factor_decay import DecayPolicy, evaluate_decay

DEFAULT_POLICY = ROOT / "config" / "quant_decay_policy.json"
DEFAULT_OUT = ROOT / "reports" / "latest" / "quant_factor_decay" / "evaluation.json"
OFF = {"", "0", "false", "no", "off"}


def _read(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return obj


def _policy(path: Path) -> DecayPolicy:
    raw = _read(path).get("policy") or {}
    allowed = {item.name for item in fields(DecayPolicy)}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise ValueError(f"unknown decay policy keys: {unknown}")
    return DecayPolicy(**{key: raw[key] for key in raw if key in allowed})


def _assert_live_off() -> None:
    for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES"):
        if str(os.environ.get(key, "0")).strip().lower() not in OFF:
            raise SystemExit(f"DECAY_MONITOR_REFUSES_LIVE_ENV:{key}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--fail-on-research-required", action="store_true")
    args = parser.parse_args()

    _assert_live_off()
    if not args.evidence.is_file():
        result = {
            "schema_version": 1,
            "state": "DATA_ERROR",
            "blockers": [f"evidence_file_missing:{args.evidence}"],
            "research_required": False,
            "automatic_retraining_allowed": False,
            "model_auto_promotion_allowed": False,
            "position_size_change_allowed": False,
            "live_trading_enabled": False,
            "real_order_authority": False,
        }
    else:
        result = evaluate_decay(_read(args.evidence), _policy(args.policy))

    result["input_path"] = str(args.evidence)
    result["policy_path"] = str(args.policy)
    result["real_orders_attempted"] = 0
    result["paper_or_frozen_oos_only"] = True
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(
        "QUANT_FACTOR_DECAY "
        + json.dumps(
            {
                "state": result.get("state"),
                "research_required": result.get("research_required"),
                "deterioration_pct": (result.get("metrics") or {}).get("deterioration_pct"),
                "blocker_count": len(result.get("blockers") or []),
                "live_trading_enabled": False,
            },
            sort_keys=True,
        )
    )
    if args.fail_on_research_required and result.get("state") == "RESEARCH_REQUIRED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
