"""
Comprehensive Import Checker - Identifies ALL Import Issues
Checks every Python file for import errors
"""

import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class ImportChecker:
    """Comprehensive import checker."""

    def __init__(self):
        self.issues = []
        self.files_checked = []
        self.imports_found = []

    def check_file(self, file_path: Path) -> List[Dict]:
        """Check a single file for import issues."""
        issues = []

        try:
            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                issues.append(
                    {"file": str(file_path), "type": "SYNTAX_ERROR", "message": f"Syntax error: {e}", "line": e.lineno}
                )
                return issues

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports_found.append(alias.name)
                        # Try to import
                        try:
                            __import__(alias.name)
                        except ImportError as e:
                            issues.append(
                                {
                                    "file": str(file_path),
                                    "type": "IMPORT_ERROR",
                                    "module": alias.name,
                                    "message": str(e),
                                }
                            )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module:
                        self.imports_found.append(module)
                        # Try to import
                        try:
                            __import__(module)
                        except ImportError as e:
                            issues.append(
                                {"file": str(file_path), "type": "IMPORT_ERROR", "module": module, "message": str(e)}
                            )

        except Exception as e:
            issues.append({"file": str(file_path), "type": "ERROR", "message": f"Error checking file: {e}"})

        return issues

    def check_all_files(self, directory: Path = None) -> Dict:
        """Check all Python files in directory."""
        if directory is None:
            directory = ROOT_DIR

        print("=" * 80)
        print("  COMPREHENSIVE IMPORT CHECKER")
        print("=" * 80)

        # Find all Python files
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(directory.glob(pattern))

        # Exclude venv and __pycache__
        python_files = [f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)]

        print(f"\nFound {len(python_files)} Python files to check")
        print("Checking imports...\n")

        all_issues = []
        for file_path in python_files:
            issues = self.check_file(file_path)
            if issues:
                all_issues.extend(issues)
            self.files_checked.append(str(file_path))

        # Summary
        print("=" * 80)
        print("  IMPORT CHECK SUMMARY")
        print("=" * 80)
        print(f"\nFiles Checked: {len(self.files_checked)}")
        print(f"Total Issues: {len(all_issues)}")
        print(f"Unique Imports: {len(set(self.imports_found))}")

        if all_issues:
            print("\n[ISSUES FOUND]")
            print("-" * 80)

            # Group by file
            by_file = {}
            for issue in all_issues:
                file = issue["file"]
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(issue)

            for file, issues in sorted(by_file.items()):
                print(f"\n{file}:")
                for issue in issues:
                    print(f"  [{issue['type']}] {issue.get('module', 'N/A')}: {issue['message']}")
        else:
            print("\n[OK] No import issues found!")

        return {"files_checked": len(self.files_checked), "issues": all_issues, "total_issues": len(all_issues)}


def main():
    """Main execution."""
    checker = ImportChecker()
    result = checker.check_all_files()

    if result["total_issues"] > 0:
        print(f"\n\nTotal Issues: {result['total_issues']}")
        return 1
    else:
        print("\n\nAll imports verified successfully!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
