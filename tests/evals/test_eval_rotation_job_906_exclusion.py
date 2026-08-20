"""Eval: rotation Job must never confuse request rejection with HTTP auth rejection."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROTATION_JOB = ROOT / "scripts" / "gcp_dhan_token_rotation_job.py"


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _classifier():
    """Execute only the classifier helpers, not the Cloud/GCP job imports."""
    src = ROTATION_JOB.read_text(encoding="utf-8")
    tree = ast.parse(src)
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if names & {"_AUTH_MARKERS", "_REQUEST_REJECTED_CODES"}:
                selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {"_safe_blob", "_is_auth_failure"}:
            selected.append(node)
    module = ast.Module(body=selected, type_ignores=[])
    ast.fix_missing_locations(module)
    ns = {"Any": object}
    exec(compile(module, str(ROTATION_JOB), "exec"), ns)
    return ns["_is_auth_failure"]


def test_rotation_job_auth_markers_exclude_906():
    src = _text("scripts/gcp_dhan_token_rotation_job.py")
    assert '"dh-906"' not in src.split("_AUTH_MARKERS")[1].split(")")[0], \
        "dh-906 must not be in _AUTH_MARKERS — it is request rejection, not auth failure"


def test_rotation_job_has_request_rejected_codes():
    src = _text("scripts/gcp_dhan_token_rotation_job.py")
    assert "_REQUEST_REJECTED_CODES" in src
    assert "906" in src.split("_REQUEST_REJECTED_CODES")[1].split("}")[0]


def test_rotation_job_is_auth_failure_guards_906():
    classify = _classifier()
    assert classify("DH-906 invalid token", status_code=400) is False


def test_http_401_wins_over_dh906_text():
    classify = _classifier()
    assert classify("401 DH-906 invalid token", status_code=401) is True


def test_http_401_wins_over_dh805_text():
    classify = _classifier()
    assert classify("401 DH-805 invalid token", status_code=401) is True


def test_http_401_wins_over_nested_dh906_payload():
    classify = _classifier()
    payload = {"errorCode": "DH-906", "errorMessage": "invalid token"}
    assert classify(payload, status_code=401) is True


def test_dh906_without_http_401_remains_non_auth():
    classify = _classifier()
    assert classify("DH-906 invalid token", status_code=None) is False


def test_dh805_without_http_401_remains_non_auth():
    classify = _classifier()
    assert classify("DH-805 invalid token", status_code=400) is False


def test_plain_invalid_token_still_classifies_as_auth_failure():
    classify = _classifier()
    assert classify("invalid token", status_code=400) is True


def test_request_rejected_numeric_status_remains_non_auth():
    classify = _classifier()
    assert classify("invalid token", status_code=906) is False
