"""Regression contract: /api/health QC classification must fail closed.

`/api/health` built `qc_status` starting from ``PASS`` and only downgraded it
on an explicit negative result:

    qc_status = "PASS"
    if not qc_data.get("qc_passed", True):
        qc_status = "FAIL"

So an absent QC file (``qc_data == {}``), a QC payload with no ``qc_passed``
key, or a pass recorded over zero verified contracts all reported
``qc_status: PASS``. Meanwhile `/api/state` reported ``NOT_READY`` with
``NO_VERIFIED_CONTRACTS`` and raised a ``QC_FAIL`` alert from the same runtime,
which is the health/state contradiction observed on the serving revision.

`classify_qc_status` now requires positive evidence before reporting PASS.
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="module")
def classify():
    old_val = os.environ.get("REQUIRE_API_KEY")
    os.environ["REQUIRE_API_KEY"] = "false"
    try:
        spec = importlib.util.spec_from_file_location(
            "dashboard_backend_app_qc_under_test",
            ROOT_DIR / "dashboard" / "backend" / "app.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.classify_qc_status
    finally:
        if old_val is not None:
            os.environ["REQUIRE_API_KEY"] = old_val
        else:
            os.environ.pop("REQUIRE_API_KEY", None)


def test_absent_qc_file_is_not_a_pass(classify):
    # qc_data is {} when outputs/qc_report.json does not exist.
    assert classify({}) == ("NOT_READY", ["NO_QC_DATA"])


def test_missing_qc_result_key_is_not_a_pass(classify):
    status, failures = classify({"status": "OK", "total_contracts": 412})

    assert status == "NOT_READY"
    assert failures == ["QC_RESULT_MISSING"]


def test_pass_over_zero_contracts_is_not_a_pass(classify):
    # The exact live case: QC claims success having verified nothing.
    status, failures = classify({"qc_passed": True, "total_contracts": 0})

    assert status == "NOT_READY"
    assert failures == ["NO_VERIFIED_CONTRACTS"]


def test_pass_with_absent_contract_count_is_not_a_pass(classify):
    status, failures = classify({"qc_passed": True})

    assert status == "NOT_READY"
    assert failures == ["NO_VERIFIED_CONTRACTS"]


def test_non_numeric_contract_count_is_not_a_pass(classify):
    status, failures = classify({"qc_passed": True, "total_contracts": "many"})

    assert status == "NOT_READY"
    assert failures == ["NO_VERIFIED_CONTRACTS"]


@pytest.mark.parametrize(
    "qc_passed",
    [
        "false",  # JSON string: truthy, would read as success on truthiness
        "true",
        "",
        1,  # ints are not QC verdicts, even when they look like one
        0,
        None,
        [],
        {},
    ],
)
def test_non_boolean_qc_result_is_never_a_pass(classify, qc_passed):
    status, failures = classify({"qc_passed": qc_passed, "total_contracts": 412})

    assert status == "NOT_READY"
    assert failures == ["QC_RESULT_NOT_BOOLEAN"]


def test_boolean_verdicts_are_still_honoured(classify):
    # Guards the isinstance check against over-tightening.
    assert classify({"qc_passed": True, "total_contracts": 412}) == ("PASS", [])
    assert classify({"qc_passed": False, "total_contracts": 412}) == ("FAIL", [])


def test_explicit_failure_outranks_no_data(classify):
    # Documents precedence: both are non-PASS, and FAIL is the more actionable
    # verdict, so an explicit failure is reported even alongside NO_DATA.
    status, failures = classify(
        {"qc_passed": False, "status": "NO_DATA", "qc_failures": ["stale chain"]}
    )

    assert status == "FAIL"
    assert failures == ["stale chain"]


def test_explicit_failure_is_preserved_and_capped(classify):
    status, failures = classify(
        {"qc_passed": False, "qc_failures": [f"f{i}" for i in range(9)]}
    )

    assert status == "FAIL"
    assert failures == ["f0", "f1", "f2", "f3", "f4"]


def test_explicit_failure_without_reasons_still_fails(classify):
    assert classify({"qc_passed": False}) == ("FAIL", [])


def test_no_data_is_preserved(classify):
    status, failures = classify(
        {"qc_passed": True, "status": "NO_DATA", "total_contracts": 0}
    )

    assert status == "NO_DATA"
    assert failures == []


def test_genuine_verified_pass_is_still_reported(classify):
    status, failures = classify(
        {"qc_passed": True, "status": "OK", "total_contracts": 412, "underlying_count": 4}
    )

    assert status == "PASS"
    assert failures == []
