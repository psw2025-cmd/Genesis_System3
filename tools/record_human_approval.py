#!/usr/bin/env python3
"""Record owner human approval gate proof artifact (does NOT enable live trading)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "latest" / "human_approval_gate"


def main() -> int:
    try:
        from dashboard.backend.human_approval_service import build_approval_status
    except ImportError:
        sys.path.insert(0, str(ROOT / "dashboard" / "backend"))
        from human_approval_service import build_approval_status

    status = build_approval_status()
    REPORT.mkdir(parents=True, exist_ok=True)
    with open(REPORT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

    lines = [
        "# Human Approval Gate",
        "",
        f"Generated: `{status['generated_utc']}`",
        f"Human approval: **{'PASS' if status['human_approval'] else 'PEND'}**",
        f"Approved by: `{status.get('approved_by') or '—'}`",
        f"Live trading enabled: **{status['live_trading_enabled']}** (ENV kill switch unchanged)",
        "",
        "## Technical gates still required before ENV flip",
        *[f"- {g}" for g in status.get("technical_gates_still_required", [])],
        "",
        f"Note: {status.get('note', '')}",
    ]
    with open(REPORT / "summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {REPORT / 'summary.md'}")
    return 0 if status["human_approval"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
