"""Lock local-laptop multi-agent safety into agent_policy.yaml v6.

v5 Claude-only / Issue-#188-bus / GCP-target schema is superseded by
docs/control_plane/LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md. Trading locks remain
fail-closed.
"""

from copy import deepcopy
from pathlib import Path

import json

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md"
AUTHORITY_DOC = ROOT / "docs" / "control_plane" / "CLAUDE_SINGLE_EXECUTION_AUTHORITY.md"
LOCAL_DIRECTIVE = ROOT / "docs" / "control_plane" / "LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md"


def _load_policy_and_schema():
    policy_path = ROOT / "agent_policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    schema_path = ROOT / policy["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return policy, schema


def test_claude_single_execution_authority_is_historical_and_keeps_safety_locks():
    text = AUTHORITY_DOC.read_text(encoding="utf-8")
    assert "SYSTEM3_CLAUDE_SINGLE_EXECUTION_AUTHORITY" in text
    assert "HISTORICAL_NON_AUTHORITY" in text
    for lock in (
        "ANALYZE_MODE=1",
        "LIVE_TRADING_ENABLED=0",
        "SYSTEM3_LIVE_TRADING_ALLOWED=0",
        "AUTO_EXECUTE_TRADES=0",
        "zero real broker orders",
        "no broker secret payload exposure",
    ):
        assert lock in text


def test_local_laptop_directive_is_active():
    text = LOCAL_DIRECTIVE.read_text(encoding="utf-8")
    assert "local Windows laptop" in text
    assert "GCP" in text
    assert "LIVE_TRADING_ENABLED=0" in text


def test_runbook_still_declares_core_persistent_reread_and_safety_contract():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1" in text
    for boundary in (
        "every merge decision",
        "every deployment or production mutation",
        "every issue/blocker closure",
        "every final response",
    ):
        assert boundary in text
    assert "Chat memory" in text
    assert "LIVE_TRADING_ENABLED=0" in text
    assert "AUTO_EXECUTE_TRADES=0" in text
    assert "docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md" in text
    assert (ROOT / "scripts" / "system3_proof_ledger.py").exists()


def test_agent_policy_validates_against_canonical_versioned_schema():
    policy, schema = _load_policy_and_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=policy, schema=schema)
    assert policy["version"] == policy["schema_version"] == 6

    prior_major = deepcopy(policy)
    prior_major["version"] = prior_major["schema_version"] = 5
    validator = jsonschema.Draft202012Validator(schema)
    assert list(validator.iter_errors(prior_major)), "v5 requires an explicit migration"


def test_execution_authority_is_multi_agent_local():
    policy, schema = _load_policy_and_schema()
    validator = jsonschema.Draft202012Validator(schema)

    assert policy["execution_authority"]["sole_controller"] == "none"
    assert policy["execution_authority"]["claude_only_ownership"] is False
    assert policy["execution_authority"]["mandatory_issue_188"] is False
    assert policy["coordination"]["github_issue_188_is_live_bus"] is False
    assert policy["runtime"]["gcp_runtime_authority"] is False
    assert str(policy.get("target_url", "")).startswith("http://127.0.0.1")

    candidate = deepcopy(policy)
    candidate["execution_authority"]["claude_only_ownership"] = True
    assert list(validator.iter_errors(candidate)), "schema accepted Claude-only ownership"


def test_trading_safety_invariants_are_schema_enforced_fail_closed():
    policy, schema = _load_policy_and_schema()
    validator = jsonschema.Draft202012Validator(schema)

    unsafe_mutations = (
        ("safety", "live_trading_enabled", True),
        ("safety", "system3_live_trading_allowed", True),
        ("safety", "auto_execute_trades", True),
        ("safety", "real_order_count_required", 1),
        ("safety", "real_order_placement_modification_cancellation_squareoff", "allowed"),
        ("safety", "broker_secret_payload_exposure", "allowed"),
        ("safety", "service_account_json_keys", "allowed"),
        ("safety", "live_enablement_requires_human_break_glass", False),
        ("coordination", "parallel_overlapping_mutation", "allowed"),
        ("completion", "stop_at_code_or_pr_or_ci", True),
    )
    for section, key, unsafe_value in unsafe_mutations:
        candidate = deepcopy(policy)
        candidate[section][key] = unsafe_value
        assert list(validator.iter_errors(candidate)), f"schema accepted unsafe {section}.{key}={unsafe_value!r}"


def test_gcp_exit_high_frequency_resume_stays_forbidden():
    policy, _schema = _load_policy_and_schema()
    section = policy.get("gcp_exit_billing_control", {})
    assert section.get("high_frequency_scheduler_resume_without_reconciled_ssot") == "forbidden"
    assert section.get("do_not_execute_gcloud") is True
