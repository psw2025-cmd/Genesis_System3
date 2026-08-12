#!/usr/bin/env python3
"""Prove the deployed Genesis System3 PAPER dashboard is public/read-only.

The proof binds evidence to the actual single 100%-traffic serving revision,
never merely the latest-created/latest-ready candidate. It performs anonymous
GET requests only, captures the real `/ui`, then runs the all-tab visual proof
for desktop and mobile. No broker order or paper mutation endpoint is called.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path("reports/latest/public_dashboard_proof")
TIMEOUT_S = 30
OFF_VALUES = {"0", "false", "no", "off"}


def _run(*args: str, timeout: int = 90) -> str:
    proc = subprocess.run(list(args), text=True, capture_output=True, timeout=timeout, check=False)
    if proc.returncode:
        raise RuntimeError(f"command_failed:{args[0]}:{proc.returncode}")
    return proc.stdout.strip()


def _json_command(*args: str) -> dict[str, Any]:
    raw = _run(*args)
    value = json.loads(raw or "{}")
    if not isinstance(value, dict):
        raise RuntimeError("gcloud_json_not_object")
    return value


def _service() -> dict[str, Any]:
    return _json_command(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )


def _serving_revision(service: dict[str, Any]) -> str:
    rows = (service.get("status") or {}).get("traffic") or service.get("traffic") or []
    serving: list[str] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        try:
            percent = int(item.get("percent") or 0)
        except (TypeError, ValueError):
            percent = 0
        if percent != 100:
            continue
        revision = str(item.get("revisionName") or item.get("revision") or "").split("/")[-1]
        if revision:
            serving.append(revision)
    if len(serving) != 1:
        raise RuntimeError(f"serving_revision_not_single_100:{serving}")
    return serving[0]


def _revision(name: str) -> dict[str, Any]:
    return _json_command(
        "gcloud", "run", "revisions", "describe", name,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )


def _containers(resource: dict[str, Any]) -> list[dict[str, Any]]:
    spec = resource.get("spec") or {}
    rows = spec.get("containers") or []
    if not rows:
        rows = (((resource.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or []
    if not rows:
        rows = (resource.get("template") or {}).get("containers") or []
    return [row for row in rows if isinstance(row, dict)]


def _env(resource: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    rows = _containers(resource)
    if not rows:
        raise RuntimeError("cloud_run_container_missing")
    plain: dict[str, str] = {}
    secrets: set[str] = set()
    for row in rows[0].get("env") or []:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "")
        if not name:
            continue
        if "value" in row:
            plain[name] = str(row.get("value") or "")
        value_from = row.get("valueFrom") or {}
        value_source = row.get("valueSource") or {}
        if value_from.get("secretKeyRef") or value_source.get("secretKeyRef"):
            secrets.add(name)
    return plain, secrets


def _service_url(service: dict[str, Any]) -> str:
    url = str((service.get("status") or {}).get("url") or service.get("uri") or "").rstrip("/")
    if not url.startswith("https://"):
        raise RuntimeError("cloud_run_https_url_missing")
    return url


def _is_off(value: Any) -> bool:
    return str(value or "").strip().lower() in OFF_VALUES


def _get_json(url: str) -> tuple[int, dict[str, Any]]:
    response = requests.get(url, timeout=TIMEOUT_S)
    try:
        body = response.json()
    except Exception:
        body = {}
    return response.status_code, body if isinstance(body, dict) else {}


def _browser_path() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("headless_chrome_not_found")


def _browser_args(url: str) -> list[str]:
    return [
        _browser_path(), "--headless", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", "--window-size=1600,1000",
        "--virtual-time-budget=12000", url,
    ]


def _render_dom(url: str) -> str:
    args = _browser_args(url)
    args.insert(-1, "--dump-dom")
    proc = subprocess.run(args, text=True, capture_output=True, timeout=60, check=False)
    if proc.returncode:
        raise RuntimeError(f"dashboard_dom_render_failed:{proc.returncode}")
    return proc.stdout or ""


def _capture(url: str, path: Path) -> None:
    args = _browser_args(url)
    args.insert(-1, f"--screenshot={path}")
    proc = subprocess.run(args, text=True, capture_output=True, timeout=60, check=False)
    if proc.returncode or not path.is_file() or path.stat().st_size < 1000:
        raise RuntimeError(f"dashboard_screenshot_failed:{proc.returncode}")


def _publish_status(state: str, description: str) -> None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    if not (token and repo and EXPECTED_SHA):
        raise RuntimeError("github_status_context_missing")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    run_id = os.getenv("GITHUB_RUN_ID", "").strip()
    target = f"{server}/{repo}/actions/runs/{run_id}" if run_id else f"{server}/{repo}"
    payload = json.dumps({
        "state": state,
        "context": "public-dashboard/runtime-proof",
        "description": description[:140],
        "target_url": target,
    }).encode()
    request = urllib.request.Request(
        f"{api}/repos/{repo}/statuses/{EXPECTED_SHA}",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 201):
            raise RuntimeError(f"commit_status_publish_failed:{response.status}")


def _run_tab_matrix() -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, "scripts/gcp_ui_tab_visual_proof.py"],
        text=True, capture_output=True, timeout=1200, check=False,
    )
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    matrix_path = OUT / "tab_visual_matrix.json"
    if proc.returncode or not matrix_path.is_file():
        raise RuntimeError(f"ui_tab_visual_proof_failed:{proc.returncode}")
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    if not isinstance(matrix, dict) or matrix.get("state") != "PASS":
        raise RuntimeError("ui_tab_visual_matrix_not_pass")
    return matrix


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    config_proof: dict[str, Any] = {"state": "FAIL", "expected_sha": EXPECTED_SHA}
    http_proof: dict[str, Any] = {"state": "FAIL"}
    try:
        if len(EXPECTED_SHA) != 40:
            raise RuntimeError("expected_git_sha_missing")

        service = _service()
        serving_revision = _serving_revision(service)
        revision = _revision(serving_revision)
        env, secret_names = _env(revision)
        url = _service_url(service)

        failures: list[str] = []
        if env.get("DEPLOY_GIT_SHA") != EXPECTED_SHA:
            failures.append("serving_deploy_git_sha_mismatch")
        if not _is_off(env.get("REQUIRE_API_KEY")):
            failures.append("dashboard_api_key_requirement_not_disabled")
        if "API_KEY" in secret_names:
            failures.append("dashboard_api_key_still_mounted")
        if env.get("ANALYZE_MODE") != "1":
            failures.append("analyze_mode_not_enabled")
        if str(env.get("SYSTEM3_MODE") or "").upper() != "ANALYZER":
            failures.append("system3_mode_not_analyzer")
        for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES"):
            if not _is_off(env.get(key)):
                failures.append(f"{key.lower()}_not_off")

        config_proof = {
            "state": "PASS" if not failures else "FAIL",
            "expected_sha": EXPECTED_SHA,
            "serving_revision": serving_revision,
            "serving_deploy_git_sha": env.get("DEPLOY_GIT_SHA"),
            "traffic_authority": "single_100_percent_serving_revision",
            "require_api_key": env.get("REQUIRE_API_KEY"),
            "api_key_mounted": "API_KEY" in secret_names,
            "worker_token_mounted": "WORKER_PUSH_TOKEN" in secret_names,
            "analyze_mode": env.get("ANALYZE_MODE"),
            "system3_mode": env.get("SYSTEM3_MODE"),
            "live_trading_enabled": env.get("LIVE_TRADING_ENABLED"),
            "system3_live_trading_allowed": env.get("SYSTEM3_LIVE_TRADING_ALLOWED"),
            "auto_execute_trades": env.get("AUTO_EXECUTE_TRADES"),
            "failures": failures,
        }
        (OUT / "config.json").write_text(json.dumps(config_proof, indent=2, sort_keys=True), encoding="utf-8")
        if failures:
            raise RuntimeError("public_dashboard_config_proof_failed")

        root = requests.get(f"{url}/", timeout=TIMEOUT_S)
        try:
            root_payload = root.json() if root.status_code == 200 else {}
        except Exception:
            root_payload = {}
        root_payload = root_payload if isinstance(root_payload, dict) else {}
        relative = root_payload.get("relative_paths") if isinstance(root_payload.get("relative_paths"), dict) else {}
        dashboard_path = str(relative.get("dashboard") or "/ui")
        if not dashboard_path.startswith("/") or dashboard_path.startswith("//"):
            raise RuntimeError("unsafe_dashboard_relative_path")
        dashboard_url = urljoin(url + "/", dashboard_path.lstrip("/"))
        dashboard = requests.get(dashboard_url, timeout=TIMEOUT_S)

        auth_status, auth = _get_json(f"{url}/api/auth/status")
        state_status, _ = _get_json(f"{url}/api/state")
        health_status, _ = _get_json(f"{url}/api/health")
        html = dashboard.text if dashboard.status_code == 200 else ""
        html_shell = '<div id="root"' in html or "<div id='root'" in html
        http_failures: list[str] = []
        for label, status in (
            ("root", root.status_code), ("dashboard_ui", dashboard.status_code),
            ("auth_status", auth_status), ("state", state_status), ("health", health_status),
        ):
            if status != 200:
                http_failures.append(f"{label}_http_{status}")
        if not html_shell:
            http_failures.append("dashboard_ui_html_shell_missing")
        if auth.get("required") is not False:
            http_failures.append("auth_status_required_not_false")
        if auth.get("mode") != "public_readonly":
            http_failures.append("auth_status_mode_not_public_readonly")
        if auth.get("configured") is not False:
            http_failures.append("auth_status_configured_not_false")
        if auth.get("authenticated") is not False:
            http_failures.append("auth_status_authenticated_not_false")
        if auth.get("credential_surface") != "REMOVED":
            http_failures.append("auth_status_credential_surface_not_removed")
        if auth.get("session") is not None:
            http_failures.append("auth_status_session_not_null")

        http_proof = {
            "state": "PASS" if not http_failures else "FAIL",
            "service_url": url,
            "dashboard_path": dashboard_path,
            "dashboard_url": dashboard_url,
            "serving_revision": serving_revision,
            "root_http_status": root.status_code,
            "dashboard_ui_http_status": dashboard.status_code,
            "dashboard_ui_html_shell": html_shell,
            "auth_status_http_status": auth_status,
            "state_http_status": state_status,
            "health_http_status": health_status,
            "auth_required": auth.get("required"),
            "auth_mode": auth.get("mode"),
            "auth_configured": auth.get("configured"),
            "auth_authenticated": auth.get("authenticated"),
            "auth_credential_surface": auth.get("credential_surface"),
            "auth_session": auth.get("session"),
            "api_key_sent_for_dashboard_reads": False,
            "cookie_sent_for_dashboard_reads": False,
            "dashboard_visible_without_login": not http_failures,
            "failures": http_failures,
        }
        (OUT / "http.json").write_text(json.dumps(http_proof, indent=2, sort_keys=True), encoding="utf-8")
        if http_failures:
            raise RuntimeError("public_dashboard_http_proof_failed")

        dom = _render_dom(dashboard_url)
        upper_dom = dom.upper()
        if "SYSTEM3" not in upper_dom:
            raise RuntimeError("rendered_product_marker_missing")
        if "DASHBOARD API KEY" in upper_dom:
            raise RuntimeError("dashboard_login_prompt_still_rendered")

        screenshot = OUT / "dashboard.png"
        _capture(dashboard_url, screenshot)
        digest = hashlib.sha256(screenshot.read_bytes()).hexdigest()
        (OUT / "dashboard.sha256").write_text(f"{digest}  dashboard.png\n", encoding="utf-8")
        visual = {
            "state": "PASS",
            "sha256": digest,
            "bytes": screenshot.stat().st_size,
            "viewport": "1600x1000",
            "source": "real_deployed_cloud_run_dashboard_ui",
            "serving_revision": serving_revision,
            "dashboard_path": dashboard_path,
            "rendered_system3_marker": True,
            "dashboard_api_key_prompt_rendered": False,
            "api_key_used": False,
        }
        (OUT / "visual.json").write_text(json.dumps(visual, indent=2, sort_keys=True), encoding="utf-8")

        matrix = _run_tab_matrix()
        tab_count = int(matrix.get("tab_count") or 0)
        pass_count = int(matrix.get("pass_count") or 0)
        _publish_status("success", f"PAPER /ui no-key + {pass_count}/{tab_count} tab visuals passed; LIVE OFF")
        print("PUBLIC_DASHBOARD_RUNTIME_PROOF " + json.dumps({
            "state": "PASS",
            "sha": EXPECTED_SHA,
            "serving_revision": serving_revision,
            "dashboard_path": dashboard_path,
            "dashboard_ui_http_status": dashboard.status_code,
            "api_key_mounted": False,
            "api_key_prompt_rendered": False,
            "screenshot_sha256": digest,
            "tab_visual_pass_count": pass_count,
            "tab_visual_count": tab_count,
            "live_trading_enabled": False,
        }, sort_keys=True))
        return 0
    except Exception as exc:
        (OUT / "config.json").write_text(json.dumps(config_proof, indent=2, sort_keys=True), encoding="utf-8")
        (OUT / "http.json").write_text(json.dumps(http_proof, indent=2, sort_keys=True), encoding="utf-8")
        try:
            _publish_status("failure", "Public PAPER dashboard or tab visual proof failed")
        except Exception as status_exc:
            print(f"PUBLIC_DASHBOARD_STATUS_PUBLISH_ERROR {type(status_exc).__name__}", file=sys.stderr)
        print("PUBLIC_DASHBOARD_RUNTIME_PROOF " + json.dumps({
            "state": "FAIL", "error_type": type(exc).__name__, "error": str(exc)[:180],
        }, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())