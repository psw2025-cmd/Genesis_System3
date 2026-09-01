"""Fail-closed repo-state guard for the local job scheduler.

GitHub main is the single source of truth for Genesis System3 (per
docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md). Local scheduled jobs
must not execute against a checkout that has diverged from main - either
uncommitted local changes or a HEAD that is behind/ahead/diverged from
origin/main - since that would mean running code nobody reviewed on main.

This module is deliberately dependency-free (no requests/PyGithub) so it can
run inside the job scheduler's own subprocess environment without extra
setup, and it never mutates repo history - at most a fast-forward-only pull.
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any


def _git(root: Path, *args: str, timeout: int = 30) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(root),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_and_sync_repo_state(root: Path, remote_branch: str = "main") -> dict[str, Any]:
    """Fetch origin, then verify local state matches it exactly.

    Returns a dict with at least {"ok": bool, "reason": str}. Never raises -
    any git failure itself is treated as a reason to halt (fail-closed), not
    an exception that could crash the caller into an ambiguous state.
    """
    try:
        rc, _, err = _git(root, "fetch", "origin", remote_branch, timeout=30)
        if rc != 0:
            return {"ok": False, "reason": "FETCH_FAILED", "detail": err[:300]}

        rc, dirty_out, err = _git(root, "status", "--porcelain")
        if rc != 0:
            return {"ok": False, "reason": "STATUS_CHECK_FAILED", "detail": err[:300]}
        if dirty_out.strip():
            dirty_count = len(dirty_out.strip().splitlines())
            return {"ok": False, "reason": "LOCAL_DIRTY_DIVERGENCE", "detail": f"{dirty_count} uncommitted change(s)"}

        rc, local_head, _ = _git(root, "rev-parse", "HEAD")
        rc2, remote_head, _ = _git(root, "rev-parse", f"origin/{remote_branch}")
        if rc != 0 or rc2 != 0 or not local_head or not remote_head:
            return {"ok": False, "reason": "SHA_RESOLUTION_FAILED"}

        if local_head == remote_head:
            return {"ok": True, "reason": "IN_SYNC", "sha": local_head}

        # Behind (or ahead-but-clean, e.g. a local commit not yet pushed):
        # only ever fast-forward. Never rebase/reset/force - if that fails,
        # halt rather than guess at a resolution.
        rc, _, err = _git(root, "merge-base", "--is-ancestor", local_head, remote_head)
        if rc != 0:
            return {
                "ok": False,
                "reason": "REPO_DIVERGENCE_HALT",
                "detail": f"local={local_head[:12]} remote={remote_head[:12]} not fast-forwardable",
            }

        rc, _, err = _git(root, "merge", "--ff-only", f"origin/{remote_branch}")
        if rc != 0:
            return {"ok": False, "reason": "FF_PULL_FAILED", "detail": err[:300]}

        rc, new_head, _ = _git(root, "rev-parse", "HEAD")
        return {"ok": True, "reason": "SYNCED_FORWARD", "sha": new_head, "previous_sha": local_head}
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": "GIT_TIMEOUT"}
    except Exception as exc:  # never let a guard crash the caller
        return {"ok": False, "reason": "GUARD_EXCEPTION", "detail": str(exc)[:300]}


_JWT_OR_TOKEN_LIKE = re.compile(r"[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}|[A-Za-z0-9+/]{40,}={0,2}")


def _scrub_value(value: Any) -> Any:
    """Redact anything that looks like a JWT/long token inside free-text fields
    (e.g. a subprocess stderr snippet), as defense in depth beyond the
    key-name filter below."""
    if isinstance(value, str):
        return _JWT_OR_TOKEN_LIKE.sub("[REDACTED_TOKEN_LIKE_VALUE]", value)
    if isinstance(value, dict):
        return {k: _scrub_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrub_value(v) for v in value]
    return value


def write_sanitized_scheduler_status(root: Path, payload: dict[str, Any]) -> Path:
    """Write a secret-free scheduler status snapshot for reports/runtime/latest/."""
    out_dir = root / "reports" / "runtime" / "latest"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "scheduler_status.json"
    safe_payload = {
        k: _scrub_value(v)
        for k, v in payload.items()
        if not any(s in k.lower() for s in ("token", "secret", "password", "pin", "totp", "key"))
    }
    out_path.write_text(json.dumps(safe_payload, indent=2, default=str), encoding="utf-8")
    return out_path


_LAST_PUSH_MARKER = ".scheduler_status_last_push"


def push_sanitized_status_if_due(root: Path, min_interval_s: int = 1800) -> dict[str, Any]:
    """Commit+push reports/runtime/latest/scheduler_status.json, rate-limited.

    Never pushes on every tick - only after min_interval_s has elapsed since
    the last successful push, so a 60s daemon loop doesn't spam commits.
    """
    marker = root / "state" / _LAST_PUSH_MARKER
    now = time.time()
    if marker.exists():
        try:
            last = float(marker.read_text().strip() or "0")
            if now - last < min_interval_s:
                return {"pushed": False, "reason": "RATE_LIMITED"}
        except Exception:
            pass

    status_path = root / "reports" / "runtime" / "latest" / "scheduler_status.json"
    if not status_path.exists():
        return {"pushed": False, "reason": "NO_STATUS_FILE"}

    rc, diff_out, _ = _git(root, "status", "--porcelain", "--", str(status_path.relative_to(root)))
    if rc != 0 or not diff_out.strip():
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(now))
        return {"pushed": False, "reason": "NO_CHANGE"}

    rc, _, err = _git(root, "add", str(status_path.relative_to(root)))
    if rc != 0:
        return {"pushed": False, "reason": "ADD_FAILED", "detail": err[:300]}

    rc, _, err = _git(
        root,
        "-c", "user.name=Genesis System3 Local Scheduler",
        "-c", "user.email=warghade2012@gmail.com",
        "commit", "-m", "chore(scheduler): update sanitized runtime status snapshot [skip ci]",
    )
    if rc != 0:
        return {"pushed": False, "reason": "COMMIT_FAILED", "detail": err[:300]}

    rc, _, err = _git(root, "push", "origin", "HEAD")
    if rc != 0:
        return {"pushed": False, "reason": "PUSH_FAILED", "detail": err[:300]}

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(str(now))
    return {"pushed": True}
