#!/usr/bin/env python3
"""Auto-deploy Genesis System3 web service to Cloud Run as one canonical revision.

Builds an immutable image tagged with the full git SHA, then applies the final
Cloud Run container, scaling, public PAPER/ANALYZER, dynamic Dhan token and
Secret Manager worker-token configuration in one service template mutation.
There is no follow-up configuration revision.

The interactive dashboard is intentionally public/read-only in ANALYZER/PAPER:
REQUIRE_API_KEY=false and API_KEY is not mounted. Worker ingestion keeps its
separate Secret Manager token. Live trading flags are always forced OFF.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from google.auth import default as google_auth_default
from google.auth.transport.requests import AuthorizedSession

ROOT = Path(__file__).resolve().parents[1]
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.environ.get("GCP_REGION", "asia-south1")
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
ROTATION_JOB = os.environ.get("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")
REPO = f"{REGION}-docker.pkg.dev/{PROJECT}/system3-containers/genesis-system3"
BUILDER_SA = f"projects/{PROJECT}/serviceAccounts/system3-builder@{PROJECT}.iam.gserviceaccount.com"

WORKER_PUSH_TOKEN_SECRET_ID = os.environ.get(
    "WORKER_PUSH_TOKEN_SECRET_ID", "system3-dashboard-worker-push-token"
)

SAFE_ENV = (
    ("LIVE_TRADING_ENABLED", "0"),
    ("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
    ("AUTO_EXECUTE_TRADES", "0"),
    ("REQUIRE_API_KEY", "false"),
    ("ANALYZE_MODE", "1"),
    ("SYSTEM3_MODE", "ANALYZER"),
    ("SYSTEM3_REAL_ONLY", "1"),
    ("DHAN_TOKEN_SOURCE", "gcp-secret-manager-dynamic"),
    ("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token"),
    ("DHAN_TOKEN_CACHE_TTL_S", "30"),
    ("DHAN_TOKEN_ROTATION_JOB", ROTATION_JOB),
    ("DHAN_TOKEN_ROTATION_SCHEDULE", "07:30 IST daily"),
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


def _require_secret_exists(session: AuthorizedSession, secret_id: str) -> None:
    """Fail closed if a required Secret Manager secret is missing or inaccessible."""
    url = f"https://secretmanager.googleapis.com/v1/projects/{PROJECT}/secrets/{secret_id}"
    resp = session.get(url, timeout=30)
    if resp.status_code != 200:
        raise SystemExit(
            f"Required Secret Manager secret '{secret_id}' is missing or inaccessible "
            f"(status {resp.status_code})."
        )


def _git_sha() -> str:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if len(sha) != 40:
        raise SystemExit(f"Expected full 40-char SHA, got {sha!r}")
    return sha


def _archive_tarball(sha: str) -> Path:
    """Archive committed tree (CI) or worktree overlay for local emergency deploys."""
    scratch_root = Path(os.environ.get("SYSTEM3_DEPLOY_SCRATCH", r"E:\System3_deploy_scratch"))
    try:
        scratch_root.mkdir(parents=True, exist_ok=True)
        out = scratch_root / f"deploy_{sha[:12]}.tgz"
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
        if status in {"FAILURE", "CANCELLED", "EXPIRED", "TIMEOUT", "INTERNAL_ERROR"}:
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

    # Public PAPER/ANALYZER dashboard: no reusable dashboard API key in the
    # serving revision. Worker ingestion keeps its separate secret.
    env_map.pop("API_KEY", None)
    env_map["WORKER_PUSH_TOKEN"] = {
        "name": "WORKER_PUSH_TOKEN",
        "valueSource": {
            "secretKeyRef": {"secret": WORKER_PUSH_TOKEN_SECRET_ID, "version": "latest"}
        },
    }
    for drop in ("DHAN_PIN", "DHAN_TOTP_SECRET", "DHAN_TOTP"):
        env_map.pop(drop, None)
    c0["env"] = list(env_map.values())

    # One canonical desired state. A second gcloud service update after this
    # step is prohibited because it creates another revision and can invalidate
    # the exact-SHA runtime proof.
    patch = session.patch(
        svc_url,
        params={"updateMask": "template.containers,template.scaling"},
        json={
            "template": {
                "containers": [c0],
                "scaling": {"minInstanceCount": 0, "maxInstanceCount": 1},
            }
        },
        timeout=120,
    )
    if patch.status_code not in (200, 201):
        raise SystemExit(f"Cloud Run patch failed {patch.status_code}: {patch.text[:600]}")

    for i in range(90):
        cur = session.get(svc_url, timeout=60).json()
        ready = str(cur.get("latestReadyRevision") or "").split("/")[-1]
        created = str(cur.get("latestCreatedRevision") or "").split("/")[-1]
        desired_containers = (cur.get("template", {}).get("containers") or [{}])
        desired_image = str(desired_containers[0].get("image") or "")
        reconciling = bool(cur.get("reconciling"))
        print(
            f"run_wait[{i}] reconciling={reconciling} "
            f"created={created or '-'} ready={ready or '-'}"
        )
        if (
            not reconciling
            and ready
            and created
            and ready == created
            and desired_image == image
        ):
            return cur
        time.sleep(5)
    raise SystemExit("Cloud Run canonical revision did not become latest-ready in time")


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
    deploy_stamp = int(time.time())
    image = f"{REPO}:{sha[:12]}-{deploy_stamp}"
    print("SHA", sha)
    print("IMAGE", image)
    print("SERVICE", SERVICE)
    print("LIVE_OFF enforced")
    print("DASHBOARD_PUBLIC_READONLY enforced (REQUIRE_API_KEY=false, API_KEY unmounted)")
    print("CANONICAL_RUNTIME_SPEC single Cloud Run revision mutation")

    session = _session()
    _require_secret_exists(session, WORKER_PUSH_TOKEN_SECRET_ID)
    print("WORKER_SECRET_PREREQUISITE_OK", WORKER_PUSH_TOKEN_SECRET_ID)
    tgz = _archive_tarball(sha)
    print("ARCHIVE_BYTES", tgz.stat().st_size)
    bucket, object_name = _upload_source(session, tgz, sha)
    print("UPLOAD", bucket, object_name)
    _build_image(session, bucket, object_name, image)
    cur = _patch_service(session, image, sha)
    rev = str(cur.get("latestReadyRevision") or "").split("/")[-1]
    print("READY", rev)
    print("URL", cur.get("uri"))
    print("IMAGE", image)
    print(json.dumps({"ok": True, "revision": rev, "image": image, "sha": sha}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
