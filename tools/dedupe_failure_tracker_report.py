#!/usr/bin/env python3
"""Normalize tracker blockers against the latest run of each workflow.

Analyzer-safe report postprocessor. It reads the generated tracker JSON and the
GitHub Actions run list, keeps a workflow blocker only when that workflow's
newest observed run is completed with a bad conclusion, and rewrites the
JSON/Markdown TODO. If the GitHub status query is unavailable it fails closed by
retaining the tracker rows. It never reads or writes broker credentials,
response bodies, cookies, order data, or dashboard secrets.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "github_render_failure_tracker"
SUMMARY_JSON = OUT / "summary.json"
SUMMARY_MD = OUT / "summary.md"
TODO_MD = ROOT / "docs" / "SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "psw2025-cmd/Genesis_System3")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}
EXCLUDED = {
    value.strip()
    for value in os.environ.get(
        "SYSTEM3_RENDER_TRACKER_EXCLUDE_WORKFLOWS",
        "System3 GitHub Render Failure Tracker",
    ).split(",")
    if value.strip()
}


def newest_per_workflow(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    selected: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        name = str(row.get("workflow") or "UNKNOWN")
        current = selected.get(name)
        row_key = (str(row.get("updated_at") or ""), int(row.get("run_id") or 0))
        current_key = (
            str((current or {}).get("updated_at") or ""),
            int((current or {}).get("run_id") or 0),
        )
        if current is None or row_key > current_key:
            selected[name] = row
    return sorted(
        selected.values(),
        key=lambda row: (str(row.get("updated_at") or ""), int(row.get("run_id") or 0)),
        reverse=True,
    )


def query_latest_run_states() -> Tuple[Dict[str, Dict[str, Any]], str | None]:
    """Return newest observed run for each workflow; never persist API payloads."""
    if not TOKEN:
        return {}, "GITHUB_TOKEN_UNAVAILABLE"
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=100"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "system3-failure-tracker-latest-state-reconciler",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except Exception as exc:  # fail closed; expose type only
        return {}, type(exc).__name__

    latest: Dict[str, Dict[str, Any]] = {}
    for run in payload.get("workflow_runs", []):
        name = str(run.get("name") or "UNKNOWN")
        if name in EXCLUDED or name in latest:
            continue
        latest[name] = {
            "workflow": name,
            "run_id": run.get("id"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "commit": run.get("head_sha"),
            "branch": run.get("head_branch"),
            "updated_at": run.get("updated_at"),
            "html_url": run.get("html_url"),
        }
    return latest, None


def reconcile_failures(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str | None]:
    latest, error = query_latest_run_states()
    if error:
        return newest_per_workflow(rows), [], error

    failures: List[Dict[str, Any]] = []
    pending: List[Dict[str, Any]] = []
    for name, run in latest.items():
        status = str(run.get("status") or "")
        conclusion = str(run.get("conclusion") or "")
        if status != "completed":
            pending.append(run)
        elif conclusion in BAD_CONCLUSIONS:
            failures.append(run)

    failures.sort(key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    pending.sort(key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    return failures, pending, None


def workflow_todo(row: Dict[str, Any]) -> str:
    if row.get("workflow") == "GITHUB_API":
        return str(row.get("todo") or "GitHub API workflow query blocked")
    return (
        f"Fix latest GitHub workflow '{row.get('workflow')}' run={row.get('run_id')} "
        f"conclusion={row.get('conclusion')} commit={str(row.get('commit') or '')[:12]}"
    )


def render_todo(row: Dict[str, Any]) -> str:
    return f"Fix Render endpoint {row.get('endpoint')}: {row.get('reason')} status={row.get('status_code')}"


def main() -> int:
    if not SUMMARY_JSON.exists():
        raise SystemExit("tracker summary missing; fail-closed fallback must create it first")

    data = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    failed, pending, reconcile_error = reconcile_failures(list(data.get("failed_workflows") or []))
    render = list(data.get("render_failures") or [])
    todo = [workflow_todo(row) for row in failed] + [render_todo(row) for row in render]

    data["failed_workflows"] = failed
    data["pending_workflows"] = pending
    data["github_failed_count"] = len(failed)
    data["github_pending_count"] = len(pending)
    data["render_failed_count"] = len(render)
    data["todo"] = todo
    data["todo_count"] = len(todo)
    data["status"] = "PASS" if not todo else "BLOCKED"
    data["workflow_failure_count_semantics"] = "latest_observed_run_state_per_workflow"
    data["historical_duplicate_failures_removed"] = True
    data["newer_success_supersedes_older_failure"] = reconcile_error is None
    data["latest_state_reconcile_error_type"] = reconcile_error
    data["live_trading_enabled"] = False
    data["order_routes_called"] = False
    data["secrets_printed"] = False
    data["response_bodies_persisted"] = False
    data["production_grade_claim_allowed"] = False
    SUMMARY_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 GitHub + Render Failure TODO",
        "",
        f"Generated UTC: `{data.get('generated_utc')}`",
        f"Status: **{data.get('status')}**",
        f"Tracker internal status: **{data.get('tracker_internal_status')}**",
        f"Repository: `{data.get('repository')}`",
        f"Render base: `{data.get('render_base')}`",
        f"GitHub workflows whose newest observed run failed: `{len(failed)}`",
        f"GitHub workflows currently queued/in progress: `{len(pending)}`",
        f"Render failed endpoints: `{len(render)}`",
        f"TODO count: `{len(todo)}`",
        "",
        "## Rule",
        "",
        "Only a workflow's newest observed run can remain an active failure. A newer successful run supersedes an older failed run. Pending runs are reported separately and do not revive superseded failures. Dashboard visual proof is still required for final claims.",
        "",
        "## TODO",
        "",
    ]
    lines += [f"- [ ] {item}" for item in todo] or ["- [x] No current GitHub/Render failures detected in this run."]
    lines += ["", "## Latest failed run per workflow", ""]
    if failed:
        lines += ["| Workflow | Run | Conclusion | Commit | Updated | Link |", "|---|---:|---|---|---|---|"]
        for row in failed:
            lines.append(
                f"| {row.get('workflow')} | {row.get('run_id') or '-'} | {row.get('conclusion')} | "
                f"`{str(row.get('commit') or '')[:12]}` | {row.get('updated_at') or '-'} | {row.get('html_url') or '-'} |"
            )
    else:
        lines.append("No workflow has a failed newest observed run.")

    lines += ["", "## Pending workflow runs", ""]
    if pending:
        lines += ["| Workflow | Run | Status | Updated |", "|---|---:|---|---|"]
        for row in pending:
            lines.append(f"| {row.get('workflow')} | {row.get('run_id') or '-'} | {row.get('status') or '-'} | {row.get('updated_at') or '-'} |")
    else:
        lines.append("No queued or in-progress workflow runs in the latest query.")

    lines += ["", "## Render endpoint failures", ""]
    if render:
        lines += ["| Endpoint | Status | Reason | Classification |", "|---|---:|---|---|"]
        for row in render:
            flags = row.get("classification") or {}
            active = ", ".join(sorted(key for key, value in flags.items() if value)) or "none"
            lines.append(f"| `{row.get('endpoint')}` | {row.get('status_code')} | {row.get('reason')} | `{active}` |")
    else:
        lines.append("No Render endpoint failures found in this run.")

    markdown = "\n".join(lines) + "\n"
    SUMMARY_MD.write_text(markdown, encoding="utf-8")
    TODO_MD.write_text(markdown, encoding="utf-8")
    print(json.dumps({
        "status": data["status"],
        "github_failed_count": len(failed),
        "github_pending_count": len(pending),
        "render_failed_count": len(render),
        "todo_count": len(todo),
        "newer_success_supersedes_older_failure": reconcile_error is None,
        "latest_state_reconcile_error_type": reconcile_error,
        "live_trading_enabled": False,
        "order_routes_called": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
