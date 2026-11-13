"""Fail-closed source preflight for the canonical Genesis Cloud Run image.

This gate intentionally uses only the Python standard library. It validates the
build context BEFORE Docker builds and never reads secrets or contacts a broker.
The source-based miniature FastAPI deployment of 2026-11-01 fails this gate.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

REQUIRED_FILES = (
    "dashboard/backend/app.py",
    "dashboard/backend/Dockerfile",
    "dashboard/frontend/package.json",
    "dashboard/frontend/src/components/Sidebar.tsx",
    "scripts/start_cloud_run.py",
    "scripts/cloud_run_build_metadata_gate.py",
    "AGENTS.md",
    "GEMINI.md",
)
REQUIRED_ROUTES = frozenset(
    ("/api/health", "/api/healthz", "/api/broker/status", "/api/batch/market-data")
)
MIN_BACKEND_BYTES = 50_000


def _route_paths(source: str) -> set[str]:
    tree = ast.parse(source)
    paths: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and decorator.func.attr in ("get", "post", "put", "delete")
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
                and isinstance(decorator.args[0].value, str)
            ):
                paths.add(decorator.args[0].value)
    return paths


def verify_source(root: Path, *, minimum_backend_bytes: int = MIN_BACKEND_BYTES) -> dict:
    root = root.resolve()
    missing = sorted(p for p in REQUIRED_FILES if not (root / p).is_file())
    if missing:
        raise ValueError("Missing required canonical source files: " + ", ".join(missing))

    backend_file = root / "dashboard/backend/app.py"
    backend = backend_file.read_text(encoding="utf-8-sig")
    backend_size = backend_file.stat().st_size
    if backend_size < minimum_backend_bytes:
        raise ValueError(
            f"Backend unexpectedly small: {backend_size} bytes; "
            f"required at least {minimum_backend_bytes}"
        )

    declared_routes = _route_paths(backend)
    missing_routes = sorted(REQUIRED_ROUTES - declared_routes)
    if missing_routes:
        raise ValueError("Missing required backend routes: " + ", ".join(missing_routes))

    docker_file = root / "dashboard/backend/Dockerfile"
    docker_source = docker_file.read_text(encoding="utf-8")
    if "scripts/start_cloud_run.py" not in docker_source or "EXPOSE 8080" not in docker_source:
        raise ValueError("Canonical Cloud Run Dockerfile/launcher contract missing")
    build_config = root / "cloudbuild.yaml"
    if not build_config.is_file():
        raise ValueError("Canonical immutable Cloud Build config missing")
    build_source = build_config.read_text(encoding="utf-8")
    if (
        "--file=dashboard/backend/Dockerfile" not in build_source
        or "--build-arg=DEPLOY_GIT_SHA=${_GIT_SHA}" not in build_source
        or "${_IMAGE}:${_GIT_SHA}" not in build_source
        or "scripts/cloud_run_build_metadata_gate.py" not in build_source
        or "cloud-run-source-deploy/genesis-system3-web" not in build_source
    ):
        raise ValueError("Cloud Build must select canonical Dockerfile and immutable SHA image")
    if "ARG DEPLOY_GIT_SHA" not in docker_source or "ENV DEPLOY_GIT_SHA=${DEPLOY_GIT_SHA}" not in docker_source:
        raise ValueError("Canonical Cloud Run image must expose exact source SHA")
    safety_contract = (
        "PAPER_MODE=1", "ANALYZE_MODE=1", "LIVE_ORDER_AUTHORITY=0",
        "REAL_BROKER_ORDERS=0", "LIVE_TRADING_ENABLED=0", "ORDER_PLACEMENT_ALLOWED=false",
    )
    if any(flag not in docker_source for flag in safety_contract):
        raise ValueError("Canonical Cloud Run image must lock PAPER mode and disable broker orders")

    return {
        "status": "PASS",
        "canonical_dockerfile": "dashboard/backend/Dockerfile",
        "canonical_build_config": "cloudbuild.yaml",
        "build_metadata_gate": "scripts/cloud_run_build_metadata_gate.py",
        "required_routes": sorted(REQUIRED_ROUTES),
        "backend_bytes": backend_size,
        "backend_sha256": hashlib.sha256(backend_file.read_bytes()).hexdigest(),
        "dockerfile_sha256": hashlib.sha256(docker_file.read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        result = verify_source(args.root)
    except (OSError, SyntaxError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
