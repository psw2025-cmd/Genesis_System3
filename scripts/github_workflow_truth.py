#!/usr/bin/env python3
"""Generate one exact-main GitHub Actions/workflow truth report.

The report is intentionally evidence-first: it resolves the current branch SHA at
runtime, inventories every active workflow, records each workflow's latest run,
collects jobs/artifacts for that run, and separately gates a small mandatory set
against the exact current SHA. Historical failures are retained as context but
cannot masquerade as current-main blockers.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MANDATORY = (
    "Genesis System3 Global Safety CI",
    "GCP Stage 2 Safety Checks",
    "GCP Dhan Token Fix CI",
    "Security Audit Evidence",
    "Cloud Run Auto Deploy",
    "Frontend Browser Runtime Smoke",
    "Full Cloud Audit and Forensic Consensus",
)
PASS_CONCLUSIONS = {"success", "neutral", "skipped"}


def _api_get(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "genesis-system3-workflow-truth",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _classify(run: dict[str, Any] | None, current_sha: str) -> str:
    if not run:
        return "MISSING"
    if str(run.get("head_sha") or "") != current_sha:
        return "STALE"
    if str(run.get("status") or "") != "completed":
        return "PENDING"
    conclusion = str(run.get("conclusion") or "").lower()
    return "PASS" if conclusion in PASS_CONCLUSIONS else "FAIL"


def _latest_run(api: str, repo: str, workflow_id: int, branch: str, token: str) -> dict[str, Any] | None:
    query = urllib.parse.urlencode({"branch": branch, "per_page": 1})
    payload = _api_get(f"{api}/repos/{repo}/actions/workflows/{workflow_id}/runs?{query}", token)
    runs = payload.get("workflow_runs") or []
    return runs[0] if runs else None


def _run_jobs(api: str, repo: str, run_id: int, token: str) -> list[dict[str, Any]]:
    payload = _api_get(f"{api}/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100", token)
    return [
        {
            "id": job.get("id"),
            "name": job.get("name"),
            "status": job.get("status"),
            "conclusion": job.get("conclusion"),
            "started_at": job.get("started_at"),
            "completed_at": job.get("completed_at"),
            "html_url": job.get("html_url"),
        }
        for job in (payload.get("jobs") or [])
    ]


def _run_artifacts(api: str, repo: str, run_id: int, token: str) -> list[dict[str, Any]]:
    payload = _api_get(f"{api}/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100", token)
    return [
        {
            "id": artifact.get("id"),
            "name": artifact.get("name"),
            "size_in_bytes": artifact.get("size_in_bytes"),
            "expired": artifact.get("expired"),
            "created_at": artifact.get("created_at"),
            "expires_at": artifact.get("expires_at"),
        }
        for artifact in (payload.get("artifacts") or [])
    ]


def _recent_issues(api: str, repo: str, token: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    payload = _api_get(
        f"{api}/repos/{repo}/issues?state=open&sort=updated&direction=desc&per_page=100",
        token,
    )
    issues: list[dict[str, Any]] = []
    prs: list[dict[str, Any]] = []
    for item in payload:
        row = {
            "number": item.get("number"),
            "title": item.get("title"),
            "updated_at": item.get("updated_at"),
            "html_url": item.get("html_url"),
            "labels": [label.get("name") for label in (item.get("labels") or [])],
        }
        (prs if item.get("pull_request") else issues).append(row)
    return issues, prs


def collect(repo: str, branch: str, token: str, mandatory: tuple[str, ...]) -> dict[str, Any]:
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    branch_payload = _api_get(f"{api}/repos/{repo}/branches/{urllib.parse.quote(branch, safe='')}", token)
    current_sha = str(((branch_payload.get("commit") or {}).get("sha")) or "")
    if not current_sha:
        raise RuntimeError(f"Unable to resolve {repo}:{branch}")

    workflows_payload = _api_get(f"{api}/repos/{repo}/actions/workflows?per_page=100", token)
    workflows: list[dict[str, Any]] = []
    mandatory_results: dict[str, str] = {}

    for wf in workflows_payload.get("workflows") or []:
        if wf.get("state") != "active":
            continue
        name = str(wf.get("name") or "")
        workflow_id = int(wf["id"])
        run = _latest_run(api, repo, workflow_id, branch, token)
        classification = _classify(run, current_sha)
        row: dict[str, Any] = {
            "id": workflow_id,
            "name": name,
            "path": wf.get("path"),
            "state": wf.get("state"),
            "mandatory": name in mandatory,
            "current_sha_classification": classification,
            "latest_run": None,
            "jobs": [],
            "artifacts": [],
        }
        if run:
            row["latest_run"] = {
                "id": run.get("id"),
                "run_number": run.get("run_number"),
                "run_attempt": run.get("run_attempt"),
                "event": run.get("event"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "head_sha": run.get("head_sha"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
                "html_url": run.get("html_url"),
            }
            run_id = int(run["id"])
            row["jobs"] = _run_jobs(api, repo, run_id, token)
            row["artifacts"] = _run_artifacts(api, repo, run_id, token)
        workflows.append(row)
        if name in mandatory:
            mandatory_results[name] = classification

    for name in mandatory:
        mandatory_results.setdefault(name, "MISSING")

    blockers = [
        {"workflow": name, "state": state}
        for name, state in mandatory_results.items()
        if state != "PASS"
    ]
    issues, prs = _recent_issues(api, repo, token)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repo,
        "branch": branch,
        "current_sha": current_sha,
        "gate_state": "PASS" if not blockers else "FAIL",
        "mandatory_workflows": list(mandatory),
        "mandatory_results": mandatory_results,
        "blockers": blockers,
        "active_workflow_count": len(workflows),
        "workflows": workflows,
        "open_issues": issues,
        "open_pull_requests": prs,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Genesis System3 Workflow Truth",
        "",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Repository: `{report['repository']}`",
        f"- Branch: `{report['branch']}`",
        f"- Exact current SHA: `{report['current_sha']}`",
        f"- Mandatory gate: **{report['gate_state']}**",
        f"- Active workflows inventoried: **{report['active_workflow_count']}**",
        "",
        "## Mandatory exact-SHA gate",
        "",
        "| Workflow | State |",
        "|---|---|",
    ]
    for name, state in report["mandatory_results"].items():
        lines.append(f"| {name} | **{state}** |")
    lines.extend(["", "## Active workflow inventory", "", "| Workflow | Latest SHA | Status | Conclusion | Exact-SHA class | Artifacts |", "|---|---|---|---|---|---|"])
    for wf in report["workflows"]:
        run = wf.get("latest_run") or {}
        artifacts = ", ".join(a["name"] for a in wf.get("artifacts") or []) or "-"
        lines.append(
            f"| {wf['name']} | `{str(run.get('head_sha') or '-')[:12]}` | {run.get('status') or '-'} | "
            f"{run.get('conclusion') or '-'} | **{wf['current_sha_classification']}** | {artifacts} |"
        )
    lines.extend(["", "## Current blockers", ""])
    if report["blockers"]:
        for blocker in report["blockers"]:
            lines.append(f"- **{blocker['workflow']}**: {blocker['state']}")
    else:
        lines.append("- None.")
    lines.extend(["", "## Recently updated open issues", ""])
    for item in report["open_issues"][:25]:
        lines.append(f"- #{item['number']} {item['title']} — updated `{item['updated_at']}`")
    lines.extend(["", "## Open pull requests", ""])
    for item in report["open_pull_requests"][:25]:
        lines.append(f"- #{item['number']} {item['title']} — updated `{item['updated_at']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", "psw2025-cmd/Genesis_System3"))
    parser.add_argument("--branch", default=os.getenv("SYSTEM3_AUTHORITY_BRANCH", "main"))
    parser.add_argument("--output-dir", default="reports/latest/workflow_control")
    parser.add_argument("--fail-on-mandatory", action="store_true")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if not token:
        print("GITHUB_TOKEN is required", file=sys.stderr)
        return 2

    mandatory_env = os.getenv("SYSTEM3_MANDATORY_WORKFLOWS", "").strip()
    mandatory = tuple(x.strip() for x in mandatory_env.split("|") if x.strip()) or DEFAULT_MANDATORY
    report = collect(args.repo, args.branch, token, mandatory)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "workflow_truth.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "workflow_truth.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"current_sha": report["current_sha"], "gate_state": report["gate_state"], "blockers": report["blockers"]}))
    return 1 if args.fail_on_mandatory and report["gate_state"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
