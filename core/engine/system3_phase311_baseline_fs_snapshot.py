"""
System3 Phase 311 - Baseline Filesystem Snapshot

Creates a daily filesystem baseline of key System3 files before market,
to detect unexpected edits and support rollback.
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Output directories
BASELINE_DIR = PROJECT_ROOT / "storage" / "system_health" / "fs_baseline"
BASELINE_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "integrity"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Paths to include in snapshot
INCLUDE_PATHS = [
    "core",
    "engine",
    "config",
    "storage/live/schemas",
]

# Patterns to exclude (logs, cache, large data)
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "logs",
    "backups",
    "*.log",
    "venv",
    ".git",
    "storage/raw",
    "storage/archive",
]


def should_exclude(path: Path) -> bool:
    """Check if path matches any exclude pattern."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file in chunks."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return ""


def scan_directory(base_path: Path, relative_to: Path) -> List[Dict[str, Any]]:
    """Recursively scan directory and collect file metadata."""
    files = []

    if not base_path.exists():
        logger.warning(f"Path does not exist: {base_path}")
        return files

    try:
        for item in base_path.rglob("*"):
            if item.is_file() and not should_exclude(item):
                try:
                    stat = item.stat()
                    rel_path = item.relative_to(relative_to)

                    files.append(
                        {
                            "path": str(rel_path).replace("\\", "/"),
                            "size_bytes": stat.st_size,
                            "mtime_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "sha256": compute_sha256(item),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to process {item}: {e}")
    except Exception as e:
        logger.error(f"Failed to scan {base_path}: {e}")

    return files


def run_phase311(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 311: Baseline Filesystem Snapshot

    Returns:
        dict: {
            "phase": 311,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {"snapshot_file": path, "file_count": N},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        today = datetime.now().strftime("%Y%m%d")
        snapshot_file = BASELINE_DIR / f"fs_snapshot_{today}.json"
        log_file = LOG_DIR / f"fs_snapshot_{today}.log"

        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.info("Phase 311: Starting filesystem baseline snapshot")

        all_files = []

        # Scan each included path
        for path_str in INCLUDE_PATHS:
            target_path = PROJECT_ROOT / path_str
            logger.info(f"Scanning: {target_path}")
            files = scan_directory(target_path, PROJECT_ROOT)
            all_files.extend(files)
            logger.info(f"  Found {len(files)} files")

        # Also include top-level .md and .py files
        for item in PROJECT_ROOT.glob("*.md"):
            if not should_exclude(item):
                try:
                    stat = item.stat()
                    all_files.append(
                        {
                            "path": item.name,
                            "size_bytes": stat.st_size,
                            "mtime_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "sha256": compute_sha256(item),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to process {item}: {e}")

        for item in PROJECT_ROOT.glob("*.py"):
            if not should_exclude(item):
                try:
                    stat = item.stat()
                    all_files.append(
                        {
                            "path": item.name,
                            "size_bytes": stat.st_size,
                            "mtime_iso": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "sha256": compute_sha256(item),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to process {item}: {e}")

        # Create snapshot
        snapshot = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "total_files": len(all_files),
            "total_size_bytes": sum(f["size_bytes"] for f in all_files),
            "files": sorted(all_files, key=lambda x: x["path"]),
        }

        # Write snapshot
        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        logger.info(f"Snapshot complete: {len(all_files)} files, " f"{snapshot['total_size_bytes']:,} bytes")
        logger.info(f"Snapshot saved to: {snapshot_file}")

        outputs = {
            "snapshot_file": str(snapshot_file),
            "file_count": len(all_files),
            "total_size_bytes": snapshot["total_size_bytes"],
            "log_file": str(log_file),
        }

        # Remove handler
        logger.removeHandler(file_handler)
        file_handler.close()

        return {
            "phase": 311,
            "status": "OK",
            "details": f"Filesystem snapshot created: {len(all_files)} files scanned",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 311 error: {e}", exc_info=True)
        return {
            "phase": 311,
            "status": "ERROR",
            "details": f"Phase 311 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase311()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
    if result["outputs"]:
        print(f"Outputs: {json.dumps(result['outputs'], indent=2)}")
