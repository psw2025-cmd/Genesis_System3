#!/usr/bin/env python3
"""Auto-deploy Genesis System3 web service to Cloud Run (image update only).

Builds an immutable image tagged with the full git SHA, then patches the Cloud
Run service container image + safe env vars. Secret mounts and other env are
preserved (never use bare --set-env-vars).

Live trading flags are always forced OFF.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from google.auth import default as google_auth_default
from google.auth.transport.requests import AuthorizedSession

ROOT = Path(__file__).resolve().parents[1]
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.environ.get("GCP_REGION", "asia-south1")
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
REPO = f"{REGION}-docker.pkg.dev/{PROJECT}/system3-containers/genesis-system3"
BUILDER_SA = f"projects/{PROJECT}/serviceAccounts/system3-builder@{PROJECT}.iam.gserviceaccount.com"

SAFE_ENV = (
    ("LIVE_TRADING_ENABLED", "0"),
    ("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
    ("AUTO_EXECUTE_TRADES", "0"),
    ("DHAN_STATUS_AUTO_REFRESH", "0"),
    ("DHAN_STATUS_REFRESH_COOLDOWN_S", "3600"),
    ("DHAN_PERSIST_TOKEN_TO_SM", "0"),
    ("SYSTEM3_STARTUP_TOKEN_REFRESH", "0"),
    ("BROKER_SELF_HEAL_TOKEN_REFRESH", "0"),
    ("CLOUD_MODE", "1"),
    ("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run"),
    ("MEM_LIMIT_MB", "960"),
    ("MEM_WARN_MB", "700"),
    ("MEM_GC_MB", "850"),
    ("MARKET_TOP_MICRO_STREAM", "0"),
    ("DHAN_STATUS_AUTO_REFRESH", "0"),
    ("DHAN_STATUS_REFRESH_COOLDOWN_S", "3600"),
    (
        "SYSTEM3_PUBLIC_BACKEND_URL",
        "https://genesis-system3-web-doq2wplepa-el.a.run.app",
    ),
    (
        "SYSTEM3_API_BASE",
        "https://genesis-system3-web-doq2wplepa-el.a.run.app",
    ),
)


def _session() -> AuthorizedSession:
    creds, _ = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(creds)


def _git_sha() -> str:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if len(sha) != 40:
        raise SystemExit(f"Expected full 40-char SHA, got {sha!r}")
    return sha


def _archive_tarball(sha: str) -> Path:
    """Archive committed tree (CI) or worktree overlay for local emergency deploys."""
    # Prefer non-C: scratch when available — local C: fills up from repeated ~20MB archives.
    scratch_root = Path(os.environ.get("SYSTEM3_DEPLOY_SCRATCH", r"E:\System3_deploy_scratch"))
    try:
        scratch_root.mkdir(parents=True, exist_ok=True)
        out = scratch_root / f"deploy_{sha[:12]}.tgz"
        # Probe writability
        (scratch_root / ".write_test").write_text("ok", encoding="utf-8")
        (scratch_root / ".write_test").unlink(missing_ok=True)
    except Exception:
        out = ROOT / ".secrets" / f"deploy_{sha[:12]}.tgz"
        out.parent.mkdir(parents=True, exist_ok=True)
    include_worktree = os.environ.get("SYSTEM3_DEPLOY_INCLUDE_WORKTREE", "").strip() in {
        "1",
        "true",
        "YES",
    }
    if include_worktree:
        env = dict(os.environ)
        idx = ROOT / ".secrets" / "deploy_index"
        subprocess.check_call(["git", "read-tree", "HEAD"], cwd=ROOT, env={**env, "GIT_INDEX_FILE": str(idx)})
        subprocess.check_call(
            ["git", "add", "-A", "--", "dashboard", "scripts", "core", "src", "config", "deploy"],
            cwd=ROOT,
            env={**env, "GIT_INDEX_FILE": str(idx)},
        )
        tree = subprocess.check_output(
            ["git", "write-tree"], cwd=ROOT, text=True, env={**env, "GIT_INDEX_FILE": str(idx)}
        ).strip()
        with out.open("wb") as fh:
            subprocess.check_call(["git", "archive", "--format=tar.gz", tree], cwd=ROOT, stdout=fh)
    else:
        with out.open("wb") as fh:
            subprocess.check_call(["git", "archive", "--format=tar.gz", "HEAD"], cwd=ROOT, stdout=fh)
    return out


def _upload_source(session: AuthorizedSession, tgz: Path, sha: str) -> tuple[str, str]:
    bucket = f"{PROJECT}_cloudbuild"
    object_name = f"source/genesis-auto-{sha[:12]}-{int(time.time())}.tgz"
    session.post(
        f"https://storage.googleapis.com/storage/v1/b?project={PROJECT}",
        json={"name": bucket, "location": REGION},
        timeout=60,
    )
    up = session.post(
        f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o"
        f"?uploadType=media&name={object_name}",
        data=tgz.read_bytes(),
        headers={"Content-Type": "application/gzip"},
        timeout=600,
    )
    if up.status_code not in (200, 201):
        raise SystemExit(f"Upload failed {up.status_code}: {up.text[:500]}")
    return bucket, object_name


def _build_image(session: AuthorizedSession, bucket: str, object_name: str, image: str) -> None:
    create = session.post(
        f"https://cloudbuild.googleapis.com/v1/projects/{PROJECT}/builds",
        json={
            "serviceAccount": BUILDER_SA,
            "options": {"logging": "CLOUD_LOGGING_ONLY"},
            "timeout": "3600s",
            "source": {"storageSource": {"bucket": bucket, "object": object_name}},
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": [
                        "build",
                        "--file=dashboard/backend/Dockerfile",
                        f"--tag={image}",
                        ".",
                    ],
                }
            ],
            "images": [image],
        },
        timeout=120,
    )
    if create.status_code not in (200, 201):
        raise SystemExit(f"Build create failed {create.status_code}: {create.text[:800]}")
    build_id = (create.json().get("metadata") or {}).get("build", {}).get("id")
    print(f"BUILD_ID {build_id}")
    for i in range(240):
        b = session.get(
            f"https://cloudbuild.googleapis.com/v1/projects/{PROJECT}/builds/{build_id}",
            timeout=60,
        ).json()
        status = b.get("status")
        print(f"build_wait[{i}] {status}")
        if status == "SUCCESS":
            return
        if status in {
            "FAILURE",
            "CANCELLED",
            "EXPIRED",
            "TIMEOUT",
            "INTERNAL_ERROR",
        }:
            raise SystemExit(
                f"Build {status}: {b.get('logUrl')} "
                f"{b.get('failureInfo') or b.get('statusDetail')}"
            )
        time.sleep(15)
    raise SystemExit("Build timed out waiting for SUCCESS")


def _patch_service(session: AuthorizedSession, image: str, sha: str) -> dict[str, Any]:
    svc_url = f"https://run.googleapis.com/v2/projects/{PROJECT}/locations/{REGION}/services/{SERVICE}"
    svc = session.get(svc_url, timeout=60).json()
    c0 = dict((svc.get("template", {}).get("containers") or [{}])[0])
    c0["image"] = image
    # MemGuard showed ~408/480MB on 512Mi — leave headroom for Dhan OC + pandas.
    c0["resources"] = {
        **(c0.get("resources") or {}),
        "limits": {
            **((c0.get("resources") or {}).get("limits") or {}),
            "memory": "1Gi",
            "cpu": ((c0.get("resources") or {}).get("limits") or {}).get("cpu") or "1",
        },
    }
    env_map = {e["name"]: e for e in c0.get("env", []) if "name" in e}
    for k, v in SAFE_ENV:
        env_map[k] = {"name": k, "value": v}
    env_map["DEPLOY_GIT_SHA"] = {"name": "DEPLOY_GIT_SHA", "value": sha}
    # Never keep PIN/TOTP on Cloud Run — minting there invalidates SM-mounted tokens.
    for drop in ("DHAN_PIN", "DHAN_TOTP_SECRET", "DHAN_TOTP"):
        env_map.pop(drop, None)
    c0["env"] = list(env_map.values())
    patch = session.patch(
        svc_url,
        params={"updateMask": "template.containers,template.scaling"},
        json={
            "template": {
                "containers": [c0],
                "scaling": {"minInstanceCount": 1, "maxInstanceCount": 10},
            }
        },
        timeout=120,
    )
    if patch.status_code not in (200, 201):
        raise SystemExit(f"Cloud Run patch failed {patch.status_code}: {patch.text[:600]}")
    for i in range(60):
        cur = session.get(svc_url, timeout=60).json()
        rev = (cur.get("latestReadyRevision") or "").split("/")[-1]
        print(f"run_wait[{i}] reconciling={cur.get('reconciling')} rev={rev}")
        if not cur.get("reconciling") and rev:
            return cur
        time.sleep(5)
    raise SystemExit("Cloud Run reconcile timed out")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-worktree",
        action="store_true",
        help="Include uncommitted dashboard/core/scripts/src/config/deploy changes",
    )
    args = parser.parse_args()
    if args.include_worktree:
        os.environ["SYSTEM3_DEPLOY_INCLUDE_WORKTREE"] = "1"

    sha = _git_sha()
    # Unique tag so Cloud Run always creates a new revision (same git SHA
    # retag alone does not force a pull when the URI string is unchanged).
    deploy_stamp = int(time.time())
    image = f"{REPO}:{sha[:12]}-{deploy_stamp}"
    print("SHA", sha)
    print("IMAGE", image)
    print("SERVICE", SERVICE)
    print("LIVE_OFF enforced")

    session = _session()
    tgz = _archive_tarball(sha)
    print("ARCHIVE_BYTES", tgz.stat().st_size)
    bucket, object_name = _upload_source(session, tgz, sha)
    print("UPLOAD", bucket, object_name)
    _build_image(session, bucket, object_name, image)
    cur = _patch_service(session, image, sha)
    rev = (cur.get("latestReadyRevision") or "").split("/")[-1]
    print("READY", rev)
    print("URL", cur.get("uri"))
    print("IMAGE", image)
    print(json.dumps({"ok": True, "revision": rev, "image": image, "sha": sha}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
