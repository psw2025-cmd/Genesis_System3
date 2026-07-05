"""
System3 Phase 97 - Backup & Recovery Engine

Create snapshots of key state files for backup.
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
RECOVERY_POINTS_DIR = STORAGE_ULTRA / "recovery_points"
CONFIG_DIR = PROJECT_ROOT / "config"

# Output file
MANIFEST_JSON = STORAGE_ULTRA / "phase97_backup_manifest.json"

RECOVERY_POINTS_DIR.mkdir(parents=True, exist_ok=True)
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Essential files to backup
ESSENTIAL_FILES = [
    "config/dhan_automation_config.json",
    "config/system3_job_scheduler.json",
    "config/system3_operator_override.json",
    "storage/ultra/ph76_ph100/phase79_adaptive_thresholds.json",
]


def create_backup() -> None:
    """Create a backup recovery point."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 97 - BACKUP & RECOVERY ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Create timestamped folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = RECOVERY_POINTS_DIR / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Copy essential files
    backed_up_files = []
    for file_path_str in ESSENTIAL_FILES:
        source_file = PROJECT_ROOT / file_path_str
        if source_file.exists():
            dest_file = backup_dir / source_file.name
            try:
                shutil.copy2(source_file, dest_file)
                backed_up_files.append(file_path_str)
                print(f"[PH97] Backed up: {file_path_str}")
            except Exception as e:
                print(f"[PH97] Error backing up {file_path_str}: {e}")

    # Update manifest
    manifest = {
        "backup_id": timestamp,
        "timestamp": datetime.now().isoformat(),
        "backup_dir": str(backup_dir),
        "files": backed_up_files,
    }

    with MANIFEST_JSON.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[PH97] Created backup recovery_points/{timestamp}")
    print(f"[PH97] Manifest saved to {MANIFEST_JSON}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 97 - Backup & Recovery Engine")
    parser.add_argument("--create-backup", action="store_true", help="Create a backup")

    args = parser.parse_args()

    try:
        if args.create_backup:
            create_backup()
        else:
            parser.print_help()

        print("\n[PH97] Backup operation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH97] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
