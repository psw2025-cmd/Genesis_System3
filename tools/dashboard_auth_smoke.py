#!/usr/bin/env python3
"""Smoke-test dashboard API-key session auth with a dummy key."""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["REQUIRE_API_KEY"] = "true"
os.environ["API_KEY"] = "dummy"
os.environ["LIVE_TRADING_ENABLED"] = "0"
os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
os.environ["DEFER_INSTRUMENT_WARMUP"] = "1"
os.environ["CLOUD_PAPER_ENGINE"] = "0"

app_module = importlib.import_module("dashboard.backend.app")


class FakeRequest:
    def __init__(
        self, path: str = "/api/state", headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None
    ):
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.url = SimpleNamespace(path=path, scheme="http")


async def main() -> int:
    locked_req = FakeRequest()
    locked = app_module._has_dashboard_api_access(locked_req)
    if locked:
        raise SystemExit("expected request without header/cookie to be locked")

    header_req = FakeRequest(headers={"X-API-Key": "dummy"})
    if not app_module._has_dashboard_api_access(header_req):
        raise SystemExit("expected X-API-Key request to pass")

    bad_payload = app_module.DashboardAuthRequest(api_key="wrong")
    try:
        await app_module.create_dashboard_session(bad_payload, FakeRequest(path="/api/auth/session"))
    except app_module.HTTPException as exc:
        if exc.status_code != 401:
            raise SystemExit(f"expected wrong key 401, got {exc.status_code}")
    else:
        raise SystemExit("expected wrong key to raise HTTPException")

    good_payload = app_module.DashboardAuthRequest(api_key="dummy")
    response = await app_module.create_dashboard_session(good_payload, FakeRequest(path="/api/auth/session"))
    cookie_header = response.headers.get("set-cookie", "")
    if "system3_dashboard_session=" not in cookie_header or "HttpOnly" not in cookie_header:
        raise SystemExit(f"expected HttpOnly dashboard session cookie, got {cookie_header!r}")

    token = app_module._dashboard_session_token()
    cookie_req = FakeRequest(cookies={"system3_dashboard_session": token})
    if not app_module._has_dashboard_api_access(cookie_req):
        raise SystemExit("expected dashboard session cookie to pass")

    status = await app_module.dashboard_auth_status(cookie_req)
    if not status.get("authenticated"):
        raise SystemExit(f"expected authenticated status, got {status}")

    print(
        {
            "locked_without_auth": locked,
            "header_auth": True,
            "bad_key_status": 401,
            "cookie_httponly": True,
            "cookie_auth": True,
            "auth_status": status,
            "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED"),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
