#!/usr/bin/env python3
"""System3 Render worker environment audit.

Safe diagnostics only:
- checks presence, never values
- never prints secrets
- never calls broker order routes
- live trading remains off
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "render_worker_env_audit"

REQUIRED = [
    "DHAN_CLIENT_ID",
    "DHAN_ACCESS_TOKEN",
    "WORKER_PUSH_TOKEN",
    "WEB_SERVICE_URL",
]
OPTIONAL = [
    "DHAN_APP_ID",
    "DHAN_APP_SECRET",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
    "DASHBOARD_API_KEY",
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def present(name: str) -> bool:
    return bool(os.environ.get(name, "").strip())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    required_presence = {name: present(name) for name in REQUIRED}
    optional_presence = {name: present(name) for name in OPTIONAL}
    live_flags = {
        "LIVE_TRADING_ENABLED": os.environ.get("LIVE_TRADING_ENABLED", "0"),
        "SYSTEM3_LIVE_TRADING_ALLOWED": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
        "ANALYZE_MODE": os.environ.get("ANALYZE_MODE", "1"),
        "SYSTEM3_MODE": os.environ.get("SYSTEM3_MODE", "analyzer"),
    }
    missing_required = [name for name, ok in required_presence.items() if not ok]
    unsafe_live = any(
        str(live_flags.get(name, "0")).strip().lower() not in ("0", "false", "", "none")
        for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED")
    )
    status = "PASS" if not missing_required and not unsafe_live else "BLOCKED"
    payload = {
        "generated_utc": utc(),
        "status": status,
        "required_presence": required_presence,
        "optional_presence": optional_presence,
        "missing_required": missing_required,
        "live_flags": live_flags,
        "worker_push_token_required_on_both_services": True,
        "worker_push_401_meaning": "WORKER_PUSH_TOKEN missing or different between Render web and worker",
        "dhan_401_meaning": "Dhan token/client-id invalid or worker/backend not reloaded after token update",
        "render_502_meaning": "backend web service crash/not started/wrong port/deploy blocked",
        "secrets_printed": False,
        "order_routes_called": False,
        "live_trading_enabled": False,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# System3 Render Worker Environment Audit",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        "",
        "## Required env presence",
        "",
        "| Env | Present |",
        "|---|---:|",
    ]
    for name, ok in required_presence.items():
        lines.append(f"| `{name}` | `{ok}` |")
    lines += [
        "",
        "## Interpretation",
        "",
        "- Worker push `401` means `WORKER_PUSH_TOKEN` is missing or different between Render web and worker.",
        "- Dhan `401` means Dhan token/client-id is invalid or the worker/backend has not reloaded after token update.",
        "- Backend `502` means backend web service crashed, did not start, listened on wrong port, or deploy is blocked.",
        "- This audit checks presence only and never prints secret values.",
        "- Live trading remains OFF.",
    ]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "missing_required": missing_required, "unsafe_live": unsafe_live}, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
