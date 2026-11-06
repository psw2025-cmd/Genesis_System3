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
        'FROM python:3.11-slim\nEXPOSE 8080\nCMD ["python", "scripts/start_cloud_run.py"]\n',
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


def test_rejects_wrong_docker_entrypoint(tmp_path):
    _make_minimal_canonical_tree(tmp_path, routes=tuple(sorted(guard.REQUIRED_ROUTES)))
    (tmp_path / "dashboard/backend/Dockerfile").write_text(
        'FROM python:3.11\nEXPOSE 8080\nCMD ["uvicorn", "main:app"]\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Dockerfile/launcher"):
        guard.verify_source(tmp_path, minimum_backend_bytes=0)


def test_accepts_complete_fixture(tmp_path):
    _make_minimal_canonical_tree(tmp_path, routes=tuple(sorted(guard.REQUIRED_ROUTES)))
    actual = guard.verify_source(tmp_path, minimum_backend_bytes=0)
    assert actual["required_routes"] == sorted(guard.REQUIRED_ROUTES)
    assert len(actual["backend_sha256"]) == 64
