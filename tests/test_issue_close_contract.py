"""Close-contract for PR #514 follow-up fixes (no backend deps required)."""
import os
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(rel):
    with open(os.path.join(REPO_ROOT, rel), "r", encoding="utf-8") as f:
        return f.read()


def test_strict_flags_helper_exists():
    src = read("dashboard/frontend/src/lib/strictFlags.ts")
    for token in [
        "isLiveFlagOn",
        "asRecord",
        "getResponseStatus",
        "getErrorMessage",
        "gainValue",
    ]:
        assert token in src, f"missing {token} in strictFlags.ts"


def test_lifecycle_truth_no_any_cast():
    src = read("dashboard/frontend/src/lib/lifecycleTruth.ts")
    assert "as any" not in src, "lifecycleTruth still contains `as any`"
    assert "isLiveFlagOn" in src
    assert "Record<string, unknown>" in src
    # ISSUE-04: banner must not claim script file is missing (file exists)
    assert "scripts/run_paper_validation.py is missing" not in src
    assert "run scripts/run_paper_validation.py to generate fresh" in src


def test_system_truth_uses_typed_flag():
    src = read("dashboard/frontend/src/components/SystemTruthControl.tsx")
    assert "isLiveFlagOn(liveFlag)" in src
    assert "(liveFlag as any)" not in src


def test_usedata_no_null_any():
    src = read("dashboard/frontend/src/hooks/useData.ts")
    assert "null as any" not in src


def test_signals_uses_typed_helpers():
    src = read("dashboard/frontend/src/components/Signals.tsx")
    assert "getResponseStatus(stateRes.reason)" in src
    assert "getErrorMessage(scannerRes.reason)" in src
    assert "(stateRes.reason as any)" not in src


def test_dist_ignored_and_untracked():
    gitignore = read(".gitignore")
    assert "dashboard/frontend/dist/" in gitignore
    proc = subprocess.run(
        ["git", "ls-files", "dashboard/frontend/dist"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == "", f"dist still tracked: {proc.stdout.strip()}"


def test_e2e_has_skip_guards():
    src = read("tests/test_micro_level_flow_diagram.py")
    assert "backend_or_skip" in src
    assert "importorskip" in src
