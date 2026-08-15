#!/usr/bin/env python3
"""Capture deployed Genesis System3 semantic + visual proof for every tab.

A screenshot existing is not proof that a dashboard tab works.  The verifier
therefore proves three independent things from the deployed Cloud Run URL:
1. navigation: the requested tab is active;
2. semantics: active <main> content is meaningful and settled (not loading/error);
3. visuals: desktop and mobile screenshots are non-empty.

Read-only evidence only: no mutation/order endpoint is called.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
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
PAGE_LOAD_TIMEOUT_S = 45
RETRY_PAGE_LOAD_TIMEOUT_S = 60
ACTIVE_TAB_WAIT_S = 30
MIN_MAIN_TEXT_CHARS = 60
SEMANTIC_CONTRACT_VERSION = 2

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

# These strings are never an acceptable final state of an active dashboard
# panel.  PENDING/BLOCKED are deliberately not forbidden: they can be truthful
# analyzer states.  The defect being prevented is a false PASS on a panel that
# has not settled or that crashed.
FORBIDDEN_MAIN_MARKERS = (
    "LOADING ",
    "LOADING…",
    "REQUEST FAILED",
    "FAILED TO FETCH",
    "NETWORK ERROR",
    "SOMETHING WENT WRONG",
    "ERROR BOUNDARY",
    "DASHBOARD API KEY",
    "ENTER API KEY",
)


def evaluate_tab_semantics(tab_id: str, snapshot: dict) -> list[str]:
    """Pure contract used by browser proof and unit tests."""
    failures: list[str] = []
    main_text = str(snapshot.get("mainText") or "").strip().upper()
    if len(main_text) < MIN_MAIN_TEXT_CHARS:
        failures.append(f"main_content_too_thin:{len(main_text)}")
    for marker in FORBIDDEN_MAIN_MARKERS:
        if marker in main_text:
            failures.append(f"unsettled_or_error_marker:{marker.strip()}")

    # Paper is the regression that exposed the old false-PASS design.  It gets
    # a stronger contract: the DOM itself must say it settled and must prove the
    # durable Firestore authority + paper order safety.
    if tab_id == "paper":
        if str(snapshot.get("paperProofState") or "").lower() != "settled":
            failures.append("paper_not_settled")
        if str(snapshot.get("paperLedgerSource") or "").upper() != "FIRESTORE_PAPER_LEDGER":
            failures.append("paper_firestore_ledger_not_proven")
        for marker in ("PAPER TRADING CONSOLE", "PAPER TRUTH PROVENANCE", "FIRESTORE_PAPER_LEDGER", "INTENTIONALLY NOT CALLED"):
            if marker not in main_text:
                failures.append(f"paper_required_marker_missing:{marker}")

    return failures


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


def _chromedriver_path() -> str:
    candidates: list[Path] = []
    which = shutil.which("chromedriver")
    if which:
        candidates.append(Path(which))
    env_path = os.getenv("CHROMEWEBDRIVER", "").strip()
    if env_path:
        candidate = Path(env_path)
        candidates.append(candidate / "chromedriver" if candidate.is_dir() else candidate)
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    raise RuntimeError("chromedriver_not_found")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class ChromeDriverSession:
    def __init__(self, *, page_load_timeout_s: int) -> None:
        self.page_load_timeout_s = int(page_load_timeout_s)
        self.port = _free_port()
        self.base = f"http://127.0.0.1:{self.port}"
        self.proc: subprocess.Popen[str] | None = None
        self.session_id = ""

    def __enter__(self) -> "ChromeDriverSession":
        self.proc = subprocess.Popen(
            [_chromedriver_path(), f"--port={self.port}", "--allowed-ips=127.0.0.1"],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                response = requests.get(f"{self.base}/status", timeout=2)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("chromedriver_start_timeout")

        value = self._request(
            "POST",
            "/session",
            {
                "capabilities": {
                    "alwaysMatch": {
                        "browserName": "chrome",
                        "pageLoadStrategy": "eager",
                        "goog:chromeOptions": {
                            "args": [
                                "--headless=new",
                                "--disable-gpu",
                                "--no-sandbox",
                                "--hide-scrollbars",
                                "--disable-dev-shm-usage",
                                "--window-size=1600,1000",
                            ]
                        },
                    }
                }
            },
            timeout=20,
            sessionless=True,
        )
        if not isinstance(value, dict) or not value.get("sessionId"):
            raise RuntimeError("webdriver_session_id_missing")
        self.session_id = str(value["sessionId"])
        self._request(
            "POST",
            f"/session/{self.session_id}/timeouts",
            {"implicit": 0, "pageLoad": self.page_load_timeout_s * 1000, "script": 10000},
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.session_id:
            try:
                self._request("DELETE", f"/session/{self.session_id}", timeout=10)
            except Exception:
                pass
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.session_id = ""

    def _request(self, method: str, path: str, payload: dict | None = None, *, timeout: int | None = None, sessionless: bool = False):
        response = requests.request(
            method,
            f"{self.base}{path}",
            json=payload,
            timeout=timeout or self.page_load_timeout_s + 10,
        )
        try:
            body = response.json()
        except Exception as exc:
            raise RuntimeError(f"webdriver_non_json:{response.status_code}") from exc
        value = body.get("value") if isinstance(body, dict) else None
        if response.status_code >= 400:
            raise RuntimeError(f"webdriver_http_{response.status_code}:{str(value)[:120]}")
        if isinstance(value, dict) and value.get("error"):
            raise RuntimeError(f"webdriver_error:{value.get('error')}:{str(value.get('message') or '')[:120]}")
        return value

    def set_viewport(self, width: int, height: int) -> None:
        self._request(
            "POST",
            f"/session/{self.session_id}/window/rect",
            {"width": int(width), "height": int(height), "x": 0, "y": 0},
        )

    def navigate(self, url: str) -> None:
        self._request(
            "POST",
            f"/session/{self.session_id}/url",
            {"url": url},
            timeout=self.page_load_timeout_s + 10,
        )

    def proof_snapshot(self, tab_id: str) -> dict:
        script = r"""
