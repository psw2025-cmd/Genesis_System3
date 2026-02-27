"""
Advanced Charting & Visualization System
Heatmaps, IV Surface, Greeks Charts
"""
import json
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')


class AdvancedCharting:
    """
    Advanced charting and visualization data preparation
    """
    
    def generate_option_chain_heatmap(
        self,
        chain_data: Dict[str, Any],
        metric: str = 'oi'
    ) -> Dict[str, Any]:
        """
        Generate heatmap data for option chain
        
        Args:
            chain_data: Chain data from API
            metric: Metric to visualize ('oi', 'volume', 'iv', 'ltp')
        
        Returns:
            Heatmap data structure
        """
        contracts = chain_data.get('contracts', [])
        if not contracts:
            return {"heatmap": [], "strikes": [], "expiries": []}
        
        # Extract unique strikes and expiries
        strikes = sorted(set(c.get('strike', 0) for c in contracts if c.get('strike')))
        expiries = sorted(set(c.get('expiry', '') for c in contracts if c.get('expiry')))
        
        # Build heatmap matrix
        heatmap_data = []
        for expiry in expiries:
            row = []
            for strike in strikes:
                # Find contracts for this strike and expiry
                matching = [
                    c for c in contracts
                    if c.get('strike') == strike and c.get('expiry') == expiry
                ]
                
                if matching:
                    # Sum CE and PE
                    value = sum(c.get(metric, 0) for c in matching)
                else:
                    value = 0
                
                row.append(value)
            heatmap_data.append({
                "expiry": expiry,
                "values": row
            })
        
        return {
            "heatmap": heatmap_data,
            "strikes": strikes,
            "expiries": expiries,
            "metric": metric,
            "spot": chain_data.get('spot', 0)
        }
    
    def generate_iv_surface(
        self,
        chain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate IV surface data
        
        Args:
            chain_data: Chain data from API
        
        Returns:
            IV surface data
        """
        contracts = chain_data.get('contracts', [])
        if not contracts:
            return {"surface": [], "strikes": [], "expiries": []}
        
        strikes = sorted(set(c.get('strike', 0) for c in contracts if c.get('strike')))
        expiries = sorted(set(c.get('expiry', '') for c in contracts if c.get('expiry')))
        
        surface_data = []
        for expiry in expiries:
            row = []
            for strike in strikes:
                # Find contracts for this strike and expiry
                matching = [
                    c for c in contracts
                    if c.get('strike') == strike and c.get('expiry') == expiry
                ]
                
                if matching:
                    # Average IV of CE and PE
                    ivs = [c.get('iv', 0) for c in matching if c.get('iv', 0) > 0]
                    avg_iv = sum(ivs) / len(ivs) if ivs else 0
                else:
                    avg_iv = 0
                
                row.append(avg_iv)
            surface_data.append({
                "expiry": expiry,
                "iv_values": row
            })
        
        return {
            "surface": surface_data,
            "strikes": strikes,
            "expiries": expiries,
            "spot": chain_data.get('spot', 0)
        }
    
    def generate_greeks_chart(
        self,
        chain_data: Dict[str, Any],
        greek: str = 'delta'
    ) -> Dict[str, Any]:
        """
        Generate Greeks chart data
        
        Args:
            chain_data: Chain data from API
            greek: Greek to visualize ('delta', 'gamma', 'theta', 'vega')
        
        Returns:
            Greeks chart data
        """
        contracts = chain_data.get('contracts', [])
        if not contracts:
            return {"data": [], "strikes": []}
        
        # Filter by option type (CE or PE)
        ce_contracts = [c for c in contracts if c.get('option_type') == 'CE']
        pe_contracts = [c for c in contracts if c.get('option_type') == 'PE']
        
        strikes = sorted(set(c.get('strike', 0) for c in contracts if c.get('strike')))
        
        ce_data = []
        pe_data = []
        
        for strike in strikes:
            ce_match = next((c for c in ce_contracts if c.get('strike') == strike), None)
            pe_match = next((c for c in pe_contracts if c.get('strike') == strike), None)
            
            ce_value = ce_match.get(greek, 0) if ce_match else 0
            pe_value = pe_match.get(greek, 0) if pe_match else 0
            
            ce_data.append(ce_value)
            pe_data.append(pe_value)
        
        return {
            "greek": greek,
            "strikes": strikes,
            "ce_data": ce_data,
            "pe_data": pe_data,
            "spot": chain_data.get('spot', 0)
        }
    
    def generate_pcr_chart(
        self,
        chain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Put-Call Ratio chart data
        
        Args:
            chain_data: Chain data from API
        
        Returns:
            PCR chart data
        """
        contracts = chain_data.get('contracts', [])
        if not contracts:
            return {"pcr_data": [], "strikes": []}
        
        strikes = sorted(set(c.get('strike', 0) for c in contracts if c.get('strike')))
        
        pcr_data = []
        for strike in strikes:
            ce_oi = sum(
                c.get('oi', 0) for c in contracts
                if c.get('strike') == strike and c.get('option_type') == 'CE'
            )
            pe_oi = sum(
                c.get('oi', 0) for c in contracts
                if c.get('strike') == strike and c.get('option_type') == 'PE'
            )
            
            pcr = pe_oi / ce_oi if ce_oi > 0 else 0
            pcr_data.append(pcr)
        
        return {
            "pcr_data": pcr_data,
            "strikes": strikes,
            "spot": chain_data.get('spot', 0),
            "overall_pcr": chain_data.get('pcr', 0)
        }
    
    def generate_equity_curve_enhanced(
        self,
        pnl_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate enhanced equity curve with drawdown
        
        Args:
            pnl_history: PnL history data
        
        Returns:
            Enhanced equity curve data
        """
        if not pnl_history:
            return {"equity_curve": [], "drawdown": [], "timestamps": []}
        
        equity = 0.0
        equity_curve = []
        drawdown = []
        timestamps = []
        peak = 0.0
        
        for entry in pnl_history:
            timestamp = entry.get('timestamp', '')
            total_pnl = entry.get('total_pnl', 0)
            
            equity += total_pnl
            equity_curve.append(equity)
            timestamps.append(timestamp)
            
            if equity > peak:
                peak = equity
            
            dd = ((equity - peak) / peak * 100) if peak > 0 else 0
            drawdown.append(dd)
        
        return {
            "equity_curve": equity_curve,
            "drawdown": drawdown,
            "timestamps": timestamps,
            "current_equity": equity,
            "peak_equity": peak,
            "max_drawdown": min(drawdown) if drawdown else 0
        }


# Global instance
_advanced_charting = AdvancedCharting()

def get_advanced_charting() -> AdvancedCharting:
    """Get global advanced charting instance"""
    return _advanced_charting
