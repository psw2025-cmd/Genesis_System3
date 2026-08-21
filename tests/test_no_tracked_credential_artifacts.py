from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    ).strip()


def test_generated_scan_dump_is_not_tracked() -> None:
    tracked = set(_git("ls-files").splitlines())
    assert "scan_output.txt" not in tracked


def test_generated_scan_dump_is_ignored() -> None:
    ignored_by = _git("check-ignore", "-v", "--no-index", "scan_output.txt")
    assert "/scan_output.txt" in ignored_by
