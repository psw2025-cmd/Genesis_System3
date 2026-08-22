"""Eval: deploy scheduler-health proof must name transport vs predicate failures."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_eval_scheduler_health_gate_replaces_opaque_jq_with_named_classes():
    gate = (ROOT / "scripts/scheduler_health_gate.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    assert "CURL_TIMEOUT" in gate
    assert "CURL_NON_2XX" in gate
    assert "INVALID_JSON" in gate
    assert "collector.execution_matches_canary_or_prior_succeeded" in gate
    assert "scripts/scheduler_health_gate.py" in workflow
    assert "jq -e --arg execution" not in workflow
    assert "jq -e --argjson pass" not in workflow
    assert "Upload scheduler-health gate report" in workflow
    assert "if: always()" in workflow.split("Upload scheduler-health gate report", 1)[1][:400]
