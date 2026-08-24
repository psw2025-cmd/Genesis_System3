from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "docs" / "authority" / "USER_ACTION_AUTONOMY_SPEED_POLICY.md"
MATRIX = ROOT / "docs" / "authority" / "RUHI_19_POINT_FAILURE_MATRIX.md"
AGENTS = ROOT / "AGENTS.md"
OPS = ROOT / "docs" / "authority" / "AUTONOMOUS_OPERATIONS_POLICY.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_user_action_policy_has_exactly_19_self_mri_checks():
    text = _text(POLICY)
    section = text.split("## Mandatory 19-point self-MRI before saying USER_ACTION=NONE", 1)[1]
    section = section.split("## Kid-level user guidance contract", 1)[0]
    checks = re.findall(r"(?m)^(\d+)\. ", section)
    assert checks == [str(i) for i in range(1, 20)]


def test_user_action_policy_preserves_mandatory_vs_acceleration_split():
    text = _text(POLICY)
    assert "MANDATORY_USER_ACTION=" in text
    assert "OPTIONAL_ACCELERATION_ACTION=" in text
    assert "HUMAN_ACTION_REQUIRED=NO" in text
    assert "does **not** permit `USER_ACTION=NONE`" in text


def test_kid_level_guidance_contract_is_complete():
    text = _text(POLICY)
    for marker in ["WHY:", "WHERE:", "CLICK:", "SET:", "DO NOT:", "RESULT:", "PROOF:", "URGENCY:"]:
        assert marker in text


def test_failure_matrix_has_exactly_19_rows_and_live_dashboard_truth_gate():
    text = _text(MATRIX)
    rows = re.findall(r"(?m)^\| (\d+) \|", text)
    assert rows == [str(i) for i in range(1, 20)]
    assert "Final truth is the current GCP-hosted dashboard" in text
    assert "LIVE_DASHBOARD_PROOF=" in text
    assert "No agent may claim final completion while `LIVE_DASHBOARD_PROOF=UNPROVEN`" in text


def test_failure_matrix_requires_agent_owned_action_and_highest_gain_next_action():
    text = _text(MATRIX)
    assert "AGENT_OWNED_ACTION=" in text
    assert "HIGHEST_GAIN_NEXT_ACTION=" in text
    assert "highest-gain" in text.lower()


def test_global_agent_contract_and_ops_policy_reference_speed_policy():
    policy_name = "USER_ACTION_AUTONOMY_SPEED_POLICY.md"
    assert policy_name in _text(AGENTS)
    assert policy_name in _text(OPS)


def test_global_contract_keeps_live_ui_semantic_truth_and_paper_safety():
    text = _text(AGENTS)
    assert "full UI audit capture all 22 canonical tabs" in text
    assert "HTTP 200 or “tab rendered” does not prove populated/semantically correct market data" in text
    assert "LIVE_TRADING_ENABLED=0" in text
    assert "AUTO_EXECUTE_TRADES=0" in text


def test_speed_policy_requires_exact_user_run_and_cross_verify_loop():
    text = _text(POLICY)
    for marker in [
        "USER_RUN_FILE_OR_COMMAND=",
        "RETURN_THIS_EVIDENCE=",
        "CROSS_VERIFY_RESULT=",
        "ONLY_REMAINING_USER_CORRECTION=",
        "AGENT_CONTINUES_WITH=",
        "Repeat this verify-correct-reverify loop",
        "do not make the user rerun already-PASS checks",
        "#RUHI #RUHI2",
    ]:
        assert marker in text


def test_speed_policy_does_not_weaken_safety_or_allow_failed_check_bypass():
    text = _text(POLICY)
    for forbidden_safety in [
        "LIVE trading",
        "real order placement/modification/cancellation",
        "service-account JSON keys",
        "bypassing failed mandatory checks",
    ]:
        assert forbidden_safety in text
