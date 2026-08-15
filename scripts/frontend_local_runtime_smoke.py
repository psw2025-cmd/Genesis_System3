#!/usr/bin/env python3
"""Fail CI if the built System3 dashboard cannot satisfy deploy/runtime proof.

Read-only analyzer/PAPER smoke: verify the same compiled frontend markers required
by the Cloud Run Docker build, serve the Vite production build, mount the app once,
then activate every canonical tab through the real sidebar. Each successfully rendered
tab is captured as a PNG visual-proof artifact. No broker mutation or order endpoint
is intentionally called.
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
PROOF_DIR = ROOT / "frontend-ui-proof"
HOST = "127.0.0.1"
BROWSER_START_ATTEMPTS = 3

# Keep this contract aligned with dashboard/backend/Dockerfile. A PR must fail
# before merge if Vite succeeds but the immutable deploy-proof bundle would fail.
REQUIRED_DEPLOY_MARKERS = (
    "Sim Live",
    "CLOUD BUILD",
    "SESSION SNAPSHOT",
    "TOKEN ROTATION PROOF",
)

TABS = [
    "decision-intel", "truth", "genesis", "e2e-proof", "overview", "sim-live",
    "options-intel", "chain", "signals", "trade", "paper", "positions",
    "risk-scenarios", "multibagger", "prediction-audit", "performance", "ml",
    "data-integrity", "broker", "alerts", "system", "gates",
]


def _verify_deploy_markers() -> None:
    assets = FRONTEND / "dist" / "assets"
    js_files = sorted(assets.glob("*.js")) if assets.is_dir() else []
    if not js_files:
        raise RuntimeError("frontend_deploy_marker_check:no_compiled_js")
    bundle = b"\n".join(path.read_bytes() for path in js_files)
    missing = [marker for marker in REQUIRED_DEPLOY_MARKERS if marker.encode("utf-8") not in bundle]
    if missing:
        raise RuntimeError(f"frontend_deploy_marker_check:missing={missing}")
    print("FRONTEND_DEPLOY_MARKERS=PASS", json.dumps(REQUIRED_DEPLOY_MARKERS))


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
    """One Chrome session with bounded cold-start retries.

    Hosted runners occasionally start chromedriver but stall while Chrome creates
    the first session. A failed attempt is fully killed and retried on a fresh
    port. The smoke never converts a failed browser startup into PASS.
    """

    def __init__(self) -> None:
        self.port = 0
        self.base = ""
        self.proc: subprocess.Popen[str] | None = None
        self.session_id = ""
        self.start_attempt = 0

    def _reset_endpoint(self) -> None:
        self.port = _free_port()
        self.base = f"http://{HOST}:{self.port}"

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
        except TimeoutError as exc:
            raise RuntimeError(f"webdriver_timeout:{method}:{path}:{timeout}s") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"webdriver_unreachable:{method}:{path}:{type(exc.reason).__name__}") from exc
        value = body.get("value") if isinstance(body, dict) else None
        if isinstance(value, dict) and value.get("error"):
            raise RuntimeError(f"webdriver_error:{value.get('error')}:{value.get('message')}")
        return value

    def _cleanup(self) -> None:
        if self.session_id and self.base:
            try:
                self._request("DELETE", f"/session/{self.session_id}", timeout=5)
            except Exception:
                pass
        self.session_id = ""
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                try:
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    pass
            except Exception:
                pass
        self.proc = None

    def _start_once(self, driver: str) -> None:
        self._reset_endpoint()
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
        }, timeout=30)
        if not isinstance(value, dict) or not value.get("sessionId"):
            raise RuntimeError("webdriver_session_missing")
        self.session_id = str(value["sessionId"])
        self._request("POST", f"/session/{self.session_id}/timeouts", {
            "implicit": 0, "pageLoad": 10000, "script": 5000,
        })

    def __enter__(self) -> "Browser":
        driver = shutil.which("chromedriver")
        if not driver:
            raise RuntimeError("chromedriver_not_found")
        errors: list[str] = []
        for attempt in range(1, BROWSER_START_ATTEMPTS + 1):
            self.start_attempt = attempt
            try:
                self._start_once(driver)
                print(f"BROWSER_SESSION_START=PASS attempt={attempt}")
                return self
            except Exception as exc:
                errors.append(f"attempt={attempt}:{type(exc).__name__}:{str(exc)[:180]}")
                print(f"BROWSER_SESSION_START=RETRY {errors[-1]}", file=sys.stderr)
                self._cleanup()
                if attempt < BROWSER_START_ATTEMPTS:
                    time.sleep(1.5 * attempt)
        raise RuntimeError("webdriver_session_start_exhausted:" + " | ".join(errors))

    def __exit__(self, exc_type, exc, tb) -> None:
        self._cleanup()

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
            path.parent.mkdir(parents=True, exist_ok=True)
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

    try:
        _verify_deploy_markers()
    except RuntimeError as exc:
        print(f"FRONTEND_DEPLOY_MARKERS=FAIL {exc}", file=sys.stderr)
        return 3

    if PROOF_DIR.exists():
        shutil.rmtree(PROOF_DIR)
    PROOF_DIR.mkdir(parents=True, exist_ok=True)

    preview_port = _free_port()
    base_url = f"http://{HOST}:{preview_port}/ui/"
    preview = subprocess.Popen(
        ["npm", "run", "preview", "--", "--host", HOST, "--port", str(preview_port), "--strictPort"],
        cwd=FRONTEND, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    failures: list[str] = []
    captured = 0
    browser_attempts = 0
    started = time.monotonic()
    try:
        _wait_http(base_url, preview, 20)
        try:
            with Browser() as browser:
                browser_attempts = browser.start_attempt
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
                        time.sleep(0.12)
                        browser.screenshot(PROOF_DIR / f"{tab_id}.png")
                        captured += 1
                        print("TAB_PASS", tab_id, f"screenshot={tab_id}.png")

                if failures:
                    browser.screenshot(PROOF_DIR / "_failure.png")
        except Exception as exc:
            failures.append(f"browser_runtime:{type(exc).__name__}:{str(exc)[:220]}")
            print("BROWSER_RUNTIME=FAIL", failures[-1], file=sys.stderr)
    finally:
        preview.terminate()
        try:
            preview.wait(timeout=5)
        except subprocess.TimeoutExpired:
            preview.kill()

    elapsed = round(time.monotonic() - started, 2)
    manifest = {
        "tabs_expected": len(TABS),
        "screenshots_captured": captured,
        "failures": failures,
        "elapsed_s": elapsed,
        "viewport": "1600x1000",
        "browser_start_attempts": browser_attempts,
        "browser_start_attempt_limit": BROWSER_START_ATTEMPTS,
        "live_trading_actions": 0,
        "deploy_markers": list(REQUIRED_DEPLOY_MARKERS),
    }
    (PROOF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if failures:
        print("FRONTEND_RUNTIME_SMOKE=FAIL", json.dumps(failures), f"elapsed_s={elapsed}", file=sys.stderr)
        return 1
    print(f"FRONTEND_RUNTIME_SMOKE=PASS tabs={len(TABS)} screenshots={captured} elapsed_s={elapsed} live_trading_actions=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
