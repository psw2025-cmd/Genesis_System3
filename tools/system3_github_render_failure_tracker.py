#!/usr/bin/env python3
"""
System3 GitHub + Render Failure Tracker

Purpose:
- Track GitHub workflow failures and Render public health/UI failures together.
- Write persistent MD/JSON TODO so failures are visible next run.
- Never print secrets.
- Never call live order routes.
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def http_probe(path: str) -> Dict[str, Any]:
    url = path if path.startswith("http") else BASE + path
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "system3-github-render-failure-tracker"})
        with urllib.request.urlopen(req, timeout=35) as resp:
            body = resp.read(20000).decode("utf-8", errors="replace")
            return {
                "url": url,
                "ok": 200 <= int(resp.status) < 400,
                "status_code": int(resp.status),
                "body_sample": body[:2000],
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(20000).decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        return {"url": url, "ok": False, "status_code": int(exc.code), "body_sample": body[:2000]}
    except Exception as exc:
        return {"url": url, "ok": False, "status_code": 0, "error": f"{type(exc).__name__}: {str(exc)[:500]}"}


def latest_failed_workflows() -> List[Dict[str, Any]]:
    if not TOKEN:
        return [{"workflow": "GITHUB_API", "conclusion": "blocked", "todo": "GITHUB_TOKEN unavailable; cannot query workflow failures."}]
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=50"
    try:
        data = get_json(url, TOKEN)
    except Exception as exc:
        return [{"workflow": "GITHUB_API", "conclusion": "blocked", "todo": f"GitHub API run query failed: {type(exc).__name__}: {str(exc)[:300]}"}]
    failed = []
    for run in data.get("workflow_runs", []):
        if run.get("status") == "completed" and run.get("conclusion") in BAD_CONCLUSIONS:
            failed.append(
                {
                    "workflow": run.get("name"),
                    "run_id": run.get("id"),
                    "conclusion": run.get("conclusion"),
                    "commit": run.get("head_sha"),
                    "branch": run.get("head_branch"),
                    "updated_at": run.get("updated_at"),
                    "html_url": run.get("html_url"),
                }
            )
    return failed


def render_failures() -> List[Dict[str, Any]]:
    failures = []
    for ep in RENDER_ENDPOINTS:
        r = http_probe(ep)
        sample = str(r.get("body_sample") or r.get("error") or "")
        low = sample.lower()
        reason = None
        if not r.get("ok"):
            reason = f"HTTP status {r.get('status_code')}"
        elif ep == "/api/deploy/info" and "commit" not in low and "sha" not in low:
            reason = "deploy info does not expose commit/sha; stale Render proof risk"
        elif any(x in low for x in ["traceback", "internal server error", "invalid_authentication", "unauthorized"]):
            reason = "error/auth text visible in response"
        if reason:
            failures.append({"endpoint": ep, "url": r.get("url"), "reason": reason, "status_code": r.get("status_code"), "sample": sample[:400]})
    return failures


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    failed_runs = latest_failed_workflows()
    render = render_failures()
    todo = []
    for r in failed_runs:
        if r.get("workflow") == "GITHUB_API":
            todo.append(r.get("todo"))
        else:
            todo.append(f"Fix GitHub workflow '{r.get('workflow')}' run={r.get('run_id')} conclusion={r.get('conclusion')} commit={str(r.get('commit') or '')[:12]}")
    for r in render:
        todo.append(f"Fix Render endpoint {r.get('endpoint')}: {r.get('reason')} status={r.get('status_code')}")

    payload = {
        "generated_utc": utc(),
        "status": "PASS" if not todo else "BLOCKED",
        "repository": REPO,
        "render_base": BASE,
        "github_failed_count": len(failed_runs),
        "render_failed_count": len(render),
        "todo_count": len(todo),
        "failed_workflows": failed_runs,
        "render_failures": render,
        "todo": todo,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 GitHub + Render Failure TODO",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Repository: `{payload['repository']}`",
        f"Render base: `{payload['render_base']}`",
        f"GitHub failed workflows: `{payload['github_failed_count']}`",
        f"Render failed endpoints: `{payload['render_failed_count']}`",
        f"TODO count: `{payload['todo_count']}`",
        "",
        "## Rule",
        "",
        "Every failed GitHub workflow and Render endpoint failure stays in this TODO until a later run proves PASS. Do not claim resolved from chat, logs, or file existence; dashboard visual proof is still required for final claims.",
        "",
        "## TODO",
        "",
    ]
    lines += [f"- [ ] {x}" for x in todo] or ["- [x] No GitHub/Render failures detected in this run."]
    lines += ["", "## GitHub workflow failures", ""]
    if failed_runs:
        lines += ["| Workflow | Run | Conclusion | Commit | Updated | Link |", "|---|---:|---|---|---|---|"]
        for r in failed_runs:
            if r.get("workflow") == "GITHUB_API":
                lines.append(f"| GITHUB_API | - | blocked | - | - | {r.get('todo')} |")
            else:
                lines.append(f"| {r.get('workflow')} | {r.get('run_id')} | {r.get('conclusion')} | `{str(r.get('commit') or '')[:12]}` | {r.get('updated_at')} | {r.get('html_url')} |")
    else:
        lines.append("No failed GitHub workflow runs found in latest query.")
    lines += ["", "## Render endpoint failures", ""]
    if render:
        lines += ["| Endpoint | Status | Reason | Sample |", "|---|---:|---|---|"]
        for r in render:
            sample = str(r.get("sample") or "").replace("\n", " ")[:160]
            lines.append(f"| `{r.get('endpoint')}` | {r.get('status_code')} | {r.get('reason')} | `{sample}` |")
    else:
        lines.append("No Render endpoint failures found in this run.")

    md = "\n".join(lines) + "\n"
    (OUT / "summary.md").write_text(md, encoding="utf-8")
    TODO_MD.write_text(md, encoding="utf-8")
    print(json.dumps(payload, indent=2)[:12000])
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
