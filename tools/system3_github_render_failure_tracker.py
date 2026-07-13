#!/usr/bin/env python3
"""
System3 GitHub + Render Failure Tracker

Purpose:
- Track GitHub workflow failures and Render public health/UI failures together.
- Write persistent MD/JSON TODO so failures are visible next run.
- Never print or persist secrets, response bodies, cookies, or tokens.
- Never call live order routes.

Important design rule:
- This tracker is REPORT-ONLY. It must not fail just because it found blockers;
  otherwise it creates an infinite self-failure storm.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "github_render_failure_tracker"
TODO_MD = ROOT / "docs" / "SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "psw2025-cmd/Genesis_System3")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
BASE = os.environ.get("DASHBOARD_BASE_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}
SELF_WORKFLOW = "System3 GitHub Render Failure Tracker"
EXCLUDED_WORKFLOWS = {
    name.strip()
    for name in os.environ.get("SYSTEM3_RENDER_TRACKER_EXCLUDE_WORKFLOWS", SELF_WORKFLOW).split(",")
    if name.strip()
}
RENDER_ENDPOINT_TIMEOUT_S = float(os.environ.get("SYSTEM3_RENDER_TRACKER_ENDPOINT_TIMEOUT_S", "12"))
GITHUB_TIMEOUT_S = float(os.environ.get("SYSTEM3_RENDER_TRACKER_GITHUB_TIMEOUT_S", "12"))
RENDER_ENDPOINTS = [
    "/",
    "/ui/",
    "/api/health",
    "/api/state",
    "/api/deploy/info",
    "/api/broker/diagnose",
    "/api/broker/funds",
    "/api/broker/holdings",
    "/api/broker/positions/live",
    "/api/scanner/top_contract_gainers",
    "/api/paper",
    "/api/ml/performance",
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_json(url: str, token: str = "") -> Dict[str, Any]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "system3-github-render-failure-tracker"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=GITHUB_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def classify_body(body: str) -> Dict[str, bool]:
    """Return safe booleans only; never return or persist response content."""
    low = body.lower()
    return {
        "mentions_commit_or_sha": "commit" in low or "sha" in low,
        "mentions_auth_error": any(
            marker in low
            for marker in (
                "invalid_authentication",
                "missing or invalid dashboard api session",
                "unauthorized",
            )
        ),
        "mentions_server_error": "traceback" in low or "internal server error" in low,
    }


def http_probe(path: str) -> Dict[str, Any]:
    url = path if path.startswith("http") else BASE + path
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "system3-github-render-failure-tracker"})
        with urllib.request.urlopen(req, timeout=RENDER_ENDPOINT_TIMEOUT_S) as resp:
            body = resp.read(20000).decode("utf-8", errors="replace")
            return {
                "url": url,
                "ok": 200 <= int(resp.status) < 400,
                "status_code": int(resp.status),
                "classification": classify_body(body),
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(20000).decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        return {
            "url": url,
            "ok": False,
            "status_code": int(exc.code),
            "classification": classify_body(body),
        }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "status_code": 0,
            "error_type": type(exc).__name__,
            "classification": {
                "mentions_commit_or_sha": False,
                "mentions_auth_error": False,
                "mentions_server_error": False,
            },
        }


def latest_failed_workflows() -> List[Dict[str, Any]]:
    if not TOKEN:
        return [{"workflow": "GITHUB_API", "conclusion": "blocked", "todo": "GITHUB_TOKEN unavailable; cannot query workflow failures."}]
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=50"
    try:
        data = get_json(url, TOKEN)
    except urllib.error.HTTPError as exc:
        # Keep this non-sensitive and useful for auth/rate-limit triage.
        reason = f"GitHub API run query failed: HTTP {exc.code}"
        if exc.code in (401, 403):
            reason += " (auth/rate-limit/permission candidate)"
        return [{"workflow": "GITHUB_API", "conclusion": "blocked", "todo": reason}]
    except Exception as exc:
        return [{"workflow": "GITHUB_API", "conclusion": "blocked", "todo": f"GitHub API run query failed: {type(exc).__name__}"}]

    failed = []
    excluded_seen = 0
    for run in data.get("workflow_runs", []):
        workflow_name = run.get("name") or "UNKNOWN"
        if workflow_name in EXCLUDED_WORKFLOWS:
            excluded_seen += 1
            continue
        if run.get("status") == "completed" and run.get("conclusion") in BAD_CONCLUSIONS:
            failed.append(
                {
                    "workflow": workflow_name,
                    "run_id": run.get("id"),
                    "conclusion": run.get("conclusion"),
                    "commit": run.get("head_sha"),
                    "branch": run.get("head_branch"),
                    "updated_at": run.get("updated_at"),
                    "html_url": run.get("html_url"),
                }
            )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "excluded_workflows.json").write_text(
        json.dumps({"excluded_workflows": sorted(EXCLUDED_WORKFLOWS), "excluded_seen_in_latest_query": excluded_seen}, indent=2),
        encoding="utf-8",
    )
    return failed


def render_failures() -> List[Dict[str, Any]]:
    failures = []
    for ep in RENDER_ENDPOINTS:
        result = http_probe(ep)
        classification = result.get("classification") or {}
        reason = None
        if not result.get("ok"):
            reason = f"HTTP status {result.get('status_code')}"
        elif ep == "/api/deploy/info" and not classification.get("mentions_commit_or_sha"):
            reason = "deploy info does not expose commit/sha; stale Render proof risk"
        elif classification.get("mentions_auth_error"):
            reason = "authentication error classification detected"
        elif classification.get("mentions_server_error"):
            reason = "server error classification detected"
        if reason:
            failures.append(
                {
                    "endpoint": ep,
                    "url": result.get("url"),
                    "reason": reason,
                    "status_code": result.get("status_code"),
                    "error_type": result.get("error_type"),
                    "classification": classification,
                }
            )
    return failures


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failed_runs = latest_failed_workflows()
    render = render_failures()
    todo = []
    for run in failed_runs:
        if run.get("workflow") == "GITHUB_API":
            todo.append(run.get("todo"))
        else:
            todo.append(
                f"Fix GitHub workflow '{run.get('workflow')}' run={run.get('run_id')} "
                f"conclusion={run.get('conclusion')} commit={str(run.get('commit') or '')[:12]}"
            )
    for failure in render:
        todo.append(
            f"Fix Render endpoint {failure.get('endpoint')}: "
            f"{failure.get('reason')} status={failure.get('status_code')}"
        )

    payload = {
        "generated_utc": utc(),
        "status": "PASS" if not todo else "BLOCKED",
        "tracker_internal_status": "PASS",
        "repository": REPO,
        "render_base": BASE,
        "github_failed_count": len(failed_runs),
        "render_failed_count": len(render),
        "todo_count": len(todo),
        "failed_workflows": failed_runs,
        "render_failures": render,
        "todo": todo,
        "excluded_workflows": sorted(EXCLUDED_WORKFLOWS),
        "render_endpoint_timeout_s": RENDER_ENDPOINT_TIMEOUT_S,
        "github_timeout_s": GITHUB_TIMEOUT_S,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "response_bodies_persisted": False,
        "production_grade_claim_allowed": False,
        "report_only_no_self_failure_storm": True,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 GitHub + Render Failure TODO",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Tracker internal status: **{payload['tracker_internal_status']}**",
        f"Repository: `{payload['repository']}`",
        f"Render base: `{payload['render_base']}`",
        f"Excluded workflows: `{', '.join(payload['excluded_workflows'])}`",
        f"GitHub failed workflows: `{payload['github_failed_count']}`",
        f"Render failed endpoints: `{payload['render_failed_count']}`",
        f"TODO count: `{payload['todo_count']}`",
        "",
        "## Rule",
        "",
        "Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. The tracker is report-only and must not create a self-failure storm. Dashboard visual proof is still required for final claims.",
        "",
        "## TODO",
        "",
    ]
    lines += [f"- [ ] {item}" for item in todo] or ["- [x] No GitHub/Render failures detected in this run."]
    lines += ["", "## GitHub workflow failures", ""]
    if failed_runs:
        lines += ["| Workflow | Run | Conclusion | Commit | Updated | Link |", "|---|---:|---|---|---|---|"]
        for run in failed_runs:
            if run.get("workflow") == "GITHUB_API":
                lines.append(f"| GITHUB_API | - | blocked | - | - | {run.get('todo')} |")
            else:
                lines.append(
                    f"| {run.get('workflow')} | {run.get('run_id')} | {run.get('conclusion')} | "
                    f"`{str(run.get('commit') or '')[:12]}` | {run.get('updated_at')} | {run.get('html_url')} |"
                )
    else:
        lines.append("No failed GitHub workflow runs found in latest query after excluding tracker self-runs.")
    lines += ["", "## Render endpoint failures", ""]
    if render:
        lines += ["| Endpoint | Status | Reason | Classification |", "|---|---:|---|---|"]
        for failure in render:
            flags = failure.get("classification") or {}
            active_flags = ", ".join(sorted(name for name, value in flags.items() if value)) or "none"
            lines.append(
                f"| `{failure.get('endpoint')}` | {failure.get('status_code')} | "
                f"{failure.get('reason')} | `{active_flags}` |"
            )
    else:
        lines.append("No Render endpoint failures found in this run.")

    markdown = "\n".join(lines) + "\n"
    (OUT / "summary.md").write_text(markdown, encoding="utf-8")
    TODO_MD.write_text(markdown, encoding="utf-8")

    # Log only non-sensitive counters and safety flags. Never print the full payload.
    print(
        json.dumps(
            {
                "generated_utc": payload["generated_utc"],
                "status": payload["status"],
                "tracker_internal_status": payload["tracker_internal_status"],
                "github_failed_count": payload["github_failed_count"],
                "render_failed_count": payload["render_failed_count"],
                "todo_count": payload["todo_count"],
                "excluded_workflows": payload["excluded_workflows"],
                "live_trading_enabled": payload["live_trading_enabled"],
                "order_routes_called": payload["order_routes_called"],
                "response_bodies_persisted": payload["response_bodies_persisted"],
                "report_only_no_self_failure_storm": payload["report_only_no_self_failure_storm"],
            },
            sort_keys=True,
        )
    )
    # Report-only workflow: never fail solely because blockers were detected.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
