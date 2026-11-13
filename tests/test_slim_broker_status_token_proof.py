"""Broker status must report only observed token facts and never expose IDs."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from dashboard.backend.app import (
    _enrich_broker_status,
    _redact_public_credentials,
    _slim_broker_status,
    _slim_token_proof,
)


def test_public_credential_redaction_covers_nested_state_and_preserves_safe_flags():
    public = _redact_public_credentials(
        {
            "broker": {
                "client_id": "private-id",
                "dhanClientId": "private-id",
                "access_token": "private-token",
                "nested": {"Authorization": "Bearer private-token"},
                "access_token_present": True,
            }
        }
    )
    assert public == {"broker": {"nested": {}, "access_token_present": True}}


def test_broker_enrichment_does_not_fabricate_rotation_or_expiry():
    expiry = datetime.now(timezone.utc) + timedelta(hours=2)
    raw_token = "opaque.secret.payload"
    with patch(
        "core.utils.env_loader.get_dhan_token",
        return_value=(raw_token, "GCP_SECRET_MANAGER_V363", "unused-provider", 23.5, expiry, False),
    ):
        status = _enrich_broker_status(
            {"connected": True, "client_id": "private-client-id", "dhanClientId": "private-client-id"}
        )

    proof = status["token_proof"]
    assert proof["source"] == "GCP_SECRET_MANAGER"
    assert proof["secret_version"] == "363"
    assert proof["expires_at_utc"] == expiry.isoformat()
    assert 1.9 < proof["hours_remaining"] <= 2.0
    assert proof["expired"] is False
    assert proof["authenticated"] is True
    assert status["token_reload"] == {"attempted": False, "success": None}
    assert status["canonical_rotation"]["attempted"] is False
    assert status["auto_renew"] is False
    assert status["totp_renew"] is False
    assert all(key not in status for key in ("client_id", "clientId", "dhan_client_id", "dhanClientId"))
    assert raw_token not in repr(status)


def test_broker_enrichment_keeps_expiry_unknown_when_claim_missing():
    with patch(
        "core.utils.env_loader.get_dhan_token",
        return_value=("opaque", "LOCAL_JWT_SESSION_FALLBACK", "unused-provider", 23.5, None, True),
    ):
        status = _enrich_broker_status({"connected": False})
    proof = status["token_proof"]
    assert proof["source"] == "LOCAL_FALLBACK"
    assert proof["expires_at_utc"] is None
    assert proof["hours_remaining"] is None
    assert proof["expired"] is None


def test_slim_token_proof_strips_secrets_and_keeps_provenance():
    proof = _slim_token_proof(
        {
            "source": "GCP_SECRET_MANAGER_DYNAMIC",
            "secret_version": "207",
            "hours_remaining": 23.5,
            "expired": False,
            "loaded_at_utc": "2026-08-14T06:00:00Z",
            "expires_at_utc": "2026-08-15T06:00:00Z",
            "access_token": "SHOULD_NOT_LEAK",
            "token": "SHOULD_NOT_LEAK",
            "token_value_exposed": True,
        }
    )
    assert proof["source"] == "GCP_SECRET_MANAGER_DYNAMIC"
    assert proof["secret_version"] == "207"
    assert proof["token_value_exposed"] is False
    assert "access_token" not in proof
    assert "token" not in proof


def test_slim_broker_status_includes_token_proof_for_system_tab():
    slim = _slim_broker_status(
        {
            "broker": "dhan",
            "connected": True,
            "status": "connected",
            "latency_ms": 42,
            "live_trading_enabled": True,
            "order_placement_allowed": True,
            "token_proof": {
                "source": "GCP_SECRET_MANAGER_DYNAMIC",
                "secret_version": "207",
                "hours_remaining": 12.0,
                "expired": False,
                "last_reload_reason": "scheduled",
                "rotation_schedule": "daily",
            },
            "token_reload": {"attempted": False, "success": None},
            "canonical_rotation": {"state": "OK", "success": True},
        }
    )
    assert slim["connected"] is True
    assert slim["live_trading_enabled"] is False
    assert slim["order_placement_allowed"] is False
    assert slim["token_proof"]["source"] == "GCP_SECRET_MANAGER_DYNAMIC"
    assert slim["token_proof"]["secret_version"] == "207"
    assert slim["token_proof"]["token_value_exposed"] is False
    assert slim["token_reload"]["attempted"] is False
    assert slim["canonical_rotation"]["success"] is True
