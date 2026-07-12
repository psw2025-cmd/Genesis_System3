#!/usr/bin/env python3
"""
System3 Workflow Failure Tracker

Tracks failed GitHub Actions workflows into a persistent Markdown/JSON TODO list.
Runs inside GitHub Actions with GITHUB_TOKEN. Does not use broker secrets.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "workflow_failure_tracker"
TODO_MD = ROOT / "docs" / "SYSTEM3_WORKFLOW_FAILURE_TODO.md"

BAD_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required"}


def api_get(url: str, token: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "system3-workflow-failure-tracker",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    repo = os.environ.get("GITHUB_REPOSITORY", "psw2025-cmd/Genesis_System3")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    OUT.mkdir(parents=True, exist_ok=True)

    payload: Dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "status": "UNKNOWN",
        "failed_count": 0,
        "failed_runs": [],
        "todo": [],
        "note": "Workflow failure tracker. Failed workflows remain TODO until a later successful run is proven.",
    }

    if not token:
        payload["status"] = "BLOCKED"
        payload["todo"].append("GITHUB_TOKEN unavailable; cannot query workflow failures.")
    else:
        url = f"https://api.github.com/repos/{repo}/actions/runs?per_page=50"
        try:
            data = api_get(url, token)
            failed = []
            for run in data.get("workflow_runs", []):
                conclusion = run.get("conclusion")
                if run.get("status") == "completed" and conclusion in BAD_CONCLUSIONS:
                    failed.append(
                        {
                            "run_id": run.get("id"),
                            "workflow": run.get("name"),
                            "conclusion": conclusion,
                            "branch": run.get("head_branch"),
                            "commit": run.get("head_sha"),
                            "created_at": run.get("created_at"),
                            "updated_at": run.get("updated_at"),
                            "html_url": run.get("html_url"),
                        }
                    )
            payload["failed_runs"] = failed
            payload["failed_count"] = len(failed)
            payload["status"] = "PASS" if not failed else "BLOCKED"
            for r in failed:
                payload["todo"].append(
                    f"Fix workflow '{r.get('workflow')}' run {r.get('run_id')} conclusion={r.get('conclusion')} commit={r.get('commit')}"
                )
        except urllib.error.HTTPError as e:
            payload["status"] = "BLOCKED"
            payload["todo"].append(f"GitHub API HTTP error while reading workflow runs: {e.code}")
        except Exception as e:
            payload["status"] = "BLOCKED"
            payload["todo"].append(f"Workflow tracker exception: {type(e).__name__}: {str(e)[:200]}")

    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# System3 Workflow Failure TODO",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Repository: `{payload['repository']}`",
        f"Status: **{payload['status']}**",
        f"Failed workflow count: `{payload['failed_count']}`",
        "",
        "## Rule",
        "",
        "Any failed workflow is a TODO item until a later successful run proves it is fixed.",
        "Do not claim resolved unless workflow status, Render verification, integration verification, and dashboard visual proof are current.",
        "",
        "## Failed workflow TODO list",
        "",
    ]
    if payload["todo"]:
        lines.extend([f"- [ ] {x}" for x in payload["todo"]])
    else:
        lines.append("- [x] No failed workflows found in latest queried runs.")
    lines.extend(["", "## Failed run details", ""])
    if payload["failed_runs"]:
        lines.append("| Workflow | Run ID | Conclusion | Commit | Updated | Link |")
        lines.append("|---|---:|---|---|---|---|")
        for r in payload["failed_runs"]:
            commit = str(r.get("commit") or "")[:12]
            lines.append(
                f"| {r.get('workflow')} | {r.get('run_id')} | {r.get('conclusion')} | `{commit}` | {r.get('updated_at')} | {r.get('html_url')} |"
            )
    else:
        lines.append("No failed run details in latest query.")
    TODO_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
