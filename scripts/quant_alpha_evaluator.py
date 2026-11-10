#!/usr/bin/env python3
"""Evaluate Genesis System3 quantitative evidence without enabling trading.

Default behavior classifies the existing costed walk-forward proof.  It writes a
machine-readable AlphaTruth report and exits successfully when evaluation itself
completed, even if performance is insufficient.  Promotion workflows may pass
--require-proven to turn a non-PROVEN research result into a non-zero exit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.quant.alpha_truth import AlphaTargets, evaluate_alpha_evidence, evaluate_legacy_costed_walkforward

DEFAULT_LEGACY = ROOT / "reports" / "latest" / "recent_backtest_walkforward_proof" / "costed_walkforward_proof.json"
DEFAULT_TARGETS = ROOT / "config" / "quant_alpha_targets.json"
DEFAULT_OUT = ROOT / "reports" / "latest" / "quant_alpha_evaluator" / "evaluation.json"
OFF_VALUES = {"", "0", "false", "no", "off"}


def _live_safety() -> None:
    for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES"):
        if str(os.environ.get(key, "0")).strip().lower() not in OFF_VALUES:
            raise SystemExit(f"ALPHATRUTH_REFUSES_LIVE_ENV:{key}")


def _git_sha() -> str:
    try:
        value = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
        return value if len(value) == 40 else "unknown"
    except Exception:
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _targets(path: Path) -> AlphaTargets:
    raw = _read_json(path)
    values = raw.get("targets") or {}
    allowed = {item.name for item in fields(AlphaTargets)}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"unknown AlphaTruth target keys: {unknown}")
    return AlphaTargets(**{key: values[key] for key in values if key in allowed})


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--evidence", type=Path, help="AlphaTruth evidence bundle JSON")
    source.add_argument(
        "--legacy-costed-proof",
        type=Path,
        default=None,
        help="Legacy costed walk-forward proof to classify",
    )
    parser.add_argument("--targets", type=Path, default=DEFAULT_TARGETS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--require-proven", action="store_true")
    args = parser.parse_args()

    _live_safety()
    targets = _targets(args.targets)
    evidence_path = args.evidence
    legacy_path = args.legacy_costed_proof
    mode = "alpha_evidence"
    if evidence_path is None:
        legacy_path = legacy_path or DEFAULT_LEGACY
        evidence_path = legacy_path
        mode = "legacy_costed_walkforward"

    if not evidence_path.is_file():
        result = {
            "schema_version": 1,
            "state": "DATA_ERROR",
            "blockers": [f"evidence_file_missing:{evidence_path}"],
            "research_candidate_allowed": False,
            "model_auto_promotion_allowed": False,
            "live_trading_enabled": False,
            "real_order_authority": False,
        }
    else:
        payload = _read_json(evidence_path)
        if mode == "legacy_costed_walkforward":
            result = evaluate_legacy_costed_walkforward(payload, targets)
        else:
            result = evaluate_alpha_evidence(payload, targets)
        result["input_sha256"] = _file_sha256(evidence_path)

    result.update(
        {
            "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            "evaluator": "AlphaTruth-v1",
            "evaluator_source_sha": _git_sha(),
            "input_path": str(evidence_path.relative_to(ROOT) if evidence_path.is_relative_to(ROOT) else evidence_path),
            "target_config_path": str(args.targets.relative_to(ROOT) if args.targets.is_relative_to(ROOT) else args.targets),
            "evaluation_mode": mode,
            "retry_budget": 5,
            "retry_exhaustion_action": "RESEARCH_REJECTED_AFTER_RETRY_BUDGET",
            "destructive_git_reset_allowed": False,
            "paper_or_analyzer_only": True,
            "live_trading_enabled": False,
            "real_orders_attempted": 0,
        }
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print("ALPHATRUTH " + json.dumps({
        "state": result.get("state"),
        "research_candidate_allowed": result.get("research_candidate_allowed"),
        "blocker_count": len(result.get("blockers") or []),
        "report": str(args.out),
        "live_trading_enabled": False,
    }, sort_keys=True))

    if args.require_proven and result.get("state") != "PROVEN":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
