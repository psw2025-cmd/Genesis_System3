"""System3 Phase 171 - File Backup"""

import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_BACKUPS = PROJECT_ROOT / "storage" / "backups" / "system3"
STORAGE_BACKUPS.mkdir(parents=True, exist_ok=True)
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase171_file_backup_report.md"


def run_phase171_file_backup() -> Dict[str, Any]:
    errors = []
    try:
        backup_count = 0
        if STORAGE_ULTRA.exists():
            backup_dir = STORAGE_BACKUPS / datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir.mkdir(parents=True, exist_ok=True)
            for file_path in STORAGE_ULTRA.glob("*.csv"):
                if file_path.is_file():
                    shutil.copy2(file_path, backup_dir / file_path.name)
                    backup_count += 1
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write(
                f"# System3 Phase 171 - File Backup Report\n\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(f"Files backed up: {backup_count}\n")
        return {
            "phase": 171,
            "status": "OK",
            "details": f"File backup: {backup_count} files",
            "outputs": {"md_path": str(OUTPUT_MD_PATH), "backup_count": backup_count},
            "errors": errors,
        }
    except Exception as e:
        return {"phase": 171, "status": "ERROR", "details": f"Phase 171 failed: {e}", "outputs": {}, "errors": [str(e)]}


def main():
    print("=" * 70)
    print("SYSTEM3 PHASE 171 - FILE BACKUP")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    result = run_phase171_file_backup()
    print(f"Phase171: {result['details']}")
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
