from pathlib import Path


SCRIPT = Path("scripts/system3_ultra_mri.py").read_text(encoding="utf-8")
WORKFLOW = Path(".github/workflows/live-proof-center.yml").read_text(encoding="utf-8")
DOC = Path("docs/authority/SYSTEM3_ULTRA_MRI_CONTROL_PLANE.md").read_text(encoding="utf-8")


def test_ultra_mri_never_reads_secret_payloads():
    assert "secrets versions access" not in SCRIPT
    assert "secrets versions access" not in WORKFLOW
    assert "Secret payloads are never dumped" in DOC


def test_ultra_mri_uses_canonical_wif():
    assert "google-github-actions/auth@v3" in WORKFLOW
    assert "github-genesis-system3/providers/github" in WORKFLOW
    assert "system3-evidence-reader@system3-openalgo-safe.iam.gserviceaccount.com" in WORKFLOW


def test_ultra_mri_covers_runtime_and_ui_proof():
    for marker in (
        "api_broker_status",
        "api_batch_chains",
        "api_state",
        "canonical_browser_proof",
        "firestore_databases",
        '"scheduler"',
        "secrets_list",
        "recent_cloud_run_logs",
        "CAPABILITY_MATRIX.csv",
        "FINAL_VERDICT.json",
    ):
        assert marker in SCRIPT


def test_ultra_mri_is_manually_runnable_and_artifacted():
    assert "workflow_dispatch:" in WORKFLOW
    assert "actions/upload-artifact@v4" in WORKFLOW
    assert "reports/latest/system3_ultra_mri/" in WORKFLOW
    assert "python scripts/system3_ultra_mri.py" in WORKFLOW


def test_access_failure_is_fail_closed():
    assert "ULTRA_MRI_ACCESS_NOT_CERTIFIED" in WORKFLOW
    assert "access_certified" in SCRIPT
