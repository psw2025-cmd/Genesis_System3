from pathlib import Path


TRACKER = Path("tools/dashboard_visible_issue_tracker.mjs")


def test_visible_issue_tracker_has_no_retired_dashboard_credential_or_session_authority():
    text = TRACKER.read_text(encoding="utf-8")
    retired = [
        "DASHBOARD_" + "API_KEY",
        "X-" + "API-Key",
        "/api/auth/" + "session",
        "credentials: 'include'",
        "extraHTTPHeaders",
    ]
    for marker in retired:
        assert marker not in text, marker


def test_visible_issue_tracker_requires_exact_public_readonly_contract():
    text = TRACKER.read_text(encoding="utf-8")
    for marker in (
        "/api/auth/status",
        "public_readonly",
        "credential_surface",
        "REMOVED",
        "payload.required === false",
        "payload.configured === false",
        "payload.authenticated === false",
        "payload.session === null",
        "credentials: 'omit'",
    ):
        assert marker in text, marker


def test_visible_issue_tracker_keeps_permanent_readonly_sentinels_and_no_order_calls():
    text = TRACKER.read_text(encoding="utf-8")
    assert "'/api/health'" in text
    assert "'/api/broker/status'" in text
    assert "browser_credentials_sent: false" in text
    assert "browser_mutations_called: false" in text
    assert "order_endpoints_called: false" in text
    for marker in ("/orders/place", "/orders/modify", "/orders/cancel", "/api/order"):
        assert marker not in text
