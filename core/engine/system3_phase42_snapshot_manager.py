"""
System3 Ultra - Phase 42: Model Snapshot & Rollback Manager

Guarantee we can always roll back: snapshot baseline models + configs before any future
promotion and provide rollback helpers.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Options: 105 (Create), 106 (List)
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
SNAPSHOTS_DIR = PROJECT_ROOT / "storage" / "snapshots"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
LOGS_ULTRA_DIR = PROJECT_ROOT / "storage" / "logs_ultra"

SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_ULTRA_DIR / "system3_phases_39_45.log"


def _log(message: str) -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Phase42] {message}\n"
    print(f"[Phase42] {message}")

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Phase42][WARN] Failed to write log: {e}")


def create_snapshot() -> Path:
    """Create a new snapshot of baseline models and configs."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = SNAPSHOTS_DIR / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    _log(f"Creating snapshot: {timestamp}")

    files_copied = []

    # Copy models
    if MODELS_DIR.exists():
        models_dest = snapshot_dir / "models"
        models_dest.mkdir(parents=True, exist_ok=True)

        for model_file in MODELS_DIR.glob("*_model.pkl"):
            dest = models_dest / model_file.name
            shutil.copy2(model_file, dest)
            files_copied.append(f"models/{model_file.name}")
            _log(f"Copied: {model_file.name}")

        for meta_file in MODELS_DIR.glob("*_meta.json"):
            dest = models_dest / meta_file.name
            shutil.copy2(meta_file, dest)
            files_copied.append(f"models/{meta_file.name}")
            _log(f"Copied: {meta_file.name}")
    else:
        _log("WARN: Models directory not found")

    # Copy configs
    config_dest = snapshot_dir / "configs"
    config_dest.mkdir(parents=True, exist_ok=True)

    # thresholds_auto.json
    thresholds_file = CONFIG_DIR / "thresholds_auto.json"
    if thresholds_file.exists():
        dest = config_dest / "thresholds_auto.json"
        shutil.copy2(thresholds_file, dest)
        files_copied.append(f"configs/thresholds_auto.json")
        _log(f"Copied: thresholds_auto.json")

    # dhan_trade_config.py (as .txt)
    trade_config_file = PROJECT_ROOT / "core" / "engine" / "dhan_trade_config.py"
    if trade_config_file.exists():
        dest = config_dest / "dhan_trade_config.txt"
        shutil.copy2(trade_config_file, dest)
        files_copied.append(f"configs/dhan_trade_config.txt")
        _log(f"Copied: dhan_trade_config.py (as .txt)")

    # Create snapshot metadata
    metadata = {
        "timestamp": timestamp,
        "created": datetime.now().isoformat(),
        "files_copied": files_copied,
        "file_count": len(files_copied),
    }

    meta_file = snapshot_dir / "snapshot_meta.json"
    with meta_file.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    _log(f"Snapshot created: {snapshot_dir} ({len(files_copied)} files)")

    return snapshot_dir


def list_snapshots() -> List[Dict[str, Any]]:
    """List all available snapshots."""
    snapshots = []

    if not SNAPSHOTS_DIR.exists():
        return snapshots

    for snapshot_dir in sorted(SNAPSHOTS_DIR.iterdir(), reverse=True):
        if not snapshot_dir.is_dir():
            continue

        try:
            meta_file = snapshot_dir / "snapshot_meta.json"
            if meta_file.exists():
                with meta_file.open("r", encoding="utf-8") as f:
                    meta = json.load(f)
                snapshots.append(
                    {
                        "name": snapshot_dir.name,
                        "created": meta.get("created", "unknown"),
                        "file_count": meta.get("file_count", 0),
                    }
                )
            else:
                # Fallback: count files
                file_count = sum(1 for _ in snapshot_dir.rglob("*") if _.is_file())
                snapshots.append(
                    {
                        "name": snapshot_dir.name,
                        "created": datetime.fromtimestamp(snapshot_dir.stat().st_mtime).isoformat(),
                        "file_count": file_count,
                    }
                )
        except Exception as e:
            _log(f"Error reading snapshot {snapshot_dir.name}: {e}")

    return snapshots


def find_latest_snapshot_dir() -> Optional[Path]:
    """Find the latest snapshot directory."""
    snapshots = list_snapshots()
    if not snapshots:
        return None

    latest_name = snapshots[0]["name"]
    return SNAPSHOTS_DIR / latest_name


def run_phase42_snapshot_create() -> None:
    """Create a new snapshot."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 42: SNAPSHOT MANAGER (CREATE)")
    print("=" * 60)
    print("\n[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Snapshot is read-only backup\n")

    snapshot_dir = create_snapshot()

    print(f"\n[OK] Phase 42 Snapshot created")
    print(f"[SAVE] Snapshot directory: {snapshot_dir}")
    print(f"\n[INFO] To rollback, manually copy files from snapshot directory to baseline locations")


def run_phase42_snapshot_list() -> None:
    """List all snapshots."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 42: SNAPSHOT MANAGER (LIST)")
    print("=" * 60)
    print()

    snapshots = list_snapshots()

    if not snapshots:
        print("[INFO] No snapshots found")
        return

    print(f"Found {len(snapshots)} snapshot(s):\n")
    print(f"{'Snapshot Name':<25} {'Created':<25} {'Files':<10}")
    print("-" * 60)

    for snap in snapshots:
        print(f"{snap['name']:<25} {snap['created']:<25} {snap['file_count']:<10}")

    print(f"\n[INFO] Latest snapshot: {snapshots[0]['name'] if snapshots else 'None'}")


def main() -> None:
    """CLI entry point."""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "create":
            run_phase42_snapshot_create()
        elif command == "list":
            run_phase42_snapshot_list()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m core.engine.system3_phase42_snapshot_manager [create|list]")
    else:
        print("Usage: python -m core.engine.system3_phase42_snapshot_manager [create|list]")


if __name__ == "__main__":
    main()
