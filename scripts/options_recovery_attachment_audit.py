#!/usr/bin/env python3
"""Cross-check a recovery proposal against actual frozen model evidence."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.options_research.recovery_diagnostics import (
    attachment_crosscheck,
    load_model_artifact_root,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    truthy = {"1", "true", "yes", "on"}
    enabled = [
        name for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED")
        if os.getenv(name, "0").strip().lower() in truthy
    ]
    if enabled:
        raise RuntimeError(f"live flags must remain disabled: {enabled}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    proof, trades = load_model_artifact_root(args.artifact_root)
    result = attachment_crosscheck(proof, trades)

    json_path = args.output_dir / "attachment_crosscheck.json"
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    feature_path = args.output_dir / "feature_feasibility.csv"
    with feature_path.open("w", newline="", encoding="utf-8") as handle:
        rows = result["feature_feasibility"]["rows"]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    cost_path = args.output_dir / "cost_stress.csv"
    with cost_path.open("w", newline="", encoding="utf-8") as handle:
        rows = result["cost_stress"]
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    markdown = [
        "# Genesis_System3 Recovery Attachment Cross-Check",
        "",
        f"- Status: **{result['status']}**",
        f"- Stop fraction: **{result['execution_semantics']['stop_loss_fraction']}**",
        f"- Stop percent: **{result['execution_semantics']['stop_loss_percent']}%**",
        f"- Target fraction: **{result['execution_semantics']['take_profit_fraction']}**",
        f"- Target percent: **{result['execution_semantics']['take_profit_percent']}%**",
        f"- Requested features: **{result['feature_feasibility']['requested_features']}**",
        f"- EOD-allowed features: **{result['feature_feasibility']['allowed_for_eod_implementation']}**",
        f"- Blocked/rejected features: **{result['feature_feasibility']['blocked_or_rejected']}**",
        "",
        "## Cost stress",
        "",
        "| Cost bps | Return | Profit factor | Sharpe | Max drawdown |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in result["cost_stress"]:
        markdown.append(
            f"| {row['cost_bps']:.0f} | {row['compounded_total_return']:.4%} | "
            f"{(row['profit_factor'] or 0):.4f} | "
            f"{(row['annualized_sharpe'] or 0):.4f} | "
            f"{row['maximum_drawdown']:.4%} |"
        )
    markdown += ["", "## Claim decisions", ""]
    for row in result["claims"]:
        markdown.append(f"- **{row['status']}** `{row['claim']}` — {row['proof']}")
    md_path = args.output_dir / "attachment_crosscheck.md"
    md_path.write_text("\n".join(markdown) + "\n", encoding="utf-8")

    manifest = {
        "status": result["status"],
        "files": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in (json_path, feature_path, cost_path, md_path)
        ],
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }
    manifest_path = args.output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
