from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_is_public_read_only_and_secret_safe():
    text = (ROOT / "observability/playbooks/synthetic_smoke.js").read_text(encoding="utf-8")

    # Public PAPER dashboard: no login/key flow and no trading/order mutation.
    forbidden = [
        "SYNTH_PASS",
        "SYNTH_USER",
        "input[name=\"password\"]",
        "place-sandbox-order",
        "place_order",
        "modify_order",
        "cancel_order",
        "SANDBOX_ORDER_URL",
        "X-API-Key",
    ]
    for marker in forbidden:
        assert marker not in text

    assert "'/api/auth/status'" in text
    assert "'/api/health'" in text
    assert "'/api/state'" in text
    assert "'/api/security/mutation-policy'" in text
    assert "checks.auth.body.required !== false" in text
    assert "checks.auth.body.mode !== 'auth_disabled'" in text
    assert "checks.mutation.body.live_mutation !== 'HARD_DENY'" in text
    assert "broker_order_called: false" in text
    assert "live_trading_enabled: false" in text

    # Trace correlation is same-origin only and evidence is scrubbed before GCS.
    assert "x-trace-id" in text
    assert "traceparent" in text
    assert "sameOrigin" in text
    assert "scrubHar" in text
    assert "req.cookies = []" in text
    assert "req.queryString = []" in text
    assert "delete req.postData" in text
    assert "delete res.content.text" in text
    assert "request_response_bodies_persisted: false" in text
    assert "cookies_persisted: false" in text
    assert "query_values_persisted: false" in text


def test_synthetic_image_matches_repository_playwright_version():
    dockerfile = (ROOT / "observability/Dockerfile.synthetic").read_text(encoding="utf-8")
    package = (ROOT / "tools/playwright-setup/package.json").read_text(encoding="utf-8")
    assert "@playwright/test\": \"1.52.0" in package
    assert "mcr.microsoft.com/playwright:v1.52.0-noble" in dockerfile
    assert "package-lock.json" in dockerfile


def test_gcs_lifecycle_keeps_hot_evidence_then_cold_archives():
    lifecycle = (ROOT / "observability/gcs_lifecycle.json").read_text(encoding="utf-8")
    assert '"SetStorageClass"' in lifecycle
    assert '"COLDLINE"' in lifecycle
    assert '"age": 30' in lifecycle
    assert '"Delete"' in lifecycle
    assert '"age": 180' in lifecycle
