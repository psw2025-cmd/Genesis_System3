"""
System3 Phase 315 - Transactional Write Guard

Protects critical files from partial or corrupted writes by enforcing transactional writes.
"""

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Log directory
LOG_DIR = PROJECT_ROOT / "logs" / "integrity"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Protected files
PROTECTED_FILES = [
    "storage/live/dhan_index_ai_signals.csv",
    "storage/live/dhan_index_ai_signals_curated.csv",
    "storage/live/dhan_index_ai_signals_with_forward.csv",
    "storage/live/dhan_index_ai_pnl_log.csv",
]

# Expected columns (minimal requirements)
EXPECTED_COLUMNS = {
    "dhan_index_ai_signals.csv": ["ts", "underlying", "pred_label"],
    "dhan_index_ai_signals_curated.csv": ["ts", "underlying", "pred_label"],
    "dhan_index_ai_signals_with_forward.csv": ["ts", "underlying", "pred_label"],
    "dhan_index_ai_pnl_log.csv": ["ts", "symbol"],
}


def validate_csv(file_path: Path, expected_cols: List[str]) -> tuple[bool, List[str]]:
    """
    Validate CSV file structure.

    Returns:
        tuple: (is_valid, list of validation errors)
    """
    validation_errors = []

    if not file_path.exists():
        return True, []  # OK if file doesn't exist yet

    try:
        # Try to load
        df = pd.read_csv(file_path)

        # Check expected columns
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            validation_errors.append(f"Missing columns: {missing_cols}")

        # Check for duplicate headers
        if df.columns.duplicated().any():
            validation_errors.append("Duplicate column headers detected")

        # Check minimum row count (allow 0 rows for new files)
        if len(df) < 0:
            validation_errors.append("Invalid row count")

        return len(validation_errors) == 0, validation_errors

    except Exception as e:
        validation_errors.append(f"Failed to load CSV: {str(e)}")
        return False, validation_errors


def transactional_write_csv(df: pd.DataFrame, target_path: Path, expected_cols: List[str]) -> tuple[bool, str]:
    """
    Write CSV with transactional semantics.

    Returns:
        tuple: (success, error_message)
    """
    temp_path = target_path.parent / f"{target_path.name}.tmp"

    try:
        # Write to temp file
        df.to_csv(temp_path, index=False)

        # Validate temp file
        is_valid, errors = validate_csv(temp_path, expected_cols)

        if not is_valid:
            temp_path.unlink()
            return False, f"Validation failed: {'; '.join(errors)}"

        # Backup existing file if it exists
        if target_path.exists():
            backup_path = target_path.parent / f"{target_path.name}.backup"
            shutil.copy2(target_path, backup_path)

        # Atomic move
        shutil.move(str(temp_path), str(target_path))

        return True, ""

    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return False, str(e)


def run_phase315(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 315: Transactional Write Guard

    Returns:
        dict: {
            "phase": 315,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {"log_file": path, "files_validated": N},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        today = datetime.now().strftime("%Y%m%d")
        log_file = LOG_DIR / f"transactional_write_guard_{today}.log"

        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.info("Phase 315: Transactional write guard initialized")

        # Validate all protected files
        validated_count = 0
        validation_failures = 0

        for file_rel_path in PROTECTED_FILES:
            file_path = PROJECT_ROOT / file_rel_path
            file_name = Path(file_rel_path).name
            expected_cols = EXPECTED_COLUMNS.get(file_name, [])

            is_valid, validation_errors = validate_csv(file_path, expected_cols)

            if file_path.exists():
                validated_count += 1

                if is_valid:
                    logger.info(f"OK {file_name}: Valid")
                else:
                    validation_failures += 1
                    logger.warning(f"WARN {file_name}: {'; '.join(validation_errors)}")

        logger.info(f"Validation complete: {validated_count} files checked, " f"{validation_failures} failures")

        outputs = {
            "log_file": str(log_file),
            "files_validated": validated_count,
            "validation_failures": validation_failures,
        }

        # Remove handler
        logger.removeHandler(file_handler)
        file_handler.close()

        status = "WARN" if validation_failures > 0 else "OK"

        return {
            "phase": 315,
            "status": status,
            "details": f"Transactional write guard: {validated_count} files validated, {validation_failures} failures",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 315 error: {e}")
        return {
            "phase": 315,
            "status": "ERROR",
            "details": f"Phase 315 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


# Utility function for other phases to use
def safe_write_csv(df: pd.DataFrame, file_path: str) -> tuple[bool, str]:
    """
    Safely write CSV with transactional semantics.
    For use by other phases.

    Args:
        df: DataFrame to write
        file_path: Relative path from PROJECT_ROOT

    Returns:
        tuple: (success, error_message)
    """
    target_path = PROJECT_ROOT / file_path
    file_name = Path(file_path).name
    expected_cols = EXPECTED_COLUMNS.get(file_name, [])

    return transactional_write_csv(df, target_path, expected_cols)


if __name__ == "__main__":
    result = run_phase315()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
