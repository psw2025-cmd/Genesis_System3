#!/usr/bin/env python3
"""Fail-closed audit for incomplete or stale dashboard visual renders.

Reads only the committed dashboard visible-issue summary. It calls no network,
broker, scanner, paper, ML, or order endpoint and never reads secrets.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SOURCE = Path("reports/latest/dashboard_visible_issue_tracker/summary.json")
OUT_DIR = Path("reports/latest/dashboard_visual_loading_postflight")
EXPECTED_TABS = 16
MAX_SOURCE_AGE_SECONDS = 2 * 60 * 60

LOADING_MARKERS = (
    "checking...",
    "checking model artifacts",
    "loading production command intelligence",
    "genesis is loading",
    "loading...",
    "please wait",
)


def _parse_generated_at(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "BLOCKED",
        "source": str(SOURCE),
        "source_generated_at": None,
        "source_age_seconds": None,
        "source_fresh": False,
        "source_status": None,
        "auth_ok": False,
        "expected_tabs": EXPECTED_TABS,
        "tabs_checked": 0,
        "coverage_complete": False,
        "screenshots_complete": False,
        "visible_issue_count": None,
        "ui_exception_count": None,
        "global_exception_present": True,
        "loading_tabs": [],
        "analyzer_mode": True,
        "live_trading_enabled": False,
        "system3_live_trading_allowed": False,
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
            result["source_generated_at"] = source.get("generated_at")

            generated_at = _parse_generated_at(source.get("generated_at"))
            if generated_at is not None:
                age = max(0, int((datetime.now(timezone.utc) - generated_at).total_seconds()))
                result["source_age_seconds"] = age
                result["source_fresh"] = age <= MAX_SOURCE_AGE_SECONDS

            auth = source.get("auth") if isinstance(source.get("auth"), dict) else {}
            result["auth_ok"] = auth.get("ok") is True

            tabs = source.get("tabs") if isinstance(source.get("tabs"), list) else []
            result["tabs_checked"] = len(tabs)
            result["coverage_complete"] = len(tabs) == EXPECTED_TABS
            result["screenshots_complete"] = (
                int(source.get("screenshot_missing_count") or 0) == 0
                and all(tab.get("screenshot_ok") is True for tab in tabs)
            )
            result["visible_issue_count"] = int(source.get("visible_issue_count") or 0)
            result["ui_exception_count"] = int(source.get("ui_exception_count") or 0)
            result["global_exception_present"] = bool(source.get("global_exception"))

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

            source_pass = all(
                (
                    source.get("status") == "PASS",
                    source.get("production_grade_claim_allowed") is True,
                    result["source_fresh"],
                    result["auth_ok"],
                    result["coverage_complete"],
                    result["screenshots_complete"],
                    result["visible_issue_count"] == 0,
                    result["ui_exception_count"] == 0,
                    not result["global_exception_present"],
                    not result["loading_tabs"],
                )
            )

            if not result["source_fresh"]:
                result["blocker"] = "dashboard visual proof is missing a valid timestamp or is older than two hours"
            elif not result["auth_ok"]:
                result["blocker"] = "dashboard authentication is not proven"
            elif not result["coverage_complete"]:
                result["blocker"] = f"dashboard tab coverage incomplete: {len(tabs)}/{EXPECTED_TABS}"
            elif not result["screenshots_complete"]:
                result["blocker"] = "one or more required dashboard screenshots are missing or invalid"
            elif result["loading_tabs"]:
                result["blocker"] = "one or more tabs were captured before async content settled"
            elif result["visible_issue_count"] != 0:
                result["blocker"] = "dashboard visual proof still contains visible blockers"
            elif result["ui_exception_count"] != 0 or result["global_exception_present"]:
                result["blocker"] = "dashboard visual proof contains scanner or global exceptions"
            elif not source_pass:
                result["blocker"] = "source dashboard proof is not a strict PASS"
            else:
                result["status"] = "PASS"
                result["production_grade_claim_allowed"] = True
        except (OSError, ValueError, TypeError) as exc:
            result["blocker"] = f"summary parse failed: {type(exc).__name__}"

    (OUT_DIR / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Dashboard Visual Loading Postflight",
        "",
        f"Status: **{result['status']}**",
        f"Source status: `{result.get('source_status')}`",
        f"Source fresh: `{str(result['source_fresh']).lower()}`",
        f"Source age seconds: `{result.get('source_age_seconds')}`",
        f"Auth OK: `{str(result['auth_ok']).lower()}`",
        f"Tabs checked: `{result['tabs_checked']}/{result['expected_tabs']}`",
        f"Coverage complete: `{str(result['coverage_complete']).lower()}`",
        f"Screenshots complete: `{str(result['screenshots_complete']).lower()}`",
        f"Visible issues: `{result.get('visible_issue_count')}`",
        f"UI exceptions: `{result.get('ui_exception_count')}`",
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
        f"status={result['status']} tabs={result['tabs_checked']}/{result['expected_tabs']} "
        f"fresh={str(result['source_fresh']).lower()} auth_ok={str(result['auth_ok']).lower()} "
        f"loading_tabs={len(result['loading_tabs'])} "
        "live_trading=OFF order_routes_called=false"
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
