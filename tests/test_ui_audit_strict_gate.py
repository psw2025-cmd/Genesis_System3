"""The UI audit must not silently pass known violations when strict mode is used."""
import importlib.util
from pathlib import Path

def _module():
    path=Path(__file__).resolve().parents[1]/"scripts"/"audit_27_tabs.py"
    spec=importlib.util.spec_from_file_location("genesis_ui_audit",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_strict_mode_rejects_missing_surface():
    audit=_module()
    assert audit.audit_exit_code([{"pass":False,"status":"MISSING_FILE"}],strict=True)==1

def test_strict_mode_rejects_false_claims():
    audit=_module()
    assert audit.audit_exit_code([{"pass":False,"status":"VIOLATION"}],strict=True)==1

def test_strict_mode_accepts_all_pass():
    audit=_module()
    assert audit.audit_exit_code([{"pass":True} for _ in range(27)],strict=True)==0

def test_report_only_mode_preserved():
    audit=_module()
    assert audit.audit_exit_code([{"pass":False}],strict=False)==0
