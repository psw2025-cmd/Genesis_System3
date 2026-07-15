#!/usr/bin/env python3
"""Analyzer-safe live frontend deployment provenance gate.

Reads only a public static build manifest and compares it with the checked-out
Sidebar source. It never calls trading, broker, scanner, paper, or mutation
routes and never reads or writes credentials.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDEBAR = ROOT / "dashboard/frontend/src/components/Sidebar.tsx"
OUT = ROOT / "reports/latest/dashboard_deploy_provenance"
BASE = os.environ.get("DASHBOARD_BASE_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
URL = f"{BASE}/ui/deploy-provenance.json"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    local_sha = hashlib.sha256(SIDEBAR.read_bytes()).hexdigest()
    http_status = 0
    remote: dict = {}
    error_type = ""
    try:
        request = urllib.request.Request(URL, headers={"Cache-Control": "no-cache", "User-Agent": "system3-analyzer-proof/1"})
        with urllib.request.urlopen(request, timeout=20) as response:
            http_status = int(response.status)
            remote = json.loads(response.read(4096).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        http_status = int(exc.code)
        error_type = "HTTP_ERROR"
    except (urllib.error.URLError, TimeoutError):
        error_type = "NETWORK_OR_TIMEOUT"
    except (json.JSONDecodeError, UnicodeDecodeError):
        error_type = "INVALID_MANIFEST"

    remote_sha = str(remote.get("sidebar_sha256") or "")
    safe_manifest = (
        http_status == 200
        and remote.get("schema") == 1
        and remote.get("sim_live_required") is True
        and remote.get("live_trading_enabled") is False
        and len(remote_sha) == 64
    )
    matched = safe_manifest and remote_sha == local_sha
    status = "PASS" if matched else "BLOCKED"
    blocker = "" if matched else (
        "DEPLOY_PROVENANCE_NOT_PUBLISHED" if http_status == 404 else
        "DEPLOYED_FRONTEND_SOURCE_MISMATCH" if safe_manifest else
        "DEPLOY_PROVENANCE_UNAVAILABLE_OR_INVALID"
    )
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": BASE,
        "status": status,
        "http_status": http_status,
        "error_type": error_type,
        "local_sidebar_sha256": local_sha,
        "deployed_sidebar_sha256": remote_sha,
        "source_match": matched,
        "sim_live_required": bool(remote.get("sim_live_required")) if remote else False,
        "blocker": blocker,
        "analyzer_mode": True,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_persisted": False,
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.md").write_text(
        "# Dashboard Deploy Provenance\n\n"
        f"Generated: {data['generated_at']}\n\n"
        f"Status: **{status}**\n\n"
        f"- HTTP: `{http_status}`\n"
        f"- Source fingerprint match: `{matched}`\n"
        f"- Blocker: `{blocker or 'none'}`\n"
        "- Analyzer mode: `ON`\n- Live trading: `OFF`\n",
        encoding="utf-8",
    )
    print(json.dumps({k: data[k] for k in ("status", "http_status", "source_match", "blocker")}, indent=2))
    return 0 if matched else 1


if __name__ == "__main__":
    raise SystemExit(main())
