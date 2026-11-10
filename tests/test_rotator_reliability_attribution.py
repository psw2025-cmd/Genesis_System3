from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evaluate_rotator_reliability.py"


def _run(tmp_path: Path, *, rows: list[dict], metadata_ok: bool = True, log_categories: dict | None = None):
    source = tmp_path / "audit.json"
    out = tmp_path / "out"
    payload = {
        "rotator": {
            "job_read_ok": metadata_ok,
            "scheduler_read_ok": metadata_ok,
            "execution_list_read_ok": metadata_ok,
            "recent_executions": rows,
        },
        "logs": {"rotator_job": {"categories": log_categories or {}}},
    }
    source.write_text(json.dumps(payload), encoding="utf-8")
    env = os.environ.copy()
    env["SYSTEM3_CLOUD_AUDIT_JSON"] = str(source)
    env["SYSTEM3_ROTATOR_RELIABILITY_DIR"] = str(out)
    env["SYSTEM3_ROTATOR_RELIABILITY_WINDOW"] = "10"
    proc = subprocess.run([sys.executable, str(SCRIPT)], env=env, text=True, capture_output=True, check=False)
    report = json.loads((out / "rotator_reliability.json").read_text(encoding="utf-8"))
    return proc, report


def _success_rows(count: int = 10) -> list[dict]:
    return [
        {"name": f"exec-{i}", "creator": "scheduler", "failedCount": 0, "succeededCount": 1}
        for i in range(count)
    ]


def test_unattributed_audit_wide_log_signatures_do_not_false_fail_recent_successes(tmp_path: Path):
    proc, report = _run(
        tmp_path,
        rows=_success_rows(),
        log_categories={"dhan_auth": 10, "timeout": 198, "restart_or_crash": 1, "rate_limit_text": 9},
    )
    assert proc.returncode == 0
    assert report["state"] == "PASS"
    assert report["success_rate"] == 1.0
    assert report["blockers"] == []
    assert report["log_signatures_block_reliability"] is False
    assert report["log_scope"] == "audit_wide_unattributed_to_recent_execution_window"
    assert report["audit_wide_log_diagnostics"]["timeout"] == 198


def test_recent_failed_execution_remains_hard_failure(tmp_path: Path):
    rows = _success_rows(9) + [
        {"name": "exec-failed", "creator": "scheduler", "failedCount": 1, "succeededCount": 0}
    ]
    proc, report = _run(tmp_path, rows=rows)
    assert proc.returncode == 2
    assert report["state"] == "FAIL"
    assert report["failed_executions"] == 1
    assert "recent_failed_executions=1" in report["blockers"]


def test_insufficient_terminal_sample_fails_closed(tmp_path: Path):
    proc, report = _run(tmp_path, rows=_success_rows(2))
    assert proc.returncode == 2
    assert report["state"] == "FAIL"
    assert "insufficient_terminal_execution_sample" in report["blockers"]


def test_missing_rotator_metadata_fails_closed(tmp_path: Path):
    proc, report = _run(tmp_path, rows=_success_rows(), metadata_ok=False)
    assert proc.returncode == 2
    assert report["state"] == "FAIL"
    assert "rotator_metadata_not_proven" in report["blockers"]
