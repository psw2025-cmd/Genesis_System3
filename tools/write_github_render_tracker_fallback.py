#!/usr/bin/env python3
"""Write fail-closed GitHub/Render tracker summary when the main tracker crashes."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path("reports/latest/github_render_failure_tracker")
DOC = Path("docs/SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "BLOCKED",
        "tracker_internal_status": "FAILED_BEFORE_SUMMARY",
        "todo": [
            "Tracker script failed before summary.json was written; inspect checkout/setup/preflight/tracker step logs."
        ],
        "todo_count": 1,
        "github_failed_count": None,
        "render_failed_count": None,
        "failed_workflows": [],
        "render_failures": [],
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "response_bodies_persisted": False,
        "production_grade_claim_allowed": False,
        "report_only_no_self_failure_storm": True,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = (
        "# System3 GitHub + Render Failure TODO\n\n"
        "Status: **BLOCKED**\n\n"
        "Tracker failed before writing normal summary. Inspect workflow step logs.\n"
    )
    (OUT / "summary.md").write_text(md, encoding="utf-8")
    DOC.write_text(md, encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
