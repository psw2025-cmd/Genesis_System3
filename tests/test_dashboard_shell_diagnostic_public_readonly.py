from pathlib import Path


DIAGNOSTIC = Path("tools/dashboard_shell_diagnostic.mjs")


def test_shell_diagnostic_has_no_retired_dashboard_credential_or_session_authority():
    text = DIAGNOSTIC.read_text(encoding="utf-8")
    for marker in (
        "DASHBOARD_" + "API_KEY",
        "X-" + "API-Key",
        "/api/auth/" + "session",
        "credentials: 'include'",
        "extraHTTPHeaders",
        "renderAuthenticatedShellWithRecovery",
        "authenticated_dashboard_rendered",
    ):
        assert marker not in text, marker


def test_shell_diagnostic_requires_exact_public_readonly_contract_and_sentinels():
    text = DIAGNOSTIC.read_text(encoding="utf-8")
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
        "'/api/health'",
        "'/api/broker/status'",
    ):
        assert marker in text, marker


def test_shell_diagnostic_records_zero_credential_mutation_and_order_activity():
    text = DIAGNOSTIC.read_text(encoding="utf-8")
    assert "browser_credentials_sent: false" in text
    assert "browser_mutations_called: false" in text
    assert "order_routes_called: false" in text
    for marker in ("/orders/place", "/orders/modify", "/orders/cancel", "/api/order"):
        assert marker not in text
