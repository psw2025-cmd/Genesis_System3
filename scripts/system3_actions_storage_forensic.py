#!/usr/bin/env python3
"""Exact-digest GitHub Actions storage forensic module for Genesis System3.

REPORT ONLY. This module inventories Actions artifacts/caches and identifies
redundant artifact candidates only when an identical GitHub artifact digest is
retained elsewhere. It never deletes artifacts/caches or mutates repository,
cloud, broker, IAM, LIVE, or order state.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "SYSTEM3_ACTIONS_STORAGE_FORENSIC_V1"
DEFAULT_MIN_AGE_DAYS = 7


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def human_bytes(value: int) -> str:
    n = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if n < 1024 or unit == "TiB":
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{value} B"


def github_get(url: str, token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def current_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, encoding="utf-8", stderr=subprocess.DEVNULL
        ).strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_main_authority() -> bool:
    return (
        os.environ.get("GITHUB_REF") == "refs/heads/main"
        and os.environ.get("GITHUB_EVENT_NAME") in {"push", "workflow_dispatch"}
    )


def artifact_row(raw: dict[str, Any]) -> dict[str, Any]:
    workflow = raw.get("workflow_run") or {}
    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "size_in_bytes": int(raw.get("size_in_bytes") or 0),
        "expired": bool(raw.get("expired")),
        "created_at": raw.get("created_at"),
        "expires_at": raw.get("expires_at"),
        "digest": raw.get("digest"),
        "workflow_run_id": workflow.get("id"),
        "head_branch": workflow.get("head_branch"),
        "head_sha": workflow.get("head_sha"),
    }


def classify_duplicate_groups(
    artifacts: list[dict[str, Any]],
    *,
    now: datetime,
    current_sha: str | None,
    main_authority: bool,
    min_age_days: int,
) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    digest_missing = 0
    for artifact in artifacts:
        digest = artifact.get("digest")
        name = str(artifact.get("name") or "")
        if not digest or not str(digest).startswith("sha256:") or not name:
            digest_missing += 1
            continue
        groups[(name, str(digest))].append(artifact)

    duplicate_groups: list[dict[str, Any]] = []
    delete_proven: list[dict[str, Any]] = []
    report_only_duplicates: list[dict[str, Any]] = []

    for (name, digest), rows in groups.items():
        if len(rows) < 2:
            continue
        ordered = sorted(rows, key=lambda r: (r.get("created_at") or "", int(r.get("id") or 0)), reverse=True)
        keep = next((row for row in ordered if not row.get("expired")), ordered[0])
        reclaimable = 0
        candidates = []
        for row in ordered:
            if row.get("id") == keep.get("id"):
                continue
            created = parse_time(row.get("created_at"))
            age_days = (now - created).total_seconds() / 86400 if created else None
            reasons = ["same_name", "same_sha256_digest", f"retained_artifact_id={keep.get('id')}"]
            blockers = []
            if row.get("expired"):
                blockers.append("already_expired_or_expiring_server_side")
            if not created:
                blockers.append("created_at_unparseable")
            elif age_days is not None and age_days < min_age_days:
                blockers.append(f"younger_than_{min_age_days}_days")
            if current_sha and row.get("head_sha") == current_sha:
                blockers.append("current_main_evidence")
            if not main_authority:
                blockers.append("not_main_authority_run")
            if keep.get("expired"):
                blockers.append("retained_copy_expired")
            if int(keep.get("size_in_bytes") or 0) != int(row.get("size_in_bytes") or 0):
                blockers.append("digest_size_inconsistency")

            decision = "ACTIONS_DELETE_PROVEN_100" if not blockers else "ACTIONS_DUPLICATE_PROVEN_REPORT_ONLY"
            candidate = {
                **row,
                "decision": decision,
                "age_days": round(age_days, 3) if age_days is not None else None,
                "reasons": reasons,
                "blockers": blockers,
                "retained_artifact": {
                    "id": keep.get("id"),
                    "name": keep.get("name"),
                    "digest": keep.get("digest"),
                    "size_in_bytes": keep.get("size_in_bytes"),
                    "created_at": keep.get("created_at"),
                    "head_branch": keep.get("head_branch"),
                    "head_sha": keep.get("head_sha"),
                    "workflow_run_id": keep.get("workflow_run_id"),
                },
            }
            candidates.append(candidate)
            if decision == "ACTIONS_DELETE_PROVEN_100":
                delete_proven.append(candidate)
                reclaimable += int(row.get("size_in_bytes") or 0)
            else:
                report_only_duplicates.append(candidate)

        duplicate_groups.append({
            "name": name,
            "digest": digest,
            "count": len(ordered),
            "total_bytes": sum(int(x.get("size_in_bytes") or 0) for x in ordered),
            "total_human": human_bytes(sum(int(x.get("size_in_bytes") or 0) for x in ordered)),
            "retained_artifact_id": keep.get("id"),
            "delete_proven_count": sum(1 for x in candidates if x["decision"] == "ACTIONS_DELETE_PROVEN_100"),
            "delete_proven_bytes": reclaimable,
            "delete_proven_human": human_bytes(reclaimable),
        })

    duplicate_groups.sort(key=lambda x: x["delete_proven_bytes"], reverse=True)
    delete_proven.sort(key=lambda x: int(x.get("size_in_bytes") or 0), reverse=True)
    report_only_duplicates.sort(key=lambda x: int(x.get("size_in_bytes") or 0), reverse=True)
    return {
        "digest_missing_count": digest_missing,
        "exact_digest_duplicate_group_count": len(duplicate_groups),
        "delete_proven": delete_proven,
        "report_only_duplicates": report_only_duplicates,
        "duplicate_groups": duplicate_groups,
    }


def fetch_all_artifacts(repo: str, token: str, max_pages: int) -> tuple[int, list[dict[str, Any]], int, bool]:
    artifacts: list[dict[str, Any]] = []
    total_count = 0
    pages = 0
    for page in range(1, max_pages + 1):
        payload = github_get(
            f"https://api.github.com/repos/{repo}/actions/artifacts?per_page=100&page={page}", token
        )
        pages = page
        if page == 1:
            total_count = int(payload.get("total_count") or 0)
        batch = payload.get("artifacts") or []
        artifacts.extend(artifact_row(raw) for raw in batch)
        if not batch or len(artifacts) >= total_count or len(batch) < 100:
            break
    return total_count, artifacts, pages, bool(total_count and len(artifacts) >= total_count)


def fetch_all_caches(repo: str, token: str, max_pages: int) -> tuple[int, list[dict[str, Any]], int, bool]:
    caches: list[dict[str, Any]] = []
    total_count = 0
    pages = 0
    for page in range(1, max_pages + 1):
        payload = github_get(
            f"https://api.github.com/repos/{repo}/actions/caches?per_page=100&page={page}", token
        )
        pages = page
        if page == 1:
            total_count = int(payload.get("total_count") or 0)
        batch = payload.get("actions_caches") or []
        for raw in batch:
            caches.append({
                "id": raw.get("id"),
                "key": raw.get("key"),
                "ref": raw.get("ref"),
                "size_in_bytes": int(raw.get("size_in_bytes") or 0),
                "created_at": raw.get("created_at"),
                "last_accessed_at": raw.get("last_accessed_at"),
            })
        if not batch or len(caches) >= total_count or len(batch) < 100:
            break
    return total_count, caches, pages, bool(total_count and len(caches) >= total_count)


def classify_stale_caches(caches: list[dict[str, Any]], now: datetime, stale_days: int = 14) -> list[dict[str, Any]]:
    rows = []
    for cache in caches:
        last = parse_time(cache.get("last_accessed_at")) or parse_time(cache.get("created_at"))
        age_days = (now - last).total_seconds() / 86400 if last else None
        ref = str(cache.get("ref") or "")
        blockers = []
        if ref == "refs/heads/main":
            blockers.append("main_cache")
        if age_days is None:
            blockers.append("last_accessed_unparseable")
        elif age_days < stale_days:
            blockers.append(f"accessed_within_{stale_days}_days")
        rows.append({
            **cache,
            "age_days_since_access": round(age_days, 3) if age_days is not None else None,
            "decision": "CACHE_RECLAIM_CANDIDATE" if not blockers else "CACHE_KEEP",
            "blockers": blockers,
        })
    return sorted(rows, key=lambda r: int(r.get("size_in_bytes") or 0), reverse=True)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-pages", type=int, default=1200)
    parser.add_argument("--min-age-days", type=int, default=DEFAULT_MIN_AGE_DAYS)
    args = parser.parse_args(argv or sys.argv[1:])

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        raise SystemExit("GITHUB_TOKEN and GITHUB_REPOSITORY are required")

    now = utc_now()
    head = current_head()
    authority = is_main_authority()
    artifact_total, artifacts, artifact_pages, artifact_complete = fetch_all_artifacts(repo, token, args.max_pages)
    cache_total, caches, cache_pages, cache_complete = fetch_all_caches(repo, token, args.max_pages)
    duplicate = classify_duplicate_groups(
        artifacts,
        now=now,
        current_sha=head,
        main_authority=authority,
        min_age_days=args.min_age_days,
    )
    cache_rows = classify_stale_caches(caches, now)
    cache_candidates = [x for x in cache_rows if x["decision"] == "CACHE_RECLAIM_CANDIDATE"]
    delete_proven = duplicate["delete_proven"]

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": now.isoformat(),
        "repository": repo,
        "head_sha": head,
        "main_authority": authority,
        "min_artifact_age_days": args.min_age_days,
        "artifact_api_total_count": artifact_total,
        "artifact_inventory_count": len(artifacts),
        "artifact_pages_scanned": artifact_pages,
        "artifact_inventory_complete": artifact_complete,
        "artifact_inventory_truncated": not artifact_complete,
        "artifact_inventory_bytes": sum(int(x.get("size_in_bytes") or 0) for x in artifacts),
        "artifact_inventory_human": human_bytes(sum(int(x.get("size_in_bytes") or 0) for x in artifacts)),
        "artifact_digest_missing_count": duplicate["digest_missing_count"],
        "exact_digest_duplicate_group_count": duplicate["exact_digest_duplicate_group_count"],
        "actions_delete_proven_count": len(delete_proven),
        "actions_delete_proven_bytes": sum(int(x.get("size_in_bytes") or 0) for x in delete_proven),
        "actions_delete_proven_human": human_bytes(sum(int(x.get("size_in_bytes") or 0) for x in delete_proven)),
        "cache_api_total_count": cache_total,
        "cache_inventory_count": len(caches),
        "cache_inventory_complete": cache_complete,
        "cache_inventory_bytes": sum(int(x.get("size_in_bytes") or 0) for x in caches),
        "cache_inventory_human": human_bytes(sum(int(x.get("size_in_bytes") or 0) for x in caches)),
        "cache_reclaim_candidate_count": len(cache_candidates),
        "cache_reclaim_candidate_bytes": sum(int(x.get("size_in_bytes") or 0) for x in cache_candidates),
        "cache_reclaim_candidate_human": human_bytes(sum(int(x.get("size_in_bytes") or 0) for x in cache_candidates)),
        "report_only": True,
        "artifacts_deleted": 0,
        "caches_deleted": 0,
    }

    out = Path(args.out)
    write_json(out / "actions_storage_summary.json", summary)
    write_json(out / "actions_delete_proven_100.json", delete_proven)
    write_json(out / "actions_exact_digest_duplicate_groups.json", duplicate["duplicate_groups"][:2000])
    write_json(out / "actions_duplicate_report_only.json", duplicate["report_only_duplicates"][:5000])
    write_json(out / "actions_cache_reclaim_candidates.json", cache_candidates)
    write_json(out / "actions_cache_inventory.json", cache_rows)

    md = [
        "# System3 Actions Storage Forensic", "",
        f"- Schema: `{SCHEMA}`",
        f"- HEAD: `{head}`",
        f"- Main-authority run: **{authority}**",
        f"- Artifact API total: **{artifact_total}**",
        f"- Artifact inventory: **{len(artifacts)} / {human_bytes(summary['artifact_inventory_bytes'])}**",
        f"- Artifact inventory complete: **{artifact_complete}**",
        f"- Exact digest duplicate groups: **{duplicate['exact_digest_duplicate_group_count']}**",
        f"- `ACTIONS_DELETE_PROVEN_100`: **{len(delete_proven)} / {summary['actions_delete_proven_human']}**",
        f"- Caches: **{len(caches)} / {summary['cache_inventory_human']}**",
        f"- Stale non-main cache candidates: **{len(cache_candidates)} / {summary['cache_reclaim_candidate_human']}**",
        "- Artifacts/caches deleted by this module: **0**", "",
        "## Artifact deletion proof contract", "",
        "A row can be `ACTIONS_DELETE_PROVEN_100` only on an exact `main` authority run and only when: same artifact name; same GitHub-reported SHA-256 digest; retained identical non-expired copy exists; sizes agree; candidate is at least the minimum age; candidate is not current-main evidence; candidate is not already expired.",
        "", "## Important", "",
        "Deletion remains a separate destructive action. This module only emits evidence. Preserve this report/manifest before any artifact deletion so deleted artifact IDs map to the retained identical artifact ID.",
    ]
    (out / "ACTIONS_STORAGE_EXECUTIVE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
