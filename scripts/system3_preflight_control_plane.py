#!/usr/bin/env python3
"""Genesis System3 permanent GitHub preflight control plane.

Build one bounded CURRENT snapshot before production-relevant work proceeds.
It inventories remote main, every configured workflow's latest run, active and
current-relevant failed runs, artifact/failing-job metadata, open PRs, recently
updated open issues, and the newest Issue #188 coordination markers.

Generated files are snapshots, never permanent live truth. Re-run this script
before each production-relevant transition.

Outputs:
  reports/latest/control_plane/workflow_issue_artifact_snapshot.json
  reports/latest/control_plane/NEXT_ACTION.md

Safety: GitHub read-only API only. Never emits GITHUB_TOKEN. No GCP, broker,
secret, LIVE, IAM, deploy, or order mutation.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "psw2025-cmd/Genesis_System3"
DEFAULT_ISSUE = 188
OUT_DIR = ROOT / "reports" / "latest" / "control_plane"
MARKERS = (
    "SYSTEM3_COORDINATION_V1",
    "SYSTEM3_URL_SINGLE_TRUTH_V1",
    "SYSTEM3_AUTONOMOUS_COORDINATION_V1",
)
ACTIVE_STATES = {"queued", "in_progress", "waiting", "pending", "requested"}
FAIL_CONCLUSIONS = {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}


@dataclass(frozen=True)
class Decision:
    status: str
    current_step: str
    next_action: str
    reason: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _token() -> str:
    return os.getenv("GITHUB_TOKEN", "").strip() or os.getenv("GH_TOKEN", "").strip()


def api_get(repo: str, path: str, *, params: dict[str, Any] | None = None) -> Any:
    query = "?" + urllib.parse.urlencode(params) if params else ""
    url = f"https://api.github.com/repos/{repo}/{path.lstrip('/')}" + query
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Genesis-System3-preflight-control-plane/1.1",
    }
    token = _token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"GitHub API HTTP {exc.code} for {path}: {body}") from exc


def api_get_pages(repo: str, path: str, *, params: dict[str, Any] | None = None, max_pages: int = 10) -> list[Any]:
    base = dict(params or {})
    base["per_page"] = 100
    result: list[Any] = []
    for page in range(1, max_pages + 1):
        base["page"] = page
        payload = api_get(repo, path, params=base)
        if not isinstance(payload, list):
            raise RuntimeError(f"Expected list payload for paged endpoint {path}")
        result.extend(payload)
        if len(payload) < 100:
            break
    return result


def _compact_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run.get("id"),
        "name": run.get("name"),
        "workflow_id": run.get("workflow_id"),
        "run_number": run.get("run_number"),
        "event": run.get("event"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "html_url": run.get("html_url"),
    }


def _artifact_meta(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "size_in_bytes": item.get("size_in_bytes"),
            "expired": item.get("expired"),
            "created_at": item.get("created_at"),
            "expires_at": item.get("expires_at"),
        }
        for item in (payload.get("artifacts") or [])
    ]


def _failed_jobs(repo: str, run_id: int | None) -> list[dict[str, Any]]:
    if not run_id:
        return []
    payload = api_get(repo, f"actions/runs/{run_id}/jobs", params={"per_page": 100})
    failures = []
    for job in payload.get("jobs") or []:
        if job.get("conclusion") not in FAIL_CONCLUSIONS:
            continue
        failed_steps = [
            {
                "number": step.get("number"),
                "name": step.get("name"),
                "status": step.get("status"),
                "conclusion": step.get("conclusion"),
            }
            for step in (job.get("steps") or [])
            if step.get("conclusion") in FAIL_CONCLUSIONS
        ]
        failures.append(
            {
                "id": job.get("id"),
                "name": job.get("name"),
                "conclusion": job.get("conclusion"),
                "started_at": job.get("started_at"),
                "completed_at": job.get("completed_at"),
                "failed_steps": failed_steps,
            }
        )
    return failures


def classify_failure_relevance(run: dict[str, Any], *, main_sha: str, active_pr_shas: set[str]) -> bool:
    """Current-main/active-PR failures block; unrelated old failures stay history."""
    if run.get("conclusion") not in FAIL_CONCLUSIONS:
        return False
    sha = str(run.get("head_sha") or "")
    return bool(sha and (sha == main_sha or sha in active_pr_shas))


def choose_next_action(*, main_sha: str, workflows: list[dict[str, Any]], active_prs: list[dict[str, Any]]) -> Decision:
    active = [r for r in workflows if r.get("status") in ACTIVE_STATES]
    deploy = next(
        (
            r
            for r in active
            if r.get("name") == "Cloud Run Auto Deploy" and r.get("head_sha") == main_sha
        ),
        None,
    )
    if deploy:
        return Decision(
            "WAITING",
            "canonical production deployment",
            "recheck deploy completion; then verify exact-serving SHA and run fresh URL proof",
            f"Cloud Run Auto Deploy #{deploy.get('run_number')} is {deploy.get('status')}",
        )

    current_failures = [r for r in workflows if r.get("relevant_failure")]
    if current_failures:
        names = ", ".join(str(r.get("name")) for r in current_failures[:3])
        return Decision(
            "WORKING",
            "current workflow failure investigation",
            "inspect failed job/step/log/artifact and remediate before proceeding",
            f"current dependency failure(s): {names}",
        )

    mergeable = [p for p in active_prs if p.get("mergeable") is True and not p.get("draft")]
    if mergeable:
        return Decision(
            "WORKING",
            "active PR gate verification",
            "verify exact-head mandatory gates; merge immediately when green",
            f"{len(mergeable)} mergeable active PR(s)",
        )

    if active:
        names = ", ".join(str(r.get("name")) for r in active[:3])
        return Decision(
            "WAITING",
            "GitHub workflow completion",
            "recheck active workflow state, then continue automatically",
            f"active workflow(s): {names}",
        )

    return Decision(
        "WORKING",
        "production truth verification",
        "verify exact serving SHA and run fresh semantic production URL proof before any PASS claim",
        "no blocking current workflow dependency detected",
    )


def _open_prs(repo: str) -> tuple[list[dict[str, Any]], set[str]]:
    summaries = api_get_pages(repo, "pulls", params={"state": "open"}, max_pages=3)
    active_prs: list[dict[str, Any]] = []
    shas: set[str] = set()
    for summary in summaries:
        number = int(summary.get("number") or 0)
        detail = api_get(repo, f"pulls/{number}") if number else summary
        head_sha = str(((detail.get("head") or {}).get("sha")) or "")
        if head_sha:
            shas.add(head_sha)
        active_prs.append(
            {
                "number": number,
                "title": detail.get("title"),
                "draft": detail.get("draft"),
                "mergeable": detail.get("mergeable"),
                "mergeable_state": detail.get("mergeable_state"),
                "head_sha": head_sha,
                "base_sha": ((detail.get("base") or {}).get("sha")),
                "updated_at": detail.get("updated_at"),
                "html_url": detail.get("html_url"),
            }
        )
    return active_prs, shas


def _recent_open_issues(repo: str) -> list[dict[str, Any]]:
    payload = api_get(repo, "issues", params={"state": "open", "sort": "updated", "direction": "desc", "per_page": 30})
    return [
        {
            "number": item.get("number"),
            "title": item.get("title"),
            "updated_at": item.get("updated_at"),
            "labels": [label.get("name") for label in (item.get("labels") or [])],
            "html_url": item.get("html_url"),
        }
        for item in payload
        if not item.get("pull_request")
    ]


def _coordination(repo: str, issue_number: int) -> tuple[dict[str, Any], dict[str, dict[str, Any] | None]]:
    issue = api_get(repo, f"issues/{issue_number}")
    comments = api_get_pages(repo, f"issues/{issue_number}/comments", max_pages=10)
    newest: dict[str, dict[str, Any] | None] = {marker: None for marker in MARKERS}
    for comment in reversed(comments):
        body = str(comment.get("body") or "")
        for marker in MARKERS:
            if newest[marker] is None and marker in body:
                newest[marker] = {
                    "comment_id": comment.get("id"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                    "html_url": comment.get("html_url"),
                    "excerpt": body[:1000],
                }
        if all(newest.values()):
            break
    return (
        {
            "number": issue.get("number"),
            "state": issue.get("state"),
            "title": issue.get("title"),
            "updated_at": issue.get("updated_at"),
            "html_url": issue.get("html_url"),
        },
        newest,
    )


def build_snapshot(repo: str, issue_number: int) -> dict[str, Any]:
    main = api_get(repo, "commits/main")
    main_sha = str(main.get("sha") or "")
    active_prs, active_pr_shas = _open_prs(repo)

    workflow_defs = (api_get(repo, "actions/workflows", params={"per_page": 100}).get("workflows") or [])
    recent_runs = (api_get(repo, "actions/runs", params={"per_page": 100}).get("workflow_runs") or [])

    workflow_inventory = []
    actionable_by_id: dict[int, dict[str, Any]] = {}

    # Every configured workflow gets an independently queried latest run, so a
    # low-frequency workflow cannot disappear merely because 100 newer runs exist.
    for workflow in workflow_defs:
        wid = int(workflow.get("id") or 0)
        latest_payload = api_get(repo, f"actions/workflows/{wid}/runs", params={"per_page": 1}) if wid else {}
        latest_raw = (latest_payload.get("workflow_runs") or [None])[0]
        latest = _compact_run(latest_raw) if latest_raw else None
        if latest_raw:
            latest["relevant_failure"] = classify_failure_relevance(
                latest_raw, main_sha=main_sha, active_pr_shas=active_pr_shas
            )
            try:
                latest["artifacts"] = _artifact_meta(
                    api_get(repo, f"actions/runs/{latest_raw.get('id')}/artifacts", params={"per_page": 100})
                )
            except Exception as exc:
                latest["artifact_query_error"] = type(exc).__name__
            if latest_raw.get("status") != "completed" or latest["relevant_failure"]:
                if latest_raw.get("conclusion") in FAIL_CONCLUSIONS:
                    latest["failed_jobs"] = _failed_jobs(repo, latest_raw.get("id"))
                actionable_by_id[int(latest_raw.get("id") or 0)] = latest
        workflow_inventory.append(
            {
                "id": wid,
                "name": workflow.get("name"),
                "path": workflow.get("path"),
                "state": workflow.get("state"),
                "latest_run": latest,
            }
        )

    # Also catch active/current-relevant runs that are not the latest run of a workflow.
    for raw in recent_runs:
        relevant_failure = classify_failure_relevance(raw, main_sha=main_sha, active_pr_shas=active_pr_shas)
        if raw.get("status") == "completed" and not relevant_failure:
            continue
        rid = int(raw.get("id") or 0)
        if rid in actionable_by_id:
            continue
        compact = _compact_run(raw)
        compact["relevant_failure"] = relevant_failure
        try:
            compact["artifacts"] = _artifact_meta(api_get(repo, f"actions/runs/{rid}/artifacts", params={"per_page": 100}))
        except Exception as exc:
            compact["artifact_query_error"] = type(exc).__name__
        if raw.get("conclusion") in FAIL_CONCLUSIONS:
            compact["failed_jobs"] = _failed_jobs(repo, rid)
        actionable_by_id[rid] = compact

    actionable_runs = sorted(
        actionable_by_id.values(), key=lambda x: str(x.get("created_at") or ""), reverse=True
    )
    issue_188, newest_markers = _coordination(repo, issue_number)
    recent_issues = _recent_open_issues(repo)
    decision = choose_next_action(main_sha=main_sha, workflows=actionable_runs, active_prs=active_prs)

    return {
        "schema": "SYSTEM3_PREFLIGHT_CONTROL_PLANE_V1",
        "captured_at_utc": utc_now(),
        "repository": repo,
        "main_sha": main_sha,
        "issue_188": issue_188,
        "status": decision.status,
        "current_step": decision.current_step,
        "next_action": decision.next_action,
        "reason": decision.reason,
        "workflow_count": len(workflow_defs),
        "workflow_inventory": workflow_inventory,
        "actionable_runs": actionable_runs,
        "open_pull_requests": active_prs,
        "recent_open_issues": recent_issues,
        "coordination_markers": newest_markers,
        "policy": {
            "historical_failures": "context_only_unless_current_main_or_active_pr_dependency",
            "before_proceed": "rerun_this_snapshot_and_revalidate_live_critical_claims",
            "green_ci": "merge_when_exact_head_mandatory_gates_green",
            "merged": "check_canonical_deploy",
            "deployed": "verify_exact_serving_sha_then_new_url_proof",
            "url_fail": "investigate_and_open_next_remediation_immediately",
            "stop_only_for": "real_external_dependency_or_genuine_user_approval",
        },
    }


def write_snapshot(snapshot: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "workflow_issue_artifact_snapshot.json"
    md_path = out_dir / "NEXT_ACTION.md"
    json_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
    md = (
        "# System3 Preflight Control Plane\n\n"
        f"Captured: `{snapshot['captured_at_utc']}`\n\n"
        f"Main: `{snapshot['main_sha']}`\n\n"
        f"STATUS: **{snapshot['status']}**\n\n"
        f"CURRENT STEP: {snapshot['current_step']}\n\n"
        f"NEXT ACTION: {snapshot['next_action']}\n\n"
        f"REASON: {snapshot['reason']}\n\n"
        "> Generated snapshot only. Re-run before every production-relevant transition; never use this stored file as live truth.\n"
    )
    md_path.write_text(md, encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Genesis System3 workflow/issue/artifact preflight")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--issue", type=int, default=DEFAULT_ISSUE)
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()

    snapshot = build_snapshot(args.repo, args.issue)
    json_path, md_path = write_snapshot(snapshot, Path(args.out_dir))
    print(f"STATUS={snapshot['status']}")
    print(f"CURRENT_STEP={snapshot['current_step']}")
    print(f"NEXT_ACTION={snapshot['next_action']}")
    print(f"SNAPSHOT={json_path}")
    print(f"NEXT_ACTION_FILE={md_path}")
    if args.print_json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
