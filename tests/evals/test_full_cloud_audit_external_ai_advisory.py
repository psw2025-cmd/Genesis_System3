from pathlib import Path


WORKFLOW = Path('.github/workflows/full-cloud-audit.yml')


def test_external_ai_unavailability_is_not_a_deterministic_runtime_failure():
    text = WORKFLOW.read_text(encoding='utf-8')
    assert "ai_external_unavailable=ai_state == 'BLOCKED_EXTERNAL_AI'" in text
    assert "external_ai_required_for_deterministic_runtime_pass':False" in text
    assert "if not deterministic_pass or ai_adverse_or_invalid:" in text
    assert "evidence_grade='DETERMINISTIC_PASS_EXTERNAL_AI_UNAVAILABLE'" in text


def test_deterministic_and_configured_ai_failures_remain_fail_closed():
    text = WORKFLOW.read_text(encoding='utf-8')
    for required in (
        "'cloud_audit_pass': cloud.get('state') == 'PASS'",
        "'cloud_safety_pass': (cloud.get('safety') or {}).get('state') == 'PASS'",
        "'rotator_reliability_pass': rotator.get('state') == 'PASS'",
        "'security_audit_pass': security.get('state') == 'PASS'",
        "ai_adverse_or_invalid=not ai_consensus_pass and not ai_external_unavailable",
        "overall='FAIL'",
    ):
        assert required in text


def test_live_and_order_safety_remain_locked():
    text = WORKFLOW.read_text(encoding='utf-8')
    assert 'LIVE_TRADING_ENABLED: "0"' in text
    assert 'SYSTEM3_LIVE_TRADING_ALLOWED: "0"' in text
    assert 'AUTO_EXECUTE_TRADES: "0"' in text
    assert "'live_trading_enabled':False" in text
    assert "'order_actions_performed':False" in text
