from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_public_dashboard_no_key_forensic_gate_passes_current_tree():
    proc = subprocess.run(
        [sys.executable, "scripts/public_dashboard_no_key_forensic.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "PUBLIC_DASHBOARD_NO_KEY_FORENSIC" in proc.stdout
    assert '"dashboard_credential_authority": "REMOVED"' in proc.stdout
    assert '"server_session_authority": "REMOVED"' in proc.stdout
    assert '"live_mutation": "HARD_DENY"' in proc.stdout


def test_obsolete_authenticated_dashboard_tools_are_absent():
    for relative in (
        "tools/dashboard_auth_smoke.py",
        "tools/dashboard_authenticated_shell_warmup.mjs",
        "tools/dashboard_live_ui_proof.mjs",
        "tools/dashboard_shell_diagnostic.mjs",
        "tools/dashboard_visible_issue_tracker.mjs",
        "scripts/verify_dashboard.ps1",
    ):
        assert not (ROOT / relative).exists(), relative
