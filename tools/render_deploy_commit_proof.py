#!/usr/bin/env python3
"""Analyzer-safe Render deployment commit proof.

Reads only /api/deploy/info, extracts Git commit metadata, and writes a
fail-closed report. Git SHAs are deployment metadata, not credentials.
No response body, token, cookie, broker payload, or order route is persisted.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_URL = os.environ.get(
    "RENDER_DEPLOY_BASE_URL", "https://genesis-system3-backend.onrender.com"
).rstrip("/")
EXPECTED = os.environ.get("GITHUB_SHA", "").strip().lower()
TIMEOUT = float(os.environ.get("RENDER_DEPLOY_TIMEOUT_S", "20"))
REPORT_DIR = Path("reports/latest/render_deploy_commit_proof")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def valid_sha(value: Any) -> str:
    text = str(value or "").strip().lower()
    return text if SHA_RE.fullmatch(text) else ""


def fetch_deployed_sha() -> tuple[int, str, str]:
    url = BASE_URL + "/api/deploy/info"
    headers = {"User-Agent": "Genesis-System3-Deploy-Commit-Proof/1.0"}
    api_key = os.environ.get("DASHBOARD_API_KEY", "").strip() or os.environ.get("API_KEY", "").strip()
    if api_key:
        headers["X-API-Key"] = api_key
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            status = int(getattr(response, "status", 0) or 0)
            payload = json.loads(response.read(256_000).decode("utf-8", errors="replace"))
            deployed = valid_sha(payload.get("git_sha") if isinstance(payload, dict) else "")
            return status, deployed, ""
    except urllib.error.HTTPError as exc:
        return int(exc.code), "", f"HTTP_{exc.code}"
    except Exception as exc:
        return 0, "", type(exc).__name__


def main() -> int:
    os.environ["ANALYZE_MODE"] = "1"
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"

    status, deployed, error = fetch_deployed_sha()
    expected = valid_sha(EXPECTED)
    exact_match = bool(expected and deployed and expected == deployed)
    prefix_match = bool(expected and deployed and deployed.startswith(expected[:7]))

    blockers: list[str] = []
    if not 200 <= status < 400:
        blockers.append("RENDER_DEPLOY_INFO_UNAVAILABLE")
    if status and not deployed:
        blockers.append("DEPLOYED_GIT_SHA_MISSING_OR_INVALID")
    if not expected:
        blockers.append("EXPECTED_GIT_SHA_MISSING_OR_INVALID")
    if expected and deployed and not prefix_match:
        blockers.append("RENDER_DEPLOY_COMMIT_MISMATCH")

    verdict = "PASS" if not blockers and exact_match else "BLOCKED"
    report = {
        "generated_utc": utc_now(),
        "verdict": verdict,
        "base_url": BASE_URL,
        "endpoint": "/api/deploy/info",
        "http_status": status,
        "expected_commit": expected or None,
        "deployed_commit": deployed or None,
        "exact_match": exact_match,
        "prefix_match": prefix_match,
        "blockers": blockers,
        "error_category": error or None,
        "safety": {
            "analyze_mode": "1",
            "live_trading_enabled": "0",
            "system3_live_trading_allowed": "0",
            "order_endpoints_called": False,
            "response_body_persisted": False,
            "secrets_written": False,
        },
        "production_grade_claim_allowed": False,
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    summary = [
        "# Render Deploy Commit Proof",
        "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Verdict: **{verdict}**",
        f"- HTTP status: `{status}`",
        f"- Expected commit: `{expected or 'unknown'}`",
        f"- Deployed commit: `{deployed or 'unknown'}`",
        f"- Exact match: `{exact_match}`",
        f"- Blockers: `{', '.join(blockers) if blockers else 'none'}`",
        "",
        "Live trading is OFF. No order route or response body was used.",
    ]
    (REPORT_DIR / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(json.dumps({"verdict": verdict, "http_status": status, "exact_match": exact_match, "blockers": blockers}))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
