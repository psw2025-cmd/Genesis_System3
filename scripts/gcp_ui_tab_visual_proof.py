#!/usr/bin/env python3
"""Capture deployed Genesis System3 visual proof for every dashboard tab.

Read-only evidence only: no mutation/order endpoint is called. Each tab is opened
through the product's `?tab=<id>` deep-link, rendered in headless Chrome, and
captured at desktop and mobile viewport sizes. The JSON matrix distinguishes
render/navigation proof from product-review completion.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlencode

import requests

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path("reports/latest/public_dashboard_proof")
TABS_OUT = OUT / "tabs"
TIMEOUT_S = 30
BROWSER_TIMEOUT_S = 35
CAPTURE_WORKERS = max(1, min(3, int(os.getenv("SYSTEM3_UI_PROOF_WORKERS", "3"))))

TABS = [
    ("decision-intel", "Decision Intel"),
    ("truth", "Truth Control"),
    ("genesis", "Genesis Brain"),
    ("e2e-proof", "E2E Proof"),
    ("overview", "Overview"),
    ("sim-live", "Sim Live"),
    ("options-intel", "Options Intel"),
    ("chain", "Option Chain"),
    ("signals", "Signals"),
    ("trade", "Trade"),
    ("paper", "Paper Trades"),
    ("positions", "Positions"),
    ("risk-scenarios", "Risk & Scenarios"),
    ("multibagger", "Multibagger V4"),
    ("prediction-audit", "Prediction Audit"),
    ("performance", "Performance"),
    ("ml", "ML Model"),
    ("data-integrity", "Data Integrity"),
    ("broker", "Broker"),
    ("alerts", "Alerts"),
    ("system", "System"),
    ("gates", "Live Gate"),
]


def _run(*args: str, timeout: int = 90) -> str:
    proc = subprocess.run(list(args), text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode:
        raise RuntimeError(f"command_failed:{args[0]}:{proc.returncode}")
    return proc.stdout.strip()


def _service_url() -> str:
    raw = _run(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    data = json.loads(raw or "{}")
    status = data.get("status") or {}
    url = str(status.get("url") or data.get("uri") or "").rstrip("/")
    if not url.startswith("https://"):
        raise RuntimeError("cloud_run_https_url_missing")
    return url


def _browser_path() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("headless_chrome_not_found")


def _args(url: str, width: int, height: int, budget_ms: int = 7000) -> list[str]:
    return [
        _browser_path(), "--headless", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", f"--window-size={width},{height}",
        f"--virtual-time-budget={budget_ms}", url,
    ]


def _render_dom(url: str) -> str:
    args = _args(url, 1600, 1000)
    args.insert(-1, "--dump-dom")
    proc = subprocess.run(args, text=True, capture_output=True, timeout=BROWSER_TIMEOUT_S, check=False)
    if proc.returncode:
        raise RuntimeError(f"tab_dom_render_failed:{proc.returncode}")
    return proc.stdout or ""


def _capture(url: str, path: Path, width: int, height: int) -> str:
    args = _args(url, width, height)
    args.insert(-1, f"--screenshot={path}")
    proc = subprocess.run(args, text=True, capture_output=True, timeout=BROWSER_TIMEOUT_S, check=False)
    if proc.returncode or not path.is_file() or path.stat().st_size < 1000:
        raise RuntimeError(f"tab_screenshot_failed:{path.name}:{proc.returncode}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _active_tab_proven(dom: str, tab_id: str) -> bool:
    for match in re.finditer(r"<button\b[^>]*>", dom, flags=re.IGNORECASE):
        tag = match.group(0)
        if f'data-dashboard-tab="{tab_id}"' in tag and 'aria-current="page"' in tag:
            return True
    return False


def _capture_tab(index: int, tab_id: str, label: str, dashboard_url: str) -> tuple[int, dict, list[str]]:
    url = f"{dashboard_url}?{urlencode({'tab': tab_id})}"
    row = {
        "id": tab_id,
        "label": label,
        "url": url,
        "proof_state": "FAIL",
        "review_state": "PENDING_USER_REVIEW",
    }
    failures: list[str] = []
    try:
        dom = _render_dom(url)
        active = _active_tab_proven(dom, tab_id)
        login_prompt = "DASHBOARD API KEY" in dom.upper()
        system3_marker = "SYSTEM3" in dom.upper()
        desktop = TABS_OUT / f"{index:02d}-{tab_id}-desktop.png"
        mobile = TABS_OUT / f"{index:02d}-{tab_id}-mobile.png"
        desktop_hash = _capture(url, desktop, 1600, 1000)
        mobile_hash = _capture(url, mobile, 430, 932)
        local_failures: list[str] = []
        if not active:
            local_failures.append("active_tab_not_proven")
        if login_prompt:
            local_failures.append("dashboard_api_key_prompt_rendered")
        if not system3_marker:
            local_failures.append("system3_marker_missing")
        row.update({
            "proof_state": "PASS" if not local_failures else "FAIL",
            "active_tab_proven": active,
            "dashboard_api_key_prompt_rendered": login_prompt,
            "system3_marker": system3_marker,
            "desktop_file": str(desktop.relative_to(OUT)),
            "desktop_sha256": desktop_hash,
            "mobile_file": str(mobile.relative_to(OUT)),
            "mobile_sha256": mobile_hash,
            "failures": local_failures,
        })
        failures.extend(f"{tab_id}:{item}" for item in local_failures)
    except Exception as exc:
        row["failures"] = [f"{type(exc).__name__}:{str(exc)[:160]}"]
        failures.append(f"{tab_id}:capture_failed")
    return index, row, failures


def _write_matrix(matrix: dict, rows: dict[int, dict], failures: list[str], *, final: bool) -> None:
    ordered = [rows[index] for index in sorted(rows)]
    pass_count = sum(1 for row in ordered if row.get("proof_state") == "PASS")
    matrix["tabs"] = ordered
    matrix["completed_count"] = len(ordered)
    matrix["pass_count"] = pass_count
    matrix["fail_count"] = len(ordered) - pass_count
    matrix["failures"] = list(failures)
    matrix["state"] = (
        "PASS"
        if final and not failures and len(ordered) == len(TABS) and pass_count == len(TABS)
        else "FAIL"
        if final
        else "IN_PROGRESS"
    )
    (OUT / "tab_visual_matrix.json").write_text(
        json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8"
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    TABS_OUT.mkdir(parents=True, exist_ok=True)
    matrix = {
        "state": "FAIL",
        "source": "real_deployed_cloud_run_ui",
        "expected_sha": EXPECTED_SHA,
        "tab_count": len(TABS),
        "capture_workers": CAPTURE_WORKERS,
        "browser_timeout_seconds": BROWSER_TIMEOUT_S,
        "viewports": {"desktop": "1600x1000", "mobile": "430x932"},
        "trading_mutations_called": False,
        "tabs": [],
    }
    try:
        if len(EXPECTED_SHA) != 40:
            raise RuntimeError("expected_git_sha_missing")
        service_url = _service_url()
        dashboard_url = f"{service_url}/ui"
        if requests.get(dashboard_url, timeout=TIMEOUT_S).status_code != 200:
            raise RuntimeError("dashboard_ui_not_http_200")

        rows: dict[int, dict] = {}
        failures: list[str] = []
        _write_matrix(matrix, rows, failures, final=False)

        with ThreadPoolExecutor(max_workers=CAPTURE_WORKERS, thread_name_prefix="ui-proof") as executor:
            futures = {
                executor.submit(_capture_tab, index, tab_id, label, dashboard_url): index
                for index, (tab_id, label) in enumerate(TABS, start=1)
            }
            for future in as_completed(futures):
                index, row, row_failures = future.result()
                rows[index] = row
                failures.extend(row_failures)
                _write_matrix(matrix, rows, failures, final=False)
                print(
                    "UI_TAB_VISUAL_PROGRESS "
                    + json.dumps({
                        "completed": len(rows),
                        "total": len(TABS),
                        "pass_count": sum(1 for item in rows.values() if item.get("proof_state") == "PASS"),
                    }, sort_keys=True),
                    flush=True,
                )

        _write_matrix(matrix, rows, failures, final=True)
        print("UI_TAB_VISUAL_PROOF " + json.dumps({
            "state": matrix["state"], "tab_count": len(TABS),
            "pass_count": matrix["pass_count"], "fail_count": matrix["fail_count"],
            "mutations_called": False,
        }, sort_keys=True))
        return 0 if matrix["state"] == "PASS" else 1
    except Exception as exc:
        matrix["fatal_error"] = f"{type(exc).__name__}:{str(exc)[:180]}"
        matrix["state"] = "FAIL"
        (OUT / "tab_visual_matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
        print("UI_TAB_VISUAL_PROOF " + json.dumps({"state": "FAIL", "error": matrix["fatal_error"]}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
