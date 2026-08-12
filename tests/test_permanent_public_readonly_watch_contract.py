from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "tools" / "permanent_live_log_watch.mjs"


def _text() -> str:
    return WATCH.read_text(encoding="utf-8")


def test_permanent_watch_has_no_retired_dashboard_auth_authority():
    text = _text()
    retired = (
        "DASHBOARD_API_KEY",
        "X-API-Key",
        "/api/auth/session",
        "DASHBOARD_API_KEY_SECRET_MISSING",
        "AUTH_FAIL:",
    )
    for marker in retired:
        assert marker not in text, marker


def test_permanent_watch_proves_public_readonly_contract_and_sentinels():
    text = _text()
    required = (
        "/api/auth/status",
        "public_readonly",
        "credential_surface",
        "REMOVED",
        "/api/health",
        "/api/broker/status",
        "credentials: 'omit'",
        "method: 'GET'",
    )
    for marker in required:
        assert marker in text, marker


def test_permanent_watch_never_mentions_order_mutation_routes():
    text = _text().lower()
    forbidden = (
        "/api/order/place",
        "/api/orders/place",
        "/api/order/modify",
        "/api/orders/modify",
        "/api/order/cancel",
        "/api/orders/cancel",
    )
    for marker in forbidden:
        assert marker not in text, marker
