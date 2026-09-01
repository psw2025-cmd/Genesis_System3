"""Lock the Claude-single-execution-authority safety contract into agent_policy.yaml.

Rewritten 2026-09-01 for policy v5 (docs/control_plane/CLAUDE_SINGLE_EXECUTION_AUTHORITY.md).
v4's autonomous_end_to_end_runbook structure and the ~1500-line detailed runbook it validated
were deliberately superseded by a user directive that consolidated execution authority under
Claude and shortened SYSTEM3_AGENT_RUNBOOK.md to reference separate authority docs
(e.g. docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md) instead of duplicating their
detail inline. This file no longer asserts on that removed narrative content; it asserts on
the safety invariants that must survive any policy restructuring, and that the schema fails
closed if any of them are ever weakened.
"""

from copy import deepcopy
from pathlib import Path

import json

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md"
AUTHORITY_DOC = ROOT / "docs" / "control_plane" / "CLAUDE_SINGLE_EXECUTION_AUTHORITY.md"


def _load_policy_and_schema():
    policy_path = ROOT / "agent_policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    schema_path = ROOT / policy["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return policy, schema


def test_claude_single_execution_authority_doc_exists_and_declares_safety_locks():
    text = AUTHORITY_DOC.read_text(encoding="utf-8")
    assert "SYSTEM3_CLAUDE_SINGLE_EXECUTION_AUTHORITY" in text
    assert "Claude is the single execution authority" in text
    for lock in (
        "ANALYZE_MODE=1",
        "LIVE_TRADING_ENABLED=0",
        "SYSTEM3_LIVE_TRADING_ALLOWED=0",
        "AUTO_EXECUTE_TRADES=0",
        "zero real broker orders",
        "no broker secret payload exposure",
    ):
        assert lock in text


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
    # Detailed browser/proof-ledger mechanics now live in a referenced authority
    # doc rather than being duplicated inline; assert the reference survives
    # instead of the literal duplicated string.
    assert "docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md" in text
    assert (ROOT / "scripts" / "system3_proof_ledger.py").exists()


def test_agent_policy_validates_against_canonical_versioned_schema():
    policy, schema = _load_policy_and_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=policy, schema=schema)
    assert policy["version"] == policy["schema_version"] == 5

    prior_major = deepcopy(policy)
    prior_major["version"] = prior_major["schema_version"] = 4
    future_major = deepcopy(policy)
    future_major["version"] = future_major["schema_version"] = 6
    validator = jsonschema.Draft202012Validator(schema)
    assert list(validator.iter_errors(prior_major)), "v4 requires an explicit migration/compatibility reader"
    assert list(validator.iter_errors(future_major)), "unknown future major versions must fail closed"


def test_execution_authority_is_schema_enforced():
    policy, schema = _load_policy_and_schema()
    validator = jsonschema.Draft202012Validator(schema)

    assert policy["execution_authority"]["sole_controller"] == "Claude"
    assert policy["execution_authority"]["other_agents_may_mutate"] is False

    candidate = deepcopy(policy)
    candidate["execution_authority"]["other_agents_may_mutate"] = True
    assert list(validator.iter_errors(candidate)), "schema accepted other agents gaining mutation rights"

    candidate = deepcopy(policy)
    candidate["execution_authority"]["sole_controller"] = "Codex"
    assert list(validator.iter_errors(candidate)), "schema accepted a non-Claude sole controller"


def test_trading_safety_invariants_are_schema_enforced_fail_closed():
    """The single most important property carried over from the v4 contract:
    any attempt to weaken a trading-safety invariant must fail schema validation,
    not merely fail a narrative string check."""
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
    policy, schema = _load_policy_and_schema()
    validator = jsonschema.Draft202012Validator(schema)
    section = policy.get("gcp_exit_billing_control", {})
    assert section.get("high_frequency_scheduler_resume_without_reconciled_ssot") == "forbidden"

    candidate = deepcopy(policy)
    candidate.setdefault("gcp_exit_billing_control", {})["high_frequency_scheduler_resume_without_reconciled_ssot"] = "allowed"
    assert list(validator.iter_errors(candidate)), "schema accepted resuming high-frequency schedulers without reconciliation"
