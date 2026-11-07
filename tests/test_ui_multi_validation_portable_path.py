"""Cloud-portable UI audit output path; no browser or cloud credentials needed."""
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ui_multi_validation_runner.py"

def test_ui_audit_uses_configurable_cloud_portable_output():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'SYSTEM3_UI_PROOF_DIR' in source
    assert 'Path(__file__).resolve().parents[1]' in source
    assert 'C:\\Users\\ADMIN' not in source
