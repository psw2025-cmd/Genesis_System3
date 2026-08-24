"""Lock the persistent autonomous runbook into every generic-agent entrypoint."""

from pathlib import Path

import json
from copy import deepcopy

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md"


def test_runbook_declares_persistent_reread_and_safety_contract():
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
    assert "scripts/system3_proof_ledger.py" in text
    assert "new Chrome/WebDriver session" in text
    assert "all 22 canonical tabs" in text
    assert "GitHub + Google Cloud + URL + F12 acceptance matrix" in text
    assert "Full data-to-decision lifecycle" in text
    assert "Dhan market and historical data" in text
    assert "CE/PE" in text and "Multibagger" in text
    assert "Desktop dashboard, chart and text contract" in text
    assert "USER_RECOMMDATION_FOR _AGENT_UPDATE_RUNBOOK" in text
    assert "World-class recommendation and user-choice protocol" in text
    assert "Laptop intake -> cloud research/PAPER loop" in text
    assert "Historical validation cannot substitute for forward PAPER evidence" in text
    assert "Never update active champion weights in place" in text
    assert "Git stores code, small schemas, manifests, hashes" in text
    assert "MRI-style coverage" in text
    assert "MRI-level autonomous scan and orchestration protocol" in text
    assert "reports/latest/mri/Concern_List.md" in text
    assert "reports/latest/mri/Concern_List.json" in text
    assert "Report all material concerns, blockers and anomalies" in text
    assert "Canonical MRI flow" in text
    assert "Immediate PAPER Observation" in text
    assert "Immutable Challenger Improvement Loop" in text
    assert "Market-data benchmark and fallback authority" in text
    assert "Alternative sources never masquerade as Dhan" not in text  # wording lives in matrix
    assert "Never replace Dhan broker/live truth" in text
    assert "Cloud accelerator training and bounded CPU failover" in text
    assert "laptop CPU run is a bounded disaster fallback" in text
    assert "PAPER feed latency objective" in text
    assert "p95 supported tick-to-PAPER-observation latency below one second" in text
    assert "option-chain REST snapshots" in text
    assert "Continuous concern reporting at every stage" in text
    assert "Do not spam identical messages" in text
    assert "Best-practice comparison checkpoint" in text
    assert "Bloomberg only when the user has a valid licensed entitlement" in text
    assert "Next Action Plan (NAP) and user guidance" in text
    assert "Never ask the user to paste secrets into chat" in text
    assert "Cycle performance decision" in text
    assert "ROLLBACK_CHAMPION" in text
    assert "Indian catalyst and sentiment intelligence" in text
    assert "Dhan remains the" in text
    assert "sole broker/live Indian symbol, quote, option-chain and trade-data authority" in text
    assert "TradingView India is excluded from automated" in text
    assert "CATALYST_LICENSE_UNPROVEN" in text
    assert "INSIDER_OR_SHAREHOLDING_DISCLOSURE" in text
    assert "price/volume-only and catalyst-only baselines" in text
    assert "The catalyst lane is" in text
    assert "Paid data and AI connector control plane" in text
    assert "Provider/product names are not capabilities" in text
    assert "ChatGPT Finance" in text
    assert "Copilot Finance" in text
    assert "Google Finance" in text
    assert "public production dashboard remains read-only" in text
    assert "Never echo, reveal, fetch back or test a credential from browser code" in text
    assert "Do not hot-patch the serving application during" in text
    assert "The connector activation lane is" in text
    assert "Secure browser OAuth connection" in text
    assert "Do not relabel API-key authentication as OAuth" in text
    assert "authorization-code" in text and "PKCE" in text
    assert "never return either token to browser" in text
    assert "logging into ChatGPT authorizes the System3 OpenAI API connector" in text
    assert "predeployed control plane" in text
    assert "External strategy-artifact intake and claim validation" in text
    assert "INCOMPLETE_SOURCE" in text
    assert "Estimated_Automatable_Percent" in text
    assert "Continuous read-only production sentinel" in text
    assert "SPLIT_BRAIN_DEPLOYMENT_RISK" in text
    assert "artifact digest/revision mapping" in text
    assert "Data-integrity and PAPER lifecycle acceptance" in text
    assert "missing fill, rewrite an execution record or force balance" in text
    assert "Master production-closure contract" in text
    assert "G01 Repository SHA" in text and "G19 Issue #188 coordination" in text
    assert "Safe API and log-correlation law" in text
    assert "Repository deep-MRI and duplication law" in text
    assert "STATE_A_VERIFIED" in text
    assert "STATE_B_EXTERNAL_BLOCKER" in text
    assert "STATE_C_OWNERSHIP_BLOCKER" in text
    assert "RHUI_PROGRESS_V2" in text
    assert "Production Score = freshly PASS applicable gates" in text
    assert "Remaining Top 20" in text


