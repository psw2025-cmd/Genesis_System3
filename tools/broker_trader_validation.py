#!/usr/bin/env python3
"""Broker trader field multi-validation proof (cloud-authoritative by default)."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest" / "broker_trader_validation"
CLOUD = "https://genesis-system3-backend.onrender.com"


def fetch_cloud_truth() -> dict:
    with urllib.request.urlopen(f"{CLOUD}/api/broker/truth", timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def build_local_truth() -> dict:
    sys.path.insert(0, str(ROOT))
    try:
        from dashboard.backend.broker_truth_validator import build_broker_truth_report
    except ImportError:
        sys.path.insert(0, str(ROOT / "dashboard" / "backend"))
        from broker_truth_validator import build_broker_truth_report
    return build_broker_truth_report()


def main() -> int:
    use_local = "--local" in sys.argv
    report = build_local_truth() if use_local else fetch_cloud_truth()
    report["proof_source"] = "local" if use_local else "cloud"

    REPORT.mkdir(parents=True, exist_ok=True)
    with open(REPORT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    val = report.get("validation") or {}
    lines = [
        "# Broker Trader Validation",
        "",
        f"Source: **{report.get('proof_source', 'cloud')}**",
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
    ok = val.get("overall") in ("VALID", "PASS_WITH_WARNINGS")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
