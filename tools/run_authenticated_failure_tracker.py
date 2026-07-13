#!/usr/bin/env python3
"""Run the GitHub/Render failure tracker with a dashboard session.

Analyzer-safe proof helper:
- Establishes only the read-only dashboard session used by protected proof endpoints.
- Never prints or persists the API key, cookies, or response body.
- Does not call broker order routes.
- Fails closed: the underlying tracker records authentication failures as blockers.
"""
from __future__ import annotations

import http.cookiejar
import json
import os
import runpy
import urllib.error
import urllib.request


def install_dashboard_session() -> None:
    base = os.environ.get(
        "DASHBOARD_BASE_URL", "https://genesis-system3-backend.onrender.com"
    ).rstrip("/")
    api_key = os.environ.get("DASHBOARD_API_KEY", "")

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    urllib.request.install_opener(opener)

    # Missing credentials remain a proof blocker. Do not fabricate a session.
    if not api_key:
        os.environ["SYSTEM3_DASHBOARD_SESSION_STATUS"] = "MISSING_KEY"
        return

    payload = json.dumps({"api_key": api_key}).encode("utf-8")
    request = urllib.request.Request(
        base + "/api/auth/session",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": "system3-authenticated-render-proof",
        },
    )
    try:
        with opener.open(request, timeout=12) as response:
            # Do not read, print, or persist the response body.
            ok = 200 <= int(response.status) < 300
            os.environ["SYSTEM3_DASHBOARD_SESSION_STATUS"] = "AUTHENTICATED" if ok else "AUTH_FAILED"
    except urllib.error.HTTPError:
        os.environ["SYSTEM3_DASHBOARD_SESSION_STATUS"] = "AUTH_HTTP_ERROR"
    except Exception:
        os.environ["SYSTEM3_DASHBOARD_SESSION_STATUS"] = "AUTH_EXCEPTION"


if __name__ == "__main__":
    install_dashboard_session()
    runpy.run_path("tools/system3_github_render_failure_tracker.py", run_name="__main__")
