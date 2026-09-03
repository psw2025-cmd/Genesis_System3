from core.config.cloud_runtime import (
    deploy_target,
    is_cloud_runtime,
    public_base_url,
    public_cors_origins,
    public_dashboard_url,
    public_ui_path,
)

LOCAL = "http://127.0.0.1:8000"


def test_public_base_url_prefers_system3_env(monkeypatch):
    monkeypatch.setenv("SYSTEM3_PUBLIC_BACKEND_URL", LOCAL)
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    assert public_base_url() == LOCAL
    assert public_dashboard_url() == f"{LOCAL}/ui"
    assert public_ui_path() == "/ui"


def test_public_base_url_reads_legacy_public_backend_url(monkeypatch):
    monkeypatch.delenv("K_SERVICE", raising=False)
    monkeypatch.delenv("SYSTEM3_DEPLOY_TARGET", raising=False)
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "https://example.invalid")
    assert public_base_url() == "https://example.invalid"


def test_local_defaults_use_loopback(monkeypatch):
    monkeypatch.delenv("K_SERVICE", raising=False)
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_DEPLOY_TARGET", raising=False)
    assert public_base_url() == LOCAL
    assert public_dashboard_url() == f"{LOCAL}/ui"
    assert deploy_target() == "local-laptop"
    assert is_cloud_runtime() is False


def test_cloud_run_is_detected_only_from_runtime_service_env(monkeypatch):
    cloud = "https://example.invalid"
    monkeypatch.setenv("K_SERVICE", "genesis-system3-web")
    monkeypatch.setenv("SYSTEM3_PUBLIC_BACKEND_URL", cloud)
    monkeypatch.setenv("PUBLIC_DASHBOARD_URL", f"{cloud}/ui")
    assert is_cloud_runtime() is True
    assert public_base_url() == cloud
    assert public_dashboard_url() == f"{cloud}/ui"


def test_public_cors_origins_skip_loopback_defaults(monkeypatch):
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    monkeypatch.delenv("K_SERVICE", raising=False)
    origins = public_cors_origins()
    assert origins == []


def test_local_dev_still_allows_loopback_without_cloud_mode(monkeypatch):
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("PUBLIC_DASHBOARD_URL", "http://127.0.0.1:8000/ui")
    monkeypatch.delenv("K_SERVICE", raising=False)
    monkeypatch.setenv("SYSTEM3_DEPLOY_TARGET", "local-laptop")
    monkeypatch.delenv("SYSTEM3_PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("SYSTEM3_API_BASE", raising=False)
    monkeypatch.delenv("DASHBOARD_BASE_URL", raising=False)
    assert public_base_url() == "http://127.0.0.1:8000"
    assert public_dashboard_url() == "http://127.0.0.1:8000/ui"
