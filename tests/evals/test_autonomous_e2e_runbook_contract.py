"""Test active 2026-10-18 cloud-only authority with separate GCP mutation approval.

Retain fail-closed PAPER/ANALYZE safety; September laptop-only and Claude-only
directives are historical. Schema version is preserved for compatible consumers.
"""

from copy import deepcopy
from pathlib import Path
import json

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md"
LEGACY_CLAUDE = ROOT / "docs" / "control_plane" / "CLAUDE_SINGLE_EXECUTION_AUTHORITY.md"
LEGACY_LOCAL = ROOT / "docs" / "control_plane" / "LOCAL_LAPTOP_USER_DIRECTIVE_20260907.md"
ACTIVE_OWNER = ROOT / "docs" / "authority" / "CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md"


def _load_policy_and_schema():
    policy = yaml.safe_load((ROOT / "agent_policy.yaml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / policy["schema_path"]).read_text(encoding="utf-8"))
    return policy, schema


def test_legacy_directives_are_retained_but_explicitly_non_authoritative():
    local = LEGACY_LOCAL.read_text(encoding="utf-8")
    claude = LEGACY_CLAUDE.read_text(encoding="utf-8")
    assert "HISTORICAL_NON_AUTHORITY" in local
    assert "CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md" in local
    assert "local Windows laptop" in local  # historical text kept for forensics
    assert "SYSTEM3_CLAUDE_SINGLE_EXECUTION_AUTHORITY" in claude
    assert "HISTORICAL_NON_AUTHORITY" in claude


def test_owner_directive_limits_authorization_and_live_trading():
    text = ACTIVE_OWNER.read_text(encoding="utf-8")
    assert "SYSTEM3_CLOUD_ONLY_OWNER_DIRECTIVE_20261018" in text
    assert "read-only GCP verification only" in text
    assert "separate explicit owner approval" in text
    for lock in (
        "ANALYZE_MODE=1", "PAPER_MODE=1", "LIVE_TRADING_ENABLED=0",
        "SYSTEM3_LIVE_TRADING_ALLOWED=0", "AUTO_EXECUTE_TRADES=0",
        "LIVE_ORDER_AUTHORITY=0", "ORDER_PLACEMENT_ALLOWED=false",
    ):
        assert lock in text


def test_runbook_preserves_fresh_read_and_safety_contract():
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1" in text
    assert "CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md" in text
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


def test_machine_policy_validates_against_versioned_schema_and_prior_major_fails():
    policy, schema = _load_policy_and_schema()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=policy, schema=schema)
    assert policy["version"] == policy["schema_version"] == 6
    prior_major = deepcopy(policy)
    prior_major["version"] = prior_major["schema_version"] = 5
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(prior_major))


def test_current_authority_cloud_only_and_non_mutating():
    policy, schema = _load_policy_and_schema()
    validate = jsonschema.Draft202012Validator(schema)
    assert policy["execution_authority"]["sole_controller"] == "none"
    assert policy["execution_authority"]["claude_only_ownership"] is False
    assert policy["execution_authority"]["mandatory_issue_188"] is False
    assert policy["coordination"]["github_issue_188_is_live_bus"] is False
    assert policy["runtime"]["authority"] == "gcp_managed_cloud_target"
    assert policy["runtime"]["gcp_runtime_authority"] is True
    assert policy["runtime"]["cloudrun_acceptance_authority"] is True
    assert policy["runtime"]["local_runtime_required"] is False
    assert policy["runtime"]["cloud_mutation_allowed_without_owner_approval"] is False
    assert policy["gcp_exit_billing_control"]["do_not_execute_gcloud"] is False
    assert policy["gcp_exit_billing_control"]["do_not_deploy_cloud_run"] is True
    assert policy["gcp_exit_billing_control"]["owner_approval_before_cloud_mutation"] is True
    assert str(policy["target_url"]).startswith("https://genesis-system3-web-")
    assert "CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md" in policy["execution_authority"]["authority_doc"]
    for section, key, illegal in (
        ("runtime", "authority", "local_windows_laptop"),
        ("runtime", "local_runtime_required", True),
        ("runtime", "cloud_mutation_allowed_without_owner_approval", True),
        ("gcp_exit_billing_control", "do_not_deploy_cloud_run", False),
        ("gcp_exit_billing_control", "owner_approval_before_cloud_mutation", False),
    ):
        candidate = deepcopy(policy)
        candidate[section][key] = illegal
        assert list(validate.iter_errors(candidate)), (section, key)


def test_trading_and_other_safety_invariants_fail_closed():
    policy, schema = _load_policy_and_schema()
    validate = jsonschema.Draft202012Validator(schema)
    unsafe = (
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
        ("execution_authority", "claude_only_ownership", True),
    )
    for section, key, illegal in unsafe:
        candidate = deepcopy(policy)
        candidate[section][key] = illegal
        assert list(validate.iter_errors(candidate)), (section, key)
