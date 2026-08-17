#!/usr/bin/env python3
"""Build a read-only, current-SHA-aware GitHub workflow control-plane inventory.

The report is metadata-only. It never reads secret values, never mutates GitHub,
and separates current-main failures from superseded history.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

OUT_DIR = Path("reports/latest/workflow_control_plane")
TERMINAL_FAILURES = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}


def is_terminal_failure(conclusion: Any) -> bool:
    return str(conclusion or "").strip().lower() in TERMINAL_FAILURES


def run_scope(run: dict[str, Any], current_main_sha: str) -> str:
    return "CURRENT_MAIN" if str(run.get("head_sha") or "") == current_main_sha else "SUPERSEDED"


def summarize_failed_steps(jobs_payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for job in jobs_payload.get("jobs") or []:
        failed_steps = [
            {"name": str(step.get("name") or ""), "number": step.get("number"), "conclusion": step.get("conclusion")}
            for step in job.get("steps") or []
            if is_terminal_failure(step.get("conclusion"))
        ]
        if is_terminal_failure(job.get("conclusion")) or failed_steps:
            out.append({
                "job_id": job.get("id"),
                "job_name": str(job.get("name") or ""),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "failed_steps": failed_steps,
            })
    return out


def _safe_url(url: Any) -> str | None:
    text = str(url or "").strip()
    return text if text.startswith("https://github.com/") else None


def _safe_run(run: dict[str, Any], current_main_sha: str) -> dict[str, Any]:
    return {
        "id": run.get("id"), "name": str(run.get("name") or ""), "workflow_id": run.get("workflow_id"),
        "run_number": run.get("run_number"), "run_attempt": run.get("run_attempt"), "event": run.get("event"),
        "status": run.get("status"), "conclusion": run.get("conclusion"), "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"), "scope": run_scope(run, current_main_sha), "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"), "run_started_at": run.get("run_started_at"),
        "html_url": _safe_url(run.get("html_url")),
    }


def _safe_artifact(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": artifact.get("id"), "name": str(artifact.get("name") or ""),
        "size_in_bytes": artifact.get("size_in_bytes"), "expired": bool(artifact.get("expired")),
        "created_at": artifact.get("created_at"), "updated_at": artifact.get("updated_at"),
        "expires_at": artifact.get("expires_at"), "digest": artifact.get("digest"),
    }


def _safe_issue(item: dict[str, Any]) -> dict[str, Any]:
    labels = [str((x or {}).get("name") or "") for x in item.get("labels") or [] if isinstance(x, dict)]
    return {
        "number": item.get("number"), "kind": "pull_request" if item.get("pull_request") else "issue",
        "title": str(item.get("title") or ""), "state": item.get("state"),
        "labels": sorted(x for x in labels if x), "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"), "html_url": _safe_url(item.get("html_url")),
    }


class GitHubReadOnly:
    def __init__(self, token: str, repository: str, api_url: str) -> None:
        self.token = token
        self.repository = repository
        self.api_url = api_url.rstrip("/")

    def get(self, path: str) -> dict[str, Any] | list[Any]:
        req = urllib.request.Request(
            f"{self.api_url}{path}",
            headers={
                "Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "genesis-system3-workflow-control-plane",
            }, method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:400]
            raise RuntimeError(f"github_read_failed status={exc.code} path={path} body={body!r}") from exc


def _iso_to_dt(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_inventory(client: GitHubReadOnly, repository: str) -> dict[str, Any]:
    owner, repo = repository.split("/", 1)
    branch = client.get(f"/repos/{owner}/{repo}/branches/main")
    if not isinstance(branch, dict):
        raise RuntimeError("main_branch_payload_invalid")
    current_main_sha = str(((branch.get("commit") or {}).get("sha") or "")).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", current_main_sha):
        raise RuntimeError("current_main_sha_unresolved")

    workflows_payload = client.get(f"/repos/{owner}/{repo}/actions/workflows?per_page=100")
    runs_payload = client.get(f"/repos/{owner}/{repo}/actions/runs?branch=main&per_page=100")
    issues_payload = client.get(f"/repos/{owner}/{repo}/issues?state=open&sort=updated&direction=desc&per_page=100")
    if not isinstance(workflows_payload, dict) or not isinstance(runs_payload, dict):
        raise RuntimeError("workflow_payload_invalid")

    workflows = workflows_payload.get("workflows") or []
    raw_runs = runs_payload.get("workflow_runs") or []
    safe_runs = [_safe_run(run, current_main_sha) for run in raw_runs]
    latest_by_workflow: dict[int, dict[str, Any]] = {}
    for run in safe_runs:
        workflow_id = run.get("workflow_id")
        if isinstance(workflow_id, int) and workflow_id not in latest_by_workflow:
            latest_by_workflow[workflow_id] = run

    workflow_inventory = []
    for workflow in workflows:
        wid = workflow.get("id")
        workflow_inventory.append({
            "id": wid, "name": str(workflow.get("name") or ""), "path": str(workflow.get("path") or ""),
            "state": workflow.get("state"), "html_url": _safe_url(workflow.get("html_url")),
            "latest_main_run": latest_by_workflow.get(wid),
        })
    workflow_inventory.sort(key=lambda x: (x["name"].lower(), x["path"]))

    current_runs = [run for run in safe_runs if run["scope"] == "CURRENT_MAIN"]
    current_failures = [run for run in current_runs if is_terminal_failure(run.get("conclusion"))]
    active_runs = [run for run in safe_runs if str(run.get("status") or "").lower() != "completed"]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    recent_failures = [
        safe for raw, safe in zip(raw_runs, safe_runs)
        if (_iso_to_dt(raw.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff
        and is_terminal_failure(raw.get("conclusion"))
    ]

    run_evidence = []
    for run in current_runs[:30]:
        run_id = run.get("id")
        if not isinstance(run_id, int):
            continue
        jobs_payload = client.get(f"/repos/{owner}/{repo}/actions/runs/{run_id}/jobs?per_page=100")
        artifacts_payload = client.get(f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts?per_page=100")
        if not isinstance(jobs_payload, dict) or not isinstance(artifacts_payload, dict):
            raise RuntimeError(f"run_evidence_payload_invalid run_id={run_id}")
        run_evidence.append({
            "run": run, "failed_jobs": summarize_failed_steps(jobs_payload),
            "artifacts": [_safe_artifact(a) for a in artifacts_payload.get("artifacts") or []],
        })

    open_items = [_safe_issue(item) for item in issues_payload] if isinstance(issues_payload, list) else []
    report = {
        "schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": repository, "source_authority": "github-api-read-only", "current_main_sha": current_main_sha,
        "workflow_count": len(workflow_inventory), "workflows": workflow_inventory, "current_main_runs": current_runs,
        "current_main_failures": current_failures, "active_runs": active_runs, "recent_48h_failures": recent_failures,
        "current_main_run_evidence": run_evidence, "open_issues_and_prs": open_items,
        "counts": {
            "current_main_runs": len(current_runs), "current_main_failures": len(current_failures),
            "active_runs": len(active_runs), "recent_48h_failures": len(recent_failures),
            "open_issues": sum(1 for x in open_items if x["kind"] == "issue"),
            "open_prs": sum(1 for x in open_items if x["kind"] == "pull_request"),
            "current_main_artifacts": sum(len(x["artifacts"]) for x in run_evidence),
        },
        "safety": {"github_write_performed": False, "runtime_mutation_performed": False,
                   "secret_values_accessed": False, "order_action_performed": False, "live_trading_enabled": False},
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# System3 Workflow Control Plane", "", f"- Generated UTC: `{report['generated_at_utc']}`",
        f"- Current main SHA: `{report['current_main_sha']}`", f"- Workflows inventoried: **{report['workflow_count']}**",
        f"- Current-main workflow runs: **{counts['current_main_runs']}**",
        f"- Current-main failures: **{counts['current_main_failures']}**", f"- Active runs: **{counts['active_runs']}**",
        f"- Failures seen in last 48h: **{counts['recent_48h_failures']}**",
        f"- Current-main artifacts indexed: **{counts['current_main_artifacts']}**",
        f"- Open issues / PRs: **{counts['open_issues']} / {counts['open_prs']}**", "", "## Current-main failures",
    ]
    failures = report.get("current_main_failures") or []
    if not failures:
        lines.append("- None")
    else:
        for run in failures:
            lines.append(f"- `{run['name']}` run `{run['id']}` — **{run['conclusion']}** — {run.get('html_url') or 'no-url'}")
    lines += ["", "## Active runs"]
    active = report.get("active_runs") or []
    if not active:
        lines.append("- None")
    else:
        for run in active:
            lines.append(f"- `{run['name']}` run `{run['id']}` — `{run['status']}` — `{run['scope']}`")
    lines += ["", "## Safety", "- Read-only GitHub API inventory: **true**", "- GitHub/runtime mutation performed: **false**",
              "- Secret values accessed: **false**", "- Order actions performed: **false**", "- LIVE trading enabled: **false**", ""]
    return "\n".join(lines)


def _self_test() -> int:
    assert is_terminal_failure("failure") and not is_terminal_failure("success")
    sha = "a" * 40
    assert run_scope({"head_sha": sha}, sha) == "CURRENT_MAIN"
    assert run_scope({"head_sha": "b" * 40}, sha) == "SUPERSEDED"
    jobs = {"jobs": [{"id": 1, "name": "x", "status": "completed", "conclusion": "failure",
                       "steps": [{"name": "bad", "number": 2, "conclusion": "failure"}]}]}
    assert summarize_failed_steps(jobs)[0]["failed_steps"][0]["name"] == "bad"
    print("WORKFLOW_CONTROL_PLANE_SELF_TEST=PASS")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return _self_test()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com").strip()
    if not token or not repository or "/" not in repository:
        raise SystemExit("WORKFLOW_CONTROL_PLANE_CONFIG_MISSING")
    report = build_inventory(GitHubReadOnly(token, repository, api_url), repository)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "workflow_inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    markdown = render_markdown(report)
    (OUT_DIR / "workflow_inventory.md").write_text(markdown, encoding="utf-8")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(markdown + "\n")
    print("WORKFLOW_CONTROL_PLANE=PASS", json.dumps({"current_main_sha": report["current_main_sha"],
          "workflow_count": report["workflow_count"], "counts": report["counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
