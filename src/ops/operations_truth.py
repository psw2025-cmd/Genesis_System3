from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

INVENTORY_TRUTH_STATES = {
    "PROVEN",
    "PROVEN_EMPTY",
    "STALE",
    "API_ERROR",
    "SCHEMA_ERROR",
    "UNKNOWN",
    "NOT_APPLICABLE",
}

REQUIRED_INVENTORY_CATEGORIES = (
    "cloud_run_services",
    "cloud_run_jobs",
    "cloud_scheduler_jobs",
    "pubsub_topics",
    "pubsub_subscriptions",
    "secret_manager_secrets",
    "service_accounts",
    "project_iam_bindings",
    "artifact_registry_repositories",
    "cloud_build_triggers",
    "cloud_build_recent_builds",
    "monitoring_dashboards",
    "alert_policies",
    "uptime_checks",
)

# Secret *metadata* is permitted. Secret payload/token/credential material is not.
FORBIDDEN_INVENTORY_KEYS = {
    "payload",
    "secret_payload",
    "secret_value",
    "raw_secret",
    "access_token",
    "refresh_token",
    "password",
    "pin_value",
    "totp_value",
    "credentials_json",
    "private_key",
}

SLO_RULES = {
    "availability_pct": "min",
    "api_success_latency_p95_ms": "max",
    "broker_read_success_pct": "min",
    "token_rotation_success_pct": "min",
    "synthetic_success_pct": "min",
}

TREND_RULES = {
    "mttr_minutes": "down",
    "false_alert_rate_pct": "down",
    "automated_recovery_rate_pct": "up",
}


@dataclass(frozen=True)
class MetricDecision:
    state: str
    value: float | None
    target: float | None
    observations: int
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "value": self.value,
            "target": self.target,
            "observations": self.observations,
            "reason": self.reason,
        }


