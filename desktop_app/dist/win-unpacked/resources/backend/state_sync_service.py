"""
State Sync Service - Periodically syncs SSOT from output files
Ensures SSOT stays up-to-date with the trading system
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pytz

IST = pytz.timezone('Asia/Kolkata')

# These will be set by the importing module
MARKET_DETECTION_AVAILABLE = False
ADVANCED_FEATURES_AVAILABLE = False


class StateSyncService:
    """Service to sync runtime state from output files"""
    
    def __init__(self, state_store, outputs_dir: Path):
        self.state_store = state_store
        self.outputs_dir = Path(outputs_dir)
        self._running = False
        self._sync_interval = 5  # Sync every 5 seconds
    
    async def start(self):
        """Start the sync service"""
        self._running = True
        asyncio.create_task(self._sync_loop())
    
    async def stop(self):
        """Stop the sync service"""
        self._running = False
    
    async def _sync_loop(self):
        """Main sync loop"""
        while self._running:
            try:
                await self.sync_state()
            except Exception as e:
                print(f"Error in state sync: {e}")
            await asyncio.sleep(self._sync_interval)
    
    async def sync_state(self):
        """Sync state from output files"""
        updates = {}
        
        # Sync market status
        try:
            if MARKET_DETECTION_AVAILABLE:
                import sys
                from pathlib import Path
                # Add src to path
                src_path = Path(__file__).parent.parent.parent / "src"
                if str(src_path) not in sys.path:
                    sys.path.insert(0, str(src_path))
                from utils.market_hours import is_market_open, get_market_status
                market_is_open, reason = is_market_open()
                market_status = get_market_status()
                
                updates["market"] = {
                    "is_open": market_is_open,
                    "reason": reason,
                    "current_time_ist": datetime.now(IST).isoformat()
                }
                
                if not market_is_open and "next_open" in market_status:
                    updates["market"]["next_open"] = market_status["next_open"]
                
                # Determine data source
                updates["data_source"] = "BROKER" if market_is_open else "SYNTHETIC"
        except Exception as e:
            print(f"Error syncing market status: {e}")
        
        # Sync health data
        try:
            health_file = self.outputs_dir / "health.json"
            if health_file.exists():
                health = json.loads(health_file.read_text())
                
                updates["mode"] = health.get("mode", "PAPER")
                updates["broker"] = {
                    "connected": health.get("broker_status") == "connected",
                    "status": health.get("broker_status", "disconnected"),
                    "name": "AngelOne"
                }
                
                # Sync QC
                qc_status = health.get("qc_status", "PASS")
                qc_failures = health.get("qc_failures", [])
                updates["qc"] = {
                    "status": qc_status,
                    "reasons": qc_failures if qc_status == "FAIL" else [],
                    "failures": qc_failures
                }
                
                # Sync cycle count
                if "cycle_count" in health:
                    updates["cycle_count"] = health["cycle_count"]
        except Exception as e:
            print(f"Error syncing health: {e}")
        
        # Sync positions
        try:
            positions_file = self.outputs_dir / "positions_live.json"
            if positions_file.exists():
                positions_data = json.loads(positions_file.read_text())
                positions = positions_data.get("positions", [])
                if isinstance(positions, list):
                    updates["positions"] = positions
        except Exception as e:
            print(f"Error syncing positions: {e}")
        
        # Sync PnL
        try:
            pnl_file = self.outputs_dir / "paper_pnl_summary.json"
            if pnl_file.exists():
                pnl_data = json.loads(pnl_file.read_text())
                updates["pnl"] = {
                    "unrealized": pnl_data.get("unrealized_pnl", 0.0),
                    "realized": pnl_data.get("realized_pnl", 0.0),
                    "total": pnl_data.get("total_pnl", 0.0),
                    "day_total": pnl_data.get("daily_pnl", 0.0)
                }
        except Exception as e:
            print(f"Error syncing PnL: {e}")
        
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
                        "last_signal": signal_data
                    }
                elif len(updates.get("positions", [])) > 0:
                    # If we have positions but no new signal, show managing state
                    updates["signals"] = {
                        "status": "MANAGING_POSITION",
                        "underlying": None,
                        "confidence": 0,
                        "reason": f"Managing {len(updates.get('positions', []))} open positions",
                        "last_signal": signal_data
                    }
        except Exception as e:
            print(f"Error syncing signals: {e}")
        
        # Sync QC data for contracts/underlyings count
        try:
            qc_file = self.outputs_dir / "qc_report_live.json"
            if qc_file.exists():
                qc_data = json.loads(qc_file.read_text())
                if "contracts_total" in qc_data:
                    updates["qc"]["contracts_total"] = qc_data["contracts_total"]
                if "underlyings" in qc_data:
                    updates["qc"]["underlyings"] = qc_data["underlyings"]
        except Exception as e:
            print(f"Error syncing QC details: {e}")
        
        # Compute risk metrics if positions exist
        try:
            positions = updates.get("positions", [])
            if positions and ADVANCED_FEATURES_AVAILABLE:
                try:
                    from dashboard.backend.risk_management import get_risk_management
                except ImportError:
                    from risk_management import get_risk_management
                risk_mgmt = get_risk_management()
                risk_metrics = risk_mgmt.calculate_portfolio_risk(positions)
                
                # Compute Greeks from positions
                total_delta = sum(p.get("delta", 0) * p.get("quantity", 0) for p in positions)
                total_gamma = sum(p.get("gamma", 0) * p.get("quantity", 0) for p in positions)
                total_theta = sum(p.get("theta", 0) * p.get("quantity", 0) for p in positions)
                total_vega = sum(p.get("vega", 0) * p.get("quantity", 0) for p in positions)
                
                updates["risk"] = {
                    "var95": risk_metrics.get("var_95", 0.0),
                    "es95": risk_metrics.get("expected_shortfall_95", 0.0),
                    "exposure": risk_metrics.get("total_exposure", 0.0),
                    "concentration": risk_metrics.get("concentration_risk", 0.0),
                    "greeks": {
                        "delta": total_delta,
                        "gamma": total_gamma,
                        "theta": total_theta,
                        "vega": total_vega
                    }
                }
        except Exception as e:
            print(f"Error computing risk metrics: {e}")
        
        # Generate alerts based on state
        try:
            alerts = []
            
            # QC FAIL alert
            if updates.get("qc", {}).get("status") == "FAIL":
                self.state_store.add_alert("WARN", "QC_FAIL", "Quality control check failed")
            
            # Broker disconnected alert
            if not updates.get("broker", {}).get("connected", False):
                self.state_store.add_alert("WARN", "BROKER_DISCONNECTED", "Broker connection lost")
            
            # Synthetic mode alert
            if updates.get("data_source") == "SYNTHETIC" and updates.get("market", {}).get("is_open", False):
                self.state_store.add_alert("INFO", "SYNTHETIC_MODE", "Using synthetic data (market open but broker unavailable)")
            
            # Positions while market closed
            positions_count = len(updates.get("positions", []))
            if positions_count > 0 and not updates.get("market", {}).get("is_open", False):
                self.state_store.add_alert("INFO", "POSITIONS_MARKET_CLOSED", f"{positions_count} positions open while market is closed")
            
        except Exception as e:
            print(f"Error generating alerts: {e}")
        
        # Apply updates to state store
        if updates:
            self.state_store.update_state(updates)


# Global instance
_sync_service: Optional[StateSyncService] = None


def get_sync_service(state_store, outputs_dir: Path) -> StateSyncService:
    """Get or create global sync service instance"""
    global _sync_service
    if _sync_service is None:
        _sync_service = StateSyncService(state_store, outputs_dir)
    return _sync_service
