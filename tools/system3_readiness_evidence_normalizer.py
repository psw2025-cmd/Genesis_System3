#!/usr/bin/env python3
"""Normalize latest System3 proof without weakening readiness gates.

This analyzer-only postprocessor separates:
- live Render visual/transport proof;
- trade-readiness proof;
- operational blockers such as broker session, chains, scheduler and deploy drift.

It never calls network, broker or order endpoints and never reads secrets.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "reports/latest/system3_public_truth/index.json"
TODO = ROOT / "reports/latest/todo_status_update/summary.json"
OUT = ROOT / "reports/latest/readiness_evidence_normalized"


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def main() -> int:
    public = load(PUBLIC)
    todo = load(TODO)
    live = (((public.get("summaries") or {}).get("dashboard_live_ui_proof") or {}).get("summary_json") or {})
    cloud = (((public.get("summaries") or {}).get("cloud_runtime_check") or {}).get("summary_json") or {})

    ui_rows = [row for row in (live.get("ui") or []) if isinstance(row, dict)]
    api_rows = [row for row in (live.get("api") or []) if isinstance(row, dict)]
    screenshots_ok = bool(ui_rows) and all(row.get("screenshot_ok") is True for row in ui_rows)
    ui_content_ok = bool(ui_rows) and all(row.get("ok") is True for row in ui_rows)
    api_transport_ok = bool(api_rows) and all(row.get("ok") is True for row in api_rows if not row.get("optional"))
    infra_blockers = list(live.get("infra_blockers") or [])
    readiness_blockers = list(live.get("trade_readiness_blockers") or live.get("blockers") or [])

    visual_capture_pass = screenshots_ok and ui_content_ok and api_transport_ok and not infra_blockers
    trade_ready = live.get("final_verdict") == "PASS" and not readiness_blockers

    warnings = [w for w in (cloud.get("warnings") or []) if isinstance(w, dict)]
    operational_blockers = [
        {"key": str(w.get("key") or "unknown"), "message": str(w.get("message") or "")}
        for w in warnings
    ]

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if trade_ready else "BLOCKED_NOT_TRADE_READY",
        "visual_capture_pass": visual_capture_pass,
        "api_transport_pass": api_transport_ok,
        "trade_ready": trade_ready,
        "production_grade_claim_allowed": bool(trade_ready),
        "readiness_blockers": readiness_blockers,
        "infra_blockers": infra_blockers,
        "operational_blockers": operational_blockers,
        "todo": {
            "status": todo.get("status", "MISSING"),
            "total": int(todo.get("total") or 0),
            "reason": str(todo.get("reason") or ""),
        },
        "safety": {
            "analyze_mode": "1",
            "live_trading_enabled": "0",
            "system3_live_trading_allowed": "0",
            "broker_order_endpoints_called": False,
            "secrets_read_or_written": False,
        },
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# System3 Readiness Evidence — Normalized",
        "",
        f"- Status: **{payload['status']}**",
        f"- Visual capture PASS: `{visual_capture_pass}`",
        f"- Read-only API transport PASS: `{api_transport_ok}`",
        f"- Trade ready: `{trade_ready}`",
        f"- Production-grade claim allowed: `{payload['production_grade_claim_allowed']}`",
        f"- Analyzer mode: `ON`",
        f"- Live trading: `OFF`",
        "",
        "## Readiness blockers",
    ]
    lines.extend([f"- `{item}`" for item in readiness_blockers] or ["- None"])
    lines.extend(["", "## Operational blockers"])
    lines.extend([f"- `{item['key']}` — {item['message']}" for item in operational_blockers] or ["- None"])
    lines.extend([
        "",
        "## 1000+ TODO",
        f"- Status: `{payload['todo']['status']}`",
        f"- Parsed items: `{payload['todo']['total']}`",
        f"- Reason: `{payload['todo']['reason']}`",
        "",
    ])
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "status": payload["status"],
        "visual_capture_pass": visual_capture_pass,
        "trade_ready": trade_ready,
        "readiness_blocker_count": len(readiness_blockers),
        "operational_blocker_count": len(operational_blockers),
        "todo_total": payload["todo"]["total"],
        "live_trading": "OFF",
    }, sort_keys=True))
    return 0 if visual_capture_pass else 2


if __name__ == "__main__":
    raise SystemExit(main())
