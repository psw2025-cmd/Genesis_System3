#!/usr/bin/env python3
"""Fail-closed audit for incomplete dashboard visual renders.

Reads the committed dashboard visible-issue summary and detects tabs captured while
still showing transient loading placeholders. This tool is report-only: it calls no
network, broker, scanner, paper, ML, or order endpoint and never reads secrets.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("reports/latest/dashboard_visible_issue_tracker/summary.json")
OUT_DIR = Path("reports/latest/dashboard_visual_loading_postflight")

LOADING_MARKERS = (
    "checking...",
    "checking model artifacts",
    "loading production command intelligence",
    "genesis is loading",
)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "BLOCKED",
        "source": str(SOURCE),
        "source_status": None,
        "tabs_checked": 0,
        "loading_tabs": [],
        "analyzer_mode": True,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_read_or_persisted": False,
        "production_grade_claim_allowed": False,
    }

    if not SOURCE.exists():
        result["blocker"] = "dashboard visible-issue summary is missing"
    else:
        try:
            source = json.loads(SOURCE.read_text(encoding="utf-8"))
            result["source_status"] = source.get("status")
            tabs = source.get("tabs") if isinstance(source.get("tabs"), list) else []
            result["tabs_checked"] = len(tabs)

            for tab in tabs:
                sample = str(tab.get("body_text_sample") or "").lower()
                hits = sorted({marker for marker in LOADING_MARKERS if marker in sample})
                if hits:
                    result["loading_tabs"].append(
                        {
                            "id": tab.get("id"),
                            "title": tab.get("title"),
                            "markers": hits,
                        }
                    )

            if not result["loading_tabs"]:
                result["status"] = "PASS"
                result["production_grade_claim_allowed"] = bool(
                    source.get("status") == "PASS"
                    and source.get("production_grade_claim_allowed") is True
                )
            else:
                result["blocker"] = "one or more tabs were captured before async content settled"
        except (OSError, ValueError, TypeError) as exc:
            result["blocker"] = f"summary parse failed: {type(exc).__name__}"

    (OUT_DIR / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Dashboard Visual Loading Postflight",
        "",
        f"Status: **{result['status']}**",
        f"Source status: `{result.get('source_status')}`",
        f"Tabs checked: `{result['tabs_checked']}`",
        f"Loading tabs: `{len(result['loading_tabs'])}`",
        "Live trading: `OFF`",
        "Order routes called: `false`",
        f"Production-grade claim allowed: `{str(result['production_grade_claim_allowed']).lower()}`",
        "",
        "## Loading-state blockers",
        "",
    ]
    if result["loading_tabs"]:
        for item in result["loading_tabs"]:
            lines.append(f"- **{item.get('title') or item.get('id')}**: {', '.join(item['markers'])}")
    else:
        lines.append("- none")
    if result.get("blocker"):
        lines.extend(["", "## Blocker", "", f"- {result['blocker']}"])
    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        "DASHBOARD_LOADING_POSTFLIGHT "
        f"status={result['status']} tabs={result['tabs_checked']} loading_tabs={len(result['loading_tabs'])} "
        "live_trading=OFF order_routes_called=false"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
