"""Portable UI static audit contract; not browser-runtime certification."""
from pathlib import Path
import os
import subprocess
import sys
import json

def test_ui_audit_runs_in_linux_and_writes_27_surface_report(tmp_path):
    root=Path(__file__).resolve().parents[1]
    env={**os.environ,"GENESIS_AUDIT_OUTPUT_DIR":str(tmp_path)}
    run=subprocess.run([sys.executable,"scripts/audit_27_tabs.py"],cwd=root,env=env,text=True,capture_output=True,timeout=40)
    assert run.returncode==0,run.stderr
    path=tmp_path/"05_27_TABS_AUDIT.json"
    assert path.exists()
    rows=json.loads(path.read_text(encoding="utf-8"))
    assert len(rows)==27
    assert len({r["tab"] for r in rows})==27
    assert all("status" in r and "violations" in r for r in rows)
