"""
Complete System Validator - Identifies ALL Issues
Comprehensive validation of entire system
"""

import sys
from pathlib import Path
import importlib.util
import ast
import json
from typing import List, Dict

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class CompleteSystemValidator:
    """Complete system validator."""

    def __init__(self):
        self.issues = []
        self.warnings = []
        self.checks_passed = []

    def check_imports(self):
        """Check all imports."""
        print("\n[CHECK 1] Import Validation")
        print("-" * 80)

        critical_modules = [
            "core.brokers.angel_one.broker",
            "src.trading.paper_executor",
            "src.trading.pnl_tracker",
            "src.trading.advanced_position_sizing",
            "src.trading.dynamic_risk_management",
            "src.selector.strategy_engine",
            "src.selector.top_symbol_selector",
            "src.metrics.greeks",
            "src.metrics.iv_solver",
            "src.storage.trade_history",
        ]

        failed = []
        for module in critical_modules:
            try:
                __import__(module)
                print(f"  OK: {module}")
                self.checks_passed.append(f"Import: {module}")
            except ImportError as e:
                print(f"  ERROR: {module} - {e}")
                self.issues.append({"type": "IMPORT_ERROR", "module": module, "error": str(e)})
                failed.append(module)

        if not failed:
            print(f"  All {len(critical_modules)} critical imports OK")
        else:
            print(f"  {len(failed)} imports failed")

        return len(failed) == 0

    def check_file_paths(self):
        """Check all file paths."""
        print("\n[CHECK 2] File Path Validation")
        print("-" * 80)

        critical_files = [
            "core/brokers/angel_one/broker.py",
            "src/trading/paper_executor.py",
            "src/trading/pnl_tracker.py",
            "src/trading/advanced_position_sizing.py",
            "src/trading/dynamic_risk_management.py",
            "src/selector/strategy_engine.py",
            "outputs/OptionChain_Master_v3_AI_FINAL.xlsx",
            "config/.env",
        ]

        missing = []
        for file_path in critical_files:
            full_path = ROOT_DIR / file_path
            if full_path.exists():
                print(f"  OK: {file_path}")
                self.checks_passed.append(f"File: {file_path}")
            else:
                print(f"  MISSING: {file_path}")
                self.issues.append({"type": "MISSING_FILE", "file": file_path})
                missing.append(file_path)

        if not missing:
            print(f"  All {len(critical_files)} critical files exist")
        else:
            print(f"  {len(missing)} files missing")

        return len(missing) == 0

    def check_configuration(self):
        """Check configuration values."""
        print("\n[CHECK 3] Configuration Validation")
        print("-" * 80)

        try:
            from src.trading.advanced_position_sizing import AdvancedPositionSizing
            from src.trading.dynamic_risk_management import DynamicRiskManager
            from src.selector.strategy_engine import StrategyEngine

            ps = AdvancedPositionSizing()
            rm = DynamicRiskManager()
            se = StrategyEngine()

            checks = [
                ("Kelly Fraction", ps.kelly_fraction == 1.0, ps.kelly_fraction, 1.0),
                ("ATR Multiplier", rm.atr_multiplier == 1.0, rm.atr_multiplier, 1.0),
                ("Fixed TP", rm.fixed_take_profit_pct == 0.5, rm.fixed_take_profit_pct, 0.5),
                ("Min Confidence", se.min_confidence == 0.5, se.min_confidence, 0.5),
                ("Min Liquidity", se.min_liquidity_score == 40.0, se.min_liquidity_score, 40.0),
            ]

            failed = []
            for name, check, actual, expected in checks:
                if check:
                    print(f"  OK: {name} = {actual}")
                    self.checks_passed.append(f"Config: {name}")
                else:
                    print(f"  ERROR: {name} = {actual} (expected {expected})")
                    self.issues.append(
                        {"type": "CONFIG_ERROR", "setting": name, "actual": actual, "expected": expected}
                    )
                    failed.append(name)

            if not failed:
                print(f"  All {len(checks)} configuration values correct")
            else:
                print(f"  {len(failed)} configuration errors")

            return len(failed) == 0

        except Exception as e:
            print(f"  ERROR: Configuration check failed - {e}")
            self.issues.append({"type": "CONFIG_CHECK_ERROR", "error": str(e)})
            return False

    def check_script_execution(self):
        """Check if scripts can execute."""
        print("\n[CHECK 4] Script Execution Validation")
        print("-" * 80)

        scripts_to_check = [
            "scripts/comprehensive_system_test.py",
            "scripts/quick_optimization_test.py",
            "scripts/final_best_strategy_selector.py",
        ]

        failed = []
        for script in scripts_to_check:
            script_path = ROOT_DIR / script
            if not script_path.exists():
                print(f"  MISSING: {script}")
                failed.append(script)
                continue

            # Try to compile
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    code = f.read()
                ast.parse(code)
                print(f"  OK: {script} (syntax valid)")
                self.checks_passed.append(f"Script: {script}")
            except SyntaxError as e:
                print(f"  SYNTAX ERROR: {script} - {e}")
                self.issues.append({"type": "SYNTAX_ERROR", "file": script, "error": str(e)})
                failed.append(script)

        if not failed:
            print(f"  All {len(scripts_to_check)} scripts valid")
        else:
            print(f"  {len(failed)} scripts have issues")

        return len(failed) == 0

    def check_data_files(self):
        """Check data files."""
        print("\n[CHECK 5] Data Files Validation")
        print("-" * 80)

        data_files = [
            "outputs/OptionChain_Master_v3_AI_FINAL.xlsx",
            "outputs/chain_raw_live.csv",
            "outputs/pnl_live.json",
        ]

        missing = []
        for file_path in data_files:
            full_path = ROOT_DIR / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print(f"  OK: {file_path} ({size:,} bytes)")
                self.checks_passed.append(f"Data: {file_path}")
            else:
                print(f"  MISSING: {file_path} (OK if not generated yet)")
                missing.append(file_path)

        if not missing:
            print(f"  All {len(data_files)} data files exist")
        else:
            print(f"  {len(missing)} data files missing (may be OK)")

        return True  # Data files optional

    def check_dependencies(self):
        """Check Python dependencies."""
        print("\n[CHECK 6] Dependencies Validation")
        print("-" * 80)

        required_packages = ["pandas", "numpy", "pytz", "openpyxl", "xlsxwriter", "logzero"]

        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  OK: {package}")
                self.checks_passed.append(f"Package: {package}")
            except ImportError:
                print(f"  MISSING: {package}")
                self.issues.append({"type": "MISSING_PACKAGE", "package": package})
                missing.append(package)

        if not missing:
            print(f"  All {len(required_packages)} packages installed")
        else:
            print(f"  {len(missing)} packages missing")

        return len(missing) == 0

    def run_all_checks(self):
        """Run all validation checks."""
        print("=" * 80)
        print("  COMPLETE SYSTEM VALIDATOR")
        print("=" * 80)

        checks = [
            ("Imports", self.check_imports),
            ("File Paths", self.check_file_paths),
            ("Configuration", self.check_configuration),
            ("Script Execution", self.check_script_execution),
            ("Data Files", self.check_data_files),
            ("Dependencies", self.check_dependencies),
        ]

        results = []
        for name, check_func in checks:
            try:
                result = check_func()
                results.append((name, result))
            except Exception as e:
                print(f"  ERROR in {name}: {e}")
                results.append((name, False))

        # Summary
        print("\n" + "=" * 80)
        print("  VALIDATION SUMMARY")
        print("=" * 80)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            status = "PASS" if result else "FAIL"
            print(f"  {status}: {name}")

        print(f"\n  Checks Passed: {passed}/{total}")
        print(f"  Issues Found: {len(self.issues)}")
        print(f"  Warnings: {len(self.warnings)}")

        if self.issues:
            print("\n[ISSUES]")
            for issue in self.issues[:20]:  # Show first 20
                print(
                    f"  [{issue['type']}] {issue.get('module', issue.get('file', issue.get('setting', 'N/A')))}: {issue.get('error', issue.get('message', 'N/A'))}"
                )
            if len(self.issues) > 20:
                print(f"  ... and {len(self.issues) - 20} more issues")

        # Save report
        report_path = ROOT_DIR / "outputs" / "complete_validation_report.json"
        with open(report_path, "w") as f:
            json.dump(
                {
                    "checks_passed": passed,
                    "total_checks": total,
                    "issues": self.issues,
                    "warnings": self.warnings,
                    "checks_passed_list": self.checks_passed,
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\n\nReport saved to: {report_path}")

        if passed == total and len(self.issues) == 0:
            print("\n  STATUS: ALL CHECKS PASSED - SYSTEM READY")
            return True
        else:
            print("\n  STATUS: ISSUES FOUND - REVIEW REQUIRED")
            return False


def main():
    """Main execution."""
    validator = CompleteSystemValidator()
    success = validator.run_all_checks()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
