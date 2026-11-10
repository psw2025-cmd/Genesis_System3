from pathlib import Path


PROOF = Path("tools/dashboard_live_ui_proof.mjs")


def test_live_ui_proof_has_no_retired_dashboard_credential_or_session_authority():
    text = PROOF.read_text(encoding="utf-8")
    retired = [
        "DASHBOARD_" + "API_KEY",
        "X-" + "API-Key",
        "/api/auth/" + "session",
        "auth_session.json",
    ]
    for marker in retired:
        assert marker not in text, marker


def test_live_ui_proof_requires_exact_public_readonly_contract():
    text = PROOF.read_text(encoding="utf-8")
    for marker in (
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


def test_live_ui_proof_keeps_permanent_readonly_sentinels_and_no_mutation_calls():
    text = PROOF.read_text(encoding="utf-8")
    assert "'/api/health'" in text
    assert "'/api/broker/status'" in text
    assert "browser_mutations_called: false" in text
    assert "browser_credentials_sent: false" in text
    for marker in ("/orders/place", "/orders/modify", "/orders/cancel", "/api/order"):
        assert marker not in text
