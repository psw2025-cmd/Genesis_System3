"""
BLK-003 FIX: Option Strike/Token Visibility Audit
Generates proof that each signal's underlying has visible PE/CE contracts.

Issue: Users couldn't see which option contract (strike/token/expiry) was 
actually tradable for a given signal's underlying symbol.

Fix: Audit every signal against Dhan's live option chain data and produce:
1. Signal → underlying mapping (direction, confidence)
2. Underlying → F&O eligibility (is it in Dhan's tradable universe?)
3. For eligible: Strike/token/expiry/spread/liquidity evidence
4. Coverage report: % of signals with proven option contracts
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pytz
from collections import defaultdict

IST = pytz.timezone("Asia/Kolkata")


class OptionVisibilityAuditor:
    """Audits signal → option strike mapping with full traceability."""
    
    def __init__(self, dhan_chain_file: Optional[Path] = None):
        """
        Initialize auditor.
        
        Args:
            dhan_chain_file: Path to Dhan's option chain cache (JSON or CSV)
        """
        self.dhan_chain_file = dhan_chain_file
        self.chain_data = {}  # {symbol: [chain_rows]}
        self.audit_results = []
        self.coverage_stats = {
            "total_signals": 0,
            "signals_with_options": 0,
            "signals_missing_options": 0,
            "eligible_equity_options": 0,
            "ineligible_symbols": [],
        }
        
        if dhan_chain_file and Path(dhan_chain_file).exists():
            self._load_chain_data(dhan_chain_file)
    
    def _load_chain_data(self, chain_file: Path):
        """Load option chain from Dhan cache (JSON or CSV)."""
        try:
            if chain_file.suffix == ".json":
                with open(chain_file) as f:
                    data = json.load(f)
                    # Flatten by symbol
                    for row in data if isinstance(data, list) else data.get("chains", []):
                        sym = row.get("symbol") or row.get("underlying")
                        if sym not in self.chain_data:
                            self.chain_data[sym] = []
                        self.chain_data[sym].append(row)
            elif chain_file.suffix == ".csv":
                with open(chain_file) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        sym = row.get("symbol") or row.get("underlying")
                        if sym not in self.chain_data:
                            self.chain_data[sym] = []
                        self.chain_data[sym].append(row)
        except Exception as e:
            print(f"Warning: Could not load chain file {chain_file}: {e}")
    
    def audit_signal(
        self,
        signal_id: str,
        underlying: str,
        direction: str,
        confidence: float,
        timestamp: datetime
    ) -> Dict:
        """
        Audit a single signal for option visibility.
        
        Returns dict with:
        - signal_id, underlying, direction, confidence
        - has_options (bool)
        - option_details: {expiries, strikes, tokens, liquidity_samples}
        - proof: list of evidence items
        """
        result = {
            "signal_id": signal_id,
            "underlying": underlying,
            "direction": direction,
            "confidence": confidence,
            "timestamp": timestamp.isoformat(),
            "has_options": False,
            "option_details": {
                "expiries": [],
                "strikes": [],
                "pe_ce_pairs": [],  # [{expiry, strike, pe_token, ce_token}, ...]
                "liquidity_samples": [],
            },
            "proof": []
        }
        
        self.coverage_stats["total_signals"] += 1
        
        # Check if symbol has option chain data
        if underlying not in self.chain_data:
            result["proof"].append(f"Symbol {underlying} not found in Dhan option chain cache")
            self.coverage_stats["ineligible_symbols"].append(underlying)
            self.coverage_stats["signals_missing_options"] += 1
            return result
        
        chain_rows = self.chain_data[underlying]
        
        if not chain_rows:
            result["proof"].append(f"No option chain rows for {underlying}")
            self.coverage_stats["signals_missing_options"] += 1
            return result
        
        # Extract expiries and strikes
        expiries = set()
        strikes_by_expiry = defaultdict(set)
        pe_ce_map = defaultdict(dict)  # {(expiry, strike): {pe: token, ce: token}}
        liquidity_samples = []
        
        for row in chain_rows:
            expiry = row.get("expiry") or row.get("expiry_date")
            strike = row.get("strike") or row.get("strike_price")
            option_type = (row.get("type") or row.get("option_type") or "").upper()
            token = row.get("token") or row.get("contract_token")
            bid_qty = row.get("bid_qty") or row.get("bid_quantity") or 0
            ask_qty = row.get("ask_qty") or row.get("ask_quantity") or 0
            bid_price = row.get("bid_price") or row.get("bid") or 0
            ask_price = row.get("ask_price") or row.get("ask") or 0
            oi = row.get("oi") or row.get("open_interest") or 0
            
            if not (expiry and strike and option_type and token):
                continue
            
            expiries.add(expiry)
            strikes_by_expiry[expiry].add(str(strike))
            
            # Track PE/CE pairs
            if option_type in ("PE", "PUT"):
                pe_ce_map[(expiry, strike)]["pe"] = token
            elif option_type in ("CE", "CALL"):
                pe_ce_map[(expiry, strike)]["ce"] = token
            
            # Capture liquidity sample for proof
            if len(liquidity_samples) < 3:  # First 3 samples
                liquidity_samples.append({
                    "expiry": expiry,
                    "strike": strike,
                    "type": option_type,
                    "token": token,
                    "bid_qty": int(bid_qty),
                    "ask_qty": int(ask_qty),
                    "spread": float(ask_price) - float(bid_price) if ask_price and bid_price else None,
                    "oi": int(oi),
                })
        
        # Build result
        result["has_options"] = len(pe_ce_map) > 0
        result["option_details"]["expiries"] = sorted(list(expiries))
        result["option_details"]["liquidity_samples"] = liquidity_samples
        
        # Build PE/CE pairs list
        for (expiry, strike), pair in sorted(pe_ce_map.items()):
            if "pe" in pair and "ce" in pair:
                result["option_details"]["pe_ce_pairs"].append({
                    "expiry": expiry,
                    "strike": strike,
                    "pe_token": pair["pe"],
                    "ce_token": pair["ce"],
                })
        
        # Build proof chain
        result["proof"] = [
            f"✓ Found {len(expiries)} expiry dates",
            f"✓ Found {len(pe_ce_map)} strike prices",
            f"✓ Found {len(result['option_details']['pe_ce_pairs'])} PE/CE pairs with both contracts",
            f"✓ Captured {len(liquidity_samples)} liquidity samples",
            f"✓ Signal confidence: {confidence:.1%}",
        ]
        
        if result["has_options"]:
            self.coverage_stats["signals_with_options"] += 1
            self.coverage_stats["eligible_equity_options"] += 1
        else:
            result["proof"].append("⚠ No complete PE/CE pairs found")
            self.coverage_stats["signals_missing_options"] += 1
        
        self.audit_results.append(result)
        return result
    
    def generate_report(self, output_file: Optional[Path] = None) -> Dict:
        """Generate audit report."""
        now = datetime.now(IST)
        
        # Compute coverage %
        coverage_pct = (
            (self.coverage_stats["signals_with_options"] / self.coverage_stats["total_signals"] * 100)
            if self.coverage_stats["total_signals"] > 0
            else 0
        )
        
        report = {
            "generated_at": now.isoformat(),
            "coverage": {
                "total_signals_audited": self.coverage_stats["total_signals"],
                "signals_with_complete_options": self.coverage_stats["signals_with_options"],
                "signals_missing_options": self.coverage_stats["signals_missing_options"],
                "coverage_percentage": round(coverage_pct, 1),
            },
            "eligible_symbols": self.coverage_stats["eligible_equity_options"],
            "ineligible_symbols": self.coverage_stats["ineligible_symbols"],
            "audit_results": self.audit_results,
            "proof_gate": coverage_pct >= 95.0,  # 95% coverage required
        }
        
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
        
        return report


def generate_sample_audit_report() -> Dict:
    """Generate sample report for demonstration (without live data)."""
    auditor = OptionVisibilityAuditor()
    
    # Simulate audit of 5 signals
    signals = [
        ("SIG-2026-08-001", "SBIN", "LONG", 0.78),
        ("SIG-2026-08-002", "AXISBANK", "LONG", 0.82),
        ("SIG-2026-08-003", "RELIANCE", "LONG", 0.71),
        ("SIG-2026-08-004", "INFY", "SHORT", 0.65),
        ("SIG-2026-08-005", "WIPRO", "LONG", 0.74),
    ]
    
    now = datetime.now(IST)
    for sig_id, underlying, direction, confidence in signals:
        # Mock audit (in production, would load real Dhan chain data)
        audit = auditor.audit_signal(sig_id, underlying, direction, confidence, now)
        
        # Simulate option availability
        if underlying in ["SBIN", "AXISBANK", "RELIANCE", "INFY"]:
            audit["has_options"] = True
            audit["option_details"]["expiries"] = ["31-AUG-26", "28-SEP-26", "26-OCT-26"]
            audit["option_details"]["pe_ce_pairs"] = [
                {"expiry": "31-AUG-26", "strike": 500, "pe_token": "251234", "ce_token": "251235"},
                {"expiry": "31-AUG-26", "strike": 510, "pe_token": "251236", "ce_token": "251237"},
                {"expiry": "28-SEP-26", "strike": 500, "pe_token": "252234", "ce_token": "252235"},
            ]
            auditor.coverage_stats["signals_with_options"] += 1
    
    report = auditor.generate_report()
    report["sample_mode"] = True
    report["note"] = "This is a SAMPLE report. In production, actual Dhan chain data would be used."
    
    return report


if __name__ == "__main__":
    print("Generating Option Visibility Audit Report...\n")
    report = generate_sample_audit_report()
    
    print(json.dumps(report, indent=2, default=str))
    print(f"\n✓ Coverage: {report['coverage']['coverage_percentage']}%")
    print(f"✓ Proof gate (≥95%): {'PASS' if report['proof_gate'] else 'FAIL'}")
