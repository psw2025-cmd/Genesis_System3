#!/usr/bin/env python3
"""System3 dashboard auto snapshot proof.

Read-only against the dashboard/backend. Writes only latest proof files under
reports/latest/dashboard_auto_snap by default. Optional git push is restricted
to that proof folder only.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com/ui").rstrip("/")
BACKEND_URL = os.getenv("BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
SNAP_DIR = Path(os.getenv("SNAP_DIR", "reports/latest/dashboard_auto_snap"))
AUTO_GIT_PUSH = os.getenv("AUTO_GIT_PUSH", "1").strip().lower() in {"1", "true", "yes", "on"}
GIT_PUSH_INTERVAL_S = int(os.getenv("GIT_PUSH_INTERVAL_S", "300") or "300")
TIMEOUT_S = int(os.getenv("DASHBOARD_SNAP_TIMEOUT_S", "25") or "25")

API_ENDPOINTS = {
    "health": "/api/health",
    "state": "/api/state",
    "qc": "/api/qc",
    "broker_status": "/api/broker/dhan/status",
    "instruments_health": "/api/instruments/health",
    "underlyings": "/api/underlyings",
    "chain_nifty": "/api/chain/NIFTY",
    "auto_gates": "/api/auto_gates",
    "paper": "/api/paper",
}

REDACT_KEY_RE = re.compile(r"(token|secret|password|pin|totp|otp|authorization|cookie|key)", re.I)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            if REDACT_KEY_RE.search(str(k)):
                if isinstance(v, bool):
                    out[k] = v
                elif v in (None, "", False):
                    out[k] = v
                else:
                    out[k] = "<redacted>"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(redact(data), indent=2, ensure_ascii=False), encoding="utf-8")


def fetch_url(url: str, accept: str = "application/json,text/html,*/*") -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "System3-dashboard-auto-snap/1.0",
            "Accept": accept,
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:  # nosec: user-configured proof URL only
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            data = None
            try:
                data = json.loads(text)
            except Exception:
                pass
            return {
                "url": url,
                "ok": 200 <= int(resp.status) < 300,
                "status": int(resp.status),
                "elapsed_s": round(time.time() - started, 3),
                "content_type": headers.get("content-type"),
                "x_frontend": headers.get("x-frontend"),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "data": data,
                "text": None if data is not None else text,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return {
            "url": url,
            "ok": False,
            "status": int(exc.code),
            "elapsed_s": round(time.time() - started, 3),
            "content_type": None,
            "x_frontend": None,
            "bytes": len(body),
            "sha256": sha256_text(body),
            "data": None,
            "text": body[:4000],
            "error": f"HTTPError: {exc}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": url,
            "ok": False,
            "status": None,
            "elapsed_s": round(time.time() - started, 3),
            "content_type": None,
            "x_frontend": None,
            "bytes": 0,
            "sha256": None,
            "data": None,
            "text": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def iter_paths(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, val in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, val
            yield from iter_paths(val, path)
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            path = f"{prefix}[{idx}]"
            yield path, val
            yield from iter_paths(val, path)


def truthy_path_hits(payloads: Dict[str, Any], key_name: str) -> list[dict[str, Any]]:
    hits = []
    for name, data in payloads.items():
        for path, value in iter_paths(data):
            if path.split(".")[-1] == key_name and value is True:
                hits.append({"payload": name, "path": path, "value": value})
    return hits


def capture_screenshots() -> Dict[str, Any]:
    result: Dict[str, Any] = {"enabled": True, "desktop": None, "mobile": None, "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:  # noqa: BLE001
        result["enabled"] = False
        result["errors"].append(f"playwright_not_available: {type(exc).__name__}: {exc}")
        return result

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=90000)
            page.wait_for_timeout(2500)
            page.screenshot(path=str(SNAP_DIR / "latest_dashboard.png"), full_page=True)
            result["desktop"] = "latest_dashboard.png"

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
            mobile.goto(DASHBOARD_URL, wait_until="networkidle", timeout=90000)
            mobile.wait_for_timeout(2500)
            mobile.screenshot(path=str(SNAP_DIR / "latest_mobile.png"), full_page=True)
            result["mobile"] = "latest_mobile.png"
            browser.close()
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"screenshot_failed: {type(exc).__name__}: {exc}")
    return result


def run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(args, cwd=Path.cwd(), capture_output=True, text=True, timeout=60)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def maybe_git_push(verdict: Dict[str, Any]) -> Dict[str, Any]:
    info: Dict[str, Any] = {"enabled": AUTO_GIT_PUSH, "attempted": False, "pushed": False, "details": []}
    if not AUTO_GIT_PUSH:
        return info

    last_push_file = SNAP_DIR / ".last_push_epoch"
    now = int(time.time())
    last = 0
    if last_push_file.exists():
        try:
            last = int(last_push_file.read_text().strip() or "0")
        except Exception:
            last = 0

    forced = bool(verdict.get("critical") or verdict.get("warnings"))
    if not forced and (now - last) < GIT_PUSH_INTERVAL_S:
        info["details"].append(f"skip_push_interval_remaining_s={GIT_PUSH_INTERVAL_S - (now - last)}")
        return info

    info["attempted"] = True
    # Hard restriction: only this proof folder is staged.
    commands = [
        ["git", "add", "reports/latest/dashboard_auto_snap/"],
        ["git", "diff", "--cached", "--quiet"],
    ]
    rc, out = run_git(commands[0])
    info["details"].append(f"git_add_rc={rc} {out[:200]}")
    rc, out = run_git(commands[1])
    if rc == 0:
        info["details"].append("no_staged_changes")
        last_push_file.write_text(str(now), encoding="utf-8")
        return info

    msg = "auto: refresh dashboard latest snapshot"
    rc, out = run_git(["git", "commit", "-m", msg])
    info["details"].append(f"git_commit_rc={rc} {out[:500]}")
    if rc != 0:
        return info
    rc, out = run_git(["git", "push"])
    info["details"].append(f"git_push_rc={rc} {out[:500]}")
    info["pushed"] = rc == 0
    if info["pushed"]:
        last_push_file.write_text(str(now), encoding="utf-8")
    return info


def main() -> int:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    ui_res = fetch_url(DASHBOARD_URL, accept="text/html,*/*")
    write_json(SNAP_DIR / "latest_ui_response.json", {k: v for k, v in ui_res.items() if k != "text"})
    if ui_res.get("text"):
        (SNAP_DIR / "latest_ui_preview.txt").write_text(str(ui_res.get("text"))[:4000], encoding="utf-8")

    payloads: Dict[str, Any] = {}
    endpoint_matrix: Dict[str, Any] = {}
    for name, endpoint in API_ENDPOINTS.items():
        res = fetch_url(BACKEND_URL + endpoint)
        endpoint_matrix[name] = {k: v for k, v in res.items() if k not in {"data", "text"}}
        data = res.get("data") if res.get("data") is not None else {"text_preview": res.get("text"), "error": res.get("error")}
        payloads[name] = data
        write_json(SNAP_DIR / f"latest_{name}.json", data)

    screenshot = capture_screenshots()

    live_hits = truthy_path_hits(payloads, "live_trading_enabled")
    order_hits = truthy_path_hits(payloads, "order_placement_allowed")
    state = payloads.get("state") if isinstance(payloads.get("state"), dict) else {}
    health = payloads.get("health") if isinstance(payloads.get("health"), dict) else {}
    qc = payloads.get("qc") if isinstance(payloads.get("qc"), dict) else {}
    chain = payloads.get("chain_nifty") if isinstance(payloads.get("chain_nifty"), dict) else {}

    warnings: list[str] = []
    critical: list[str] = []
    if not ui_res.get("ok"):
        critical.append("DASHBOARD_UI_NOT_OK")
    if live_hits:
        critical.append("LIVE_TRADING_ENABLED_TRUE_IN_API")
    if order_hits:
        critical.append("ORDER_PLACEMENT_ALLOWED_TRUE_IN_API")
    if str(state.get("mode", "")).upper() == "LIVE":
        critical.append("STATE_MODE_LIVE")
    if ui_res.get("x_frontend") == "vue-legacy":
        warnings.append("LEGACY_VUE_FRONTEND_SERVED")
    if "{{" in str(ui_res.get("text") or "") and "}}" in str(ui_res.get("text") or ""):
        warnings.append("RAW_TEMPLATE_TOKENS_IN_HTML")
    if not screenshot.get("desktop"):
        warnings.append("DESKTOP_SCREENSHOT_NOT_CREATED")
    if not screenshot.get("mobile"):
        warnings.append("MOBILE_SCREENSHOT_NOT_CREATED")
    if not endpoint_matrix.get("chain_nifty", {}).get("ok"):
        warnings.append("CHAIN_NIFTY_ENDPOINT_NOT_OK")

    verdict = {
        "generated_utc": utc_now(),
        "dashboard_url": DASHBOARD_URL,
        "backend_url": BACKEND_URL,
        "frontend_header": ui_res.get("x_frontend"),
        "critical": critical,
        "warnings": warnings,
        "final_verdict": "FAIL" if critical else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
        "mode": state.get("mode") or health.get("mode"),
        "broker_connected": (state.get("broker") or {}).get("connected") if isinstance(state.get("broker"), dict) else (health.get("broker") or {}).get("connected"),
        "market_open": (state.get("market") or {}).get("is_open") if isinstance(state.get("market"), dict) else (health.get("market") or {}).get("is_open"),
        "qc_status": qc.get("status") or qc.get("qc_status"),
        "chain_status": chain.get("status"),
        "chain_source": chain.get("data_source") or chain.get("source_priority"),
        "chain_contracts": chain.get("total_contracts") or len(chain.get("contracts", []) or []),
        "live_trading_hits": live_hits,
        "order_allowed_hits": order_hits,
        "screenshot": screenshot,
    }

    write_json(SNAP_DIR / "endpoint_matrix.json", endpoint_matrix)
    write_json(SNAP_DIR / "latest_verdict.json", verdict)

    summary_lines = [
        "# System3 Dashboard Auto Snapshot",
        "",
        f"Generated UTC: `{verdict['generated_utc']}`",
        f"Dashboard URL: `{DASHBOARD_URL}`",
        f"Backend URL: `{BACKEND_URL}`",
        f"Frontend header: `{verdict.get('frontend_header')}`",
        f"Final verdict: **{verdict['final_verdict']}**",
        "",
        "## Runtime",
        f"- Mode: `{verdict.get('mode')}`",
        f"- Broker connected: `{verdict.get('broker_connected')}`",
        f"- Market open: `{verdict.get('market_open')}`",
        f"- QC status: `{verdict.get('qc_status')}`",
        f"- NIFTY chain: status=`{verdict.get('chain_status')}`, source=`{verdict.get('chain_source')}`, contracts=`{verdict.get('chain_contracts')}`",
        "",
        "## Critical",
        *(f"- `{x}`" for x in critical),
        *( ["- none"] if not critical else [] ),
        "",
        "## Warnings",
        *(f"- `{x}`" for x in warnings),
        *( ["- none"] if not warnings else [] ),
        "",
        "## Files",
        "- `latest_dashboard.png`",
        "- `latest_mobile.png`",
        "- `latest_verdict.json`",
        "- `endpoint_matrix.json`",
    ]
    (SNAP_DIR / "latest_summary.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    git_info = maybe_git_push(verdict)
    write_json(SNAP_DIR / "latest_git_push.json", git_info)

    print(json.dumps({"verdict": verdict, "git": git_info}, indent=2, ensure_ascii=False))
    return 2 if critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
