#!/usr/bin/env python3
"""
Pull DHAN_* env vars from Render into local .secrets/dhan.env (one-time laptop setup).

Requires Render API key (Dashboard -> Account Settings -> API Keys):
  set RENDER_API_KEY=rnd_...
  python tools/sync_render_secrets.py

Or place key in .secrets/render_api_key (single line, gitignored).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / ".secrets"
DHAN_ENV = SECRETS / "dhan.env"
KEY_FILE = SECRETS / "render_api_key"
SERVICE_NAME = os.environ.get("RENDER_SERVICE_NAME", "genesis-system3-backend")

DHAN_KEYS = (
    "DHAN_CLIENT_ID",
    "DHAN_APP_ID",
    "DHAN_APP_SECRET",
    "DHAN_ACCESS_TOKEN",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
)


def _api_key() -> str:
    k = os.environ.get("RENDER_API_KEY", "").strip()
    if not k and KEY_FILE.exists():
        k = KEY_FILE.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    if not k:
        raise SystemExit(
            "RENDER_API_KEY missing.\n" "  set RENDER_API_KEY=rnd_...   OR\n" "  echo rnd_... > .secrets/render_api_key"
        )
    return k


def _get(url: str, key: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _find_service_id(key: str) -> str:
    data = _get("https://api.render.com/v1/services?limit=50", key)
    for item in data:
        svc = item.get("service") or item
        name = svc.get("name") or svc.get("slug")
        if name == SERVICE_NAME:
            return svc["id"]
    raise SystemExit(f"Render service '{SERVICE_NAME}' not found")


def _fetch_env(key: str, service_id: str) -> dict[str, str]:
    out: dict[str, str] = {}
    cursor = ""
    while True:
        url = f"https://api.render.com/v1/services/{service_id}/env-vars?limit=100"
        if cursor:
            url += f"&cursor={cursor}"
        data = _get(url, key)
        for item in data:
            ev = item.get("envVar") or item
            k = ev.get("key", "")
            v = ev.get("value", "")
            if k in DHAN_KEYS and v:
                out[k] = v
        cursor = ""
        if isinstance(data, list) and len(data) < 100:
            break
        if not cursor:
            break
    return out


def _write_dhan_env(values: dict[str, str]) -> None:
    SECRETS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Auto-synced from Render — gitignored",
        "SYSTEM3_LIVE_TRADING_ALLOWED=0",
        "LIVE_TRADING_ENABLED=0",
        "",
    ]
    for k in DHAN_KEYS:
        if k in values:
            lines.append(f"{k}={values[k]}")
    DHAN_ENV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    key = _api_key()
    print(f"Fetching env from Render service: {SERVICE_NAME}")
    sid = _find_service_id(key)
    values = _fetch_env(key, sid)
    if not values:
        raise SystemExit("No DHAN_* vars returned — check Render dashboard env")

    missing = [k for k in DHAN_KEYS if k not in values]
    _write_dhan_env(values)
    print(f"Wrote {DHAN_ENV.relative_to(ROOT)} ({len(values)} keys)")
    for k in DHAN_KEYS:
        mark = "OK" if k in values else "MISSING"
        print(f"  {k}: {mark}")
    if missing:
        print(f"Warning: still missing {missing}")

    # Verify token
    sys.path.insert(0, str(ROOT))
    from core.brokers.dhan.token_manager import verify_token

    v = verify_token()
    print(f"Token valid: {v.get('valid')} ({v.get('reason', v.get('hours_remaining', ''))})")
    return 0 if not missing and v.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
