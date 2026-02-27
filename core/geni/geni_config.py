"""
System3 GENI - Configuration Module

Provides path helpers and safety flags.
All paths are relative to project root.
All safety flags default to False (SAFE MODE).
"""

from pathlib import Path
from typing import Optional

# Project root - resolve from this file's location
_GENI_DIR = Path(__file__).parent
_CORE_DIR = _GENI_DIR.parent
PROJECT_ROOT = _CORE_DIR.parent.resolve()

# Core paths
PATH_CORE = PROJECT_ROOT / "core"
PATH_STORAGE = PROJECT_ROOT / "storage"
PATH_LOGS = PROJECT_ROOT / "logs"
PATH_DOCS = PROJECT_ROOT / "docs"
PATH_TESTS = PROJECT_ROOT / "tests"

# Key scripts
SYSTEM3_ULTRA_ENTRY = PROJECT_ROOT / "system3_ultra.py"
ULTRA_DAILY_RUNNER = PROJECT_ROOT / "system3_ultra_daily_runner.py"
ULTRA_RUNTIME_LOOPS = PROJECT_ROOT / "system3_ultra_runtime_loops.py"
ULTRA_VALIDATION = PROJECT_ROOT / "system3_ultra_validation.py"
FULL_VERIFICATION = PROJECT_ROOT / "run_full_verification_checklist.py"

# GENI-specific paths
PATH_GENI_STORAGE = PATH_STORAGE / "geni"
GENI_STATE_FILE = PATH_GENI_STORAGE / "system3_geni_state.json"
GENI_LAST_RUN_JSON = PATH_GENI_STORAGE / "system3_geni_last_run.json"
GENI_LAST_RUN_MD = PATH_GENI_STORAGE / "system3_geni_last_run.md"

# Ensure GENI storage directory exists
PATH_GENI_STORAGE.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SAFETY FLAGS (READ-ONLY, ALL DEFAULT TO False)
# ============================================================================
# These flags are for future reference only.
# They must NOT be used to enable any live trading or auto-promotion.
# All operations remain SAFE MODE by default.

AUTO_EXECUTE_REAL_TRADES = False
AUTO_UPDATE_CONFIGS = False
AUTO_PROMOTE_MODELS = False
GENI_ULTRA_LIVE_MODE = False

# ============================================================================
# VALIDATION
# ============================================================================


def validate_paths() -> list[str]:
    """
    Validate that key paths exist.

    Returns:
        List of warning messages (empty if all paths valid)
    """
    warnings = []

    required_paths = [
        (PROJECT_ROOT, "Project root"),
        (PATH_CORE, "Core directory"),
        (PATH_STORAGE, "Storage directory"),
        (PATH_LOGS, "Logs directory"),
        (PATH_DOCS, "Docs directory"),
    ]

    for path, name in required_paths:
        if not path.exists():
            warnings.append(f"{name} missing: {path}")

    required_scripts = [
        (SYSTEM3_ULTRA_ENTRY, "system3_ultra.py"),
    ]

    for path, name in required_scripts:
        if not path.exists():
            warnings.append(f"Required script missing: {name}")

    return warnings
