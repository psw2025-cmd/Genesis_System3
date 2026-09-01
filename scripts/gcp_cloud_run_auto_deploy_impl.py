#!/usr/bin/env python3
"""Safely deploy Genesis System3 to Cloud Run.

Deployment contract:
- build an immutable image for the exact git SHA;
- force LIVE and automatic order execution OFF;
- create the new Cloud Run revision with *zero production traffic*;
- address the candidate through a revision tag and prove its exact Ready state;
- prove the tagged candidate HTTP/API before promotion;
- promote 100% traffic only to that exact proven revision;
- on any candidate failure, preserve/restore the previously serving traffic;
- capture sanitized failed-revision evidence automatically;
- never use latestReadyRevisionName as a substitute for serving-traffic proof.

The public ANALYZER/PAPER dashboard remains read-only. Worker ingestion uses its
separate Secret Manager token. No Dhan PIN/TOTP secret is mounted in the web
service.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
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
RUNTIME_SA = f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com"
CANDIDATE_TAG = "candidate"

WORKER_PUSH_TOKEN_SECRET_ID = os.environ.get(
    "WORKER_PUSH_TOKEN_SECRET_ID", "system3-dashboard-worker-push-token"
)

# This is the complete authoritative Cloud Run web-service runtime contract.
# Startup-critical values are explicit so a clean service recreation cannot
# silently re-enable eager warm-up or lose analyzer-only state constraints.
SAFE_ENV = (
    ("LIVE_TRADING_ENABLED", "0"),
    ("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
    ("AUTO_EXECUTE_TRADES", "0"),
    ("REQUIRE_API_KEY", "false"),
    ("ANALYZE_MODE", "1"),
    ("SYSTEM3_MODE", "ANALYZER"),
    ("SYSTEM3_REAL_ONLY", "1"),
    ("CLOUD_PAPER_ENGINE", "0"),
    ("DEFER_INSTRUMENT_WARMUP", "1"),
    ("SYSTEM3_STATE_BACKEND", "firestore"),
    ("SYSTEM3_STATE_BACKEND_REQUIRED", "1"),
    ("SYSTEM3_FIRESTORE_PROJECT", PROJECT),
    ("SYSTEM3_STATE_REFRESH_S", "5"),
    ("SYSTEM3_SYNC_INTERVAL_S", "60"),
    ("DHAN_TOKEN_SOURCE", "gcp-secret-manager-dynamic"),
    ("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token"),
    ("DHAN_TOKEN_CACHE_TTL_S", "30"),
    ("DHAN_TOKEN_ROTATION_JOB", os.environ.get("DHAN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")),
    ("DHAN_TOKEN_ROTATION_SCHEDULE", "*/5 * * * * Asia/Kolkata"),
    ("DHAN_STATUS_AUTO_REFRESH", "0"),
    ("DHAN_STATUS_REFRESH_COOLDOWN_S", "3600"),
    ("DHAN_PERSIST_TOKEN_TO_SM", "0"),
    ("SYSTEM3_STARTUP_TOKEN_REFRESH", "0"),
    ("BROKER_SELF_HEAL_TOKEN_REFRESH", "0"),
    # Scheduler/manual-only token authority.  The web process must never invoke
    # the canonical rotation path; normal TTL discovery can still adopt a newly
    # published Secret Manager version.  The independent rotator remint cooldown
    # remains 30 minutes in the Cloud Run Job configuration.
    ("DHAN_CANONICAL_ROTATION_SELF_HEAL", "0"),
    ("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "900"),
    ("DHAN_ROTATE_PUBSUB_TOPIC", "broker-token-rotate"),
    ("DHAN_CANONICAL_ROTATION_WAIT_S", "120"),
    ("CLOUD_MODE", "1"),
    ("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run"),
    ("MEM_LIMIT_MB", "960"),
    ("MEM_WARN_MB", "700"),
    ("MEM_GC_MB", "850"),
    # Rank the already-paced option-chain cache for the Signals/Market Top WS
    # board. This loop performs no additional Dhan option-chain fan-out; keeping
    # it disabled leaves the market-hours UI permanently at 0 rows.
    ("MARKET_TOP_MICRO_STREAM", "1"),
    ("SYSTEM3_PUBLIC_BACKEND_URL", "https://genesis-system3-web-doq2wplepa-el.a.run.app"),
    ("SYSTEM3_API_BASE", "https://genesis-system3-web-doq2wplepa-el.a.run.app"),
    ("PUBLIC_BACKEND_URL", "https://genesis-system3-web-doq2wplepa-el.a.run.app"),
    ("PUBLIC_DASHBOARD_URL", "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui"),
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


def _traffic_allocations(service: dict[str, Any]) -> dict[str, int]:
    """Return resolved production traffic by immutable revision name."""
    allocations: dict[str, int] = {}
    for item in ((service.get("status") or {}).get("traffic") or []):
        revision = str(item.get("revisionName") or "")
        percent = int(item.get("percent") or 0)
        if revision and percent > 0:
            allocations[revision] = allocations.get(revision, 0) + percent
    return dict(sorted(allocations.items()))


def _traffic_percent(service: dict[str, Any], revision: str) -> int:
    return _traffic_allocations(service).get(revision, 0)


def _restore_traffic(allocations: dict[str, int]) -> None:
    if not allocations or sum(allocations.values()) != 100:
        raise RuntimeError(f"refusing unsafe rollback traffic map: {allocations}")
    target = ",".join(f"{revision}={percent}" for revision, percent in allocations.items())
    _run(
        [
            "gcloud", "run", "services", "update-traffic", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}", f"--to-revisions={target}", "--quiet",
        ],
        capture=True,
    )
    restored = _traffic_allocations(_service_json())
    if restored != allocations:
        raise RuntimeError(f"traffic rollback proof failed: expected={allocations} actual={restored}")
    print("PREVIOUS_TRAFFIC_RESTORED", json.dumps(restored, sort_keys=True))


def _ready_condition(revision: dict[str, Any]) -> tuple[str, str, str]:
    for condition in ((revision.get("status") or {}).get("conditions") or []):
        if condition.get("type") == "Ready":
            return (
                str(condition.get("status") or "Unknown"),
                str(condition.get("reason") or ""),
                str(condition.get("message") or "")[:500],
            )
    return "Unknown", "", ""


def _wait_revision_ready(revision_name: str, timeout_s: int = 180) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    terminal_reasons = {
        "HealthCheckContainerError",
        "ContainerMissing",
        "ContainerPermissionDenied",
        "RevisionFailed",
    }
    while time.time() < deadline:
        last = _revision_json(revision_name)
        status, reason, message = _ready_condition(last)
        print("candidate_ready", revision_name, status, reason)
        if status == "True":
            return last
        if status == "False" and reason in terminal_reasons:
            raise RuntimeError(
                f"candidate revision terminal failure: revision={revision_name} reason={reason} message={message}"
            )
        time.sleep(5)
    status, reason, message = _ready_condition(last)
    raise RuntimeError(
        f"candidate revision readiness timeout: revision={revision_name} status={status} reason={reason} message={message}"
    )


def _run_failed_revision_forensic(revision_name: str) -> None:
    script = ROOT / "scripts" / "gcp_failed_revision_forensic.py"
    if not script.exists() or not revision_name:
        return
    env = dict(os.environ)
    env.update(
        {
            "FAILED_REVISION": revision_name,
            "GOOGLE_CLOUD_PROJECT": PROJECT,
            "GCP_REGION": REGION,
            "GCP_CLOUD_RUN_SERVICE": SERVICE,
        }
    )
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    print("FAILED_REVISION_FORENSIC_RC", proc.returncode)
    if proc.stdout:
        print(proc.stdout[-16000:])
    if proc.stderr:
        print(proc.stderr[-4000:])


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
    env_map = dict(SAFE_ENV)
    env_map.pop("API_KEY", None)
    env_map["DEPLOY_GIT_SHA"] = sha
    return ",".join(f"{key}={value}" for key, value in env_map.items())


def _candidate_url(service: dict[str, Any], candidate: str) -> str:
    for item in ((service.get("status") or {}).get("traffic") or []):
        if item.get("tag") == CANDIDATE_TAG and item.get("revisionName") == candidate and item.get("url"):
            return str(item["url"]).rstrip("/")
    raise RuntimeError(f"candidate tag URL not published for exact revision {candidate}")


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


def _candidate_created_after(service: dict[str, Any], before_created: str) -> str:
    candidate = str(((service.get("status") or {}).get("latestCreatedRevisionName") or ""))
    return candidate if candidate and candidate != before_created else ""


def _assert_candidate_image(revision: dict[str, Any], image: str) -> None:
    containers = ((revision.get("spec") or {}).get("containers") or [])
    if not containers:
        containers = ((((revision.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or [])
    deployed_image = str((containers[0] if containers else {}).get("image") or "")
    if image not in deployed_image and deployed_image != image:
        raise RuntimeError(f"candidate image mismatch: expected={image} actual={deployed_image}")


def _preserve_previous_ready(previous_ready: dict[str, int]) -> None:
    """Fail closed unless the exact pre-candidate traffic map is preserved."""
    still_ready = _traffic_allocations(_service_json())
    if still_ready != previous_ready:
        _restore_traffic(previous_ready)
        still_ready = _traffic_allocations(_service_json())
    if still_ready != previous_ready:
        raise RuntimeError(
            f"previous traffic preservation failed: expected={previous_ready} actual={still_ready}"
        )
    print("PREVIOUS_TRAFFIC_RESTORED", json.dumps(still_ready, sort_keys=True))


def _deploy_candidate(image: str, sha: str) -> tuple[str, str, dict[str, int]]:
    before = _service_json()
    before_created = str(((before.get("status") or {}).get("latestCreatedRevisionName") or ""))
    previous_traffic = _traffic_allocations(before)
    if not previous_traffic or sum(previous_traffic.values()) != 100:
        raise RuntimeError(f"no exact 100% serving traffic map to protect: {previous_traffic}")
    print("PREVIOUS_TRAFFIC", json.dumps(previous_traffic, sort_keys=True))

    cmd = [
        "gcloud", "run", "deploy", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", f"--image={image}",
        f"--service-account={RUNTIME_SA}", "--port=8080",
        # Dhan Quote APIs are account-limited to one request/second and the
        # current single-flight/cache is process-local. Keep one serving
        # instance until a tested distributed broker-data governor replaces it.
        "--no-traffic", f"--tag={CANDIDATE_TAG}", "--min=1", "--max=1",
        "--memory=1Gi", "--cpu=1", "--concurrency=50", "--timeout=300",
        "--allow-unauthenticated", f"--update-env-vars={_env_arg(sha)}",
        "--remove-secrets=API_KEY,DHAN_PIN,DHAN_TOTP_SECRET,DHAN_TOTP",
        f"--update-secrets=WORKER_PUSH_TOKEN={WORKER_PUSH_TOKEN_SECRET_ID}:latest",
        "--quiet",
    ]

    deploy_error: subprocess.CalledProcessError | None = None
    try:
        _run(cmd, capture=True)
    except subprocess.CalledProcessError as exc:
        deploy_error = exc

    service = _service_json()
    candidate = _candidate_created_after(service, before_created)
    current_traffic = _traffic_allocations(service)

    # --no-traffic is an invariant, not an assumption. If Cloud Run traffic ever
    # drifts during candidate creation, restore the exact previous allocation.
    if current_traffic != previous_traffic:
        print(
            "CANDIDATE_TRAFFIC_DRIFT",
            json.dumps({"before": previous_traffic, "after": current_traffic}, sort_keys=True),
        )
        _restore_traffic(previous_traffic)
        current_traffic = _traffic_allocations(_service_json())

    if not candidate:
        if deploy_error:
            raise deploy_error
        raise RuntimeError("new candidate revision was not identified")

    try:
        revision = _wait_revision_ready(candidate)
        _assert_candidate_image(revision, image)
    except Exception:
        print("CANDIDATE_DEPLOY_FAILED", candidate)
        _run_failed_revision_forensic(candidate)
        _preserve_previous_ready(previous_traffic)
        raise

    # A nonzero gcloud exit can race with revision reconciliation. The exact
    # immutable revision Ready condition above is the authority; if it became
    # Ready and still has 0% traffic, continue to tagged HTTP proof.
    if deploy_error:
        print("GCLOUD_DEPLOY_NONZERO_BUT_EXACT_REVISION_READY", candidate)

    service = _service_json()
    if _traffic_percent(service, candidate) != 0:
        _restore_traffic(previous_traffic)
        raise RuntimeError(f"candidate unexpectedly has production traffic before proof: {candidate}")

    url = _candidate_url(service, candidate)
    print("CANDIDATE", candidate)
    print("CANDIDATE_URL", url)
    print("CANDIDATE_TRAFFIC", "0%")

    try:
        health = _http_json(f"{url}/api/health")
        if not isinstance(health, dict):
            raise RuntimeError("candidate /api/health did not return JSON object")
        auth = _http_json(f"{url}/api/auth/status")
        if auth.get("required") is not False:
            raise RuntimeError(f"candidate auth/read-only proof failed: {auth}")
        state = _http_json(f"{url}/api/state")
        if not isinstance(state, dict):
            raise RuntimeError("candidate /api/state did not return JSON object")
        broker = _http_json(f"{url}/api/broker/status")
        if broker.get("live_trading_enabled") is not False or broker.get("order_placement_allowed") is not False:
            raise RuntimeError("candidate broker safety proof failed")
    except Exception:
        print("CANDIDATE_DEPLOY_FAILED", candidate)
        _run_failed_revision_forensic(candidate)
        _preserve_previous_ready(previous_traffic)
        raise

    print("CANDIDATE_HTTP_PROOF_OK", candidate)

    # Promote the exact tested immutable revision, never a floating latest tag.
    _run(
        [
            "gcloud", "run", "services", "update-traffic", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}", f"--to-revisions={candidate}=100", "--quiet",
        ],
        capture=True,
    )

    promoted = _service_json()
    promoted_traffic = _traffic_allocations(promoted)
    if promoted_traffic != {candidate: 100}:
        _restore_traffic(previous_traffic)
        raise RuntimeError(
            f"candidate traffic proof failed: expected={{{candidate!r}: 100}} actual={promoted_traffic}"
        )
    ready_status, ready_reason, ready_message = _ready_condition(_revision_json(candidate))
    if ready_status != "True":
        _restore_traffic(previous_traffic)
        raise RuntimeError(
            f"promoted revision lost Ready state: {candidate} {ready_status} {ready_reason} {ready_message}"
        )

    print("PROMOTED_TRAFFIC", json.dumps(promoted_traffic, sort_keys=True))
    # Keep the candidate tag for the *next* zero-traffic proof, but do not
    # leave 100% production traffic labeled as a candidate.
    try:
        _run(
            [
                "gcloud", "run", "services", "update-traffic", SERVICE,
                f"--project={PROJECT}", f"--region={REGION}",
                "--remove-tags=candidate", "--quiet",
            ],
            capture=True,
        )
        print("PRODUCTION_CANDIDATE_TAG_REMOVED", candidate)
    except Exception as exc:
        print("PRODUCTION_CANDIDATE_TAG_REMOVE_SKIPPED", type(exc).__name__)
    return candidate, url, previous_traffic


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
    print("DEPLOYMENT_MODEL candidate-no-traffic-exact-ready-http-proof-explicit-promotion")
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

    candidate, candidate_url, previous_traffic = _deploy_candidate(image, sha)
    print("READY", candidate)
    print("PREVIOUS_TRAFFIC_RETAINED_FOR_ROLLBACK", json.dumps(previous_traffic, sort_keys=True))
    print("CANDIDATE_URL", candidate_url)
    print("IMAGE", image)
    print(
        json.dumps(
            {
                "ok": True,
                "revision": candidate,
                "previous_traffic": previous_traffic,
                "image": image,
                "sha": sha,
                "traffic_percent": 100,
                "live_trading_enabled": False,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
