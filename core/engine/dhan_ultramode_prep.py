"""
Dhan Index Options - Ultra-Mode Prep Layer

Prepares system for future LIVE AUTO mode.
SAFE MODE ONLY - All features disabled by default.
AUTO-EXECUTION: DISABLED
AUTO-UPDATE: DISABLED
"""

from pathlib import Path
from typing import Dict, Any
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
ULTRAMODE_CONFIG_JSON = CONFIG_DIR / "ultramode_config.json"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)


class UltraModeConfig:
    """Ultra-Mode configuration (all disabled by default)."""

    def __init__(self):
        self.live_execution_enabled = False  # ❌ DISABLED
        self.auto_trade_execution = False  # ❌ DISABLED
        self.auto_threshold_update = False  # ❌ DISABLED
        self.auto_model_retrain = False  # ❌ DISABLED
        self.auto_pnl_simulation = False  # ❌ DISABLED
        self.max_daily_trades = 20
        self.max_trades_per_underlying = 5
        self.emergency_stop_enabled = True  # ✅ Enabled for safety
        self.read_only_mode = True  # ✅ Read-only by default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "live_execution_enabled": self.live_execution_enabled,
            "auto_trade_execution": self.auto_trade_execution,
            "auto_threshold_update": self.auto_threshold_update,
            "auto_model_retrain": self.auto_model_retrain,
            "auto_pnl_simulation": self.auto_pnl_simulation,
            "max_daily_trades": self.max_daily_trades,
            "max_trades_per_underlying": self.max_trades_per_underlying,
            "emergency_stop_enabled": self.emergency_stop_enabled,
            "read_only_mode": self.read_only_mode,
            "last_updated": datetime.utcnow().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UltraModeConfig":
        """Create from dictionary."""
        config = cls()
        config.live_execution_enabled = data.get("live_execution_enabled", False)
        config.auto_trade_execution = data.get("auto_trade_execution", False)
        config.auto_threshold_update = data.get("auto_threshold_update", False)
        config.auto_model_retrain = data.get("auto_model_retrain", False)
        config.auto_pnl_simulation = data.get("auto_pnl_simulation", False)
        config.max_daily_trades = data.get("max_daily_trades", 20)
        config.max_trades_per_underlying = data.get("max_trades_per_underlying", 5)
        config.emergency_stop_enabled = data.get("emergency_stop_enabled", True)
        config.read_only_mode = data.get("read_only_mode", True)
        return config


def load_ultramode_config() -> UltraModeConfig:
    """Load Ultra-Mode configuration."""
    if ULTRAMODE_CONFIG_JSON.exists():
        try:
            import json

            with ULTRAMODE_CONFIG_JSON.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return UltraModeConfig.from_dict(data)
        except Exception:
            pass

    # Return default (all disabled)
    return UltraModeConfig()


def save_ultramode_config(config: UltraModeConfig) -> bool:
    """Save Ultra-Mode configuration."""
    try:
        import json

        with ULTRAMODE_CONFIG_JSON.open("w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"[ULTRAMODE] Failed to save config: {e}")
        return False


def check_ultramode_readiness() -> Dict[str, Any]:
    """
    Check system readiness for Ultra-Mode (read-only check).

    Returns:
        Dict with readiness status
    """
    config = load_ultramode_config()

    checks = {
        "live_execution": config.live_execution_enabled,
        "auto_trade": config.auto_trade_execution,
        "auto_threshold": config.auto_threshold_update,
        "auto_retrain": config.auto_model_retrain,
        "read_only_mode": config.read_only_mode,
    }

    all_disabled = all(not v for k, v in checks.items() if k != "read_only_mode")
    read_only_active = checks["read_only_mode"]

    return {
        "status": "READY" if all_disabled and read_only_active else "NOT_READY",
        "checks": checks,
        "message": (
            "Ultra-Mode prep complete. All auto-features disabled. Read-only mode active."
            if all_disabled and read_only_active
            else "Ultra-Mode not ready. Some features may be enabled."
        ),
    }


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - ULTRA-MODE PREP LAYER ===")
    print("[INFO] SAFE MODE ONLY - All features disabled by default\n")
    print("[SAFETY] AUTO-EXECUTION: DISABLED")
    print("[SAFETY] AUTO-UPDATE: DISABLED")
    print("[SAFETY] READ-ONLY MODE: ACTIVE\n")

    config = load_ultramode_config()

    print("=== CURRENT CONFIGURATION ===")
    print(f"Live Execution: {'❌ DISABLED' if not config.live_execution_enabled else '⚠️ ENABLED'}")
    print(f"Auto Trade Execution: {'❌ DISABLED' if not config.auto_trade_execution else '⚠️ ENABLED'}")
    print(f"Auto Threshold Update: {'❌ DISABLED' if not config.auto_threshold_update else '⚠️ ENABLED'}")
    print(f"Auto Model Retrain: {'❌ DISABLED' if not config.auto_model_retrain else '⚠️ ENABLED'}")
    print(f"Auto PnL Simulation: {'❌ DISABLED' if not config.auto_pnl_simulation else '⚠️ ENABLED'}")
    print(f"Emergency Stop: {'✅ ENABLED' if config.emergency_stop_enabled else '❌ DISABLED'}")
    print(f"Read-Only Mode: {'✅ ACTIVE' if config.read_only_mode else '❌ INACTIVE'}")

    print("\n=== READINESS CHECK ===")
    readiness = check_ultramode_readiness()
    print(f"Status: {readiness['status']}")
    print(f"Message: {readiness['message']}")

    print(f"\n[INFO] Config file: {ULTRAMODE_CONFIG_JSON}")
    print("[NOTE] All features remain disabled. Manual activation required for LIVE mode.")


if __name__ == "__main__":
    main()
