from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "system3_drive_archive_control.py"
RUNBOOK = ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def test_stage_chunks_and_manifest_are_reproducible(tmp_path: Path) -> None:
    source = tmp_path / "logs" / "historical.log"
    source.parent.mkdir()
    source.write_bytes(b"abcdef" * 1000)
    queue = tmp_path / "queue"

    result = run(
        "stage",
        "--source",
        str(source),
        "--queue",
        str(queue),
        "--chunk-bytes",
        "1024",
    )
    manifest_path = Path(json.loads(result.stdout)["manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["schema"] == "SYSTEM3_DRIVE_ARCHIVE_V1"
    assert manifest["source"]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert len(manifest["parts"]) == 6
    assert sum(part["size"] for part in manifest["parts"]) == source.stat().st_size
    for part in manifest["parts"]:
        path = manifest_path.parent / part["name"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == part["sha256"]


def test_secret_like_source_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "access-token.log"
    source.write_text("redacted", encoding="utf-8")
    result = run("stage", "--source", str(source), "--queue", str(tmp_path / "q"), check=False)
    assert result.returncode != 0
    assert "SECRET_LIKE_PATH" in result.stderr


def test_cleanup_fails_closed_without_verified_private_receipt(tmp_path: Path) -> None:
    source = tmp_path / "logs" / "old.log"
    source.parent.mkdir()
    source.write_bytes(b"x" * 4096)
    queue = tmp_path / "queue"
    manifest_path = Path(json.loads(run("stage", "--source", str(source), "--queue", str(queue)).stdout)["manifest"])

    missing = run("cleanup", "--manifest", str(manifest_path), check=False)
    assert missing.returncode != 0
    assert source.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = {
        "schema": "SYSTEM3_DRIVE_RECEIPT_V1",
        "owner": "owner@example.com",
        "shared": True,
        "verified_at_utc": "2026-08-24T00:00:00Z",
        "parts": [
            {
                "name": part["name"],
                "size": part["size"],
                "sha256": part["sha256"],
                "drive_file_id": "id",
                "drive_parent_id": "parent",
            }
            for part in manifest["parts"]
        ],
    }
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    shared = run(
        "cleanup",
        "--manifest",
        str(manifest_path),
        "--receipt",
        str(receipt_path),
        "--expected-owner",
        "owner@example.com",
        "--expected-parent-id",
        "parent",
        "--delete-source",
        check=False,
    )
    assert shared.returncode != 0
    assert "DRIVE_OBJECT_SHARED" in shared.stderr
    assert source.exists()


def test_cleanup_requires_exact_remote_sha_and_deletes_only_with_explicit_gate(tmp_path: Path) -> None:
    source = tmp_path / "logs" / "old.log"
    source.parent.mkdir()
    source.write_bytes(b"archive-me" * 1000)
    manifest_path = Path(
        json.loads(
            run(
                "stage",
                "--source",
                str(source),
                "--queue",
                str(tmp_path / "queue"),
                "--chunk-bytes",
                "2048",
            ).stdout
        )["manifest"]
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = {
        "schema": "SYSTEM3_DRIVE_RECEIPT_V1",
        "owner": "owner@example.com",
        "shared": False,
        "verified_at_utc": "2026-08-24T00:00:00Z",
        "parts": [
            {
                "name": part["name"],
                "size": part["size"],
                "sha256": part["sha256"],
                "drive_file_id": f"id-{index}",
                "drive_parent_id": "parent",
            }
            for index, part in enumerate(manifest["parts"])
        ],
    }
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

    verify = run(
        "verify",
        "--manifest",
        str(manifest_path),
        "--receipt",
        str(receipt_path),
        "--expected-owner",
        "owner@example.com",
        "--expected-parent-id",
        "parent",
    )
    assert json.loads(verify.stdout)["status"] == "PASS"
    assert source.exists()

    cleanup = run(
        "cleanup",
        "--manifest",
        str(manifest_path),
        "--receipt",
        str(receipt_path),
        "--expected-owner",
        "owner@example.com",
        "--expected-parent-id",
        "parent",
        "--delete-source",
    )
    assert json.loads(cleanup.stdout)["status"] == "DELETED_VERIFIED_SOURCE"
    assert not source.exists()


def test_source_snapshot_refuses_dirty_or_non_authoritative_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "a.txt").write_text("one", encoding="utf-8")
    subprocess.run(["git", "add", "a.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "one"], cwd=repo, check=True, capture_output=True)
    (repo / "a.txt").write_text("dirty", encoding="utf-8")

    result = run("snapshot", "--repo", str(repo), "--queue", str(tmp_path / "queue"), check=False)
    assert result.returncode != 0
    assert "DIRTY_WORKTREE" in result.stderr


def test_low_space_trigger_stages_only_old_allowlisted_log_types(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    old = logs / "old.log"
    old.write_bytes(b"z" * 4096)
    recent = logs / "recent.log"
    recent.write_bytes(b"r" * 4096)
    ignored = logs / "database.db"
    ignored.write_bytes(b"d" * 4096)
    os_time = 1_700_000_000
    import os

    os.utime(old, (os_time, os_time))
    result = run(
        "trigger",
        "--log-root",
        str(logs),
        "--queue",
        str(tmp_path / "queue"),
        "--free-threshold-gib",
        "999999",
        "--min-bytes",
        "1024",
        "--min-age-hours",
        "24",
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "LOW_SPACE_STAGED_WAITING_FOR_DRIVE"
    assert len(payload["manifests"]) == 1
    manifest = json.loads(Path(payload["manifests"][0]).read_text(encoding="utf-8"))
    assert manifest["source"]["path"] == str(old.resolve())
    assert old.exists()
    assert recent.exists()
    assert ignored.exists()


def test_runbook_locks_drive_archive_authority_and_cleanup_receipt() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    for marker in (
        "Google Drive is an **archive/recovery surface only**",
        "GitHub `main` remains the",
        "SYSTEM3_DRIVE_ARCHIVE_V1",
        "SYSTEM3_DRIVE_RECEIPT_V1",
        "shared=false",
        "--delete-source",
        "Google Drive Desktop local-sync state alone is never",
        "service-account",
    ):
        assert marker in text
