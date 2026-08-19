"""Eval: rotation Job must never classify DH-906 as auth failure."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_rotation_job_auth_markers_exclude_906():
    src = _text("scripts/gcp_dhan_token_rotation_job.py")
    assert '"dh-906"' not in src.split("_AUTH_MARKERS")[1].split(")")[0], \
        "dh-906 must not be in _AUTH_MARKERS — it is request rejection, not auth failure"


def test_rotation_job_has_request_rejected_codes():
    src = _text("scripts/gcp_dhan_token_rotation_job.py")
    assert "_REQUEST_REJECTED_CODES" in src
    assert "906" in src.split("_REQUEST_REJECTED_CODES")[1].split("}")[0]


def test_rotation_job_is_auth_failure_guards_906():
    src = _text("scripts/gcp_dhan_token_rotation_job.py")
    assert "dh-906" in src.split("_is_auth_failure")[1].split("return")[0].lower() or \
           "_REQUEST_REJECTED_CODES" in src.split("_is_auth_failure")[1].split("return")[0]
