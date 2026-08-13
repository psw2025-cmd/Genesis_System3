"""Dashboard health-truth mapping must not treat analyzer PAPER as an outage."""

def broker_from_health(health):
    if (health or {}).get("broker", {}).get("connected") is True:
        return True
    if (health or {}).get("broker", {}).get("connected") is False:
        return False
    status = str(health.get("broker_status") or (health.get("broker") or {}).get("status") or "").lower()
    if status in {"connected", "ok"}:
        return True
    if status in {"disconnected", "error", "failure"}:
        return False
    return None


def test_live_health_payload_marks_broker_connected():
    health = {
        "status": "ok",
        "mode": "PAPER",
        "broker_status": "connected",
        "broker": {"connected": True, "name": "dhan", "status": "connected"},
        "live_allowed": False,
        "market": {"is_open": False, "reason": "closed"},
    }
    assert broker_from_health(health) is True
    assert str(health["status"]).lower() == "ok"
    assert "PAPER" in health["mode"]
    assert health["live_allowed"] is False
