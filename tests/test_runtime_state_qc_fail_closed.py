"""Regression contract: runtime QC status must fail closed, never fail open.

Two defects this locks out:

1. ``RuntimeStateStore._enforce_safety_invariants`` was defined twice, byte
   identical. The second definition silently shadowed the first, so any future
   edit to the first would have been dead code on a safety-critical path.
2. QC status defaulted to ``PASS`` when health data was missing or empty, both
   in the initial state (with zero contracts) and in ``sync_from_files``. That
   let ``/api/health`` report ``qc_status: PASS`` while the same runtime state
   carried an active QC failure. ``state_sync_service`` already defaults to
   ``NOT_READY``; these paths now match it.
"""

import ast
import inspect
import json

from dashboard.backend.runtime_state_store import RuntimeStateStore


def _method_definition_count(name: str) -> int:
    source = inspect.getsource(RuntimeStateStore)
    tree = ast.parse(source.lstrip())
    class_def = tree.body[0]
    return sum(
        1
        for node in class_def.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    )


def test_safety_invariants_method_is_not_shadowed():
    assert _method_definition_count("_enforce_safety_invariants") == 1


def test_initial_qc_status_is_not_a_vacuous_pass(tmp_path):
    store = RuntimeStateStore(tmp_path)
    qc = store.get_state()["qc"]

    # Nothing has been measured yet, so QC must not claim to have passed.
    assert qc["contracts_total"] == 0
    assert qc["underlyings"] == 0
    assert qc["status"] != "PASS"
    assert qc["status"] == "NOT_READY"


def _sync_with_health(tmp_path, health: dict) -> dict:
    (tmp_path / "health.json").write_text(json.dumps(health))
    store = RuntimeStateStore(tmp_path)
    store.sync_from_files()
    return store.get_state()["qc"]


def test_missing_qc_status_does_not_default_to_pass(tmp_path):
    qc = _sync_with_health(tmp_path, {"is_connected": True})

    assert qc["status"] == "NOT_READY"


def test_empty_qc_status_does_not_default_to_pass(tmp_path):
    qc = _sync_with_health(tmp_path, {"is_connected": True, "qc_status": ""})

    assert qc["status"] == "NOT_READY"


def test_null_qc_status_does_not_default_to_pass(tmp_path):
    qc = _sync_with_health(tmp_path, {"is_connected": True, "qc_status": None})

    assert qc["status"] == "NOT_READY"


def test_reported_failure_is_preserved(tmp_path):
    qc = _sync_with_health(
        tmp_path,
        {"is_connected": True, "qc_status": "FAIL", "qc_failures": ["stale chain"]},
    )

    assert qc["status"] == "FAIL"
    assert qc["failures"] == ["stale chain"]


def test_genuine_pass_is_still_reported(tmp_path):
    qc = _sync_with_health(
        tmp_path,
        {"is_connected": True, "qc_status": "pass", "contracts_total": 412, "underlyings": 4},
    )

    assert qc["status"] == "PASS"
    assert qc["contracts_total"] == 412
