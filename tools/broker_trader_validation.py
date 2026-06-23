#!/usr/bin/env python3
"""Broker trader field multi-validation proof."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest" / "broker_trader_validation"


def main() -> int:
    sys.path.insert(0, str(ROOT))
    try:
        from dashboard.backend.broker_truth_validator import build_broker_truth_report
    except ImportError:
        sys.path.insert(0, str(ROOT / "dashboard" / "backend"))
        from broker_truth_validator import build_broker_truth_report

    report = build_broker_truth_report()
    REPORT.mkdir(parents=True, exist_ok=True)
    with open(REPORT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    val = report.get("validation") or {}
    lines = [
        "# Broker Trader Validation",
        "",
        f"Overall: **{val.get('overall')}**",
        f"Valid fields: **{val.get('valid_count')}/{val.get('total_fields')}** ({val.get('valid_pct')}%)",
        f"Broker connected: **{report.get('broker_connected')}**",
        f"Data source: `{report.get('data_source')}`",
        "",
        "## Trader fields",
    ]
    for k, v in (report.get("trader_fields") or {}).items():
        lines.append(f"- {k}: {v.get('status')} valid={v.get('valid')} value={v.get('value')}")

    with open(REPORT / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {REPORT / 'summary.md'}")
    return 0 if val.get("overall") in ("VALID", "PASS_WITH_WARNINGS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