const id = arguments[0];
const button = document.querySelector('[data-dashboard-tab="' + CSS.escape(id) + '"]');
const bodyText = (document.body && document.body.innerText || '').toUpperCase();
const main = document.querySelector('#dashboard-main');
const mainText = (main && main.innerText || '').trim();
const paper = document.querySelector('[data-paper-proof-state]');
return {
  active: !!button && button.getAttribute('aria-current') === 'page',
  system3: bodyText.includes('SYSTEM3'),
  dashboardKeyPrompt: bodyText.includes('DASHBOARD API KEY') || bodyText.includes('ENTER API KEY'),
  readyState: document.readyState,
  mainText: mainText,
  mainTextLength: mainText.length,
  paperProofState: paper ? paper.getAttribute('data-paper-proof-state') : null,
  paperLedgerSource: paper ? paper.getAttribute('data-paper-ledger-source') : null
};
"""
        value = self._request(
            "POST",
            f"/session/{self.session_id}/execute/sync",
            {"script": script, "args": [tab_id]},
            timeout=15,
        )
        return value if isinstance(value, dict) else {}

    def wait_for_settled(self, tab_id: str) -> dict:
        deadline = time.monotonic() + ACTIVE_TAB_WAIT_S
        last: dict = {}
        while time.monotonic() < deadline:
            last = self.proof_snapshot(tab_id)
            if last.get("active") and last.get("system3") and not evaluate_tab_semantics(tab_id, last):
                return last
            time.sleep(0.5)
        return last

    def screenshot(self, path: Path) -> str:
        encoded = self._request("GET", f"/session/{self.session_id}/screenshot", timeout=20)
        if not isinstance(encoded, str) or not encoded:
            raise RuntimeError("webdriver_screenshot_missing")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise RuntimeError("webdriver_screenshot_invalid_base64") from exc
        path.write_bytes(raw)
        if path.stat().st_size < 1000:
            raise RuntimeError(f"webdriver_screenshot_too_small:{path.name}")
        return hashlib.sha256(raw).hexdigest()


def _capture_tab(
    browser: ChromeDriverSession,
    index: int,
    tab_id: str,
    label: str,
    dashboard_url: str,
    *,
    retry: bool = False,
) -> tuple[int, dict, list[str]]:
    url = f"{dashboard_url}?{urlencode({'tab': tab_id})}"
    row = {
        "id": tab_id,
        "label": label,
        "url": url,
        "proof_state": "FAIL",
        "review_state": "PENDING_USER_REVIEW",
        "capture_retry": retry,
        "browser_transport": "webdriver_single_session",
        "mobile_reload_required": False,
        "semantic_contract_version": SEMANTIC_CONTRACT_VERSION,
    }
    failures: list[str] = []
    try:
        browser.set_viewport(1600, 1000)
        browser.navigate(url)
        snapshot = browser.wait_for_settled(tab_id)
        active = bool(snapshot.get("active"))
        login_prompt = bool(snapshot.get("dashboardKeyPrompt"))
        system3_marker = bool(snapshot.get("system3"))
        desktop_semantic_failures = evaluate_tab_semantics(tab_id, snapshot)

        desktop = TABS_OUT / f"{index:02d}-{tab_id}-desktop.png"
        mobile = TABS_OUT / f"{index:02d}-{tab_id}-mobile.png"
        desktop_hash = browser.screenshot(desktop)

        browser.set_viewport(430, 932)
        mobile_snapshot = browser.wait_for_settled(tab_id)
        mobile_semantic_failures = evaluate_tab_semantics(tab_id, mobile_snapshot)
        mobile_hash = browser.screenshot(mobile)

        local_failures: list[str] = []
        if not active:
            local_failures.append("active_tab_not_proven")
        if not mobile_snapshot.get("active"):
            local_failures.append("active_tab_lost_after_mobile_resize")
        if login_prompt or mobile_snapshot.get("dashboardKeyPrompt"):
            local_failures.append("dashboard_api_key_prompt_rendered")
        if not system3_marker or not mobile_snapshot.get("system3"):
            local_failures.append("system3_marker_missing")
        local_failures.extend(f"desktop_semantic:{item}" for item in desktop_semantic_failures)
        local_failures.extend(f"mobile_semantic:{item}" for item in mobile_semantic_failures)

        row.update({
            "proof_state": "PASS" if not local_failures else "FAIL",
            "active_tab_proven": active,
            "mobile_active_tab_proven": bool(mobile_snapshot.get("active")),
            "dashboard_api_key_prompt_rendered": bool(login_prompt or mobile_snapshot.get("dashboardKeyPrompt")),
            "system3_marker": bool(system3_marker and mobile_snapshot.get("system3")),
            "desktop_main_text_length": int(snapshot.get("mainTextLength") or 0),
            "mobile_main_text_length": int(mobile_snapshot.get("mainTextLength") or 0),
            "desktop_semantic_settled": not desktop_semantic_failures,
            "mobile_semantic_settled": not mobile_semantic_failures,
            "paper_proof_state": snapshot.get("paperProofState") if tab_id == "paper" else None,
            "paper_ledger_source": snapshot.get("paperLedgerSource") if tab_id == "paper" else None,
            "desktop_file": str(desktop.relative_to(OUT)),
            "desktop_sha256": desktop_hash,
            "mobile_file": str(mobile.relative_to(OUT)),
            "mobile_sha256": mobile_hash,
            "failures": local_failures,
        })
        failures.extend(f"{tab_id}:{item}" for item in local_failures)
    except Exception as exc:
        row["failures"] = [f"{type(exc).__name__}:{str(exc)[:180]}"]
        failures.append(f"{tab_id}:capture_failed")
    finally:
        try:
            browser.set_viewport(1600, 1000)
        except Exception:
            pass
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
    (OUT / "tab_visual_matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")


def _capture_pass(
    dashboard_url: str,
    indexes: list[int],
    rows: dict[int, dict],
    failures: list[str],
    matrix: dict,
    *,
    retry: bool,
    page_load_timeout_s: int,
) -> list[str]:
    next_failures = list(failures)
    with ChromeDriverSession(page_load_timeout_s=page_load_timeout_s) as browser:
        for index in indexes:
            tab_id, label = TABS[index - 1]
            index, row, row_failures = _capture_tab(browser, index, tab_id, label, dashboard_url, retry=retry)
            rows[index] = row
            next_failures = [item for item in next_failures if not item.startswith(f"{tab_id}:")]
            next_failures.extend(row_failures)
            _write_matrix(matrix, rows, next_failures, final=False)
            print(
                ("UI_TAB_VISUAL_RETRY_PROGRESS " if retry else "UI_TAB_VISUAL_PROGRESS ")
                + json.dumps({
                    "tab": tab_id,
                    "completed": len(rows),
                    "total": len(TABS),
                    "proof_state": row.get("proof_state"),
                    "pass_count": sum(1 for item in rows.values() if item.get("proof_state") == "PASS"),
                }, sort_keys=True),
                flush=True,
            )
    return next_failures


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    TABS_OUT.mkdir(parents=True, exist_ok=True)
    matrix = {
        "state": "FAIL",
        "source": "real_deployed_cloud_run_ui",
        "expected_sha": EXPECTED_SHA,
        "tab_count": len(TABS),
        "browser_transport": "webdriver_single_session",
        "page_load_strategy": "eager",
        "page_load_timeout_seconds": PAGE_LOAD_TIMEOUT_S,
        "retry_page_load_timeout_seconds": RETRY_PAGE_LOAD_TIMEOUT_S,
        "retry_mode": "failed_tabs_fresh_browser_once",
        "semantic_contract_version": SEMANTIC_CONTRACT_VERSION,
        "semantic_rule": "active main must be non-thin and free of persistent loading/error markers",
        "viewports": {"desktop": "1600x1000", "mobile": "430x932"},
        "mobile_reload_required": False,
        "expected_page_navigations_initial": len(TABS),
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

        initial_indexes = list(range(1, len(TABS) + 1))
        failures = _capture_pass(
            dashboard_url,
            initial_indexes,
            rows,
            failures,
            matrix,
            retry=False,
            page_load_timeout_s=PAGE_LOAD_TIMEOUT_S,
        )

        retry_indexes = [index for index, row in sorted(rows.items()) if row.get("proof_state") != "PASS"]
        matrix["initial_fail_count"] = len(retry_indexes)
        matrix["retry_count"] = len(retry_indexes)
        if retry_indexes:
            print(
                "UI_TAB_VISUAL_RETRY "
                + json.dumps({
                    "indexes": retry_indexes,
                    "mode": "fresh_webdriver_session_serial",
                    "page_load_timeout_s": RETRY_PAGE_LOAD_TIMEOUT_S,
                }, sort_keys=True),
                flush=True,
            )
            failures = _capture_pass(
                dashboard_url,
                retry_indexes,
                rows,
                failures,
                matrix,
                retry=True,
                page_load_timeout_s=RETRY_PAGE_LOAD_TIMEOUT_S,
            )

        _write_matrix(matrix, rows, failures, final=True)
        print("UI_TAB_VISUAL_PROOF " + json.dumps({
            "state": matrix["state"],
            "tab_count": len(TABS),
            "pass_count": matrix["pass_count"],
            "fail_count": matrix["fail_count"],
            "retry_count": matrix.get("retry_count", 0),
            "semantic_contract_version": SEMANTIC_CONTRACT_VERSION,
            "browser_transport": "webdriver_single_session",
            "mutations_called": False,
        }, sort_keys=True))
        return 0 if matrix["state"] == "PASS" else 1
    except Exception as exc:
        matrix["fatal_error"] = f"{type(exc).__name__}:{str(exc)[:180]}"
        matrix["state"] = "FAIL"
        (OUT / "tab_visual_matrix.json").write_text(json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8")
        print(
            "UI_TAB_VISUAL_PROOF " + json.dumps({"state": "FAIL", "error": matrix["fatal_error"]}),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