def _contains_forbidden_key(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_INVENTORY_KEYS:
                return normalized
            found = _contains_forbidden_key(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _contains_forbidden_key(child)
            if found:
                return found
    return None


def classify_inventory_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        return {"state": "SCHEMA_ERROR", "count": None, "reason": "record_not_mapping"}

    state = str(record.get("state") or "UNKNOWN").upper()
    if state not in INVENTORY_TRUTH_STATES:
        return {"state": "SCHEMA_ERROR", "count": None, "reason": f"invalid_state:{state}"}

    if state in {"PROVEN", "PROVEN_EMPTY"}:
        source = record.get("source")
        observed_at = record.get("observed_at")
        items = record.get("items")
        if not isinstance(source, str) or not source.strip():
            return {"state": "SCHEMA_ERROR", "count": None, "reason": "missing_source"}
        if not isinstance(observed_at, str) or not observed_at.strip():
            return {"state": "SCHEMA_ERROR", "count": None, "reason": "missing_observed_at"}
        if not isinstance(items, list):
            return {"state": "SCHEMA_ERROR", "count": None, "reason": "items_not_list"}

        forbidden = _contains_forbidden_key(items)
        if forbidden:
            return {
                "state": "SCHEMA_ERROR",
                "count": None,
                "reason": f"secret_payload_field_forbidden:{forbidden}",
            }

        count = len(items)
        if state == "PROVEN_EMPTY" and count != 0:
            return {
                "state": "SCHEMA_ERROR",
                "count": count,
                "reason": "proven_empty_contains_items",
            }
        normalized_state = "PROVEN_EMPTY" if count == 0 else "PROVEN"
        return {
            "state": normalized_state,
            "count": count,
            "reason": "inventory_query_completed",
            "source": source,
            "observed_at": observed_at,
        }

    return {
        "state": state,
        "count": None,
        "reason": str(record.get("reason") or state.lower()),
        "source": record.get("source"),
        "observed_at": record.get("observed_at"),
    }


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def evaluate_slo_metric(
    name: str,
    record: Any,
    *,
    target: float,
    minimum_observations: int,
) -> MetricDecision:
    if name not in SLO_RULES:
        return MetricDecision("SCHEMA_ERROR", None, target, 0, "unknown_slo_metric")
    if not isinstance(record, Mapping):
        return MetricDecision("NOT_PROVEN", None, target, 0, "metric_missing")

    value = _numeric(record.get("value"))
    observations_raw = record.get("observations", 0)
    observations = observations_raw if isinstance(observations_raw, int) and observations_raw >= 0 else 0
    source = record.get("source")
    observed_at = record.get("observed_at")

    if value is None:
        return MetricDecision("SCHEMA_ERROR", None, target, observations, "value_not_numeric")
    if not isinstance(source, str) or not source.strip():
        return MetricDecision("SCHEMA_ERROR", value, target, observations, "missing_source")
    if not isinstance(observed_at, str) or not observed_at.strip():
        return MetricDecision("SCHEMA_ERROR", value, target, observations, "missing_observed_at")
    if observations < minimum_observations:
        return MetricDecision(
            "NOT_PROVEN",
            value,
            target,
            observations,
            f"insufficient_observations:{observations}<{minimum_observations}",
        )

    rule = SLO_RULES[name]
    passed = value >= target if rule == "min" else value <= target
    comparator = ">=" if rule == "min" else "<="
    return MetricDecision(
        "PASS" if passed else "FAIL",
        value,
        target,
        observations,
        f"observed_{value:g}{comparator}target_{target:g}" if passed else f"observed_{value:g}_misses_{comparator}_{target:g}",
    )


def evaluate_trend_metric(name: str, record: Any, *, minimum_incidents: int) -> dict[str, Any]:
    if name not in TREND_RULES:
        return {"state": "SCHEMA_ERROR", "reason": "unknown_trend_metric"}
    if not isinstance(record, Mapping):
        return {"state": "NOT_PROVEN", "reason": "trend_missing"}

    baseline = _numeric(record.get("baseline"))
    current = _numeric(record.get("current"))
    observations_raw = record.get("incidents", 0)
    incidents = observations_raw if isinstance(observations_raw, int) and observations_raw >= 0 else 0
    if baseline is None or current is None:
        return {"state": "SCHEMA_ERROR", "reason": "trend_values_not_numeric", "incidents": incidents}
    if incidents < minimum_incidents:
        return {
            "state": "NOT_PROVEN",
            "baseline": baseline,
            "current": current,
            "incidents": incidents,
            "reason": f"insufficient_incidents:{incidents}<{minimum_incidents}",
        }

    direction = TREND_RULES[name]
    if current == baseline:
        state = "FLAT"
    elif (direction == "down" and current < baseline) or (direction == "up" and current > baseline):
        state = "IMPROVING"
    else:
        state = "REGRESSING"
    return {
        "state": state,
        "baseline": baseline,
        "current": current,
        "incidents": incidents,
        "reason": f"desired_direction:{direction}",
    }


def _validate_governance(targets: Mapping[str, Any]) -> list[str]:
    governance = targets.get("governance")
    if not isinstance(governance, Mapping):
        return ["missing_governance"]

    required_exact = {
        "live_trading_enabled": False,
        "order_probe_allowed": False,
        "pull_request_production_mutation_allowed": False,
        "secret_payload_inventory_allowed": False,
        "har_redaction_required": True,
        "candidate_initial_traffic_pct": 0,
        "rollback_by_traffic_reassignment": True,
        "cloud_run_revision_restart_supported": False,
        "hidden_token_fallback_allowed": False,
        "unknown_state_fail_open_allowed": False,
    }
    violations = []
    for key, expected in required_exact.items():
        if governance.get(key) != expected:
            violations.append(f"{key}!={expected!r}")
    if governance.get("canonical_token_authority") != "gcp-secret-manager-dynamic":
        violations.append("canonical_token_authority_invalid")
    retry_limit = governance.get("incident_remediation_retry_limit")
    if not isinstance(retry_limit, int) or retry_limit < 0 or retry_limit > 2:
        violations.append("incident_remediation_retry_limit_invalid")
    return violations


def evaluate_operations_truth(evidence: Mapping[str, Any], targets: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate baseline SRE evidence without granting mutation or trading authority.

    This is intentionally a baseline authority, not a production-readiness gate.
    It distinguishes successful inventory collection from actual SLO health.
    """

    governance_violations = _validate_governance(targets)
    inventory_input = evidence.get("inventory") if isinstance(evidence, Mapping) else None
    inventory_input = inventory_input if isinstance(inventory_input, Mapping) else {}

    inventory: dict[str, dict[str, Any]] = {}
    for category in REQUIRED_INVENTORY_CATEGORIES:
        inventory[category] = classify_inventory_record(inventory_input.get(category))

    inventory_problem_states = {"STALE", "API_ERROR", "SCHEMA_ERROR", "UNKNOWN"}
    inventory_all_observed = all(
        item["state"] in {"PROVEN", "PROVEN_EMPTY", "NOT_APPLICABLE"} for item in inventory.values()
    )
    inventory_has_error = any(item["state"] in inventory_problem_states for item in inventory.values())
    inventory_state = "PROVEN" if inventory_all_observed else "PARTIAL"
    if any(item["state"] == "SCHEMA_ERROR" for item in inventory.values()):
        inventory_state = "SCHEMA_ERROR"

    slo_targets = targets.get("slo_targets") if isinstance(targets.get("slo_targets"), Mapping) else {}
    minimum = targets.get("minimum_evidence") if isinstance(targets.get("minimum_evidence"), Mapping) else {}
    scorecard_input = evidence.get("scorecard") if isinstance(evidence.get("scorecard"), Mapping) else {}

    minimum_key = {
        "availability_pct": "availability_observations",
        "api_success_latency_p95_ms": "latency_observations",
        "broker_read_success_pct": "broker_read_observations",
        "token_rotation_success_pct": "token_rotation_observations",
        "synthetic_success_pct": "synthetic_observations",
    }

    scorecard: dict[str, dict[str, Any]] = {}
    for metric in SLO_RULES:
        target = _numeric(slo_targets.get(metric))
        min_obs_raw = minimum.get(minimum_key[metric], 0)
        min_obs = min_obs_raw if isinstance(min_obs_raw, int) and min_obs_raw >= 0 else 0
        if target is None:
            decision = MetricDecision("SCHEMA_ERROR", None, None, 0, "target_missing_or_non_numeric")
        else:
            decision = evaluate_slo_metric(
                metric,
                scorecard_input.get(metric),
                target=target,
                minimum_observations=min_obs,
            )
        scorecard[metric] = decision.as_dict()

    score_states = {item["state"] for item in scorecard.values()}
    if "SCHEMA_ERROR" in score_states:
        scorecard_state = "SCHEMA_ERROR"
    elif "FAIL" in score_states:
        scorecard_state = "TARGET_FAIL"
    elif score_states == {"PASS"}:
        scorecard_state = "PROVEN"
    else:
        scorecard_state = "INSUFFICIENT_EVIDENCE"

    trend_input = evidence.get("trends") if isinstance(evidence.get("trends"), Mapping) else {}
    min_incidents_raw = minimum.get("trend_incidents", 0)
    min_incidents = min_incidents_raw if isinstance(min_incidents_raw, int) and min_incidents_raw >= 0 else 0
    trends = {
        name: evaluate_trend_metric(name, trend_input.get(name), minimum_incidents=min_incidents)
        for name in TREND_RULES
    }

    risk_register = evidence.get("risk_register") if isinstance(evidence.get("risk_register"), list) else []
    architecture_map = evidence.get("architecture_map") if isinstance(evidence.get("architecture_map"), Mapping) else {
        "nodes": [],
        "edges": [],
        "state": "UNKNOWN",
    }

    if governance_violations:
        state = "SCHEMA_ERROR"
    elif inventory_has_error or inventory_state != "PROVEN" or scorecard_state != "PROVEN":
        state = "PARTIAL_EVIDENCE"
    else:
        # Even when baseline inventory + SLO measurements are all proven, the
        # wider nine-phase autonomous-remediation program still requires
        # synthetic, incident, runbook and recovery evidence before closure.
        state = "BASELINE_PROVEN_NOT_FULL_SRE_CLOSURE"

    return {
        "schema_version": 1,
        "scope": "BASELINE_INVENTORY_AND_SLO_SCORECARD",
        "state": state,
        "inventory_state": inventory_state,
        "scorecard_state": scorecard_state,
        "inventory": inventory,
        "scorecard": scorecard,
        "trends": trends,
        "risk_register": risk_register,
        "architecture_map": architecture_map,
        "governance_violations": governance_violations,
        "targets_are_goals_not_current_claims": bool(targets.get("targets_are_goals_not_current_claims")),
        "live_trading_enabled": False,
        "real_orders_attempted": 0,
        "order_probe_allowed": False,
        "production_mutation_from_pr_allowed": False,
        "full_sre_program_closed": False,
    }
