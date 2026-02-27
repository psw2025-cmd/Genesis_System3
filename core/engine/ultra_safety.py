"""
System3 Ultra Safety Switches

Central safety control for Ultra-Mode features.
All auto-features disabled by default.
"""

import json
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "core" / "config"
SAFETY_JSON = CONFIG_DIR / "system3_ultra_safety.json"

# Default safety settings (all False)
DEFAULT_SAFETY = {
    "AUTO_EXECUTE_TRADES": False,
    "AUTO_UPDATE_THRESHOLDS": False,
    "AUTO_RETRAIN_MODELS": False,
    "AUTO_PROMOTE_MODELS": False,
    "AUTO_WRITE_CONFIG": False,
}


def load_ultra_safety() -> Dict[str, bool]:
    """
    Load Ultra safety switches.

    Returns:
        Dict with safety flags (all default to False if missing)
    """
    if not SAFETY_JSON.exists():
        return DEFAULT_SAFETY.copy()

    try:
        with SAFETY_JSON.open("r", encoding="utf-8") as f:
            user_config = json.load(f)
            # Merge with defaults (defaults take precedence if key missing)
            result = DEFAULT_SAFETY.copy()
            result.update(user_config)
            return result
    except Exception:
        return DEFAULT_SAFETY.copy()


def is_ultra_enabled(flag_name: str) -> bool:
    """
    Check if a specific Ultra feature is enabled.

    Args:
        flag_name: One of the safety switch keys

    Returns:
        True if enabled, False otherwise (defaults to False)
    """
    safety = load_ultra_safety()
    return safety.get(flag_name, False)


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA SAFETY SWITCHES ===\n")
    safety = load_ultra_safety()
    print("Current Safety Settings:")
    for key, value in safety.items():
        status = "✅ ENABLED" if value else "❌ DISABLED"
        print(f"  {key}: {value} ({status})")
    print("\n[NOTE] All features default to DISABLED for safety.")


if __name__ == "__main__":
    main()
