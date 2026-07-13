#!/usr/bin/env python3
"""System3 Render Worker Preflight Audit.

Purpose:
- Diagnose worker env/config issues without printing secrets.
- Verify backend reachability and push-token presence/mismatch symptoms.
- Verify Dhan env presence only by safe booleans/lengths.
- Never call live order routes.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "render_worker_preflight"
DEFAULT_BACKEND = "https://genesis-system3-backend.onrender.com"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def secret_state(name: str, min_len: int = 1) -> Dict[str, Any]:
    val = os.environ.get(name, "")
    stripped = val.strip()
    return {
        "name": name,
        "present": bool(stripped),
        "length_ok": len(stripped) >= min_len,
        "length": len(stripped) if stripped else 0,
    }


def probe(url: str, token: str = "") -> Dict[str, Any]:
    headers = {"User-Agent": "system3-render-worker-preflight"}
    if token:
        headers["X-Worker-Token"] = token
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": 200 <= int(resp.status) < 400, "status_code": int(resp.status), "error_type": None}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status_code": int(exc.code), "error_type": "HTTPError"}
    except Exception as exc:
        return {"ok": False, "status_code": 0, "error_type": type(exc).__name__}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    backend = os.environ.get("WEB_SERVICE_URL") or os.environ.get("SYSTEM3_API_BASE") or DEFAULT_BACKEND
    backend = backend.rstrip("/")
    worker_push_token = os.environ.get("WORKER_PUSH_TOKEN", "").strip()

    env_checks = {
        "DHAN_CLIENT_ID": secret_state("DHAN_CLIENT_ID", 3),
        "DHAN_ACCESS_TOKEN": secret_state("DHAN_ACCESS_TOKEN", 20),
        "DHAN_PIN": secret_state("DHAN_PIN", 4),
        "DHAN_TOTP_SECRET": secret_state("DHAN_TOTP_SECRET", 8),
        "WEB_SERVICE_URL": secret_state("WEB_SERVICE_URL", 8),
        "SYSTEM3_API_BASE": secret_state("SYSTEM3_API_BASE", 8),
        "WORKER_PUSH_TOKEN": secret_state("WORKER_PUSH_TOKEN", 8),
    }

    backend_health = probe(f"{backend}/api/health")
    backend_state = probe(f"{backend}/api/state")
    scheduler_push_probe = probe(f"{backend}/api/scheduler/health/push", worker_push_token)
    chain_push_probe = probe(f"{backend}/api/chain/push", worker_push_token)

    blockers = []
    if not backend_health.get("ok"):
        blockers.append(f"backend /api/health not reachable: status={backend_health.get('status_code')} error={backend_health.get('error_type')}")
    if not backend_state.get("ok"):
        blockers.append(f"backend /api/state not reachable: status={backend_state.get('status_code')} error={backend_state.get('error_type')}")
    if not env_checks["DHAN_CLIENT_ID"]["present"]:
        blockers.append("DHAN_CLIENT_ID missing in worker env")
    if not env_checks["DHAN_ACCESS_TOKEN"]["length_ok"]:
        blockers.append("DHAN_ACCESS_TOKEN missing/too short in worker env")
    if not env_checks["WORKER_PUSH_TOKEN"]["length_ok"]:
        blockers.append("WORKER_PUSH_TOKEN missing/too short in worker env")
    if scheduler_push_probe.get("status_code") == 401 or chain_push_probe.get("status_code") == 401:
        blockers.append("WORKER_PUSH_TOKEN rejected by backend; token missing or different between web and worker")
    if backend_health.get("status_code") == 502 or backend_state.get("status_code") == 502:
        blockers.append("backend web service returning 502; worker push cannot succeed until backend restarts/deploys")

    payload = {
        "generated_utc": utc(),
        "status": "PASS" if not blockers else "BLOCKED",
        "backend_base": backend,
        "env_checks": env_checks,
        "probes": {
            "backend_health": backend_health,
            "backend_state": backend_state,
            "scheduler_push_probe": scheduler_push_probe,
            "chain_push_probe": chain_push_probe,
        },
        "blockers": blockers,
        "safety": {
            "live_trading_enabled": False,
            "order_routes_called": False,
            "secrets_printed": False,
            "dhan_order_routes_called": False,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# System3 Render Worker Preflight",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Backend base: `{backend}`",
        "",
        "## Blockers",
        "",
    ]
    md += [f"- [ ] {b}" for b in blockers] or ["- [x] No worker preflight blockers detected."]
    md += [
        "",
        "## Safe env presence checks",
        "",
        "| Name | Present | Length OK | Length |",
        "|---|---:|---:|---:|",
    ]
    for item in env_checks.values():
        md.append(f"| `{item['name']}` | {item['present']} | {item['length_ok']} | {item['length']} |")
    md += [
        "",
        "## Safety",
        "",
        "- Live trading enabled: `false`",
        "- Order routes called: `false`",
        "- Secrets printed: `false`",
    ]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "blocker_count": len(blockers),
        "backend_health": backend_health,
        "backend_state": backend_state,
        "scheduler_push_status": scheduler_push_probe.get("status_code"),
        "chain_push_status": chain_push_probe.get("status_code"),
        "live_trading_enabled": False,
        "order_routes_called": False,
    }, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
