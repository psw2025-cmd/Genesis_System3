from pathlib import Path


def test_vite_preview_defaults_to_local_api_not_production_alias():
    config = (Path(__file__).resolve().parents[1] / "dashboard" / "frontend" / "vite.config.ts").read_text(encoding="utf-8")

    preview_config = config.split("preview:", 1)[1]
    assert "process.env.DEV_PROXY_TARGET || 'http://127.0.0.1:8000'" in preview_config
    assert "genesis-system3-web-doq2wplepa-el.a.run.app" not in preview_config
    legacy_alias_proxy = "^/(genesis-production-brief|autonomous-brain|hidden-secrets-lab|never-die-monitor|hunger-meter|data-truth-score|health|final-message)$"
    assert config.count(legacy_alias_proxy) == 2
