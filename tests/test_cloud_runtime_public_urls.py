"""Public Cloud Run URL helpers must never advertise localhost in cloud mode."""
import os

from core.config.cloud_runtime import (
    public_base_url,
    public_cors_origins,
    public_dashboard_url,
    public_ui_path,
)

CLOUD = "https://genesis-system3-web-doq2wplepa-el.a.run.app"


def test_public_base_url_prefers_system3_env(monkeypatch):
    monkeypatch.setenv("SYSTEM3_PUBLIC_BACKEND_URL", CLOUD)
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    assert public_base_url() == CLOUD
    assert public_dashboard_url() == f"{CLOUD}/ui"
    assert public_ui_path() == "/ui"


def test_public_base_url_reads_legacy_public_backend_url(monkeypatch):
    monkeypatch.delenv("CLOUD_MODE", raising=False)
    monkeypatch.delenv("SYSTEM3_DEPLOY_TARGET", raising=False)
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "https://example.invalid")
    assert public_base_url() == "https://example.invalid"


def test_cloud_mode_rejects_localhost_override(monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "1")
    monkeypatch.setenv("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run")
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("PUBLIC_DASHBOARD_URL", "http://localhost:3000")
    assert public_base_url() == CLOUD
    assert public_dashboard_url() == f"{CLOUD}/ui"
    assert "127.0.0.1" not in public_base_url()
    assert "localhost" not in public_dashboard_url()


def test_public_cors_origins_include_canonical_and_regional_alias(monkeypatch):
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    origins = public_cors_origins()
    assert CLOUD in origins
    assert "https://genesis-system3-web-802404398783.asia-south1.run.app" in origins
    assert all("127.0.0.1" not in origin and "localhost" not in origin for origin in origins)


def test_local_dev_still_allows_loopback_without_cloud_mode(monkeypatch):
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("PUBLIC_DASHBOARD_URL", "http://127.0.0.1:8000/ui")
    monkeypatch.delenv("CLOUD_MODE", raising=False)
    monkeypatch.delenv("K_SERVICE", raising=False)
    monkeypatch.setenv("SYSTEM3_DEPLOY_TARGET", "local")
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    assert public_base_url() == "http://127.0.0.1:8000"
    assert public_dashboard_url() == "http://127.0.0.1:8000/ui"
