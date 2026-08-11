#!/usr/bin/env python3
"""Safely deploy Genesis System3 to Cloud Run.

Deployment contract:
- build an immutable image for the exact git SHA;
- force LIVE and automatic order execution OFF;
- create the new Cloud Run revision with *zero production traffic*;
- address the candidate through a revision tag and prove HTTP/API startup;
- promote 100% traffic only to that exact proven revision;
- on any candidate failure, leave the previously serving revision untouched;
- never report READY merely because an older revision is still ready.

The public ANALYZER/PAPER dashboard remains read-only. Worker ingestion uses its
separate Secret Manager token. No Dhan PIN/TOTP secret is mounted in the web
service.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
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
CANDIDATE_TAG = "candidate"

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
    ("DHAN_TOKEN_SOURCE", "gcp-secret-manager-dynamic"),
    ("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token"),
    ("DHAN_TOKEN_CACHE_TTL_S", "30"),
    ("DHAN_TOKEN_ROTATION_JOB", os.environ.get("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")),
    ("DHAN_TOKEN_ROTATION_SCHEDULE", "07:30 IST daily"),
    ("DHAN_STATUS_AUTO_REFRESH", "0"),
    ("DHAN_STATUS_REFRESH_COOLDOWN_S", "3600"),
    ("DHAN_PERSIST_TOKEN_TO_SM", "0"),
    ("SYSTEM3_STARTUP_TOKEN_REFRESH", "0"),
    ("BROKER_SELF_HEAL_TOKEN_REFRESH", "0"),
    ("DHAN_CANONICAL_ROTATION_SELF_HEAL", "1"),
    ("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "130"),
    ("DHAN_CANONICAL_ROTATION_WAIT_S", "120"),
    ("CLOUD_MODE", "1"),
    ("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run"),
    ("MEM_LIMIT_MB", "960"),
    ("MEM_WARN_MB", "700"),
    ("MEM_GC_MB", "850"),
    ("MARKET_TOP_MICRO_STREAM", "0"),
    ("SYSTEM3_PUBLIC_BACKEND_URL", "https://genesis-system3-web-doq2wplepa-el.a.run.app"),
    ("SYSTEM3_API_BASE", "https://genesis-system3-web-doq2wplepa-el.a.run.app"),
)


def _session() -> AuthorizedSession:
    creds, _ = google_auth_default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return AuthorizedSession(creds)


def _run(args: list[str], *, capture: bool = False) -> str:
    print("GCLOUD", " ".join(args[:4]), "...")
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=False,
    )
    if proc.returncode:
        if capture:
            if proc.stdout:
                print(proc.stdout[-4000:])
            if proc.stderr:
                print(proc.stderr[-4000:])
        raise subprocess.CalledProcessError(proc.returncode, args, proc.stdout, proc.stderr)
    return (proc.stdout or "").strip() if capture else ""


def _service_json() -> dict[str, Any]:
    raw = _run(
        [
            "gcloud", "run", "services", "describe", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}", "--format=json",
        ],
        capture=True,
    )
    return json.loads(raw)


def _revision_json(revision: str) -> dict[str, Any]:
    raw = _run(
        [
            "gcloud", "run", "revisions", "describe", revision,
            f"--project={PROJECT}", f"--region={REGION}", "--format=json",
        ],
        capture=True,
    )
    return json.loads(raw)


def _require_secret_exists(session: AuthorizedSession, secret_id: str) -> None:
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
    scratch_root = Path(os.environ.get("SYSTEM3_DEPLOY_SCRATCH", r"E:\System3_deploy_scratch"))
    try:
        scratch_root.mkdir(parents=True, exist_ok=True)
        out = scratch_root / f"deploy_{sha[:12]}.tgz"
        (scratch_root / ".write_test").write_text("ok", encoding="utf-8")
        (scratch_root / ".write_test").unlink(missing_ok=True)
    except Exception:
        out = ROOT / ".secrets" / f"deploy_{sha[:12]}.tgz"
        out.parent.mkdir(parents=True, exist_ok=True)
    include_worktree = os.environ.get("SYSTEM3_DEPLOY_INCLUDE_WORKTREE", "").strip() in {"1", "true", "YES"}
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
        f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=media&name={object_name}",
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
            "steps": [{
                "name": "gcr.io/cloud-builders/docker",
                "args": ["build", "--file=dashboard/backend/Dockerfile", f"--tag={image}", "."],
            }],
            "images": [image],
        },
        timeout=120,
    )
    if create.status_code not in (200, 201):
        raise SystemExit(f"Build create failed {create.status_code}: {create.text[:800]}")
    build_id = (create.json().get("metadata") or {}).get("build", {}).get("id")
    print(f"BUILD_ID {build_id}")
    for i in range(240):
        b = session.get(f"https://cloudbuild.googleapis.com/v1/projects/{PROJECT}/builds/{build_id}", timeout=60).json()
        status = b.get("status")
        print(f"build_wait[{i}] {status}")
        if status == "SUCCESS":
            return
        if status in {"FAILURE", "CANCELLED", "EXPIRED", "TIMEOUT", "INTERNAL_ERROR"}:
            raise SystemExit(f"Build {status}: {b.get('logUrl')} {b.get('failureInfo') or b.get('statusDetail')}")
        time.sleep(15)
    raise SystemExit("Build timed out waiting for SUCCESS")


def _env_arg(sha: str) -> str:
    pairs = list(SAFE_ENV) + [("DEPLOY_GIT_SHA", sha)]
    return ",".join(f"{k}={v}" for k, v in pairs)


def _candidate_url(service: dict[str, Any]) -> str:
    for item in ((service.get("status") or {}).get("traffic") or []):
        if item.get("tag") == CANDIDATE_TAG and item.get("url"):
            return str(item["url"]).rstrip("/")
    # Some gcloud/API versions expose tagged URLs at the top-level traffic list.
    for item in (service.get("traffic") or []):
        if item.get("tag") == CANDIDATE_TAG and item.get("url"):
            return str(item["url"]).rstrip("/")
    raise RuntimeError("candidate revision tag URL was not published")


def _http_json(url: str, attempts: int = 12) -> dict[str, Any]:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=20) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last = exc
            print(f"candidate_probe[{attempt}] {type(exc).__name__}")
            time.sleep(min(5, attempt))
    raise RuntimeError(f"candidate HTTP proof failed for {url}: {type(last).__name__ if last else 'unknown'}")


def _deploy_candidate(image: str, sha: str) -> tuple[str, str, str]:
    before = _service_json()
    previous_ready = str(((before.get("status") or {}).get("latestReadyRevisionName") or ""))
    if not previous_ready:
        raise RuntimeError("no previously ready Cloud Run revision to protect")
    print("PREVIOUS_READY", previous_ready)

    cmd = [
        "gcloud", "run", "deploy", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", f"--image={image}",
        "--no-traffic", f"--tag={CANDIDATE_TAG}", "--min=0", "--max=1",
        "--memory=1Gi", "--cpu=1", f"--update-env-vars={_env_arg(sha)}",
        "--remove-secrets=API_KEY,DHAN_PIN,DHAN_TOTP_SECRET,DHAN_TOTP",
        f"--update-secrets=WORKER_PUSH_TOKEN={WORKER_PUSH_TOKEN_SECRET_ID}:latest",
        "--quiet",
    ]
    try:
        _run(cmd, capture=True)
    except subprocess.CalledProcessError:
        after_fail = _service_json()
        still_ready = str(((after_fail.get("status") or {}).get("latestReadyRevisionName") or ""))
        print("CANDIDATE_DEPLOY_FAILED previous_ready=", previous_ready, "still_ready=", still_ready)
        if still_ready != previous_ready:
            raise RuntimeError(
                f"failed candidate changed ready revision: before={previous_ready} after={still_ready}"
            )
        raise

    service = _service_json()
    candidate = str(((service.get("status") or {}).get("latestCreatedRevisionName") or ""))
    if not candidate or candidate == previous_ready:
        raise RuntimeError(f"new candidate revision not identified: candidate={candidate!r} previous={previous_ready!r}")

    revision = _revision_json(candidate)
    containers = ((revision.get("spec") or {}).get("containers") or [])
    if not containers:
        containers = ((((revision.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or [])
    deployed_image = str((containers[0] if containers else {}).get("image") or "")
    if image not in deployed_image and deployed_image != image:
        raise RuntimeError(f"candidate image mismatch: expected={image} actual={deployed_image}")

    url = _candidate_url(service)
    print("CANDIDATE", candidate)
    print("CANDIDATE_URL", url)
    print("CANDIDATE_TRAFFIC", "0%")

    auth = _http_json(f"{url}/api/auth/status")
    if auth.get("required") is not False:
        raise RuntimeError(f"candidate auth/read-only proof failed: {auth}")
    state = _http_json(f"{url}/api/state")
    if not isinstance(state, dict):
        raise RuntimeError("candidate /api/state did not return JSON object")
    print("CANDIDATE_HTTP_PROOF_OK", candidate)

    # Promote the exact tested immutable revision, never the floating LATEST tag.
    _run([
        "gcloud", "run", "services", "update-traffic", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", f"--to-revisions={candidate}=100", "--quiet",
    ], capture=True)

    promoted = _service_json()
    ready = str(((promoted.get("status") or {}).get("latestReadyRevisionName") or ""))
    if ready != candidate:
        raise RuntimeError(f"promotion proof failed: candidate={candidate} latestReady={ready}")

    traffic = ((promoted.get("status") or {}).get("traffic") or [])
    candidate_percent = 0
    for item in traffic:
        if item.get("revisionName") == candidate:
            candidate_percent += int(item.get("percent") or 0)
    if candidate_percent != 100:
        raise RuntimeError(f"candidate traffic proof failed: revision={candidate} percent={candidate_percent}")

    return candidate, url, previous_ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-worktree", action="store_true")
    args = parser.parse_args()
    if args.include_worktree:
        os.environ["SYSTEM3_DEPLOY_INCLUDE_WORKTREE"] = "1"

    sha = _git_sha()
    deploy_stamp = int(time.time())
    image = f"{REPO}:{sha[:12]}-{deploy_stamp}"
    print("SHA", sha)
    print("IMAGE", image)
    print("SERVICE", SERVICE)
    print("DEPLOYMENT_MODEL candidate-no-traffic-health-proof-explicit-promotion")
    print("LIVE_OFF enforced")
    print("DASHBOARD_PUBLIC_READONLY enforced (REQUIRE_API_KEY=false, API_KEY unmounted)")

    session = _session()
    _require_secret_exists(session, WORKER_PUSH_TOKEN_SECRET_ID)
    print("WORKER_SECRET_PREREQUISITE_OK", WORKER_PUSH_TOKEN_SECRET_ID)
    tgz = _archive_tarball(sha)
    print("ARCHIVE_BYTES", tgz.stat().st_size)
    bucket, object_name = _upload_source(session, tgz, sha)
    print("UPLOAD", bucket, object_name)
    _build_image(session, bucket, object_name, image)

    candidate, candidate_url, previous_ready = _deploy_candidate(image, sha)
    print("READY", candidate)
    print("PREVIOUS_READY_RETAINED_FOR_ROLLBACK", previous_ready)
    print("CANDIDATE_URL", candidate_url)
    print("IMAGE", image)
    print(json.dumps({
        "ok": True,
        "revision": candidate,
        "previous_revision": previous_ready,
        "image": image,
        "sha": sha,
        "traffic_percent": 100,
        "live_trading_enabled": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
