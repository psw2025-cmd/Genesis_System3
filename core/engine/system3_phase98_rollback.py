"""
System3 Phase 98 - Rollback Mechanism

Read backup manifest and print rollback plan (dry-run only).
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
RECOVERY_POINTS_DIR = STORAGE_ULTRA / "recovery_points"
MANIFEST_JSON = STORAGE_ULTRA / "phase97_backup_manifest.json"

# Output file
OUTPUT_MD = STORAGE_ULTRA / "phase98_rollback_plan.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)


def find_backup(backup_id: str) -> Optional[Dict[str, Any]]:
    """Find backup by ID or 'latest'."""
    if backup_id == "latest":
        if not MANIFEST_JSON.exists():
            return None
        try:
            with MANIFEST_JSON.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    else:
        # Find by ID
        backup_dir = RECOVERY_POINTS_DIR / backup_id
        if backup_dir.exists():
            return {
                "backup_id": backup_id,
                "backup_dir": str(backup_dir),
                "files": list(backup_dir.glob("*")),
            }
        return None


def generate_rollback_plan(backup_id: str) -> None:
    """Generate rollback plan."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 98 - ROLLBACK MECHANISM")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Find backup
    backup = find_backup(backup_id)
    if not backup:
        print(f"[PH98] Backup not found: {backup_id}")
        return

    # Generate rollback plan
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 98 - Rollback Plan\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Backup ID**: {backup['backup_id']}\n\n")

        f.write("## Files to Restore\n\n")
        f.write("| Source File | Target Path | Manual Command |\n")
        f.write("|-------------|------------|----------------|\n")

        backup_dir = Path(backup["backup_dir"])
        files = backup.get("files", [])

        for file_path_str in files:
            if isinstance(file_path_str, str):
                source_file = backup_dir / Path(file_path_str).name
                target_file = PROJECT_ROOT / file_path_str

                if source_file.exists():
                    # Windows copy command
                    cmd = f'copy "{source_file}" "{target_file}"'
                    f.write(f"| {source_file.name} | {file_path_str} | `{cmd}` |\n")

    print(f"[PH98] Generated rollback plan for backup={backup_id}")
    print(f"[PH98] Rollback plan written to {OUTPUT_MD}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 98 - Rollback Mechanism")
    parser.add_argument("--backup", type=str, default="latest", help="Backup ID or 'latest'")

    args = parser.parse_args()

    try:
        generate_rollback_plan(args.backup)
        print("\n[PH98] Rollback plan generation complete.")
        return 0
    except Exception as e:
        print(f"\n[PH98] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
