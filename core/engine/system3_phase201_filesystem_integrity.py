"""
System3 Phase 201 - Filesystem Integrity Verifier

Scans all core System3 directories and verifies mandatory folders exist.
Auto-creates missing non-critical directories.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Output path
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_fs_integrity_report.md"

# Critical directories (must exist)
CRITICAL_DIRS = [
    PROJECT_ROOT / "core",
    PROJECT_ROOT / "storage",
    PROJECT_ROOT / "logs",
    PROJECT_ROOT / "config",
]

# Non-critical directories (auto-create if missing)
NON_CRITICAL_DIRS = [
    PROJECT_ROOT / "core" / "engine",
    PROJECT_ROOT / "core" / "ultra",
    PROJECT_ROOT / "core" / "models",
    PROJECT_ROOT / "storage" / "live",
    PROJECT_ROOT / "storage" / "archive",
    PROJECT_ROOT / "storage" / "meta",
    PROJECT_ROOT / "storage" / "config",
    PROJECT_ROOT / "storage" / "ultra",
    PROJECT_ROOT / "logs" / "config",
    PROJECT_ROOT / "logs" / "data_cleaning",
    PROJECT_ROOT / "logs" / "history",
    PROJECT_ROOT / "logs" / "ml",
    PROJECT_ROOT / "logs" / "risk",
    PROJECT_ROOT / "logs" / "research",
    PROJECT_ROOT / "logs" / "performance",
    PROJECT_ROOT / "logs" / "data",
    PROJECT_ROOT / "logs" / "brokers",
    PROJECT_ROOT / "logs" / "env",
    PROJECT_ROOT / "logs" / "models",
    PROJECT_ROOT / "logs" / "meta",
    PROJECT_ROOT / "logs" / "signals",
]


def run_phase201(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 201: Filesystem Integrity Verifier.

    Returns:
        dict: {
            "phase": 201,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "missing_critical_count": int,
                "created_dirs": list,
            },
            "errors": [],
        }
    """
    errors = []
    missing_critical = []
    created_dirs = []

    try:
        # Check critical directories
        for dir_path in CRITICAL_DIRS:
            if not dir_path.exists():
                missing_critical.append(str(dir_path))
            elif not dir_path.is_dir():
                missing_critical.append(f"{dir_path} (exists but not a directory)")

        # Auto-create non-critical directories
        for dir_path in NON_CRITICAL_DIRS:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(str(dir_path))
                except Exception as e:
                    errors.append(f"Failed to create {dir_path}: {e}")

        # Generate report
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Filesystem Integrity Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Critical Directories\n\n")
            if missing_critical:
                f.write("### ❌ MISSING CRITICAL DIRECTORIES\n\n")
                for missing in missing_critical:
                    f.write(f"- `{missing}`\n")
            else:
                f.write("### ✅ All Critical Directories Present\n\n")
                for dir_path in CRITICAL_DIRS:
                    f.write(f"- `{dir_path}` ✅\n")

            f.write("\n## Non-Critical Directories\n\n")
            if created_dirs:
                f.write(f"### ✅ Created {len(created_dirs)} Non-Critical Directories\n\n")
                for created in created_dirs:
                    f.write(f"- `{created}` ✅\n")
            else:
                f.write("### ✅ All Non-Critical Directories Present\n\n")

            f.write("\n## Summary\n\n")
            f.write(f"- **Missing Critical**: {len(missing_critical)}\n")
            f.write(f"- **Created Non-Critical**: {len(created_dirs)}\n")

            if missing_critical:
                f.write("\n⚠️ **ACTION REQUIRED**: Missing critical directories must be created manually.\n")
            else:
                f.write("\n✅ **STATUS**: Filesystem integrity verified.\n")

        # Determine status
        if missing_critical:
            status = "ERROR"
            details = f"Missing {len(missing_critical)} critical directory(ies)"
        elif errors:
            status = "WARN"
            details = f"Created {len(created_dirs)} directories with {len(errors)} error(s)"
        else:
            status = "OK"
            details = f"Filesystem integrity verified. Created {len(created_dirs)} non-critical directories"

        return {
            "phase": 201,
            "status": status,
            "details": details,
            "outputs": {
                "missing_critical_count": len(missing_critical),
                "created_dirs": created_dirs,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 201,
            "status": "ERROR",
            "details": f"Phase 201 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 201 - FILESYSTEM INTEGRITY VERIFIER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase201()

    print(f"Phase 201: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Missing Critical: {result['outputs']['missing_critical_count']}")
        print(f"Created Dirs: {len(result['outputs']['created_dirs'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
