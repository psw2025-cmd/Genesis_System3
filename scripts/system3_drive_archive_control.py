#!/usr/bin/env python3
"""Fail-closed System3 source/log archival queue for private Google Drive.

This controller never authenticates to Drive and never treats a local sync copy
as remote proof. A Drive-capable agent uploads each staged part, downloads and
hashes it, then supplies a metadata receipt. Source cleanup requires that exact
receipt plus an explicit deletion gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARCHIVE_SCHEMA = "SYSTEM3_DRIVE_ARCHIVE_V1"
RECEIPT_SCHEMA = "SYSTEM3_DRIVE_RECEIPT_V1"
DEFAULT_CHUNK_BYTES = 5 * 1024 * 1024
LOG_SUFFIXES = {".log", ".txt", ".json", ".jsonl", ".csv"}
SECRET_LIKE = re.compile(
    r"(^|[._-])(access[_-]?token|refresh[_-]?token|secret|credential|password|passwd|"
    r"private[_-]?key|service[_-]?account|\.env)([._-]|$)",
    re.IGNORECASE,
)


class ArchiveError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args], stderr=subprocess.STDOUT, text=True
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise ArchiveError(f"GIT_ERROR: {exc.output.strip()}") from exc


def reject_secret_like(path: Path) -> None:
    for part in path.parts:
        if SECRET_LIKE.search(part):
            raise ArchiveError(f"SECRET_LIKE_PATH: {path}")


def is_secret_like(path: Path) -> bool:
    return any(SECRET_LIKE.search(part) for part in path.parts)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "archive"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stage_file(source: Path, queue: Path, chunk_bytes: int, kind: str, git_sha: str | None = None) -> Path:
    source = source.resolve(strict=True)
    reject_secret_like(source)
    if not source.is_file():
        raise ArchiveError(f"SOURCE_NOT_FILE: {source}")
    if chunk_bytes < 1024:
        raise ArchiveError("CHUNK_TOO_SMALL")

    source_hash = sha256(source)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = queue.resolve() / f"{stamp}_{safe_name(source.name)}_{source_hash[:12]}"
    bundle.mkdir(parents=True, exist_ok=False)
    parts: list[dict[str, Any]] = []
    with source.open("rb") as handle:
        index = 1
        while True:
            block = handle.read(chunk_bytes)
            if not block:
                break
            name = f"{safe_name(source.name)}.part{index:04d}"
            part_path = bundle / name
            part_path.write_bytes(block)
            parts.append({"name": name, "size": len(block), "sha256": sha256(part_path)})
            index += 1

    manifest = {
        "schema": ARCHIVE_SCHEMA,
        "created_at_utc": utc_now(),
        "archive_kind": kind,
        "git_sha": git_sha,
        "source": {"path": str(source), "size": source.stat().st_size, "sha256": source_hash},
        "parts": parts,
        "drive_contract": {
            "private_owner_only": True,
            "remote_content_hash_required": True,
            "remote_size_required": True,
            "remote_parent_required": True,
            "local_sync_state_alone_sufficient": False,
        },
        "cleanup_state": "WAITING_FOR_VERIFIED_DRIVE_RECEIPT",
    }
    manifest_path = bundle / "manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path


def snapshot(repo: Path, queue: Path, chunk_bytes: int) -> Path:
    repo = repo.resolve(strict=True)
    if git(repo, "status", "--porcelain"):
        raise ArchiveError("DIRTY_WORKTREE: snapshot only exact committed cloud truth")
    head = git(repo, "rev-parse", "HEAD")
    try:
        origin_main = git(repo, "rev-parse", "origin/main")
    except ArchiveError:
        origin_main = ""
    if not origin_main or head != origin_main:
        raise ArchiveError(f"NOT_EXACT_ORIGIN_MAIN: head={head} origin_main={origin_main}")

    tracked = git(repo, "ls-tree", "-r", "--name-only", head).splitlines()
    exclusions = sorted(name for name in tracked if is_secret_like(Path(name)))

    queue.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="system3-source-snapshot-") as temp_dir:
        raw_archive = Path(temp_dir) / f"Genesis_System3_{head}.raw.zip"
        archive = Path(temp_dir) / f"Genesis_System3_{head}.zip"
        try:
            subprocess.run(
                ["git", "-C", str(repo), "archive", "--format=zip", f"--output={raw_archive}", head],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise ArchiveError(f"GIT_ARCHIVE_FAILED: {exc.stderr}") from exc
        with zipfile.ZipFile(raw_archive, "r") as source_zip, zipfile.ZipFile(
            archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as safe_zip:
            for info in source_zip.infolist():
                if info.is_dir() or is_secret_like(Path(info.filename)):
                    continue
                safe_zip.writestr(info, source_zip.read(info.filename))
        manifest_path = stage_file(archive, queue, chunk_bytes, "EXACT_ORIGIN_MAIN_SOURCE_SNAPSHOT", head)
        manifest = load_json(manifest_path)
        manifest["source"] = {
            "path": f"git:{repo}@{head}",
            "size": archive.stat().st_size,
            "sha256": sha256(archive),
        }
        manifest["snapshot"] = {
            "source_authority": "github_origin_main",
            "tracked_path_count": len(tracked),
            "secret_like_paths_excluded": exclusions,
            "complete_tracked_snapshot": not exclusions,
            "source_cleanup_allowed": False,
        }
        write_json(manifest_path, manifest)
        return manifest_path


def trigger(
    log_roots: list[Path],
    queue: Path,
    free_threshold_gib: float,
    min_bytes: int,
    min_age_hours: float,
    chunk_bytes: int,
) -> dict[str, Any]:
    if not log_roots:
        raise ArchiveError("LOG_ROOT_REQUIRED")
    queue.mkdir(parents=True, exist_ok=True)
    anchor = log_roots[0].resolve(strict=True)
    free_gib = shutil.disk_usage(anchor).free / (1024**3)
    if free_gib >= free_threshold_gib:
        return {"status": "NO_TRIGGER_FREE_SPACE_OK", "free_gib": round(free_gib, 3), "manifests": []}

    cutoff = time.time() - min_age_hours * 3600
    existing: set[tuple[str, str]] = set()
    for manifest_path in queue.glob("*/manifest.json"):
        try:
            manifest = load_json(manifest_path)
            existing.add((manifest["source"]["path"].casefold(), manifest["source"]["sha256"]))
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            continue

    manifests: list[str] = []
    for root in log_roots:
        root = root.resolve(strict=True)
        for source in sorted(root.rglob("*")):
            if source.is_symlink() or not source.is_file() or source.suffix.casefold() not in LOG_SUFFIXES:
                continue
            reject_secret_like(source.relative_to(root))
            stat = source.stat()
            if stat.st_size < min_bytes or stat.st_mtime > cutoff:
                continue
            digest = sha256(source)
            if (str(source).casefold(), digest) in existing:
                continue
            manifests.append(str(stage_file(source, queue, chunk_bytes, "LOW_SPACE_LOG_TRIGGER")))
    return {
        "status": "LOW_SPACE_STAGED_WAITING_FOR_DRIVE" if manifests else "LOW_SPACE_NO_ELIGIBLE_LOGS",
        "free_gib": round(free_gib, 3),
        "manifests": manifests,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_receipt(
    manifest_path: Path,
    receipt_path: Path,
    expected_owner: str,
    expected_parent_id: str,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    receipt = load_json(receipt_path)
    if manifest.get("schema") != ARCHIVE_SCHEMA:
        raise ArchiveError("INVALID_ARCHIVE_SCHEMA")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise ArchiveError("INVALID_RECEIPT_SCHEMA")
    if receipt.get("shared") is not False:
        raise ArchiveError("DRIVE_OBJECT_SHARED")
    if receipt.get("owner", "").casefold() != expected_owner.casefold():
        raise ArchiveError("DRIVE_OWNER_MISMATCH")
    if not receipt.get("verified_at_utc"):
        raise ArchiveError("MISSING_REMOTE_VERIFICATION_TIME")

    expected = {part["name"]: part for part in manifest.get("parts", [])}
    actual = {part.get("name"): part for part in receipt.get("parts", [])}
    if set(expected) != set(actual):
        raise ArchiveError("DRIVE_PART_SET_MISMATCH")
    for name, local in expected.items():
        remote = actual[name]
        if remote.get("size") != local["size"]:
            raise ArchiveError(f"DRIVE_SIZE_MISMATCH: {name}")
        if remote.get("sha256", "").casefold() != local["sha256"].casefold():
            raise ArchiveError(f"DRIVE_SHA256_MISMATCH: {name}")
        if remote.get("drive_parent_id") != expected_parent_id:
            raise ArchiveError(f"DRIVE_PARENT_MISMATCH: {name}")
        if not remote.get("drive_file_id"):
            raise ArchiveError(f"MISSING_DRIVE_FILE_ID: {name}")
    return {
        "status": "PASS",
        "manifest": str(manifest_path.resolve()),
        "receipt": str(receipt_path.resolve()),
        "verified_parts": len(expected),
        "source_sha256": manifest["source"]["sha256"],
    }


def cleanup(
    manifest_path: Path,
    receipt_path: Path | None,
    expected_owner: str,
    expected_parent_id: str,
    delete_source: bool,
) -> dict[str, Any]:
    if receipt_path is None:
        raise ArchiveError("VERIFIED_DRIVE_RECEIPT_REQUIRED")
    result = verify_receipt(manifest_path, receipt_path, expected_owner, expected_parent_id)
    manifest = load_json(manifest_path)
    if manifest.get("archive_kind") == "EXACT_ORIGIN_MAIN_SOURCE_SNAPSHOT":
        raise ArchiveError("SOURCE_CLEANUP_FORBIDDEN_FOR_REPOSITORY_SNAPSHOT")
    source = Path(manifest["source"]["path"])
    if not delete_source:
        return {**result, "status": "VERIFIED_NO_DELETE"}
    if not source.exists() or not source.is_file():
        raise ArchiveError("SOURCE_MISSING_OR_NOT_FILE")
    reject_secret_like(source)
    if source.stat().st_size != manifest["source"]["size"] or sha256(source) != manifest["source"]["sha256"]:
        raise ArchiveError("SOURCE_CHANGED_AFTER_STAGING")
    source.unlink()
    return {**result, "status": "DELETED_VERIFIED_SOURCE", "deleted_source": str(source)}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    stage = commands.add_parser("stage")
    stage.add_argument("--source", type=Path, required=True)
    stage.add_argument("--queue", type=Path, required=True)
    stage.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    snap = commands.add_parser("snapshot")
    snap.add_argument("--repo", type=Path, required=True)
    snap.add_argument("--queue", type=Path, required=True)
    snap.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    trigger_cmd = commands.add_parser("trigger")
    trigger_cmd.add_argument("--log-root", type=Path, action="append", required=True)
    trigger_cmd.add_argument("--queue", type=Path, required=True)
    trigger_cmd.add_argument("--free-threshold-gib", type=float, default=20.0)
    trigger_cmd.add_argument("--min-bytes", type=int, default=10 * 1024 * 1024)
    trigger_cmd.add_argument("--min-age-hours", type=float, default=24.0)
    trigger_cmd.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK_BYTES)
    for name in ("verify", "cleanup"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--manifest", type=Path, required=True)
        cmd.add_argument("--receipt", type=Path, required=name == "verify")
        cmd.add_argument("--expected-owner", required=True)
        cmd.add_argument("--expected-parent-id", required=True)
        if name == "cleanup":
            cmd.add_argument("--delete-source", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "stage":
            manifest = stage_file(args.source, args.queue, args.chunk_bytes, "EXPLICIT_LOG_OR_EVIDENCE")
            result = {"status": "STAGED_WAITING_FOR_DRIVE", "manifest": str(manifest)}
        elif args.command == "snapshot":
            manifest = snapshot(args.repo, args.queue, args.chunk_bytes)
            result = {"status": "STAGED_WAITING_FOR_DRIVE", "manifest": str(manifest)}
        elif args.command == "trigger":
            result = trigger(
                args.log_root,
                args.queue,
                args.free_threshold_gib,
                args.min_bytes,
                args.min_age_hours,
                args.chunk_bytes,
            )
        elif args.command == "verify":
            result = verify_receipt(args.manifest, args.receipt, args.expected_owner, args.expected_parent_id)
        else:
            result = cleanup(
                args.manifest,
                args.receipt,
                args.expected_owner,
                args.expected_parent_id,
                args.delete_source,
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ArchiveError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
