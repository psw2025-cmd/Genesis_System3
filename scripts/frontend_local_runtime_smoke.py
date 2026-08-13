#!/usr/bin/env python3
"""Fail CI if the built dashboard compiles but cannot render in a real browser.

This is a local, read-only frontend smoke. It serves Vite's production build,
opens every canonical dashboard tab with ChromeDriver, and proves the React root,
SYSTEM3 marker, active-tab state, and public-readonly credential surface render.
No backend, broker, paper-order, or mutation endpoint is required or called on
purpose; API requests made by the UI resolve against the local preview server.
"""
from __future__ import annotations

import base64
import json
import os
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
PORT = 4173
BASE_URL = f"http://{HOST}:{PORT}/ui/"

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


def _wait_preview(proc: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"vite_preview_exited:{proc.returncode}")
        try:
            with urllib.request.urlopen(BASE_URL, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(0.25)
    raise RuntimeError("vite_preview_start_timeout")


class Browser:
    def __init__(self) -> None:
        self.port = _free_port()
        self.base = f"http://{HOST}:{self.port}"
        self.proc: subprocess.Popen[str] | None = None
        self.session_id = ""

    def _request(self, method: str, path: str, payload: dict | None = None, timeout: int = 20):
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
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f"{self.base}/status", timeout=2) as response:
                    if response.status == 200:
                        break
            except (urllib.error.URLError, TimeoutError):
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("chromedriver_start_timeout")

        value = self._request("POST", "/session", {
            "capabilities": {"alwaysMatch": {
                "browserName": "chrome",
                "pageLoadStrategy": "eager",
                "goog:chromeOptions": {"args": [
                    "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--disable-dev-shm-usage", "--window-size=1600,1000",
                ]},
            }}
        })
        if not isinstance(value, dict) or not value.get("sessionId"):
            raise RuntimeError("webdriver_session_missing")
        self.session_id = str(value["sessionId"])
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
        self._request("POST", f"/session/{self.session_id}/url", {"url": url}, timeout=30)

    def snapshot(self, tab_id: str) -> dict:
        script = r"""
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
"""
        value = self._request(
            "POST", f"/session/{self.session_id}/execute/sync",
            {"script": script, "args": [tab_id]}, timeout=15,
        )
        return value if isinstance(value, dict) else {}

    def screenshot(self, path: Path) -> None:
        encoded = self._request("GET", f"/session/{self.session_id}/screenshot", timeout=20)
        if isinstance(encoded, str) and encoded:
            path.write_bytes(base64.b64decode(encoded))


def main() -> int:
    if not (FRONTEND / "dist" / "index.html").is_file():
        print("FAIL: Vite dist missing; run npm run build first", file=sys.stderr)
        return 2

    preview = subprocess.Popen(
        ["npm", "run", "preview", "--", "--host", HOST, "--port", str(PORT), "--strictPort"],
        cwd=FRONTEND, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    failures: list[str] = []
    try:
        _wait_preview(preview)
        with Browser() as browser:
            for tab_id in TABS:
                browser.navigate(f"{BASE_URL}?tab={tab_id}")
                deadline = time.monotonic() + 8
                snap: dict = {}
                while time.monotonic() < deadline:
                    snap = browser.snapshot(tab_id)
                    if snap.get("rootChildren", 0) > 0 and snap.get("system3") and snap.get("active"):
                        break
                    time.sleep(0.25)

                tab_failures = []
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
        if preview.stdout:
            output = preview.stdout.read()
            if output:
                print("VITE_PREVIEW_LOG\n" + output[-4000:])

    if failures:
        print("FRONTEND_RUNTIME_SMOKE=FAIL", json.dumps(failures), file=sys.stderr)
        return 1
    print(f"FRONTEND_RUNTIME_SMOKE=PASS tabs={len(TABS)} live_trading_actions=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
