"""
System3 GENI - Validation Helpers

Runs validation routines and parses results.
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .geni_config import FULL_VERIFICATION, PROJECT_ROOT, ULTRA_VALIDATION
from .geni_state import GeniState, load_state, save_state


@dataclass
class ValidationResult:
    """Validation result container."""

    success: bool
    total_checks: int
    passed: int
    failed: int
    warnings: List[str]
    details: List[str]
    raw_output: str = ""


def _parse_validation_output(output: str) -> ValidationResult:
    """
    Parse validation script output to extract results.

    Args:
        output: stdout from validation script

    Returns:
        ValidationResult with parsed information
    """
    # Default result
    result = ValidationResult(
        success=False,
        total_checks=0,
        passed=0,
        failed=0,
        warnings=[],
        details=[],
        raw_output=output,
    )

    # Look for common patterns
    lines = output.split("\n")

    # Check for success indicators (from run_full_verification_checklist.py)
    success_patterns = [
        r"ALL VERIFICATIONS PASSED",
        r"✓ ALL VERIFICATIONS PASSED",
        r"verification categories passed",
        r"\[PASS\]",
        r"Validation complete",
        r"All.*passed",
    ]

    for line in lines:
        for pattern in success_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                result.success = True
                break

    # Try to extract numbers from patterns like:
    # "Total: X/Y verification categories passed" (from run_full_verification_checklist.py)
    # "Total tests: X" / "Passed: Y" / "Failed: Z" (from system3_ultra_validation.py)
    number_patterns = [
        r"Total:\s*(\d+)\s*/\s*(\d+)\s*verification categories passed",
        r"Total tests:\s*(\d+)",
        r"Passed:\s*(\d+)",
        r"Failed:\s*(\d+)",
        r"(\d+)\s*/\s*(\d+)\s*(?:passed|checks|verification)",
        r"Total.*?(\d+).*?Passed.*?(\d+).*?Failed.*?(\d+)",
        r"(\d+)\s+passed",
        r"(\d+)\s+failed",
    ]

    # Try to extract from "Total tests: X" / "Passed: Y" / "Failed: Z" format (system3_ultra_validation.py)
    # This should be done BEFORE the loop to prioritize this format
    total_tests_match = re.search(r"Total tests:\s*(\d+)", output, re.IGNORECASE)
    passed_match = re.search(r"Passed:\s*(\d+)", output, re.IGNORECASE)
    failed_match = re.search(r"Failed:\s*(\d+)", output, re.IGNORECASE)

    if total_tests_match and passed_match:
        try:
            result.total_checks = int(total_tests_match.group(1))
            result.passed = int(passed_match.group(1))
            if failed_match:
                result.failed = int(failed_match.group(1))
            else:
                result.failed = result.total_checks - result.passed
            result.success = result.failed == 0 and result.total_checks > 0
            # If we found this format, we're done - don't try other patterns
            return result
        except (ValueError, AttributeError):
            pass

    for line in lines:
        for pattern in number_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    try:
                        # Pattern "Total: X/Y" - X is passed, Y is total
                        result.passed = int(groups[0])
                        result.total_checks = int(groups[1])
                        result.failed = result.total_checks - result.passed
                        # If we found numbers, assume success if passed == total
                        if result.passed == result.total_checks:
                            result.success = True
                        break
                    except ValueError:
                        pass

    # Count [PASS] and [FAIL] markers
    pass_count = len([l for l in lines if "[PASS]" in l])
    fail_count = len([l for l in lines if "[FAIL]" in l])

    if pass_count > 0 or fail_count > 0:
        result.total_checks = pass_count + fail_count
        result.passed = pass_count
        result.failed = fail_count
        result.success = fail_count == 0 and pass_count > 0

    # Extract warnings
    for line in lines:
        if "[WARN]" in line or "warning" in line.lower():
            # Clean ANSI codes
            clean_line = re.sub(r"\033\[[0-9;]*m", "", line).strip()
            if clean_line:
                result.warnings.append(clean_line)

    # If we couldn't parse, try to infer from output
    if result.total_checks == 0:
        if "ALL VERIFICATIONS PASSED" in output or "✓ ALL" in output:
            result.success = True
        elif "SOME VERIFICATIONS FAILED" in output or "⚠ SOME" in output:
            result.success = False
        elif "error" in output.lower() or "failed" in output.lower():
            result.success = False
        elif "ok" in output.lower() or "complete" in output.lower():
            result.success = True

    # Add key lines as details (last 20 lines, cleaned)
    for line in lines[-20:]:
        if line.strip() and len(line.strip()) < 200:
            # Clean ANSI codes
            clean_line = re.sub(r"\033\[[0-9;]*m", "", line).strip()
            if clean_line:
                result.details.append(clean_line)

    return result


def run_full_validation() -> ValidationResult:
    """
    Run full validation suite.

    Returns:
        ValidationResult with validation outcome
    """
    print("[GENI] Running full validation...")

    try:
        result = subprocess.run(
            ["python", str(FULL_VERIFICATION)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        output = result.stdout + "\n" + result.stderr

        validation_result = _parse_validation_output(output)

        # Update state
        state = load_state()
        state.validation_passed = validation_result.success
        state.last_validation_summary = (
            f"Full validation: {validation_result.passed}/{validation_result.total_checks} passed"
            if validation_result.total_checks > 0
            else f"Full validation: {'PASSED' if validation_result.success else 'FAILED'}"
        )
        save_state(state)

        return validation_result

    except subprocess.TimeoutExpired:
        return ValidationResult(
            success=False,
            total_checks=0,
            passed=0,
            failed=0,
            warnings=["Validation timed out after 5 minutes"],
            details=["Timeout"],
            raw_output="",
        )
    except Exception as e:
        return ValidationResult(
            success=False,
            total_checks=0,
            passed=0,
            failed=1,
            warnings=[f"Validation execution error: {e}"],
            details=[str(e)],
            raw_output="",
        )


def run_quick_validation() -> ValidationResult:
    """
    Run quick validation (Ultra validation only).

    Returns:
        ValidationResult with validation outcome
    """
    print("[GENI] Running quick validation...")

    try:
        result = subprocess.run(
            ["python", str(ULTRA_VALIDATION)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute timeout
        )

        output = result.stdout + "\n" + result.stderr

        # Parse output
        validation_result = _parse_validation_output(output)

        # For system3_ultra_validation.py, also check return code
        if result.returncode == 0 and validation_result.total_checks == 0:
            # If return code is 0, assume success
            validation_result.success = True
            # Try to count test markers in output
            lines = output.split("\n")
            test_count = len([l for l in lines if "✓" in l or "[PASS]" in l or "PASS" in l])
            if test_count > 0:
                validation_result.total_checks = test_count
                validation_result.passed = test_count
                validation_result.failed = 0

        # Update state
        state = load_state()
        state.validation_passed = validation_result.success
        state.last_validation_summary = (
            f"Quick validation: {validation_result.passed}/{validation_result.total_checks} passed"
            if validation_result.total_checks > 0
            else f"Quick validation: {'PASSED' if validation_result.success else 'FAILED'}"
        )
        save_state(state)

        return validation_result

    except subprocess.TimeoutExpired:
        return ValidationResult(
            success=False,
            total_checks=0,
            passed=0,
            failed=0,
            warnings=["Quick validation timed out"],
            details=["Timeout"],
            raw_output="",
        )
    except Exception as e:
        return ValidationResult(
            success=False,
            total_checks=0,
            passed=0,
            failed=1,
            warnings=[f"Quick validation execution error: {e}"],
            details=[str(e)],
            raw_output="",
        )
