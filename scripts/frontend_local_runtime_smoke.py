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
import hashlib
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "dashboard" / "frontend"
PROOF_DIR = ROOT / "frontend-ui-proof"
HOST = "127.0.0.1"

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
    "data-integrity", "broker", "alerts", "system", "system-readiness", "gates",
]
MOBILE_VIEWPORT_WIDTH = 390


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
        _wait_http(f"{self.base}/status", self.proc, 20)
        # GitHub-hosted runners occasionally need >15s to cold-start headless
        # Chrome even after chromedriver /status is ready.  The old 15s HTTP
        # deadline produced false CI failures before any tab was exercised.
        # Keep one session creation request, but give that bounded startup path
        # enough time; the workflow still has an outer 180s attempt budget.
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
        }, timeout=60)
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

    def set_viewport(self, width: int, height: int) -> None:
        self._request("POST", f"/session/{self.session_id}/goog/cdp/execute", {
            "cmd": "Emulation.setDeviceMetricsOverride",
            "params": {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": True},
        }, timeout=8)

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
const main = document.getElementById('dashboard-main');
const mainText = (main && main.innerText || '').trim();
const heading = main && main.querySelector('h1,h2,h3,.workspace-title,.panel-title');
const overflowNodes = main ? Array.from(main.querySelectorAll('*')).filter(el => {
  const style = getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  return rect.width > 0 && rect.height > 0 && (rect.right > window.innerWidth + 2 || el.scrollWidth > el.clientWidth + 8) && style.display !== 'none';
}).slice(0, 8).map(el => ({tag: el.tagName, cls: String(el.className || '').slice(0, 90), right: Math.round(el.getBoundingClientRect().right), client: el.clientWidth, scroll: el.scrollWidth, overflowX: getComputedStyle(el).overflowX})) : [];
const button = document.querySelector('[data-dashboard-tab="' + CSS.escape(id) + '"]');
const text = (document.body && document.body.innerText || '').toUpperCase();
return {
  readyState: document.readyState,
  viewportWidth: window.innerWidth,
  rootChildren: root ? root.childElementCount : -1,
  active: !!button && button.getAttribute('aria-current') === 'page',
  system3: text.includes('SYSTEM3'),
  keyPrompt: text.includes('DASHBOARD API KEY') || text.includes('ENTER API KEY'),
  horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
  mainChars: mainText.length,
  mainHeading: heading ? (heading.innerText || '').trim().slice(0, 100) : '',
  loadingFallback: mainText.includes('Loading dashboard section'),
  overflowNodes,
  bodyText: text.slice(0, 300),
};
""", [tab_id])
        return value if isinstance(value, dict) else {}

    def screenshot(self, path: Path) -> None:
        encoded = self._request("GET", f"/session/{self.session_id}/screenshot", timeout=10)
        if isinstance(encoded, str) and encoded:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(base64.b64decode(encoded))


def _wait_tab(browser: Browser, tab_id: str, timeout_s: float = 10.0) -> dict:
    deadline = time.monotonic() + timeout_s
    snap: dict = {}
    while time.monotonic() < deadline:
        snap = browser.snapshot(tab_id)
        if (
            snap.get("rootChildren", 0) > 0
            and snap.get("system3")
            and snap.get("active")
            and snap.get("mainChars", 0) > 10
            and snap.get("mainHeading")
            and not snap.get("loadingFallback")
        ):
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
    node = shutil.which("node")
    vite_cli = FRONTEND / "node_modules" / "vite" / "bin" / "vite.js"
    if not node or not vite_cli.is_file():
        print("FAIL: node or local Vite CLI unavailable", file=sys.stderr)
        return 2
    preview = subprocess.Popen(
        [node, str(vite_cli), "preview", "--host", HOST, "--port", str(preview_port), "--strictPort"],
        cwd=FRONTEND, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    failures: list[str] = []
    captured = 0
    started = time.monotonic()
    try:
        _wait_http(base_url, preview, 20)
        with Browser() as browser:
            browser.navigate(base_url + "?tab=decision-intel")
            first = _wait_tab(browser, "decision-intel", 5)
            if first.get("rootChildren", 0) <= 0 or not first.get("system3"):
                failures.append("initial_mount:react_root_or_system3_missing")

            for tab_id in TABS:
                if not browser.activate(tab_id):
                    failures.append(f"{tab_id}:sidebar_button_missing")
                    print("TAB_FAIL", tab_id, "sidebar_button_missing")
                    continue
                snap = _wait_tab(browser, tab_id, 10)
                tab_failures: list[str] = []
                if snap.get("rootChildren", 0) <= 0:
                    tab_failures.append("react_root_empty")
                if not snap.get("system3"):
                    tab_failures.append("system3_marker_missing")
                if not snap.get("active"):
                    tab_failures.append("active_tab_not_proven")
                if snap.get("mainChars", 0) <= 10 or not snap.get("mainHeading"):
                    tab_failures.append("tab_content_not_proven")
                if snap.get("loadingFallback"):
                    tab_failures.append("lazy_content_still_loading")
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

            # Give the mobile viewport a fresh renderer. Desktop chart-heavy tabs
            # otherwise accumulate GPU/DOM state and can crash Chromium mid-loop.
            browser.__exit__(None, None, None)
            browser = Browser().__enter__()
            browser.navigate(base_url + "?tab=decision-intel")
            _wait_tab(browser, "decision-intel", 10)
            browser.set_viewport(MOBILE_VIEWPORT_WIDTH, 844)
            # Let the app's bounded route-chunk prefetch settle in the new
            # mobile renderer before measuring per-tab loading behavior.
            time.sleep(3)
            for tab_id in TABS:
                if not browser.activate(tab_id):
                    failures.append(f"mobile_{tab_id}:sidebar_button_missing")
                    continue
                snap = _wait_tab(browser, tab_id, 10)
                if tab_id == "decision-intel":
                    print("MOBILE_LAYOUT_DIAGNOSTIC", json.dumps(snap.get("overflowNodes", []), sort_keys=True))
                if (
                    not snap.get("active")
                    or not snap.get("system3")
                    or abs(snap.get("viewportWidth", 9999) - MOBILE_VIEWPORT_WIDTH) > 1
                    or snap.get("mainChars", 0) <= 10
                    or not snap.get("mainHeading")
                    or snap.get("loadingFallback")
                ):
                    failures.append(f"mobile_{tab_id}:render_not_proven")
                    print("MOBILE_TAB_FAIL", tab_id, json.dumps(snap, sort_keys=True))
                    continue
                if snap.get("horizontalOverflow"):
                    failures.append(f"mobile_{tab_id}:horizontal_overflow")
                    print("MOBILE_TAB_FAIL", tab_id, "horizontal_overflow")
                    continue
                browser.screenshot(PROOF_DIR / "mobile" / f"{tab_id}.png")
                captured += 1
                print("MOBILE_TAB_PASS", tab_id)

            if failures:
                browser.screenshot(PROOF_DIR / "_failure.png")
    finally:
        preview.terminate()
        try:
            preview.wait(timeout=5)
        except subprocess.TimeoutExpired:
            preview.kill()

    elapsed = round(time.monotonic() - started, 2)
    desktop_failed = {item.split(":", 1)[0] for item in failures if not item.startswith("mobile_")}
    mobile_failed = {
        item.split(":", 1)[0].removeprefix("mobile_")
        for item in failures if item.startswith("mobile_")
    }

    def screenshot_record(relative: str) -> dict:
        path = PROOF_DIR / relative
        if not path.is_file():
            return {"path": relative, "status": "MISSING"}
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return {"path": relative, "status": "CAPTURED", "sha256": digest}

    tab_results = []
    for tab_id in TABS:
        desktop = screenshot_record(f"{tab_id}.png")
        mobile = screenshot_record(f"mobile/{tab_id}.png")
        desktop_ok = tab_id not in desktop_failed and desktop["status"] == "CAPTURED"
        mobile_ok = tab_id not in mobile_failed and mobile["status"] == "CAPTURED"
        tab_results.append({
            "tab_id": tab_id,
            "desktop_status": "PASS" if desktop_ok else "FAIL",
            "desktop_screenshot": desktop,
            "mobile_status": "PASS" if mobile_ok else "FAIL",
            "mobile_screenshot": mobile,
        })
    manifest = {
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "tabs_expected": len(TABS),
        "screenshots_captured": captured,
        "desktop_tabs_passed": sum(item["desktop_status"] == "PASS" for item in tab_results),
        "mobile_tabs_passed": sum(item["mobile_status"] == "PASS" for item in tab_results),
        "failures": failures,
        "elapsed_s": elapsed,
        "viewports": ["1600x1000", "390x844"],
        "live_trading_actions": 0,
        "deploy_markers": list(REQUIRED_DEPLOY_MARKERS),
        "tabs": tab_results,
    }
    (PROOF_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if failures:
        print("FRONTEND_RUNTIME_SMOKE=FAIL", json.dumps(failures), f"elapsed_s={elapsed}", file=sys.stderr)
        return 1
    print(f"FRONTEND_RUNTIME_SMOKE=PASS tabs={len(TABS)} desktop_mobile_screenshots={captured} mobile_viewport={MOBILE_VIEWPORT_WIDTH}px elapsed_s={elapsed} live_trading_actions=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
