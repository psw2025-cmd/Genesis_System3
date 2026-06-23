"""
Runtime State Store (SSOT) - Single Source of Truth
Provides unified, atomic, versioned state for all dashboard pages
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import pytz
import threading

IST = pytz.timezone("Asia/Kolkata")

# REAL_ONLY MODE: Disable synthetic data generation (default: True)
REAL_ONLY = os.environ.get("SYSTEM3_REAL_ONLY", "1").strip().lower() in ("1", "true", "yes")


class RuntimeStateStore:
    """
    Single Source of Truth for dashboard state.
    All pages read from this store to ensure consistency.
    """

    def __init__(self, outputs_dir: Path):
        self.outputs_dir = Path(outputs_dir)
        self._state = {}
        self._state_version = 0
        self._lock = threading.Lock()
        self._last_update = None

        # Initialize state
        self._initialize_state()

    def _check_broker_connectivity(self) -> Dict[str, Any]:
        """Check broker connectivity and return status - uses health.json as source of truth"""
        # First try to read from health.json (same source as /api/health)
        try:
            from core.brokers.dhan.dhan_readonly import get_status as _dhan_status
            result = _dhan_status()
            return result
        except Exception as e:
            return {
                "connected": False,
                "name": "dhan",
                "status": "error",
                "error": str(e)[:200],
                "latency_ms": None,
                "last_ok": None,
            }

    def _initialize_state(self):
        """Initialize state with defaults"""
        # Don't check broker connectivity on initialization - use sync_from_files instead
        # This ensures consistency with /api/health endpoint
        broker_status = {
            "connected": False,
            "name": "dhan",
            "status": "disconnected",
            "error": None,
            "latency_ms": None,
            "last_ok": None,
        }

        self._state = {
            "state_version": 0,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "timestamp_ist": datetime.now(IST).isoformat(),
            "mode": "PAPER",  # Always PAPER mode - no real trading allowed
            "data_source": "not_ready" if REAL_ONLY else "SYNTHETIC",
            "market": {
                "is_open": False,
                "reason": "Market closed",
                "next_open": None,
                "current_time_ist": datetime.now(IST).isoformat(),
            },
            "broker": broker_status,
            "qc": {"status": "PASS", "reasons": [], "contracts_total": 0, "underlyings": 0, "failures": []},
            "signals": {
                "status": "NO_TRADE",
                "underlying": None,
                "confidence": 0,
                "reason": "No signal generated",
                "last_signal": None,
            },
            "positions": [],
            "pnl": {"unrealized": 0.0, "realized": 0.0, "total": 0.0, "day_total": 0.0},
            "risk": {
                "var95": 0.0,
                "es95": 0.0,
                "exposure": 0.0,
                "concentration": 0.0,
                "greeks": {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0},
                "limits": {"status": "PASS", "breaches": []},
            },
            "model": {"active": None, "type": None, "fallback_used": False, "metrics": {}},
            "alerts": [],
        }

    def update_state(self, updates: Dict[str, Any]) -> int:
        """
        Atomically update state and increment version.
        Returns new state_version.
        """
        with self._lock:
            self._state_version += 1

            # Update timestamp
            now_utc = datetime.utcnow()
            now_ist = datetime.now(IST)

            self._state["state_version"] = self._state_version
            self._state["timestamp_utc"] = now_utc.isoformat() + "Z"
            self._state["timestamp_ist"] = now_ist.isoformat()
            self._last_update = now_ist

            # Increment cycle count on state update
            if "cycle_count" not in self._state:
                self._state["cycle_count"] = 0
            self._state["cycle_count"] = self._state_version
            self._state["last_cycle_ts_iso"] = now_ist.isoformat()
            self._state["last_fetch_ts_iso"] = now_ist.isoformat()

            # Check broker connectivity periodically (every 10 state updates)
            # BUT: Don't overwrite broker status if it was set by sync_from_files
            # Only check if broker status is not already set
            if self._state_version % 10 == 0 and "broker" not in updates:
                self._state["broker"] = self._check_broker_connectivity()

            # Deep merge updates
            self._deep_merge(self._state, updates)

            # Save to file for persistence
            self._save_state()

            return self._state_version

    def _deep_merge(self, base: Dict, updates: Dict):
        """Deep merge updates into base dictionary"""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get_state(self) -> Dict[str, Any]:
        """Get current state snapshot (thread-safe)"""
        with self._lock:
            # Return a deep copy to prevent external modifications
            return json.loads(json.dumps(self._state))

    def get_state_version(self) -> int:
        """Get current state version"""
        return self._state_version

    def _save_state(self):
        """Save state to file for persistence"""
        try:
            state_file = self.outputs_dir / "runtime_state.json"
            with open(state_file, "w") as f:
                json.dump(self._state, f, indent=2)

            # Also save to state_snapshots for history
            snapshots_dir = self.outputs_dir / "state_snapshots"
            snapshots_dir.mkdir(exist_ok=True)
            snapshot_file = snapshots_dir / f"state_{self._state_version}.json"
            with open(snapshot_file, "w") as f:
                json.dump(self._state, f, indent=2)

            # Keep only last 1000 snapshots
            snapshot_files = sorted(
                snapshots_dir.glob("state_*.json"),
                key=lambda f: int(f.stem.split("_")[1]) if f.stem.split("_")[1].isdigit() else 0,
            )
            if len(snapshot_files) > 1000:
                for old_file in snapshot_files[:-1000]:
                    try:
                        old_file.unlink()
                    except:
                        pass
        except Exception as e:
            print(f"Warning: Failed to save state: {e}")

    def load_state(self):
        """Load state from file if exists"""
        try:
            state_file = self.outputs_dir / "runtime_state.json"
            if state_file.exists():
                with open(state_file, "r") as f:
                    loaded = json.load(f)
                    with self._lock:
                        self._state = loaded
                        self._state_version = loaded.get("state_version", 0)
        except Exception as e:
            print(f"Warning: Failed to load state: {e}")

    def sync_from_files(self):
        """
        Sync state from existing output files.
        This bridges the gap during migration.
        """
        updates = {}

        # Sync health data
        try:
            health_file = self.outputs_dir / "health.json"
            if health_file.exists():
                health = json.loads(health_file.read_text())

                # Always enforce PAPER mode - never allow LIVE mode (safety)
                updates["mode"] = "PAPER"  # Force PAPER regardless of health data

                # Use is_connected from health.json (same logic as /api/health endpoint)
                # health.json has 'is_connected' field, /api/health converts it to 'broker_status'
                is_connected = health.get("is_connected", False)
                broker_status_str = "connected" if is_connected else "disconnected"

                updates["broker"] = {
                    "connected": is_connected,
                    "name": "dhan",
                    "status": broker_status_str,  # Match /api/health format
                    "error": None,
                    "latency_ms": health.get("broker_latency_ms"),
                    "last_ok": datetime.now(IST).isoformat() if is_connected else None,
                }
                updates["market"] = {
                    "is_open": health.get("market_status") == "open",
                    "reason": health.get("market_status", "closed"),
                }
                # REAL_ONLY MODE: Never set data_source to SYNTHETIC
                health_data_source = health.get("data_source", "not_ready" if REAL_ONLY else "SYNTHETIC")
                if REAL_ONLY and health_data_source.lower() in ("synthetic", "simulated"):
                    updates["data_source"] = "not_ready"
                else:
                    updates["data_source"] = health_data_source
                updates["qc"] = {
                    "status": health.get("qc_status", "PASS"),
                    "reasons": health.get("qc_failures", []),
                    "contracts_total": health.get("contracts_total", 0),
                    "underlyings": health.get("underlyings", 0),
                    "failures": health.get("qc_failures", []),
                }

                if "performance_sla" in health:
                    updates["performance"] = health["performance_sla"]
        except Exception as e:
            print(f"Warning: Failed to sync health: {e}")

        # Sync positions with reconciliation
        try:
            from dashboard.backend.position_reconciliation import PositionReconciliation

            reconciler = PositionReconciliation(self.outputs_dir)
            broker_connected = updates.get("broker", {}).get("connected", False)
            reconciliation = reconciler.reconcile(broker_connected)

            updates["positions"] = reconciliation["positions"]
            updates["positions_source"] = reconciliation["positions_source"]
            updates["reconciliation"] = {
                "status": reconciliation["reconciliation_status"],
                "mismatches": reconciliation["mismatches"],
                "timestamp": reconciliation["timestamp"],
            }
        except Exception as e:
            print(f"Warning: Failed to reconcile positions: {e}")
            # Fallback to simple sync
            try:
                positions_file = self.outputs_dir / "positions_live.json"
                if positions_file.exists():
                    positions_data = json.loads(positions_file.read_text())
                    positions = positions_data.get("positions", [])
                    if isinstance(positions, list):
                        updates["positions"] = positions
                        updates["positions_source"] = "INTERNAL_UNVERIFIED"
            except:
                pass

        # Sync PnL
        try:
            pnl_file = self.outputs_dir / "paper_pnl_summary.json"
            if pnl_file.exists():
                pnl_data = json.loads(pnl_file.read_text())
                updates["pnl"] = {
                    "unrealized": pnl_data.get("unrealized_pnl", 0.0),
                    "realized": pnl_data.get("realized_pnl", 0.0),
                    "total": pnl_data.get("total_pnl", 0.0),
                    "day_total": pnl_data.get("daily_pnl", 0.0),
                }
        except Exception as e:
            print(f"Warning: Failed to sync PnL: {e}")

        # Sync signals
        try:
            signal_file = self.outputs_dir / "top_trade_signal.json"
            if signal_file.exists():
                signal_data = json.loads(signal_file.read_text())
                if signal_data.get("action") == "TRADE":
                    updates["signals"] = {
                        "status": "BUY" if signal_data.get("direction") == "LONG" else "SELL",
                        "underlying": signal_data.get("underlying"),
                        "confidence": signal_data.get("confidence", 0) * 100,
                        "reason": signal_data.get("reason", ""),
                        "last_signal": signal_data,
                    }
        except Exception as e:
            print(f"Warning: Failed to sync signals: {e}")

        # Add cycle tracking
        updates["cycle_count"] = 0
        updates["last_cycle_ts_iso"] = None
        updates["last_fetch_ts_iso"] = datetime.now(IST).isoformat()

        # Apply updates
        if updates:
            self.update_state(updates)

    def add_alert(self, level: str, code: str, message: str):
        """Add an alert to the state"""
        alert = {
            "level": level,  # INFO, WARN, CRIT
            "code": code,
            "message": message,
            "ts": datetime.now(IST).isoformat(),
            "read": False,
        }

        with self._lock:
            if "alerts" not in self._state:
                self._state["alerts"] = []
            self._state["alerts"].insert(0, alert)  # Most recent first
            # Keep only last 100 alerts
            self._state["alerts"] = self._state["alerts"][:100]
            self._state_version += 1
            self._save_state()


# Global instance
_state_store: Optional[RuntimeStateStore] = None


def get_state_store(outputs_dir: Optional[Path] = None) -> RuntimeStateStore:
    """Get or create global state store instance"""
    global _state_store
    if _state_store is None:
        if outputs_dir is None:
            # Default to outputs directory
            outputs_dir = Path(__file__).parent.parent.parent / "outputs"
        _state_store = RuntimeStateStore(outputs_dir)
        _state_store.load_state()
        _state_store.sync_from_files()
    return _state_store
    def upsert_alert(self, level: str, code: str, message: str) -> None:
        """Insert alert only if not already active. Prevents duplicate flood every 5s."""
        with self._lock:
            # Check if active (non-resolved) alert with same code exists
            existing = [a for a in self._state.get("alerts", [])
                        if a.get("code") == code and not a.get("resolved", False)]
            if existing:
                existing[0]["ts"] = datetime.now(IST).isoformat()
                return
            alert = {
                "level": level, "code": code, "message": message,
                "ts": datetime.now(IST).isoformat(),
                "read": False, "resolved": False,
            }
            alerts = self._state.get("alerts", [])
            alerts.insert(0, alert)
            self._state["alerts"] = alerts[:100]
            self._state_version += 1

    def resolve_alert(self, code: str) -> None:
        """Remove active alert by code. Called when condition clears."""
        with self._lock:
            alerts = self._state.get("alerts", [])
            before = len(alerts)
            self._state["alerts"] = [
                a for a in alerts
                if not (a.get("code") == code and not a.get("resolved", False))
            ]
            if len(self._state["alerts"]) != before:
                self._state_version += 1


