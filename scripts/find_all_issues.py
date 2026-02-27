"""
Find ALL Issues - Comprehensive Issue Detection
Identifies every possible issue in the system
"""

import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict
import json

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class IssueFinder:
    """Comprehensive issue finder."""

    def __init__(self):
        self.all_issues = []

    def check_syntax(self, file_path: Path) -> List[Dict]:
        """Check syntax errors."""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            issues.append({"type": "SYNTAX_ERROR", "file": str(file_path), "line": e.lineno, "message": str(e)})
        except Exception as e:
            issues.append({"type": "FILE_ERROR", "file": str(file_path), "message": str(e)})
        return issues

    def check_imports(self, file_path: Path) -> List[Dict]:
        """Check import errors."""
        issues = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name)
                        except ImportError:
                            # Check if it's a local module
                            if not self.is_local_module(alias.name, file_path):
                                issues.append(
                                    {
                                        "type": "IMPORT_ERROR",
                                        "file": str(file_path),
                                        "module": alias.name,
                                        "message": f"Module not found: {alias.name}",
                                    }
                                )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            __import__(node.module)
                        except ImportError:
                            if not self.is_local_module(node.module, file_path):
                                issues.append(
                                    {
                                        "type": "IMPORT_ERROR",
                                        "file": str(file_path),
                                        "module": node.module,
                                        "message": f"Module not found: {node.module}",
                                    }
                                )
        except:
            pass  # Syntax errors handled separately
        return issues

    def is_local_module(self, module_name: str, file_path: Path) -> bool:
        """Check if module is local."""
        # Check if it's in core, src, or scripts
        parts = module_name.split(".")
        if parts[0] in ["core", "src", "scripts"]:
            return True

        # Check if file exists
        module_path = ROOT_DIR / module_name.replace(".", "/")
        if module_path.exists() or (module_path.parent / f"{module_path.name}.py").exists():
            return True

        return False

    def check_path_consistency(self) -> List[Dict]:
        """Check ROOT_DIR path consistency."""
        issues = []
        python_files = []
        for directory in [ROOT_DIR / "scripts", ROOT_DIR / "src"]:
            if directory.exists():
                python_files.extend(directory.rglob("*.py"))

        python_files = [f for f in python_files if "venv" not in str(f)]

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for parent.parent.parent (should be parent.parent)
                if "parent.parent.parent" in content and "ROOT_DIR" in content:
                    # Check if file is in scripts or src
                    if "scripts" in str(file_path) or "src" in str(file_path):
                        issues.append(
                            {
                                "type": "PATH_ERROR",
                                "file": str(file_path),
                                "message": "ROOT_DIR should be parent.parent, not parent.parent.parent",
                            }
                        )
            except:
                pass

        return issues

    def find_all_issues(self):
        """Find all issues."""
        print("=" * 80)
        print("  COMPREHENSIVE ISSUE FINDER")
        print("=" * 80)

        # Find all Python files
        python_files = []
        for directory in [ROOT_DIR / "scripts", ROOT_DIR / "src"]:
            if directory.exists():
                python_files.extend(directory.rglob("*.py"))

        python_files = [f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)]

        print(f"\nChecking {len(python_files)} Python files...\n")

        # Check syntax
        print("[1] Checking syntax...")
        for file_path in python_files:
            issues = self.check_syntax(file_path)
            self.all_issues.extend(issues)

        # Check imports (only for critical files)
        print("[2] Checking imports...")
        critical_files = [
            "scripts/run_live_chain.py",
            "scripts/comprehensive_system_test.py",
            "src/trading/paper_executor.py",
            "src/trading/pnl_tracker.py",
            "src/trading/advanced_position_sizing.py",
            "src/trading/dynamic_risk_management.py",
            "src/selector/strategy_engine.py",
        ]

        for rel_path in critical_files:
            file_path = ROOT_DIR / rel_path
            if file_path.exists():
                issues = self.check_imports(file_path)
                self.all_issues.extend(issues)

        # Check path consistency
        print("[3] Checking path consistency...")
        issues = self.check_path_consistency()
        self.all_issues.extend(issues)

        # Summary
        print("\n" + "=" * 80)
        print("  ISSUE SUMMARY")
        print("=" * 80)

        by_type = {}
        for issue in self.all_issues:
            issue_type = issue["type"]
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(issue)

        for issue_type, issues in sorted(by_type.items()):
            print(f"\n{issue_type}: {len(issues)} issues")
            for issue in issues[:10]:  # Show first 10
                print(f"  - {Path(issue['file']).name}: {issue.get('message', issue.get('module', 'N/A'))}")
            if len(issues) > 10:
                print(f"  ... and {len(issues) - 10} more")

        print(f"\n\nTotal Issues Found: {len(self.all_issues)}")

        # Save report
        report_path = ROOT_DIR / "outputs" / "all_issues_report.json"
        with open(report_path, "w") as f:
            json.dump(
                {
                    "total_issues": len(self.all_issues),
                    "issues_by_type": {k: len(v) for k, v in by_type.items()},
                    "issues": self.all_issues,
                },
                f,
                indent=2,
                default=str,
            )

        print(f"Report saved to: {report_path}")

        return len(self.all_issues)


def main():
    """Main execution."""
    finder = IssueFinder()
    total = finder.find_all_issues()

    if total == 0:
        print("\n\n✅ NO ISSUES FOUND - SYSTEM READY")
        return 0
    else:
        print(f"\n\n⚠️  {total} ISSUES FOUND - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
