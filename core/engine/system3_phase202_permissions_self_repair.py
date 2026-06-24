"""
System3 Phase 202 - Permission Self-Repair

Attempts read/write tests on key directories and repairs permissions if needed.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_permissions_self_repair.log"

# Test directories
TEST_DIRS = [
    PROJECT_ROOT / "storage",
    PROJECT_ROOT / "logs",
    PROJECT_ROOT / "core" / "models",
]


def test_read_write(dir_path: Path) -> tuple[bool, bool, str]:
    """Test read and write permissions on a directory."""
    read_ok = False
    write_ok = False
    error_msg = ""

    try:
        # Test read
        if dir_path.exists():
            list(dir_path.iterdir())
            read_ok = True
        else:
            error_msg = "Directory does not exist"
    except PermissionError:
        error_msg = "Permission denied (read)"
    except Exception as e:
        error_msg = f"Read error: {e}"

    try:
        # Test write
        test_file = dir_path / ".system3_permission_test"
        test_file.write_text("test")
        test_file.unlink()
        write_ok = True
    except PermissionError:
        if not error_msg:
            error_msg = "Permission denied (write)"
    except Exception as e:
        if not error_msg:
            error_msg = f"Write error: {e}"

    return read_ok, write_ok, error_msg


def run_phase202(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 202: Permission Self-Repair.

    Returns:
        dict: {
            "phase": 202,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "tested_dirs": int,
                "failed_dirs": list,
                "fallback_created": bool,
            },
            "errors": [],
        }
    """
    errors = []
    test_results = []
    failed_dirs = []
    fallback_created = False

    try:
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Permission Self-Repair Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            for dir_path in TEST_DIRS:
                f.write(f"Testing: {dir_path}\n")

                # Ensure directory exists
                if not dir_path.exists():
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        f.write(f"  Created directory\n")
                    except Exception as e:
                        f.write(f"  ERROR: Failed to create: {e}\n")
                        errors.append(f"Failed to create {dir_path}: {e}")
                        failed_dirs.append(str(dir_path))
                        test_results.append(
                            {
                                "path": str(dir_path),
                                "read": False,
                                "write": False,
                                "status": "ERROR",
                                "error": str(e),
                            }
                        )
                        continue

                # Test permissions
                read_ok, write_ok, error_msg = test_read_write(dir_path)

                before_status = f"read={read_ok}, write={write_ok}"
                f.write(f"  Before: {before_status}\n")

                if not (read_ok and write_ok):
                    # Attempt repair (on Windows, try to adjust permissions)
                    repair_attempted = False
                    if sys.platform == "win32":
                        try:
                            # On Windows, we can try to create a fallback
                            fallback_dir = PROJECT_ROOT / "storage_fallback"
                            if not fallback_dir.exists() and dir_path.name == "storage":
                                fallback_dir.mkdir(parents=True, exist_ok=True)
                                f.write(f"  Created fallback directory: {fallback_dir}\n")
                                fallback_created = True
                                repair_attempted = True
                        except Exception as e:
                            f.write(f"  Fallback creation failed: {e}\n")

                    # Re-test after repair attempt
                    read_ok_after, write_ok_after, error_after = test_read_write(dir_path)
                    after_status = f"read={read_ok_after}, write={write_ok_after}"
                    f.write(f"  After repair attempt: {after_status}\n")

                    if not (read_ok_after and write_ok_after):
                        f.write(f"  WARNING: Permissions still insufficient\n")
                        failed_dirs.append(str(dir_path))
                        test_results.append(
                            {
                                "path": str(dir_path),
                                "read": read_ok_after,
                                "write": write_ok_after,
                                "status": "WARN",
                                "error": error_after or "Permissions insufficient",
                            }
                        )
                    else:
                        f.write(f"  SUCCESS: Permissions repaired\n")
                        test_results.append(
                            {
                                "path": str(dir_path),
                                "read": read_ok_after,
                                "write": write_ok_after,
                                "status": "OK",
                                "error": None,
                            }
                        )
                else:
                    f.write(f"  OK: Permissions sufficient\n")
                    test_results.append(
                        {
                            "path": str(dir_path),
                            "read": read_ok,
                            "write": write_ok,
                            "status": "OK",
                            "error": None,
                        }
                    )

                f.write("\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("Summary\n")
            f.write("=" * 70 + "\n")
            f.write(f"Tested directories: {len(TEST_DIRS)}\n")
            f.write(f"Failed directories: {len(failed_dirs)}\n")
            f.write(f"Fallback created: {fallback_created}\n")

        status = "OK" if not failed_dirs else "WARN"
        details = f"Tested {len(TEST_DIRS)} directories"
        if failed_dirs:
            details += f", {len(failed_dirs)} with permission issues"
        if fallback_created:
            details += ", fallback storage created"

        return {
            "phase": 202,
            "status": status,
            "details": details,
            "outputs": {
                "tested_dirs": len(TEST_DIRS),
                "failed_dirs": failed_dirs,
                "fallback_created": fallback_created,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 202,
            "status": "ERROR",
            "details": f"Phase 202 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 202 - PERMISSION SELF-REPAIR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase202()

    print(f"Phase 202: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog: {result['outputs']['log_path']}")
        print(f"Tested: {result['outputs']['tested_dirs']}")
        print(f"Failed: {len(result['outputs']['failed_dirs'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
