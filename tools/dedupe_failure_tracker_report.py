#!/usr/bin/env python3
"""Normalize the failure tracker to one current blocker per workflow.

Analyzer-safe report postprocessor. It reads only the generated tracker JSON,
keeps the newest failed/cancelled run for each workflow, and rewrites the
JSON/Markdown TODO. It never reads or writes credentials, response bodies,
cookies, tokens, or order data.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "github_render_failure_tracker"
SUMMARY_JSON = OUT / "summary.json"
SUMMARY_MD = OUT / "summary.md"
TODO_MD = ROOT / "docs" / "SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md"


def newest_per_workflow(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Keep one newest row per workflow; GitHub API order is not assumed."""
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


def workflow_todo(row: Dict[str, Any]) -> str:
    if row.get("workflow") == "GITHUB_API":
        return str(row.get("todo") or "GitHub API workflow query blocked")
    return (
        f"Fix latest GitHub workflow '{row.get('workflow')}' run={row.get('run_id')} "
        f"conclusion={row.get('conclusion')} commit={str(row.get('commit') or '')[:12]}"
    )


def render_todo(row: Dict[str, Any]) -> str:
    return (
        f"Fix Render endpoint {row.get('endpoint')}: "
        f"{row.get('reason')} status={row.get('status_code')}"
    )


def main() -> int:
    if not SUMMARY_JSON.exists():
        raise SystemExit("tracker summary missing; fail-closed fallback must create it first")

    data = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    failed = newest_per_workflow(list(data.get("failed_workflows") or []))
    render = list(data.get("render_failures") or [])
    todo = [workflow_todo(row) for row in failed] + [render_todo(row) for row in render]

    data["failed_workflows"] = failed
    data["github_failed_count"] = len(failed)
    data["render_failed_count"] = len(render)
    data["todo"] = todo
    data["todo_count"] = len(todo)
    data["status"] = "PASS" if not todo else "BLOCKED"
    data["workflow_failure_count_semantics"] = "latest_failed_run_per_workflow"
    data["historical_duplicate_failures_removed"] = True
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
        f"GitHub workflows with a latest failed run: `{len(failed)}`",
        f"Render failed endpoints: `{len(render)}`",
        f"TODO count: `{len(todo)}`",
        "",
        "## Rule",
        "",
        "Only the newest failed/cancelled run per workflow is listed. Historical duplicate runs are excluded. Dashboard visual proof is still required for final claims.",
        "",
        "## TODO",
        "",
    ]
    lines += [f"- [ ] {item}" for item in todo] or ["- [x] No GitHub/Render failures detected in this run."]
    lines += ["", "## Latest failed run per workflow", ""]
    if failed:
        lines += ["| Workflow | Run | Conclusion | Commit | Updated | Link |", "|---|---:|---|---|---|---|"]
        for row in failed:
            lines.append(
                f"| {row.get('workflow')} | {row.get('run_id') or '-'} | {row.get('conclusion')} | "
                f"`{str(row.get('commit') or '')[:12]}` | {row.get('updated_at') or '-'} | {row.get('html_url') or '-'} |"
            )
    else:
        lines.append("No latest workflow failures found after tracker exclusions.")

    lines += ["", "## Render endpoint failures", ""]
    if render:
        lines += ["| Endpoint | Status | Reason | Classification |", "|---|---:|---|---|"]
        for row in render:
            flags = row.get("classification") or {}
            active = ", ".join(sorted(key for key, value in flags.items() if value)) or "none"
            lines.append(
                f"| `{row.get('endpoint')}` | {row.get('status_code')} | {row.get('reason')} | `{active}` |"
            )
    else:
        lines.append("No Render endpoint failures found in this run.")

    markdown = "\n".join(lines) + "\n"
    SUMMARY_MD.write_text(markdown, encoding="utf-8")
    TODO_MD.write_text(markdown, encoding="utf-8")
    print(json.dumps({
        "status": data["status"],
        "github_failed_count": len(failed),
        "render_failed_count": len(render),
        "todo_count": len(todo),
        "historical_duplicate_failures_removed": True,
        "live_trading_enabled": False,
        "order_routes_called": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
