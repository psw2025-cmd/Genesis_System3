#!/usr/bin/env python3
"""Genesis System3 permanent GitHub preflight control plane.

Purpose
-------
Build one bounded, current snapshot before production-relevant work proceeds.
The snapshot inventories current remote main, every configured workflow's latest
run, active/relevant failed runs, artifact metadata, open pull requests, and
Issue #188 coordination markers. Historical failures remain history unless they
are still relevant to current main/active PR/deployment dependencies.

Outputs
-------
reports/latest/control_plane/workflow_issue_artifact_snapshot.json
reports/latest/control_plane/NEXT_ACTION.md

Safety
------
Read-only GitHub API calls only. Never prints or writes GITHUB_TOKEN. No GCP,
secret, broker, LIVE, or order mutations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
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
MARKERS = ("SYSTEM3_COORDINATION_V1", "SYSTEM3_URL_SINGLE_TRUTH_V1", "SYSTEM3_AUTONOMOUS_COORDINATION_V1")


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
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    url = f"https://api.github.com/repos/{repo}/{path.lstrip('/')}" + query
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Genesis-System3-preflight-control-plane/1.0"}
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
    result = []
    for item in payload.get("artifacts") or []:
        result.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "size_in_bytes": item.get("size_in_bytes"),
            "expired": item.get("expired"),
            "created_at": item.get("created_at"),
            "expires_at": item.get("expires_at"),
        })
    return result


def classify_failure_relevance(run: dict[str, Any], *, main_sha: str, active_pr_shas: set[str]) -> bool:
    """Keep current failures actionable while leaving unrelated history historical."""
    if run.get("conclusion") not in {"failure", "cancelled", "timed_out", "action_required", "startup_failure"}:
        return False
    sha = str(run.get("head_sha") or "")
    return bool(sha and (sha == main_sha or sha in active_pr_shas))


def choose_next_action(*, main_sha: str, workflows: list[dict[str, Any]], active_prs: list[dict[str, Any]]) -> Decision:
    active = [r for r in workflows if r.get("status") in {"queued", "in_progress", "waiting", "pending", "requested"}]
    deploy = next((r for r in active if r.get("name") == "Cloud Run Auto Deploy" and r.get("head_sha") == main_sha), None)
    if deploy:
        return Decision("WAITING", "canonical production deployment", "recheck deploy completion; then verify exact-serving SHA and run fresh URL proof", f"Cloud Run Auto Deploy #{deploy.get('run_number')} is {deploy.get('status')}")

    current_failures = [r for r in workflows if r.get("relevant_failure")]
    if current_failures:
        names = ", ".join(str(r.get("name")) for r in current_failures[:3])
        return Decision("WORKING", "current workflow failure investigation", "inspect failed job/step/log/artifact and remediate before proceeding", f"current dependency failure(s): {names}")

    mergeable = [p for p in active_prs if p.get("mergeable") is True and not p.get("draft")]
    if mergeable:
        return Decision("WORKING", "active PR gate verification", "verify exact-head mandatory gates; merge immediately when green", f"{len(mergeable)} mergeable active PR(s)")

    if active:
        names = ", ".join(str(r.get("name")) for r in active[:3])
        return Decision("WAITING", "GitHub workflow completion", "recheck active workflow state, then continue automatically", f"active workflow(s): {names}")

    return Decision("WORKING", "production truth verification", "verify exact serving SHA and run fresh semantic production URL proof before any PASS claim", "no blocking current workflow dependency detected")


def build_snapshot(repo: str, issue_number: int) -> dict[str, Any]:
    main = api_get(repo, "commits/main")
    main_sha = str(main.get("sha") or "")

    workflows_payload = api_get(repo, "actions/workflows", params={"per_page": 100})
    workflow_defs = workflows_payload.get("workflows") or []

    prs = api_get(repo, "pulls", params={"state": "open", "per_page": 100})
    active_prs: list[dict[str, Any]] = []
    active_pr_shas: set[str] = set()
    for pr in prs:
        head_sha = str(((pr.get("head") or {}).get("sha")) or "")
        if head_sha:
            active_pr_shas.add(head_sha)
        active_prs.append({
            "number": pr.get("number"),
            "title": pr.get("title"),
            "draft": pr.get("draft"),
            "mergeable": pr.get("mergeable"),
            "head_sha": head_sha,
            "base_sha": ((pr.get("base") or {}).get("sha")),
            "updated_at": pr.get("updated_at"),
            "html_url": pr.get("html_url"),
        })

    runs_payload = api_get(repo, "actions/runs", params={"per_page": 100})
    runs = runs_payload.get("workflow_runs") or []
    by_workflow: dict[int, list[dict[str, Any]]] = {}
    for run in runs:
        wid = int(run.get("workflow_id") or 0)
        by_workflow.setdefault(wid, []).append(run)

    workflow_inventory = []
    actionable_runs: list[dict[str, Any]] = []
    for workflow in workflow_defs:
        wid = int(workflow.get("id") or 0)
        wruns = by_workflow.get(wid, [])
        latest = _compact_run(wruns[0]) if wruns else None
        workflow_inventory.append({
            "id": wid,
            "name": workflow.get("name"),
            "path": workflow.get("path"),
            "state": workflow.get("state"),
            "latest_run": latest,
        })
        for raw in wruns:
            compact = _compact_run(raw)
            relevant_failure = classify_failure_relevance(raw, main_sha=main_sha, active_pr_shas=active_pr_shas)
            compact["relevant_failure"] = relevant_failure
            if raw.get("status") != "completed" or relevant_failure:
                try:
                    artifacts = api_get(repo, f"actions/runs/{raw.get('id')}/artifacts", params={"per_page": 100})
                    compact["artifacts"] = _artifact_meta(artifacts)
                except Exception as exc:
                    compact["artifact_query_error"] = type(exc).__name__
                actionable_runs.append(compact)

    comments = api_get(repo, f"issues/{issue_number}/comments", params={"per_page": 100})
    newest_markers: dict[str, dict[str, Any] | None] = {marker: None for marker in MARKERS}
    for comment in reversed(comments):
        body = str(comment.get("body") or "")
        for marker in MARKERS:
            if newest_markers[marker] is None and marker in body:
                newest_markers[marker] = {
                    "comment_id": comment.get("id"),
                    "created_at": comment.get("created_at"),
                    "updated_at": comment.get("updated_at"),
                    "html_url": comment.get("html_url"),
                    "excerpt": body[:1000],
                }
        if all(newest_markers.values()):
            break

    decision_input = [dict(run) for run in actionable_runs]
    decision = choose_next_action(main_sha=main_sha, workflows=decision_input, active_prs=active_prs)

    return {
        "schema": "SYSTEM3_PREFLIGHT_CONTROL_PLANE_V1",
        "captured_at_utc": utc_now(),
        "repository": repo,
        "main_sha": main_sha,
        "issue_number": issue_number,
        "status": decision.status,
        "current_step": decision.current_step,
        "next_action": decision.next_action,
        "reason": decision.reason,
        "workflow_count": len(workflow_defs),
        "workflow_inventory": workflow_inventory,
        "actionable_runs": actionable_runs,
        "open_pull_requests": active_prs,
        "coordination_markers": newest_markers,
        "policy": {
            "historical_failures": "context_only_unless_current_main_or_active_pr_dependency",
            "before_proceed": "rerun_this_snapshot_and_revalidate_live_critical_claims",
            "green_ci": "merge_when_exact_head_mandatory_gates_green",
            "merged": "check_canonical_deploy",
            "deployed": "verify_exact_serving_sha_then_new_url_proof",
            "url_fail": "investigate_and_open_next_remediation_immediately",
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
        "> This file is a generated snapshot, not permanent live truth. Re-run the preflight before every production-relevant transition.\n"
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
