"""
Position Reconciliation Module
Reconciles broker positions, internal ledger, and UI state
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")


class PositionReconciliation:
    """
    Reconciles positions from multiple sources:
    - Broker positions (truth when connected)
    - Internal ledger (paper/live)
    - UI state
    """

    def __init__(self, outputs_dir: Path):
        self.outputs_dir = Path(outputs_dir)

    def get_broker_positions(self) -> List[Dict[str, Any]]:
        """Get positions from broker (when connected). Read-only - no
        orders are ever placed from this path."""
        try:
            from core.brokers.dhan.dhan_payload_normalizer import (
                normalize_position_row,
                normalize_positions_payload,
            )
            from core.brokers.dhan.dhan_readonly import (
                get_positions as dhan_get_positions,
            )
        except ImportError as e:
            print(f"Broker positions unavailable (import failed): {e}")
            return []

        try:
            result = dhan_get_positions()
            if not result.get("success", True) and result.get("data") is None:
                return []
            raw_rows = normalize_positions_payload(result.get("data"))
            positions = []
            for raw in raw_rows:
                row = normalize_position_row(raw)
                # reconcile() compares on position_id/qty; trading_symbol is
                # the closest thing Dhan gives to a stable per-position key.
                row["position_id"] = row.get("trading_symbol") or row.get("symbol")
                row["qty"] = row.get("net_qty", 0)
                positions.append(row)
            return positions
        except Exception as e:
            print(f"Error fetching broker positions: {e}")
            return []

    def get_internal_positions(self) -> List[Dict[str, Any]]:
        """Get positions from internal ledger"""
        positions_file = self.outputs_dir / "positions_live.json"
        if not positions_file.exists():
            return []

        try:
            data = json.loads(positions_file.read_text())
            if isinstance(data, dict):
                return data.get("positions", [])
            elif isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"Error reading internal positions: {e}")
            return []

    def reconcile(self, broker_connected: bool, broker_positions: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Reconcile positions and return reconciliation result

        Returns:
            {
                "positions": [...],  # Final reconciled positions
                "positions_source": "BROKER" | "INTERNAL_VERIFIED" | "INTERNAL_UNVERIFIED",
                "mismatches": [...],  # List of mismatches if any
                "reconciliation_status": "OK" | "MISMATCH" | "ERROR",
                "timestamp": "..."
            }
        """
        if broker_positions is None:
            broker_positions = self.get_broker_positions() if broker_connected else []

        internal_positions = self.get_internal_positions()

        result = {
            "positions": [],
            "positions_source": "INTERNAL_UNVERIFIED",
            "mismatches": [],
            "reconciliation_status": "OK",
            "timestamp": datetime.now(IST).isoformat(),
        }

        if broker_connected and broker_positions:
            # Broker is truth
            result["positions"] = broker_positions
            result["positions_source"] = "BROKER"

            # Check for mismatches
            broker_ids = {p.get("position_id") or p.get("symbol"): p for p in broker_positions}
            internal_ids = {p.get("position_id"): p for p in internal_positions}

            # Find mismatches
            for bid, bpos in broker_ids.items():
                if bid not in internal_ids:
                    result["mismatches"].append(
                        {"type": "BROKER_ONLY", "position_id": bid, "broker": bpos, "internal": None}
                    )
                else:
                    # Compare key fields
                    ipos = internal_ids[bid]
                    if abs(bpos.get("qty", 0) - ipos.get("qty", 0)) > 0.01:
                        result["mismatches"].append(
                            {
                                "type": "QTY_MISMATCH",
                                "position_id": bid,
                                "broker_qty": bpos.get("qty"),
                                "internal_qty": ipos.get("qty"),
                            }
                        )

            for iid, ipos in internal_ids.items():
                if iid not in broker_ids:
                    result["mismatches"].append(
                        {"type": "INTERNAL_ONLY", "position_id": iid, "broker": None, "internal": ipos}
                    )

            if result["mismatches"]:
                result["reconciliation_status"] = "MISMATCH"
        else:
            # Use internal positions, but mark as unverified
            result["positions"] = internal_positions
            if broker_connected:
                result["positions_source"] = "INTERNAL_VERIFIED"  # Broker connected but no positions
            else:
                result["positions_source"] = "INTERNAL_UNVERIFIED"  # Broker disconnected

        return result
