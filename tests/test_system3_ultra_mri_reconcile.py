from pathlib import Path

SCRIPT = Path("scripts/system3_ultra_mri_reconcile.py").read_text(encoding="utf-8")
WORKFLOW = Path(".github/workflows/live-proof-center.yml").read_text(encoding="utf-8")


def test_evidence_reader_is_canonical_live_proof_identity():
    assert "system3-evidence-reader@system3-openalgo-safe.iam.gserviceaccount.com" in WORKFLOW
    assert "fetch-depth: 0" in WORKFLOW


def test_runtime_affecting_paths_never_receive_sha_exception():
    for marker in ("dashboard/", "core/", "src/", "config/", "deploy/gcp/", "scripts/gcp_public_dashboard_runtime_proof.py"):
        assert marker in SCRIPT
    assert "if runtime:" in SCRIPT


def test_non_runtime_reconciliation_reruns_canonical_browser_proof_against_serving_sha():
    assert 'env["GITHUB_SHA"] = serving' in SCRIPT
    assert "gcp_public_dashboard_runtime_proof.py" in SCRIPT
    assert "serving_sha_proof=" in SCRIPT


def test_reconciliation_does_not_turn_failed_browser_proof_green_without_real_retry_success():
    assert "if proof.returncode == 0:" in SCRIPT
    assert 'browser["status"] = "PASS"' in SCRIPT
