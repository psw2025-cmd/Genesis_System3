"""Batch slim broker status must retain safe token_proof for System tab."""

from dashboard.backend.app import _slim_broker_status, _slim_token_proof


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
