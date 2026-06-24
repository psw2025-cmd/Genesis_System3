"""
System3 Phase 149 - Log Inventory

Lists last-modified times of major log files.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_MD_PATH = STORAGE_ULTRA / "phase149_log_inventory.md"


def run_phase149_log_inventory() -> Dict[str, Any]:
    """
    Generate log inventory.

    Returns:
        dict: {
            "phase": 149,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []

    try:
        # Scan logs directory
        log_files = []
        if LOGS_DIR.exists():
            # Get all log files (recursive)
            for log_file in LOGS_DIR.rglob("*.log"):
                if log_file.is_file():
                    log_files.append(
                        {
                            "name": log_file.name,
                            "path": str(log_file.relative_to(PROJECT_ROOT)),
                            "size": log_file.stat().st_size,
                            "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                        }
                    )

            # Also check for .txt files in logs
            for log_file in LOGS_DIR.rglob("*.txt"):
                if log_file.is_file():
                    log_files.append(
                        {
                            "name": log_file.name,
                            "path": str(log_file.relative_to(PROJECT_ROOT)),
                            "size": log_file.stat().st_size,
                            "modified": datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                        }
                    )

        # Sort by modified time (newest first)
        log_files.sort(key=lambda x: x["modified"], reverse=True)

        # Generate MD report
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Log Inventory\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Log Files\n\n")
            if log_files:
                f.write(f"**Total Log Files**: {len(log_files)}\n\n")
                f.write("| File Name | Path | Size (bytes) | Last Modified |\n")
                f.write("|-----------|------|--------------|---------------|\n")
                # Show top 50 most recent
                for file_info in log_files[:50]:
                    f.write(
                        f"| {file_info['name']} | {file_info['path']} | {file_info['size']} | {file_info['modified'][:19]} |\n"
                    )
                if len(log_files) > 50:
                    f.write(f"\n*... and {len(log_files) - 50} more log files*\n")
            else:
                f.write("No log files found in `logs/` directory.\n")

        status = "OK"
        details = f"Log inventory generated: {len(log_files)} log files"

        return {
            "phase": 149,
            "status": status,
            "details": details,
            "outputs": {
                "md_path": str(OUTPUT_MD_PATH),
                "log_file_count": len(log_files),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 149,
            "status": "ERROR",
            "details": f"Phase 149 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 149 - LOG INVENTORY")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase149_log_inventory()

    print(f"Phase149: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog files: {result['outputs']['log_file_count']}")
        print(f"Report: {result['outputs']['md_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
