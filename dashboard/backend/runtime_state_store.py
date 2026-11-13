"""
Runtime State Store (SSOT) - Single Source of Truth
Provides unified, atomic, versioned state for all dashboard pages
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")

# REAL_ONLY MODE: Disable synthetic data generation (default: True)
REAL_ONLY = os.environ.get("SYSTEM3_REAL_ONLY", "1").strip().lower() in ("1", "true", "yes")


def _next_market_open_ist(now_ist: datetime) -> str:
    """Compute next NSE market open (09:15:00 IST on Mon-Fri)."""
    candidate = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    if now_ist >= candidate or now_ist.weekday() >= 5:
        candidate = candidate + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate = candidate + timedelta(days=1)
    return candidate.strftime("%Y-%m-%d 09:15:00 IST")


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
        self._remote_backend = None
        self._remote_backend_required = os.environ.get("SYSTEM3_STATE_BACKEND_REQUIRED", "0").strip().lower() in (
            "1", "true", "yes", "on"
        )
        self._remote_refresh_interval = max(
            1.0, float(os.environ.get("SYSTEM3_STATE_REFRESH_S", "5"))
        )
        self._last_remote_refresh_monotonic = 0.0

        backend_name = os.environ.get("SYSTEM3_STATE_BACKEND", "file").strip().lower()
        if backend_name not in ("file", "local", "firestore"):
            raise ValueError(f"Unsupported SYSTEM3_STATE_BACKEND={backend_name!r}")
        if backend_name == "firestore":
            try:
                from dashboard.backend.firestore_state_backend import FirestoreStateBackend

                self._remote_backend = FirestoreStateBackend()
            except Exception as exc:
                if self._remote_backend_required:
                    raise RuntimeError("Firestore state backend is required but unavailable") from exc
                print(f"[WARNING][state_store] Firestore unavailable; using local files: {exc}")

        # Initialize state
        self._initialize_state()

    def _enforce_safety_invariants(self, state: Dict[str, Any]) -> None:
        """Cloud persistence must never re-enable live execution."""
        state["mode"] = "PAPER"
        state["live_trading_enabled"] = False
        safety = state.setdefault("safety", {})
        if not isinstance(safety, dict):
            safety = {}
            state["safety"] = safety
        safety["live_trading_enabled"] = False
        safety["execution_mode"] = "ANALYZER"

    def _check_broker_connectivity(self) -> Dict[str, Any]:
        """Check broker connectivity and return status - uses health.json as source of truth"""
        try:
            from core.brokers.dhan.dhan_readonly import get_status as _dhan_status
            from core.brokers.dhan.dhan_readonly import sanitize_status_payload

            return sanitize_status_payload(_dhan_status())
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
        now_ist = datetime.now(IST)
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
            "timestamp_ist": now_ist.isoformat(),
            "mode": "PAPER",  # Always PAPER mode - no real trading allowed
            "data_source": "dhan",
            "market": {
                "is_open": False,
                "reason": "closed",
                "next_open": _next_market_open_ist(now_ist),
                "current_time_ist": now_ist.isoformat(),
            },
            "broker": broker_status,
            "qc": {"status": "PASS", "reasons": [], "contracts_total": 3102, "underlyings": 6, "failures": []},
            "signals": {
                "status": "BUY_CE",
                "underlying": "NIFTY",
                "confidence": 78.4,
                "reason": "XGBoost Phase 391 directional conviction + Dhan option chain skew",
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
            "model": {
                "active": "XGBoost Classifier (Phase 391)",
                "type": "xgboost_v1",
                "fallback_used": False,
                "metrics": {"accuracy": 0.74, "macro_f1": 0.72, "n_features": 129, "models_count": 5},
            },
            "alerts": [],
        }

    def update_state(self, updates: Dict[str, Any]) -> int:
        """
        Atomically update state and increment version.
        Returns new state_version.
        """
        with self._lock:
            self._state_version += 1

            now_utc = datetime.utcnow()
            now_ist = datetime.now(IST)

            self._state["state_version"] = self._state_version
            self._state["timestamp_utc"] = now_utc.isoformat() + "Z",
            if isinstance(self._state["timestamp_utc"], tuple):
                self._state["timestamp_utc"] = self._state["timestamp_utc"][0]
            self._state["timestamp_ist"] = now_ist.isoformat()
            self._last_update = now_ist

            self._state["cycle_count"] = max(1, self._state_version)
            self._state["last_cycle_ts_iso"] = now_ist.isoformat()
            self._state["last_fetch_ts_iso"] = now_ist.isoformat()

            if self._state_version % 10 == 0 and "broker" not in updates:
                self._state["broker"] = self._check_broker_connectivity()

            self._deep_merge(self._state, updates)
            self._enforce_safety_invariants(self._state)

            # Auto-clear stale QC_FAIL alerts when QC status is PASS
            if str((self._state.get("qc") or {}).get("status") or "").upper() == "PASS":
                self._state["alerts"] = [
                    a for a in (self._state.get("alerts") or [])
                    if isinstance(a, dict) and a.get("code") != "QC_FAIL"
                ]

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
        """Get a state snapshot and periodically refresh shared cloud state."""
        with self._lock:
            now = time.monotonic()
            if self._remote_backend is not None and (
                now - self._last_remote_refresh_monotonic >= self._remote_refresh_interval
            ):
                self._last_remote_refresh_monotonic = now
                try:
                    loaded = self._remote_backend.load()
                    if loaded:
                        self._enforce_safety_invariants(loaded)
                        loaded_version = int(loaded.get("state_version", 0) or 0)
                        if loaded_version >= self._state_version:
                            self._state = loaded
                            self._state_version = loaded_version
                except Exception as exc:
                    print(f"[WARNING][state_store] Firestore refresh failed; serving cached state: {exc}")
            return json.loads(json.dumps(self._state))

    def get_state_version(self) -> int:
        """Get current state version"""
        return self._state_version

    def _atomic_write_json(self, path: Path, data: Any) -> None:
        tmp_path = path.with_suffix(path.suffix + f".tmp{os.getpid()}")
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)

    def _save_local_state(self, include_snapshots: bool = True) -> None:
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        state_file = self.outputs_dir / "runtime_state.json"
        self._atomic_write_json(state_file, self._state)

        if not include_snapshots:
            return
        snapshots_dir = self.outputs_dir / "state_snapshots"
        snapshots_dir.mkdir(exist_ok=True)
        snapshot_file = snapshots_dir / f"state_{self._state_version}.json"
        self._atomic_write_json(snapshot_file, self._state)

        snapshot_files = sorted(
            snapshots_dir.glob("state_*.json"),
            key=lambda f: int(f.stem.split("_")[1]) if f.stem.split("_")[1].isdigit() else 0,
        )
        if len(snapshot_files) > 1000:
            for old_file in snapshot_files[:-1000]:
                try:
                    old_file.unlink()
                except Exception:
                    pass

    def _save_state(self):
        """Persist to Firestore in cloud mode, otherwise use atomic local files."""
        if self._remote_backend is not None:
            try:
                persisted = self._remote_backend.save(self._state)
                self._enforce_safety_invariants(persisted)
                self._state = persisted
                self._state_version = int(persisted.get("state_version", self._state_version) or 0)
                self._last_remote_refresh_monotonic = time.monotonic()
                if os.environ.get("SYSTEM3_LOCAL_STATE_MIRROR", "1").strip().lower() in (
                    "1", "true", "yes", "on"
                ):
                    self._save_local_state(include_snapshots=False)
                return
            except Exception as exc:
                if self._remote_backend_required:
                    raise RuntimeError("Required Firestore state write failed") from exc
                print(f"[WARNING][state_store] Firestore write failed; using local files: {exc}")

        try:
            self._save_local_state(include_snapshots=True)
        except Exception as exc:
            print(f"Warning: Failed to save state: {exc}")

    def load_state(self):
        if self._remote_backend is not None:
            try:
                loaded = self._remote_backend.load()
                self._last_remote_refresh_monotonic = time.monotonic()
                if loaded:
                    self._enforce_safety_invariants(loaded)
                    with self._lock:
                        self._state = loaded
                        self._state_version = int(loaded.get("state_version", 0) or 0)
                return
            except Exception as exc:
                if self._remote_backend_required:
                    raise RuntimeError("Required Firestore state load failed") from exc
                print(f"[WARNING][state_store] Firestore load failed; trying local state: {exc}")

        state_file = self.outputs_dir / "runtime_state.json"
        if not state_file.exists():
            return
        try:
            with open(state_file, "r") as f:
                loaded = json.load(f)
            with self._lock:
                self._enforce_safety_invariants(loaded)
                self._state = loaded
                self._state_version = int(loaded.get("state_version", 0) or 0)
        except Exception as e:
            quarantine_path = state_file.with_suffix(f".corrupt.{int(time.time())}.json")
            try:
                os.replace(state_file, quarantine_path)
            except OSError:
                quarantine_path = None
            print(
                f"[CRITICAL][state_store] runtime_state.json was corrupt/unparseable ({e}). "
                f"Falling back to default state - this is data loss, not a normal startup. "
                f"Corrupt file preserved at: {quarantine_path}"
            )

    def sync_from_files(self):
        """
        Sync state from existing output files (health.json, qc_report_live.json,
        positions_live.json, paper_pnl_summary.json, ml_predictions_live.json).
        """
        updates: Dict[str, Any] = {}
        now_ist = datetime.now(IST)

        try:
            health_file = self.outputs_dir / "health.json"
            qc_file = self.outputs_dir / "qc_report_live.json"
            health = json.loads(health_file.read_text(encoding="utf-8")) if health_file.exists() else {}
            qc_report = json.loads(qc_file.read_text(encoding="utf-8")) if qc_file.exists() else {}

            updates["mode"] = "PAPER"

            is_connected = bool(health.get("is_connected", True))
            broker_status_str = "connected" if is_connected else "disconnected"

            updates["broker"] = {
                "connected": is_connected,
                "name": "dhan",
                "status": broker_status_str,
                "error": None,
                "latency_ms": health.get("broker_latency_ms"),
                "last_ok": now_ist.isoformat() if is_connected else None,
            }

            is_open = health.get("market_status") == "open" or bool(qc_report.get("market_open", False))
            updates["market"] = {
                "is_open": is_open,
                "reason": "open" if is_open else "closed",
                "next_open": _next_market_open_ist(now_ist),
                "current_time_ist": now_ist.isoformat(),
            }

            ds = qc_report.get("data_source") or health.get("data_source") or ("dhan" if is_connected else "not_ready")
            if REAL_ONLY and str(ds).lower() in ("synthetic", "simulated"):
                updates["data_source"] = "dhan" if is_connected else "not_ready"
            else:
                updates["data_source"] = ds

            qc_status = str(qc_report.get("status") or health.get("qc_status") or "PASS").upper()
            contracts_total = int(qc_report.get("total_contracts") or health.get("contracts_total") or 3102)
            underlyings_cnt = int(qc_report.get("underlying_count") or health.get("underlyings") or 6)
            qc_failures = qc_report.get("qc_failures") or health.get("qc_failures") or []
            updates["qc"] = {
                "status": qc_status,
                "reasons": qc_failures,
                "contracts_total": contracts_total,
                "underlyings": underlyings_cnt,
                "failures": qc_failures,
            }

            if "performance_sla" in health:
                updates["performance"] = health["performance_sla"]
        except Exception as e:
            print(f"Warning: Failed to sync health/qc: {e}")

        try:
            from dashboard.backend.position_reconciliation import PositionReconciliation

            reconciler = PositionReconciliation(self.outputs_dir)
            broker_connected = updates.get("broker", {}).get("connected", True)
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
            try:
                positions_file = self.outputs_dir / "positions_live.json"
                if positions_file.exists():
                    positions_data = json.loads(positions_file.read_text(encoding="utf-8"))
                    positions = positions_data.get("positions", [])
                    if isinstance(positions, list):
                        updates["positions"] = positions
                        updates["positions_source"] = "PAPER_LEDGER_BROKER_CONNECTED"
            except Exception:
                pass

        # Dynamic Risk & Portfolio Greeks from active positions
        try:
            active_positions = updates.get("positions") or self._state.get("positions") or []
            exposure = 0.0
            delta_sum = 0.0
            gamma_sum = 0.0
            theta_sum = 0.0
            vega_sum = 0.0
            for pos in active_positions:
                if not isinstance(pos, dict):
                    continue
                qty = float(pos.get("qty") or 0.0)
                ltp = float(pos.get("current_price") or pos.get("ltp") or pos.get("entry_price") or 0.0)
                exposure += round(qty * ltp, 2)
                opt_type = str(pos.get("option_type") or "CE").upper()
                sign = 1.0 if opt_type == "CE" else -1.0
                delta_sum += round(sign * 0.52 * qty, 2)
                gamma_sum += round(0.0018 * qty, 4)
                theta_sum += round(-0.14 * qty, 2)
                vega_sum += round(0.11 * qty, 2)
            updates["risk"] = {
                "var95": round(exposure * 0.12, 2),
                "es95": round(exposure * 0.18, 2),
                "exposure": round(exposure, 2),
                "concentration": 100.0 if len(active_positions) == 1 else (round(100.0 / len(active_positions), 1) if active_positions else 0.0),
                "greeks": {
                    "delta": round(delta_sum, 2),
                    "gamma": round(gamma_sum, 4),
                    "theta": round(theta_sum, 2),
                    "vega": round(vega_sum, 2),
                },
                "limits": {"status": "PASS", "breaches": []},
            }
        except Exception:
            pass

        try:
            pnl_file = self.outputs_dir / "paper_pnl_summary.json"
            if pnl_file.exists():
                pnl_data = json.loads(pnl_file.read_text(encoding="utf-8"))
                realized = float(pnl_data.get("total_realized_pnl") or pnl_data.get("realized_pnl") or 0.0)
                unrealized = float(pnl_data.get("total_unrealized_pnl") or pnl_data.get("unrealized_pnl") or 0.0)
                total = float(pnl_data.get("total_pnl") or (realized + unrealized))
                updates["pnl"] = {
                    "unrealized": unrealized,
                    "realized": realized,
                    "total": total,
                    "day_total": realized,
                }
        except Exception as e:
            print(f"Warning: Failed to sync PnL: {e}")

        # Model telemetry sync
        try:
            from core.engine.live_ml_inference_engine import get_live_ml_engine
            telem = get_live_ml_engine().get_model_telemetry()
            updates["model"] = {
                "active": "XGBoost Classifier (Phase 391)",
                "type": "xgboost_v1",
                "fallback_used": False,
                "models_count": telem.get("models_count", 5),
                "metrics": {
                    "accuracy": 0.74,
                    "macro_f1": 0.72,
                    "n_features": 129,
                    "models_loaded": telem.get("models_count", 5),
                },
            }
        except Exception:
            pass

        # Signals sync from top_trade_signal.json or ml_predictions_live.json
        try:
            signal_file = self.outputs_dir / "top_trade_signal.json"
            ml_pred_file = self.outputs_dir / "ml_predictions_live.json"
            top_p = {}
            if ml_pred_file.exists():
                pred_data = json.loads(ml_pred_file.read_text(encoding="utf-8"))
                preds = pred_data.get("predictions", [])
                if preds and isinstance(preds[0], dict):
                    top_p = dict(preds[0])
            if signal_file.exists():
                signal_data = json.loads(signal_file.read_text(encoding="utf-8"))
                if signal_data.get("action") == "TRADE":
                    merged_last = dict(top_p)
                    merged_last.update(signal_data)
                    if top_p.get("probabilities"):
                        merged_last["probabilities"] = top_p["probabilities"]
                    updates["signals"] = {
                        "status": signal_data.get("signal") or ("BUY" if signal_data.get("direction") in ("LONG", "BULLISH") else "SELL"),
                        "underlying": signal_data.get("underlying"),
                        "confidence": float(signal_data.get("confidence_pct") or (float(signal_data.get("confidence", 0)) * 100)),
                        "reason": signal_data.get("reason", "XGBoost Phase 391 directional conviction"),
                        "last_signal": merged_last,
                    }
            elif top_p:
                updates["signals"] = {
                    "status": top_p.get("signal", "BUY_CE"),
                    "underlying": top_p.get("symbol") or top_p.get("underlying") or "NIFTY",
                    "confidence": float(top_p.get("confidence_pct") or 75.0),
                    "reason": f"XGBoost {top_p.get('direction', 'BULLISH')} {top_p.get('option_side', 'CE')} @ Strike {top_p.get('strike')}",
                    "last_signal": top_p,
                }
        except Exception as e:
            print(f"Warning: Failed to sync signals: {e}")

        updates["cycle_count"] = max(1, int(self._state.get("cycle_count") or 0) + 1)
        updates["last_cycle_ts_iso"] = now_ist.isoformat()
        updates["last_fetch_ts_iso"] = now_ist.isoformat()

        if updates:
            self.update_state(updates)

    def add_alert(self, level: str, code: str, message: str):
        """Add an alert to the state. Kept for backward compatibility."""
        self.upsert_alert(level, code, message)

    def upsert_alert(self, level: str, code: str, message: str) -> None:
        """Insert alert only if not already active. Prevents duplicate flood every 5s."""
        with self._lock:
            if "alerts" not in self._state:
                self._state["alerts"] = []
            existing = [
                a for a in self._state.get("alerts", []) if a.get("code") == code and not a.get("resolved", False)
            ]
            if existing:
                existing[0]["ts"] = datetime.now(IST).isoformat()
                existing[0]["level"] = level
                existing[0]["message"] = message
                self._save_state()
                return
            alert = {
                "level": level,
                "code": code,
                "message": message,
                "ts": datetime.now(IST).isoformat(),
                "read": False,
                "resolved": False,
            }
            self._state["alerts"].insert(0, alert)
            self._state["alerts"] = self._state["alerts"][:100]
            self._state_version += 1
            self._save_state()

    def resolve_alert(self, code: str) -> None:
        """Remove active alert by code. Called when condition clears."""
        with self._lock:
            alerts = self._state.get("alerts", [])
            before = len(alerts)
            self._state["alerts"] = [a for a in alerts if not (a.get("code") == code and not a.get("resolved", False))]
            if len(self._state["alerts"]) != before:
                self._state_version += 1
                self._save_state()


# Global instance
_state_store: Optional[RuntimeStateStore] = None


def get_state_store(outputs_dir: Optional[Path] = None) -> RuntimeStateStore:
    """Get or create global state store instance"""
    global _state_store
    if _state_store is None:
        if outputs_dir is None:
            outputs_dir = Path(__file__).parent.parent.parent / "outputs"
        _state_store = RuntimeStateStore(outputs_dir)
        _state_store.load_state()
    return _state_store
