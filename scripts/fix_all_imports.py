"""
Fix All Import Issues - Comprehensive Fix
Identifies and fixes all import path issues
"""

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent


def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content

        # Fix ROOT_DIR paths
        # Pattern 1: ROOT_DIR = Path(__file__).parent.parent
        content = re.sub(
            r"ROOT_DIR = Path\(__file__\)\.parent\.parent\.parent", "ROOT_DIR = Path(__file__).parent.parent", content
        )

        # Pattern 2: Ensure sys.path setup is correct
        if "ROOT_DIR = Path(__file__).parent.parent" in content:
            # Check if sys.path setup exists
            if "sys.path.insert(0, str(ROOT_DIR))" not in content:
                # Add after ROOT_DIR definition
                content = re.sub(
                    r"(ROOT_DIR = Path\(__file__\)\.parent\.parent\s*\n)",
                    r"\1if str(ROOT_DIR) not in sys.path:\n    sys.path.insert(0, str(ROOT_DIR))\n\n",
                    content,
                )

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"  ERROR fixing {file_path}: {e}")
        return False


def main():
    """Fix all import issues."""
    print("=" * 80)
    print("  FIXING ALL IMPORT ISSUES")
    print("=" * 80)

    # Find all Python files
    python_files = []
    for directory in [ROOT_DIR / "scripts", ROOT_DIR / "src"]:
        if directory.exists():
            python_files.extend(directory.rglob("*.py"))

    # Exclude venv
    python_files = [f for f in python_files if "venv" not in str(f)]

    print(f"\nFound {len(python_files)} Python files")
    print("Fixing imports...\n")

    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            print(f"  Fixed: {file_path.relative_to(ROOT_DIR)}")
            fixed_count += 1

    print(f"\n\nFixed {fixed_count} files")
    print("Import fixes complete!")


if __name__ == "__main__":
    main()
