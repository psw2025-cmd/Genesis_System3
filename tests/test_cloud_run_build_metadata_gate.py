from __future__ import annotations

import pytest

from scripts.cloud_run_build_metadata_gate import EXPECTED_IMAGE, validate


def test_accepts_full_commit_sha_and_approved_image():
    validate("2ed7161f8d7c09cb1b418873b5b2ab5570ec836c", EXPECTED_IMAGE)


@pytest.mark.parametrize("sha", ["", "UNSET", "abc", "A" * 40, "0" * 39])
def test_rejects_missing_or_malformed_commit_sha(sha):
    with pytest.raises(ValueError, match="full lowercase 40-character"):
        validate(sha, EXPECTED_IMAGE)


def test_rejects_unapproved_artifact_registry_repository():
    with pytest.raises(ValueError, match="approved System3 Artifact Registry"):
        validate("2ed7161f8d7c09cb1b418873b5b2ab5570ec836c", "example.invalid/attacker/image")
