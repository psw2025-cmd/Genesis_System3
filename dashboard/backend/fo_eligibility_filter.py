"""
BLK-004 FIX: Equity F&O Eligibility Filter
Prevents trade-ready signals on non-tradable equities.

Issue: System could rank cash-only equities for options trading,
creating impossible trade scenarios (no actual contracts to execute).

Fix: 
1. Maintain NSE F&O universe whitelist (updated daily from NSE/Dhan)
2. Pre-filter signals through F&O check before strategy ranking
3. Log rejection reason for each filtered symbol
4. Integrate into paper-trade workflow with audit trail
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import pytz
from collections import defaultdict

IST = pytz.timezone("Asia/Kolkata")


class FOEligibilityFilter:
    """Manages F&O (Futures & Options) tradability checks."""
    
    def __init__(self):
        """Initialize F&O eligibility filter with NSE universe."""
        # NSE F&O tradable equities (equity options are subset of this)
        # This list should be synced daily from NSE/Dhan
        self.fo_eligible_equities = {
            # Index names (liquid, high-volume)
            "SBIN", "AXISBANK", "ICICIBANK", "HDFC", "HDFCBANK",
            "RELIANCE", "TCS", "INFY", "LT", "ITC",
            "BHARTIARTL", "SUNPHARMA", "WIPRO", "ASIANPAINT", "MARUTI",
            "BAJAJ-AUTO", "BAJAJFINSV", "WIPRO", "HEROMOTOCO", "KOTAKBANK",
            "DRREDDY", "CIPLA", "DIVISLAB", "TECHM", "TATAMOTORS",
            "TATASTEEL", "M&M", "BOSCHLTD", "POWERGRID", "GAIL",
            "ONGC", "NIFTY50", "BANKNIFTY", "NIFTYNXT50",
            # Add more as needed based on NSE daily list
        }

        # Track rejections for audit
        self.rejection_log = defaultdict(list)  # {symbol: [timestamps]}
        self.approval_log = defaultdict(list)  # {symbol: [timestamps]}

    def bootstrap_universe(self, config_path: Optional[Path] = None) -> None:
        """Load config JSON then merge Dhan OPTSTK underlyings when available."""
        root = Path(__file__).resolve().parents[2]
        cfg = Path(config_path) if config_path else (root / "config" / "nse_fo_universe.json")
        if cfg.exists():
            self.load_from_nse_list(cfg)
        try:
            from core.brokers.dhan.equity_fo_universe import (
                INDEX_FO_SYMBOLS,
                load_equity_fo_universe,
            )

            data = load_equity_fo_universe()
            underlyings = data.get("underlyings") or []
            self.fo_eligible_equities.update(str(s).upper() for s in underlyings if s)
            self.fo_eligible_equities.update(INDEX_FO_SYMBOLS)
        except Exception as e:
            print(f"Warning: could not merge Dhan OPTSTK universe: {e}")

    def load_from_nse_list(self, nse_fo_file: Path):
        """Load F&O universe from NSE/Dhan instrument list."""
        try:
            if nse_fo_file.suffix == ".json":
                with open(nse_fo_file) as f:
                    data = json.load(f)
                    # Expecting: {symbols: [...]} or [{symbol: ...}, ...]
                    if isinstance(data, dict) and "symbols" in data:
                        self.fo_eligible_equities.update(data["symbols"])
                    elif isinstance(data, list):
                        self.fo_eligible_equities.update(
                            str(row.get("symbol")).upper()
                            for row in data
                            if isinstance(row, dict) and row.get("symbol")
                        )
            elif nse_fo_file.suffix == ".csv":
                import csv
                with open(nse_fo_file) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sym = row.get("symbol") or row.get("name")
                        if sym:
                            self.fo_eligible_equities.add(sym.upper())
        except Exception as e:
            print(f"Warning: Could not load NSE list {nse_fo_file}: {e}")
    
    def is_eligible(self, symbol: str) -> Tuple[bool, str]:
        """
        Check if symbol is F&O tradable.
        
        Returns: (is_eligible, reason)
        """
        symbol_upper = symbol.upper()
        
        if symbol_upper in self.fo_eligible_equities:
            self.approval_log[symbol_upper].append(datetime.now(IST))
            return True, "IN_NSE_FO_UNIVERSE"
        
        self.rejection_log[symbol_upper].append(datetime.now(IST))
        return False, "NOT_IN_NSE_FO_UNIVERSE"
    
    def filter_signals(self, signals: List[Dict]) -> Tuple[List[Dict], List[Tuple[str, str]]]:
        """
        Filter signal list through F&O eligibility.
        
        Args:
            signals: List of {id, underlying, direction, confidence, ...}
            
        Returns:
            (eligible_signals, rejected_signals_with_reasons)
        """
        eligible = []
        rejected = []
        
        for signal in signals:
            underlying = signal.get("underlying") or signal.get("symbol")
            is_eligible, reason = self.is_eligible(underlying)
            
            if is_eligible:
                signal["fo_check"] = {"eligible": True, "reason": reason}
                eligible.append(signal)
            else:
                rejected.append((underlying, reason))
        
        return eligible, rejected
    
    def get_audit_report(self) -> Dict:
        """Generate audit report of rejections/approvals."""
        now = datetime.now(IST)
        
        all_checked = set(list(self.rejection_log.keys()) + list(self.approval_log.keys()))
        
        report = {
            "generated_at": now.isoformat(),
            "fo_universe_size": len(self.fo_eligible_equities),
            "symbols_checked": len(all_checked),
            "total_approvals": sum(len(v) for v in self.approval_log.values()),
            "total_rejections": sum(len(v) for v in self.rejection_log.values()),
            "rejection_details": [
                {
                    "symbol": sym,
                    "rejection_count": len(timestamps),
                    "first_rejection": timestamps[0].isoformat(),
                    "last_rejection": timestamps[-1].isoformat(),
                }
                for sym, timestamps in sorted(self.rejection_log.items(), 
                                             key=lambda x: len(x[1]), reverse=True)
            ],
        }
        
        return report
    
    def get_current_universe(self) -> Set[str]:
        """Return current F&O universe."""
        return self.fo_eligible_equities.copy()


_fo_filter_singleton: Optional[FOEligibilityFilter] = None


def get_fo_eligibility_filter() -> FOEligibilityFilter:
    global _fo_filter_singleton
    if _fo_filter_singleton is None:
        _fo_filter_singleton = FOEligibilityFilter()
        _fo_filter_singleton.bootstrap_universe()
    return _fo_filter_singleton


def create_sample_fo_universe() -> Dict:
    """Create sample NSE F&O universe file."""
    return {
        "generated_at": datetime.now(IST).isoformat(),
        "source": "NSE",
        "symbols": [
            "SBIN", "AXISBANK", "ICICIBANK", "HDFC", "HDFCBANK",
            "RELIANCE", "TCS", "INFY", "LT", "ITC",
            "BHARTIARTL", "SUNPHARMA", "WIPRO", "ASIANPAINT", "MARUTI",
            "BAJAJ-AUTO", "BAJAJFINSV", "HEROMOTOCO", "KOTAKBANK",
            "DRREDDY", "CIPLA", "DIVISLAB", "TECHM", "TATAMOTORS",
        ],
        "count": 25,
        "last_updated": "2026-08-06",
        "notes": "Subset of NSE F&O universe for testing"
    }


if __name__ == "__main__":
    print("Testing F&O Eligibility Filter...\n")
    
    # Initialize filter
    filter_obj = FOEligibilityFilter()
    
    # Test eligibility checks
    test_symbols = [
        "SBIN",       # Eligible
        "AXISBANK",   # Eligible
        "RELIANCE",   # Eligible
        "RANDOMCORP", # Not eligible
        "PENNY_STOCK",# Not eligible
        "INFY",       # Eligible
    ]
    
    print("Individual symbol checks:")
    for sym in test_symbols:
        eligible, reason = filter_obj.is_eligible(sym)
        status = "✓ ELIGIBLE" if eligible else "✗ REJECTED"
        print(f"  {sym:15} → {status:15} ({reason})")
    
    # Test signal filtering
    test_signals = [
        {"id": "SIG-1", "underlying": "SBIN", "direction": "LONG", "confidence": 0.80},
        {"id": "SIG-2", "underlying": "RANDOMCORP", "direction": "LONG", "confidence": 0.75},
        {"id": "SIG-3", "underlying": "RELIANCE", "direction": "SHORT", "confidence": 0.65},
        {"id": "SIG-4", "underlying": "PENNY_STOCK", "direction": "LONG", "confidence": 0.90},
    ]
    
    print("\n\nSignal filtering:")
    eligible, rejected = filter_obj.filter_signals(test_signals)
    print(f"  Input signals: {len(test_signals)}")
    print(f"  Eligible: {len(eligible)}")
    print(f"  Rejected: {len(rejected)}")
    
    for underlying, reason in rejected:
        print(f"    ✗ {underlying}: {reason}")
    
    # Audit report
    print("\n\nAudit Report:")
    audit = filter_obj.get_audit_report()
    print(f"  F&O Universe size: {audit['fo_universe_size']}")
    print(f"  Symbols checked: {audit['symbols_checked']}")
    print(f"  Total approvals: {audit['total_approvals']}")
    print(f"  Total rejections: {audit['total_rejections']}")
    
    if audit['rejection_details']:
        print(f"\n  Top rejections:")
        for detail in audit['rejection_details'][:3]:
            print(f"    {detail['symbol']}: {detail['rejection_count']} times")
