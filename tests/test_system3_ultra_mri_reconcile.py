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


def test_non_runtime_reconciliation_runs_canonical_browser_proof_in_process():
    assert "import scripts.gcp_public_dashboard_runtime_proof as proof_module" in SCRIPT
    assert "proof_module.EXPECTED_SHA = serving_sha" in SCRIPT
    assert "proof_module.main()" in SCRIPT
    assert "serving_sha_proof=" in SCRIPT
    assert 'subprocess.run([sys.executable' not in SCRIPT


def test_runtime_sha_is_strictly_validated_before_reconciliation():
    assert 're.compile(r"^[0-9a-f]{40}$")' in SCRIPT
    assert '"git", "cat-file", "-e"' in SCRIPT
    assert "_valid_commit_sha(serving)" in SCRIPT


def test_reconciliation_does_not_turn_failed_browser_proof_green_without_real_retry_success():
    assert "if proof_rc == 0:" in SCRIPT
    assert 'browser["status"] = "PASS"' in SCRIPT


def test_reconciled_non_runtime_head_replaces_initial_status_failure_only_after_retry_passes():
    publish = SCRIPT.index("_publish_reconciled_head_status(head, serving)")
    retry_gate = SCRIPT.index("if proof_rc == 0:")
    matrix_pass = SCRIPT.index('browser["status"] = "PASS"')
    assert retry_gate < publish < matrix_pass
    assert '"context": "public-dashboard/runtime-proof"' in SCRIPT
    assert '"state": "success"' in SCRIPT
    assert "head_status_publish_error" in SCRIPT
    assert "return 0" in SCRIPT