def test_agent_entrypoints_reference_runbook_authority():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    policy = (ROOT / "agent_policy.yaml").read_text(encoding="utf-8")
    path = "docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md"
    assert path in agents
    assert "re-read before every merge" in agents
    assert path in policy
    assert "SYSTEM3_AUTONOMOUS_E2E_RUNBOOK_V1" in policy
    assert "chat_memory_satisfies_reread: false" in policy
    assert "SYSTEM3_USER_SELECTABLE_SOLUTION_MATRIX.md" in policy
    assert "generated_visuals_are_design_inspiration_only: true" in policy
    assert "historical_validation_replaces_forward_paper: false" in policy
    assert "champion_weights_mutable_in_place: false" in policy
    assert "concerns_required_before_first_commit: true" in policy
    assert "active_champion_in_place_weight_update: forbidden" in policy
    assert "alternative_sources_never_masquerade_as_dhan: true" in policy
    assert "bounded_laptop_cpu_last_resort" in policy
    assert "websocket_tick_to_observation_p95_target_ms: 1000" in policy
    assert "repeat_identical_unchanged_messages: false" in policy
    assert "licensed_institutional_benchmark_if_entitled" in policy
    assert "nap_required_for_genuine_user_action: true" in policy
    assert "tradingview_automated_non_display_use_without_separate_license: forbidden" in policy
    assert "price_only_vs_catalyst_ablation_required: true" in policy
    assert "public_dashboard_raw_secret_input: forbidden" in policy
    assert "google_finance: no_general_api_assumed" in policy
    assert "hot_patch_serving_app_during_market_hours: forbidden" in policy
    assert "activation_can_enable_live_or_orders: false" in policy
    assert "oauth_button_requires_documented_provider_support: true" in policy
    assert "oauth_flow: authorization_code_with_pkce" in policy
    assert "oauth_tokens_server_side_encrypted_only: true" in policy
    assert "api_key_provider_setup: authenticated_admin_to_secret_manager_only" in policy
    assert "automatable_percentage_is_completion_proof: false" in policy
    assert "service_account_json_keys: forbidden" in policy
    assert "self_reported_serving_sha_alone_sufficient: false" in policy
    assert "web_runtime_may_invoke_dhan_rotator: false" in policy
    assert "infer_missing_fills_or_rewrite_records: forbidden" in policy
    assert "mission: maximum_safely_achievable_production_pass" in policy
    assert "format: RHUI_PROGRESS_V2" in policy
    assert "duplicate_root_cause_lane: forbidden" in policy
    assert "unproven_stale_fail_or_blocked_counts_green: false" in policy


def test_solution_matrix_rejects_visual_hype_and_keeps_user_choices():
    matrix = (ROOT / "docs" / "project_control" / "SYSTEM3_USER_SELECTABLE_SOLUTION_MATRIX.md").read_text(
        encoding="utf-8"
    )
    assert "Recommended default" in matrix
    assert "Higher-capability challenger" in matrix
    assert "10 unique hashes" in matrix
    assert "Rejected as technical authority" in matrix
    assert "100% confidence" in matrix
    assert "LIVE/automatic execution implied by artwork" in matrix
    assert "Paid data and AI connector decisions" in matrix
    assert "credentials are configured only through an authenticated admin path" in matrix
    assert "Unsupported OAuth is displayed as unavailable, never emulated" in matrix
    assert "ends mid-URL" in matrix
    assert "sole-deployer/split-brain detection" in matrix


