"""System3 Phase 174 - Retention Policy"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase174_retention_policy_report.md"


def run_phase174_retention_policy() -> Dict[str, Any]:
    errors = []
    try:
        cutoff_date = datetime.now() - timedelta(days=90)  # 90-day retention
        files_to_archive = []
        if STORAGE_ULTRA.exists():
            for file_path in STORAGE_ULTRA.glob("*"):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        files_to_archive.append(file_path.name)
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write(
                f"# System3 Phase 174 - Retention Policy Report\n\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )
            f.write(f"Retention cutoff: {cutoff_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Files eligible for archiving: {len(files_to_archive)}\n")
            f.write("**NOTE**: No files deleted - manual action required.\n")
        return {
            "phase": 174,
            "status": "OK",
            "details": f"Retention policy: {len(files_to_archive)} files eligible",
            "outputs": {"md_path": str(OUTPUT_MD_PATH), "files_eligible": len(files_to_archive)},
            "errors": errors,
        }
    except Exception as e:
        return {"phase": 174, "status": "ERROR", "details": f"Phase 174 failed: {e}", "outputs": {}, "errors": [str(e)]}


def main():
    print("=" * 70)
    print("SYSTEM3 PHASE 174 - RETENTION POLICY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    result = run_phase174_retention_policy()
    print(f"Phase174: {result['details']}")
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
