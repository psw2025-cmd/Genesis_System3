from __future__ import annotations

from pathlib import Path


def test_cloud_run_deploy_secret_role_guard_has_no_self_match_or_real_grant():
    workflow = Path(".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")

    # Construct forbidden role fragments without embedding them verbatim in the
    # test or workflow guard. A literal occurrence must correspond to a real
    # executable/configuration line and remains forbidden.
    secret_accessor_marker = "secret" + "Accessor"
    secret_version_adder_marker = "secretVersion" + "Adder"

    executable_lines = [
        line.strip()
        for line in workflow.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    hits = [
        line
        for line in executable_lines
        if secret_accessor_marker in line or secret_version_adder_marker in line
    ]
    assert hits == []

    # The inline deployment guard must also construct its marker strings, so a
    # future edit cannot reintroduce the same self-matching assertion defect.
    assert 'secret_accessor_marker = "secret" + "Accessor"' in workflow
    assert 'secret_version_adder_marker = "secretVersion" + "Adder"' in workflow
    assert "secret_role_hits" in workflow