def test_twelve_recommendations_and_guarded_iam_are_machine_locked():
    runbook = RUNBOOK.read_text(encoding="utf-8")
    policy = yaml.safe_load((ROOT / "agent_policy.yaml").read_text(encoding="utf-8"))
    matrix = (ROOT / "docs/project_control/SYSTEM3_USER_SELECTABLE_SOLUTION_MATRIX.md").read_text(
        encoding="utf-8"
    )
    for recommendation_id in [f"R{i:02d}" for i in range(1, 13)]:
        assert recommendation_id in runbook
        assert recommendation_id in policy["autonomous_end_to_end_runbook"]["recommendation_ledger"]["ids"]
        assert recommendation_id in matrix
    assert "SPLIT_BRAIN_DEPLOYMENT_RISK" in runbook
    assert policy["autonomous_end_to_end_runbook"]["production_sentinel"]["may_redeploy_or_repair_iam"] is False
    assert policy["autonomous_end_to_end_runbook"]["iam_recovery"]["sentinel_can_repair"] is False
    assert policy["autonomous_end_to_end_runbook"]["iam_recovery"]["audit_log_function_can_grant_roles"] is False
    assert policy["autonomous_end_to_end_runbook"]["dhan_rotation_governance"]["web_runtime_invocation"] == "forbidden"
    assert policy["autonomous_end_to_end_runbook"]["paper_lifecycle_reconciliation"]["paper_equals_real_execution"] is False


def test_agent_policy_validates_against_canonical_versioned_schema():
    policy_path = ROOT / "agent_policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    schema_path = ROOT / policy["schema_path"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(instance=policy, schema=schema)
    assert policy["version"] == policy["schema_version"] == 4

    prior_major = deepcopy(policy)
    prior_major["version"] = prior_major["schema_version"] = 3
    future_major = deepcopy(policy)
    future_major["version"] = future_major["schema_version"] = 5
    validator = jsonschema.Draft202012Validator(schema)
    assert list(validator.iter_errors(prior_major)), "v3 requires an explicit migration/compatibility reader"
    assert list(validator.iter_errors(future_major)), "unknown future major versions must fail closed"


def test_mri_connector_and_compute_safety_are_schema_enforced():
    policy = yaml.safe_load((ROOT / "agent_policy.yaml").read_text(encoding="utf-8"))
    schema = json.loads((ROOT / policy["schema_path"]).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    unsafe_mutations = (
        ("market_data_authority", "primary_live_indian_broker", "another_feed"),
        ("compute", "laptop_production_or_paper_serving", True),
        ("paper_latency", "target_is_slo_not_guarantee", False),
        ("paper_latency", "live_or_hft_authority_granted", True),
        ("continuous_concern_reporting", "repeat_identical_unchanged_messages", True),
        ("catalyst_intelligence", "market_and_broker_truth", "news_feed"),
        ("paid_ai_connector_control_plane", "public_dashboard_raw_secret_input", "allowed"),
        ("paid_ai_connector_control_plane", "browser_may_read_secret_payload", True),
        ("paid_ai_connector_control_plane", "activation_can_enable_live_or_orders", True),
    )
    for section, key, unsafe_value in unsafe_mutations:
        candidate = deepcopy(policy)
        candidate["autonomous_end_to_end_runbook"]["mri_autonomous_scan"][section][key] = unsafe_value
        assert list(validator.iter_errors(candidate)), f"schema accepted unsafe {section}.{key}"


def test_resilience_and_supply_chain_alternatives_are_fail_closed():
    policy = yaml.safe_load((ROOT / "agent_policy.yaml").read_text(encoding="utf-8"))
    controls = policy["autonomous_end_to_end_runbook"]
    assert controls["deployment_supply_chain"]["workflow_actions_must_use_reviewed_full_sha"] is True
    assert controls["dag_resilience_testing"]["primary"] == [
        "pytest",
        "property_based",
        "state_machine",
        "fault_injection",
    ]
    assert controls["dag_resilience_testing"]["chaos_mesh"] == "only_if_governed_kubernetes_environment_exists"
    assert controls["data_integrity_audit"]["mode"] == "read_only"
    assert controls["paper_telemetry"]["latency_metrics"] == ["p50", "p95", "p99", "max"]
