from dashboard.backend.scheduler_contract import coverage_expectations
from scripts.gcp_control_plane_verify import verify_payload


def healthy_payload():
    expected = coverage_expectations()
    return {
        "healthy": True,
        "live_trading_enabled": False,
        "coverage": {
            "contract_matched": True,
            "total": expected["expected_total"],
            "workload": expected["expected_workload"],
            "control": expected["expected_control"],
            "enabled": expected["expected_enabled"],
            "paused": expected["expected_paused"],
            **expected,
        },
        "observability": {"alert_severity": "none"},
    }


def test_control_plane_verifier_accepts_current_dynamic_contract():
    result = verify_payload(healthy_payload())
    assert result["ok"] is True
    assert result["expected"]["expected_total"] == 10


def test_control_plane_verifier_rejects_old_nine_resource_world():
    payload = healthy_payload()
    payload["coverage"]["total"] = 9
    payload["coverage"]["expected_total"] = 9
    result = verify_payload(payload)
    assert result["ok"] is False
    assert result["checks"]["expected_total"] is False
    assert result["checks"]["total_matches_expected"] is False


def test_control_plane_verifier_rejects_hidden_extra_or_missing_lane():
    payload = healthy_payload()
    payload["coverage"]["contract_matched"] = False
    result = verify_payload(payload)
    assert result["ok"] is False
    assert result["checks"]["contract_matched"] is False
