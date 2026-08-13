#!/usr/bin/env python3
"""Fail CI if the built System3 dashboard compiles but cannot render in Chrome.

Read-only analyzer/PAPER smoke: serve the Vite production build, mount the app once,
then activate every canonical tab through the real sidebar. This avoids 22 full app
remounts and the network/poller amplification they cause. No broker mutation or order
endpoint is intentionally called.
"""
from __future__ import annotations

import base64
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "dashboard" / "frontend"
HOST = "127.0.0.1"

TABS = [
    "decision-intel", "truth", "genesis", "e2e-proof", "overview", "sim-live",
    "options-intel", "chain", "signals", "trade", "paper", "positions",
    "risk-scenarios", "multibagger", "prediction-audit", "performance", "ml",
    "data-integrity", "broker", "alerts", "system", "gates",
]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def _wait_http(url: str, proc: subprocess.Popen[str], timeout_s: float = 20.0) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"process_exited:{proc.returncode}:{url}")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.2)
    raise RuntimeError(f"http_start_timeout:{url}")


class Browser:
    def __init__(self) -> None:
        self.port = _free_port()
        self.base = f"http://{HOST}:{self.port}"
        self.proc: subprocess.Popen[str] | None = None
        self.session_id = ""

    def _request(self, method: str, path: str, payload: dict | None = None, timeout: int = 10):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base}{path}", data=data, method=method,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"webdriver_http_{exc.code}:{detail}") from exc
        value = body.get("value") if isinstance(body, dict) else None
        if isinstance(value, dict) and value.get("error"):
            raise RuntimeError(f"webdriver_error:{value.get('error')}:{value.get('message')}")
        return value

    def __enter__(self) -> "Browser":
        driver = shutil.which("chromedriver")
        if not driver:
            raise RuntimeError("chromedriver_not_found")
        self.proc = subprocess.Popen(
            [driver, f"--port={self.port}", f"--allowed-ips={HOST}"],
            text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        )
        _wait_http(f"{self.base}/status", self.proc, 15)
        value = self._request("POST", "/session", {
            "capabilities": {"alwaysMatch": {
                "browserName": "chrome",
                "pageLoadStrategy": "eager",
                "goog:chromeOptions": {"args": [
                    "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--disable-dev-shm-usage", "--disable-background-networking",
                    "--window-size=1600,1000",
                ]},
            }}
        }, timeout=15)
        if not isinstance(value, dict) or not value.get("sessionId"):
            raise RuntimeError("webdriver_session_missing")
        self.session_id = str(value["sessionId"])
        self._request("POST", f"/session/{self.session_id}/timeouts", {
            "implicit": 0, "pageLoad": 10000, "script": 5000,
        })
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.session_id:
            try:
                self._request("DELETE", f"/session/{self.session_id}", timeout=5)
            except Exception:
                pass
        if self.proc is not None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()

    def navigate(self, url: str) -> None:
        self._request("POST", f"/session/{self.session_id}/url", {"url": url}, timeout=12)

    def _execute(self, script: str, args: list | None = None):
        return self._request(
            "POST", f"/session/{self.session_id}/execute/sync",
            {"script": script, "args": args or []}, timeout=8,
        )

    def activate(self, tab_id: str) -> bool:
        value = self._execute(r"""
const id = arguments[0];
const button = document.querySelector('[data-dashboard-tab="' + CSS.escape(id) + '"]');
if (!button) return false;
if (button.getAttribute('aria-current') !== 'page') button.click();
return true;
""", [tab_id])
        return bool(value)

    def snapshot(self, tab_id: str) -> dict:
        value = self._execute(r"""
const id = arguments[0];
const root = document.getElementById('root');
const button = document.querySelector('[data-dashboard-tab="' + CSS.escape(id) + '"]');
const text = (document.body && document.body.innerText || '').toUpperCase();
return {
  readyState: document.readyState,
  rootChildren: root ? root.childElementCount : -1,
  active: !!button && button.getAttribute('aria-current') === 'page',
  system3: text.includes('SYSTEM3'),
  keyPrompt: text.includes('DASHBOARD API KEY') || text.includes('ENTER API KEY'),
  bodyText: text.slice(0, 300),
};
""", [tab_id])
        return value if isinstance(value, dict) else {}

    def screenshot(self, path: Path) -> None:
        encoded = self._request("GET", f"/session/{self.session_id}/screenshot", timeout=10)
        if isinstance(encoded, str) and encoded:
            path.write_bytes(base64.b64decode(encoded))


def _wait_tab(browser: Browser, tab_id: str, timeout_s: float = 3.0) -> dict:
    deadline = time.monotonic() + timeout_s
    snap: dict = {}
    while time.monotonic() < deadline:
        snap = browser.snapshot(tab_id)
        if snap.get("rootChildren", 0) > 0 and snap.get("system3") and snap.get("active"):
            return snap
        time.sleep(0.15)
    return snap


def main() -> int:
    if not (FRONTEND / "dist" / "index.html").is_file():
        print("FAIL: Vite dist missing; run npm run build first", file=sys.stderr)
        return 2

    preview_port = _free_port()
    base_url = f"http://{HOST}:{preview_port}/ui/"
    preview = subprocess.Popen(
        ["npm", "run", "preview", "--", "--host", HOST, "--port", str(preview_port), "--strictPort"],
        cwd=FRONTEND, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    failures: list[str] = []
    started = time.monotonic()
    try:
        _wait_http(base_url, preview, 20)
        with Browser() as browser:
            # One mount only. Subsequent tabs use the actual sidebar/store transition.
            browser.navigate(base_url + "?tab=decision-intel")
            first = _wait_tab(browser, "decision-intel", 5)
            if first.get("rootChildren", 0) <= 0 or not first.get("system3"):
                failures.append("initial_mount:react_root_or_system3_missing")

            for tab_id in TABS:
                if not browser.activate(tab_id):
                    failures.append(f"{tab_id}:sidebar_button_missing")
                    print("TAB_FAIL", tab_id, "sidebar_button_missing")
                    continue
                snap = _wait_tab(browser, tab_id, 3)
                tab_failures: list[str] = []
                if snap.get("rootChildren", 0) <= 0:
                    tab_failures.append("react_root_empty")
                if not snap.get("system3"):
                    tab_failures.append("system3_marker_missing")
                if not snap.get("active"):
                    tab_failures.append("active_tab_not_proven")
                if snap.get("keyPrompt"):
                    tab_failures.append("credential_prompt_rendered")
                if tab_failures:
                    failures.extend(f"{tab_id}:{item}" for item in tab_failures)
                    print("TAB_FAIL", tab_id, json.dumps(snap, sort_keys=True), tab_failures)
                else:
                    print("TAB_PASS", tab_id)

            if failures:
                browser.screenshot(ROOT / "frontend-runtime-smoke-failure.png")
    finally:
        preview.terminate()
        try:
            preview.wait(timeout=5)
        except subprocess.TimeoutExpired:
            preview.kill()

    elapsed = round(time.monotonic() - started, 2)
    if failures:
        print("FRONTEND_RUNTIME_SMOKE=FAIL", json.dumps(failures), f"elapsed_s={elapsed}", file=sys.stderr)
        return 1
    print(f"FRONTEND_RUNTIME_SMOKE=PASS tabs={len(TABS)} elapsed_s={elapsed} live_trading_actions=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
