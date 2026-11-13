"""Regression checks for Cloud Run full-source deployment preflight."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "scripts" / "cloud_run_source_integrity_gate.py"
spec = importlib.util.spec_from_file_location("cloud_source_guard", FILE)
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def _make_minimal_canonical_tree(root: Path, *, routes: tuple[str, ...]) -> None:
    for rel in guard.REQUIRED_FILES:
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("placeholder\n", encoding="utf-8")
    app_file = root / "dashboard/backend/app.py"
    app_file.write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n"
        + "".join(f'@app.get("{p}")\ndef route_{i}():\n    return {{}}\n' for i, p in enumerate(routes)),
        encoding="utf-8",
    )
    (root / "dashboard/backend/Dockerfile").write_text(
        'FROM python:3.11-slim\nARG DEPLOY_GIT_SHA=unknown\nENV DEPLOY_GIT_SHA=${DEPLOY_GIT_SHA}\n'
        'ENV PAPER_MODE=1 ANALYZE_MODE=1 LIVE_ORDER_AUTHORITY=0 REAL_BROKER_ORDERS=0 '
        'LIVE_TRADING_ENABLED=0 ORDER_PLACEMENT_ALLOWED=false\nEXPOSE 8080\n'
        'CMD ["python", "scripts/start_cloud_run.py"]\n',
        encoding="utf-8",
    )
    (root / "cloudbuild.yaml").write_text(
        "steps:\n  - args:\n      - --file=dashboard/backend/Dockerfile\n"
        "      - --build-arg=DEPLOY_GIT_SHA=${_GIT_SHA}\n      - --tag=${_IMAGE}:${_GIT_SHA}\n"
        "      - scripts/cloud_run_build_metadata_gate.py\n"
        "      - asia-south1-docker.pkg.dev/system3-openalgo-safe/cloud-run-source-deploy/genesis-system3-web\n",
        encoding="utf-8",
    )


def test_current_main_has_canonical_source_and_routes():
    assert guard.verify_source(ROOT)["status"] == "PASS"


def test_rejects_miniature_source_upload(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.11\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("from fastapi import FastAPI\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required canonical source files"):
        guard.verify_source(tmp_path)


def test_rejects_missing_broker_route(tmp_path):
    _make_minimal_canonical_tree(tmp_path, routes=("/api/health", "/api/batch/market-data"))
    with pytest.raises(ValueError, match="/api/broker/status"):
        guard.verify_source(tmp_path, minimum_backend_bytes=0)


def test_rejects_missing_uptime_healthz_route(tmp_path):
    _make_minimal_canonical_tree(
        tmp_path,
        routes=tuple(sorted(guard.REQUIRED_ROUTES - {"/api/healthz"})),
    )
    with pytest.raises(ValueError, match="/api/healthz"):
        guard.verify_source(tmp_path, minimum_backend_bytes=0)


def test_rejects_wrong_docker_entrypoint(tmp_path):
    _make_minimal_canonical_tree(tmp_path, routes=tuple(sorted(guard.REQUIRED_ROUTES)))
    (tmp_path / "dashboard/backend/Dockerfile").write_text(
        'FROM python:3.11\nARG DEPLOY_GIT_SHA=unknown\nENV DEPLOY_GIT_SHA=${DEPLOY_GIT_SHA}\n'
        'ENV PAPER_MODE=1 ANALYZE_MODE=1 LIVE_ORDER_AUTHORITY=0 REAL_BROKER_ORDERS=0 '
        'LIVE_TRADING_ENABLED=0 ORDER_PLACEMENT_ALLOWED=false\nEXPOSE 8080\n'
        'CMD ["uvicorn", "main:app"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Dockerfile/launcher"):
        guard.verify_source(tmp_path, minimum_backend_bytes=0)


def test_accepts_complete_fixture(tmp_path):
    _make_minimal_canonical_tree(tmp_path, routes=tuple(sorted(guard.REQUIRED_ROUTES)))
    actual = guard.verify_source(tmp_path, minimum_backend_bytes=0)
    assert actual["required_routes"] == sorted(guard.REQUIRED_ROUTES)
    assert actual["canonical_build_config"] == "cloudbuild.yaml"
    assert actual["build_metadata_gate"] == "scripts/cloud_run_build_metadata_gate.py"
    assert len(actual["backend_sha256"]) == 64
