"""Fail-closed cloud scheduler collector target-discovery regression tests."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from scripts.gcp_worker_job import _collector_job_targets


def resource(name, *, state="ENABLED", valid=True, kind="http"):
    return {
        "name": name+"-schedule",
        "state": state,
        "target_job": name,
        "target_uri_valid": valid,
        "target_type": kind,
    }


def test_include_expected_and_all_valid_enabled_external_targets():
    actual = [
        resource("genesis-system3-rank"),
        resource("daily-gain-validate-job"),
        resource("system3-smoketest-job"),
    ]
    assert _collector_job_targets(["genesis-system3-rank"], actual) == [
        "daily-gain-validate-job",
        "genesis-system3-rank",
        "system3-smoketest-job",
    ]


def test_invalid_uri_excluded_even_if_name_looks_real():
    assert _collector_job_targets([], [resource("missing-run", valid=False)]) == []


def test_paused_scheduler_does_not_add_new_target():
    assert _collector_job_targets([], [resource("paused-old", state="PAUSED")]) == []


def test_non_http_target_cannot_be_job_invocation():
    assert _collector_job_targets([], [resource("pubsub-event", kind="pubsub")]) == []


def test_duplicate_expected_and_discovered_target_is_deduplicated():
    rows = [resource("genesis-system3-rank"), resource("genesis-system3-rank")]
    assert _collector_job_targets(["genesis-system3-rank"], rows) == ["genesis-system3-rank"]


@pytest.mark.parametrize("bad_target", ["", None, 55, "evil/path", "abc?query=1", "x:run"])
def test_non_job_names_are_excluded(bad_target):
    rows = [{"state": "ENABLED", "target_type": "http", "target_uri_valid": True, "target_job": bad_target}]
    assert _collector_job_targets([], rows) == []


def test_missing_gcp_evidence_is_not_fabricated():
    assert _collector_job_targets([], []) == []


def test_collector_integration_passes_live_resources_to_discovery():
    from scripts import gcp_worker_job
    tree = ast.parse(Path(gcp_worker_job.__file__).read_text(encoding="utf-8"))
    fn = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "_collect_scheduler_facts")
    assert "_collector_job_targets(expected_job_targets(), resources)" in ast.unparse(fn)


def test_expected_targets_remain_included_when_actual_rows_missing():
    assert _collector_job_targets(["genesis-system3-validate"], []) == ["genesis-system3-validate"]
